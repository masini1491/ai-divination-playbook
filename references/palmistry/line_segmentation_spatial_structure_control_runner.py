#!/usr/bin/env python3
"""REFERENCE-ONLY spatial-structure / texture-cue control for palm-line segmentation.

Implements LINE_SEGMENTATION_SPATIAL_STRUCTURE_CONTROL_PLAN.md.
No anatomical truth, palmistry interpretation, or production threshold is
established by this executable.
"""

from __future__ import annotations

import argparse
import json
import math
import zipfile
from pathlib import Path
from typing import Any

import cv2
import numpy as np

import line_segmentation_repeatability_runner as base
import line_segmentation_adapter_diagnosis_runner as adapter
import line_segmentation_content_dependence_control_runner as content

ADAPTER_NAME = "C_G1_M0"
PRIOR_CONTENT_CONTROL_SHA = (
    "317e85351e4141206b28aec5277433ba3caed9a53e3eb01866cd38900699022f"
)
CONDITIONS = (
    "baseline_512",
    "residual_shuffle_64",
    "residual_shuffle_32",
    "residual_sign_flip",
)
SHUFFLE_SPECS = {
    "residual_shuffle_64": {"tile": 64, "mul": 17, "add": 23},
    "residual_shuffle_32": {"tile": 32, "mul": 73, "add": 37},
}


def permutation(tile: int, mul: int, add: int) -> list[int]:
    if 512 % tile:
        raise RuntimeError(f"tile does not divide 512: {tile}")
    side = 512 // tile
    n = side * side
    if math.gcd(mul, n) != 1:
        raise RuntimeError(f"non-bijective permutation spec: mul={mul} n={n}")
    p = [int((mul * d + add) % n) for d in range(n)]
    if len(set(p)) != n:
        raise RuntimeError("tile permutation is not bijective")
    if any(d == s for d, s in enumerate(p)):
        raise RuntimeError("tile permutation contains fixed positions")
    return p


def tile_shuffle(x: np.ndarray, tile: int, mul: int, add: int) -> tuple[np.ndarray, list[int]]:
    if x.shape[0] != 512 or x.shape[1] != 512:
        raise RuntimeError(f"tile shuffle requires 512 frame: {x.shape}")
    p = permutation(tile, mul, add)
    side = 512 // tile
    out = np.empty_like(x)
    for dst, src in enumerate(p):
        dy, dx = divmod(dst, side)
        sy, sx = divmod(src, side)
        out[dy*tile:(dy+1)*tile, dx*tile:(dx+1)*tile, ...] = (
            x[sy*tile:(sy+1)*tile, sx*tile:(sx+1)*tile, ...]
        )
    return out, p


def inverse_tile_shuffle(x: np.ndarray, tile: int, mul: int, add: int) -> np.ndarray:
    p = permutation(tile, mul, add)
    side = 512 // tile
    out = np.empty_like(x)
    for dst, src in enumerate(p):
        dy, dx = divmod(dst, side)
        sy, sx = divmod(src, side)
        out[sy*tile:(sy+1)*tile, sx*tile:(sx+1)*tile, ...] = (
            x[dy*tile:(dy+1)*tile, dx*tile:(dx+1)*tile, ...]
        )
    return out


def lowpass32(baseline: np.ndarray) -> np.ndarray:
    x = cv2.resize(baseline, (32, 32), interpolation=cv2.INTER_AREA)
    x = cv2.resize(x, (512, 512), interpolation=cv2.INTER_LINEAR)
    return np.ascontiguousarray(x, dtype=np.uint8)


def clip_reconstruct(low: np.ndarray, residual: np.ndarray) -> tuple[np.ndarray, float]:
    raw = low.astype(np.int16) + residual.astype(np.int16)
    clipped = np.logical_or(raw < 0, raw > 255)
    rgb = np.clip(raw, 0, 255).astype(np.uint8)
    return np.ascontiguousarray(rgb), float(clipped.mean())


