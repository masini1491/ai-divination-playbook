# Palm Line Segmentation Content-Dependence / Specificity Control Plan

Status: **REFERENCE-ONLY / PREDECLARED / NO CONTENT-CONTROL OUTPUT INSPECTED**

本文件凍結 corrected upstream-affine-fixed `C_G1_M0` repeatability qualification 之後的下一個 bounded evidence node。

前一節點已建立：

- corrected `C_G1_M0` baseline = 10/10 all-three；
- 47/50 perturbation conditions retain all three classes；
- 50/50 retain some foreground；
- 4/150 class comparisons are appearance transitions；
- high repeatability alone仍無法區分「真正依賴掌紋影像內容」與「在 training-like palm crop 上穩定套用 canonical three-line structural prior」。

因此本節點只回答：**當 corrected palm crop geometry 保持不變、但 line-scale / spatial image content 被預先定義地削弱或移除時，模型輸出會如何改變？**

## Evidence authority

Pinned corrected adapter diagnosis raw artifact：

```text
c51651cdc267b0416c0883ffba13e1ed0b5992aa808944e1786e2bc20d0e38d3
```

Pinned corrected G1 repeatability raw artifact：

```text
a1f0293f3662846255f335fe79d060b054852367f60c74fa4d558e6fe825d238
```

Primary adapter remains：

```text
C_G1_M0
```

No mirror, no margin change, no geometry retuning。

## Frozen model/runtime/source

Do not change：

```text
model SHA256 = 3c02b88b82e54889d0ab2bf2ba108aec554a1b50759f7c7aaa45f2f114ed24ff
metadata SHA256 = 880b17a1f0ae8f0ad9c4061b0674e86381f50fadb242a662b44fdbaf4b919a98
onnxruntime = 1.29.0
numpy = 1.26.4
opencv-python = 4.10.0.84
provider = CPUExecutionProvider
```

Reuse exactly the same ten frozen MOHI sources：

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

Reuse frozen raw-image MediaPipe landmarks and current corrected upstream-affine-fixed `C_G1_M0` implementation。

## Why controls operate in the 512×512 model-input frame

Corrected G1 crops have different native sizes. Applying blur/downsampling in native crop pixels would make effective content destruction depend on crop size.

Therefore every corrected C crop is first resized exactly once using the shipped model preprocessing geometry：

```text
corrected C crop
→ RGB bilinear resize 512×512
```

The frozen controls are then generated in this common 512×512 RGB frame, before `/255` and ImageNet normalization。

This holds model-input geometry constant and makes content-control strength identical across subjects。

## Frozen content conditions

Exactly four conditions per source：

### C0 — baseline

```text
baseline_512
```

The unmodified 512×512 resized corrected C crop。

### C1 — lowpass_32

```text
512×512
→ INTER_AREA downsample to 32×32
→ INTER_LINEAR upsample to 512×512
```

Purpose：strongly suppress fine palm-line / crease-scale detail while retaining coarse palm shape, illumination and color layout。

### C2 — lowpass_16

```text
512×512
→ INTER_AREA downsample to 16×16
→ INTER_LINEAR upsample to 512×512
```

Purpose：stronger low-frequency-only control。No parameter selection after output inspection。

### C3 — global_mean_rgb

For each image independently：

```text
channel-wise mean RGB of baseline_512
→ round to nearest uint8
→ fill the entire 512×512 frame with that RGB triplet
```

Purpose：remove all spatial structure while retaining only per-image mean color level。This is a destructive negative control, not a realistic palm image。

## Prohibited post-outcome changes

Do not add or change：

- Gaussian sigma sweep；
- alternative low-pass sizes；
- threshold / softmax cutoff；
- morphology；
- skeletonization；
- histogram equalization；
- contrast rescue；
- line enhancement；
- per-image exclusions；
- new content controls after seeing outcome。

The fixed 32×32 and 16×16 controls are not tuned to this dataset。

## Baseline reproduction gate

The corrected repeatability raw artifact is required as an input to the runner and its SHA256 must equal：

