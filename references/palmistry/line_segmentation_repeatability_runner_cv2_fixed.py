#!/usr/bin/env python3
"""Corrected entrypoint for palm-line segmentation repeatability runner.

REFERENCE-ONLY. The first non-MOHI dry run exposed a synthetic-fixture-only
implementation typo: OpenCV Python has no ``cv2.arc`` primitive. This wrapper
preserves the full MOHI execution path from ``line_segmentation_repeatability_runner.py``
and replaces only the non-MOHI synthetic dry-run helper with the equivalent
``cv2.ellipse(..., startAngle, endAngle, ...)`` arc drawing call.
"""

from __future__ import annotations

import json

import cv2
import numpy as np

import line_segmentation_repeatability_runner as base


def dry_run_fixed(sess) -> None:
    side = 384
    rgb = np.zeros((side, side, 3), dtype=np.uint8)
    cv2.ellipse(
        rgb,
        (side // 2, side // 2 + 25),
        (105, 135),
        0,
        0,
        360,
        (175, 145, 125),
        -1,
    )
    for yoff in (-50, 0, 50):
        cv2.ellipse(
            rgb,
            (side // 2, side // 2 + yoff),
            (85, 45),
            0,
            190,
            345,
            (95, 75, 70),
            2,
        )

    baseline, logs = base.infer_mask(sess, rgb)
    variants = {}
    for name in (
        "rotate_p5",
        "rotate_m5",
        "scale_090",
        "scale_110",
        "center_crop_3pct",
    ):
        matrix = base.variant_matrix(name, side)
        variant_rgb = base.apply_variant(rgb, matrix)
        variant_mask, _ = base.infer_mask(sess, variant_rgb)
        mapped = base.inverse_map_mask(variant_mask, matrix)
        variants[name] = {
            "matrix_shape": list(matrix.shape),
            "mapped_shape": list(mapped.shape),
            "mapped_values_subset": sorted(int(x) for x in np.unique(mapped)),
        }

    print(
        json.dumps(
            {
                "mode": "NON-MOHI DRY RUN",
                "baseline_shape": list(baseline.shape),
                "baseline_values_subset": sorted(int(x) for x in np.unique(baseline)),
                "finite_logit_summary": all(np.isfinite(list(logs.values()))),
                "variants": variants,
                "schema": "PASS",
            },
            indent=2,
        )
    )


def main() -> None:
    base.dry_run = dry_run_fixed
    base.main()


if __name__ == "__main__":
    main()
