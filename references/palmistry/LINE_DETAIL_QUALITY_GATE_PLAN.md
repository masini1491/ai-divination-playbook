# Principal-line Line-detail Quality Gate — Predeclared Plan

Status: **REFERENCE-ONLY / PREDECLARED RESEARCH PLAN / NO PRODUCTION THRESHOLD**

## Purpose

本 Cold plan 凍結 principal-line observation 的下一個 bounded evidence node：

> 當 palm image 的 line-detail quality 因失焦、有效解析度降低或對比壓縮而下降時，已通過 bounded class-specificity audit 的 `heart_line / head_line / life_line` segmentation 與 frozen manual reference 的 agreement 是否系統性下降？哪些 image-quality descriptor 值得保留為 future admission evidence family？

本研究不是 production quality-gate calibration，也不建立 cutoff。

## Why this node is next

既有 evidence 已完成：

- corrected `C_G1_M0` adapter diagnosis；
- bounded implementation repeatability；
- content-dependence與 spatial-structure controls；
- blind manual anatomical audit；
- P001 post-hoc blur caveat；
- principal-line class-specificity bounded closure。

因此目前 bottleneck 已不是「模型是否有 class-specific spatial meaning」，而是：

```text
pipeline can execute
≠ image is sufficiently observable
≠ output should be admitted as a Palm Observation Fact
```

`PHOTO_VALIDATION.md` 與 `OBSERVATION_SCHEMA_DRAFT.md` 已把 `quality.line_detail` 列為 task-specific gate；P001 又提供直接 case evidence：影像過於模糊時，人工 trace 本身就可能需要猜測。

## Frozen provenance

Reuse only already-frozen research assets：

```text
corrected adapter                    = C_G1_M0
frozen manual annotation SHA256      = 51c4886e20cb9aee2d660fe1ca39f25b927398261478c013090ab5d611858041
frozen manual comparison result SHA  = 6f95828b70b388028a46ee1879835d432d9dd695bdbbdd1f2656b6ebf3572284
spatial-structure raw SHA256          = ba65456e3c7c3a645a4000c721961d0f600b46541ffc7e7566525b99a55f87e7
line comparison tolerance             = 8 px in 512×512 corrected frame
```

Model/runtime/normalization/class mapping must remain identical to the bounded anatomical audit unless a future amendment is committed before execution。

## Source-set rule

### Primary quantitative set

Use：

```text
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

`P001/S1/01.jpg` is **excluded from the primary reference-based quantitative set before this study executes** because the observer has already recorded that its frozen manual trace was partly inferred from a blurry source image。

This does not alter or replace the original 10-image audit。P001 remains available only as a descriptive natural low-quality sentinel。

No other source may be removed after results are seen。

## Why the existing manual reference can be reused

This first quality study uses **geometry-preserving photometric/detail degradations only**。

The 512×512 pixel coordinate frame remains unchanged：

```text
no rotation
no translation
no crop
no mirror
no geometric warp
```

Therefore the already-frozen manual centerlines for P002–P010 remain in the same pixel coordinates and may serve as fixed reference geometry without post-outcome re-annotation。

## Frozen degradation families

For every primary source, evaluate the original corrected baseline plus the following variants。

### A. Gaussian blur

Apply isotropic Gaussian blur in the final 512×512 model-input frame：

```text
sigma = 1.5 px
sigma = 3.0 px
sigma = 6.0 px
```

Kernel size must be deterministically derived large enough to contain the Gaussian support and reported in execution metadata。

### B. Resolution destruction

Downsample the 512×512 corrected image using area resampling, then resize back to 512×512 using bilinear interpolation：

```text
256 × 256 → 512 × 512
128 × 128 → 512 × 512
 64 × 64  → 512 × 512
