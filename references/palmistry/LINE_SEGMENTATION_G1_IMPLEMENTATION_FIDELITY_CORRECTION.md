# Palm Line Segmentation G1 Implementation Fidelity Correction

Status: **REFERENCE-ONLY / PRE-EXISTING FIDELITY ISSUE CORRECTED / G1 RERUN REQUIRED**

## Scope

This document records an implementation-fidelity issue in the first `G1_reconstructed_upstream_like` runner and the governance consequence for already-produced G1 artifacts.

The issue concerns only the C/D reconstructed-upstream-like crop path. A/B first-study geometry is unaffected.

## Pinned upstream behavior

Pinned upstream source：

```text
samuelwbarber/palm-line-reader
revision bc48939f4deee6d8ff842bfde499396dab9c4830
pipeline/hand_preprocess.py
```

After choosing the fingers-up rotation, upstream reconstruction computes：

```text
x0,y0 = rotated landmark min - margin
x1,y1 = rotated landmark max + margin
out_w = ceil(x1-x0)
out_h = ceil(y1-y0)
```

using the **float** bbox coordinates. It then copies the selected rotation matrix, subtracts the float `x0/y0` directly from affine translation, and performs one `cv2.warpAffine` from the original source into `(out_w,out_h)`.

Therefore the bbox-origin translation is part of the affine transform itself; there is no intermediate source-sized rotated canvas followed by a second crop.

## Previous local implementation

The first local G1 implementation instead：

1. rounded bbox boundaries using floor/ceil；
2. warped the source into the original `(w,h)` canvas；
3. cropped/padded that intermediate rotated canvas using integer bounds。

This could clip or shift content near source boundaries and did not reproduce the pinned reconstruction's float affine/crop semantics exactly.

The concern was implementation-level, not outcome-derived. It is therefore corrected without changing：

- model；
- runtime；
- source sample；
- frozen landmarks；
- rotation-sign selection；
- fixed 100 px margin；
- mirror definitions；
- class mapping；
- thresholds；
- morphology。

## Corrected implementation

`line_segmentation_adapter_diagnosis_runner.py` now：

```text
rp = rotate_points(points, best_matrix)
x0,y0 = rp.min - 100.0
x1,y1 = rp.max + 100.0
out_w = ceil(x1-x0)
out_h = ceil(y1-y0)

crop_matrix = best_matrix.copy()
crop_matrix[0,2] -= x0
crop_matrix[1,2] -= y0

crop = warpAffine(original_rgb, crop_matrix, (out_w,out_h))
```

Metadata now retains both：

```text
rotation_matrix_source_frame
crop_affine_matrix
rotated_landmark_bbox_xyxy_with_margin_float
```

## Governance consequence for existing artifacts

The following already-produced artifacts are preserved and must **not** be deleted or overwritten：

```text
MOHI_line_segmentation_adapter_diagnosis.json
SHA256 83becc491dbebbe9cbf053a023f43303750b6e38d6a9cc662f1718cf8f30f423

MOHI_line_segmentation_g1_repeatability.json
SHA256 d15169f7e849840f19aa29d7336005799e90ff4cf93b536f73b0199b5047dab0
```

They remain useful only as **legacy diagnostic evidence for the superseded G1 implementation**.

A/B observations inside the first adapter-diagnosis artifact remain technically unaffected by this correction. C/D observations and any downstream `C_G1_M0` repeatability interpretation are superseded for exact-upstream-fidelity qualification until rerun.

Accordingly, previous statements such as "G1 repeatability bounded PASS" must not be treated as the current qualification state. The current state is：

```text
corrected G1 implementation ready for re-validation
substantive corrected-G1 MOHI output not yet inspected
```

## Required rerun order

1. run syntax check + non-MOHI adapter dry run on corrected runner；
2. run corrected adapter diagnosis to a **new output filename**；
3. hash corrected adapter artifact；
4. inspect corrected adapter result；
5. update downstream G1 repeatability provenance to corrected adapter hash；
6. rerun G1 repeatability to another **new output filename**；
7. hash and interpret corrected repeatability artifact；
8. only then decide whether to proceed to content-dependence / specificity control。

Recommended corrected adapter output filename：

```text
MOHI_line_segmentation_adapter_diagnosis_upstream_affine_fixed.json
```

The old artifact must remain unchanged for auditability.

## Evidence boundary

This correction does not assert that the pinned upstream reconstruction is historical training truth; upstream itself labels the preprocessing module a reconstruction. The correction only makes the local `G1` hypothesis faithful to that pinned reconstruction's affine/crop implementation.

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
