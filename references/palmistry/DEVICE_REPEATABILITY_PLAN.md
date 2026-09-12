# Palm Device-to-Device Repeatability Plan

Status: **REFERENCE-ONLY / PREDECLARED / EXECUTION BLOCKED BY DATA-USE GATE**

This Cold plan freezes the next Palmistry observation research node after the completed MOHI multi-session study: **device-to-device repeatability**.

The target is not biometric verification. Dataset class / palm labels are used only as corpus-provided grouping keys.

## Why this node is next

MOHI established bounded same-device mobile-phone multi-session repeatability under one capture setup. It did **not** establish how much the same palm observation geometry changes when the capture device changes.

The next question is therefore:

> Under a fixed pinned full-hand landmark runtime, how much additional observation variation is introduced by changing smartphone device while holding dataset palm class constant?

## Candidate correction: MPW-180 is not the primary paired-device corpus

`bingolo/PalmWildNet` / MPW-180 remains relevant for mobile-device diversity, but the repository currently exposes only README / figures / code-license surface while its promised dataset DOI/link and `DATASET_LICENSE` artifact are absent.

The README describes:

```text
180 subjects
multiple smartphones
flash / non-flash
indoor / outdoor
720 videos
thousands of ROI images
```

However, this design is participant-owned-device diversity rather than a clearly documented same-palm-across-multiple-smartphones paired acquisition protocol.

Therefore MPW-180 should not be treated as the primary corpus for estimating smartphone-to-smartphone repeatability unless released metadata later proves repeated same-palm capture across devices.

## Primary structural candidate: MPD-v2

The public Mobile Palmprint project describes a mobile palmprint database with repeated acquisition on two smartphone devices and two collection periods. The current X-Palm benchmark documentation also represents MPD-v2 filenames as:

```text
{subject}_{session}_{device}_{hand}_{iteration}.jpg
```

This is structurally valuable because device and session are explicit factors rather than confounded into one label.

The intended first device-repeatability design would require, for the same dataset palm class:

```text
same device / same session
same device / cross session
cross device / same session
cross device / cross session
```

This lets device effect be compared against the already-known session effect instead of collapsing both together.

### Current gate

The public project/download surface is visible, but this Playbook has not yet captured a sufficiently explicit dataset-level reuse license or equivalent permission statement authorizing automated research reuse.

Decision:

```text
STRUCTURAL FIT = HIGH
DEVICE FACTOR = EXPLICIT
SESSION FACTOR = EXPLICIT
DATA-USE / LICENSE GATE = UNRESOLVED
EXECUTION = BLOCKED
```

## Secondary structural candidate: XJTU-UP

Public literature and project references describe XJTU-UP as an unconstrained palmprint dataset captured using multiple smartphones and lighting conditions. Recent X-Palm benchmark documentation describes the dataset layout as device-separated trees, including iPhone and Huawei capture branches.

This makes XJTU-UP useful for independent confirmation of device sensitivity.

However, the current Playbook evidence has not yet closed a sufficiently explicit dataset-level data-use permission statement.

Decision:

```text
MULTI-DEVICE STRUCTURE = STRONG
CONTACTLESS FULL-HAND DOMAIN = STRONG
DATA-USE / LICENSE GATE = UNRESOLVED
EXECUTION = BLOCKED
```

## Cross-domain reference: X-Palm

X-Palm is a 2026 paired scanner ↔ smartphone palmprint dataset with smartphone images collected across 80+ device models from 10+ brands. It is distributed for non-commercial academic use through a signed EULA workflow.

X-Palm is useful for **scanner-to-smartphone domain shift** and broad smartphone diversity, but it is not the preferred first smartphone-to-smartphone repeatability corpus because participant-owned phones do not by themselves establish that the same palm was captured across multiple phone models.

Decision:

```text
PAIRED CROSS-DOMAIN = YES
BROAD SMARTPHONE DIVERSITY = YES
SAME-PALM MULTI-PHONE PAIRING = NOT ESTABLISHED BY CURRENT EVIDENCE
ACCESS = EULA-CONTROLLED
```

