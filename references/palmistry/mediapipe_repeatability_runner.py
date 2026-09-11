#!/usr/bin/env python3
"""Cold research runner for MediaPipe real-image palm landmark repeatability.

Downloads the official Hand Landmarker model and one public/free-licensed palm
image, runs controlled image transforms, exports detector coordinates plus exact
inverse transforms, and feeds them into real_image_repeatability_probe.py.

This is research instrumentation, not a production Palmistry runtime owner.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import urllib.request
from pathlib import Path
from typing import Iterable

import cv2
import mediapipe as mp
import numpy as np

from real_image_repeatability_probe import evaluate_study, print_results

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/1/hand_landmarker.task"
)
CASE_A_SOURCE_PAGE = "https://commons.wikimedia.org/wiki/File:Right_Hand_Palm.png"
CASE_A_IMAGE_URL = "https://commons.wikimedia.org/wiki/Special:Redirect/file/Right_Hand_Palm.png"
CASE_A_LICENSE = "CC BY-SA 4.0"
USER_AGENT = "ai-divination-playbook-palmistry-research/1.0"
MAX_BASELINE_DIM = 1600
ANCHORS = (0, 5, 17)


def download(url: str, destination: Path) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    h = hashlib.sha256()
    with urllib.request.urlopen(request, timeout=60) as response, destination.open("wb") as out:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)
            h.update(chunk)
    return h.hexdigest()


def ensure_max_dim(image: np.ndarray, max_dim: int = MAX_BASELINE_DIM) -> tuple[np.ndarray, float]:
    height, width = image.shape[:2]
    largest = max(height, width)
    if largest <= max_dim:
        return image, 1.0
    scale = max_dim / float(largest)
    resized = cv2.resize(
        image,
        (max(1, round(width * scale)), max(1, round(height * scale))),
        interpolation=cv2.INTER_AREA,
    )
    return resized, scale


def affine3(matrix2x3: np.ndarray) -> list[list[float]]:
    return [
        [float(matrix2x3[0, 0]), float(matrix2x3[0, 1]), float(matrix2x3[0, 2])],
        [float(matrix2x3[1, 0]), float(matrix2x3[1, 1]), float(matrix2x3[1, 2])],
        [0.0, 0.0, 1.0],
    ]


def bbox_area(landmarks: Iterable[object]) -> float:
    points = list(landmarks)
    xs = [float(p.x) for p in points]
    ys = [float(p.y) for p in points]
    return max(0.0, max(xs) - min(xs)) * max(0.0, max(ys) - min(ys))


def category_name(category: object) -> str | None:
    name = getattr(category, "category_name", None)
    if isinstance(name, str) and name:
        return name
    display = getattr(category, "display_name", None)
    if isinstance(display, str) and display:
        return display
    return None


def detect_one(landmarker: object, image_bgr: np.ndarray) -> dict[str, object]:
    rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(rgb))
    result = landmarker.detect(mp_image)
    hand_landmarks = list(result.hand_landmarks)
    if not hand_landmarks:
        raise RuntimeError("MediaPipe detected no hands")

    index = max(range(len(hand_landmarks)), key=lambda i: bbox_area(hand_landmarks[i]))
    selected = hand_landmarks[index]
    height, width = image_bgr.shape[:2]
    anchors = {
        str(anchor): [float(selected[anchor].x) * width, float(selected[anchor].y) * height]
        for anchor in ANCHORS
    }

    handedness = None
    if index < len(result.handedness) and result.handedness[index]:
        handedness = category_name(result.handedness[index][0])

    return {
        "landmarks": anchors,
        "handedness": handedness,
        "candidate_count": len(hand_landmarks),
        "selected_index": index,
        "selected_bbox_area_normalized": bbox_area(selected),
    }


def variant_identity(image: np.ndarray) -> tuple[np.ndarray, list[list[float]]]:
    return image.copy(), [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]


def variant_rotate(image: np.ndarray, angle_deg: float) -> tuple[np.ndarray, list[list[float]]]:
    h, w = image.shape[:2]
    center = ((w - 1) / 2.0, (h - 1) / 2.0)
    forward = cv2.getRotationMatrix2D(center, angle_deg, 1.0)
    transformed = cv2.warpAffine(
        image,
        forward,
        (w, h),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(255, 255, 255),
    )
    inverse = cv2.invertAffineTransform(forward)
    return transformed, affine3(inverse)


def variant_scale(image: np.ndarray, requested_scale: float) -> tuple[np.ndarray, list[list[float]]]:
    h, w = image.shape[:2]
    new_w = max(1, round(w * requested_scale))
    new_h = max(1, round(h * requested_scale))
    interpolation = cv2.INTER_AREA if requested_scale < 1.0 else cv2.INTER_CUBIC
    transformed = cv2.resize(image, (new_w, new_h), interpolation=interpolation)
    sx = new_w / float(w)
    sy = new_h / float(h)
    return transformed, [[1.0 / sx, 0.0, 0.0], [0.0, 1.0 / sy, 0.0], [0.0, 0.0, 1.0]]


def variant_crop(image: np.ndarray, margin_fraction: float = 0.03) -> tuple[np.ndarray, list[list[float]]]:
    h, w = image.shape[:2]
    x0 = round(w * margin_fraction)
    y0 = round(h * margin_fraction)
    x1 = w - x0
    y1 = h - y0
    if x1 <= x0 or y1 <= y0:
        raise RuntimeError("crop collapsed image")
    transformed = image[y0:y1, x0:x1].copy()
    return transformed, [[1.0, 0.0, float(x0)], [0.0, 1.0, float(y0)], [0.0, 0.0, 1.0]]


def variant_mirror(image: np.ndarray) -> tuple[np.ndarray, list[list[float]]]:
    _, w = image.shape[:2]
    transformed = cv2.flip(image, 1)
    return transformed, [[-1.0, 0.0, float(w - 1)], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]


def metrics_to_json(metrics: object) -> dict[str, object]:
    return {
        "name": metrics.name,
        "max_anchor_drift_fraction": metrics.max_anchor_drift_fraction,
        "mean_anchor_drift_fraction": metrics.mean_anchor_drift_fraction,
        "axis_angle_deg": metrics.axis_angle_deg,
        "width_rel_error": metrics.width_rel_error,
        "height_rel_error": metrics.height_rel_error,
        "max_canonical_grid_drift": metrics.max_canonical_grid_drift,
        "handedness_changed": metrics.handedness_changed,
    }


def run(output_dir: Path) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    model_path = output_dir / "hand_landmarker.task"
    image_path = output_dir / "Right_Hand_Palm.png"

    model_sha256 = download(MODEL_URL, model_path)
    source_sha256 = download(CASE_A_IMAGE_URL, image_path)

    original = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if original is None:
        raise RuntimeError("failed to decode Case A image")
    baseline_image, baseline_scale = ensure_max_dim(original)

    options = mp.tasks.vision.HandLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=str(model_path)),
        running_mode=mp.tasks.vision.RunningMode.IMAGE,
        num_hands=2,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    with mp.tasks.vision.HandLandmarker.create_from_options(options) as landmarker:
        baseline_detection = detect_one(landmarker, baseline_image)
        variant_factories = [
            ("same-pixels-rerun", lambda img: variant_identity(img)),
            ("rotate+10deg", lambda img: variant_rotate(img, +10.0)),
            ("rotate-10deg", lambda img: variant_rotate(img, -10.0)),
            ("scale-0.75x", lambda img: variant_scale(img, 0.75)),
            ("scale-1.25x", lambda img: variant_scale(img, 1.25)),
            ("crop-3pct", lambda img: variant_crop(img, 0.03)),
            ("horizontal-mirror", lambda img: variant_mirror(img)),
        ]

        variants = []
        variant_metadata = {}
        for name, factory in variant_factories:
            transformed, inverse = factory(baseline_image)
            detection = detect_one(landmarker, transformed)
            variants.append(
                {
                    "name": name,
                    "landmarks": detection["landmarks"],
                    "inverse_transform": inverse,
                    "handedness": detection["handedness"],
                }
            )
            variant_metadata[name] = {
                "shape": list(transformed.shape[:2]),
                "candidate_count": detection["candidate_count"],
                "selected_index": detection["selected_index"],
                "selected_bbox_area_normalized": detection["selected_bbox_area_normalized"],
            }

    study = {
        "baseline": {
            "landmarks": baseline_detection["landmarks"],
            "handedness": baseline_detection["handedness"],
        },
        "variants": variants,
    }
    metrics = evaluate_study(study)

    provenance = {
        "status": "research-only",
        "case": "Case A — single right palm",
        "source_page": CASE_A_SOURCE_PAGE,
        "source_license": CASE_A_LICENSE,
        "source_sha256": source_sha256,
        "source_original_shape": list(original.shape[:2]),
        "working_baseline_shape": list(baseline_image.shape[:2]),
        "working_baseline_scale_from_source": baseline_scale,
        "model_url": MODEL_URL,
        "model_sha256": model_sha256,
        "mediapipe_version": getattr(mp, "__version__", "unknown"),
        "opencv_version": cv2.__version__,
        "python_version": platform.python_version(),
        "target_selection": "largest normalized landmark bounding box; Case A expected single target",
        "baseline_candidate_count": baseline_detection["candidate_count"],
        "baseline_selected_index": baseline_detection["selected_index"],
        "baseline_selected_bbox_area_normalized": baseline_detection["selected_bbox_area_normalized"],
        "variant_metadata": variant_metadata,
    }

    (output_dir / "case_a_study.json").write_text(json.dumps(study, indent=2), encoding="utf-8")
    (output_dir / "case_a_provenance.json").write_text(json.dumps(provenance, indent=2), encoding="utf-8")
    (output_dir / "case_a_metrics.json").write_text(
        json.dumps([metrics_to_json(m) for m in metrics], indent=2), encoding="utf-8"
    )

    print("=== PROVENANCE ===")
    print(json.dumps(provenance, indent=2))
    print("=== METRICS ===")
    print_results(metrics)
    print("=== METRICS_JSON ===")
    print(json.dumps([metrics_to_json(m) for m in metrics], indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="palmistry-repeatability-output")
    args = parser.parse_args()
    return run(Path(args.output_dir))


if __name__ == "__main__":
    sys.exit(main())
