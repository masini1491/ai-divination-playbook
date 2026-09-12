# Palm Line Segmentation G1 Repeatability Qualification Plan

Status: **REFERENCE-ONLY / PREDECLARED / NO G1 PERTURBATION OUTPUT INSPECTED**

本文件凍結 adapter/domain diagnosis 之後的下一個 bounded evidence node：驗證 `C_G1_M0`（reconstructed-upstream-like geometry / no mirror）下，shipped FP32 palm-line segmentation model 對小幅幾何 perturbation 的 repeatability 與 class-presence robustness。

## Motivation

Adapter/domain diagnosis 已觀察到：

```text
A_G0_M0: heart 0/10, head 2/10, life 5/10
B_G0_M1: heart 0/10, head 2/10, life 3/10
C_G1_M0: heart 10/10, head 10/10, life 10/10
D_G1_M1: heart 10/10, head 10/10, life 10/10
```

此結果強烈指向 crop geometry 為主要 observability factor，而 mirror 不是主要 factor。

然而 `C/D` 的 10/10 all-three-class baseline activation 也可能反映 strong model prior，而不一定代表 anatomically correct segmentation。因此需要在固定 G1 geometry 下做 perturbation qualification，檢查這種 activation 是否 robust、是否 class-specific overlap stable、是否容易 appearance/disappearance 或 fragmentation。

## Frozen condition

Primary adapter：

```text
C_G1_M0
= reconstructed-upstream-like geometry
= no horizontal mirror
```

Selection rationale：

- G1 是 adapter diagnosis 中的 dominant factor；
- C 與 D 都達到 10/10 all-three presence；
- mirror 沒有 presence-level gain；
- C 少一個 transformation/assumption，因此作為 primary qualification condition。

`C_G1_M0` remains a **reconstructed geometry hypothesis**, not historical-training truth。

## Frozen model/runtime

Do not change：

```text
model: models/student_fp32.onnx
SHA256: 3c02b88b82e54889d0ab2bf2ba108aec554a1b50759f7c7aaa45f2f114ed24ff
metadata SHA256: 880b17a1f0ae8f0ad9c4061b0674e86381f50fadb242a662b44fdbaf4b919a98
onnxruntime: 1.29.0
numpy: 1.26.4
opencv-python: 4.10.0.84
provider: CPUExecutionProvider
```

Model preprocessing remains shipped contract：

```text
RGB
→ bilinear resize 512×512
→ float32 /255
→ ImageNet mean/std
→ NCHW
→ raw logits [1,4,512,512]
→ argmax axis 1
```

No threshold, softmax cutoff, morphology cleanup, skeletonization, class remapping, or post-hoc mask rescue。

## Frozen source sample

Reuse exactly the same 10 MOHI source entries：

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

Reuse the same MOHI package, frozen raw-image frame and frozen 21-point MediaPipe landmark evidence。

## Frozen C_G1_M0 crop

For each source image：

1. raw RGB decode in frozen raw-image frame；
2. use frozen L0..L20 coordinates；
3. rotation center = mean of all 21 landmarks；
4. choose sign so L9 is above L0 and horizontal residual is minimized；
5. rotate original image canvas about that center；
6. transform all landmarks through same affine matrix；
7. crop rotated-landmark bbox + fixed 100 px on each side；
8. black-pad outside source if needed；
9. no square-padding requirement；
10. no horizontal mirror；
11. resulting RGB crop is immutable baseline C crop for this source。

The 100 px margin is frozen before outcome inspection and must not be tuned。

## Frozen perturbations

Apply only after immutable C crop construction：

```text
baseline
rotate +5°
rotate -5°
scale 0.90×
scale 1.10×
center crop 3% each side then resize to baseline crop size
```

Same transform semantics as the first repeatability study：

- center-based；
- RGB rotation/scale uses bilinear interpolation；
- introduced regions black；
- center crop uses the exact continuous affine definition from first study；
- no brightness/contrast/blur/compression/color jitter/mirror。

Because C crops are not necessarily square, perturbation transforms must be defined in the crop’s native rectangular frame using crop center. Rotation/scale output canvas must remain the same baseline crop width/height. Center crop 3% is applied independently to width and height and resized back to baseline width/height.

## Inverse mapping

For each perturbation, retain exact forward affine matrix and inverse-map predicted masks to the baseline C crop frame with nearest-neighbor interpolation。

Baseline mask remains in baseline C crop frame。

All comparison metrics are computed only after inverse mapping to this common baseline C frame。

## Primary metrics

For each source × perturbation：

- per-class presence for classes 1/2/3；
- all-three-class presence boolean；
- per-class Dice / IoU vs baseline；
- foreground-union Dice / IoU；
- baseline / variant foreground pixel count；
- per-class connected-component count；
- largest-component fraction；
- presence transition status；
- foreground component count；
- per-image predicted-class set。

Empty handling remains frozen：

```text
both empty => not_applicable_empty_both, Dice/IoU = null
one empty  => appearance_transition, Dice/IoU = 0
```

Do not assign perfect agreement to both-empty cases。

## Aggregation order

Interpret in this order：

1. execution/source integrity；
2. baseline C class-presence accounting；
3. class-presence retention under each perturbation；
4. appearance/disappearance transitions；
5. per-class Dice/IoU；
6. foreground-union Dice/IoU；
7. component fragmentation / largest-component fraction；
8. per-image heterogeneity；
9. focused P001/P009 analysis；
10. bounded comparison against first-study G0 repeatability only at the level of presence/within-adapter behavior, not direct cross-crop pixel Dice。

## Frozen directional questions

Before any G1 perturbation outputs are inspected：

1. Does the C baseline reproduce the adapter-diagnosis 10/10 all-three-class presence?
2. Do all three classes remain present under all five small perturbations, or do appearance/disappearance transitions reappear?
3. Which class is least repeatable under C geometry?
4. Are rotations more disruptive than scale / mild crop under C, or does the first-study asymmetry remain context-dependent?
5. Is foreground-union repeatability materially higher than class-specific repeatability, indicating class-boundary uncertainty rather than foreground-presence instability?
6. Do P001/P009 remain all-three observable under perturbation, or was their G1 baseline activation brittle?
7. Do component counts remain near one component per class, or does small perturbation induce fragmentation?
8. Does C materially reduce the appearance/disappearance problem seen under G0 while preserving non-pathological occupancy?

## Stop rules

Stop before interpretation if：

- model/runtime/source identities drift；
- C crop implementation differs from the predeclared adapter diagnosis implementation；
- any C baseline fails deterministic reproduction；
- affine matrices are not retained；
- inverse mapping is not exact/recorded；
- perturbation requires threshold/morphology rescue；
- any source is excluded after seeing outcome；
- implementation changes after outcome inspection。

## Prohibitions

Do not：

- tune 100 px margin；
- add mirror after seeing results；
- add arbitrary new perturbations；
- tune threshold；
- morphologically clean masks；
- map tool-local classes to Chinese palmistry names；
- interpret predicted class presence as anatomical truth；
- derive production admission thresholds from 10 images；
- compare G0-vs-G1 pixel Dice without a common raw-image mapping。

## Execution accounting

Expected formal run：

```text
10 source images
× (1 baseline + 5 perturbations)
= 60 ONNX inference executions
```

## Evidence boundary

If successfully executed, this node can establish only：

> Under a pinned FP32 segmentation model and fixed reconstructed-upstream-like no-mirror crop, how robust the model’s own three tool-local palm-line classes are to small geometric perturbations on the bounded 10-image MOHI sample.

It cannot establish anatomical truth, palmistry correctness, historical training preprocessing, or production suitability。

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
