# Palm Line Segmentation G1 Repeatability — Upstream-Affine-Fixed Results

Status: **REFERENCE-ONLY / CORRECTED BOUNDED QUALIFICATION COMPLETE / RAW ARTIFACT HASH PINNED**

This document records the corrected upstream-affine-fixed `C_G1_M0` repeatability qualification defined by `LINE_SEGMENTATION_G1_REPEATABILITY_UPSTREAM_AFFINE_FIXED_PLAN.md`.

It supersedes `LINE_SEGMENTATION_G1_REPEATABILITY_RESULTS.md` for exact-upstream-affine G1 qualification. The older result remains historical evidence for the superseded pre-correction G1 crop implementation.

## Raw evidence

Corrected raw artifact:

```text
/home/user/palm-detector-study/results/MOHI_line_segmentation_g1_repeatability_upstream_affine_fixed.json
```

SHA256:

```text
a1f0293f3662846255f335fe79d060b054852367f60c74fa4d558e6fe825d238
```

Pinned corrected adapter-diagnosis artifact:

```text
c51651cdc267b0416c0883ffba13e1ed0b5992aa808944e1786e2bc20d0e38d3
```

Execution:

```text
10 frozen source images
× (1 baseline + 5 frozen perturbations)
= 60 ONNX inference executions
stop = false
```

## Baseline observability

Corrected `C_G1_M0` baseline remains:

```text
heart_line_presence = 10/10
head_line_presence  = 10/10
life_line_presence  = 10/10
all_three_presence  = 10/10
any_foreground      = 10/10
```

This reproduces the corrected adapter-diagnosis presence regime.

## Presence retention under perturbation

| Variant | heart | head | life | all three | any foreground |
|---|---:|---:|---:|---:|---:|
| rotate +5° | 8/10 | 10/10 | 10/10 | 8/10 | 10/10 |
| rotate -5° | 10/10 | 10/10 | 10/10 | 10/10 | 10/10 |
| scale 0.90× | 10/10 | 10/10 | 10/10 | 10/10 | 10/10 |
| scale 1.10× | 9/10 | 10/10 | 9/10 | 9/10 | 10/10 |
| center crop 3% | 10/10 | 10/10 | 10/10 | 10/10 | 10/10 |

Across the 50 perturbed image conditions:

```text
all-three-class retention = 47 / 50
any-foreground retention  = 50 / 50
```

Across baseline + perturbations:

```text
all-three-class presence = 57 / 60 conditions
any-foreground presence  = 60 / 60 conditions
```

Therefore corrected G1 remains highly observable under the frozen perturbation family, but not perfectly stable.

## Class-level repeatability

Across 50 baseline-vs-variant comparisons per class:

### heart_line

```text
Dice mean   = 0.825225
Dice median = 0.918045
Dice p10    = 0.366291
Dice p90    = 0.944084
Dice min    = 0.000000
Dice max    = 0.951582
IoU mean    = 0.754512

comparable            = 47
appearance_transition = 3
```

Heart remains the least reliable class by transition count and lower-tail behavior.

### head_line

```text
Dice mean   = 0.898246
Dice median = 0.922333
Dice p10    = 0.869036
Dice p90    = 0.943182
Dice min    = 0.426045
Dice max    = 0.950616
IoU mean    = 0.823607

comparable            = 50
appearance_transition = 0
```

`head_line` remains the strongest and most consistently retained class in this bounded qualification.

### life_line

```text
Dice mean   = 0.853957
Dice median = 0.905521
Dice p10    = 0.826074
Dice p90    = 0.929055
Dice min    = 0.000000
Dice max    = 0.946168
IoU mean    = 0.770471

comparable            = 49
appearance_transition = 1
```

Life remains generally repeatable with one disappearance event.

## Aggregate transition accounting

Across all classes and perturbations:

```text
150 class-level baseline-vs-variant comparisons
146 comparable
4 appearance transitions
0 empty-both cases
```

Observed transitions:

```text
P001 rotate +5°   heart_line disappears
P001 scale 1.10×  heart_line disappears
P001 scale 1.10×  life_line disappears
P002 rotate +5°   heart_line disappears
```

No `head_line` disappearance occurs anywhere in the bounded sample.

## Transform-level behavior

Foreground-union repeatability:

| Variant | Mean Dice | Median Dice | Min | Max |
|---|---:|---:|---:|---:|
| rotate +5° | 0.867418 | 0.902848 | 0.662075 | 0.937724 |
| rotate -5° | 0.901518 | 0.917958 | 0.734445 | 0.944327 |
| scale 0.90× | 0.888870 | 0.910317 | 0.732713 | 0.923968 |
| scale 1.10× | 0.842457 | 0.899002 | 0.321154 | 0.925782 |
| center crop 3% | 0.900058 | 0.919516 | 0.706031 | 0.940470 |

