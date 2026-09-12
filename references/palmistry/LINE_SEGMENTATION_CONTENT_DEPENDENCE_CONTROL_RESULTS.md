# Palm Line Segmentation Content-Dependence / Specificity Control Results

Status: **REFERENCE-ONLY / BOUNDED RESULT / RAW ARTIFACT HASH PINNED**

This document closes the predeclared content-dependence / specificity control in `LINE_SEGMENTATION_CONTENT_DEPENDENCE_CONTROL_PLAN.md`.

The study asks only whether the shipped FP32 model's three tool-local classes remain active when the corrected `C_G1_M0` palm geometry is held fixed but line-scale / spatial image content is deliberately removed.

It does **not** establish anatomical correctness, palmistry validity, or production suitability.

## Provenance

Corrected adapter diagnosis raw SHA256:

```text
c51651cdc267b0416c0883ffba13e1ed0b5992aa808944e1786e2bc20d0e38d3
```

Corrected G1 repeatability raw SHA256:

```text
a1f0293f3662846255f335fe79d060b054852367f60c74fa4d558e6fe825d238
```

Content-control raw artifact:

```text
/home/user/palm-detector-study/results/MOHI_line_segmentation_content_dependence_control.json
```

SHA256:

```text
317e85351e4141206b28aec5277433ba3caed9a53e3eb01866cd38900699022f
```

Formal execution:

```text
10 frozen MOHI sources × 4 content conditions = 40 ONNX inference executions
baseline_reproduction_failures = 0
stop = false
```

## Baseline reproduction

`baseline_512` reproduces the corrected G1 regime on every source:

```text
heart_line_presence = 10/10
head_line_presence  = 10/10
life_line_presence  = 10/10
all_three_presence  = 10/10
any_foreground      = 10/10
```

Foreground fraction:

```text
mean   = 0.014684
median = 0.015825
p10    = 0.011698
p90    = 0.017928
min    = 0.003269
max    = 0.018669
```

This closes the deterministic baseline gate for the content-control node.

## Content-destruction result

All three destructive controls collapse every source to background-only output.

| Condition | heart | head | life | all three | any foreground |
|---|---:|---:|---:|---:|---:|
| baseline_512 | 10/10 | 10/10 | 10/10 | 10/10 | 10/10 |
| lowpass_32 | 0/10 | 0/10 | 0/10 | 0/10 | 0/10 |
| lowpass_16 | 0/10 | 0/10 | 0/10 | 0/10 | 0/10 |
| global_mean_rgb | 0/10 | 0/10 | 0/10 | 0/10 | 0/10 |

For `lowpass_32`, `lowpass_16`, and `global_mean_rgb`, foreground fraction is exactly zero on all ten sources.

Thus there is no evidence in this bounded control that a training-like corrected palm geometry alone is sufficient to make the model paint the three canonical tool-local classes.

## Manipulation checks

Observed mean Sobel gradient-energy ratio relative to baseline:

```text
baseline_512   = 1.000000
lowpass_32     = 0.475178
lowpass_16     = 0.371932
global_mean_rgb= 0.000000
```

Observed normalized mean absolute difference from baseline:

```text
lowpass_32      mean = 0.013563
lowpass_16      mean = 0.024480
global_mean_rgb mean = 0.115867
```

On the real MOHI sample, the frozen low-pass controls therefore materially reduce grayscale gradient energy while preserving progressively less spatial detail.

The non-MOHI dry-run had shown a small synthetic Sobel increase for low-pass controls; this did not occur on the formal MOHI sample and was not used as a pass/fail criterion.

## Within-image baseline versus controls

For every source, every shipped foreground class transitions from present at baseline to absent under each destructive control.

For each of the three controls:

```text
heart_line: 10/10 appearance transitions, Dice = 0
head_line : 10/10 appearance transitions, Dice = 0
life_line : 10/10 appearance transitions, Dice = 0
foreground union: 10/10 appearance transitions, Dice = 0
```

No control/source pair retains any foreground pixels.

This is stronger evidence of content dependence than merely observing reduced overlap or fragmented masks: the argmax output changes completely to background.

## Cross-person consensus

Baseline pairwise overlap across ten sources is low in the common 512×512 model frame:

