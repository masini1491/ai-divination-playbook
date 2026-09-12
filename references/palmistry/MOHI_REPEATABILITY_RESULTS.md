# MOHI Multi-session Repeatability Results

Status: **REFERENCE-ONLY / BOUNDED EMPIRICAL RESULT**

This Cold note records the first predeclared permission-qualified contactless multi-session palm observation repeatability study.

## Frozen source/runtime

Source sample:

```text
10 dataset person IDs
3 sessions
5 captures / session
150 images total
```

Uploaded result artifact reported:

```text
sample ZIP SHA256:
6309f2390b0013858928c6c77344b4aa869edc8c0aeb9a61db93b73ae83feec2

MediaPipe 1.0.1
Hand Landmarker model SHA256:
fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1

IMAGE mode
num_hands = 2
min detection / presence / tracking = 0.5 / 0.5 / 0.5
source image = 3264 × 2448
working image = 1600 × 1200
```

No threshold lowering or post-hoc subject replacement was used.

## Runtime compatibility

All 150 images decoded and all 150 returned exactly one candidate:

```text
total = 150
usable exactly-one = 150
usable rate = 1.0
candidate count distribution:
1 candidate = 150
```

All observed handedness labels in the result artifact were `Right`; handedness remains detector metadata rather than anatomical authority.

This establishes a bounded positive domain-compatibility result for the MOHI mobile-phone full-hand capture setup under the frozen runtime.

It does not establish compatibility for all phone cameras or uncontrolled field images.

## Within-session repeatability

Across 300 within-session pairs:

| Metric | Mean | Median | P90 | P95 | Max |
|---|---:|---:|---:|---:|---:|
| normalized anchor mean drift | 0.05056 | 0.03891 | 0.10380 | 0.13307 | 0.18033 |
| normalized anchor max drift | 0.07119 | 0.05086 | 0.15345 | 0.20881 | 0.30479 |
| canonical-axis angle delta | 7.14° | 4.62° | 18.92° | 25.45° | 43.02° |
| width relative difference | 0.04024 | 0.02790 | 0.09261 | 0.12350 | 0.23141 |
| height relative difference | 0.04442 | 0.02677 | 0.11254 | 0.16440 | 0.27966 |
| canonical 21-landmark mean drift | 0.05882 | 0.05080 | 0.10203 | 0.12319 | 0.26042 |
| canonical 21-landmark max drift | 0.18100 | 0.15954 | 0.32619 | 0.42936 | 0.72217 |

## Cross-session repeatability

Across 750 cross-session pairs:

| Metric | Mean | Median | P90 | P95 | Max |
|---|---:|---:|---:|---:|---:|
| normalized anchor mean drift | 0.07216 | 0.06488 | 0.12837 | 0.14928 | 0.21806 |
| normalized anchor max drift | 0.10384 | 0.08723 | 0.19908 | 0.22719 | 0.37518 |
| canonical-axis angle delta | 10.26° | 7.52° | 22.01° | 27.70° | 40.06° |
| width relative difference | 0.05450 | 0.04346 | 0.11399 | 0.14302 | 0.26323 |
| height relative difference | 0.06188 | 0.04282 | 0.15650 | 0.19332 | 0.28583 |
| canonical 21-landmark mean drift | 0.07599 | 0.06994 | 0.12202 | 0.13983 | 0.27284 |
| canonical 21-landmark max drift | 0.23552 | 0.22060 | 0.36743 | 0.44644 | 0.74641 |

## Bounded interpretation

Every pooled cross-session mean is higher than the corresponding within-session mean.

Examples:

```text
anchor mean drift:
0.05056 within → 0.07216 cross
≈ 1.43×

canonical mean drift:
0.05882 within → 0.07599 cross
≈ 1.29×

axis angle delta:
7.14° within → 10.26° cross
≈ 1.44×
```

Within this bounded MOHI setup, independent captures are not perfectly invariant, and changing session adds measurable observation variation beyond same-session recapture variation.

This supports preserving `within-session` and `cross-session` as separate evidence classes rather than collapsing them into one repeatability number.

## Data-integrity caution

Several pooled metrics have an observed minimum of exactly `0.0`, including both within-session and cross-session summaries.

Because pair construction does not intentionally include self-pairs, an exact-zero result must not automatically be interpreted as exceptional repeatability.

Before using these distributions for any stronger calibration claim, perform a duplicate-source / duplicate-content audit on the 150-image sample using source-image hashes or equivalent provenance evidence.

Until that audit closes:

```text
150/150 positive runtime compatibility = established
cross-session > within-session pooled drift = established descriptively
exact-zero pairs = unresolved integrity signal
production tolerance / cutoff = not established
```

## Evidence boundary

This study establishes a bounded empirical repeatability distribution for one MOHI subset under one pinned MediaPipe runtime.

It does **not** establish:

- biometric identity continuity;
- device-to-device repeatability;
- long-term longitudinal palm stability;
- production Palmistry admission thresholds;
- detector-to-detector agreement;
- principal-line segmentation repeatability;
- anatomical handedness authority from detector labels.

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
