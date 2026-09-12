#!/usr/bin/env python3
"""REFERENCE-ONLY bounded adapter/domain diagnosis for palm-line segmentation.

Implements LINE_SEGMENTATION_ADAPTER_DOMAIN_DIAGNOSIS_PLAN.md.
No anatomical truth, palmistry interpretation, confidence threshold, or production
admission threshold is established by this executable.
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

ADAPTERS = ("A_G0_M0", "B_G0_M1", "C_G1_M0", "D_G1_M1")
REFERENCE_RESULT_SHA = "396e47b83f040c5a71207fbef287a5c6fd94f55927e448cd0daeb6a24555d9c5"
UPSTREAM_REVISION = "bc48939f4deee6d8ff842bfde499396dab9c4830"
UPSTREAM_FIXED_MARGIN_PX = 100.0


def rotate_points(points: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    return points @ matrix[:, :2].T + matrix[:, 2]


def crop_with_padding(rgb: np.ndarray, x0: int, y0: int, x1: int, y1: int) -> np.ndarray:
    """Crop [x0,y0,x1,y1) with deterministic black padding outside source."""
    h, w = rgb.shape[:2]
    out_w, out_h = max(1, x1 - x0), max(1, y1 - y0)
    out = np.zeros((out_h, out_w, 3), dtype=np.uint8)
    sx0, sy0 = max(0, x0), max(0, y0)
    sx1, sy1 = min(w, x1), min(h, y1)
    if sx1 <= sx0 or sy1 <= sy0:
        raise RuntimeError("adapter crop does not intersect source image")
    dx0, dy0 = sx0 - x0, sy0 - y0
    out[dy0:dy0 + (sy1 - sy0), dx0:dx0 + (sx1 - sx0)] = rgb[sy0:sy1, sx0:sx1]
    return out


def reconstructed_upstream_crop(rgb: np.ndarray, points: np.ndarray) -> tuple[np.ndarray, dict[str, Any]]:
    """Frozen-landmark reconstruction of pinned upstream crop geometry hypothesis."""
    h, w = rgb.shape[:2]
    center = tuple(points.mean(axis=0))
    v = points[9] - points[0]
    if float(np.linalg.norm(v)) <= base.EPS:
        raise RuntimeError("degenerate L0->L9 axis")

    theta = math.degrees(math.atan2(float(v[0]), -float(v[1])))
    best_matrix = None
    best_dx = None
    best_angle = None
    for angle in (theta, -theta):
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rp = rotate_points(points, matrix)
        if rp[9][1] >= rp[0][1]:
            continue
        dx = abs(float(rp[9][0] - rp[0][0]))
        if best_dx is None or dx < best_dx:
            best_dx = dx
            best_matrix = matrix
            best_angle = angle
    if best_matrix is None:
        best_angle = theta
        best_matrix = cv2.getRotationMatrix2D(center, theta, 1.0)

    rp = rotate_points(points, best_matrix)
    mins, maxs = rp.min(axis=0), rp.max(axis=0)
    x0 = math.floor(float(mins[0] - UPSTREAM_FIXED_MARGIN_PX))
    y0 = math.floor(float(mins[1] - UPSTREAM_FIXED_MARGIN_PX))
    x1 = math.ceil(float(maxs[0] + UPSTREAM_FIXED_MARGIN_PX))
    y1 = math.ceil(float(maxs[1] + UPSTREAM_FIXED_MARGIN_PX))

    # Rotate on the original canvas, matching the reconstruction's rotate-first geometry.
    rotated = cv2.warpAffine(
        rgb,
        best_matrix,
        (w, h),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(0, 0, 0),
    )
    crop = crop_with_padding(rotated, x0, y0, x1, y1)
    return crop, {
        "geometry": "G1_reconstructed_upstream_like",
        "source_size_hw": [h, w],
        "rotation_center_xy": [float(center[0]), float(center[1])],
        "rotation_deg": float(best_angle),
        "rotation_matrix": best_matrix.tolist(),
        "rotated_landmark_bbox_xyxy_with_margin": [x0, y0, x1, y1],
        "fixed_margin_px": UPSTREAM_FIXED_MARGIN_PX,
        "crop_size_hw": list(crop.shape[:2]),
        "upstream_revision": UPSTREAM_REVISION,
        "authority_note": "reconstructed geometry hypothesis; not historical-training truth",
    }


def make_adapter(adapter: str, rgb: np.ndarray, points: np.ndarray) -> tuple[np.ndarray, dict[str, Any]]:
    if adapter in ("A_G0_M0", "B_G0_M1"):
        crop, meta = base.crop_palm(rgb, points)
        meta = {**meta, "geometry": "G0_first_study"}
    elif adapter in ("C_G1_M0", "D_G1_M1"):
        crop, meta = reconstructed_upstream_crop(rgb, points)
    else:
        raise KeyError(adapter)

    mirrored = adapter in ("B_G0_M1", "D_G1_M1")
    if mirrored:
        crop = np.ascontiguousarray(crop[:, ::-1, :])
    meta["horizontal_mirror"] = mirrored
    meta["mirror_semantics"] = "deterministic study transform; not anatomical handedness truth"
    return crop, meta


def mask_stats(mask: np.ndarray) -> dict[str, Any]:
    total = int(mask.size)
    classes = {}
    predicted = []
    for c in (1, 2, 3):
        s = base.component_stats(mask == c)
        if s["foreground_px"] > 0:
            predicted.append(base.CLASS_NAMES[c])
        classes[str(c)] = {
            "name": base.CLASS_NAMES[c],
            **s,
            "fraction": float(s["foreground_px"] / total),
            "present": bool(s["foreground_px"] > 0),
        }
    fg = base.component_stats(mask > 0)
    return {
        "classes": classes,
        "foreground_union": {
            **fg,
            "fraction": float(fg["foreground_px"] / total),
            "present": bool(fg["foreground_px"] > 0),
        },
        "predicted_classes": predicted,
    }


def summarize(images: list[dict[str, Any]]) -> dict[str, Any]:
    out = {}
    for adapter in ADAPTERS:
        rows = [r["adapters"][adapter]["stats"] for r in images]
        out[adapter] = {
            "heart_line_presence": sum(r["classes"]["1"]["present"] for r in rows),
            "head_line_presence": sum(r["classes"]["2"]["present"] for r in rows),
            "life_line_presence": sum(r["classes"]["3"]["present"] for r in rows),
            "any_foreground_presence": sum(r["foreground_union"]["present"] for r in rows),
            "all_three_presence": sum(len(r["predicted_classes"]) == 3 for r in rows),
            "foreground_fraction": base.num_summary([r["foreground_union"]["fraction"] for r in rows]),
            "foreground_components": base.num_summary([float(r["foreground_union"]["components"]) for r in rows]),
        }
    return out


def dry_run(sess) -> None:
    h, w = 480, 640
    rgb = np.zeros((h, w, 3), dtype=np.uint8)
    cv2.ellipse(rgb, (320, 280), (120, 145), 0, 0, 360, (180, 145, 125), -1)
    # Synthetic 21-point geometry with wrist below middle MCP.
    pts = np.asarray([
        [320, 420], [275, 365], [250, 320], [235, 270], [225, 220],
        [285, 315], [280, 245], [278, 185], [276, 130],
        [320, 300], [320, 220], [320, 150], [320, 90],
        [355, 315], [362, 245], [368, 185], [372, 135],
        [390, 335], [405, 275], [417, 225], [428, 180],
    ], dtype=np.float64)

    adapters = {}
    for name in ADAPTERS:
        crop, meta = make_adapter(name, rgb, pts)
        mask, logits = base.infer_mask(sess, crop)
        adapters[name] = {
            "crop_shape": list(crop.shape),
            "mask_shape": list(mask.shape),
            "finite_logit_summary": bool(np.isfinite(list(logits.values())).all()),
            "predicted_values_subset": sorted(int(x) for x in np.unique(mask)),
            "horizontal_mirror": meta["horizontal_mirror"],
        }
    print(json.dumps({
        "mode": "NON-MOHI ADAPTER DIAGNOSIS DRY RUN",
        "adapters": adapters,
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

    output = {
        "status": "REFERENCE-ONLY / PREDECLARED ADAPTER-DOMAIN DIAGNOSIS RAW EVIDENCE",
        "runtime": runtime,
        **model_identity,
        "model": str(args.model),
        "metadata": str(args.meta),
        "source_zip": str(args.zip),
        "source_zip_sha256": base.EXPECTED_ZIP_SHA,
        "mediapipe_results": str(args.mediapipe_results),
        "mediapipe_model_sha256": base.EXPECTED_MP_MODEL_SHA,
        "reference_first_study_raw_sha256": REFERENCE_RESULT_SHA,
        "upstream_reconstruction_revision": UPSTREAM_REVISION,
        "adapters_contract": list(ADAPTERS),
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
            rec = {**src, "raw_size_hw": [h, w], "adapters": {}}
            for adapter in ADAPTERS:
                crop, adapter_meta = make_adapter(adapter, rgb, points)
                mask, logits = base.infer_mask(sess, crop)
                rec["adapters"][adapter] = {
                    "adapter": adapter_meta,
                    "crop_size_hw": list(crop.shape[:2]),
                    "logits": logits,
                    "stats": mask_stats(mask),
                }
            output["images"].append(rec)
            print(f"[{idx:02d}/10] {src['file']}: A/B/C/D complete")

    if len(output["images"]) != 10:
        raise RuntimeError(f"expected 10 completed source images, got {len(output['images'])}")
    output["execution"] = {
        "selected_sources": 10,
        "adapters_per_source": 4,
        "completed_inferences": 40,
        "stop": False,
    }
    output["summary"] = summarize(output["images"])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nDONE")
    print(json.dumps(output["execution"], indent=2))
    print(args.output)


if __name__ == "__main__":
    main()
