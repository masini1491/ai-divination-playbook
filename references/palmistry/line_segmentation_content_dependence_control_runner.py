#!/usr/bin/env python3
"""REFERENCE-ONLY palm-line content-dependence / specificity control.

Implements LINE_SEGMENTATION_CONTENT_DEPENDENCE_CONTROL_PLAN.md.
No anatomical truth, palmistry interpretation, or production threshold is
established by this executable.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from itertools import combinations
from pathlib import Path
from typing import Any

import cv2
import numpy as np

import line_segmentation_repeatability_runner as base
import line_segmentation_adapter_diagnosis_runner as adapter

ADAPTER_NAME = "C_G1_M0"
CORRECTED_ADAPTER_DIAGNOSIS_SHA = (
    "c51651cdc267b0416c0883ffba13e1ed0b5992aa808944e1786e2bc20d0e38d3"
)
CORRECTED_REPEATABILITY_SHA = (
    "a1f0293f3662846255f335fe79d060b054852367f60c74fa4d558e6fe825d238"
)
CONDITIONS = ("baseline_512", "lowpass_32", "lowpass_16", "global_mean_rgb")


def sha256_array(x: np.ndarray) -> str:
    a = np.ascontiguousarray(x)
    h = hashlib.sha256()
    h.update(str(a.dtype).encode("ascii"))
    h.update(np.asarray(a.shape, dtype=np.int64).tobytes())
    h.update(a.tobytes())
    return h.hexdigest()


def gradient_energy(rgb: np.ndarray) -> float:
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype(np.float32) / 255.0
    gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    return float(np.sqrt(gx * gx + gy * gy).mean())


def input_stats(rgb: np.ndarray, baseline: np.ndarray) -> dict[str, Any]:
    x = rgb.astype(np.float32)
    b = baseline.astype(np.float32)
    ge = gradient_energy(rgb)
    bge = gradient_energy(baseline)
    return {
        "rgb_mean": [float(v) for v in x.mean(axis=(0, 1))],
        "rgb_std": [float(v) for v in x.std(axis=(0, 1))],
        "mean_abs_difference_from_baseline_0_1": float(np.abs(x - b).mean() / 255.0),
        "sobel_gradient_energy": ge,
        "gradient_energy_ratio_to_baseline": None if bge <= base.EPS else float(ge / bge),
    }


def make_conditions(crop: np.ndarray) -> dict[str, np.ndarray]:
    baseline = cv2.resize(crop, (512, 512), interpolation=cv2.INTER_LINEAR)
    lp32 = cv2.resize(baseline, (32, 32), interpolation=cv2.INTER_AREA)
    lp32 = cv2.resize(lp32, (512, 512), interpolation=cv2.INTER_LINEAR)
    lp16 = cv2.resize(baseline, (16, 16), interpolation=cv2.INTER_AREA)
    lp16 = cv2.resize(lp16, (512, 512), interpolation=cv2.INTER_LINEAR)
    mean_rgb = np.rint(baseline.astype(np.float64).mean(axis=(0, 1))).clip(0, 255).astype(np.uint8)
    global_mean = np.empty_like(baseline)
    global_mean[...] = mean_rgb
    return {
        "baseline_512": np.ascontiguousarray(baseline, dtype=np.uint8),
        "lowpass_32": np.ascontiguousarray(lp32, dtype=np.uint8),
        "lowpass_16": np.ascontiguousarray(lp16, dtype=np.uint8),
        "global_mean_rgb": np.ascontiguousarray(global_mean, dtype=np.uint8),
    }


def infer_512(sess, rgb512: np.ndarray) -> tuple[np.ndarray, dict[str, Any]]:
    if rgb512.shape != (512, 512, 3) or rgb512.dtype != np.uint8:
        raise RuntimeError(f"512 RGB contract failed: {rgb512.shape} {rgb512.dtype}")
    x = rgb512.astype(np.float32) / 255.0
    x = (x - base.MEAN) / base.STD
    x = np.transpose(x, (2, 0, 1))[None, ...]
    x = np.ascontiguousarray(x, dtype=np.float32)
    logits = sess.run(["logits"], {"input": x})[0]
    if logits.shape != (1, 4, 512, 512) or logits.dtype != np.float32 or not np.isfinite(logits).all():
        raise RuntimeError(
            f"invalid logits: shape={logits.shape} dtype={logits.dtype} "
            f"finite={np.isfinite(logits).all()}"
        )
    mask = np.argmax(logits, axis=1)[0].astype(np.uint8)
    class_logits = {}
    for c in range(4):
        z = logits[0, c]
        class_logits[str(c)] = {
            "name": base.CLASS_NAMES[c],
            "mean": float(z.mean()),
            "max": float(z.max()),
            "p95": float(np.percentile(z, 95)),
            "winner_fraction": float(np.mean(mask == c)),
        }
    return mask, {
        "logit_min": float(logits.min()),
        "logit_max": float(logits.max()),
        "logit_mean": float(logits.mean()),
        "by_class": class_logits,
    }


def predicted_classes(mask: np.ndarray) -> list[str]:
    return [base.CLASS_NAMES[c] for c in (1, 2, 3) if np.any(mask == c)]


def validate_repeatability_reference(path: Path) -> dict[str, Any]:
    got = base.sha256_file(path)
    if got != CORRECTED_REPEATABILITY_SHA:
        raise RuntimeError(f"corrected repeatability SHA mismatch: {got}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("adapter_diagnosis_raw_sha256") != CORRECTED_ADAPTER_DIAGNOSIS_SHA:
        raise RuntimeError("corrected repeatability adapter-diagnosis provenance mismatch")
    ex = data.get("execution", {})
    if ex != {
        "selected_sources": 10,
        "conditions_per_source": 6,
        "completed_inferences": 60,
        "stop": False,
    }:
        raise RuntimeError(f"corrected repeatability execution contract mismatch: {ex}")
    return data


def overlap_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    dices = [r["dice"] for r in rows if r["dice"] is not None]
    ious = [r["iou"] for r in rows if r["iou"] is not None]
    return {
        "dice": base.num_summary(dices),
        "iou": base.num_summary(ious),
        "not_applicable_empty_both": sum(r["status"] == "not_applicable_empty_both" for r in rows),
        "appearance_transitions": sum(r["status"] == "appearance_transition" for r in rows),
        "comparable": sum(r["status"] == "comparable" for r in rows),
    }


def cross_person_consensus(mask_rows: list[tuple[str, np.ndarray]]) -> dict[str, Any]:
    out: dict[str, Any] = {"pair_count": 0, "classes": {}}
    pairs = list(combinations(mask_rows, 2))
    out["pair_count"] = len(pairs)
    for c in (1, 2, 3):
        rr = [base.overlap(a[1] == c, b[1] == c) for a, b in pairs]
        out["classes"][str(c)] = {"name": base.CLASS_NAMES[c], **overlap_summary(rr)}
    rr = [base.overlap(a[1] > 0, b[1] > 0) for a, b in pairs]
    out["foreground_union"] = overlap_summary(rr)
    return out


def summarize(images: list[dict[str, Any]]) -> dict[str, Any]:
    presence = {}
    manipulation = {}
    within_baseline = {}
    for cond in CONDITIONS:
        rows = [r["conditions"][cond] for r in images]
        presence[cond] = {
            "heart_line_presence": sum("heart_line" in x["predicted_classes"] for x in rows),
            "head_line_presence": sum("head_line" in x["predicted_classes"] for x in rows),
            "life_line_presence": sum("life_line" in x["predicted_classes"] for x in rows),
            "all_three_presence": sum(len(x["predicted_classes"]) == 3 for x in rows),
            "any_foreground_presence": sum(bool(x["predicted_classes"]) for x in rows),
            "foreground_fraction": base.num_summary([
                x["stats"]["foreground_union"]["fraction"] for x in rows
            ]),
        }
        manipulation[cond] = {
            "mean_abs_difference_from_baseline_0_1": base.num_summary([
                x["input_stats"]["mean_abs_difference_from_baseline_0_1"] for x in rows
            ]),
            "sobel_gradient_energy": base.num_summary([
                x["input_stats"]["sobel_gradient_energy"] for x in rows
            ]),
            "gradient_energy_ratio_to_baseline": base.num_summary([
                x["input_stats"]["gradient_energy_ratio_to_baseline"] for x in rows
                if x["input_stats"]["gradient_energy_ratio_to_baseline"] is not None
            ]),
        }
        if cond == "baseline_512":
            continue
        classes = {}
        for c in (1, 2, 3):
            rr = [x["comparison_to_baseline"]["classes"][str(c)]["overlap"] for x in rows]
            classes[str(c)] = {"name": base.CLASS_NAMES[c], **overlap_summary(rr)}
        rr = [x["comparison_to_baseline"]["foreground_union"]["overlap"] for x in rows]
        within_baseline[cond] = {
            "classes": classes,
            "foreground_union": overlap_summary(rr),
        }
    return {
        "presence": presence,
        "manipulation": manipulation,
        "within_baseline": within_baseline,
    }


def dry_run(sess) -> None:
    rgb = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.ellipse(rgb, (320, 280), (120, 145), 0, 0, 360, (180, 145, 125), -1)
    pts = np.asarray([
        [320, 420], [275, 365], [250, 320], [235, 270], [225, 220],
        [285, 315], [280, 245], [278, 185], [276, 130],
        [320, 300], [320, 220], [320, 150], [320, 90],
        [355, 315], [362, 245], [368, 185], [372, 135],
        [390, 335], [405, 275], [417, 225], [428, 180],
    ], dtype=np.float64)
    crop, meta = adapter.make_adapter(ADAPTER_NAME, rgb, pts)
    conds = make_conditions(crop)
    baseline = conds["baseline_512"]
    out = {}
    for name in CONDITIONS:
        mask, logs = infer_512(sess, conds[name])
        out[name] = {
            "input_shape": list(conds[name].shape),
            "input_sha256": sha256_array(conds[name]),
            "mask_shape": list(mask.shape),
            "mask_values_subset": sorted(int(v) for v in np.unique(mask)),
            "finite_logit_summary": bool(np.isfinite([
                logs["logit_min"], logs["logit_max"], logs["logit_mean"]
            ]).all()),
            "input_stats": input_stats(conds[name], baseline),
        }
    print(json.dumps({
        "mode": "NON-MOHI CONTENT-DEPENDENCE CONTROL DRY RUN",
        "adapter": ADAPTER_NAME,
        "adapter_geometry": meta.get("geometry"),
        "horizontal_mirror": meta.get("horizontal_mirror"),
        "conditions": out,
        "schema": "PASS",
    }, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", type=Path, required=True)
    ap.add_argument("--meta", type=Path, required=True)
    ap.add_argument("--zip", type=Path)
    ap.add_argument("--mediapipe-results", type=Path)
    ap.add_argument("--repeatability-results", type=Path)
    ap.add_argument("--output", type=Path)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    runtime = base.validate_runtime()
    sess, model_identity = base.validate_model(args.model, args.meta)
    if args.dry_run:
        dry_run(sess)
        return

    if any(x is None for x in (
        args.zip, args.mediapipe_results, args.repeatability_results, args.output
    )):
        ap.error("full mode requires --zip --mediapipe-results --repeatability-results --output")

    repeat = validate_repeatability_reference(args.repeatability_results)
    repeat_by_file = {r["file"]: r for r in repeat["images"]}
    rows, sha_groups = base.validate_source(args.zip)
    mp_data = base.validate_mediapipe_results(args.mediapipe_results, rows)
    mp_by_file = {r["file"]: r for r in mp_data["images"]}
    selected = base.select_sources(rows, sha_groups)

    output: dict[str, Any] = {
        "status": "REFERENCE-ONLY / PREDECLARED CONTENT-DEPENDENCE CONTROL RAW EVIDENCE",
        "runtime": runtime,
        **model_identity,
        "model": str(args.model),
        "metadata": str(args.meta),
        "source_zip": str(args.zip),
        "source_zip_sha256": base.EXPECTED_ZIP_SHA,
        "mediapipe_results": str(args.mediapipe_results),
        "mediapipe_model_sha256": base.EXPECTED_MP_MODEL_SHA,
        "adapter": ADAPTER_NAME,
        "corrected_adapter_diagnosis_raw_sha256": CORRECTED_ADAPTER_DIAGNOSIS_SHA,
        "corrected_repeatability_raw_sha256": CORRECTED_REPEATABILITY_SHA,
        "conditions_contract": list(CONDITIONS),
        "images": [],
    }

    masks_by_condition: dict[str, list[tuple[str, np.ndarray]]] = {c: [] for c in CONDITIONS}
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
                raise RuntimeError(f"raw frame mismatch for {src['file']}")
            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            points = base.mp_points(mp_rec)
            crop, meta = adapter.make_adapter(ADAPTER_NAME, rgb, points)
            if meta.get("geometry") != "G1_reconstructed_upstream_like" or meta.get("horizontal_mirror") is not False:
                raise RuntimeError(f"corrected C adapter contract drift for {src['file']}")

            conds = make_conditions(crop)
            baseline_rgb = conds["baseline_512"]
            condition_rows: dict[str, Any] = {}
            baseline_mask = None
            for cond in CONDITIONS:
                mask, logs = infer_512(sess, conds[cond])
                if baseline_mask is None:
                    baseline_mask = mask
                row = {
                    "input_sha256": sha256_array(conds[cond]),
                    "mask_sha256": sha256_array(mask),
                    "predicted_classes": predicted_classes(mask),
                    "input_stats": input_stats(conds[cond], baseline_rgb),
                    "logits": logs,
                    "stats": adapter.mask_stats(mask),
                    "comparison_to_baseline": None if cond == "baseline_512" else base.compare_masks(baseline_mask, mask),
                }
                condition_rows[cond] = row
                masks_by_condition[cond].append((src["file"], mask.copy()))

            if baseline_mask is None:
                raise RuntimeError("baseline mask missing")
            native_mask = cv2.resize(
                baseline_mask, (crop.shape[1], crop.shape[0]), interpolation=cv2.INTER_NEAREST
            )
            native_stats = adapter.mask_stats(native_mask)
            ref = repeat_by_file.get(src["file"])
            if ref is None:
                raise RuntimeError(f"repeatability reference missing {src['file']}")
            if predicted_classes(native_mask) != ref["baseline"]["predicted_classes"]:
                raise RuntimeError(f"baseline class reproduction failed for {src['file']}")
            if native_stats != ref["baseline"]["stats"]:
                raise RuntimeError(f"baseline mask-stat reproduction failed for {src['file']}")

            output["images"].append({
                **src,
                "raw_size_hw": [h, w],
                "adapter": meta,
                "crop_size_hw": list(crop.shape[:2]),
                "baseline_reproduction": {
                    "reference_file": src["file"],
                    "predicted_classes_exact": True,
                    "mask_stats_exact": True,
                },
                "conditions": condition_rows,
            })
            print(f"[{idx:02d}/10] {src['file']}: baseline + 3 content controls complete")

    if len(output["images"]) != 10:
        raise RuntimeError(f"expected 10 completed sources, got {len(output['images'])}")

    output["execution"] = {
        "selected_sources": 10,
        "conditions_per_source": 4,
        "completed_inferences": 40,
        "baseline_reproduction_failures": 0,
        "stop": False,
    }
    output["summary"] = summarize(output["images"])
    output["cross_person_consensus"] = {
        cond: cross_person_consensus(masks_by_condition[cond]) for cond in CONDITIONS
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nDONE")
    print(json.dumps(output["execution"], indent=2))
    print(args.output)


if __name__ == "__main__":
    main()
