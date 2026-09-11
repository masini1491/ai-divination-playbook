#!/usr/bin/env python3
"""Cold research probe for scene-local association ambiguity.

Builds a synthetic twin-hand composite from the pinned MediaPipe upstream
`right_hands.jpg` fixture, then moves a duplicate of one detected hand toward the
fixed baseline target. MediaPipe is run on every composite so candidate counts,
ranking, separation, and collapse/loss are observed from real detector output.

The compositing itself is synthetic research instrumentation. It is not a natural
capture distribution, biometric identity logic, or a production admission rule.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np

from real_image_repeatability_probe import Point, build_basis, norm

FIXTURE_URL = (
    "https://storage.googleapis.com/mediapipe-assets/tasks/testdata/vision/"
    "right_hands.jpg?generation=1782185275057115"
)
FIXTURE_SHA256 = "4b5134daa4cb60465535239535f9f74c2842aba3aa5fd30bf04ef5678f93d87f"
MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/1/hand_landmarker.task"
)
MODEL_SHA256 = "fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1"
USER_AGENT = "ai-divination-playbook-palmistry-research/1.0"
ANCHORS = (0, 5, 17)
SEPARATION_FRACTIONS = (2.50, 2.00, 1.50, 1.25, 1.00, 0.75, 0.50, 0.35, 0.25, 0.15, 0.00)


def download(url: str, destination: Path) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    h = hashlib.sha256()
    with urllib.request.urlopen(req, timeout=60) as response, destination.open("wb") as out:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)
            h.update(chunk)
    return h.hexdigest()


def category_name(category: object) -> str | None:
    for attr in ("category_name", "display_name"):
        value = getattr(category, attr, None)
        if isinstance(value, str) and value:
            return value
    return None


def detect_full(landmarker: object, image_bgr: np.ndarray) -> list[dict[str, object]]:
    rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    image = mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(rgb))
    result = landmarker.detect(image)
    height, width = image_bgr.shape[:2]
    out: list[dict[str, object]] = []
    for index, landmarks in enumerate(result.hand_landmarks):
        handedness = None
        if index < len(result.handedness) and result.handedness[index]:
            handedness = category_name(result.handedness[index][0])
        pixels = [[float(point.x) * width, float(point.y) * height] for point in landmarks]
        xs = [point[0] for point in pixels]
        ys = [point[1] for point in pixels]
        out.append(
            {
                "index": index,
                "handedness": handedness,
                "all_landmarks": pixels,
                "landmarks": {str(anchor): pixels[anchor] for anchor in ANCHORS},
                "bbox_area_normalized":
                    (max(xs) - min(xs)) * (max(ys) - min(ys)) / float(width * height),
            }
        )
    return out


def anchor_points(candidate: dict[str, object]) -> dict[int, Point]:
    raw = candidate["landmarks"]
    assert isinstance(raw, dict)
    return {int(key): Point(float(value[0]), float(value[1])) for key, value in raw.items()}


def palm_width(candidate: dict[str, object]) -> float:
    return build_basis(anchor_points(candidate)).width


def build_hand_layer(image: np.ndarray, candidate: dict[str, object]) -> tuple[np.ndarray, np.ndarray]:
    raw = candidate["all_landmarks"]
    assert isinstance(raw, list)
    points = np.array([[round(float(x)), round(float(y))] for x, y in raw], dtype=np.int32)
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    hull = cv2.convexHull(points)
    cv2.fillConvexPoly(mask, hull, 255)
    radius = max(4, round(0.12 * palm_width(candidate)))
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * radius + 1, 2 * radius + 1))
    mask = cv2.dilate(mask, kernel)
    blur = max(3, radius // 2 * 2 + 1)
    mask = cv2.GaussianBlur(mask, (blur, blur), 0)
    nonzero = cv2.findNonZero((mask > 8).astype(np.uint8))
    if nonzero is None:
        raise RuntimeError("hand mask is empty")
    x, y, w, h = cv2.boundingRect(nonzero)
    return image[y : y + h, x : x + w].copy(), mask[y : y + h, x : x + w].copy()


def paste_layer(canvas: np.ndarray, patch: np.ndarray, alpha: np.ndarray, center: tuple[int, int]) -> None:
    patch_h, patch_w = patch.shape[:2]
    left = round(center[0] - patch_w / 2)
    top = round(center[1] - patch_h / 2)
    right = left + patch_w
    bottom = top + patch_h

    x0 = max(0, left)
    y0 = max(0, top)
    x1 = min(canvas.shape[1], right)
    y1 = min(canvas.shape[0], bottom)
    if x1 <= x0 or y1 <= y0:
        return

    px0 = x0 - left
    py0 = y0 - top
    px1 = px0 + (x1 - x0)
    py1 = py0 + (y1 - y0)
    patch_view = patch[py0:py1, px0:px1].astype(np.float32)
    alpha_view = alpha[py0:py1, px0:px1].astype(np.float32)[..., None] / 255.0
    base = canvas[y0:y1, x0:x1].astype(np.float32)
    canvas[y0:y1, x0:x1] = np.clip(patch_view * alpha_view + base * (1.0 - alpha_view), 0, 255).astype(np.uint8)


def score_candidates(
    candidates: list[dict[str, object]], baseline_target: dict[str, object], baseline_width: float
) -> dict[str, object]:
    baseline = anchor_points(baseline_target)
    scored: list[tuple[float, float, dict[str, object]]] = []
    for candidate in candidates:
        points = anchor_points(candidate)
        distances = [norm(points[anchor] - baseline[anchor]) / baseline_width for anchor in ANCHORS]
        scored.append((sum(distances) / len(distances), max(distances), candidate))
    scored.sort(key=lambda item: item[0])
    if not scored:
        return {
            "best_mean_anchor_distance_fraction": None,
            "best_max_anchor_distance_fraction": None,
            "second_best_mean_anchor_distance_fraction": None,
            "separation_fraction": None,
            "candidate_scores": [],
        }
    second = scored[1][0] if len(scored) > 1 else None
    return {
        "best_mean_anchor_distance_fraction": scored[0][0],
        "best_max_anchor_distance_fraction": scored[0][1],
        "second_best_mean_anchor_distance_fraction": second,
        "separation_fraction": None if second is None else second - scored[0][0],
        "candidate_scores": [
            {
                "index": candidate["index"],
                "handedness": candidate["handedness"],
                "mean_anchor_distance_fraction": mean_distance,
                "max_anchor_distance_fraction": max_distance,
            }
            for mean_distance, max_distance, candidate in scored
        ],
    }


def run(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    fixture_path = output_dir / "right_hands.jpg"
    model_path = output_dir / "hand_landmarker.task"
    fixture_sha = download(FIXTURE_URL, fixture_path)
    model_sha = download(MODEL_URL, model_path)
    if fixture_sha != FIXTURE_SHA256:
        raise RuntimeError(f"fixture SHA mismatch: {fixture_sha}")
    if model_sha != MODEL_SHA256:
        raise RuntimeError(f"model SHA mismatch: {model_sha}")

    source = cv2.imread(str(fixture_path), cv2.IMREAD_COLOR)
    if source is None:
        raise RuntimeError("failed to decode upstream fixture")

    options = mp.tasks.vision.HandLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=str(model_path)),
        running_mode=mp.tasks.vision.RunningMode.IMAGE,
        num_hands=4,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    with mp.tasks.vision.HandLandmarker.create_from_options(options) as landmarker:
        source_candidates = detect_full(landmarker, source)
        if len(source_candidates) < 2:
            raise RuntimeError(f"expected >=2 source candidates, got {len(source_candidates)}")
        source_target = max(source_candidates, key=lambda item: float(item["bbox_area_normalized"]))
        patch, alpha = build_hand_layer(source, source_target)
        source_width = palm_width(source_target)

        margin = max(30, round(0.30 * source_width))
        canvas_h = max(source.shape[0], patch.shape[0] + 2 * margin)
        canvas_w = max(
            source.shape[1],
            round(patch.shape[1] + 2 * margin + max(SEPARATION_FRACTIONS) * source_width),
        )
        target_center = (margin + patch.shape[1] // 2, canvas_h // 2)

        baseline_canvas = np.full((canvas_h, canvas_w, 3), 255, dtype=np.uint8)
        paste_layer(baseline_canvas, patch, alpha, target_center)
        baseline_candidates = detect_full(landmarker, baseline_canvas)
        if not baseline_candidates:
            raise RuntimeError("isolated baseline composite produced no hand candidate")
        baseline_target = min(
            baseline_candidates,
            key=lambda item: abs(float(item["bbox_area_normalized"]) - float(source_target["bbox_area_normalized"])),
        )
        baseline_width = palm_width(baseline_target)

        rows = []
        for requested_separation in SEPARATION_FRACTIONS:
            canvas = np.full_like(baseline_canvas, 255)
            paste_layer(canvas, patch, alpha, target_center)
            competitor_center = (
                target_center[0] + round(requested_separation * baseline_width),
                target_center[1],
            )
            paste_layer(canvas, patch, alpha, competitor_center)
            candidates = detect_full(landmarker, canvas)
            score = score_candidates(candidates, baseline_target, baseline_width)
            rows.append(
                {
                    "requested_copy_separation_fraction": requested_separation,
                    "candidate_count": len(candidates),
                    "best_mean_anchor_distance_fraction": score["best_mean_anchor_distance_fraction"],
                    "best_max_anchor_distance_fraction": score["best_max_anchor_distance_fraction"],
                    "second_best_mean_anchor_distance_fraction": score["second_best_mean_anchor_distance_fraction"],
                    "separation_fraction": score["separation_fraction"],
                    "candidate_scores": score["candidate_scores"],
                }
            )

    result = {
        "status": "research-only",
        "fixture_sha256": fixture_sha,
        "model_sha256": model_sha,
        "mediapipe_version": getattr(mp, "__version__", "unknown"),
        "opencv_version": cv2.__version__,
        "source_candidate_count": len(source_candidates),
        "source_selected_index": source_target["index"],
        "source_palm_width_px": source_width,
        "baseline_composite_shape_h_w": [canvas_h, canvas_w],
        "isolated_baseline_candidate_count": len(baseline_candidates),
        "isolated_baseline_selected_index": baseline_target["index"],
        "isolated_baseline_palm_width_px": baseline_width,
        "composition": (
            "one detected source hand is isolated with a dilated/feathered convex-hull mask; "
            "a duplicate is pasted on a white canvas at controlled horizontal offsets"
        ),
        "rows": rows,
    }
    (output_dir / "association_ambiguity.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    print("requested_sep | candidates | best_mean | second_best | score_gap")
    for row in rows:
        def fmt(value: object) -> str:
            return "-" if value is None else f"{float(value) * 100.0:.3f}%"
        print(
            f"{row['requested_copy_separation_fraction']:>5.2f}W | {row['candidate_count']:>2} | "
            f"{fmt(row['best_mean_anchor_distance_fraction']):>9} | "
            f"{fmt(row['second_best_mean_anchor_distance_fraction']):>11} | "
            f"{fmt(row['separation_fraction']):>9}"
        )
    print("=== ASSOCIATION_AMBIGUITY_JSON ===")
    print(json.dumps(result, indent=2))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="palmistry-association-ambiguity-output")
    args = parser.parse_args()
    result = run(Path(args.output_dir))
    if not any(int(row["candidate_count"]) >= 2 for row in result["rows"]):
        raise RuntimeError("stress sweep never exercised a multi-candidate state")
    return 0


if __name__ == "__main__":
    sys.exit(main())