def build_conditions(baseline: np.ndarray) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    if baseline.shape != (512, 512, 3) or baseline.dtype != np.uint8:
        raise RuntimeError(f"baseline contract failed: {baseline.shape} {baseline.dtype}")
    low = lowpass32(baseline)
    residual = baseline.astype(np.int16) - low.astype(np.int16)
    if not np.array_equal(low.astype(np.int16) + residual, baseline.astype(np.int16)):
        raise RuntimeError("integer residual reconstruction failed")

    out: dict[str, np.ndarray] = {"baseline_512": baseline.copy()}
    meta: dict[str, Any] = {
        "lowpass_32_sha256": content.sha256_array(low),
        "residual_mean_abs_0_255": float(np.abs(residual.astype(np.float32)).mean()),
        "residual_max_abs_0_255": int(np.abs(residual).max()),
        "conditions": {
            "baseline_512": {"clipped_fraction": 0.0},
        },
    }

    for name, spec in SHUFFLE_SPECS.items():
        shuffled, p = tile_shuffle(residual, **spec)
        restored = inverse_tile_shuffle(shuffled, **spec)
        if not np.array_equal(restored, residual):
            raise RuntimeError(f"residual permutation inverse failed: {name}")
        if int(np.abs(shuffled).sum(dtype=np.int64)) != int(np.abs(residual).sum(dtype=np.int64)):
            raise RuntimeError(f"residual L1 preservation failed: {name}")
        rgb, clipped = clip_reconstruct(low, shuffled)
        out[name] = rgb
        meta["conditions"][name] = {
            "tile_px": spec["tile"],
            "mul": spec["mul"],
            "add": spec["add"],
            "tile_count": len(p),
            "fixed_tile_positions": sum(i == v for i, v in enumerate(p)),
            "clipped_fraction": clipped,
        }

    flipped_rgb, flipped_clip = clip_reconstruct(low, -residual)
    out["residual_sign_flip"] = flipped_rgb
    meta["conditions"]["residual_sign_flip"] = {
        "clipped_fraction": flipped_clip,
    }
    return out, meta


def validate_prior(path: Path) -> dict[str, Any]:
    got = base.sha256_file(path)
    if got != PRIOR_CONTENT_CONTROL_SHA:
        raise RuntimeError(f"prior content-control SHA mismatch: {got}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("execution") != {
        "selected_sources": 10,
        "conditions_per_source": 4,
        "completed_inferences": 40,
        "baseline_reproduction_failures": 0,
        "stop": False,
    }:
        raise RuntimeError(f"prior content-control execution drift: {data.get('execution')}")
    if data.get("corrected_adapter_diagnosis_raw_sha256") != content.CORRECTED_ADAPTER_DIAGNOSIS_SHA:
        raise RuntimeError("prior corrected-adapter provenance drift")
    if data.get("corrected_repeatability_raw_sha256") != content.CORRECTED_REPEATABILITY_SHA:
        raise RuntimeError("prior corrected-repeatability provenance drift")
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


