# Palm Line Segmentation G1 Repeatability Results

Status: **REFERENCE-ONLY / BOUNDED RESULT / RAW ARTIFACT HASH PENDING**

本文件收斂 `LINE_SEGMENTATION_G1_REPEATABILITY_PLAN.md` 第一輪正式 MOHI `C_G1_M0` repeatability qualification。

本研究只回答：在同一批 10 張 MOHI source、同一個 pinned FP32 ONNX model、同一組 frozen MediaPipe landmarks 與固定 `C_G1_M0` adapter 下，五種小幅幾何 perturbations 是否會破壞 shipped tool-local classes (`heart_line`, `head_line`, `life_line`) 的 observability 與 mask geometry。

本研究沒有 anatomical line ground truth，因此高 repeatability 不等於高 segmentation accuracy。

## Execution

```text
10 source images
× (1 baseline + 5 frozen perturbations)
= 60 ONNX inference executions
```

Final accounting：

```json
{
  "selected_sources": 10,
  "conditions_per_source": 6,
  "completed_inferences": 60,
  "stop": false
}
```

Raw local artifact：

```text
/home/user/palm-detector-study/results/MOHI_line_segmentation_g1_repeatability.json
```

Full SHA256 尚待補記。

## Frozen adapter

```text
adapter = C_G1_M0
geometry = G1_reconstructed_upstream_like
horizontal_mirror = false
```

`G1` 仍只是 pinned upstream reconstruction 所啟發的 geometry hypothesis，不是 historical-training truth。

## Baseline observability

All 10 baseline images predict all three tool-local classes：

```text
heart_line_presence = 10/10
head_line_presence  = 10/10
life_line_presence  = 10/10
all_three_presence  = 10/10
any_foreground      = 10/10
```

This reproduces the preceding adapter/domain diagnosis baseline behavior under C_G1_M0.

## Presence retention under perturbation

| Variant | heart | head | life | all three | any foreground |
|---|---:|---:|---:|---:|---:|
| rotate +5° | 9/10 | 10/10 | 10/10 | 9/10 | 10/10 |
| rotate -5° | 10/10 | 10/10 | 10/10 | 10/10 | 10/10 |
| scale 0.90× | 10/10 | 10/10 | 10/10 | 10/10 | 10/10 |
| scale 1.10× | 9/10 | 10/10 | 9/10 | 9/10 | 10/10 |
| center crop 3% | 10/10 | 10/10 | 10/10 | 10/10 | 10/10 |

Across the 50 perturbed image conditions：

```text
all-three-class retention = 48 / 50
any-foreground retention  = 50 / 50
```

Across baseline + perturbations：

```text
all-three-class presence = 58 / 60 conditions
any-foreground presence  = 60 / 60 conditions
```

Thus the 10/10 G1 baseline activation is not generally brittle to the frozen small perturbations.

## Class-level repeatability

Across 50 baseline-vs-variant comparisons per class：

### heart_line

```text
Dice n=50
mean   = 0.817579
median = 0.913714
p10    = 0.334654
p90    = 0.942749
min    = 0.000000
max    = 0.951172

IoU mean = 0.747656
```

Status accounting：

```text
comparable            = 48
appearance_transition = 2
```

Heart-line geometry is usually highly repeatable, but the distribution has a pronounced low tail driven primarily by P001.

### head_line

```text
Dice n=50
mean   = 0.893445
median = 0.916176
p10    = 0.856713
p90    = 0.942286
min    = 0.297926
max    = 0.946651

IoU mean = 0.818665
```

Status accounting：

```text
comparable            = 50
appearance_transition = 0
```

`head_line` is the strongest and most consistently retained of the three shipped classes under this bounded G1 qualification.

### life_line

```text
Dice n=50
mean   = 0.854348
median = 0.899761
p10    = 0.834299
p90    = 0.929805
min    = 0.000000
max    = 0.941419

IoU mean = 0.770893
```

Status accounting：

```text
comparable            = 49
appearance_transition = 1
```

Life-line repeatability is also strong in most cases, with one disappearance event under scale 1.10× on P001.

## Aggregate transition accounting

Across all three classes and all 50 perturbation conditions：

```text
150 class-level baseline-vs-variant comparisons
147 comparable
3 appearance transitions
0 empty-both cases
```

The three transitions are all on P001：

```text
rotate +5°   heart_line disappears
scale 1.10×  heart_line disappears
scale 1.10×  life_line disappears
```

No `head_line` disappearance occurred anywhere in the bounded sample.

## Transform-level results

Foreground-union repeatability：

| Variant | Mean Dice | Median Dice | Min | Max |
|---|---:|---:|---:|---:|
| rotate +5° | 0.863127 | 0.904841 | 0.654744 | 0.938432 |
| rotate -5° | 0.881583 | 0.924424 | 0.504503 | 0.942689 |
| scale 0.90× | 0.891708 | 0.911383 | 0.768951 | 0.923085 |
| scale 1.10× | 0.835006 | 0.903173 | 0.236454 | 0.926286 |
| center crop 3% | 0.903354 | 0.917202 | 0.753307 | 0.943764 |

Observed ordering in this bounded sample：

```text
center crop 3% strongest by mean foreground Dice
scale 1.10× weakest by mean foreground Dice
```

This is descriptive only; no monotonic transform law is inferred from ten images.

## Frozen question 1 — does all-three observability survive perturbation?

Answer：**Yes, overwhelmingly, but not perfectly.**

```text
48 / 50 perturbed conditions retain all three classes
50 / 50 retain at least some foreground
```

The only all-three failures are：

```text
P001 rotate +5°
P001 scale 1.10×
```

