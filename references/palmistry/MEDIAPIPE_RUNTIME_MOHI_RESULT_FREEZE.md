# MediaPipe Runtime-only MOHI — Formal Result Freeze

Status: **REFERENCE-ONLY / FORMAL RAW RESULT FROZEN / SUBSTANTIVE METRICS NOT YET INTERPRETED**

## Purpose

本文件只凍結 controlled MediaPipe `1.0.1` vs `1.0.0` MOHI runtime-only formal execution 的 raw result identity、execution accounting 與 preflight gates。

此文件**不解讀** cross-runtime geometry、candidate-count agreement、handedness、canonical-coordinate delta 或 compatibility。

## Frozen experiment contract

Formal runner：

```text
references/palmistry/mediapipe_runtime_mohi_compare_runner.py
Git blob = b4cd51d0b7c793ab5107e6b84047521d40fdee0d
```

Frozen Phase-0 identities：

```text
MediaPipe 1.0.1 identity JSON SHA256
cc31a3d5120663f36b5f6ae47206d53465a38cdf861dd8d3b0f6f46cc023f357

MediaPipe 1.0.0 identity JSON SHA256
e1fb2836891b863bbe8fd5edb311c00482cd7e6c1d950d3666bf2bed330d7485
```

The Phase-0 contract already fixed：

```text
Python = 3.12.14
NumPy = 2.5.3
OpenCV = 5.0.0
same non-MediaPipe package set
same Hand Landmarker model bytes
same system GL/EGL/GLES prerequisite set
```

The formal MOHI runner additionally fixes：

```text
same source ZIP bytes
same explicit controller-side JPEG decode
same full-frame resize policy
same contiguous RGB pixel-array bytes per entry
same Hand Landmarker model SHA256
same IMAGE mode
same num_hands = 2
same 0.5 / 0.5 / 0.5 thresholds
same candidate-association policy
same projected-width canonical palm basis
```

## Preflight gates

Operator-provided formal execution output recorded：

```text
RUNNER SOURCE GATE = PASS
PHASE0 ARTIFACT GATE = PASS
REQUIRED FILE GATE = PASS
PY_COMPILE = PASS
CLI_PREFLIGHT = PASS
```

No runner source or Phase-0 artifact drift was observed before execution。

## Execution accounting

Formal execution completed both runtime passes：

```text
image_entries = 150
primary_unique_source_representatives = 148
duplicate_group_count = 2
baseline_inferences = 150
comparison_inferences = 150
stop = false

manifest_rows = 150
persons = 10
unique_source_bytes = 148
integrity_duplicate_groups = 2

EXECUTION_ACCOUNTING_CHECK = PASS
```

This preserves the known MOHI accounting boundary：150 manifest entries, 148 unique source-byte representatives, and two byte-identical duplicate groups。

## Frozen raw result artifact

```text
/home/user/palm-detector-study/results/MOHI_mediapipe_runtime_101_vs_100.json
SHA256 = bcee8126b3c5ce4b01a7dcf921edac627961351423121e6a975c2462142ade9d
```

The SHA256 was printed immediately after execution-accounting assertions and before substantive summary inspection。

Formal execution log：

```text
/home/user/palm-detector-study/results/MOHI_mediapipe_runtime_101_vs_100.log
SHA256 = 1336a803f95d0c879bb0281bc916e58be2684a110472a232854b6193786d9f43
```

The log is operational provenance only；the raw JSON remains the formal result artifact for subsequent analysis。

## Inspection boundary at freeze time

At freeze time the operator-side script explicitly stopped after：

1. completing both 150-entry runtime passes；
2. checking only execution/source accounting；
3. hashing the raw JSON；
4. hashing the execution log。

The script then printed：

```text
SUBSTANTIVE SUMMARY HAS NOT BEEN INSPECTED
```

Therefore this document deliberately does not record or characterize：

- candidate-count agreement rate；
- candidate transition distribution；
- raw 21-landmark deltas；
- L0/L5/L17 anchor deltas；
- canonical-coordinate deltas；
- axis-angle / width / height deltas；
- handedness-label agreement；
- duplicate deterministic reproduction；
- any worst-case entry；
- any compatibility threshold or pass/fail conclusion。

Those belong to a subsequent substantive-inspection step against this exact frozen SHA256。

## Next allowed action

Read only the already-frozen raw result with SHA256 verification first, then inspect the precomputed descriptive summaries and targeted per-entry diagnostics required to explain heterogeneity。

No rerun is required unless：

- raw-result SHA no longer matches；
- accounting fields fail to reproduce；
- a later audit finds an implementation defect in the frozen runner。

Substantive interpretation must remain descriptive and bounded. No numeric compatibility cutoff may be invented post hoc。

## Boundary

This freeze proves formal execution completion and artifact identity only。It does **not** establish：

- MediaPipe `1.0.0` and `1.0.1` geometric equivalence；
- upgrade safety；
- future-version portability；
- anatomical truth；
- biometric identity；
- Palmistry interpretation validity。

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**。
