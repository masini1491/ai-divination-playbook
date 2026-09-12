# Palm Line Segmentation — Blind Anatomical Manual Audit Plan

Status: **REFERENCE-ONLY / PREDECLARED / NO MANUAL ANNOTATION INSPECTED**

本節點承接已完成的 corrected adapter、repeatability、content-dependence 與 spatial-structure controls。

目前已建立的 bounded evidence 是：

- corrected `C_G1_M0` 使 10/10 frozen MOHI sources 出現 shipped `heart_line / head_line / life_line` 三類；
- small geometric perturbations 下大致可重複；
- low-pass / flat-color destructive controls 使 foreground 全部消失；
- spatially shuffled high-frequency residual 即使維持或提高 Sobel high-frequency energy，也幾乎無法恢復 foreground；
- residual polarity reversal 仍可保留部分 baseline structure。

最新 pinned spatial-structure raw artifact：

```text
ba65456e3c7c3a645a4000c721961d0f600b46541ffc7e7566525b99a55f87e7
```

因此剩餘主要問題不是「模型是否使用影像內容」，而是：

> **模型輸出的三個 shipped classes 是否真的落在 independent observer 所辨識的對應主要掌紋／掌褶結構上？**

本節點只做 observation-level anatomical/manual audit，不做 palmistry fortune interpretation。

## Authority / source lock

Freeze：

```text
spatial-structure raw artifact SHA256 = ba65456e3c7c3a645a4000c721961d0f600b46541ffc7e7566525b99a55f87e7
prior content-dependence raw SHA256    = 317e85351e4141206b28aec5277433ba3caed9a53e3eb01866cd38900699022f
corrected repeatability raw SHA256     = a1f0293f3662846255f335fe79d060b054852367f60c74fa4d558e6fe825d238
corrected adapter diagnosis SHA256     = c51651cdc267b0416c0883ffba13e1ed0b5992aa808944e1786e2bc20d0e38d3
```

Reuse exactly the same ten frozen MOHI sources and corrected `C_G1_M0` baseline 512×512 input frame。

No image exclusion after seeing model overlays。

## Blinding rule

Manual reference annotation must be created **before model masks or overlays are viewed for this audit**。

The annotation packet therefore has two logically separate parts：

```text
reference_blind/
model_sealed/
```

During reference annotation, annotator may open only `reference_blind/`。

`model_sealed/` contains model masks / overlays for later comparison and must remain unopened until all reference annotations are frozen and hashed。

This is not cryptographic blinding against a determined user；it is a procedural evidence boundary。

## Annotation target

For each 512×512 corrected baseline image, independently annotate up to three target major crease centerlines corresponding to the tool-local labels：

```text
heart_line
head_line
life_line
```

The task is purely visual/anatomical observation：trace the visible major crease structure believed to correspond to each class label。

Do not use model prediction to decide where to draw。

For each class one of these statuses must be recorded：

```text
observable
uncertain
not_observable
```

Rules：

- `observable`: sufficiently visible to trace a centerline;
- `uncertain`: candidate structure exists but class identity or path is ambiguous;
- `not_observable`: no defensible independent trace can be made.

Unknown / not-observable is a valid result and must not be rescued。

## Annotation representation

Reference trace is stored as an ordered polyline in 512×512 pixel coordinates：

```json
{
  "class": "heart_line",
  "status": "observable",
  "points_xy": [[x0,y0], [x1,y1], ...]
}
```

Coordinates must stay within `[0,511]`。

No smoothing, curve fitting, or model-assisted snapping is applied before freeze。

## Frozen comparison geometry

Because model masks have finite thickness while manual references are centerlines, exact pixel Dice is not the primary metric。

For every observable manual trace use a predeclared symmetric tolerance radius：

```text
reference/model tolerance radius = 8 px in the 512×512 frame
```

No radius sweep after outcome inspection。

Derive：

1. **model-on-reference precision-like coverage**
   - fraction of model-class pixels falling within 8 px of the manual reference centerline；
2. **reference-on-model coverage**
   - fraction of rasterized manual centerline pixels falling within 8 px of the model-class mask；
3. **bidirectional coverage harmonic mean**
   - harmonic mean of the above two values when defined；
4. **median nearest-distance model→reference** in pixels；
5. **median nearest-distance reference→model** in pixels；
6. class presence / absence agreement at observation level。

The 8 px tolerance is an audit convenience, not a production threshold。

## Semantic mismatch accounting

For every observable reference class, also compare that manual reference against **all three model classes**。

Record：

```text
manual heart -> model heart/head/life
manual head  -> model heart/head/life
manual life  -> model heart/head/life
```

This distinguishes：

- correct spatial + correct class label；
- correct spatial structure but wrong shipped label；
- no corresponding model structure。

Do not post-hoc relabel model classes to maximize agreement。

## Primary summaries

Across the ten images report for each manual class：

- counts of `observable / uncertain / not_observable`；
- number of observable references with corresponding model class present；
- correct-class coverage summaries；
- best-wrong-class coverage summaries；
- count where a wrong model class exceeds correct-class harmonic coverage；
- median nearest-distance summaries；
- per-source table。

No single aggregate score is treated as anatomical truth。

## Optional second annotation pass

If a second independent human annotator is available, use the same blind packet and same schema, then report inter-annotator agreement separately before comparison to model。

A second annotator is preferred but not required for this bounded exploratory audit。With only one annotator, conclusions must explicitly remain single-observer evidence。

## Stop rules

Stop before model comparison if：

- source/model/provenance SHA drifts；
- baseline image SHA does not reproduce prior raw evidence；
- annotator opens model overlays before freezing annotations；
- reference annotation file is edited after its freeze SHA is recorded；
- coordinate schema is invalid；
- any image is removed because its prediction looks poor。

## Interpretation boundary

A favorable manual audit would support that the model output is spatially associated with independently visible target crease structures on this bounded sample。

It still would not establish：

- clinical anatomy；
- identity / biometrics；
- population-wide segmentation accuracy；
- Chinese palmistry semantic equivalence；
- fortune-reading validity；
- a production cutoff。

An unfavorable or mixed audit must be preserved as evidence and must not trigger threshold lowering or post-hoc class relabeling。

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
