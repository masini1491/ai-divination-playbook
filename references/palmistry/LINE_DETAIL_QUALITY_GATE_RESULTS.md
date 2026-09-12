# Principal-line Line-detail Quality Gate — Results

Status: **REFERENCE-ONLY / BOUNDED QUALITY-SENSITIVITY RESULTS COMPLETE / NO PRODUCTION THRESHOLD**

## Purpose

本文件解讀 `LINE_DETAIL_QUALITY_GATE_PLAN.md` 已預先凍結的 9-source × 10-condition primary study。

正式 raw artifact 已先由 `LINE_DETAIL_QUALITY_GATE_RESULT_FREEZE.md` 固定，在 substantive summary inspection 前完成 SHA256 freeze。

Frozen formal artifact：

```text
/home/user/palm-detector-study/results/MOHI_line_detail_quality_gate.json
SHA256 = 2ec6542d353a1ab8336476868be2cecf7e71f2e27cdb01e36f154b2ab065a4b7
```

Execution accounting：

```text
P002/S1/01.jpg through P010/S1/01.jpg
9 primary sources
× 10 conditions
= 90 primary inference conditions
stop = false
P001 sentinel = not executed
```

P001 remains outside primary quantitative analysis because its frozen manual reference is observer-reported blur-confounded.

## Baseline reference regime

Primary baseline manual-reference agreement：

| Class | Presence | Harmonic mean | Harmonic median | Harmonic p10 | Harmonic min |
|---|---:|---:|---:|---:|---:|
| heart_line | 9/9 | 0.9620 | 0.9763 | 0.9123 | 0.8340 |
| head_line | 9/9 | 0.9429 | 0.9579 | 0.9009 | 0.7342 |
| life_line | 9/9 | 0.8224 | 0.8317 | 0.7495 | 0.7488 |

All baseline wrong-class-win counts remain zero.

This baseline is not a production accuracy claim. It is the frozen within-study reference regime against which detail degradation is compared.

## Image-quality descriptor manipulation check

Primary means：

| Condition | Laplacian variance | Tenengrad | Sobel mean magnitude | RMS contrast |
|---|---:|---:|---:|---:|
| baseline | 287.69 | 413.07 | 12.203 | 0.12643 |
| blur sigma 1.5 | 14.84 | 205.02 | 8.367 | 0.12570 |
| blur sigma 3.0 | 7.84 | 130.01 | 7.107 | 0.12469 |
| blur sigma 6.0 | 6.63 | 78.48 | 6.014 | 0.12230 |
| down/up 256 | 32.86 | 260.32 | 9.530 | 0.12601 |
| down/up 128 | 13.64 | 177.10 | 8.030 | 0.12546 |
| down/up 64 | 8.63 | 112.13 | 6.835 | 0.12399 |
| contrast 0.75 | 168.44 | 234.75 | 9.270 | 0.09477 |
| contrast 0.50 | 77.85 | 105.14 | 6.264 | 0.06317 |
| contrast 0.25 | 24.47 | 27.98 | 3.313 | 0.03160 |

Manipulations moved the intended descriptors directionally, but cross-family values do not map one-to-one onto observation quality. Therefore no single descriptor threshold is justified.

## Gaussian-blur family

### sigma = 1.5 px

Agreement remains close to baseline：

```text
heart Hmean 0.9702  delta +0.0082
head  Hmean 0.9325  delta -0.0103
life  Hmean 0.8273  delta +0.0049

presence 9/9 for all classes
appearance transitions = 0
wrong-class wins = 0
```

The small positive heart/life changes are bounded fluctuations and must not be generalized as evidence that blur improves the model.

### sigma = 3.0 px

A material degradation regime appears：

```text
heart Hmean 0.7528  delta -0.2092  presence 8/9
head  Hmean 0.7446  delta -0.1983  presence 8/9
life  Hmean 0.7126  delta -0.1099  presence 8/9
```

Each class has one appearance transition. Harmonic minima reach zero while medians remain relatively high, showing strong per-source heterogeneity rather than uniform graceful decay.

### sigma = 6.0 px

All shipped principal-line classes collapse in all nine primary sources：

```text
heart presence 0/9
head  presence 0/9
life  presence 0/9

Hmean = 0 for all classes
appearance transitions = 9 per class
```

This is a clear bounded fail regime under severe blur.

## Resolution-destruction family

### 256 → 512

Performance remains near baseline：

```text
heart Hmean 0.9703  delta +0.0083
head  Hmean 0.9386  delta -0.0043
life  Hmean 0.8303  delta +0.0079

presence 9/9 all classes
wrong-class wins 0
```

Again, tiny positive deltas are not interpreted as a general benefit.

### 128 → 512

A class-dependent intermediate regime appears：

```text
heart Hmean 0.9507  delta -0.0113  presence 9/9
head  Hmean 0.8024  delta -0.1404  presence 8/9
life  Hmean 0.7394  delta -0.0831  presence 8/9
```

Heart remains comparatively stable while head/life each incur one appearance transition.

### 64 → 512

Strong degradation occurs：

```text
heart Hmean 0.2987  delta -0.6633  presence 5/9
head  Hmean 0.4224  delta -0.5205  presence 5/9
life  Hmean 0.3502  delta -0.4723  presence 5/9
```

Each class has four appearance transitions. `life_line` also records one wrong-class-exceeds-correct case, the only wrong-class win in this study summary.

This is a bounded low-detail failure regime, not a production cutoff.

## Contrast-compression family

### factor = 0.75

Essentially baseline-like：

