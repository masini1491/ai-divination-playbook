# Palm Line Segmentation Repeatability Results

Status: **REFERENCE-ONLY / BOUNDED RESULT / RAW ARTIFACT HASH PENDING**

本文件收斂 `LINE_SEGMENTATION_REPEATABILITY_PLAN.md` 第一輪正式 MOHI execution 的 bounded result。

本研究只回答 shipped FP32 ONNX 在 study-local deterministic palm crop 下，對小幅 image-space perturbation 的 **segmentation repeatability / observability**。它不建立 anatomical line truth、Palmistry interpretation validity、中西 terminology equivalence 或 production threshold。

## Execution boundary

Formal execution completed：

```text
10 predeclared source images
× (1 baseline + 5 perturbations)
= 60 ONNX inference executions
```

Final accounting：

```json
{
  "selected": 10,
  "completed": 10,
  "stop": false
}
```

Runtime/model/crop/transform contracts were frozen before result inspection and are documented separately.

Generated local raw evidence artifact：

```text
/home/user/palm-detector-study/results/MOHI_line_segmentation_repeatability.json
```

其 full SHA256 尚未記錄，因此本結果文件保留 `RAW ARTIFACT HASH PENDING`；後續補 hash 不得改變本次 frozen analysis contract。

## First-order finding: observability precedes repeatability

Baseline class presence across 10 selected sources：

| Tool-local class | Baseline present | Baseline total pixels |
|---|---:|---:|
| `heart_line` | 0 / 10 | 0 |
| `head_line` | 2 / 10 | 10,286 |
| `life_line` | 5 / 10 | 105,031 |

因此三個 shipped classes 並非在這個 MOHI deterministic crop/domain 下都具有足夠 observation support。

這代表第一層問題不是「三類線的 Dice 哪個比較高」，而是：

```text
class not observed at baseline
≠ high repeatability
≠ correct absence
```

尤其 `heart_line` 在 10/10 baseline 都沒有任何 predicted pixels，因此本 probe **無法估計 heart_line repeatability**。

## Class-level repeatability

### heart_line

Across all 50 baseline-vs-variant comparisons：

```text
not_applicable_empty_both = 50
comparable                = 0
appearance_transition     = 0
```

Result：

```text
Dice / IoU = NOT ESTIMABLE IN THIS PROBE
```

不得把 50 次 empty-both 說成 perfect agreement；這只代表 model 在 baseline 與所有 perturbed cases 都沒有輸出這一類。

### head_line

Baseline present only 2/10 images。

Across 50 comparisons：

```text
not_applicable_empty_both = 39
comparable                = 5
appearance_transition     = 6
```

Non-NA Dice summary：

```text
n      = 11
mean   = 0.236943
median = 0.000000
p10    = 0.000000
p90    = 0.718489
min    = 0.000000
max    = 0.765604
```

IoU mean：

```text
0.173074
```

Interpretation：`head_line` 在此 sample 的主要問題不是小幅 boundary drift，而是 **low observability + disappearance / appearance sensitivity**。在少數 retained cases 可以得到中等 overlap，但整體不能描述成穩定 class。

### life_line

Baseline present 5/10 images。

Across 50 comparisons：

```text
not_applicable_empty_both = 19
comparable                = 22
appearance_transition     = 9
```

Non-NA Dice summary：

```text
n      = 31
mean   = 0.542009
median = 0.765832
p10    = 0.000000
p90    = 0.892005
min    = 0.000000
max    = 0.920938
```

IoU mean：

```text
0.459620
```

`life_line` 是三個 shipped classes 中在本 probe 唯一具有相對足夠 retained evidence 的 class。其 conditional retained cases 常可達 Dice 約 0.75–0.92，但 9 次 appearance/disappearance transitions 證明 observability 仍不是穩定常數。

## Frozen research question 1

> Are the three shipped line classes equally stable under small transforms, or is one class systematically less repeatable?

Answer：**No; they are not equally observable or equally repeatable.**

更精確地說：

- `heart_line`：not estimable，因 baseline 0/10；
- `head_line`：observability 最弱，baseline 2/10，non-NA median Dice 0；
- `life_line`：baseline 5/10；conditional retained overlap 明顯較好，但仍有 disappearance / appearance。

因此不能建立簡單的三類 ranking，因為 `heart_line` 根本沒有足夠 observation support。可支持的 bounded ordering只有：

```text
life_line has stronger usable repeatability evidence than head_line
heart_line remains unobservable / not estimable in this probe
```

## Transform-level results

Foreground-union Dice：

| Variant | n | Mean | Median | Min | Max |
|---|---:|---:|---:|---:|---:|
| rotate +5° | 6 | 0.590358 | 0.735577 | 0.000000 | 0.920938 |
| rotate -5° | 7 | 0.445347 | 0.633315 | 0.000000 | 0.901653 |
| scale 0.90× | 7 | 0.454817 | 0.525677 | 0.000000 | 0.892005 |
| scale 1.10× | 6 | 0.486034 | 0.628361 | 0.000000 | 0.848275 |
| center crop 3% | 6 | 0.633882 | 0.717326 | 0.000000 | 0.903911 |

The effective n differs because empty-both comparisons are not assigned artificial perfect scores.

## Frozen research question 2

> Are rotation perturbations materially more disruptive than scale / mild center-crop perturbations?

Answer：**Not as a general rule in this bounded sample.**

Observed pattern is directional and context-dependent：

```text
rotate -5°  foreground mean Dice ≈ 0.445
scale 0.90 foreground mean Dice ≈ 0.455
scale 1.10 foreground mean Dice ≈ 0.486
rotate +5° foreground mean Dice ≈ 0.590
crop 3%    foreground mean Dice ≈ 0.634
```

