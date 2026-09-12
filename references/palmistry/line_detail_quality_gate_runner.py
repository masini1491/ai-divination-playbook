#!/usr/bin/env python3
"""REFERENCE-ONLY principal-line line-detail quality-gate research runner.

Implements LINE_DETAIL_QUALITY_GATE_PLAN.md.

The runner reuses the frozen corrected C_G1_M0 512x512 geometry and frozen
manual centerline references.  It applies only geometry-preserving detail /
contrast degradations, then measures model/manual agreement and model
self-repeatability.  It does not establish a production threshold.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path
from typing import Any

import cv2
import numpy as np

import line_segmentation_repeatability_runner as base
import line_segmentation_content_dependence_control_runner as content
import line_segmentation_anatomical_manual_audit_runner as audit


FROZEN_ANNOTATION_SHA256 = (
    "51c4886e20cb9aee2d660fe1ca39f25b927398261478c013090ab5d611858041"
)
FROZEN_AUDIT_RESULT_SHA256 = (
    "6f95828b70b388028a46ee1879835d432d9dd695bdbbdd1f2656b6ebf3572284"
)
FROZEN_SPATIAL_SHA256 = (
    "ba65456e3c7c3a645a4000c721961d0f600b46541ffc7e7566525b99a55f87e7"
)
TOLERANCE_PX = 8.0

PRIMARY_FILES = tuple(f"P{i:03d}/S1/01.jpg" for i in range(2, 11))
P001_SENTINEL = "P001/S1/01.jpg"
CLASSES = audit.CLASSES
CLASS_TO_ID = audit.CLASS_TO_ID

CONDITIONS: tuple[dict[str, Any], ...] = (
    {"name": "baseline", "family": "baseline", "level": None, "unit": None},
    {"name": "blur_sigma_1p5", "family": "gaussian_blur", "level": 1.5, "unit": "sigma_px"},
    {"name": "blur_sigma_3p0", "family": "gaussian_blur", "level": 3.0, "unit": "sigma_px"},
    {"name": "blur_sigma_6p0", "family": "gaussian_blur", "level": 6.0, "unit": "sigma_px"},
    {"name": "downup_256", "family": "resolution", "level": 256, "unit": "downsample_side_px"},
    {"name": "downup_128", "family": "resolution", "level": 128, "unit": "downsample_side_px"},
    {"name": "downup_64", "family": "resolution", "level": 64, "unit": "downsample_side_px"},
    {"name": "contrast_0p75", "family": "contrast_compression", "level": 0.75, "unit": "factor"},
    {"name": "contrast_0p50", "family": "contrast_compression", "level": 0.50, "unit": "factor"},
    {"name": "contrast_0p25", "family": "contrast_compression", "level": 0.25, "unit": "factor"},
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def num_summary(values: list[float]) -> dict[str, Any]:
    if not values:
        return {
            "n": 0,
            "mean": None,
            "median": None,
            "p10": None,
            "p90": None,
            "min": None,
            "max": None,
        }
    a = np.asarray(values, dtype=np.float64)
    if not np.isfinite(a).all():
        raise RuntimeError("non-finite value in numeric summary")
    return {
        "n": int(a.size),
        "mean": float(a.mean()),
        "median": float(np.median(a)),
        "p10": float(np.percentile(a, 10)),
        "p90": float(np.percentile(a, 90)),
        "min": float(a.min()),
        "max": float(a.max()),
    }


def overlap(a: np.ndarray, b: np.ndarray) -> dict[str, Any]:
    aa = np.asarray(a, dtype=bool)
    bb = np.asarray(b, dtype=bool)
    na, nb = int(aa.sum()), int(bb.sum())
    if na == 0 and nb == 0:
        return {
            "status": "not_applicable_empty_both",
            "dice": None,
            "iou": None,
            "a_px": na,
            "b_px": nb,
            "intersection_px": 0,
        }
    inter = int(np.logical_and(aa, bb).sum())
    if na == 0 or nb == 0:
        return {
            "status": "appearance_transition",
            "dice": 0.0,
            "iou": 0.0,
            "a_px": na,
            "b_px": nb,
            "intersection_px": inter,
        }
    union = na + nb - inter
    return {
        "status": "comparable",
        "dice": float(2.0 * inter / (na + nb)),
        "iou": float(inter / union),
        "a_px": na,
        "b_px": nb,
        "intersection_px": inter,
    }


def gaussian_kernel_size(sigma: float) -> int:
    radius = int(np.ceil(3.0 * sigma))
    return 2 * radius + 1


def apply_condition(baseline: np.ndarray, spec: dict[str, Any]) -> tuple[np.ndarray, dict[str, Any]]:
    if baseline.shape != (512, 512, 3) or baseline.dtype != np.uint8:
        raise RuntimeError(f"baseline contract failed: {baseline.shape} {baseline.dtype}")

    family = spec["family"]
    level = spec["level"]
    meta: dict[str, Any] = {
        "family": family,
        "level": level,
        "unit": spec["unit"],
        "formal_clipping_fraction": 0.0,
    }

    if family == "baseline":
        out = baseline.copy()

    elif family == "gaussian_blur":
        sigma = float(level)
        k = gaussian_kernel_size(sigma)
        out = cv2.GaussianBlur(
            baseline,
            (k, k),
            sigmaX=sigma,
            sigmaY=sigma,
            borderType=cv2.BORDER_REFLECT_101,
        )
        meta["kernel_size"] = k

    elif family == "resolution":
        side = int(level)
        small = cv2.resize(baseline, (side, side), interpolation=cv2.INTER_AREA)
        out = cv2.resize(small, (512, 512), interpolation=cv2.INTER_LINEAR)
        meta["downsample_side_px"] = side
        meta["downsample_interpolation"] = "INTER_AREA"
        meta["upsample_interpolation"] = "INTER_LINEAR"

    elif family == "contrast_compression":
        factor = float(level)
        x = baseline.astype(np.float32)
        raw = 127.5 + factor * (x - 127.5)
        clipped = np.logical_or(raw < 0.0, raw > 255.0)
        meta["formal_clipping_fraction"] = float(clipped.mean())
        out = np.rint(np.clip(raw, 0.0, 255.0)).astype(np.uint8)
        meta["midpoint_0_255"] = 127.5
        meta["factor"] = factor

    else:
        raise RuntimeError(f"unknown condition family: {family}")

    out = np.ascontiguousarray(out, dtype=np.uint8)
    if out.shape != baseline.shape:
        raise RuntimeError(f"condition changed geometry: {spec['name']} {out.shape}")
    return out, meta


def quality_descriptors(rgb: np.ndarray) -> dict[str, Any]:
    if rgb.shape != (512, 512, 3) or rgb.dtype != np.uint8:
        raise RuntimeError(f"descriptor input contract failed: {rgb.shape} {rgb.dtype}")
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype(np.float32)
    lap = cv2.Laplacian(gray, cv2.CV_32F, ksize=3)
    gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    grad_sq = gx * gx + gy * gy
    grad_mag = np.sqrt(grad_sq)
    x = rgb.astype(np.float32)
    out = {
        "laplacian_variance": float(lap.var()),
        "tenengrad_mean_squared_gradient": float(grad_sq.mean()),
        "sobel_mean_gradient_magnitude": float(grad_mag.mean()),
        "rms_contrast_0_1": float(gray.std() / 255.0),
        "gray_mean_0_255": float(gray.mean()),
        "gray_std_0_255": float(gray.std()),
        "rgb_mean_0_255": [float(v) for v in x.mean(axis=(0, 1))],
        "rgb_std_0_255": [float(v) for v in x.std(axis=(0, 1))],
    }
    vals = [
        out["laplacian_variance"],
        out["tenengrad_mean_squared_gradient"],
        out["sobel_mean_gradient_magnitude"],
        out["rms_contrast_0_1"],
        out["gray_mean_0_255"],
        out["gray_std_0_255"],
    ]
    if not np.isfinite(vals).all():
        raise RuntimeError("non-finite image-quality descriptor")
    return out


def model_stats(mask: np.ndarray) -> dict[str, Any]:
    if mask.shape != (512, 512):
        raise RuntimeError(f"mask geometry drift: {mask.shape}")
    class_counts = {c: int(np.sum(mask == cid)) for c, cid in CLASS_TO_ID.items()}
    return {
        "class_pixel_counts": class_counts,
        "class_presence": {c: bool(class_counts[c] > 0) for c in CLASSES},
        "foreground_union_px": int(np.sum(mask > 0)),
        "foreground_union_fraction": float(np.mean(mask > 0)),
    }


def validate_frozen_audit_result(path: Path) -> dict[str, Any]:
    got = sha256_file(path)
    if got != FROZEN_AUDIT_RESULT_SHA256:
        raise RuntimeError(f"frozen anatomical-audit result SHA drift: {got}")
    data = json.loads(path.read_text(encoding="utf-8"))
    return data


def validate_context(args) -> tuple[
    dict[str, Any],
    list[dict[str, Any]],
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
]:
    if abs(float(audit.TOLERANCE_PX) - TOLERANCE_PX) > 1e-12:
        raise RuntimeError(f"manual-audit tolerance drift: {audit.TOLERANCE_PX}")

    if sha256_file(args.spatial_results) != FROZEN_SPATIAL_SHA256:
        raise RuntimeError("spatial-control SHA drift")
    spatial = audit.validate_spatial(args.spatial_results)
    spatial_by = {r["file"]: r for r in spatial["images"]}

    selected, mp_by = audit.load_context(args.zip, args.mediapipe_results)
    selected_files = tuple(r["file"] for r in selected)
    expected_all = (P001_SENTINEL,) + PRIMARY_FILES
    if selected_files != expected_all:
        raise RuntimeError(f"selected source set/order drift: {selected_files}")

    anns = audit.validate_annotations(
        args.annotations,
        FROZEN_ANNOTATION_SHA256,
        spatial_by,
    )
    ann_by = {r["file"]: r for r in anns["images"]}

    validate_frozen_audit_result(args.audit_result)

    for f in PRIMARY_FILES:
        row = ann_by[f]
        for c in CLASSES:
            if row["annotations"][c]["status"] != "observable":
                raise RuntimeError(f"primary frozen reference unexpectedly non-observable: {f} {c}")

    return spatial, selected, mp_by, spatial_by, ann_by


def manual_comparisons(
    ann_row: dict[str, Any],
    mask: np.ndarray,
) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for ref_class in CLASSES:
        ann = ann_row["annotations"][ref_class]
        if ann["status"] != "observable":
            raise RuntimeError(f"primary reference not observable: {ref_class}")
        ref = audit.raster_polyline(ann["points_xy"])
        comparisons = {
            model_class: audit.compare_one(ref, mask == CLASS_TO_ID[model_class])
            for model_class in CLASSES
        }
        correct = comparisons[ref_class]
        wrong = [(mc, comparisons[mc]) for mc in CLASSES if mc != ref_class]
        best_wrong_class, best_wrong = max(
            wrong,
            key=lambda item: float(item[1]["harmonic_coverage"]),
        )
        out[ref_class] = {
            "comparisons": comparisons,
            "correct": correct,
            "best_wrong_class": best_wrong_class,
            "best_wrong_harmonic_coverage": float(best_wrong["harmonic_coverage"]),
            "wrong_class_exceeds_correct": bool(
                float(best_wrong["harmonic_coverage"])
                > float(correct["harmonic_coverage"])
            ),
        }
    return out


def summarize_primary(images: list[dict[str, Any]]) -> dict[str, Any]:
    primary = [r for r in images if r["analysis_set"] == "primary"]
    if len(primary) != 9:
        raise RuntimeError(f"primary summary expected 9 images, got {len(primary)}")

    out: dict[str, Any] = {}
    for spec in CONDITIONS:
        name = spec["name"]
        rows = [r["conditions"][name] for r in primary]
        q = {
            "laplacian_variance": num_summary([
                float(x["quality_descriptors"]["laplacian_variance"]) for x in rows
            ]),
            "tenengrad_mean_squared_gradient": num_summary([
                float(x["quality_descriptors"]["tenengrad_mean_squared_gradient"]) for x in rows
            ]),
            "sobel_mean_gradient_magnitude": num_summary([
                float(x["quality_descriptors"]["sobel_mean_gradient_magnitude"]) for x in rows
            ]),
            "rms_contrast_0_1": num_summary([
                float(x["quality_descriptors"]["rms_contrast_0_1"]) for x in rows
            ]),
            "formal_clipping_fraction": num_summary([
                float(x["transform"]["formal_clipping_fraction"]) for x in rows
            ]),
        }
        classes: dict[str, Any] = {}
        for c in CLASSES:
            correct = [x["manual_reference"][c]["correct"] for x in rows]
            ov = [x["comparison_to_baseline"][c] for x in rows]
            classes[c] = {
                "model_presence_count": int(sum(x["model"]["class_presence"][c] for x in rows)),
                "correct_harmonic_coverage": num_summary([
                    float(z["harmonic_coverage"]) for z in correct
                ]),
                "model_on_reference_coverage": num_summary([
                    float(z["model_on_reference_coverage"]) for z in correct
                ]),
                "reference_on_model_coverage": num_summary([
                    float(z["reference_on_model_coverage"]) for z in correct
                ]),
                "median_model_to_reference_px": num_summary([
                    float(z["median_model_to_reference_px"])
                    for z in correct
                    if z["median_model_to_reference_px"] is not None
                ]),
                "median_reference_to_model_px": num_summary([
                    float(z["median_reference_to_model_px"])
                    for z in correct
                    if z["median_reference_to_model_px"] is not None
                ]),
                "best_wrong_harmonic_coverage": num_summary([
                    float(x["manual_reference"][c]["best_wrong_harmonic_coverage"])
                    for x in rows
                ]),
                "wrong_class_exceeds_correct_count": int(sum(
                    x["manual_reference"][c]["wrong_class_exceeds_correct"] for x in rows
                )),
                "baseline_mask_dice": num_summary([
                    float(z["dice"]) for z in ov if z["dice"] is not None
                ]),
                "baseline_mask_iou": num_summary([
                    float(z["iou"]) for z in ov if z["iou"] is not None
                ]),
                "appearance_transition_count": int(sum(
                    z["status"] == "appearance_transition" for z in ov
                )),
            }
        out[name] = {
            "family": spec["family"],
            "level": spec["level"],
            "unit": spec["unit"],
            "n_sources": 9,
            "quality_descriptors": q,
            "classes": classes,
        }
    return out


def dry_run(sess) -> None:
    y, x = np.mgrid[0:512, 0:512]
    base_img = np.zeros((512, 512, 3), dtype=np.uint8)
    base_img[..., 0] = np.clip(70 + x * 0.20, 0, 255).astype(np.uint8)
    base_img[..., 1] = np.clip(80 + y * 0.18, 0, 255).astype(np.uint8)
    base_img[..., 2] = 120
    cv2.ellipse(base_img, (256, 285), (135, 170), 0, 0, 360, (185, 155, 135), -1)
    cv2.line(base_img, (145, 225), (365, 245), (75, 55, 45), 3)
    cv2.line(base_img, (150, 285), (355, 315), (70, 50, 40), 3)
    cv2.ellipse(base_img, (205, 320), (75, 120), 15, 250, 95, (65, 48, 40), 3)
    base_img = np.ascontiguousarray(base_img, dtype=np.uint8)

    refs = {
        "heart_line": audit.raster_polyline([[145, 225], [250, 235], [365, 245]]),
        "head_line": audit.raster_polyline([[150, 285], [250, 300], [355, 315]]),
        "life_line": audit.raster_polyline([[180, 245], [150, 315], [175, 390]]),
    }

    rows = {}
    for spec in CONDITIONS:
        img, meta = apply_condition(base_img, spec)
        mask, logs = content.infer_512(sess, img)
        comparisons = {
            c: audit.compare_one(refs[c], mask == CLASS_TO_ID[c]) for c in CLASSES
        }
        rows[spec["name"]] = {
            "shape": list(img.shape),
            "dtype": str(img.dtype),
            "input_sha256": content.sha256_array(img),
            "transform": meta,
            "quality_descriptors": quality_descriptors(img),
            "mask_sha256": content.sha256_array(mask),
            "model": model_stats(mask),
            "finite_logit_summary": bool(np.isfinite([
                logs["logit_min"], logs["logit_max"], logs["logit_mean"]
            ]).all()),
            "synthetic_reference_comparison": comparisons,
        }

    print(json.dumps({
        "mode": "NON-MOHI LINE-DETAIL QUALITY GATE DRY RUN",
        "conditions": list(rows),
        "condition_count": len(rows),
        "rows": rows,
        "schema": "PASS",
    }, indent=2))


def run_full(args, sess, runtime: dict[str, Any], model_identity: dict[str, Any]) -> None:
    spatial, selected, mp_by, spatial_by, ann_by = validate_context(args)

    wanted = set(PRIMARY_FILES)
    if args.include_p001_sentinel:
        wanted.add(P001_SENTINEL)

    images: list[dict[str, Any]] = []
    decode_flag = cv2.IMREAD_COLOR | cv2.IMREAD_IGNORE_ORIENTATION

    with zipfile.ZipFile(args.zip) as zf:
        for src in selected:
            f = src["file"]
            if f not in wanted:
                continue

            baseline, adapter_meta = audit.regenerate_baseline(zf, src, mp_by[f])
            expected_input_sha = spatial_by[f]["conditions"]["baseline_512"]["input_sha256"]
            baseline_input_sha = content.sha256_array(baseline)
            if baseline_input_sha != expected_input_sha:
                raise RuntimeError(f"baseline input reproduction failed: {f}")

            condition_rows: dict[str, Any] = {}
            baseline_mask: np.ndarray | None = None

            for spec in CONDITIONS:
                img, transform_meta = apply_condition(baseline, spec)
                mask, logits = content.infer_512(sess, img)
                mask_sha = content.sha256_array(mask)

                if spec["name"] == "baseline":
                    expected_mask_sha = spatial_by[f]["conditions"]["baseline_512"]["mask_sha256"]
                    if mask_sha != expected_mask_sha:
                        raise RuntimeError(f"baseline mask reproduction failed: {f}")
                    baseline_mask = mask.copy()

                if baseline_mask is None:
                    raise RuntimeError("baseline condition must execute first")

                baseline_overlap = {
                    c: overlap(baseline_mask == CLASS_TO_ID[c], mask == CLASS_TO_ID[c])
                    for c in CLASSES
                }
                foreground_overlap = overlap(baseline_mask > 0, mask > 0)

                if f in PRIMARY_FILES:
                    manual = manual_comparisons(ann_by[f], mask)
                    manual_note = None
                else:
                    manual = None
                    manual_note = (
                        "P001 frozen manual reference is reference-quality-confounded; "
                        "no manual-reference quality metric is used in this study."
                    )

                condition_rows[spec["name"]] = {
                    "family": spec["family"],
                    "level": spec["level"],
                    "unit": spec["unit"],
                    "input_sha256": content.sha256_array(img),
                    "transform": transform_meta,
                    "quality_descriptors": quality_descriptors(img),
                    "mask_sha256": mask_sha,
                    "model": model_stats(mask),
                    "logit_summary": logits,
                    "comparison_to_baseline": {
                        **baseline_overlap,
                        "foreground_union": foreground_overlap,
                    },
                    "manual_reference": manual,
                    "manual_reference_note": manual_note,
                }

            images.append({
                "file": f,
                "analysis_set": "primary" if f in PRIMARY_FILES else "p001_sentinel",
                "source_sha256": src.get("sha256"),
                "baseline_input_sha256": baseline_input_sha,
                "adapter_meta": adapter_meta,
                "conditions": condition_rows,
            })
            print(f"[{len(images):02d}] completed {f}")

    primary_count = sum(r["analysis_set"] == "primary" for r in images)
    sentinel_count = sum(r["analysis_set"] == "p001_sentinel" for r in images)
    if primary_count != 9:
        raise RuntimeError(f"primary execution count drift: {primary_count}")
    if sentinel_count != (1 if args.include_p001_sentinel else 0):
        raise RuntimeError(f"sentinel execution count drift: {sentinel_count}")

    output: dict[str, Any] = {
        "status": "REFERENCE-ONLY / PREDECLARED LINE-DETAIL QUALITY-GATE RAW EVIDENCE",
        "runtime": runtime,
        **model_identity,
        "model": str(args.model),
        "metadata": str(args.meta),
        "source_zip": str(args.zip),
        "mediapipe_results": str(args.mediapipe_results),
        "spatial_results": str(args.spatial_results),
        "annotations": str(args.annotations),
        "frozen_annotation_sha256": FROZEN_ANNOTATION_SHA256,
        "frozen_anatomical_audit_result": str(args.audit_result),
        "frozen_anatomical_audit_result_sha256": FROZEN_AUDIT_RESULT_SHA256,
        "frozen_spatial_sha256": FROZEN_SPATIAL_SHA256,
        "comparison_tolerance_px": TOLERANCE_PX,
        "primary_files": list(PRIMARY_FILES),
        "p001_sentinel_included": bool(args.include_p001_sentinel),
        "p001_sentinel_reference_quality_confounded": True,
        "conditions_contract": list(CONDITIONS),
        "descriptor_contract": {
            "laplacian_variance": "variance of 3x3 CV_32F Laplacian on grayscale 0..255",
            "tenengrad_mean_squared_gradient": "mean(Sobel_x^2 + Sobel_y^2), 3x3, grayscale 0..255",
            "sobel_mean_gradient_magnitude": "mean(sqrt(Sobel_x^2 + Sobel_y^2)), grayscale 0..255",
            "rms_contrast_0_1": "grayscale standard deviation / 255",
            "contrast_midpoint": 127.5,
        },
        "execution": {
            "primary_sources": primary_count,
            "sentinel_sources": sentinel_count,
            "conditions_per_source": len(CONDITIONS),
            "primary_inferences": primary_count * len(CONDITIONS),
            "sentinel_inferences": sentinel_count * len(CONDITIONS),
            "stop": False,
        },
        "summary_primary_by_condition": summarize_primary(images),
        "images": images,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print("\nDONE")
    print(json.dumps(output["execution"], indent=2))
    print(args.output)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", type=Path, required=True)
    ap.add_argument("--meta", type=Path, required=True)
    ap.add_argument("--zip", type=Path)
    ap.add_argument("--mediapipe-results", type=Path)
    ap.add_argument("--spatial-results", type=Path)
    ap.add_argument("--annotations", type=Path)
    ap.add_argument("--audit-result", type=Path)
    ap.add_argument("--output", type=Path)
    ap.add_argument("--include-p001-sentinel", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    runtime = base.validate_runtime()
    sess, model_identity = base.validate_model(args.model, args.meta)

    if args.dry_run:
        dry_run(sess)
        return

    required = (
        args.zip,
        args.mediapipe_results,
        args.spatial_results,
        args.annotations,
        args.audit_result,
        args.output,
    )
    if any(x is None for x in required):
        ap.error(
            "full mode requires --zip --mediapipe-results --spatial-results "
            "--annotations --audit-result --output"
        )

    run_full(args, sess, runtime, model_identity)


if __name__ == "__main__":
    main()
