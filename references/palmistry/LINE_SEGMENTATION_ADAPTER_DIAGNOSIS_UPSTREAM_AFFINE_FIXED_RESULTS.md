# Palm Line Segmentation Adapter Diagnosis — Upstream-Affine-Fixed Results

Status: **REFERENCE-ONLY / CORRECTED BOUNDED RESULT / RAW ARTIFACT HASH PINNED**

This document supersedes the legacy C/D interpretation in `LINE_SEGMENTATION_ADAPTER_DOMAIN_DIAGNOSIS_RESULTS.md` for exact-upstream-affine G1 ranking. A/B are unaffected by the G1 affine correction.

Corrected raw artifact:

```text
/home/user/palm-detector-study/results/MOHI_line_segmentation_adapter_diagnosis_upstream_affine_fixed.json
```

SHA256:

```text
c51651cdc267b0416c0883ffba13e1ed0b5992aa808944e1786e2bc20d0e38d3
```

Execution:

```text
10 frozen sources × 4 adapters = 40 ONNX inference executions
stop = false
```

## Corrected aggregate summary

| Adapter | heart | head | life | any foreground | all three | FG fraction mean | FG components mean |
|---|---:|---:|---:|---:|---:|---:|---:|
| A_G0_M0 | 0/10 | 2/10 | 5/10 | 5/10 | 0/10 | 0.001591 | 1.2 |
| B_G0_M1 | 0/10 | 2/10 | 3/10 | 5/10 | 0/10 | 0.000878 | 0.8 |
| C_G1_M0 | 10/10 | 10/10 | 10/10 | 10/10 | 10/10 | 0.014686 | 3.2 |
| D_G1_M1 | 10/10 | 10/10 | 10/10 | 10/10 | 10/10 | 0.016436 | 2.6 |

## Frozen factor questions after fidelity correction

### Mirror at G0

```text
A_G0_M0 -> B_G0_M1
heart: 0 -> 0
head : 2 -> 2
life : 5 -> 3
any  : 5 -> 5
all3 : 0 -> 0
```

No observability gain is produced by mirror alone under G0.

### Mirror at G1

```text
C_G1_M0 -> D_G1_M1
heart: 10 -> 10
head : 10 -> 10
life : 10 -> 10
any  : 10 -> 10
all3 : 10 -> 10
```

No presence-level mirror gain appears once G1 geometry is used.

### Geometry at M0

```text
A_G0_M0 -> C_G1_M0
heart: 0 -> 10
head : 2 -> 10
life : 5 -> 10
any  : 5 -> 10
all3 : 0 -> 10
```

### Geometry at M1

```text
B_G0_M1 -> D_G1_M1
heart: 0 -> 10
head : 2 -> 10
life : 3 -> 10
any  : 5 -> 10
all3 : 0 -> 10
```

The dominant first-order factor therefore remains crop geometry, not horizontal mirror.

## Legacy versus corrected G1 behavior

Legacy C/D had the same 10/10 presence regime:

```text
legacy C_G1_M0: all three = 10/10
legacy D_G1_M1: all three = 10/10
```

The corrected affine preserves this regime exactly.

Aggregate foreground occupancy changes are small:

```text
C FG fraction mean: 0.014706 -> 0.014686
D FG fraction mean: 0.016468 -> 0.016436
```

Aggregate foreground component means change modestly:

```text
C: 3.0 -> 3.2
D: 2.5 -> 2.6
```

Per-image corrected crop dimensions differ from legacy by at most approximately one pixel per reported dimension in this bounded sample. All ten legacy-to-corrected C and D predicted-class sets remain `heart_line + head_line + life_line`.

Thus the implementation-fidelity correction is materially important for provenance, but it does **not** change the substantive adapter-regime conclusion on this sample.

## P001 and P009

Corrected C/D continue to restore all three shipped classes for both P001 and P009.

Examples under corrected C_G1_M0:

```text
P001 foreground fraction = 0.003260, all three present
P009 foreground fraction = 0.018659, all three present
```

This preserves the bounded conclusion that G0 non-observability for those images is not invariant to crop geometry.

## Corrected affine provenance

The corrected G1 implementation uses:

1. frozen 21-point landmarks in the raw image frame;
2. rotation center = mean of all 21 points;
3. sign selection that places L9 above L0 and minimizes horizontal residual;
4. float rotated-landmark bbox + fixed 100 px margin;
5. output width/height = `ceil(bbox span)`;
6. bbox origin absorbed directly into affine translation;
7. one direct source-to-output `warpAffine`;
8. no horizontal mirror for C; horizontal mirror after crop for D.

The runner records `rotation_matrix_source_frame`, `crop_affine_matrix`, and `rotated_landmark_bbox_xyxy_with_margin_float` for G1 provenance.

## Overall bounded corrected diagnosis

The corrected result supports the same first-order conclusion as the legacy diagnosis, now with the upstream-affine fidelity issue closed:

> On this bounded ten-image MOHI sample, reconstructed-upstream-like G1 crop geometry changes the shipped FP32 model from sparse/partial G0 predictions to all-three-class predictions on every source image, while horizontal mirror provides no presence-level gain.

This does **not** establish anatomical correctness or segmentation accuracy. The all-three 10/10 regime can still be consistent with either better image/model compatibility or a strong learned structural prior.

## Next evidence node

Proceed to a new, separately predeclared **upstream-affine-fixed G1 repeatability qualification** using corrected `C_G1_M0` and corrected adapter artifact SHA:

```text
c51651cdc267b0416c0883ffba13e1ed0b5992aa808944e1786e2bc20d0e38d3
```

The legacy G1 repeatability artifact and result remain historical evidence for the superseded crop implementation and must not be reused as the corrected repeatability result.

## Evidence boundary

Do not infer:

- anatomical correctness;
- segmentation ground-truth accuracy;
- Palmistry interpretation validity;
- equivalence to Chinese palm-line terminology;
- historical training truth;
- production admission thresholds.

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
