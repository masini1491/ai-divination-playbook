# Palm Line Segmentation Repeatability Plan

Status: **REFERENCE-ONLY / PREDECLARED / RUNTIME-MODEL GATE OPEN / NO RESULT INSPECTION**

本 Cold plan 凍結 Palmistry observation research 的下一個 independent evidence node：**principal-line segmentation repeatability / transform sensitivity**。

本研究不驗證手相學解讀，也不把 model class 當成中國傳統掌紋 terminology authority。目標只是在 permission-qualified palm images 上，量化同一個 shipped line-segmentation model 對小幅 image-space perturbation 的 mask stability。

## Research question

在固定 palm crop 與固定 shipped ONNX model 下：

> 對同一張 palm crop 做小幅 rotation / scale / crop perturbation，再把 predicted masks inverse-map 回 baseline crop frame 時，background / heart-line / head-line / life-line segmentation masks 的重疊穩定性有多高？

這個 node 衡量的是 **segmentation implementation uncertainty**，不是 line truth accuracy。

## Upstream implementation

Source repository：

```text
samuelwbarber/palm-line-reader
reviewed revision:
bc48939f4deee6d8ff842bfde499396dab9c4830
license: MIT
```

Shipped model contract from `models/model_meta.json`：

```text
model: palm-line-student-exp2
architecture: segmentation_models_pytorch UNet / mit_b0
input: RGB float32 NCHW [1,3,512,512]
resize: plain bilinear to 512×512, no letterbox
normalization: ImageNet mean/std after /255
output: logits [1,4,512,512]
classes:
0 background
1 heart_line
2 head_line
3 life_line
```

Upstream metadata reports `val_fg_dice = 0.8098`, but this aggregate validation metric is not treated as a per-image accuracy guarantee.

## Frozen model choice

First-study baseline：

```text
models/student_fp32.onnx
```

Reason：upstream metadata explicitly describes fp32 as `highest fidelity / verification baseline`。

FP16 / INT8 are not mixed into this first study. Quantization sensitivity is a separate future node.

Before any MOHI inference, runtime/model gate must record：

```text
onnxruntime exact version
numpy exact version
opencv exact version
execution provider(s)
student_fp32.onnx full SHA256
upstream revision
model_meta.json identity / SHA
```

No result inspection is allowed before this gate closes.

## Source sample

Reuse existing permission-qualified MOHI source package：

```text
10 dataset person IDs
3 sessions
5 image entries / session
150 image entries total
```

Source ZIP SHA256 remains：

```text
6309f2390b0013858928c6c77344b4aa869edc8c0aeb9a61db93b73ae83feec2
```

First-study sample is deliberately small and deterministic because this node is a transform-repeatability probe, not a population estimate.

Select one source image per person：

```text
P001/S1/01.jpg
P002/S1/01.jpg
...
P010/S1/01.jpg
```

If any selected source is byte-duplicate of another selected source, replace only by the next lexicographic path for that same person before any model output is inspected.

## Frozen palm-crop adapter

Do **not** use upstream reconstructed `pipeline/hand_preprocess.py` as historical training truth. That module explicitly states the original preprocessing file was not recovered and the current implementation is a reconstruction.

Instead, define a study-local deterministic crop using already frozen MediaPipe MOHI raw landmarks.

For each selected baseline source：

```text
1. use frozen MediaPipe 21 raw-image landmarks from MOHI evidence;
2. use the same raw pixel frame as that evidence;
3. compute all-21-landmark bounding box;
4. expand by 15% of max(bbox_width, bbox_height) on every side;
5. pad outside-image regions with black if needed;
6. rotate once so L0(wrist) → L9(middle MCP) points vertically upward;
7. re-crop to the smallest square containing the rotated expanded ROI;
8. this square RGB image becomes the immutable baseline palm crop for the segmentation study.
```

No handedness-based mirroring is used in this first study.

This crop is study-local and source-neutral; it is not claimed to reproduce upstream training preprocessing.

## Why transforms are applied after crop freeze

The purpose is to isolate segmentation sensitivity from detector/crop sensitivity.

Therefore：

```text
raw image + frozen landmarks
→ one immutable baseline crop
→ perturb baseline crop pixels
→ segmentation inference
→ inverse-map predicted mask to baseline-crop frame
```

