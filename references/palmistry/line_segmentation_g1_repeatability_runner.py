#!/usr/bin/env python3
"""REFERENCE-ONLY G1 repeatability qualification for palm-line segmentation.

Implements LINE_SEGMENTATION_G1_REPEATABILITY_PLAN.md. Uses the frozen C_G1_M0
adapter from line_segmentation_adapter_diagnosis_runner.py and the same model,
runtime, source, perturbation family, overlap metrics and summary semantics as
the first repeatability study. No anatomical truth or production threshold is
established by this executable.
"""

from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path
from typing import Any

import cv2
import numpy as np

import line_segmentation_repeatability_runner as base
import line_segmentation_adapter_diagnosis_runner as adapter

ADAPTER_NAME = "C_G1_M0"
REFERENCE_ADAPTER_DIAGNOSIS_SHA = "83becc491dbebbe9cbf053a023f43303750b6e38d6a9cc662f1718cf8f30f423"
VARIANTS = ("rotate_p5", "rotate_m5", "scale_090", "scale_110", "center_crop_3pct")


def variant_matrix_rect(name: str, width: int, height: int) -> np.ndarray:
    center = ((width - 1) / 2.0, (height - 1) / 2.0)
    if name == "rotate_p5":
        return cv2.getRotationMatrix2D(center, 5.0, 1.0)
    if name == "rotate_m5":
        return cv2.getRotationMatrix2D(center, -5.0, 1.0)
    if name == "scale_090":
        return cv2.getRotationMatrix2D(center, 0.0, 0.90)
    if name == "scale_110":
        return cv2.getRotationMatrix2D(center, 0.0, 1.10)
    if name == "center_crop_3pct":
        lx = 0.03 * width
        ly = 0.03 * height
        sx = width / (0.94 * width)
        sy = height / (0.94 * height)
        return np.asarray(
            [[sx, 0.0, -lx * sx], [0.0, sy, -ly * sy]],
            dtype=np.float64,
        )
    raise KeyError(name)