`rotate -5°` 是較弱 variant 之一，但 `rotate +5°` 明顯沒有同樣程度的 degradation；scale 0.90× 也同樣具有強 disruption。因此不能把「rotation > scale/crop」提升成 monotonic rule。

本結果支持：

```text
transform sensitivity is asymmetric and image/context dependent
```

## Frozen research question 3

> Does transform sensitivity manifest mainly as boundary displacement, line disappearance/appearance, or connected-component fragmentation?

Answer：**Severe failures are dominated by observability transitions; boundary displacement and component changes are secondary retained-case effects.**

Across 50 comparisons：

```text
head_line appearance transitions = 6
life_line appearance transitions = 9
```

Examples：

- P003 `head_line` disappears under rotate -5° and scale 0.90×；
- P008 `head_line` and `life_line` both disappear under rotate -5° / scale 0.90× / scale 1.10×；
- P007 / P010 have baseline-absent `life_line` that appears under multiple transforms；
- P005 has baseline-absent `head_line` that appears only under rotate +5°。

Component topology also changes in retained cases：

- P002 life：baseline 2 components → mostly 1 component；
- P003 life：1 → 2 under rotate -5°；1 → 3 under center crop；
- P008 head：3 → 2 under rotate +5°，3 → 1 under center crop。

Thus：

```text
severe instability: appearance / disappearance
retained-case instability: boundary displacement + component topology changes
```

No morphology cleanup was applied, so these effects are direct shipped-model observations under the frozen adapter.

## Frozen research question 4

> Are there palm images with consistently higher segmentation instability across perturbation types?

Answer：**Yes, but distinguish instability from complete non-observability.**

### Relatively stable retained examples

```text
P002 class mean Dice = 0.823419
P004 class mean Dice = 0.852746
P006 class mean Dice = 0.893228
```

These are dominated by retained `life_line` predictions across all five perturbations.

### Mixed / unstable examples

P003：

```text
class-specific mean Dice = 0.467416
foreground-union mean     = 0.572453
```

It retains life-line geometry reasonably, but head-line presence/classification is unstable.

P008：

```text
class-specific mean Dice = 0.188755
foreground-union mean     = 0.170713
```

P008 is the clearest strongly unstable baseline-positive case；multiple variants collapse both head and life predictions.

### Baseline-negative but transform-sensitive examples

```text
P005: a head_line appears under rotate +5°
P007: life_line appears under rotate -5° / scale 0.90×
P010: life_line appears under rotate -5° / scale 0.90× / scale 1.10× / crop 3%
```

These are not merely low Dice; they are **observability-flip cases**.

### Fully unobservable examples

```text
P001: no class-specific or foreground comparable values
P009: no class-specific or foreground comparable values
```

These should not be described as stable. They are simply outside the model's observed foreground support under every frozen condition in this probe.

## Frozen research question 5

> Is foreground-union repeatability materially higher than class-specific repeatability, suggesting class-boundary uncertainty rather than line-presence uncertainty?

Answer：**No consistent evidence supports that as the dominant mechanism.**

Examples：

- P003 improves from class-specific mean 0.467 to foreground-union mean 0.572, so some class-assignment uncertainty may exist there；
- P008 does not improve (`0.189` class-specific vs `0.171` foreground-union)；
- P002 / P004 / P006 are effectively identical at class-specific and union levels because only one foreground class is retained；
- multiple severe failures are literal foreground appearance/disappearance, which unioning classes cannot rescue。

Therefore this first bounded study does **not** support the claim that instability is mainly class-boundary relabeling while generic line presence remains stable.

The stronger conclusion is：

```text
foreground observability itself is unstable on a meaningful subset of images
```

## Overall bounded interpretation

The shipped `palm-line-reader` FP32 model is executable and can produce repeatable principal-line masks on some MOHI palms, especially retained `life_line` cases. However, under the study-local deterministic crop/domain：

- `heart_line` was never observed；
- `head_line` had very low baseline observability and frequent disappearance；
- `life_line` had the strongest retained repeatability but still showed appearance/disappearance；
- small geometric transforms can cause not only mask displacement but entire class appearance/disappearance；
- transform direction/context matters；
- per-image heterogeneity is large。

Thus the first implementation-level admission implication is qualitative only：

> A principal-line observation layer cannot treat a single segmentation pass or a single class-presence decision as sufficient evidence. Before any future Palm Observation Fact is admitted, the pipeline needs an explicit observability / perturbation-consistency gate, or an alternative model/crop adapter with stronger evidence.

This is **not** a production cutoff and does not promote the model into canonical Palmistry routing.

## What this result does not establish

Do not infer：

- that a missing predicted line means the anatomical line is absent；
- that `heart/head/life` map to Chinese `天/人/地紋`；
- that MOHI is representative of all consumer palm photos；
- that the study-local crop reproduces upstream training preprocessing；
- that Dice thresholds for admission are known；
- that the model is inaccurate against ground truth（no ground-truth segmentation labels were used）；
- that any Palmistry interpretation is validated。

## Next evidence implication

Before considering this segmentation source usable for canonical Palm Observation Facts, the highest-value next node is **adapter/domain diagnosis**, not threshold tuning：

1. determine whether the low observability is primarily caused by study-local crop/orientation mismatch vs upstream training-domain mismatch；
2. compare a small predeclared set of adapter variants without using outcome-driven thresholding；
3. preserve the same FP32 model and class contract；
4. if observability remains weak, treat this source as implementation reference rather than candidate observation backend。

Any next adapter comparison must be predeclared before inspecting its model outputs.

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
