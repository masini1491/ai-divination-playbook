#!/usr/bin/env python3
"""Cold runner for bounded palm-line segmentation repeatability research.

REFERENCE-ONLY. This executable implements LINE_SEGMENTATION_REPEATABILITY_PLAN.md.
It measures stability of the shipped tool-local heart/head/life segmentation
classes under frozen image-space perturbations. It does not establish line truth,
Chinese-palmistry terminology equivalence, or production thresholds.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import platform
import sys
import zipfile
from collections import defaultdict, deque
from importlib import metadata
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import onnxruntime as ort

EXPECTED = {
    "python": "3.11.16",
    "numpy": "1.26.4",
    "opencv-python": "4.10.0.84",
    "onnxruntime": "1.29.0",
}
EXPECTED_ZIP_SHA = "6309f2390b0013858928c6c77344b4aa869edc8c0aeb9a61db93b73ae83feec2"
EXPECTED_MP_MODEL_SHA = "fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1"
EXPECTED_MODEL_SHA = "3c02b88b82e54889d0ab2bf2ba108aec554a1b50759f7c7aaa45f2f114ed24ff"
EXPECTED_META_SHA = "880b17a1f0ae8f0ad9c4061b0674e86381f50fadb242a662b44fdbaf4b919a98"
SELECTED = [f"P{i:03d}/S1/01.jpg" for i in range(1, 11)]
CLASS_NAMES = {0: "background", 1: "heart_line", 2: "head_line", 3: "life_line"}
MEAN = np.asarray([0.485, 0.456, 0.406], dtype=np.float32)
STD = np.asarray([0.229, 0.224, 0.225], dtype=np.float32)
EPS = 1e-12


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def package_version(name: str) -> str:
    return metadata.version(name)


def validate_runtime() -> dict[str, Any]:
    observed = {
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "opencv-python": package_version("opencv-python"),
        "cv2": cv2.__version__,
        "onnxruntime": ort.__version__,
        "available_providers": ort.get_available_providers(),
    }
    mismatches = {}
    for key, want in EXPECTED.items():
        got = observed[key]
        if got != want:
            mismatches[key] = {"expected": want, "actual": got}
    if "CPUExecutionProvider" not in observed["available_providers"]:
        mismatches["CPUExecutionProvider"] = {"expected": True, "actual": False}
    if mismatches:
        raise RuntimeError(f"runtime lock mismatch: {json.dumps(mismatches, indent=2)}")
    return observed


def validate_model(model_path: Path, meta_path: Path) -> tuple[ort.InferenceSession, dict[str, Any]]:
    model_sha = sha256_file(model_path)
    meta_sha = sha256_file(meta_path)
    if model_sha != EXPECTED_MODEL_SHA:
        raise RuntimeError(f"model SHA mismatch: {model_sha}")
    if meta_sha != EXPECTED_META_SHA:
        raise RuntimeError(f"metadata SHA mismatch: {meta_sha}")

    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    if meta.get("input", {}).get("name") != "input":
        raise RuntimeError("metadata input name drift")
    if meta.get("input", {}).get("shape") != [1, 3, 512, 512]:
        raise RuntimeError("metadata input shape drift")
    if meta.get("output", {}).get("name") != "logits":
        raise RuntimeError("metadata output name drift")
    if meta.get("output", {}).get("shape") != [1, 4, 512, 512]:
        raise RuntimeError("metadata output shape drift")
    classes = [(x.get("index"), x.get("name")) for x in meta.get("classes", [])]
    if classes != [(0, "background"), (1, "heart_line"), (2, "head_line"), (3, "life_line")]:
        raise RuntimeError(f"metadata class order drift: {classes}")

    sess = ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])
    if sess.get_providers() != ["CPUExecutionProvider"]:
        raise RuntimeError(f"unexpected session providers: {sess.get_providers()}")
    ins, outs = sess.get_inputs(), sess.get_outputs()
    if len(ins) != 1 or (ins[0].name, ins[0].shape, ins[0].type) != (
        "input", [1, 3, 512, 512], "tensor(float)"
    ):
        raise RuntimeError(f"model input contract drift: {[(x.name, x.shape, x.type) for x in ins]}")
    if len(outs) != 1 or (outs[0].name, outs[0].shape, outs[0].type) != (
        "logits", [1, 4, 512, 512], "tensor(float)"
    ):
        raise RuntimeError(f"model output contract drift: {[(x.name, x.shape, x.type) for x in outs]}")

    return sess, {
        "model_sha256": model_sha,
        "metadata_sha256": meta_sha,
        "session_providers": sess.get_providers(),
    }


def load_manifest(zf: zipfile.ZipFile) -> list[dict[str, Any]]:
    if "manifest.tsv" not in zf.namelist():
        raise RuntimeError("manifest.tsv missing")
    rows = list(csv.DictReader(io.StringIO(zf.read("manifest.tsv").decode("utf-8")), delimiter="\t"))
    required = {"sample_path", "dataset_person_id", "session", "image_index", "sha256"}
    if not rows or not required.issubset(rows[0]):
        raise RuntimeError("manifest missing required columns")
    out = []
    for r in rows:
        out.append({
            "file": r["sample_path"],
            "p": int(r["dataset_person_id"]),
            "s": int(r["session"]),
            "i": int(r["image_index"]),
            "sha256": r["sha256"].strip().lower(),
        })
    return out


def validate_source(zip_path: Path) -> tuple[list[dict[str, Any]], dict[str, list[str]]]:
    got_zip = sha256_file(zip_path)
    if got_zip != EXPECTED_ZIP_SHA:
        raise RuntimeError(f"MOHI ZIP SHA mismatch: {got_zip}")
    with zipfile.ZipFile(zip_path) as zf:
        rows = load_manifest(zf)
        if len(rows) != 150 or len({r["p"] for r in rows}) != 10:
            raise RuntimeError(f"unexpected manifest structure: rows={len(rows)} persons={len({r['p'] for r in rows})}")
        names = set(zf.namelist())
        sha_groups: dict[str, list[str]] = defaultdict(list)
        for r in rows:
            if r["file"] not in names:
                raise RuntimeError(f"missing ZIP entry: {r['file']}")
            data = zf.read(r["file"])
            got = sha256_bytes(data)
            if got != r["sha256"]:
                raise RuntimeError(f"manifest SHA mismatch: {r['file']}")
            sha_groups[got].append(r["file"])
    return rows, dict(sha_groups)


def validate_mediapipe_results(path: Path, rows: list[dict[str, Any]]) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("zip_sha256") != EXPECTED_ZIP_SHA:
        raise RuntimeError("MediaPipe evidence ZIP SHA mismatch")
    if data.get("model_sha256") != EXPECTED_MP_MODEL_SHA:
        raise RuntimeError("MediaPipe model SHA mismatch")
    if data.get("mediapipe") != "1.0.1":
        raise RuntimeError("MediaPipe version mismatch")
    images = data.get("images", [])
    if len(images) != 150:
        raise RuntimeError(f"MediaPipe evidence must contain 150 images, got {len(images)}")
    by_file = {r.get("file"): r for r in images}
    for src in rows:
        rec = by_file.get(src["file"])
        if not rec or not rec.get("usable"):
            raise RuntimeError(f"MediaPipe frozen evidence unusable for {src['file']}")
        lm = rec.get("hand", {}).get("lm")
        if not isinstance(lm, list) or len(lm) != 21:
            raise RuntimeError(f"MediaPipe landmark contract failed for {src['file']}")
    return data


def select_sources(rows: list[dict[str, Any]], sha_groups: dict[str, list[str]]) -> list[dict[str, Any]]:
    by_file = {r["file"]: r for r in rows}
    chosen = []
    chosen_sha = set()
    by_person: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        by_person[r["p"]].append(r)
    for p in range(1, 11):
        preferred = f"P{p:03d}/S1/01.jpg"
        candidates = sorted(by_person[p], key=lambda r: r["file"])
        ordered = [by_file[preferred]] + [r for r in candidates if r["file"] != preferred]
        pick = None
        for r in ordered:
            if r["sha256"] not in chosen_sha:
                pick = r
                break
        if pick is None:
            raise RuntimeError(f"no unique source available for person {p}")
        chosen.append(pick)
        chosen_sha.add(pick["sha256"])
    if len(chosen) != 10 or len(chosen_sha) != 10:
        raise RuntimeError("selected-source uniqueness contract failed")
    return chosen


def mp_points(rec: dict[str, Any]) -> np.ndarray:
    pts = np.asarray([[float(v[0]), float(v[1])] for v in rec["hand"]["lm"]], dtype=np.float64)
    if pts.shape != (21, 2) or not np.isfinite(pts).all():
        raise RuntimeError("21 finite MediaPipe raw landmarks required")
    return pts


def crop_palm(rgb: np.ndarray, points: np.ndarray) -> tuple[np.ndarray, dict[str, Any]]:
    """Create deterministic immutable square palm crop from frozen raw landmarks."""
    h, w = rgb.shape[:2]
    mins = points.min(axis=0)
    maxs = points.max(axis=0)
    bw, bh = maxs - mins
    margin = 0.15 * max(float(bw), float(bh))
    x0f, y0f = mins[0] - margin, mins[1] - margin
    x1f, y1f = maxs[0] + margin, maxs[1] + margin
    x0, y0 = math.floor(x0f), math.floor(y0f)
    x1, y1 = math.ceil(x1f), math.ceil(y1f)
    roi_w, roi_h = max(1, x1 - x0), max(1, y1 - y0)

    roi = np.zeros((roi_h, roi_w, 3), dtype=np.uint8)
    sx0, sy0 = max(0, x0), max(0, y0)
    sx1, sy1 = min(w, x1), min(h, y1)
    if sx1 <= sx0 or sy1 <= sy0:
        raise RuntimeError("expanded landmark ROI does not intersect source image")
    dx0, dy0 = sx0 - x0, sy0 - y0
    roi[dy0:dy0 + (sy1 - sy0), dx0:dx0 + (sx1 - sx0)] = rgb[sy0:sy1, sx0:sx1]

    p = points - np.asarray([x0, y0], dtype=np.float64)
    v = p[9] - p[0]
    if float(np.linalg.norm(v)) <= EPS:
        raise RuntimeError("degenerate L0->L9 crop axis")
    theta = math.degrees(math.atan2(float(v[1]), float(v[0])))
    rotate_deg = -90.0 - theta
    center = ((roi_w - 1) / 2.0, (roi_h - 1) / 2.0)
    M = cv2.getRotationMatrix2D(center, rotate_deg, 1.0)

    corners = np.asarray(
        [[0, 0], [roi_w - 1, 0], [roi_w - 1, roi_h - 1], [0, roi_h - 1]],
        dtype=np.float64,
    )
    rc = corners @ M[:, :2].T + M[:, 2]
    minc, maxc = rc.min(axis=0), rc.max(axis=0)
    out_w = int(math.ceil(maxc[0] - minc[0] + 1.0))
    out_h = int(math.ceil(maxc[1] - minc[1] + 1.0))
    M2 = M.copy()
    M2[0, 2] -= minc[0]
    M2[1, 2] -= minc[1]
    rotated = cv2.warpAffine(
        roi, M2, (out_w, out_h), flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0)
    )

    side = max(out_w, out_h)
    square = np.zeros((side, side, 3), dtype=np.uint8)
    ox = (side - out_w) // 2
    oy = (side - out_h) // 2
    square[oy:oy + out_h, ox:ox + out_w] = rotated

    return square, {
        "source_size_hw": [h, w],
        "expanded_roi_xyxy_int": [x0, y0, x1, y1],
        "margin_px_float": margin,
        "rotation_deg": rotate_deg,
        "rotated_size_hw": [out_h, out_w],
        "square_size": side,
        "square_offset_xy": [ox, oy],
        "roi_rotation_matrix": M2.tolist(),
    }


def preprocess(rgb: np.ndarray) -> np.ndarray:
    x = cv2.resize(rgb, (512, 512), interpolation=cv2.INTER_LINEAR).astype(np.float32) / 255.0
    x = (x - MEAN) / STD
    x = np.transpose(x, (2, 0, 1))[None, ...]
    return np.ascontiguousarray(x, dtype=np.float32)


def infer_mask(sess: ort.InferenceSession, rgb: np.ndarray) -> tuple[np.ndarray, dict[str, float]]:
    logits = sess.run(["logits"], {"input": preprocess(rgb)})[0]
    if logits.shape != (1, 4, 512, 512) or logits.dtype != np.float32 or not np.isfinite(logits).all():
        raise RuntimeError(f"invalid logits: shape={logits.shape} dtype={logits.dtype} finite={np.isfinite(logits).all()}")
    mask512 = np.argmax(logits, axis=1)[0].astype(np.uint8)
    mask = cv2.resize(mask512, (rgb.shape[1], rgb.shape[0]), interpolation=cv2.INTER_NEAREST)
    return mask, {
        "logit_min": float(logits.min()),
        "logit_max": float(logits.max()),
        "logit_mean": float(logits.mean()),
    }


def variant_matrix(name: str, side: int) -> np.ndarray:
    center = ((side - 1) / 2.0, (side - 1) / 2.0)
    if name == "rotate_p5":
        return cv2.getRotationMatrix2D(center, 5.0, 1.0)
    if name == "rotate_m5":
        return cv2.getRotationMatrix2D(center, -5.0, 1.0)
    if name == "scale_090":
        return cv2.getRotationMatrix2D(center, 0.0, 0.90)
    if name == "scale_110":
        return cv2.getRotationMatrix2D(center, 0.0, 1.10)
    if name == "center_crop_3pct":
        # Crop 3% from each side and resize the remaining 94% back to full size.
        lo = 0.03 * side
        span = 0.94 * side
        s = side / span
        return np.asarray([[s, 0.0, -lo * s], [0.0, s, -lo * s]], dtype=np.float64)
    raise KeyError(name)


def apply_variant(rgb: np.ndarray, M: np.ndarray) -> np.ndarray:
    side = rgb.shape[0]
    return cv2.warpAffine(
        rgb, M, (side, side), flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0)
    )


def inverse_map_mask(mask: np.ndarray, M: np.ndarray) -> np.ndarray:
    side = mask.shape[0]
    Minv = cv2.invertAffineTransform(M)
    return cv2.warpAffine(
        mask, Minv, (side, side), flags=cv2.INTER_NEAREST,
        borderMode=cv2.BORDER_CONSTANT, borderValue=0
    )


def overlap(a: np.ndarray, b: np.ndarray) -> dict[str, Any]:
    aa, bb = a.astype(bool), b.astype(bool)
    na, nb = int(aa.sum()), int(bb.sum())
    if na == 0 and nb == 0:
        return {"status": "not_applicable_empty_both", "dice": None, "iou": None, "a_px": 0, "b_px": 0}
    if na == 0 or nb == 0:
        return {"status": "appearance_transition", "dice": 0.0, "iou": 0.0, "a_px": na, "b_px": nb}
    inter = int(np.logical_and(aa, bb).sum())
    union = int(np.logical_or(aa, bb).sum())
    return {
        "status": "comparable",
        "dice": float(2.0 * inter / (na + nb)),
        "iou": float(inter / union),
        "a_px": na,
        "b_px": nb,
        "intersection_px": inter,
        "union_px": union,
    }


def component_stats(binary: np.ndarray) -> dict[str, Any]:
    img = binary.astype(np.uint8)
    n, _, stats, _ = cv2.connectedComponentsWithStats(img, connectivity=8)
    areas = [int(stats[i, cv2.CC_STAT_AREA]) for i in range(1, n)]
    total = int(img.sum())
    return {
        "components": len(areas),
        "foreground_px": total,
        "largest_component_fraction": None if total == 0 else float(max(areas) / total),
    }


def compare_masks(baseline: np.ndarray, mapped: np.ndarray) -> dict[str, Any]:
    out = {"classes": {}}
    for c in (1, 2, 3):
        a, b = baseline == c, mapped == c
        out["classes"][str(c)] = {
            "name": CLASS_NAMES[c],
            "overlap": overlap(a, b),
            "baseline_components": component_stats(a),
            "variant_components": component_stats(b),
        }
    fa, fb = baseline > 0, mapped > 0
    out["foreground_union"] = {
        "overlap": overlap(fa, fb),
        "baseline_components": component_stats(fa),
        "variant_components": component_stats(fb),
    }
    return out


def num_summary(vals: list[float]) -> dict[str, Any] | None:
    if not vals:
        return None
    x = np.asarray(vals, dtype=float)
    return {
        "n": int(x.size),
        "mean": float(x.mean()),
        "median": float(np.median(x)),
        "p10": float(np.percentile(x, 10)),
        "p90": float(np.percentile(x, 90)),
        "min": float(x.min()),
        "max": float(x.max()),
    }


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    variants = ["rotate_p5", "rotate_m5", "scale_090", "scale_110", "center_crop_3pct"]
    by_variant = {}
    for v in variants:
        rr = [r["variants"][v] for r in records]
        classes = {}
        for c in (1, 2, 3):
            dices = [x["comparison"]["classes"][str(c)]["overlap"]["dice"] for x in rr]
            ious = [x["comparison"]["classes"][str(c)]["overlap"]["iou"] for x in rr]
            classes[str(c)] = {
                "name": CLASS_NAMES[c],
                "dice": num_summary([x for x in dices if x is not None]),
                "iou": num_summary([x for x in ious if x is not None]),
                "not_applicable_empty_both": sum(x is None for x in dices),
                "appearance_transitions": sum(
                    x["comparison"]["classes"][str(c)]["overlap"]["status"] == "appearance_transition"
                    for x in rr
                ),
            }
        fg_dice = [x["comparison"]["foreground_union"]["overlap"]["dice"] for x in rr]
        fg_iou = [x["comparison"]["foreground_union"]["overlap"]["iou"] for x in rr]
        by_variant[v] = {
            "classes": classes,
            "foreground_union": {
                "dice": num_summary([x for x in fg_dice if x is not None]),
                "iou": num_summary([x for x in fg_iou if x is not None]),
            },
        }

    by_class = {}
    for c in (1, 2, 3):
        dices = []
        ious = []
        for r in records:
            for v in variants:
                o = r["variants"][v]["comparison"]["classes"][str(c)]["overlap"]
                if o["dice"] is not None:
                    dices.append(o["dice"])
                    ious.append(o["iou"])
        by_class[str(c)] = {"name": CLASS_NAMES[c], "dice": num_summary(dices), "iou": num_summary(ious)}

    by_person = {}
    for r in records:
        dices = []
        fg = []
        for v in variants:
            for c in (1, 2, 3):
                d = r["variants"][v]["comparison"]["classes"][str(c)]["overlap"]["dice"]
                if d is not None:
                    dices.append(d)
            fd = r["variants"][v]["comparison"]["foreground_union"]["overlap"]["dice"]
            if fd is not None:
                fg.append(fd)
        by_person[str(r["p"])] = {
            "file": r["file"],
            "class_specific_dice": num_summary(dices),
            "foreground_union_dice": num_summary(fg),
        }

    return {"n_images": len(records), "by_variant": by_variant, "by_class": by_class, "by_person": by_person}


def dry_run(sess: ort.InferenceSession) -> None:
    side = 384
    rgb = np.zeros((side, side, 3), dtype=np.uint8)
    cv2.ellipse(rgb, (side // 2, side // 2 + 25), (105, 135), 0, 0, 360, (175, 145, 125), -1)
    for yoff in (-50, 0, 50):
        cv2.arc(rgb, (side // 2, side // 2 + yoff), (85, 45), 0, 190, 345, (95, 75, 70), 2)
    baseline, logs = infer_mask(sess, rgb)
    variants = {}
    for name in ("rotate_p5", "rotate_m5", "scale_090", "scale_110", "center_crop_3pct"):
        M = variant_matrix(name, side)
        vrgb = apply_variant(rgb, M)
        vmask, _ = infer_mask(sess, vrgb)
        mapped = inverse_map_mask(vmask, M)
        variants[name] = {
            "matrix_shape": list(M.shape),
            "mapped_shape": list(mapped.shape),
            "mapped_values_subset": sorted(int(x) for x in np.unique(mapped)),
        }
    print(json.dumps({
        "mode": "NON-MOHI DRY RUN",
        "baseline_shape": list(baseline.shape),
        "baseline_values_subset": sorted(int(x) for x in np.unique(baseline)),
        "finite_logit_summary": all(np.isfinite(list(logs.values()))),
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

    runtime = validate_runtime()
    sess, model_identity = validate_model(args.model, args.meta)

    if args.dry_run:
        dry_run(sess)
        return

    if args.zip is None or args.mediapipe_results is None or args.output is None:
        ap.error("full mode requires --zip --mediapipe-results --output")

    rows, sha_groups = validate_source(args.zip)
    mp_data = validate_mediapipe_results(args.mediapipe_results, rows)
    mp_by_file = {r["file"]: r for r in mp_data["images"]}
    selected = select_sources(rows, sha_groups)

    output = {
        "status": "REFERENCE-ONLY / PREDECLARED PALM-LINE SEGMENTATION REPEATABILITY RAW EVIDENCE",
        "runtime": runtime,
        "model": str(args.model),
        "metadata": str(args.meta),
        **model_identity,
        "source_zip": str(args.zip),
        "source_zip_sha256": EXPECTED_ZIP_SHA,
        "mediapipe_results": str(args.mediapipe_results),
        "mediapipe_model_sha256": EXPECTED_MP_MODEL_SHA,
        "decode_contract": "cv2.IMREAD_COLOR | cv2.IMREAD_IGNORE_ORIENTATION",
        "sample_contract": "one deterministic unique source per person; prefer Pxxx/S1/01.jpg",
        "crop_contract": "21-landmark bbox + 15% max-dimension margin; black pad; rotate L0->L9 upward; square pad",
        "variants_contract": ["rotate_p5", "rotate_m5", "scale_090", "scale_110", "center_crop_3pct"],
        "images": [],
    }

    decode_flag = cv2.IMREAD_COLOR | cv2.IMREAD_IGNORE_ORIENTATION
    with zipfile.ZipFile(args.zip) as zf:
        for idx, src in enumerate(selected, 1):
            rec = {**src}
            data = zf.read(src["file"])
            bgr = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), decode_flag)
            if bgr is None:
                raise RuntimeError(f"decode failed for selected source {src['file']}")
            h, w = bgr.shape[:2]
            mp_rec = mp_by_file[src["file"]]
            if mp_rec.get("raw") != [h, w]:
                raise RuntimeError(f"raw frame mismatch for {src['file']}: decoded={[h,w]} mp={mp_rec.get('raw')}")
            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            crop, crop_meta = crop_palm(rgb, mp_points(mp_rec))
            baseline_mask, baseline_logits = infer_mask(sess, crop)
            side = crop.shape[0]
            baseline_stats = {
                str(c): {"name": CLASS_NAMES[c], **component_stats(baseline_mask == c)}
                for c in (1, 2, 3)
            }
            baseline_stats["foreground_union"] = component_stats(baseline_mask > 0)

            variants = {}
            for name in ("rotate_p5", "rotate_m5", "scale_090", "scale_110", "center_crop_3pct"):
                M = variant_matrix(name, side)
                vrgb = apply_variant(crop, M)
                vmask, vlogits = infer_mask(sess, vrgb)
                mapped = inverse_map_mask(vmask, M)
                variants[name] = {
                    "forward_matrix": M.tolist(),
                    "inverse_matrix": cv2.invertAffineTransform(M).tolist(),
                    "logits": vlogits,
                    "comparison": compare_masks(baseline_mask, mapped),
                }

            rec.update({
                "raw_size_hw": [h, w],
                "raw_frame_match": True,
                "crop": crop_meta,
                "baseline": {"logits": baseline_logits, "stats": baseline_stats},
                "variants": variants,
            })
            output["images"].append(rec)
            print(f"[{idx:02d}/10] {src['file']}: complete")

    if len(output["images"]) != 10:
        raise RuntimeError(f"expected 10 completed images, got {len(output['images'])}")
    output["execution"] = {"selected": 10, "completed": 10, "stop": False}
    output["summary"] = summarize(output["images"])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nDONE")
    print(json.dumps(output["execution"], indent=2))
    print(args.output)


if __name__ == "__main__":
    main()