```text
heart Hmean 0.9604  delta -0.0016
head  Hmean 0.9422  delta -0.0007
life  Hmean 0.8238  delta +0.0013

presence 9/9 all classes
wrong-class wins 0
```

### factor = 0.50

Still broadly retained：

```text
heart Hmean 0.9239  delta -0.0381
head  Hmean 0.9324  delta -0.0104
life  Hmean 0.8214  delta -0.0010

presence 9/9 all classes
appearance transitions 0
wrong-class wins 0
```

### factor = 0.25

This condition provides the strongest evidence that model presence cannot self-certify observation quality：

```text
heart presence 9/9, Hmean 0.8081, delta -0.1539
head  presence 9/9, Hmean 0.7927, delta -0.1501
life  presence 9/9, Hmean 0.8006, delta -0.0219
```

Heart/head average centerline-distance summaries also deteriorate strongly：

```text
heart median-model→reference mean = 16.448 px
heart median-reference→model mean = 15.551 px

head median-model→reference mean = 22.407 px
head median-reference→model mean = 18.415 px
```

Despite this, class presence remains 9/9 and no appearance transition is triggered.

Therefore：

> `model class present` is not sufficient evidence that line-detail quality is adequate.

This directly supports the fail-closed uncertainty contract in `OBSERVATION_UNCERTAINTY_COMPOSITION_DRAFT.md`.

## Class-specific sensitivity

The predeclared expectation that `heart_line` might be the uniquely most quality-sensitive class is **not uniformly supported**.

Observed regimes differ by degradation family：

- blur sigma 3.0: heart and head show larger relative loss than life;
- resolution 128: head degrades most, heart remains comparatively stable;
- resolution 64: heart has the largest Hmean drop;
- contrast 0.25: heart/head degrade substantially while life remains comparatively stable;
- severe blur sigma 6.0: all classes collapse equally by presence.

Therefore no single universal class-sensitivity ranking should be promoted.

A separate fact remains: `life_line` has the lowest baseline harmonic mean in this particular manual-reference audit, but lower baseline agreement is not equivalent to being the most degradation-sensitive class.

## Descriptor-family interpretation

### Laplacian variance

Useful as a blur/detail descriptor family because it falls sharply with Gaussian blur and resolution destruction.

However it cannot be used alone as a cross-family admission score. Similar or even lower values can occur under different degradation types with materially different line agreement.

### Tenengrad / Sobel gradient descriptors

Also useful as detail/focus evidence families. They decline directionally under blur and resolution loss and respond to contrast compression.

They remain heterogeneous across degradation families, so no single universal threshold is supported.

### RMS contrast

RMS contrast is especially informative for photometric contrast loss and remains comparatively stable under blur/resolution manipulations.

This supports keeping it as a **complementary photometric descriptor**, not treating it as a generic line-detail score.

### Resulting quality-feature architecture

The supported bounded architecture is multi-feature rather than scalar：

```text
focus / high-frequency detail evidence
  = Laplacian + gradient descriptors

photometric contrast evidence
  = RMS contrast / related contrast descriptors

model output evidence
  = presence + mask geometry + manual/reference or robustness provenance
```

These evidence types should remain separate until a later held-out calibration study exists.

## Predeclared directional questions

### Q1 — Does stronger line-detail destruction reduce correct-class agreement?

**Supported directionally, but not perfectly monotonic at mild levels.**

Mild blur / 256-downsample can show tiny neutral or positive fluctuations. Material degradation appears at blur sigma 3.0, resolution 128 for some classes, resolution 64 for all classes, and contrast 0.25 especially for heart/head.

### Q2 — Which class is most quality-sensitive?

**No universal winner.** Sensitivity is degradation-family dependent.

### Q3 — Do simple image-quality descriptors track observation degradation consistently?

**They track their manipulation family directionally, but not as a single universal scalar quality variable.**

Laplacian/Tenengrad/Sobel remain useful candidate feature families for detail/focus; RMS contrast remains useful for contrast loss.

### Q4 — Can model output remain present after reference agreement degrades?

**Yes.** Contrast factor 0.25 is the clearest bounded example: 9/9 presence for all three classes while heart/head manual-reference agreement and distance metrics materially worsen.

## Bounded evidence decision

This node supports the following research decision：

> Palm Observation requires an image-quality / observability gate that is independent of model class presence. A future `line_detail` admission system should preserve separate detail/focus and contrast evidence rather than compressing them into one unvalidated score.

It does **not** support choosing a production cutoff such as：

```text
Laplacian variance < X => reject
Tenengrad < Y => reject
RMS contrast < Z => reject
```

The current 9-source study is too small and intentionally synthetic in degradation family to calibrate such thresholds.

## What this node closes

Boundedly closed：

- whether controlled detail destruction can materially degrade principal-line observation;
- whether model presence can be trusted as its own quality certificate;
- whether task-specific `line_detail` quality evidence is necessary;
- whether multiple descriptor families are preferable to a single generic score.

Still open：

- held-out quality-threshold calibration;
- natural low-quality photo validation beyond P001 descriptive evidence;
- glare / uneven illumination / JPEG / crop / occlusion families;
- device-to-device capture quality portability;
- production `sufficient / partial / insufficient` numeric boundaries.

## Boundary

Do not infer from this study：

- anatomical ground truth;
- a production image-quality threshold;
- a universal class ranking;
- that mild synthetic blur or resizing improves real-world performance;
- that synthetic degradation distributions represent arbitrary phone photos;
- Palmistry interpretation validity.

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
