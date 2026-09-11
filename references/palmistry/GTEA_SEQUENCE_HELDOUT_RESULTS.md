# GTEA Sequence-held-out Validation Results

Status: **REFERENCE-ONLY / NATURAL CAPTURE EXECUTED**

This Cold report records the execution of the predeclared whole-sequence validation plan in `GTEA_SEQUENCE_HELDOUT_PLAN.md`. It does not establish a production Palmistry gate, threshold, routing rule, or method capability.

## Provenance

Dataset archive SHA256:

```text
a64c0fcff572414fa964c5b524e989ffe2e0a6023316bf4554a0f3e24d66fb8b
```

Pinned Hand Landmarker SHA256:

```text
fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1
```

Research workflow run:

```text
run 34626446265
head 9f3c2e1b3cf2d381c28428320cbe00f93e0984b7
job 103352600776
conclusion success
```

Runtime kept the frozen detector contract:

```text
MediaPipe 1.0.1
Python 3.12.14
num_hands 4
detection / presence / tracking thresholds 0.5 / 0.5 / 0.5
running_mode IMAGE
```

## Population

Direct-XML two-hand admission produced:

```text
eligible frames   556
GTEA sequences     25
```

Final Hand Landmarker candidate distribution:

| Candidates | Frames |
|---:|---:|
| 0 | 110 |
| 1 | 276 |
| 2 | 170 |

One sequence (`s1_cofhoney`) was outcome-homogeneous with `0` retained and `23` lost frames. It is therefore excluded from within-sequence retained-vs-lost AUC direction claims, as predeclared.

Informative sequences with both retained and lost outcomes: **24**.

## Primary held-out result

The predeclared direction was:

```text
retained >=2 frames should tend to have
higher area_ratio and higher min_area_frac than lost <2 frames
```

Observed whole-sequence direction agreement:

| Feature | Informative sequences agreeing | Fraction |
|---|---:|---:|
| `area_ratio` | 22 / 24 | **91.7%** |
| `min_area_frac` | 18 / 24 | **75.0%** |

This is the key held-out result.

`area_ratio` therefore shows substantially stronger cross-sequence directional stability than `min_area_frac` under this frozen evaluation.

## Heterogeneity is preserved

The held-out result is not universal.

Two informative sequences had `area_ratio` AUC below `0.5`:

```text
s2_cheese   AUC 0.36
s3_hotdog   AUC 0.2632
```

Six informative sequences had `min_area_frac` AUC below `0.5`:

```text
s1_cheese   0.3889
s2_cheese   0.14
s3_cheese   0.4545
s3_hotdog   0.2368
s3_peanut   0.4375
s4_hotdog   0.40625
```

These exceptions are not averaged away. They are evidence that neither feature is a complete causal or admission rule.

## Examples of strong directional agreement

Several sequences showed strong within-sequence ordering in the predeclared direction.

Examples:

```text
s2_tea
  area_ratio AUC    0.96875
  min_area_frac AUC 1.0

s3_tea
  area_ratio AUC    0.95833
  min_area_frac AUC 0.81667

s2_hotdog
  area_ratio AUC    0.85714
  min_area_frac AUC 0.68831

s4_peanut
  area_ratio AUC    0.71429
  min_area_frac AUC 0.84524
```

These values are descriptive observations for the pinned dataset/runtime, not threshold calibration.

## Truncation descriptor result

The predeclared border-touch descriptor was intentionally simple. In this dataset, many hand polygons touch or extend to image boundaries, so `truncated_hands` often saturates near `2` in both retained and lost groups.

Sequence-level retained/lost truncation means are inconsistent in direction. Therefore this descriptor does not currently add a stable standalone admission signal.

The conclusion is not that truncation is irrelevant. Rather, this specific binary border-touch/count descriptor is too coarse for a production-quality visibility model.

## Interpretation

The pooled 240-frame study previously suggested:

```text
visible-area balance
+ smaller-hand relative scale
↔ two candidates more often retained
```

The whole-sequence validation sharpens that claim:

```text
area_ratio
→ direction preserved in 22 / 24 informative sequences
→ strongest current natural observability feature family

min_area_frac
→ direction preserved in 18 / 24 informative sequences
→ useful secondary signal, but more sequence-dependent
```

This supports prioritizing **relative left/right visible-area balance** over a simple absolute smaller-hand-size rule when designing future observability research.

It still does not justify:

```text
area_ratio < X => reject
min_area_frac < Y => reject
```

No production `X` or `Y` is established.

## Evidence boundary

Supported:

1. candidate-loss behavior is widespread across 25 natural GTEA sequences;
2. `area_ratio` preserves the prior retained>lost direction in 91.7% of informative sequences;
3. `min_area_frac` preserves that direction in 75.0% of informative sequences;
4. meaningful sequence-level heterogeneity remains;
5. the current border-touch truncation descriptor is too coarse to act as a standalone gate.

Not supported:

- causality;
- production numeric thresholds;
- a universal observability score;
- generalization beyond this dataset/model/runtime;
- biometric identity continuity;
- natural retained-two association near-tie / ranking-swap distribution.

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.

## Next bounded node

The next highest-value natural-image node is no longer basic candidate retention/loss or simple size-balance validation. It is to screen the **170 retained-two natural frames** for scene-local association ambiguity:

```text
>=2 candidates retained
→ associate candidates to annotated left/right geometry with an explicit rule
→ measure best-vs-second association gap / ranking stability
→ stop if geometric association cannot be defended
```

This is a separate ambiguity family and must not be used to tune the observability findings above.
