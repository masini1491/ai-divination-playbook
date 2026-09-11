#!/usr/bin/env python3
"""Cold research probe for retained-two-candidate association near-ties.

Uses the same isolated hand layer as ASSOCIATION_AMBIGUITY_STRESS, but places two
identical hand copies symmetrically around the isolated baseline target. The pair
stays spatially separated while its center is shifted across the baseline target,
which can create two detector candidates that are both plausible scene-local
successors.

Requested composition geometry is preserved separately from detector-observed
candidate geometry. This is synthetic research instrumentation, not biometric
identity logic and not a production admission threshold.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np

from association_ambiguity_probe import (
    ANCHORS,
    FIXTURE_SHA256,
    FIXTURE_URL,
    MODEL_SHA256,
    MODEL_URL,
    anchor_points,
    build_hand_layer,
    detect_full,
    download,
    palm_width,
    paste_layer,
    score_candidates,
)
from real_image_repeatability_probe import norm

PAIR_SEPARATION_FRACTION = 2.00
CENTER_BIASES = (-0.30, -0.20, -0.15, -0.10, -0.05, 0.00, 0.05, 0.10, 0.15, 0.20, 0.30)


def observed_pair_distance(candidates: list[dict[str, object]], baseline_width: float) -> float | None:
    if len(candidates) < 2:
        return None
    first = anchor_points(candidates[0])
    second = anchor_points(candidates[1])
    distances = [norm(first[anchor] - second[anchor]) / baseline_width for anchor in ANCHORS]
    return sum(distances) / len(distances)


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

        margin = max(40, round(0.40 * source_width))
        required_span = (PAIR_SEPARATION_FRACTION + 2 * max(abs(v) for v in CENTER_BIASES)) * source_width
        canvas_w = max(source.shape[1], round(required_span + patch.shape[1] + 2 * margin))
        canvas_h = max(source.shape[0], patch.shape[0] + 2 * margin)
        baseline_center = (canvas_w // 2, canvas_h // 2)

        baseline_canvas = np.full((canvas_h, canvas_w, 3), 255, dtype=np.uint8)
        paste_layer(baseline_canvas, patch, alpha, baseline_center)
        baseline_candidates = detect_full(landmarker, baseline_canvas)
        if not baseline_candidates:
            raise RuntimeError("isolated baseline composite produced no hand candidate")
        baseline_target = min(
            baseline_candidates,
            key=lambda item: abs(float(item["bbox_area_normalized"]) - float(source_target["bbox_area_normalized"])),
        )
        baseline_width = palm_width(baseline_target)

        rows = []
        for requested_bias in CENTER_BIASES:
            canvas = np.full_like(baseline_canvas, 255)
            pair_center_x = baseline_center[0] + round(requested_bias * baseline_width)
            half_span = 0.5 * PAIR_SEPARATION_FRACTION * baseline_width
            left_center = (round(pair_center_x - half_span), baseline_center[1])
            right_center = (round(pair_center_x + half_span), baseline_center[1])
            paste_layer(canvas, patch, alpha, left_center)
            paste_layer(canvas, patch, alpha, right_center)

            candidates = detect_full(landmarker, canvas)
            score = score_candidates(candidates, baseline_target, baseline_width)
            ranked = score["candidate_scores"]
            row = {
                "requested_pair_separation_fraction": PAIR_SEPARATION_FRACTION,
                "requested_pair_center_bias_fraction": requested_bias,
                "candidate_count": len(candidates),
                "observed_candidate_pair_mean_anchor_distance_fraction": observed_pair_distance(candidates, baseline_width),
                "best_mean_anchor_distance_fraction": score["best_mean_anchor_distance_fraction"],
                "best_max_anchor_distance_fraction": score["best_max_anchor_distance_fraction"],
                "second_best_mean_anchor_distance_fraction": score["second_best_mean_anchor_distance_fraction"],
                "score_separation_fraction": score["separation_fraction"],
                "best_index": None if not ranked else ranked[0]["index"],
                "second_index": None if len(ranked) < 2 else ranked[1]["index"],
                "candidate_scores": ranked,
            }
            rows.append(row)

    retained = [row for row in rows if int(row["candidate_count"]) >= 2]
    min_gap_row = None
    if retained:
        min_gap_row = min(
            retained,
            key=lambda row: float(row["score_separation_fraction"])
            if row["score_separation_fraction"] is not None
            else float("inf"),
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
        "isolated_baseline_candidate_count": len(baseline_candidates),
        "isolated_baseline_selected_index": baseline_target["index"],
        "isolated_baseline_palm_width_px": baseline_width,
        "requested_pair_separation_fraction": PAIR_SEPARATION_FRACTION,
        "requested_center_biases": list(CENTER_BIASES),
        "measurement_boundary": (
            "requested_pair_separation_fraction and requested_pair_center_bias_fraction are composition inputs; "
            "observed_candidate_pair_mean_anchor_distance_fraction and association scores are post-detector observations"
        ),
        "composition": (
            "two identical copies of one detected source hand are pasted on a white canvas; "
            "their requested separation is fixed at 2.00 isolated-baseline palm widths while the pair center shifts across the baseline target"
        ),
        "rows": rows,
        "minimum_observed_score_gap_retained_two_candidate_row": min_gap_row,
    }
    (output_dir / "association_near_tie.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    print("bias | candidates | observed_pair | best | second | score_gap | best_idx | second_idx")
    for row in rows:
        def pct(value: object) -> str:
            return "-" if value is None else f"{float(value) * 100.0:.3f}%"
        print(
            f"{float(row['requested_pair_center_bias_fraction']):+0.2f}W | "
            f"{int(row['candidate_count']):>2} | "
            f"{pct(row['observed_candidate_pair_mean_anchor_distance_fraction']):>11} | "
            f"{pct(row['best_mean_anchor_distance_fraction']):>9} | "
            f"{pct(row['second_best_mean_anchor_distance_fraction']):>9} | "
            f"{pct(row['score_separation_fraction']):>9} | "
            f"{str(row['best_index']):>3} | {str(row['second_index']):>3}"
        )
    print("=== RETAINED_TWO_CANDIDATE_NEAR_TIE_JSON ===")
    print(json.dumps(result, indent=2))

    if not retained:
        raise RuntimeError("no retained-two-candidate row was observed")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="palmistry-association-near-tie-output")
    args = parser.parse_args()
    run(Path(args.output_dir))
    return 0


if __name__ == "__main__":
    sys.exit(main())
