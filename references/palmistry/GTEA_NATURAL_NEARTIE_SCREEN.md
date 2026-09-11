# GTEA Natural Retained-two Association Screen

Status: **REFERENCE-ONLY / NATURAL CAPTURE EXECUTED**

This Cold study screens natural GTEA frames where the pinned final Hand Landmarker returns exactly two candidates. It asks whether two different one-to-one assignments between detector candidates and the XML `Left hand` / `Right hand` annotations can become geometrically near-equivalent.

It does **not** define biometric identity, anatomical handedness from detector labels, or a production ambiguity threshold.

## Provenance

Research run:

```text
run 34627736409
head e9534fdbe55f5681c93a2de2aa439eccc396862e
job 103356811040
conclusion success
```

Pinned baseline:

```text
MediaPipe               1.0.1
Python                  3.12.14
Hand Landmarker SHA256  fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1
num_hands               4
detection/presence/tracking thresholds = 0.5 / 0.5 / 0.5
running_mode             IMAGE
```

Dataset archive SHA256 remains:

```text
a64c0fcff572414fa964c5b524e989ffe2e0a6023316bf4554a0f3e24d66fb8b
```

## Association rule

The XML annotation provides left/right hand polygons but no 21-landmark ground truth. Therefore the synthetic anchor-to-baseline metric is not reused as though it were natural-image ground truth.

For each detector candidate:

```text
candidate palm center = mean(L0 wrist, L5 index MCP, L17 little MCP)
```

For each XML hand object:

```text
XML target center = polygon centroid
```

For exactly two candidates, evaluate the two possible one-to-one assignments:

```text
A = c0→Left + c1→Right
B = c1→Left + c0→Right
```

Each assignment cost is the sum of candidate-center-to-XML-centroid distances normalized by image diagonal.

The lower-cost assignment is `best`; the other is `second`.

Also check whether each best-assigned candidate palm center lies inside its assigned XML polygon.

MediaPipe `handedness` is recorded only as detector output and is **not** used as anatomical left/right truth.

## Population

Exactly-two final-candidate frames:

```text
170
```

Geometric self-consistency of the best assignment:

| Best-assigned palm centers inside their XML polygons | Frames |
|---:|---:|
| 2 of 2 | **170** |
| 1 of 2 | 0 |
| 0 of 2 | 0 |

Thus the selected scene-local assignment is geometrically self-consistent for all 170 retained-two frames under this rule.

## Assignment-gap distribution

Observed best-vs-second assignment cost gap, normalized by image diagonal:

```text
minimum  = 0.1721273612
10th pct = 0.2751062265
median   = 0.4410073321
```

Smallest observed frame:

```text
s3_hotdog_0000000100
best cost     = 0.2818931505 diagonals
second cost   = 0.4540205117 diagonals
gap           = 0.1721273612 diagonals
relative gap  = 0.6106120737 × best cost
inside check  = 2 / 2
```

The second assignment is therefore still materially worse than the best assignment even at the observed minimum. This natural screen did **not** reproduce the controlled synthetic near-tie family where two candidate assignments become almost equally plausible.

No numeric `gap < X` production rule is inferred from these values.

## Important non-evidence: A/B flips

The workflow also counted 79 changes between labels `A` and `B` across adjacent retained samples.

This number is **not evidence of association ranking instability**.

`A` / `B` are defined using detector candidate list positions (`c0`, `c1`). Prior controlled evidence already shows candidate list index is not stable identity and can reorder across transforms/captures. Therefore:

```text
A ↔ B change
≠ left/right association swap
≠ target identity swap
≠ natural near-tie evidence
```

The 79 count is retained only as an instrumentation warning demonstrating why candidate-index lineage must not be promoted to identity.

## Handedness boundary

Some low-gap frames contain detector handedness outputs such as:

```text
[Left, Left]
[Right, Right]
```

while the geometry-based assignment remains fully consistent with both XML polygons. This further supports the existing rule that detector handedness output is not anatomical-side authority for the Palmistry observation contract.

## Interpretation

Supported:

1. 170 natural GTEA retained-two frames provide a broad natural association screen;
2. the centroid-based best assignment is geometrically self-consistent in 170 / 170 frames;
3. the observed best-vs-second assignment gap never approaches an obvious geometric near-tie under this metric;
4. candidate list reorder cannot be interpreted as identity or association instability;
5. detector handedness labels remain separate from anatomical left/right evidence.

Not supported:

- a claim that natural retained-two near-ties never occur;
- a production ambiguity cutoff;
- biometric or cross-frame identity continuity;
- generalization beyond GTEA / this pinned model/runtime;
- using candidate list index as a stable target identifier.

## Research consequence

Association ambiguity family B now has:

```text
controlled synthetic evidence: near-tie + ranking swap reproduced
natural GTEA screen: no near-tie reproduced under centroid-to-XML association
```

The correct conclusion is a **negative natural reproduction result**, not a threshold.

A higher-value next node is therefore to investigate transform / capture repeatability on natural or controlled single-target palms, or detector/runtime compatibility, rather than forcing a smaller gap from this GTEA set.

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
