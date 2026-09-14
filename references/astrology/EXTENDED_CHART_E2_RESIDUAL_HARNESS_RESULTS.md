# Astrology Extended Chart Facts — Phase E2 Residual Harness Results

Status: **REFERENCE-ONLY / RESEARCH / NUMERICAL ORACLE COLLECTION STILL PENDING**

Baseline: `masini1491/ai-divination-playbook@3a3090a8f63651f4654e81c6b0e719b095d6b1bd`

This result file records the next Phase E2 step after the oracle environment contract.

## 1. Objective

Prepare a fail-closed comparison harness for the planned matrix:

```text
5 objects × 4 fixture times = 20 comparable Swiss / Horizons observations
```

Objects:

```text
Chiron
Ceres
Pallas
Juno
Vesta
```

The harness must calculate residuals without inventing an admission tolerance.

## 2. Important execution discovery

The current execution environment already contains a Kerykeion Swiss ephemeris file at:

```text
/opt/pyvenv/lib/python3.13/site-packages/kerykeion/sweph/seas_18.se1
```

It was independently fingerprinted before use.

Observed local file:

```text
size_bytes:    223002
git_blob_sha:  5de13e59a926abf8c27fa2adf0e440bd1b2c4e7d
sha256:        5fd9c2aa1654e37c09a6aeb558076e795409b7dc4bd948ebc0faa7d4a7686b5b
header:        SWISSEPH 1
underlying JPL: DE431
creation/copyright generation: 2023 family
```

Pinned E2 oracle contract requires:

```text
size_bytes:    223004
git_blob_sha:  8f900cab7e557e4c41f758a6bf3a3c3967e7e3db
header:        SWISSEPH 3
underlying JPL: DE441
source revision: aloistr/swisseph@91339e55d2351f32548d8a8d5bca6aa93b4f6da7
```

Therefore the local Kerykeion file is **not** an admissible substitute for the pinned Phase E2 Swiss oracle.

Classification:

```text
DATA_IDENTITY_MISMATCH
```

Research rule applied correctly:

> A numerically usable ephemeris file with the wrong pinned identity must fail closed rather than silently become the oracle.

No real residuals in this result file were generated from the mismatched DE431 file.

## 3. Additional provenance confirmation

Pinned `theriftlab/immanuel-python@eba98099b7724598064113ffa1322e78dc4bccf6` contains:

```text
immanuel/resources/ephemeris/seas_18.se1
blob_sha = 8f900cab7e557e4c41f758a6bf3a3c3967e7e3db
size     = 223004
```

This is the same binary identity already pinned from the official Swiss Ephemeris repository.

That gives a second repository-level provenance observation for the exact desired data file, but repository binary content is still not committed into this Playbook.

## 4. Residual harness

Added:

```text
compare_extended_chart_e2_residuals.py
extended_chart_e2_residual_synthetic.json
```

The comparison harness validates:

1. manifest schema and REFERENCE_ONLY authority;
2. tolerance remains `NOT_DEFINED_PENDING_RESIDUAL_COLLECTION`;
3. exact 5 × 4 object / fixture matrix identity;
4. no duplicate object / fixture pairs;
5. exact UTC identity from the manifest;
6. normalized longitude domain `[0, 360)`;
7. finite numeric longitude / speed values;
8. measured-oracle Swiss provenance against pinned revision / binary blob / size;
9. measured-oracle Horizons provenance against the pinned observer contract;
10. shortest circular longitude separation;
11. absolute speed difference;
12. per-object mean / max residual summaries.

## 5. Synthetic execution

The synthetic dataset is explicitly labelled:

```text
dataset_kind = synthetic_test
notes = Synthetic arithmetic-only data. Not astronomical observations.
```

It exists only to validate residual arithmetic and fail-closed behavior.

Local execution result:

```text
status: SYNTHETIC_HARNESS_PASS
sample_count: 20
tolerance_status: NOT_DEFINED_PENDING_RESIDUAL_COLLECTION
```

The fixture deliberately includes this wrap case:

```text
Swiss longitude:    359.9995°
Horizons longitude:   0.0005°
```

Correct circular residual:

```text
~0.001°
```

not approximately `359.999°`.

This validates the wrap-safe longitude comparison logic.

## 6. Fail-closed regression probes

Three negative probes were executed locally.

### 6.1 Missing observation

Removed one row from the 20-row matrix.

Result:

```text
return code: 2
status: FAIL_CLOSED
error: incomplete observation matrix; missing 1 pairs
```

### 6.2 Duplicate observation

Duplicated `E2-F01 / Chiron`.

Result:

```text
return code: 2
status: FAIL_CLOSED
error: duplicate fixture/object pair: ('E2-F01', 'Chiron')
```

### 6.3 Wrong measured Swiss provenance

Changed the measured-oracle Swiss binary identity to an invalid SHA.

Result:

```text
return code: 2
status: FAIL_CLOSED
error: Swiss provenance mismatch: ephemeris_blob_sha
```

These probes establish that the harness will not summarize an incomplete, duplicated, or wrong-oracle dataset as valid E2 residual evidence.

## 7. External numerical collection status

### Swiss

Exact desired binary identity is known and available in pinned external repositories, but the current execution environment cannot directly obtain that binary through its normal network path.

A different Swiss binary is locally available but was correctly rejected as a data-identity mismatch.

### NASA/JPL Horizons

The Horizons API contract remains pinned in `extended_chart_e2_oracle_manifest.json`.

Dynamic API navigation is externally reachable in principle, but the current generic web retrieval layer does not expose arbitrary parameterized Horizons responses as a reusable raw fixture source in this run.

Therefore no synthetic values are being mislabeled as Horizons observations.

## 8. Current E2 status

```text
object identities                 RESOLVED
Swiss object mappings             RESOLVED
main asteroid data dependency     RESOLVED
pinned binary identity            RESOLVED
license boundary                  RESOLVED
independent oracle contract       RESOLVED
comparison harness                IMPLEMENTED / SYNTHETIC PASS
matrix completeness validation    PASS
circular longitude arithmetic     PASS
measured provenance validation    PASS / fail-closed regression
real Swiss observations           PENDING
real Horizons observations        PENDING
real 20-row residual matrix       PENDING
research tolerance                NOT DEFINED
production admission              NOT GRANTED
```

## 9. Exit gate unchanged

Phase E2 does **not** become complete because the harness passes synthetic data.

Completion still requires:

```text
exact pinned Swiss binary execution
+ exact Horizons observer queries
+ 20 real paired observations
+ residual characterization
+ holdout validation before a tolerance proposal
```

Until then the correct status is:

**E2 PARTIAL / EXECUTION HARNESS READY / REAL RESIDUAL COLLECTION PENDING**