```text
45 source pairs
heart_line mean Dice = 0.098816
head_line  mean Dice = 0.136031
life_line  mean Dice = 0.070340
foreground-union mean Dice = 0.161658
foreground-union median Dice = 0.141943
```

Under each destructive control, all ten outputs are empty foreground masks. Therefore all 45 pairwise foreground/class comparisons are `not_applicable_empty_both`; there is no non-empty canonical-template convergence to measure.

This result does **not** support the predeclared canonical-prior pattern in which content removal would cause different palms to converge toward a shared structured three-line template.

## P001 / P002

P001 and P002 behave the same qualitatively as the other eight sources under the content controls:

```text
baseline_512: all three classes present
lowpass_32: no foreground
lowpass_16: no foreground
global_mean_rgb: no foreground
```

The content-dependence control therefore does not identify P001/P002 as special cases. Their repeatability sensitivity remains a separate observation from the global content-removal response.

## Global-mean negative control

For all ten `global_mean_rgb` inputs:

```text
background winner_fraction = 1.000000
heart_line winner_fraction = 0.000000
head_line winner_fraction  = 0.000000
life_line winner_fraction  = 0.000000
```

Background mean logits are approximately +5, while the three foreground-class mean logits are negative. The flat-color negative control therefore does not reveal latent structured foreground masks hidden only by a narrow argmax tie.

## Answer to the frozen directional questions

1. **Does C0 reproduce corrected G1 baseline exactly?** Yes; 0 baseline reproduction failures.
2. **Do all three classes remain under `lowpass_32`?** No; all foreground disappears on 10/10 sources.
3. **Do they remain under `lowpass_16`?** No; all foreground disappears on 10/10 sources.
4. **Does structured output persist under `global_mean_rgb`?** No; all ten outputs are background-only.
5. **Does baseline-vs-control overlap decline?** It collapses completely to Dice 0 via appearance transitions for all classes and foreground union.
6. **Does cross-person consensus rise toward a non-empty canonical template?** No. Controls produce only empty foreground masks.
7. **Are heart/head/life differently affected?** Not at the presence level; all three collapse completely under all three destructive controls.
8. **Do P001/P002 behave differently?** Not under this control family; they collapse to background like all other sources.
9. **Is there pathological foreground flooding or fragmentation?** No; the opposite occurs—foreground disappears completely.

## Bounded interpretation

The strongest supported conclusion is:

> In this bounded ten-image MOHI sample, the corrected `C_G1_M0` geometry is not sufficient by itself to sustain the shipped model's three foreground classes. Removing fine-to-mid-scale spatial image content causes a complete transition to background on every source.

This materially weakens the **strong geometry-only canonical-prior hypothesis** that the model simply paints three canonical lines whenever it sees a training-like palm crop.

The result is instead consistent with substantial **image-content dependence**.

However, this control does **not** establish that the model is specifically responding to anatomically correct heart/head/life lines. A model may depend on high-frequency or mid-frequency palm texture, crease fragments, illumination edges, acquisition texture, or other correlated visual cues without segmenting the intended anatomical structures correctly.

Therefore the evidence boundary is:

```text
SUPPORTED:
- geometry alone is insufficient in these controls;
- foreground prediction requires spatial image content at frequencies removed by lowpass_32;
- no structured three-line output persists on flat-color inputs;
- no non-empty cross-person canonical-template convergence is observed.

NOT ESTABLISHED:
- anatomical line correctness;
- semantic correctness of heart/head/life labels;
- which spatial frequencies are minimally sufficient;
- whether the decisive high-frequency cues are true palm creases versus incidental texture;
- production admission thresholds.
```

## Recommended next evidence node

Do **not** add new low-pass sizes to this completed node. Its control family is frozen and closed.

The highest-value next node should distinguish **coherent palm-line spatial structure** from merely **generic high-frequency texture**. A separately predeclared structure-disruption control can preserve local texture statistics while breaking global spatial arrangement, for example with deterministic fixed-grid tile permutation and an inverse-permutation mask comparison.

That follow-up would ask whether predicted foreground follows relocated local image evidence, collapses when global structure is disrupted, or remains in canonical output locations.

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