Therefore the preceding 10/10 G1 baseline result is not a one-frame-only activation artifact across most images.

## Frozen question 2 — is mask geometry repeatable, not merely class presence?

Answer：**Yes for most source/transform combinations.**

Class-level mean Dice values are：

```text
heart_line = 0.817579
head_line  = 0.893445
life_line  = 0.854348
```

Medians are all approximately 0.90 or higher. This means the evidence is stronger than simple persistence of class labels; mapped mask geometry itself usually overlaps strongly with baseline.

However, this does not establish anatomical correctness. A stable learned prior could also be repeatable.

## Frozen question 3 — appearance/disappearance vs boundary/topology drift

Answer：**Severe class disappearance is rare under G1; residual uncertainty is mostly geometry/topology drift.**

Only 3/150 class comparisons are appearance transitions. The remaining low-quality cases are generally still comparable masks with displacement or connected-component changes.

Notable component changes include：

```text
P001 center crop 3% heart: 1 -> 3 components
P001 center crop 3% life : 1 -> 2 components
P002 rotate +5° head      : 1 -> 2 components
P002 scale 0.90× heart    : 1 -> 2 components
P004 scale 1.10× life     : 1 -> 2 components
P004 center crop 3% life  : 1 -> 2 components
P006 center crop 3% heart : 1 -> 2 components
```

Thus under G1 the dominant implementation uncertainty moves from class observability failure toward boundary/topology variation.

## Frozen question 4 — person heterogeneity

Per-person mean class-specific Dice：

```text
P001 = 0.435640
P002 = 0.800211
P003 = 0.919835
P004 = 0.912357
P005 = 0.921335
P006 = 0.903924
P007 = 0.917129
P008 = 0.925133
P009 = 0.918139
P010 = 0.897535
```

P001 is the clear outlier and contains all three appearance transitions. P002 is second-lowest but remains materially more stable than P001. P003–P010 except P001/P002 cluster near approximately 0.90 mean class-specific Dice.

This heterogeneity means a future admission layer cannot rely only on pooled averages; per-observation robustness remains necessary.

## Frozen question 5 — P001 / P009 qualification

P009, which was fully unobservable under the first-study G0 adapter, is highly repeatable under G1：

```text
class-specific mean Dice = 0.918139
foreground-union mean     = 0.918804
all five perturbations retain all three classes
```

Thus P009 strongly supports the adapter-compatibility diagnosis rather than an image-intrinsic inability of the model to produce lines.

P001 is different：

```text
class-specific mean Dice = 0.435640
foreground-union mean     = 0.594352
```

It loses heart under rotate +5°, and loses heart + life under scale 1.10×. It is therefore a clear bounded failure/outlier under the current perturbation qualification.

## Comparison with first-study G0 repeatability

The first-study G0 probe had：

```text
heart_line = not estimable / baseline 0/10
head_line mean Dice = 0.236943
life_line mean Dice = 0.542009
```

Under G1：

```text
heart_line mean Dice = 0.817579
head_line mean Dice  = 0.893445
life_line mean Dice  = 0.854348
```

Because each study measures within-adapter baseline-vs-perturbation repeatability in a different crop frame, these values should not be interpreted as direct anatomical accuracy improvement or direct mask agreement across G0 vs G1.

They do support the bounded statement that **within-adapter implementation repeatability is substantially stronger under G1 than under the first-study G0 geometry** on this same ten-image sample and perturbation family.

## Overall bounded qualification

The strongest supported conclusion is：

> `C_G1_M0` converts the shipped FP32 palm-line model from sparse/brittle observability under the first-study geometry into a generally high-observability, high-repeatability implementation regime on this bounded MOHI sample.

Specifically：

- baseline all-three presence = 10/10；
- perturbation all-three retention = 48/50；
- any foreground retention = 50/50；
- only 3/150 class comparisons are appearance transitions；
- class median Dice values are all about 0.90 or higher；
- P003–P010 are generally highly stable；
- P001 remains a significant outlier；
- P002 shows moderate residual sensitivity。

Therefore the hypothesis that G1's 10/10 baseline behavior is merely a globally brittle activation is **not supported** by this qualification.

However, repeatability alone still cannot distinguish：

1. image-content-sensitive segmentation that is genuinely compatible with the crop geometry；from
2. a stable learned canonical three-line prior that persists whenever a training-like palm crop is presented。

That distinction becomes the next evidence problem.

## Admission implication

This node justifies a stronger implementation-level statement than the first G0 study：

> G1-like geometry is a plausible candidate adapter for further qualification because its outputs are usually both observable and perturbation-repeatable.

It still does **not** justify admitting the three predicted line masks as canonical Palm Observation Facts without an additional content-dependence / specificity gate.

A future observation layer should retain per-observation robustness evidence because P001 demonstrates that pooled high repeatability can conceal a meaningful failure case.

## Next evidence node

The next highest-value experiment should test **content dependence versus canonical model prior**, not another margin sweep and not threshold tuning.

A separate predeclared negative/control-content probe should ask whether the shipped model's stable three-class pattern materially responds when line-scale visual evidence is intentionally degraded or spatial structure is disrupted while gross palm-crop geometry is held approximately constant.

Any such probe must be frozen before inspecting outputs and must avoid using its result to tune preprocessing parameters.

## Evidence boundary

Do not infer from this node：

- anatomical correctness；
- segmentation ground-truth accuracy；
- Palmistry interpretation validity；
- equivalence to Chinese palm-line terminology；
- that G1 reproduces the historical training crop；
- production admission thresholds；
- that every palm truly contains three visible canonical lines；
- that P001 failure has a known biological or imaging cause。

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
