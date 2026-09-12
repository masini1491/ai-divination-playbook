#!/usr/bin/env python3
"""Cold research runner for MOHI MediaPipe-vs-RTMPose detector agreement.

REFERENCE-ONLY. This script does not define production thresholds or biometric
identity claims. It reuses frozen MediaPipe evidence and runs the independently
pinned RTMPose-Hand5 detector under DETECTOR_AGREEMENT_PLAN.md.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import platform
import statistics
import sys
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import torch
import torchvision
import mmcv
import mmengine
import mmdet
import mmpose
from importlib import metadata
from mmpose.apis import inference_topdown, init_model

EXPECTED_ZIP_SHA = "6309f2390b0013858928c6c77344b4aa869edc8c0aeb9a61db93b73ae83feec2"
EXPECTED_MP_MODEL_SHA = "fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1"
EXPECTED_CHECKPOINT_SHA = "b74fb5941684fe13c337b8d4fce644293e12903fed5407f8b27921f107dc6003"
EXPECTED_CHECKPOINT_NAME = "rtmpose-m_simcc-hand5_pt-aic-coco_210e-256x256-74fb594_20230320.pth"
EXPECTED = {
    "python": "3.9.18",
    "numpy": "1.26.4",
    "opencv-python": "4.10.0.84",
    "torch": "1.13.1",
    "torchvision": "0.14.1",
    "mmcv": "2.0.0",
    "mmengine": "0.10.4",
    "mmdet": "3.2.0",
    "mmpose": "1.3.2",
    "chumpy": "0.70",
    "setuptools": "80.9.0",
}
EPS = 1e-9
ANCHORS = (0, 5, 17)


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
        "torch": torch.__version__,
        "torchvision": torchvision.__version__,
        "mmcv": mmcv.__version__,
        "mmengine": mmengine.__version__,
        "mmdet": mmdet.__version__,
        "mmpose": mmpose.__version__,
        "chumpy": package_version("chumpy"),
        "setuptools": package_version("setuptools"),
        "cuda_available": bool(torch.cuda.is_available()),
    }
    mismatches = {}
    for key, want in EXPECTED.items():
        got = observed[key]
        if got != want:
            mismatches[key] = {"expected": want, "actual": got}
    if observed["cuda_available"]:
        mismatches["cuda_available"] = {"expected": False, "actual": True}
    if mismatches:
        raise RuntimeError(f"runtime lock mismatch: {json.dumps(mismatches, indent=2)}")
    return observed


def resolve_config() -> Path:
    pkg = Path(mmpose.__file__).resolve().parent
    candidates = [
        pkg / ".mim" / "configs" / "hand_2d_keypoint" / "rtmpose" / "hand5" /
        "rtmpose-m_8xb256-210e_hand5-256x256.py",
        pkg.parent / "configs" / "hand_2d_keypoint" / "rtmpose" / "hand5" /
        "rtmpose-m_8xb256-210e_hand5-256x256.py",
    ]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError("frozen RTMPose Hand5 config not found")


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
        if len(rows) != 150 or len({r['p'] for r in rows}) != 10:
            raise RuntimeError(f"unexpected manifest structure: rows={len(rows)} persons={len({r['p'] for r in rows})}")
        names = set(zf.namelist())
        sha_groups: dict[str, list[str]] = defaultdict(list)
        for r in rows:
            if r["file"] not in names:
                raise RuntimeError(f"missing ZIP entry: {r['file']}")
            got = sha256_bytes(zf.read(r["file"]))
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
        raise RuntimeError(f"MediaPipe evidence must contain 150 image entries, got {len(images)}")
    by_file = {r.get("file"): r for r in images}
    for source in rows:
        rec = by_file.get(source["file"])
        if not rec or not rec.get("usable"):
            raise RuntimeError(f"MediaPipe frozen evidence not usable for {source['file']}")
        lm = rec.get("hand", {}).get("lm")
        if not isinstance(lm, list) or len(lm) != 21:
            raise RuntimeError(f"MediaPipe landmark contract failed for {source['file']}")
    return data


def palm_basis(points: np.ndarray) -> dict[str, Any]:
    if points.shape != (21, 2) or not np.isfinite(points).all():
        raise ValueError("21 finite 2D keypoints required")
    p0, p5, p17 = points[0], points[5], points[17]
    midpoint = (p5 + p17) / 2.0
    eyv = midpoint - p0
    height = float(np.linalg.norm(eyv))
    if height <= EPS:
        raise ValueError("degenerate palm height axis")
    ey = eyv / height
    raw_ex = p5 - p17
    orth = raw_ex - float(np.dot(raw_ex, ey)) * ey
    orth_n = float(np.linalg.norm(orth))
    if orth_n <= EPS:
        raise ValueError("degenerate palm width axis")
    ex = orth / orth_n
    if float(np.dot(p5 - midpoint, ex)) <= 0:
        ex = -ex
    width = float(np.dot(p5 - p17, ex))
    if width <= EPS:
        raise ValueError("degenerate palm width")
    rel = points - p0
    canonical = np.column_stack((rel @ ex / width, rel @ ey / height))
    angle = math.degrees(math.atan2(float(ey[1]), float(ey[0])))
    return {"width": width, "height": height, "angle_deg": angle, "canonical": canonical}


def angle_delta(a: float, b: float) -> float:
    return abs((b - a + 180.0) % 360.0 - 180.0)


def rel_diff(a: float, b: float) -> float:
    return abs(a - b) / ((a + b) / 2.0)


def summary(vals: list[float]) -> dict[str, Any] | None:
    if not vals:
        return None
    x = np.asarray(vals, dtype=float)
    return {
        "n": int(x.size),
        "mean": float(x.mean()),
        "median": float(np.median(x)),
        "p90": float(np.percentile(x, 90)),
        "p95": float(np.percentile(x, 95)),
        "min": float(x.min()),
        "max": float(x.max()),
        "std": float(x.std()),
    }


def pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 2 or len(xs) != len(ys):
        return None
    x, y = np.asarray(xs, float), np.asarray(ys, float)
    if float(x.std()) <= EPS or float(y.std()) <= EPS:
        return None
    return float(np.corrcoef(x, y)[0, 1])


def mp_points(rec: dict[str, Any]) -> np.ndarray:
    return np.asarray([[float(v[0]), float(v[1])] for v in rec["hand"]["lm"]], dtype=float)


def rtm_output(model: Any, img: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    results = inference_topdown(model, img, bboxes=None)
    if len(results) != 1:
        raise RuntimeError(f"RTMPose expected one full-image result, got {len(results)}")
    pred = results[0].pred_instances
    keypoints = np.asarray(pred.keypoints, dtype=float)
    scores = np.asarray(pred.keypoint_scores, dtype=float)
    if keypoints.shape == (1, 21, 2):
        keypoints = keypoints[0]
    if scores.shape == (1, 21):
        scores = scores[0]
    if keypoints.shape != (21, 2) or scores.shape != (21,):
        raise RuntimeError(f"unexpected RTMPose shapes: keypoints={keypoints.shape} scores={scores.shape}")
    if not np.isfinite(keypoints).all() or not np.isfinite(scores).all():
        raise RuntimeError("non-finite RTMPose output")
    return keypoints, scores


def agreement(mp_xy: np.ndarray, rt_xy: np.ndarray, scores: np.ndarray, width: int, height: int) -> dict[str, Any]:
    scale = np.asarray([width, height], dtype=float)
    raw_delta = np.linalg.norm(mp_xy / scale - rt_xy / scale, axis=1)
    mpb, rtb = palm_basis(mp_xy), palm_basis(rt_xy)
    can_delta = np.linalg.norm(mpb["canonical"] - rtb["canonical"], axis=1)
    anchor_raw = raw_delta[list(ANCHORS)]
    return {
        "raw_21_delta": raw_delta.tolist(),
        "raw_mean": float(raw_delta.mean()),
        "raw_median": float(np.median(raw_delta)),
        "raw_max": float(raw_delta.max()),
        "anchor_raw_delta": anchor_raw.tolist(),
        "anchor_mean": float(anchor_raw.mean()),
        "anchor_max": float(anchor_raw.max()),
        "axis_angle_delta_deg": angle_delta(mpb["angle_deg"], rtb["angle_deg"]),
        "width_rel_diff": rel_diff(mpb["width"], rtb["width"]),
        "height_rel_diff": rel_diff(mpb["height"], rtb["height"]),
        "canonical_21_delta": can_delta.tolist(),
        "canonical_mean": float(can_delta.mean()),
        "canonical_max": float(can_delta.max()),
        "rtmpose_score_mean": float(scores.mean()),
        "rtmpose_score_median": float(np.median(scores)),
        "rtmpose_score_min": float(scores.min()),
        "rtmpose_anchor_scores": [float(scores[i]) for i in ANCHORS],
    }


def summarize_primary(records: list[dict[str, Any]]) -> dict[str, Any]:
    metrics = ("raw_mean", "raw_median", "raw_max", "anchor_mean", "anchor_max", "axis_angle_delta_deg",
               "width_rel_diff", "height_rel_diff", "canonical_mean", "canonical_max",
               "rtmpose_score_mean", "rtmpose_score_median", "rtmpose_score_min")
    pooled = {k: summary([r["agreement"][k] for r in records]) for k in metrics}
    per_keypoint = {
        str(i): {
            "raw_delta": summary([r["agreement"]["raw_21_delta"][i] for r in records]),
            "canonical_delta": summary([r["agreement"]["canonical_21_delta"][i] for r in records]),
            "rtmpose_score": summary([r["rtmpose"]["scores"][i] for r in records]),
        }
        for i in range(21)
    }
    by_person = {}
    for p in sorted({r["p"] for r in records}):
        rr = [r for r in records if r["p"] == p]
        by_person[str(p)] = {k: summary([x["agreement"][k] for x in rr]) for k in metrics}
    by_session = {}
    for s in sorted({r["s"] for r in records}):
        rr = [r for r in records if r["s"] == s]
        by_session[str(s)] = {k: summary([x["agreement"][k] for x in rr]) for k in metrics}
    score_mean = [r["agreement"]["rtmpose_score_mean"] for r in records]
    return {
        "n": len(records),
        "pooled": pooled,
        "per_keypoint": per_keypoint,
        "per_person": by_person,
        "per_session": by_session,
        "score_relationship": {
            "pearson_score_mean_vs_raw_mean": pearson(score_mean, [r["agreement"]["raw_mean"] for r in records]),
            "pearson_score_mean_vs_canonical_mean": pearson(score_mean, [r["agreement"]["canonical_mean"] for r in records]),
        },
    }


def dry_run(model: Any) -> None:
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.rectangle(img, (240, 180), (400, 420), (180, 180, 180), -1)
    keypoints, scores = rtm_output(model, img)
    print(json.dumps({
        "mode": "NON-MOHI DRY RUN",
        "keypoints_shape": list(keypoints.shape),
        "scores_shape": list(scores.shape),
        "finite_keypoints": bool(np.isfinite(keypoints).all()),
        "finite_scores": bool(np.isfinite(scores).all()),
        "score_mean": float(scores.mean()),
        "schema": "PASS",
    }, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", type=Path)
    ap.add_argument("--mediapipe-results", type=Path)
    ap.add_argument("--checkpoint", type=Path, required=True)
    ap.add_argument("--output", type=Path)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    runtime = validate_runtime()
    if args.checkpoint.name not in {EXPECTED_CHECKPOINT_NAME, "rtmpose-m-hand5.pth"}:
        raise RuntimeError(f"unexpected checkpoint filename: {args.checkpoint.name}")
    checkpoint_sha = sha256_file(args.checkpoint)
    if checkpoint_sha != EXPECTED_CHECKPOINT_SHA:
        raise RuntimeError(f"checkpoint SHA mismatch: {checkpoint_sha}")
    config = resolve_config()
    model = init_model(str(config), str(args.checkpoint), device="cpu")
    model.eval()

    if args.dry_run:
        dry_run(model)
        return

    if not args.zip or not args.mediapipe_results or not args.output:
        ap.error("full execution requires --zip, --mediapipe-results, and --output")

    rows, sha_groups = validate_source(args.zip)
    mp_data = validate_mediapipe_results(args.mediapipe_results, rows)
    mp_by_file = {r["file"]: r for r in mp_data["images"]}
    representative = {}
    for digest, paths in sha_groups.items():
        representative[digest] = sorted(paths)[0]

    output = {
        "status": "REFERENCE-ONLY / PREDECLARED DETECTOR AGREEMENT RAW EVIDENCE",
        "runtime": runtime,
        "config": str(config),
        "config_sha256": sha256_file(config),
        "checkpoint": str(args.checkpoint),
        "checkpoint_sha256": checkpoint_sha,
        "source_zip": str(args.zip),
        "source_zip_sha256": EXPECTED_ZIP_SHA,
        "mediapipe_results": str(args.mediapipe_results),
        "mediapipe_model_sha256": EXPECTED_MP_MODEL_SHA,
        "canonical_basis_owner": "NORMALIZATION_CONTRACT_DRAFT.md / normalization_probe.py",
        "images": [],
    }

    with zipfile.ZipFile(args.zip) as zf:
        for n, source in enumerate(rows, 1):
            data = zf.read(source["file"])
            img = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)
            rec = {**source, "decode": img is not None}
            if img is None:
                rec.update({"rtmpose_usable": False, "failure": "decode_failed"})
                output["images"].append(rec)
                print(f"[{n:03d}/150] {source['file']}: decode failed")
                continue
            h, w = img.shape[:2]
            mp_rec = mp_by_file[source["file"]]
            mp_xy = mp_points(mp_rec)
            try:
                rt_xy, scores = rtm_output(model, img)
                metrics = agreement(mp_xy, rt_xy, scores, w, h)
                palm_basis(rt_xy)
            except Exception as exc:
                rec.update({"raw_size": [h, w], "rtmpose_usable": False, "failure": f"{type(exc).__name__}: {exc}"})
            else:
                digest = source["sha256"]
                rec.update({
                    "raw_size": [h, w],
                    "rtmpose_usable": True,
                    "unique_representative": representative[digest] == source["file"],
                    "mediapipe": {"xy": mp_xy.tolist()},
                    "rtmpose": {"xy": rt_xy.tolist(), "scores": scores.tolist()},
                    "agreement": metrics,
                })
            output["images"].append(rec)
            print(f"[{n:03d}/150] {source['file']}: {'usable' if rec.get('rtmpose_usable') else 'FAILED'}")

    usable = [r for r in output["images"] if r.get("rtmpose_usable")]
    primary = [r for r in usable if r.get("unique_representative")]
    if len(usable) != 150:
        output["execution"] = {"total": 150, "usable": len(usable), "primary_unique": len(primary), "stop": True}
        args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
        raise RuntimeError(f"RTMPose geometry usable on {len(usable)}/150; stop before interpretation")
    if len(primary) != 148:
        raise RuntimeError(f"expected 148 unique source-byte representatives, got {len(primary)}")

    duplicate_checks = []
    by_file = {r["file"]: r for r in usable}
    for digest, paths in sorted(sha_groups.items()):
        if len(paths) <= 1:
            continue
        base = by_file[sorted(paths)[0]]
        for other_path in sorted(paths)[1:]:
            other = by_file[other_path]
            a = np.asarray(base["rtmpose"]["xy"], float)
            b = np.asarray(other["rtmpose"]["xy"], float)
            sa = np.asarray(base["rtmpose"]["scores"], float)
            sb = np.asarray(other["rtmpose"]["scores"], float)
            duplicate_checks.append({
                "sha256": digest,
                "a": base["file"],
                "b": other["file"],
                "keypoints_exact_equal": bool(np.array_equal(a, b)),
                "scores_exact_equal": bool(np.array_equal(sa, sb)),
                "keypoints_max_abs_delta": float(np.max(np.abs(a - b))),
                "scores_max_abs_delta": float(np.max(np.abs(sa - sb))),
            })

    output["execution"] = {"total": 150, "usable": 150, "primary_unique": 148, "stop": False}
    output["duplicate_consistency"] = duplicate_checks
    output["primary_148"] = summarize_primary(primary)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nDONE")
    print(json.dumps(output["execution"], indent=2))
    print(args.output)


if __name__ == "__main__":
    main()
