# Palm Line Segmentation G1 Repeatability — Upstream-Affine-Fixed Plan

Status: **REFERENCE-ONLY / PREDECLARED / NO CORRECTED-G1 PERTURBATION OUTPUT INSPECTED**

This v2 plan replaces the legacy G1 repeatability contract for future corrected-G1 qualification. The legacy plan/result remain historical evidence for the superseded rotate-canvas-then-crop implementation.

## Frozen upstream evidence dependency

Corrected adapter-diagnosis raw artifact:

```text
/home/user/palm-detector-study/results/MOHI_line_segmentation_adapter_diagnosis_upstream_affine_fixed.json
SHA256 = c51651cdc267b0416c0883ffba13e1ed0b5992aa808944e1786e2bc20d0e38d3
```

Corrected bounded result:

```text
C_G1_M0 = heart/head/life/all-three 10/10
D_G1_M1 = heart/head/life/all-three 10/10
```

Mirror again provides no presence-level gain, so corrected `C_G1_M0` remains the primary repeatability condition.

## Frozen model/runtime/sample

Unchanged from the legacy G1 repeatability study:

```text
student_fp32.onnx SHA256 = 3c02b88b82e54889d0ab2bf2ba108aec554a1b50759f7c7aaa45f2f114ed24ff
model_meta.json SHA256 = 880b17a1f0ae8f0ad9c4061b0674e86381f50fadb242a662b44fdbaf4b919a98
onnxruntime = 1.29.0
numpy = 1.26.4
opencv-python = 4.10.0.84
provider = CPUExecutionProvider
```

Reuse exactly:

```text
P001/S1/01.jpg
P002/S1/01.jpg
P003/S1/01.jpg
P004/S1/01.jpg
P005/S1/01.jpg
P006/S1/01.jpg
P007/S1/01.jpg
P008/S1/01.jpg
P009/S1/01.jpg
P010/S1/01.jpg
```

No source replacement or post-outcome exclusion.

## Corrected frozen C_G1_M0 crop

For each source:

1. decode raw RGB in the frozen raw-image frame;
2. use the frozen 21 MediaPipe landmarks;
3. center rotation on the mean of all 21 landmarks;
4. choose the rotation sign that places L9 above L0 and minimizes horizontal residual;
5. transform landmarks in the source-frame rotation affine;
6. compute the **float** rotated-landmark bbox plus fixed 100 px margin;
7. set output width/height to `ceil(bbox span)`;
8. copy the source-frame rotation affine and subtract the float bbox origin directly from affine translation;
9. perform one direct source-to-output `warpAffine` with bilinear interpolation and black border;
10. no square padding;
11. no horizontal mirror.

This direct source-to-crop affine composition is the fidelity-critical difference from the superseded v1 plan.

The adapter runner records:

```text
rotation_matrix_source_frame
crop_affine_matrix
rotated_landmark_bbox_xyxy_with_margin_float
```

The fixed 100 px margin remains frozen and must not be tuned.

## Frozen perturbations

Apply only after the corrected immutable C crop is constructed:

```text
baseline
rotate +5°
rotate -5°
scale 0.90×
scale 1.10×
center crop 3% each side then resize to baseline crop size
```

Rectangular-frame transform semantics remain unchanged from v1:

- rotate/scale about native crop center;
- output width/height remain equal to baseline crop dimensions;
- bilinear RGB transform;
- black introduced regions;
- center crop 3% independently in x/y;
- exact forward affine retained;
- predicted masks inverse-mapped to baseline crop frame with nearest-neighbor interpolation.

## Metrics and empty handling

Unchanged from v1:

- per-class presence;
- all-three presence;
- per-class Dice/IoU;
- foreground-union Dice/IoU;
- pixel counts;
- connected-component counts;
- largest-component fraction;
- presence transitions;
- predicted-class sets.

```text
both empty => not_applicable_empty_both; Dice/IoU = null
one empty  => appearance_transition; Dice/IoU = 0
```

## Frozen directional questions

1. Does corrected C baseline reproduce corrected adapter-diagnosis 10/10 all-three presence?
2. Do all three classes remain present under all five perturbations?
3. Which class is least repeatable under corrected C?
4. Which transform is most disruptive in corrected C?
5. Is foreground-union repeatability materially different from class-specific repeatability?
6. Does corrected P001 remain the main outlier, or was that behavior specific to the superseded crop implementation?
7. Does corrected P009 remain robustly observable?
8. Do component/topology changes remain bounded?
9. Does the corrected result materially reproduce or overturn the legacy G1 repeatability regime?

## Stop rules

Stop before substantive interpretation if:

- corrected adapter raw SHA does not match `c51651cdc267b0416c0883ffba13e1ed0b5992aa808944e1786e2bc20d0e38d3` in the runner provenance;
- model/runtime/source identity drifts;
- corrected C implementation differs from the corrected adapter diagnosis implementation;
- any baseline/variant affine is missing;
- inverse mapping is missing;
- any threshold, morphology, margin, mirror, class remapping, source exclusion, or rescue is introduced after result inspection.

## Execution accounting

Expected formal execution:

```text
10 source images × 6 conditions = 60 ONNX inference executions
```

Use a new output artifact name; do not overwrite the legacy G1 repeatability JSON.

## Evidence boundary

This node can qualify only corrected-G1 implementation repeatability. It cannot establish anatomical truth, segmentation accuracy, Palmistry validity, historical training truth, or production suitability.

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