Do not re-run MediaPipe for each transform.

## Frozen perturbation set

For every baseline palm crop, execute exactly these variants：

```text
baseline
rotate +5°
rotate -5°
scale 0.90×
scale 1.10×
center crop 3% each side, then resize back to baseline crop size
```

Transforms operate about crop center.

Rotation / scale use bilinear interpolation for RGB input. Areas introduced by transform are black.

Do not add brightness, blur, compression, mirror, color-jitter, or larger transforms after seeing outcomes. Those require a later predeclared node.

## Model preprocessing

Every variant follows shipped contract exactly：

```text
RGB
→ plain bilinear resize 512×512
→ float32 / 255
→ per-channel ImageNet normalize
→ NCHW [1,3,512,512]
→ student_fp32.onnx
→ logits [1,4,512,512]
→ argmax axis=1
```

No softmax threshold is used in first study.

## Inverse mapping

For transform variants, predicted class-index masks are mapped back through the exact inverse image transform into the baseline crop frame before comparison.

Mask inverse mapping uses nearest-neighbor interpolation only.

The baseline prediction remains in the baseline crop frame.

## Primary metrics

For each non-background class `c ∈ {1,2,3}` and each variant：

```text
Dice_c = 2|A∩B| / (|A|+|B|)
IoU_c  = |A∩B| / |A∪B|
```

where：

```text
A = baseline predicted mask for class c
B = inverse-mapped variant predicted mask for class c
```

Also record：

- foreground union Dice / IoU where foreground = classes 1|2|3;
- class pixel counts at baseline and variant;
- connected-component count per class;
- largest-component area fraction per class;
- class absence / appearance transitions.

If both A and B are empty for a class, record the overlap metric as `not_applicable_empty_both`, not as perfect agreement.

If one is empty and the other is not, Dice / IoU = 0 and record an appearance/disappearance transition.

## Aggregation order

```text
source integrity
→ runtime/model identity
→ crop construction accounting
→ baseline model output accounting
→ per-image/per-class transform metrics
→ per-transform summaries
→ per-class summaries
→ per-person heterogeneity
→ only then qualitative interpretation
```

Do not collapse immediately to one pooled mean.

## Directional research questions

Frozen before result inspection：

1. Are the three shipped line classes equally stable under small transforms, or is one class systematically less repeatable?
2. Are rotation perturbations materially more disruptive than scale / mild center-crop perturbations?
3. Does transform sensitivity manifest mainly as boundary displacement, line disappearance/appearance, or connected-component fragmentation?
4. Are there palm images with consistently higher segmentation instability across all perturbation types?
5. Is foreground-union repeatability materially higher than class-specific repeatability, suggesting class-boundary uncertainty rather than line-presence uncertainty?

## Stop rules

Stop before interpretation if：

- `student_fp32.onnx` identity cannot be pinned by full SHA256;
- ONNX input/output shapes differ from upstream metadata contract;
- runtime/provider identity is not recorded;
- any selected source image or MediaPipe evidence fails source integrity;
- baseline crop cannot be deterministically reconstructed;
- exact forward/inverse transform matrices are not retained;
- output requires a post-hoc confidence threshold to make masks usable;
- model execution fails on any selected baseline image.

## Prohibitions

Do **not**：

- call model output ground truth palm lines;
- map `heart/head/life` directly to Chinese `天/人/地紋`;
- infer fortune / health / personality from masks in this node;
- tune crop margin after looking at results;
- tune logits / probability thresholds after looking at results;
- exclude unstable palms post hoc;
- add morphological cleanup not specified by shipped model contract;
- use upstream reconstructed crop as historical-training authority;
- derive a production cutoff from this 10-image bounded probe;
- commit MOHI source images or ONNX binaries into this repo.

## Evidence boundary

If successfully executed, this study can establish only：

> On a deterministic 10-image MOHI bounded sample and a pinned shipped fp32 ONNX model, the transform-repeatability distribution of the model's own three principal-line segmentation classes under a fixed study-local palm crop adapter.

It does not establish：

- anatomical line truth;
- model accuracy against human ground truth;
- Chinese Palmistry terminology equivalence;
- longitudinal line stability;
- device-to-device repeatability;
- production admission thresholds.

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
