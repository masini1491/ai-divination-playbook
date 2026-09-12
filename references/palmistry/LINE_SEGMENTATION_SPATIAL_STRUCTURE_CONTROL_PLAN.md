# Palm Line Segmentation Spatial-Structure / Texture-Cue Control Plan

Status: **REFERENCE-ONLY / PREDECLARED / NO SPATIAL-STRUCTURE CONTROL OUTPUT INSPECTED**

本文件凍結 content-dependence control 之後的下一個 bounded evidence node。

前一節點已觀察到：

```text
baseline_512     : all-three 10/10
lowpass_32       : any foreground 0/10
lowpass_16       : any foreground 0/10
global_mean_rgb  : any foreground 0/10
```

這使「只靠 training-like palm geometry 即固定產生三線」的強 geometry-only prior 假說變弱，但仍不能區分模型真正依賴 coherent palm-line / crease structure，或只是依賴一般高頻 texture / local contrast cues。

本節點只回答：**保留 corrected palm geometry 與低頻 palm appearance，並保留高頻 residual 的能量與局部像素內容，但重新排列 residual 的空間位置或反轉其極性時，模型輸出如何改變？**

## Evidence authority

Pinned content-dependence raw artifact：

```text
317e85351e4141206b28aec5277433ba3caed9a53e3eb01866cd38900699022f
```

The referenced artifact itself pins：

```text
corrected adapter diagnosis = c51651cdc267b0416c0883ffba13e1ed0b5992aa808944e1786e2bc20d0e38d3
corrected G1 repeatability = a1f0293f3662846255f335fe79d060b054852367f60c74fa4d558e6fe825d238
```

Primary adapter remains `C_G1_M0`。No mirror、margin、threshold、morphology or geometry retuning。

## Frozen model/runtime/source

Same pinned model/runtime and same ten MOHI sources as the preceding nodes。All controls operate in the same 512×512 RGB model-input frame before `/255` and ImageNet normalization。

## Frozen decomposition

For each corrected C crop：

```text
baseline_512 = shipped bilinear resize to 512×512
lowpass_32   = baseline_512 -> INTER_AREA 32×32 -> INTER_LINEAR 512×512
residual     = int16(baseline_512) - int16(lowpass_32)
```

The identity reconstruction must hold exactly in integer arithmetic before clipping：

```text
int16(lowpass_32) + residual == int16(baseline_512)
```

The generated `baseline_512` and `lowpass_32` RGB array SHA256 values must exactly reproduce those already recorded in the pinned content-dependence artifact for every source。Failure stops the run。

## Frozen conditions

Exactly four inference conditions per source：

### S0 — baseline_512

Unmodified baseline model-input RGB frame。

### S1 — residual_shuffle_64

Keep `lowpass_32` in its original spatial frame。Split only the high-frequency residual into an 8×8 grid of 64×64 tiles。

For destination tile index `d` in row-major order：

```text
source tile index = (17*d + 23) mod 64
```

Destination receives that source residual tile。Because `gcd(17,64)=1`, this is a permutation；the chosen offset yields no fixed tile positions。

Then reconstruct：

```text
clip(lowpass_32 + shuffled_residual, 0, 255)
```

Purpose：retain coarse palm geometry/illumination and the same residual sample distribution while disrupting coherent crease-scale spatial arrangement at a 64 px tile scale。

### S2 — residual_shuffle_32

Same construction, using a 16×16 grid of 32×32 residual tiles。

For destination index `d`：

```text
source tile index = (73*d + 37) mod 256
```

`gcd(73,256)=1`; no fixed tile positions under this mapping。

Purpose：stronger spatial disruption while retaining the same low-frequency frame and residual value distribution before clipping。

### S3 — residual_sign_flip

Preserve residual spatial location and magnitude but reverse local residual polarity：

```text
clip(lowpass_32 - residual, 0, 255)
```

