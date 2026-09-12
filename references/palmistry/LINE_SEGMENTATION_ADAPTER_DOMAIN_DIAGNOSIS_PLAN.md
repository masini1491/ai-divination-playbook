# Palm Line Segmentation Adapter / Domain Diagnosis Plan

Status: **REFERENCE-ONLY / PREDECLARED / NO ADAPTER-DIAGNOSIS OUTPUT INSPECTED**

本文件凍結 `LINE_SEGMENTATION_REPEATABILITY_RESULTS.md` 之後的下一個 bounded evidence node：判斷低 observability 是否主要與 **crop/orientation adapter mismatch** 有關，而不是立即調整 model threshold、class contract 或更換 model。

## Motivation

第一輪 MOHI segmentation-repeatability probe 在固定 study-local adapter 下觀察到：

```text
heart_line baseline present = 0 / 10
head_line  baseline present = 2 / 10
life_line  baseline present = 5 / 10
```

因此下一步應先診斷 input adapter / domain compatibility，而不是從 outcome 反推 threshold。

Upstream pinned revision：

```text
samuelwbarber/palm-line-reader
bc48939f4deee6d8ff842bfde499396dab9c4830
```

其 `pipeline/hand_preprocess.py` 明確標示為 **reconstruction**：original `/home/ubuntu` preprocessing file 未被恢復。該 reconstruction 使用：

- MediaPipe landmarks；
- wrist L0 → middle MCP L9 fingers-up rotation；
- rotation center = all-landmark mean；
- rotate first；
- rotated-landmark bbox + fixed 100 px margin；
- optional horizontal mirror to one consistent MediaPipe handedness label。

因此本 node 只把這些內容當作 **upstream reconstructed geometry hypothesis**，不稱為 historical-training truth。

Upstream `plan.md` additionally states the student input should be a tight fingers-up palm crop and that training used slight rotation and crop/margin jitter. This supports testing adapter geometry as a plausible compatibility factor, but does not prove any one adapter is correct.

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

Model preprocessing remains shipped contract：RGB → plain bilinear 512×512 → /255 → ImageNet mean/std → NCHW float32 → argmax 4-class logits。

No probability/logit threshold is introduced。

## Frozen source sample

Reuse exactly the same 10 source entries as first study：

```text
P001/S1/01.jpg
P002/S1/01.jpg
...
P010/S1/01.jpg
```

Use the same permission-qualified MOHI package and the same frozen MediaPipe raw landmarks / raw-image frame。

No source replacement is permitted unless source integrity itself fails。

## Diagnosis factors

This node separates two adapter factors：

```text
Factor G — crop geometry
G0 = first-study geometry
G1 = upstream-reconstruction-like geometry

Factor M — horizontal mirror
M0 = no mirror
M1 = deterministic mirror
```

This yields four predeclared adapters。

### Adapter A = G0 / M0 — existing first-study adapter

Reference condition; do not recompute its interpretation if the existing raw artifact can be reused verbatim。

```text
all-21-landmark bbox in raw frame
+ 15% of max bbox dimension on every side
black pad if needed
crop first
rotate crop so L0→L9 points up
re-crop / square-pad rotated ROI
no mirror
plain resize to 512×512 for model
```

Existing raw artifact SHA256：

```text
396e47b83f040c5a71207fbef287a5c6fd94f55927e448cd0daeb6a24555d9c5
```

### Adapter B = G0 / M1 — existing geometry + mirror only

Same exact pixels/geometry as Adapter A before model input, then horizontal flip once before model resize/inference。

Purpose：isolate chirality canonicalization effect without changing crop geometry。

The mirror is a study-local deterministic transform, not anatomical handedness truth。

### Adapter C = G1 / M0 — reconstructed-upstream-like geometry, no mirror

Using frozen raw MediaPipe landmarks rather than rerunning a detector：

```text
1. use raw RGB and frozen L0..L20 coordinates;
2. center = mean of all 21 landmark coordinates;
3. choose rotation sign so L9 is vertically above L0 and horizontal L0↔L9 residual is minimized;
4. rotate full raw image about that center;
5. transform all 21 landmarks through exact affine matrix;
6. crop rotated landmark bbox + fixed 100 px margin on all sides;
7. black pad if bbox+margin exits source canvas;
8. no square-padding requirement;
9. no horizontal mirror;
10. plain bilinear resize crop to 512×512 for shipped model.
```