```text
a1f0293f3662846255f335fe79d060b054852367f60c74fa4d558e6fe825d238
```

For every source, the runner must reconstruct corrected C, run the C0 512 inference, map its mask back to the native corrected crop using nearest-neighbor interpolation, and reproduce the corrected-repeatability baseline predicted classes and mask statistics exactly。

If any source fails this deterministic baseline reproduction, stop before interpreting content-control outputs。

## Primary within-image metrics

For each source and each control：

- predicted class set；
- per-class foreground pixels / fraction；
- foreground-union pixels / fraction；
- connected-component count；
- largest-component fraction；
- per-class Dice / IoU against C0 in the same 512×512 frame；
- foreground-union Dice / IoU against C0；
- mask SHA256；
- controlled RGB input SHA256。

Empty handling remains：

```text
both empty => not_applicable_empty_both, Dice/IoU = null
one empty  => appearance_transition, Dice/IoU = 0
```

## Input-destruction metrics

For each condition record：

- RGB channel mean；
- RGB channel std；
- mean absolute pixel difference from baseline, normalized by 255；
- Sobel gradient-energy mean in grayscale；
- gradient-energy ratio to baseline when baseline energy > 0。

These are manipulation checks, not segmentation quality metrics。

## Cross-person consensus metrics

All output masks remain in a common 512×512 model frame。For each condition and each class, compute all 45 pairwise comparisons across the ten sources：

- pairwise Dice summary；
- pairwise IoU summary；
- empty-both count；
- appearance-transition count。

Repeat for foreground union。

Interpretation purpose：

- if content destruction causes different people’s masks to converge toward a similar template, pairwise consensus should rise；
- if controls instead suppress outputs or preserve subject-specific differences, consensus behavior should differ。

Pairwise consensus is descriptive only and does not establish anatomical truth。

## Frozen directional questions

Before any control output is inspected：

1. Does C0 reproduce the corrected repeatability baseline exactly?
2. Do all three classes remain present under `lowpass_32`?
3. Do they remain present under the stronger `lowpass_16`?
4. Does any structured three-class output persist under `global_mean_rgb`, where all spatial evidence is removed?
5. How much does baseline-vs-control mask overlap decline as high-frequency image content is removed?
6. Does cross-person mask consensus rise as content is removed, suggesting convergence toward a canonical template?
7. Are heart/head/life affected differently by content destruction?
8. Do P001/P002 behave differently from the otherwise highly repeatable subjects?
9. Are any observed effects accompanied by pathological foreground flooding or fragmentation?

## Interpretation constraints

Evidence more consistent with **content dependence** would include one or more of：

- substantial class disappearance under low-pass controls；
- substantial baseline-vs-control geometric change；
- collapse toward background under `global_mean_rgb`；
- persistence of meaningful between-subject output differences despite low-pass controls。

Evidence more consistent with a **strong canonical prior** would include one or more of：

- all-three outputs remain common despite severe low-pass filtering；
- masks remain highly overlapped with baseline after line-scale detail removal；
- `global_mean_rgb` still produces structured line-like classes；
- cross-person mask consensus rises strongly as image content is removed。

These are qualitative evidence patterns, not predeclared production thresholds。

Mixed results are explicitly allowed。

## Execution accounting

Expected formal run：

```text
10 source images × 4 content conditions = 40 ONNX inference executions
```

No third-party images are written to the repository。Raw JSON remains local evidence only。

## Stop rules

Stop before substantive interpretation if：

- model/runtime/source identity drifts；
- corrected adapter-diagnosis SHA reference drifts；
- corrected repeatability artifact SHA differs from the pinned value；
- C0 native-frame baseline reproduction fails for any source；
- any condition requires rescue/tuning；
- condition generation is nondeterministic；
- source exclusions occur after outcome inspection。

## Evidence boundary

This node can test whether model output is sensitive to spatial / high-frequency image content under a bounded corrected-G1 setup。

It still cannot establish：

- anatomical palm-line correctness；
- segmentation ground-truth accuracy；
- Palmistry validity；
- historical training truth；
- production suitability；
- biometric identity properties。

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
