# MOHI Multi-session Repeatability Results

Status: **REFERENCE-ONLY / BOUNDED EMPIRICAL RESULT / INTEGRITY AUDIT CLOSED**

This Cold note records the first predeclared permission-qualified contactless multi-session palm observation repeatability study.

## Frozen source/runtime

Source sample:

```text
10 dataset person IDs
3 sessions
5 captures / session
150 image entries total
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

All 150 image entries decoded and all 150 returned exactly one candidate:

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

The original pooled result contains 300 within-session pairs:

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

The original pooled result contains 750 cross-session pairs:

| Metric | Mean | Median | P90 | P95 | Max |
|---|---:|---:|---:|---:|---:|
| normalized anchor mean drift | 0.07216 | 0.06488 | 0.12837 | 0.14928 | 0.21806 |
| normalized anchor max drift | 0.10384 | 0.08723 | 0.19908 | 0.22719 | 0.37518 |
| canonical-axis angle delta | 10.26° | 7.52° | 22.01° | 27.70° | 40.06° |
| width relative difference | 0.05450 | 0.04346 | 0.11399 | 0.14302 | 0.26323 |
| height relative difference | 0.06188 | 0.04282 | 0.15650 | 0.19332 | 0.28583 |
| canonical 21-landmark mean drift | 0.07599 | 0.06994 | 0.12202 | 0.13983 | 0.27284 |
| canonical 21-landmark max drift | 0.23552 | 0.22060 | 0.36743 | 0.44644 | 0.74641 |

## Integrity audit closure

A deterministic follow-up audit compared the 150 manifest rows with the ZIP contents and source-image SHA256 values.

Observed:

```text
manifest rows = 150
ZIP image entries = 150
manifest hash mismatches = 0

duplicate SHA groups = 2
duplicate image entries = 4
```

The two duplicate-content groups are:

```text
P005/S1/01.jpg == P005/S3/02.jpg
SHA256 = 8a40753c427c5b8441e92c6e8070cea6610455c428c7a5ac4fed32d777246fc7

P001/S3/03.jpg == P001/S3/05.jpg
SHA256 = a76b6cbc7fec8d90f454dca7c3e217a942d57b9adf4247ca1eac8184d2378f18
```

The audit found exactly two byte-identical detector-geometry groups, and both correspond exactly to those duplicate source-image groups:

```text
P005/S1/01 ↔ P005/S3/02
same_source_bytes = true
cross-session duplicate pair

P001/S3/03 ↔ P001/S3/05
same_source_bytes = true
within-session duplicate pair
```

Therefore the observed exact-zero geometry is explained by duplicate source bytes rather than an unexplained detector coincidence.

The original pooled tables above intentionally remain the raw experiment output. Their exact-zero minima must not be interpreted as independent-capture perfect invariance.

For pooled means, the duplicate effect is bounded and too small to change the qualitative comparison:

```text
within-session:
1 duplicate zero pair among 300
removing it multiplies pooled means by 300 / 299
≈ +0.334%

cross-session:
1 duplicate zero pair among 750
removing it multiplies pooled means by 750 / 749
≈ +0.134%
```

Because every cross-session pooled mean was already higher than its corresponding within-session mean, excluding the two duplicate-induced zero pairs does not reverse that ordering.

A future publication-grade reanalysis may regenerate complete duplicate-excluded median / percentile tables from pair-level records. This is not required to close the present integrity question and must not be replaced by inferred percentiles from pooled summaries.

## Bounded interpretation

Every original pooled cross-session mean is higher than the corresponding within-session mean.

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

Within this bounded MOHI setup, non-duplicate independent captures are not perfectly invariant, and changing session adds measurable observation variation beyond same-session recapture variation.

This supports preserving `within-session` and `cross-session` as separate evidence classes rather than collapsing them into one repeatability number.

The integrity audit changes the interpretation of the exact-zero minima, not the direction of the pooled repeatability result.

## Evidence boundary

This study establishes a bounded empirical repeatability distribution for one MOHI subset under one pinned MediaPipe runtime, with the duplicate-content caveat now explicitly characterized.

It does **not** establish:

- biometric identity continuity;
- device-to-device repeatability;
- long-term longitudinal palm stability;
- production Palmistry admission thresholds;
- detector-to-detector agreement;
- principal-line segmentation repeatability;
- anatomical handedness authority from detector labels.

The sample contains two duplicate-content pairs and therefore must not be described as 150 unique independent source photographs.

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
