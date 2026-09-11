# GTEA Sequence-held-out Validation Plan

Status: **REFERENCE-ONLY / PREDECLARED RESEARCH PLAN**

This Cold plan freezes the next natural-capture validation question before inspecting held-out results. It does not define a production Palmistry gate, threshold, routing rule, or method capability.

## Research question

Do the natural two-hand observability signals seen in the prior bounded GTEA study preserve their **direction/order across whole held-out sequences**, rather than only across temporally correlated frames pooled together?

Candidate feature family carried forward from prior evidence:

- `area_ratio`: smaller annotated hand polygon area / larger annotated hand polygon area;
- `min_area_frac`: smaller annotated hand polygon area / image area;
- explicit truncation / visibility descriptors derived from source annotations.

Features that are not promoted as primary candidates from the prior study include centroid separation, whole-frame brightness, global blur, and simple hand proximity.

## Unit of hold-out

A GTEA sequence is the atomic hold-out unit. Frames from a held-out sequence must not contribute to fitting or choosing a score for that same sequence.

No random frame-level train/test split is sufficient because adjacent annotation samples are temporally correlated.

## Outcome

For every direct-XML two-hand frame, the pinned final MediaPipe Hand Landmarker outcome is reduced only to:

```text
retained = final candidate count >= 2
lost     = final candidate count < 2
```

The source annotation and detector observation remain separate evidence layers.

## Evaluation

Primary evaluation is sequence-level direction consistency, not one pooled p-value.

For each sequence with both retained and lost outcomes, report at minimum:

- eligible frame count;
- retained / lost counts;
- median `area_ratio` in retained vs lost;
- median `min_area_frac` in retained vs lost;
- Mann-Whitney probability-form AUC for each feature;
- whether each feature's direction agrees with the prior pooled observation (`retained > lost`);
- truncation descriptor summaries when available.

Also report the number/proportion of informative sequences whose direction agrees. Do not convert this into a production cutoff.

## Stop / interpretation rules

- If ordering is inconsistent across sequences, record heterogeneity; do not average it away into a universal rule.
- If a sequence has only retained or only lost outcomes, report it as outcome-homogeneous and exclude it from within-sequence AUC direction claims.
- Exploratory p-values, if reported, are descriptive and not threshold authority.
- Do not tune numeric cutoffs on held-out sequences.
- Do not lower MediaPipe thresholds to increase candidate count.
- Do not treat detector candidate count as biometric identity continuity.

## Pinned detector baseline

Keep the prior research baseline unless a separate compatibility study is explicitly opened:

```text
MediaPipe               1.0.1
Python                  3.12.x
Hand Landmarker SHA256  fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1
num_hands               4
detection/presence/tracking thresholds = 0.5 / 0.5 / 0.5
running_mode             IMAGE
```

## Independent parallel screen

Natural retained-two frames may also be screened for association near-ties, but that is a separate outcome family. A near-tie result must not be folded into the observability score or used to tune this held-out analysis.

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