This mirrors the current upstream reconstructed geometry as closely as possible while holding landmark evidence fixed。

### Adapter D = G1 / M1 — reconstructed-upstream-like geometry + mirror

Same as Adapter C, then horizontal flip once before model resize/inference。

Purpose：test combined geometry + chirality canonicalization hypothesis。

## Why no upstream MediaPipe rerun

Do not rerun upstream `hand_landmarker.task` in this node because that would simultaneously change：

- detector implementation/version；
- landmark geometry；
- crop geometry；
- potentially handedness metadata。

The diagnosis question is adapter compatibility, so frozen MOHI landmark evidence remains constant。

## Primary diagnosis metrics

This is **not** another perturbation-repeatability study yet。

For each adapter and each of the 10 baseline source images, record：

1. class presence (`foreground_px > 0`) for classes 1/2/3；
2. foreground-union presence；
3. class pixel count and fraction of 512×512 model mask；
4. connected-component count and largest-component fraction；
5. per-image set of predicted classes。

Aggregate first by adapter：

```text
heart_line presence count / 10
head_line presence count / 10
life_line presence count / 10
any-foreground presence count / 10
all-three-classes presence count / 10
```

Also retain per-image outputs; do not collapse immediately to pooled totals。

## Secondary cross-adapter comparisons

For each source image and each class, compare Adapter A against B/C/D only when at least one side predicts the class：

- presence transition；
- Dice / IoU after mapping masks to the common raw-image frame if exact inverse geometry is available；
- otherwise do **not** compare pixel overlap across differently cropped 512×512 frames。

Presence comparison is valid without a common pixel frame; geometry overlap is not。

## Frozen directional questions

Before any Adapter B/C/D outputs are inspected：

1. Does horizontal mirror alone materially increase class observability relative to Adapter A?
2. Does reconstructed-upstream-like crop geometry materially increase class observability relative to Adapter A?
3. Is any improvement concentrated in `heart_line` / `head_line`, or only in already-observable `life_line`?
4. Is there a geometry × mirror interaction (D stronger than either B or C alone)?
5. Do previously fully-unobservable P001/P009 gain stable foreground support under any adapter?
6. Do adapters that increase presence also cause implausibly large foreground occupancy or severe fragmentation, indicating possible hallucination / domain mismatch rather than a clean compatibility gain?

## Interpretation guardrails

A higher presence count is **not automatically better accuracy** because there is no line ground truth in MOHI。

Possible outcomes：

### Geometry/mirror strongly changes observability

Then first-study low observability is at least partly adapter-sensitive. This justifies a later, separately predeclared repeatability comparison for the strongest *non-pathological* adapter(s)。

### All adapters remain similarly sparse

Then evidence shifts toward broader model/domain mismatch on this MOHI sample, though it still does not prove model inaccuracy against anatomical truth。

### Presence rises but masks become huge/fragmented

Do not call this improvement. Treat it as potential unstable activation / mismatch and retain the first-study caution。

## Stop rules

Stop before interpretation if：

- model/runtime/artifact identities drift；
- source ZIP or frozen MediaPipe evidence integrity fails；
- any adapter cannot be deterministically reconstructed；
- forward transform matrices / crop coordinates are not retained；
- different model preprocessing is accidentally used across adapters；
- a threshold, morphology cleanup, or class remapping becomes necessary；
- outcome inspection occurs before all four adapter definitions are fixed。

## Prohibitions

Do not：

- tune the 100 px reconstructed margin after outputs are seen；
- tune the 15% reference margin after outputs are seen；
- add multiple arbitrary margin sweeps to rescue observability；
- rerun MediaPipe per adapter；
- use anatomical handedness claims to justify mirror direction；
- add softmax thresholds；
- morphologically clean masks；
- map tool-local classes to Chinese Palmistry line names；
- select only images where an adapter looks good；
- derive production admission thresholds from this 10-image diagnosis。

## Evidence boundary

If successfully executed, this node can establish only：

> On the same bounded 10-image MOHI sample, with a pinned FP32 line-segmentation model and frozen landmark evidence, how predicted class observability changes across four predeclared crop/mirror adapters.

It cannot establish which adapter is anatomically correct, which segmentation is ground truth, or that any adapter is suitable for production Palmistry interpretation。

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
