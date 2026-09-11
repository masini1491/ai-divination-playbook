#!/usr/bin/env python3
"""Cold research runner for MediaPipe palm landmark transform consistency.

Runs Case A (single palm) and Case B (multi-hand scene) with a pinned MediaPipe
Hand Landmarker model. Candidate association is scene-local only: a baseline target
is chosen by largest normalized hand bbox; transformed candidates are inverse-mapped
to baseline coordinates and matched by minimum mean L0/L5/L17 distance.

This is research instrumentation, NOT biometric identity and NOT a production owner.
"""
from __future__ import annotations

import argparse, hashlib, json, platform, sys, urllib.request
from pathlib import Path
from typing import Iterable
import cv2
import mediapipe as mp
import numpy as np
from real_image_repeatability_probe import (
    Point, apply_homography, build_basis, evaluate_study, norm, parse_matrix, print_results
)

MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
USER_AGENT = "ai-divination-playbook-palmistry-research/1.0"
MAX_BASELINE_DIM = 1600
ANCHORS = (0, 5, 17)
CASES = {
    "case_a": {
        "label": "Case A — single right palm",
        "source_page": "https://commons.wikimedia.org/wiki/File:Right_Hand_Palm.png",
        "image_url": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Right_Hand_Palm.png",
        "license": "CC BY-SA 4.0",
    },
    "case_b": {
        "label": "Case B — two palms, left emphasized",
        "source_page": "https://commons.wikimedia.org/wiki/File:Open_Palm_of_the_Left_Hand,_Fingers.jpg",
        "image_url": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Open_Palm_of_the_Left_Hand,_Fingers.jpg",
        "license": "CC BY-SA 4.0",
    },
}


def download(url, dst):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    h = hashlib.sha256()
    with urllib.request.urlopen(req, timeout=60) as r, dst.open("wb") as f:
        while True:
            b = r.read(1024 * 1024)
            if not b:
                break
            f.write(b)
            h.update(b)
    return h.hexdigest()


def ensure_max_dim(img, max_dim=MAX_BASELINE_DIM):
    h, w = img.shape[:2]
    largest = max(h, w)
    if largest <= max_dim:
        return img, 1.0
    s = max_dim / float(largest)
    return cv2.resize(img, (max(1, round(w * s)), max(1, round(h * s))), interpolation=cv2.INTER_AREA), s


def bbox_area(lms: Iterable[object]):
    pts = list(lms)
    xs = [float(p.x) for p in pts]
    ys = [float(p.y) for p in pts]
    return max(0, max(xs) - min(xs)) * max(0, max(ys) - min(ys))


def category_name(cat):
    for attr in ("category_name", "display_name"):
        v = getattr(cat, attr, None)
        if isinstance(v, str) and v:
            return v
    return None


def detect_all(landmarker, img):
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = landmarker.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(rgb)))
    h, w = img.shape[:2]
    out = []
    for i, lms in enumerate(result.hand_landmarks):
        handed = None
        if i < len(result.handedness) and result.handedness[i]:
            handed = category_name(result.handedness[i][0])
        out.append({
            "index": i,
            "handedness": handed,
            "bbox_area_normalized": bbox_area(lms),
            "landmarks": {str(a): [float(lms[a].x) * w, float(lms[a].y) * h] for a in ANCHORS},
        })
    return out


def affine3(m):
    return [[float(m[0, 0]), float(m[0, 1]), float(m[0, 2])], [float(m[1, 0]), float(m[1, 1]), float(m[1, 2])], [0.0, 0.0, 1.0]]


def identity(img):
    return img.copy(), [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]


def rotate(img, deg):
    h, w = img.shape[:2]
    center = ((w - 1) / 2.0, (h - 1) / 2.0)
    forward = cv2.getRotationMatrix2D(center, deg, 1.0)
    transformed = cv2.warpAffine(img, forward, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255))
    return transformed, affine3(cv2.invertAffineTransform(forward))


def scale(img, factor):
    h, w = img.shape[:2]
    nw, nh = max(1, round(w * factor)), max(1, round(h * factor))
    interpolation = cv2.INTER_AREA if factor < 1 else cv2.INTER_CUBIC
    return cv2.resize(img, (nw, nh), interpolation=interpolation), [[w / nw, 0.0, 0.0], [0.0, h / nh, 0.0], [0.0, 0.0, 1.0]]


def crop(img, fraction=0.03):
    h, w = img.shape[:2]
    x0, y0 = round(w * fraction), round(h * fraction)
    return img[y0:h-y0, x0:w-x0].copy(), [[1.0, 0.0, float(x0)], [0.0, 1.0, float(y0)], [0.0, 0.0, 1.0]]


def mirror(img):
    _, w = img.shape[:2]
    return cv2.flip(img, 1), [[-1.0, 0.0, float(w - 1)], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]


VARIANTS = [
    ("same-pixels-rerun", identity),
    ("rotate+10deg", lambda img: rotate(img, 10.0)),
    ("rotate-10deg", lambda img: rotate(img, -10.0)),
    ("scale-0.75x", lambda img: scale(img, 0.75)),
    ("scale-1.25x", lambda img: scale(img, 1.25)),
    ("crop-3pct", lambda img: crop(img, 0.03)),
    ("horizontal-mirror", mirror),
]


def anchors_points(candidate):
    return {int(k): Point(float(v[0]), float(v[1])) for k, v in candidate["landmarks"].items()}


def mean_anchor_distance_after_inverse(candidate, inverse_transform, baseline_target, baseline_width):
    matrix = parse_matrix(inverse_transform)
    candidate_points = anchors_points(candidate)
    baseline_points = anchors_points(baseline_target)
    distances = [norm(apply_homography(candidate_points[a], matrix) - baseline_points[a]) / baseline_width for a in ANCHORS]
    return sum(distances) / len(distances), max(distances)