## Frozen execution plan if MPD-v2 data-use gate closes

Do not tune this after observing results.

### Frozen first-study unit

Use the first 10 dataset palm classes, ordered by dataset-provided identifier, that satisfy all required device × session cells.

Require for every selected palm class:

```text
2 devices
2 sessions / periods
5 captures per device-session cell
```

Target:

```text
10 palm classes × 2 devices × 2 sessions × 5 captures
= 200 image entries
```

If the official corpus actually exposes 10 captures per cell, use deterministic indices 1..5 for the bounded first study rather than expanding after outcomes are seen.

Do not replace failed palm classes after inference.

### Frozen runtime

Reuse the MOHI runtime exactly:

```text
MediaPipe 1.0.1
Hand Landmarker model SHA256:
fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1

running_mode = IMAGE
num_hands = 2
min_hand_detection_confidence = 0.5
min_hand_presence_confidence = 0.5
min_tracking_confidence = 0.5
max working dimension = 1600
```

Require exactly one usable hand candidate. Zero or multiple candidates fail closed. Do not lower thresholds.

### Frozen geometry

Reuse the existing L0 / L5 / L17 canonical basis and raw-image inverse mapping.

Detector handedness remains metadata only.

### Frozen comparison classes

For each palm class separately:

```text
A. within-device / within-session
B. within-device / cross-session
C. cross-device / within-session
D. cross-device / cross-session
```

Do not pool before per-palm distributions are available.

### Minimum outputs

Report:

- acquisition / decode success;
- candidate-count distribution by device and session;
- exactly-one usable rate by device/session/palm class;
- source duplicate audit before interpreting zero drift;
- normalized L0/L5/L17 anchor drift;
- canonical-axis angle drift;
- canonical width / height relative drift;
- canonical landmark drift;
- per-palm heterogeneity;
- A/B/C/D descriptive distributions separately;
- explicit failures and truncation / ambiguity conditions.

### Analysis order

```text
permission + acquisition integrity
→ duplicate audit
→ detector usability
→ per-palm within-device / within-session
→ per-palm within-device / cross-session
→ per-palm cross-device / within-session
→ per-palm cross-device / cross-session
→ pooled descriptive summaries
→ qualitative interpretation
```

## Directional research questions

The study is descriptive, not a hypothesis test, but the predeclared questions are:

1. Is cross-device / same-session drift larger than same-device / same-session drift?
2. Is cross-device / cross-session drift larger than same-device / cross-session drift?
3. How large is device-induced drift relative to the MOHI session effect already observed?
4. Are some palm classes disproportionately device-sensitive?
5. Does detector usability itself differ materially by device?

No production cutoff is derived from these questions.

## Stop rules

Stop before inference if:

- dataset reuse permission remains unresolved;
- same-palm cross-device grouping cannot be established from dataset metadata alone;
- device / session labels require identity inference;
- source files are only ROI crops unsuitable for the frozen full-hand runtime and no official full-hand source is available;
- device metadata is incomplete or ambiguous;
- an unplanned preprocessing rule would be required.

## Prohibitions

Do **not**:

- treat public download availability as permission authority;
- infer real-world identity;
- train biometric authentication models for this node;
- lower detector thresholds;
- derive production tolerances;
- replace failed classes after inference;
- generalize scanner-to-phone results into phone-to-phone repeatability;
- treat broad device diversity as same-palm paired multi-device evidence;
- commit third-party source images into this repository.

## Evidence boundary

If executed successfully, this study may establish a bounded empirical smartphone device-repeatability distribution for the chosen corpus and pinned runtime.

It still will not establish:

- universal smartphone invariance;
- long-term longitudinal stability;
- detector-to-detector agreement;
- principal-line segmentation repeatability;
- biometric identity continuity;
- production Palmistry thresholds.

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