def summarize(images: list[dict[str, Any]]) -> dict[str, Any]:
    presence: dict[str, Any] = {}
    direct: dict[str, Any] = {}
    inverse_unshuffle: dict[str, Any] = {}
    manipulation: dict[str, Any] = {}
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
            "clipped_fraction": base.num_summary([
                x["control_meta"]["clipped_fraction"] for x in rows
            ]),
        }
        if cond == "baseline_512":
            continue
        classes = {}
        for c in (1, 2, 3):
            rr = [x["comparison_to_baseline"]["classes"][str(c)]["overlap"] for x in rows]
            classes[str(c)] = {"name": base.CLASS_NAMES[c], **overlap_summary(rr)}
        rr = [x["comparison_to_baseline"]["foreground_union"]["overlap"] for x in rows]
        direct[cond] = {"classes": classes, "foreground_union": overlap_summary(rr)}

        if cond in SHUFFLE_SPECS:
            classes = {}
            for c in (1, 2, 3):
                rr = [x["inverse_unshuffle_comparison"]["classes"][str(c)]["overlap"] for x in rows]
                classes[str(c)] = {"name": base.CLASS_NAMES[c], **overlap_summary(rr)}
            rr = [x["inverse_unshuffle_comparison"]["foreground_union"]["overlap"] for x in rows]
            inverse_unshuffle[cond] = {
                "classes": classes,
                "foreground_union": overlap_summary(rr),
            }
    return {
        "presence": presence,
        "manipulation": manipulation,
        "direct_vs_baseline": direct,
        "inverse_unshuffle_vs_baseline": inverse_unshuffle,
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
    baseline = cv2.resize(crop, (512, 512), interpolation=cv2.INTER_LINEAR)
    baseline = np.ascontiguousarray(baseline, dtype=np.uint8)
    conds, control_meta = build_conditions(baseline)
    out = {}
    for name in CONDITIONS:
        mask, logs = content.infer_512(sess, conds[name])
        row = {
            "input_shape": list(conds[name].shape),
            "input_sha256": content.sha256_array(conds[name]),
            "mask_shape": list(mask.shape),
            "mask_values_subset": sorted(int(v) for v in np.unique(mask)),
            "finite_logit_summary": bool(np.isfinite([
                logs["logit_min"], logs["logit_max"], logs["logit_mean"]
            ]).all()),
            "control_meta": control_meta["conditions"][name],
        }
        if name in SHUFFLE_SPECS:
            inv = inverse_tile_shuffle(mask, **SHUFFLE_SPECS[name])
            row["inverse_unshuffle_shape"] = list(inv.shape)
        out[name] = row
    print(json.dumps({
        "mode": "NON-MOHI SPATIAL-STRUCTURE CONTROL DRY RUN",
        "adapter": ADAPTER_NAME,
        "adapter_geometry": meta.get("geometry"),
        "horizontal_mirror": meta.get("horizontal_mirror"),
        "residual_mean_abs_0_255": control_meta["residual_mean_abs_0_255"],
        "conditions": out,
        "schema": "PASS",
    }, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", type=Path, required=True)
    ap.add_argument("--meta", type=Path, required=True)
    ap.add_argument("--zip", type=Path)
    ap.add_argument("--mediapipe-results", type=Path)
    ap.add_argument("--content-control-results", type=Path)
    ap.add_argument("--output", type=Path)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    runtime = base.validate_runtime()
    sess, model_identity = base.validate_model(args.model, args.meta)
    if args.dry_run:
        dry_run(sess)
        return

    if any(x is None for x in (
        args.zip, args.mediapipe_results, args.content_control_results, args.output
    )):
        ap.error("full mode requires --zip --mediapipe-results --content-control-results --output")

    prior = validate_prior(args.content_control_results)
    prior_by_file = {r["file"]: r for r in prior["images"]}
    rows, sha_groups = base.validate_source(args.zip)
    mp_data = base.validate_mediapipe_results(args.mediapipe_results, rows)
    mp_by_file = {r["file"]: r for r in mp_data["images"]}
    selected = base.select_sources(rows, sha_groups)

    output: dict[str, Any] = {
        "status": "REFERENCE-ONLY / PREDECLARED SPATIAL-STRUCTURE CONTROL RAW EVIDENCE",
        "runtime": runtime,
        **model_identity,
        "model": str(args.model),
        "metadata": str(args.meta),
        "source_zip": str(args.zip),
        "source_zip_sha256": base.EXPECTED_ZIP_SHA,
        "mediapipe_results": str(args.mediapipe_results),
        "mediapipe_model_sha256": base.EXPECTED_MP_MODEL_SHA,
        "adapter": ADAPTER_NAME,
        "prior_content_control_raw_sha256": PRIOR_CONTENT_CONTROL_SHA,
        "conditions_contract": list(CONDITIONS),
        "shuffle_specs": SHUFFLE_SPECS,
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
            crop, adapter_meta = adapter.make_adapter(ADAPTER_NAME, rgb, points)
            if adapter_meta.get("geometry") != "G1_reconstructed_upstream_like" or adapter_meta.get("horizontal_mirror") is not False:
                raise RuntimeError(f"corrected C adapter contract drift for {src['file']}")

            baseline = cv2.resize(crop, (512, 512), interpolation=cv2.INTER_LINEAR)
            baseline = np.ascontiguousarray(baseline, dtype=np.uint8)
            conds, control_meta = build_conditions(baseline)
            prior_rec = prior_by_file.get(src["file"])
            if prior_rec is None:
                raise RuntimeError(f"prior content-control source missing: {src['file']}")
            if content.sha256_array(baseline) != prior_rec["conditions"]["baseline_512"]["input_sha256"]:
                raise RuntimeError(f"baseline input reproduction failed: {src['file']}")
            if control_meta["lowpass_32_sha256"] != prior_rec["conditions"]["lowpass_32"]["input_sha256"]:
                raise RuntimeError(f"lowpass_32 anchor reproduction failed: {src['file']}")

            condition_rows: dict[str, Any] = {}
            baseline_mask = None
            for cond in CONDITIONS:
                mask, logs = content.infer_512(sess, conds[cond])
                if baseline_mask is None:
                    baseline_mask = mask
                row: dict[str, Any] = {
                    "input_sha256": content.sha256_array(conds[cond]),
                    "mask_sha256": content.sha256_array(mask),
                    "predicted_classes": content.predicted_classes(mask),
                    "input_stats": content.input_stats(conds[cond], baseline),
                    "logits": logs,
                    "stats": adapter.mask_stats(mask),
                    "control_meta": control_meta["conditions"][cond],
                    "comparison_to_baseline": None if cond == "baseline_512" else base.compare_masks(baseline_mask, mask),
                }
                if cond in SHUFFLE_SPECS:
                    inv_mask = inverse_tile_shuffle(mask, **SHUFFLE_SPECS[cond])
                    row["inverse_unshuffle_mask_sha256"] = content.sha256_array(inv_mask)
                    row["inverse_unshuffle_comparison"] = base.compare_masks(baseline_mask, inv_mask)
                condition_rows[cond] = row
                masks_by_condition[cond].append((src["file"], mask.copy()))

            if baseline_mask is None:
                raise RuntimeError("baseline mask missing")
            prior_base = prior_rec["conditions"]["baseline_512"]
            if content.sha256_array(baseline_mask) != prior_base["mask_sha256"]:
                raise RuntimeError(f"baseline mask reproduction failed: {src['file']}")
            if content.predicted_classes(baseline_mask) != prior_base["predicted_classes"]:
                raise RuntimeError(f"baseline classes reproduction failed: {src['file']}")
            if adapter.mask_stats(baseline_mask) != prior_base["stats"]:
                raise RuntimeError(f"baseline stats reproduction failed: {src['file']}")

            output["images"].append({
                **src,
                "raw_size_hw": [h, w],
                "adapter": adapter_meta,
                "crop_size_hw": list(crop.shape[:2]),
                "anchor_reproduction": {
                    "baseline_input_sha_exact": True,
                    "lowpass_32_input_sha_exact": True,
                    "baseline_mask_sha_exact": True,
                    "baseline_classes_exact": True,
                    "baseline_stats_exact": True,
                },
                "residual": {
                    "mean_abs_0_255": control_meta["residual_mean_abs_0_255"],
                    "max_abs_0_255": control_meta["residual_max_abs_0_255"],
                    "lowpass_32_sha256": control_meta["lowpass_32_sha256"],
                },
                "conditions": condition_rows,
            })
            print(f"[{idx:02d}/10] {src['file']}: baseline + 3 spatial controls complete")

    if len(output["images"]) != 10:
        raise RuntimeError(f"expected 10 completed sources, got {len(output['images'])}")

    output["execution"] = {
        "selected_sources": 10,
        "conditions_per_source": 4,
        "completed_inferences": 40,
        "anchor_reproduction_failures": 0,
        "stop": False,
    }
    output["summary"] = summarize(output["images"])
    output["cross_person_consensus"] = {
        cond: content.cross_person_consensus(masks_by_condition[cond]) for cond in CONDITIONS
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nDONE")
    print(json.dumps(output["execution"], indent=2))
    print(args.output)


if __name__ == "__main__":
    main()