def select_transformed_candidate(candidates, inverse_transform, baseline_target, baseline_width):
    if not candidates:
        raise RuntimeError("MediaPipe detected no hands")
    scored = []
    for candidate in candidates:
        mean_d, max_d = mean_anchor_distance_after_inverse(candidate, inverse_transform, baseline_target, baseline_width)
        scored.append((mean_d, max_d, candidate))
    scored.sort(key=lambda item: item[0])
    best = scored[0]
    second = scored[1][0] if len(scored) > 1 else None
    return best[2], {
        "best_mean_anchor_distance_fraction": best[0],
        "best_max_anchor_distance_fraction": best[1],
        "second_best_mean_anchor_distance_fraction": second,
        "separation_fraction": None if second is None else second - best[0],
        "candidate_scores": [
            {
                "index": item[2]["index"],
                "handedness": item[2]["handedness"],
                "mean_anchor_distance_fraction": item[0],
                "max_anchor_distance_fraction": item[1],
            }
            for item in scored
        ],
        "selection_rule": "minimum mean L0/L5/L17 distance after inverse transform; scene-local association only",
    }


def metric_json(metric):
    return {key: getattr(metric, key) for key in (
        "name", "max_anchor_drift_fraction", "mean_anchor_drift_fraction", "axis_angle_deg",
        "width_rel_error", "height_rel_error", "max_canonical_grid_drift", "handedness_changed"
    )}


def run_case(case_id, config, landmarker, model_sha, root):
    case_dir = root / case_id
    case_dir.mkdir(parents=True, exist_ok=True)
    image_path = case_dir / ("source.png" if case_id == "case_a" else "source.jpg")
    source_sha = download(config["image_url"], image_path)
    original = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if original is None:
        raise RuntimeError(f"failed to decode {case_id}")
    baseline_image, baseline_scale = ensure_max_dim(original)
    baseline_candidates = detect_all(landmarker, baseline_image)
    if not baseline_candidates:
        raise RuntimeError(f"no hands in {case_id} baseline")
    baseline_target = max(baseline_candidates, key=lambda c: c["bbox_area_normalized"])
    baseline_width = build_basis(anchors_points(baseline_target)).width

    variants = []
    metadata = {}
    for name, factory in VARIANTS:
        transformed, inverse_transform = factory(baseline_image)
        candidates = detect_all(landmarker, transformed)
        selected, match = select_transformed_candidate(candidates, inverse_transform, baseline_target, baseline_width)
        variants.append({
            "name": name,
            "landmarks": selected["landmarks"],
            "inverse_transform": inverse_transform,
            "handedness": selected["handedness"],
        })
        metadata[name] = {
            "shape": list(transformed.shape[:2]),
            "candidate_count": len(candidates),
            "selected_index": selected["index"],
            "selected_handedness": selected["handedness"],
            "selected_bbox_area_normalized": selected["bbox_area_normalized"],
            "match": match,
        }

    study = {"baseline": {"landmarks": baseline_target["landmarks"], "handedness": baseline_target["handedness"]}, "variants": variants}
    metrics = evaluate_study(study)
    provenance = {
        "status": "research-only",
        "case_id": case_id,
        "case": config["label"],
        "source_page": config["source_page"],
        "source_license": config["license"],
        "source_sha256": source_sha,
        "source_original_shape": list(original.shape[:2]),
        "working_baseline_shape": list(baseline_image.shape[:2]),
        "working_baseline_scale_from_source": baseline_scale,
        "model_url": MODEL_URL,
        "model_sha256": model_sha,
        "mediapipe_version": getattr(mp, "__version__", "unknown"),
        "opencv_version": cv2.__version__,
        "python_version": platform.python_version(),
        "baseline_candidate_count": len(baseline_candidates),
        "baseline_target_rule": "largest normalized landmark bounding box; scene-local target only",
        "baseline_selected_index": baseline_target["index"],
        "baseline_selected_handedness": baseline_target["handedness"],
        "baseline_selected_bbox_area_normalized": baseline_target["bbox_area_normalized"],
        "baseline_all_candidates": [
            {"index": c["index"], "handedness": c["handedness"], "bbox_area_normalized": c["bbox_area_normalized"]}
            for c in baseline_candidates
        ],
        "variant_metadata": metadata,
    }

    (case_dir / "study.json").write_text(json.dumps(study, indent=2), encoding="utf-8")
    (case_dir / "provenance.json").write_text(json.dumps(provenance, indent=2), encoding="utf-8")
    (case_dir / "metrics.json").write_text(json.dumps([metric_json(m) for m in metrics], indent=2), encoding="utf-8")
    print(f"=== {case_id.upper()} PROVENANCE ===")
    print(json.dumps(provenance, indent=2))
    print(f"=== {case_id.upper()} METRICS ===")
    print_results(metrics)
    print(f"=== {case_id.upper()} METRICS_JSON ===")
    print(json.dumps([metric_json(m) for m in metrics], indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="palmistry-repeatability-output")
    args = parser.parse_args()
    root = Path(args.output_dir)
    root.mkdir(parents=True, exist_ok=True)
    model_path = root / "hand_landmarker.task"
    model_sha = download(MODEL_URL, model_path)
    options = mp.tasks.vision.HandLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=str(model_path)),
        running_mode=mp.tasks.vision.RunningMode.IMAGE,
        num_hands=2,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    with mp.tasks.vision.HandLandmarker.create_from_options(options) as landmarker:
        for case_id, config in CASES.items():
            run_case(case_id, config, landmarker, model_sha, root)
    return 0


if __name__ == "__main__":
    sys.exit(main())
