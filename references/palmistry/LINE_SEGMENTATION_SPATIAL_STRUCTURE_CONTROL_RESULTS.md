# Palm Line Segmentation Spatial-Structure / Texture-Cue Control Results

Status: **REFERENCE-ONLY / BOUNDED RESULT / RAW ARTIFACT HASH PINNED**

本文件記錄 `LINE_SEGMENTATION_SPATIAL_STRUCTURE_CONTROL_PLAN.md` 的正式結果。它回答的是：在 corrected `C_G1_M0`、相同 512×512 model-input geometry 與相同低頻 palm appearance 下，若只重新排列高頻 residual 的空間位置，或只反轉 residual 極性，模型輸出如何變化。

## Raw evidence

```text
/home/user/palm-detector-study/results/MOHI_line_segmentation_spatial_structure_control.json
```

SHA256：

```text
ba65456e3c7c3a645a4000c721961d0f600b46541ffc7e7566525b99a55f87e7
```

Pinned prior content-dependence artifact：

```text
317e85351e4141206b28aec5277433ba3caed9a53e3eb01866cd38900699022f
```

Execution：

```text
10 sources × 4 conditions = 40 inference executions
anchor_reproduction_failures = 0
stop = false
```

## Frozen conditions

```text
baseline_512
residual_shuffle_64
residual_shuffle_32
residual_sign_flip
```

The two shuffle conditions retain the original `lowpass_32` spatial frame and permute only the high-frequency residual using the predeclared fixed no-fixed-point mappings. `residual_sign_flip` preserves residual location and magnitude but reverses residual polarity.

## Presence / occupancy

| condition | heart | head | life | all three | any foreground | FG fraction mean |
|---|---:|---:|---:|---:|---:|---:|
| baseline_512 | 10/10 | 10/10 | 10/10 | 10/10 | 10/10 | 0.014684 |
| residual_shuffle_64 | 0/10 | 0/10 | 2/10 | 0/10 | 2/10 | 0.000019 |
| residual_shuffle_32 | 0/10 | 0/10 | 0/10 | 0/10 | 0/10 | 0.000000 |
| residual_sign_flip | 6/10 | 7/10 | 8/10 | 6/10 | 8/10 | 0.009479 |

The 64 px shuffle therefore produces only two extremely small life-line activations; the 32 px shuffle eliminates all foreground; sign flip preserves substantial foreground on most sources.

## Manipulation checks

Mean Sobel gradient-energy ratios relative to baseline：

```text
baseline              1.000000
residual_shuffle_64   1.102674
residual_shuffle_32   1.185921
residual_sign_flip    1.040703
```

Thus shuffle collapse cannot be attributed to insufficient generic high-frequency energy. Both shuffle controls contain at least as much mean Sobel-gradient energy as baseline, yet foreground almost entirely disappears.

Formal MOHI clipping fractions are very small：

```text
shuffle_64 mean = 0.000147  (~0.0147%)
shuffle_32 mean = 0.000122  (~0.0122%)
sign_flip  mean = 0.000060  (~0.0060%)
```

The observed collapse therefore does not plausibly reduce to widespread clipping. Clipping remains a measured manipulation side effect and is not ignored.

## Direct overlap with baseline

### residual_shuffle_64

```text
heart: direct Dice mean = 0.000000
head : direct Dice mean = 0.000000
life : direct Dice mean = 0.000000
union: direct Dice mean = 0.000000
```

Two sources retain tiny life-line foreground, but those activations have zero direct overlap with baseline life-line pixels.

### residual_shuffle_32

All three classes and foreground union have direct Dice = 0.0 with 10/10 baseline-to-empty appearance transitions.

### residual_sign_flip

```text
heart Dice mean = 0.447889
head  Dice mean = 0.434686
life  Dice mean = 0.590080
union Dice mean = 0.518611
union Dice median = 0.644230
```

The sign-flipped result is therefore materially closer to baseline than either shuffled condition.

## Inverse-unshuffle diagnostic

Aggregate inverse-unshuffle improvements remain negligible：

```text
shuffle_64:
  life  inverse Dice mean = 0.007940
  union inverse Dice mean = 0.002105

shuffle_32:
  all classes / union inverse Dice mean = 0.000000
```

The only non-zero per-source inverse-unshuffle union Dice values occur for the two tiny `shuffle_64` life-line activations：

```text
P006 = 0.006444
P009 = 0.014604
```

This is not meaningful restoration of the baseline masks. The bounded sample therefore provides no substantial evidence that predictions simply follow relocated local residual tiles.

## Cross-person consensus

Baseline foreground-union cross-person Dice mean：

```text
0.161658
```

`shuffle_64` and `shuffle_32` do not converge to a common structured template. They mostly collapse to empty masks. Under sign flip, foreground-union pairwise Dice mean is only：

```text
0.067161
```

which is lower than baseline. No canonical-template convergence is observed.

## Per-source heterogeneity under sign flip

`residual_sign_flip` responses are heterogeneous：

```text
P001: no foreground
P002: head + life
P003: all three
P004: life only
P005: all three
P006: all three
P007: all three
P008: all three
P009: all three
P010: no foreground
```

Thus polarity sensitivity is source dependent. It cannot be summarized as either polarity-invariant or polarity-required.

## Bounded interpretation

The strongest result from this node is：

> **Generic high-frequency residual energy is not sufficient for the shipped model to produce the baseline three-class masks. Spatial arrangement of the high-frequency structure is materially important.**

The evidence chain is：

1. `lowpass_32` alone previously produced 0/10 foreground;
2. adding the same residual samples back at shuffled locations raises or preserves high-frequency energy but does not restore the baseline classes;
3. 32 px shuffling yields complete foreground collapse;
4. 64 px shuffling yields only two tiny, non-overlapping life-line activations;
5. inverse-unshuffle does not materially recover baseline overlap;
6. preserving residual location while reversing polarity retains substantial foreground in 8/10 sources and all three classes in 6/10.

This pattern is more consistent with dependence on **coherent spatial high-frequency / crease-like structure** than with dependence on generic texture energy or a geometry-only canonical three-line prior.

At the same time, sign-flip results show that exact dark-vs-light polarity is **not an absolute requirement**. Polarity contributes materially, but spatial support / arrangement appears more important than polarity alone in this bounded sample.

## What this still does not establish

This node does **not** prove：

- that predicted pixels are anatomically correct palm lines；
- that `heart_line`, `head_line`, and `life_line` labels correspond correctly to visible human crease structures；
- that the model distinguishes major creases from unrelated skin texture, shadows, folds, or acquisition artifacts；
- semantic correctness under Chinese palmistry terminology；
- production eligibility or any admission cutoff。

The remaining dominant evidence gap is no longer content dependence or perturbation stability. It is **independent anatomical/manual validation against visible line structure**.

## Next evidence node

The next highest-value node should therefore be a predeclared anatomical/manual audit using the frozen corrected baseline outputs. It should keep model outputs hidden during reference annotation, separate observation from interpretation, and compare independently marked visible crease structure against the model only after annotation is frozen.

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