Purpose：test sensitivity to dark-vs-light local contrast polarity without moving the residual spatial support。

## No post-outcome tuning

Do not change tile sizes, permutations, low-pass anchor, sign convention, clipping behavior, model threshold, morphology, sample membership, adapter geometry, or add rescue controls after seeing outputs。

## Baseline and anchor reproduction gates

The runner must load the pinned content-dependence JSON and verify its SHA256 exactly。

For every source：

1. regenerated `baseline_512` input SHA == prior `baseline_512` input SHA；
2. regenerated `lowpass_32` input SHA == prior `lowpass_32` input SHA；
3. newly inferred S0 baseline mask SHA == prior baseline mask SHA；
4. predicted classes and mask stats exactly reproduce the prior baseline；
5. `lowpass_32 + residual` reconstructs baseline exactly before clipping。

Any failure stops before interpretation。

## Primary metrics

For every source × condition：

- predicted class set；
- per-class and foreground occupancy；
- connected components / largest component fraction；
- RGB input SHA / mask SHA；
- direct per-class and union Dice/IoU versus S0 baseline；
- mean absolute RGB difference versus baseline；
- Sobel gradient energy and ratio to baseline；
- clipping fraction when reconstructing manipulated RGB；
- residual mean absolute magnitude before reconstruction。

For S1/S2 additionally compute an **inverse-unshuffle diagnostic**：take the predicted mask tiles in the shuffled frame and place destination tile `d` back into its corresponding original source tile index. Compare this inverse-unshuffled mask with S0 baseline。

This is descriptive only. Because the low-frequency frame is never shuffled, inverse-unshuffle is not an exact image-space inverse of the whole manipulated input。

## Cross-person consensus

For each condition, compute the same 45 pairwise class / foreground-union Dice summaries across ten subjects as in the preceding content-dependence study。

## Frozen directional questions

Before output inspection：

1. Does S0 reproduce the prior content-dependence baseline exactly?
2. Does adding spatially shuffled high-frequency residual to the otherwise non-activating lowpass anchor restore any foreground classes?
3. Is restoration stronger for 64 px or 32 px residual tiles?
4. When shuffled outputs exist, is inverse-unshuffle Dice materially higher than direct Dice, consistent with predictions following relocated local residual cues?
5. Do outputs instead stay close to baseline locations despite shuffled residual, consistent with a stronger geometry/coarse-context prior?
6. Does residual sign flip retain, distort, or eliminate foreground classes?
7. Are effects class-specific?
8. Do P001/P002 differ from the other subjects?
9. Do controls cause pathological foreground flooding or fragmentation?
10. Does cross-person consensus rise under any manipulation?

## Interpretation constraints

Evidence more consistent with dependence on **coherent spatial crease structure** includes：

- shuffled residual fails to restore foreground despite high-frequency residual being present；
- sign flip strongly suppresses or changes predictions；
- outputs require the original residual arrangement rather than merely its energy/distribution。

Evidence more consistent with **generic/local texture cue dependence** includes：

- shuffled residual restores substantial foreground；
- output relocates with shuffled residual such that inverse-unshuffle agreement exceeds direct agreement；
- class activation persists despite destruction of global crease arrangement。

Evidence more consistent with a **canonical spatial prior** includes：

- shuffled residual restores lines primarily in baseline-like fixed locations, with direct agreement stronger than inverse-unshuffle agreement despite relocated residual evidence。

Mixed evidence is explicitly allowed。

None of these patterns establishes anatomical correctness or segmentation accuracy。

## Execution accounting

Expected formal run：

```text
10 source images × 4 conditions = 40 ONNX inference executions
```

No third-party images are committed。Raw JSON remains local evidence。

## Stop rules

Stop before substantive interpretation if any pinned identity drifts, baseline/lowpass anchor reproduction fails, integer reconstruction fails, permutation integrity fails, model/runtime/source identity drifts, or any control requires post-hoc rescue。

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