```

This changes available spatial detail while preserving output-frame geometry。

### C. Contrast compression

Around per-channel midpoint `127.5`, apply：

```text
I' = 127.5 + factor × (I - 127.5)
```

with：

```text
factor = 0.75
factor = 0.50
factor = 0.25
```

Clip only to legal 8-bit range after the transform。Record clipping fraction as a manipulation check。

## Intentionally excluded from this first node

Do not include：

- JPEG compression；
- synthetic glare patch；
- uneven illumination；
- color-temperature shift；
- crop / occlusion；
- rotation / scale；
- denoising / sharpening rescue；
- threshold sweep；
- morphology cleanup。

Those are separate evidence families。This study first isolates focus/detail/contrast degradation under invariant geometry。

## Expected execution accounting

Primary set：

```text
9 sources
× (1 baseline + 9 degradation variants)
= 90 inference conditions
```

P001 may be evaluated descriptively but is not included in primary aggregate reference-based summaries。

## Manipulation-check descriptors

For every input condition record at minimum：

1. grayscale Laplacian variance；
2. grayscale Tenengrad / Sobel gradient-energy summary；
3. grayscale RMS contrast；
4. image mean / standard deviation；
5. transform family and nominal level；
6. formal clipping fraction；
7. source image identity and input-image SHA256。

These descriptors are **research observability features**, not admission scores。

Do not select a descriptor after results merely because it correlates best。All listed descriptors must be reported。

## Frozen model outputs

For each condition record：

- presence / pixel count for shipped class 1/2/3；
- foreground-union pixel count；
- class mask SHA256 or equivalent deterministic mask digest；
- model/logit finite checks；
- no threshold or class remapping changes。

## Primary comparison metrics

For each manual class on every P002–P010 condition, compare degraded-condition model output against the **same frozen manual reference** with the existing 8 px geometry：

1. model-on-reference coverage；
2. reference-on-model coverage；
3. harmonic coverage；
4. median model→reference distance；
5. median reference→model distance；
6. class presence / disappearance。

Also compare each degraded model mask to its own source baseline model mask using class-specific Dice / IoU as an implementation-stability secondary metric。

Manual-reference agreement is primary；baseline-model Dice is secondary because model self-consistency cannot establish observation correctness。

## Predeclared directional questions

### Q1. Does stronger line-detail destruction reduce correct-class manual-reference agreement?

Within each degradation family, report per-level and per-source behavior。The expected research direction is lower harmonic coverage and/or increased distance as degradation becomes stronger。

Failure to show monotonicity must be preserved；do not reorder levels or remove sources。

### Q2. Which class is most quality-sensitive?

Report heart / head / life separately。Do not use pooled foreground alone to hide class-specific disappearance。

Existing repeatability evidence makes `heart_line` a plausible higher-sensitivity class, but this is only a directional expectation and must not be promoted to a rule before execution。

### Q3. Do simple image-quality descriptors track observation degradation consistently?

For Laplacian variance, Tenengrad and RMS contrast，report descriptive association with correct-class harmonic coverage and class disappearance。

No descriptor cutoff may be chosen from this first study。

### Q4. Does model output remain present after reference agreement has materially degraded?

This is especially important for an admission gate：

```text
model class still present
+ low manual-reference agreement
```

would demonstrate why model presence cannot be used as its own quality certificate。

## Aggregate reporting

For each class × degradation family × level report：

- n；
- class presence count；
- harmonic coverage mean / median / p10 / min；
- median-distance summaries；
- baseline-mask Dice mean / median / min；
- descriptor summaries；
- number of appearance transitions from baseline。

Also report per-source tables so P002–P010 heterogeneity remains visible。

No single aggregate score becomes `line_detail` truth。

## P001 sentinel handling

P001 may be run through the same degradation pipeline only to answer a descriptive question：

> does the already low-confidence natural source behave as an extreme or unstable case under further degradation？

Because its frozen manual reference is reference-quality-confounded：

- do not include P001 in primary manual-reference means / percentiles；
- do not use P001 to calibrate any descriptor；
- do not edit its annotation；
- preserve it as a qualitative sentinel only。

## Stop rules

Stop interpretation if any of the following occurs：

- frozen annotation SHA drifts；
- source/model/runtime/adapter provenance drifts；
- geometry of a degradation is not pixel-aligned with baseline；
- input hash accounting is incomplete；
- model output is non-finite；
- class mapping changes；
- any source is removed after outcome inspection；
- any threshold / morphology / preprocessing rescue is introduced post hoc。

## Decision boundary

A favorable result may support：

- line-detail quality materially affects principal-line observation reliability；
- one or more image descriptors are promising candidates for future quality-gate research；
- model class presence alone is insufficient as admission evidence。

It still does **not** establish：

- a production blur threshold；
- a universal quality score；
- smartphone-device generalization；
- Palmistry interpretation validity；
- anatomical ground truth；
- a production routing rule。

A mixed or non-monotonic result must be preserved and should redirect the next node toward richer localized quality descriptors rather than threshold tuning。

## Follow-on node

After this study, the next contract-level node should combine observation evidence without collapsing it into one score：

```text
target-selection state
+ image-quality state
+ landmark-frame uncertainty
+ line-mask uncertainty
→ Palm Observation Fact uncertainty provenance
```

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**。