`scale 1.10×` remains the weakest perturbation by mean foreground-union Dice. The strongest top-level transform ordering changes slightly relative to the superseded legacy run (`rotate -5°` narrowly exceeds center crop 3% here), so no general transform law should be inferred.

## Per-person heterogeneity

Mean class-specific Dice:

```text
P001 = 0.467411
P002 = 0.808678
P003 = 0.921537
P004 = 0.913521
P005 = 0.919936
P006 = 0.903261
P007 = 0.926516
P008 = 0.918193
P009 = 0.919372
P010 = 0.893003
```

P001 remains the clear outlier and contains three of four appearance transitions. P002 is the second-lowest and contributes the additional rotate +5° heart disappearance. P003–P010 otherwise cluster near approximately 0.89–0.93 mean class-specific Dice.

This preserves the requirement for per-observation robustness evidence rather than relying only on pooled averages.

## P001 / P009

P001 remains only partially qualified:

```text
class-specific mean Dice = 0.467411
foreground-union mean     = 0.640383
```

It loses heart under rotate +5° and loses heart + life under scale 1.10×.

P009 remains strongly repeatable under corrected G1:

```text
class-specific mean Dice = 0.919372
foreground-union mean     = 0.920049
all five perturbations retain all three classes
```

Thus corrected G1 continues to support the adapter-compatibility explanation for P009's earlier G0 non-observability.

## Legacy versus corrected repeatability

Legacy superseded result versus corrected result:

```text
heart Dice mean   0.817579 -> 0.825225
heart Dice median 0.913714 -> 0.918045

head Dice mean    0.893445 -> 0.898246
head Dice median  0.916176 -> 0.922333

life Dice mean    0.854348 -> 0.853957
life Dice median  0.899761 -> 0.905521
```

Presence regime is also largely preserved:

```text
baseline all-three: 10/10 -> 10/10
rotate -5° all-three: 10/10 -> 10/10
scale 0.90× all-three: 10/10 -> 10/10
scale 1.10× all-three: 9/10 -> 9/10
center crop 3% all-three: 10/10 -> 10/10
rotate +5° all-three: 9/10 -> 8/10
```

The fidelity correction therefore changes exact evidence values and adds one extra bounded transition, but it does not change the overall implementation-level repeatability regime.

## Frozen directional questions

1. **Baseline reproduction:** yes, corrected C remains 10/10 all-three.
2. **Presence retention:** high but not perfect; 47/50 perturbed conditions retain all three classes.
3. **Least repeatable class:** heart, based on 3 transitions and the deepest lower tail.
4. **Transform sensitivity:** scale 1.10× is weakest by foreground mean Dice; rotate +5° causes the most heart disappearance. There is no basis for a universal rotation-vs-scale rule.
5. **Foreground union vs class-specific:** union overlap is not dramatically higher in a way that would make class relabeling the dominant explanation; residual instability includes genuine within-class geometry/presence sensitivity, especially P001/P002.
6. **P001/P009:** P009 robustly qualifies; P001 remains a clear bounded failure/outlier.
7. **Fragmentation:** no evidence here of a global fragmentation explosion; baseline foreground components are mostly 3, with P001/P010 at 4.
8. **G0 comparison:** corrected G1 still materially reduces the severe observability/appearance-disappearance problem seen under the first-study G0 geometry while keeping sparse foreground occupancy rather than a foreground flood.

## Bounded qualification decision

No predeclared numeric production threshold exists, so this node should not be described as a production pass/fail test.

The supported evidence decision is:

> **Corrected `C_G1_M0` clears the bounded implementation-repeatability evidence gate strongly enough to continue research, while retaining explicit per-observation exceptions.**

It does not support treating every corrected G1 mask as valid. In particular, P001 and the rotate +5° P002 heart failure show that observation-level robustness gating remains necessary.

Most importantly, repeatability cannot distinguish a content-sensitive segmenter from a stable canonical three-line prior. That becomes the next evidence problem.

## Next evidence node

Proceed to a separately predeclared **content-dependence / specificity control**. Hold corrected `C_G1_M0`, model, runtime, sample, resize/normalization and class mapping fixed. Alter only image-content evidence in predefined ways, without threshold/morphology rescue or post-outcome tuning.

The goal is to test whether predicted line geometry materially depends on palm image content, versus persisting as a largely canonical three-line structural prior whenever the input retains a training-like palm crop.

## Evidence boundary

Do not infer from this node:

- anatomical correctness;
- ground-truth segmentation accuracy;
- Palmistry interpretation validity;
- historical training truth;
- production admission thresholds;
- that every palm truly contains the predicted three classes;
- that P001/P002 instability has a known biological cause.

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
