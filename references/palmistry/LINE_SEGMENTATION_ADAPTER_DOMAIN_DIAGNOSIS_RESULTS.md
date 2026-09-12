# Palm Line Segmentation Adapter / Domain Diagnosis Results

Status: **REFERENCE-ONLY / BOUNDED RESULT / RAW ARTIFACT HASH PENDING**

本文件收斂 `LINE_SEGMENTATION_ADAPTER_DOMAIN_DIAGNOSIS_PLAN.md` 第一輪正式 MOHI adapter/domain diagnosis。

本研究只回答：在同一批 10 張 MOHI source、同一個 pinned FP32 ONNX model、同一組 frozen MediaPipe landmarks 下，**crop geometry** 與 **horizontal mirror** 兩個 adapter factors 對 shipped tool-local classes (`heart_line`, `head_line`, `life_line`) 的 predicted observability 有何影響。

本研究沒有 anatomical line ground truth，因此 presence 增加不等於 accuracy 增加。

## Execution

```text
10 source images × 4 adapters = 40 ONNX inference executions
```

Final accounting：

```json
{
  "selected_sources": 10,
  "adapters_per_source": 4,
  "completed_inferences": 40,
  "stop": false
}
```

Raw local artifact：

```text
/home/user/palm-detector-study/results/MOHI_line_segmentation_adapter_diagnosis.json
```

Full SHA256 尚待補記。

## Adapter definitions

```text
A_G0_M0 = first-study geometry / no mirror
B_G0_M1 = first-study geometry / horizontal mirror
C_G1_M0 = reconstructed-upstream-like geometry / no mirror
D_G1_M1 = reconstructed-upstream-like geometry / horizontal mirror
```

`G1` 只是 pinned upstream reconstruction 所啟發的 geometry hypothesis，不是 historical-training truth。

## First-order summary

| Adapter | heart | head | life | any foreground | all three | FG fraction mean | FG components mean |
|---|---:|---:|---:|---:|---:|---:|---:|
| A_G0_M0 | 0/10 | 2/10 | 5/10 | 5/10 | 0/10 | 0.001591 | 1.2 |
| B_G0_M1 | 0/10 | 2/10 | 3/10 | 5/10 | 0/10 | 0.000878 | 0.8 |
| C_G1_M0 | 10/10 | 10/10 | 10/10 | 10/10 | 10/10 | 0.014706 | 3.0 |
| D_G1_M1 | 10/10 | 10/10 | 10/10 | 10/10 | 10/10 | 0.016468 | 2.5 |

The dominant factor is visibly geometry, not mirror.

## Frozen question 1 — mirror effect under G0

> Does horizontal mirror alone materially increase class observability relative to Adapter A?

Answer：**No.**

```text
A_G0_M0 -> B_G0_M1
heart: 0 -> 0
head : 2 -> 2
life : 5 -> 3
any foreground: 5 -> 5
all three: 0 -> 0
```

Mirror changes which individual images/classes activate, but there is no overall observability gain under the first-study geometry. `life_line` presence actually decreases by 2 images.

Therefore first-study low observability cannot be explained primarily by missing horizontal mirroring.

## Frozen question 2 — geometry effect

> Does reconstructed-upstream-like crop geometry materially increase class observability relative to Adapter A?

Answer：**Yes, very strongly in this bounded sample.**

At M0：

```text
A_G0_M0 -> C_G1_M0
heart: 0 -> 10   (+10)
head : 2 -> 10   (+8)
life : 5 -> 10   (+5)
any foreground: 5 -> 10
all three: 0 -> 10
```

At M1：

```text
B_G0_M1 -> D_G1_M1
heart: 0 -> 10   (+10)
head : 2 -> 10   (+8)
life : 3 -> 10   (+7)
any foreground: 5 -> 10
all three: 0 -> 10
```

This is a large adapter-sensitivity signal. It strongly suggests that the first-study sparse outputs were at least partly caused by a geometry/domain compatibility mismatch between the model and the first-study square crop.

It does **not** prove the G1 outputs are anatomically correct.

## Frozen question 3 — which classes gain

> Is improvement concentrated only in already-observable life_line, or does it restore heart/head observability too?

Answer：**The largest qualitative gains are precisely in the previously weak/missing classes.**

Under G1, both mirror states show：

```text
heart_line = 10/10
head_line  = 10/10
life_line  = 10/10
```

Thus the geometry effect is not merely amplifying `life_line`; it changes the full class-observation regime from sparse/partial to all-three-classes on every source image.