def apply_variant_rect(rgb: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    h, w = rgb.shape[:2]
    return cv2.warpAffine(
        rgb,
        matrix,
        (w, h),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(0, 0, 0),
    )


def inverse_map_mask_rect(mask: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    h, w = mask.shape[:2]
    inv = cv2.invertAffineTransform(matrix)
    return cv2.warpAffine(
        mask,
        inv,
        (w, h),
        flags=cv2.INTER_NEAREST,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=0,
    )


def predicted_classes(mask: np.ndarray) -> list[str]:
    return [base.CLASS_NAMES[c] for c in (1, 2, 3) if np.any(mask == c)]


def summarize_presence(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_variant = {}
    for variant in VARIANTS:
        rr = [r["variants"][variant] for r in records]
        by_variant[variant] = {
            "heart_line_presence": sum("heart_line" in x["predicted_classes"] for x in rr),
            "head_line_presence": sum("head_line" in x["predicted_classes"] for x in rr),
            "life_line_presence": sum("life_line" in x["predicted_classes"] for x in rr),
            "all_three_presence": sum(len(x["predicted_classes"]) == 3 for x in rr),
            "any_foreground_presence": sum(bool(x["predicted_classes"]) for x in rr),
        }
    baseline = {
        "heart_line_presence": sum("heart_line" in r["baseline"]["predicted_classes"] for r in records),
        "head_line_presence": sum("head_line" in r["baseline"]["predicted_classes"] for r in records),
        "life_line_presence": sum("life_line" in r["baseline"]["predicted_classes"] for r in records),
        "all_three_presence": sum(len(r["baseline"]["predicted_classes"]) == 3 for r in records),
        "any_foreground_presence": sum(bool(r["baseline"]["predicted_classes"]) for r in records),
    }
    return {"baseline": baseline, "by_variant": by_variant}


def dry_run(sess) -> None:
    h, w = 480, 640
    rgb = np.zeros((h, w, 3), dtype=np.uint8)
    cv2.ellipse(rgb, (320, 280), (120, 145), 0, 0, 360, (180, 145, 125), -1)
    pts = np.asarray([
        [320, 420], [275, 365], [250, 320], [235, 270], [225, 220],
        [285, 315], [280, 245], [278, 185], [276, 130],
        [320, 300], [320, 220], [320, 150], [320, 90],
        [355, 315], [362, 245], [368, 185], [372, 135],
        [390, 335], [405, 275], [417, 225], [428, 180],
    ], dtype=np.float64)
    crop, meta = adapter.make_adapter(ADAPTER_NAME, rgb, pts)
    baseline, logs = base.infer_mask(sess, crop)
    ch, cw = crop.shape[:2]
    variants = {}
    for name in VARIANTS:
        matrix = variant_matrix_rect(name, cw, ch)
        vrgb = apply_variant_rect(crop, matrix)
        vmask, _ = base.infer_mask(sess, vrgb)
        mapped = inverse_map_mask_rect(vmask, matrix)
        variants[name] = {
            "matrix_shape": list(matrix.shape),
            "variant_shape": list(vrgb.shape),
            "mapped_shape": list(mapped.shape),
            "mapped_values_subset": sorted(int(x) for x in np.unique(mapped)),
        }
    print(json.dumps({
        "mode": "NON-MOHI G1 REPEATABILITY DRY RUN",
        "adapter": ADAPTER_NAME,
        "crop_shape": list(crop.shape),
        "adapter_geometry": meta.get("geometry"),
        "horizontal_mirror": meta.get("horizontal_mirror"),
        "baseline_shape": list(baseline.shape),
        "baseline_values_subset": sorted(int(x) for x in np.unique(baseline)),
        "finite_logit_summary": bool(np.isfinite(list(logs.values())).all()),
        "variants": variants,
        "schema": "PASS",
    }, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", type=Path, required=True)
    ap.add_argument("--meta", type=Path, required=True)
    ap.add_argument("--zip", type=Path)
    ap.add_argument("--mediapipe-results", type=Path)
    ap.add_argument("--output", type=Path)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    runtime = base.validate_runtime()
    sess, model_identity = base.validate_model(args.model, args.meta)
    if args.dry_run:
        dry_run(sess)
        return

    if args.zip is None or args.mediapipe_results is None or args.output is None:
        ap.error("full mode requires --zip --mediapipe-results --output")

    rows, sha_groups = base.validate_source(args.zip)
    mp_data = base.validate_mediapipe_results(args.mediapipe_results, rows)
    mp_by_file = {r["file"]: r for r in mp_data["images"]}
    selected = base.select_sources(rows, sha_groups)

    output: dict[str, Any] = {
        "status": "REFERENCE-ONLY / PREDECLARED G1 REPEATABILITY RAW EVIDENCE",
        "runtime": runtime,
        **model_identity,
        "model": str(args.model),
        "metadata": str(args.meta),
        "source_zip": str(args.zip),
        "source_zip_sha256": base.EXPECTED_ZIP_SHA,
        "mediapipe_results": str(args.mediapipe_results),
        "mediapipe_model_sha256": base.EXPECTED_MP_MODEL_SHA,
        "adapter": ADAPTER_NAME,
        "adapter_diagnosis_raw_sha256": REFERENCE_ADAPTER_DIAGNOSIS_SHA,
        "upstream_reconstruction_revision": adapter.UPSTREAM_REVISION,
        "variants_contract": list(VARIANTS),
        "images": [],
    }

    decode_flag = cv2.IMREAD_COLOR | cv2.IMREAD_IGNORE_ORIENTATION
    with zipfile.ZipFile(args.zip) as zf:
        for idx, src in enumerate(selected, 1):
            data = zf.read(src["file"])
            bgr = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), decode_flag)
            if bgr is None:
                raise RuntimeError(f"decode failed: {src['file']}")
            h, w = bgr.shape[:2]
            mp_rec = mp_by_file[src["file"]]
            if mp_rec.get("raw") != [h, w]:
                raise RuntimeError(f"raw frame mismatch for {src['file']}: decoded={[h,w]} mp={mp_rec.get('raw')}")
            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            points = base.mp_points(mp_rec)

            crop, adapter_meta = adapter.make_adapter(ADAPTER_NAME, rgb, points)
            if adapter_meta.get("geometry") != "G1_reconstructed_upstream_like" or adapter_meta.get("horizontal_mirror") is not False:
                raise RuntimeError(f"C_G1_M0 adapter contract drift for {src['file']}")

            baseline_mask, baseline_logits = base.infer_mask(sess, crop)
            rec: dict[str, Any] = {
                **src,
                "raw_size_hw": [h, w],
                "adapter": adapter_meta,
                "crop_size_hw": list(crop.shape[:2]),
                "baseline": {
                    "logits": baseline_logits,
                    "stats": adapter.mask_stats(baseline_mask),
                    "predicted_classes": predicted_classes(baseline_mask),
                },
                "variants": {},
            }

            ch, cw = crop.shape[:2]
            for name in VARIANTS:
                matrix = variant_matrix_rect(name, cw, ch)
                vrgb = apply_variant_rect(crop, matrix)
                vmask, vlogits = base.infer_mask(sess, vrgb)
                mapped = inverse_map_mask_rect(vmask, matrix)
                rec["variants"][name] = {
                    "forward_matrix": matrix.tolist(),
                    "inverse_matrix": cv2.invertAffineTransform(matrix).tolist(),
                    "variant_size_hw": list(vrgb.shape[:2]),
                    "logits": vlogits,
                    "predicted_classes": predicted_classes(vmask),
                    "mapped_predicted_classes": predicted_classes(mapped),
                    "comparison": base.compare_masks(baseline_mask, mapped),
                    "variant_stats": adapter.mask_stats(vmask),
                    "mapped_stats": adapter.mask_stats(mapped),
                }

            output["images"].append(rec)
            print(f"[{idx:02d}/10] {src['file']}: baseline + 5 perturbations complete")

    if len(output["images"]) != 10:
        raise RuntimeError(f"expected 10 completed source images, got {len(output['images'])}")

    output["execution"] = {
        "selected_sources": 10,
        "conditions_per_source": 6,
        "completed_inferences": 60,
        "stop": False,
    }
    output["presence_summary"] = summarize_presence(output["images"])
    output["summary"] = base.summarize(output["images"])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nDONE")
    print(json.dumps(output["execution"], indent=2))
    print(args.output)


if __name__ == "__main__":
    main()
