#!/usr/bin/env python3
"""REFERENCE-ONLY corrected-G1 repeatability qualification wrapper.

Implements LINE_SEGMENTATION_G1_REPEATABILITY_UPSTREAM_AFFINE_FIXED_PLAN.md.
Reuses the validated rectangular perturbation/inverse-mapping implementation
from line_segmentation_g1_repeatability_runner.py, but pins provenance to the
corrected upstream-affine-fixed adapter diagnosis artifact. The imported
adapter module provides the corrected direct source-to-crop G1 affine.
"""

from __future__ import annotations

import line_segmentation_g1_repeatability_runner as impl

CORRECTED_ADAPTER_DIAGNOSIS_SHA = (
    "c51651cdc267b0416c0883ffba13e1ed0b5992aa808944e1786e2bc20d0e38d3"
)


def main() -> None:
    # Provenance-only correction: the shared implementation imports the current
    # corrected adapter module. Override the legacy artifact reference before
    # execution so emitted JSON points to the corrected upstream evidence node.
    impl.REFERENCE_ADAPTER_DIAGNOSIS_SHA = CORRECTED_ADAPTER_DIAGNOSIS_SHA
    impl.main()


if __name__ == "__main__":
    main()