That pattern is highly informative for adapter compatibility, but also means future validation must guard against a strong model prior that could paint all three classes regardless of true image content.

## Frozen question 4 — geometry × mirror interaction

> Is D materially stronger than either B or C, indicating an interaction?

Answer：**No presence-level interaction is evident.**

```text
C_G1_M0: 10/10 for heart/head/life/all-three
D_G1_M1: 10/10 for heart/head/life/all-three
```

Once G1 geometry is used, mirroring adds no additional class-presence gain.

There are secondary output differences：

```text
FG fraction mean:
C = 0.014706
D = 0.016468

FG component mean:
C = 3.0
D = 2.5
```

These differences may matter for topology/shape, but they do not support mirror as the main observability mechanism.

## Frozen question 5 — P001 / P009

> Do previously fully-unobservable P001/P009 gain foreground support under alternative adapters?

Answer：**Yes under G1 geometry, for all three classes.**

P001：

```text
A: no foreground
B: head only, very small
C: heart + head + life
D: heart + head + life
```

P009：

```text
A: no foreground
B: no foreground
C: heart + head + life
D: heart + head + life
```

This demonstrates that their first-study non-observability was not invariant to adapter geometry.

However, this diagnosis contains only one inference per adapter/source. It does **not** establish that G1 predictions on P001/P009 are perturbation-stable.

## Frozen question 6 — pathological occupancy / fragmentation

> Do adapters that increase presence also create implausibly huge occupancy or severe fragmentation?

Answer：**No obvious fragmentation explosion is present, but correctness remains unverified.**

G1 foreground occupancy：

```text
C mean = 1.4706% of crop pixels
D mean = 1.6468% of crop pixels
```

This is much larger than sparse G0 output, but still small in absolute image-area terms rather than a gross foreground flood.

Topology is also comparatively simple：

```text
C foreground components: mean=3.0, median=3, max=3
D foreground components: mean=2.5, median=2, max=4
```

Most per-class G1 predictions are one connected component with largest-component fraction 1.0. One noted D case (P006 `head_line`) contains 2 components with largest-component fraction about 0.70.

Thus the G1 gain is not accompanied by an obvious many-fragment activation explosion.

Still, the extremely regular pattern — all three classes on all 10 sources, usually one connected component each — is compatible with either：

1. substantially better model/input compatibility；or
2. a strong learned structural prior that activates three canonical lines whenever the crop geometry looks training-like。

Without ground-truth masks or a perturbation test under G1, these two explanations cannot yet be separated.

## Overall bounded diagnosis

The strongest supported conclusion is：

> The first-study line-segmentation observability failure is strongly adapter-geometry-sensitive. Horizontal mirroring is not the primary factor. A reconstructed-upstream-like crop geometry changes model behavior from sparse/partial predictions to three-class predictions on every bounded MOHI source image.

This materially changes the interpretation of the first repeatability study：the poor heart/head observability there should not be treated as evidence that the shipped model intrinsically cannot observe those classes on MOHI. The first-study adapter itself was a major compatibility variable.

At the same time, this result does **not** promote G1 to a valid observation backend. The 10/10 all-three activation pattern requires a second gate to determine whether the predictions are perturbation-stable and non-pathological.

## Next evidence node

The highest-value next experiment is a **predeclared G1 repeatability qualification**, keeping all model/runtime/class contracts fixed.

Recommended primary condition：

```text
C_G1_M0
```

Reason：

- G1 is the dominant factor；
- C achieves the same 10/10 class presence as D；
- C avoids introducing mirror semantics that showed no presence benefit；
- C therefore isolates geometry with fewer transformations/assumptions。

Repeat exactly the previously frozen perturbation family on the immutable C crop：

```text
baseline
rotate +5°
rotate -5°
scale 0.90×
scale 1.10×
center crop 3%
```

Primary questions should be：

1. do all-three classes remain observable under small perturbations；
2. per-class Dice / IoU under C geometry；
3. appearance/disappearance transitions；
4. component fragmentation；
5. whether P001/P009 remain observable under perturbation；
6. whether the strong 10/10 baseline activation is robust or brittle。

Do not compare C-vs-A Dice directly unless masks are first mapped to a common raw-image frame. Presence and within-adapter perturbation metrics are sufficient for the next gate.

## Evidence boundary

Do not infer from this node：

- anatomical correctness；
- Palmistry correctness；
- equivalence to Chinese palm-line terminology；
- production admission thresholds；
- that G1 is the historical training crop；
- that three predicted classes must truly exist in every MOHI palm。

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
