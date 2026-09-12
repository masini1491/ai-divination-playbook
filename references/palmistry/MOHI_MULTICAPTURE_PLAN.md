# MOHI Multi-capture Repeatability Plan

Status: **REFERENCE-ONLY / PREDECLARED EXPERIMENT PLAN**

This Cold plan freezes the first permission-qualified contactless multi-session corpus experiment for Palmistry observation repeatability.

It must be committed **before** any MOHI landmark/repeatability result is inspected.

## Why MOHI is qualified

Official Mutah University material states that the hand-image databases are freely available for **research and teaching purposes**; other uses require consultation with the authors.

MOHI specifically uses mobile-phone-camera hand images rather than a scanner/contact sensor.

The associated paper describes:

```text
200 persons
right hand only
3 sessions
5 images / person / session
15 MOHI images / person
3,000 MOHI images total
mobile-phone camera
3264 × 2448 original resolution
session interval ≈ 3 days
white-paper background
intentional variation in rotation, scale, and lighting
```

The official download page divides each session into four 50-person groups.

This closes the current research-node gates simultaneously:

```text
permission-qualified
+ contactless / full-hand domain
+ repeated independent captures
+ explicit multi-session structure
+ dataset-provided subject/session/image naming
```

## Research question

For a bounded deterministic subset of MOHI right-hand images, under the existing pinned MediaPipe Hand Landmarker runtime:

> how stable is the canonical L0/L5/L17 palm observation geometry across independent captures within a session versus across sessions?

This is **not** biometric identity verification.

Dataset person IDs are used only as corpus-provided grouping labels.

## Frozen acquisition unit

Do not acquire the full 3,000-image corpus first.

Start with:

```text
Session 1 / Group 1
Session 2 / Group 1
Session 3 / Group 1
```

These correspond to the same 50-person group according to the official download organization.

If archive contents confirm stable person IDs across the three groups, continue with the deterministic subset below.

If person-ID correspondence is not preserved, stop and record the mismatch before inference.

## Frozen first-study subset

Select the first 10 corpus person IDs present in all three acquired session groups, ordered numerically by dataset person ID.

For each selected person:

```text
S1: images 1..5
S2: images 1..5
S3: images 1..5
```

Target first study:

```text
10 persons × 3 sessions × 5 images = 150 images
```

Do not replace failed persons after inference.

Missing/corrupt source files are reported as acquisition failures, not silently resampled.

## Frozen runtime

Reuse the same pinned research runtime already established by Palmistry evidence:

```text
MediaPipe 1.0.1
Hand Landmarker model SHA256:
fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1

running_mode = IMAGE
num_hands = 2
min_hand_detection_confidence = 0.5
min_hand_presence_confidence = 0.5
min_tracking_confidence = 0.5
```

Use the existing max-dimension preprocessing convention unless the source acquisition check shows that MOHI requires a different already-canonical adapter. Do not introduce a new resize rule after inspecting outcomes.

Require exactly one usable target hand per source image for canonical repeatability analysis.

If zero or multiple candidates remain, fail closed for that image.

Do not lower detector thresholds.

## Geometry

For usable images:

1. retain raw-image dimensions and preprocessing transform provenance;
2. map landmarks back to raw-image geometry;
3. use L0 / L5 / L17 to build the existing canonical palm basis;
4. preserve handedness output only as detector metadata, not anatomical identity authority;
5. compute observation differences within dataset person group.

## Frozen comparisons

For each person separately, report:

### Within-session

All pairwise repeatability among the 5 captures inside each session:

```text
S1 within
S2 within
S3 within
```

### Cross-session

Compare independent captures across:

```text
S1 ↔ S2
S2 ↔ S3
S1 ↔ S3
```

Do not collapse all comparisons into one pooled number before per-person and per-session distributions are available.

## Minimum outputs

Report at minimum:

- source acquisition success/failure;
- image decode success/failure;
- candidate-count distribution by session;
- exactly-one usable rate by session and person;
- L0/L5/L17 anchor drift in normalized raw-image geometry;
- canonical-axis angle drift;
- canonical width/height relative drift;
- canonical grid/landmark drift using the existing research metric owner;
- within-session distributions;
- cross-session distributions;
- per-person heterogeneity;
- explicit failures caused by truncation, rotation, target ambiguity, landmark collapse, or other observed conditions.

## Analysis order

Preserve this order:

```text
acquisition integrity
→ detector usability
→ per-person within-session distributions
→ per-person cross-session distributions
→ pooled descriptive summaries
→ only then qualitative interpretation
```

No production cutoff is derived from this corpus.

## Stop rules

Stop before repeatability inference if:

- the official session/group downloads cannot be reproduced;
- session groups do not preserve a usable common person-ID grouping;
- files are not the full-hand MOHI images described by the official source;
- provenance or data-use authority materially conflicts with the official research/teaching statement.

Stop expansion beyond the first 150 images if:

- the pinned runtime produces insufficient usable full-hand landmarks for a meaningful repeated-capture distribution;
- an unplanned preprocessing change would be required to obtain results;
- source naming/grouping requires identity inference beyond dataset-provided fields.

## Prohibitions

Do **not**:

- train or evaluate a biometric authentication model;
- infer real-world identity from person IDs;
- use gender or age metadata for this Palmistry research question;
- lower thresholds after failures;
- tune a production admission threshold;
- replace failed subjects with easier ones;
- commit third-party MOHI source images into this Playbook;
- generalize results to device-to-device repeatability unless device metadata actually supports that claim.

## Evidence boundary

A successful first study may establish a bounded empirical distribution for **independent multi-capture and approximately three-day multi-session observation repeatability under this MOHI capture setup**.

It still will not establish:

- general smartphone-to-smartphone device repeatability;
- long-term longitudinal stability;
- detector-to-detector agreement;
- principal-line segmentation repeatability;
- biometric identity continuity;
- production Palmistry thresholds.

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
