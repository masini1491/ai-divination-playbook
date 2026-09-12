# MediaPipe Runtime-only MOHI Runner — Static Review

Status: **REFERENCE-ONLY / PRE-EXECUTION STATIC REVIEW / NO MOHI CROSS-RUNTIME RESULT**

## Reviewed artifact

```text
references/palmistry/mediapipe_runtime_mohi_compare_runner.py
Git blob = b4cd51d0b7c793ab5107e6b84047521d40fdee0d
```

Review target is the exact runner pinned by `MEDIAPIPE_RUNTIME_MOHI_COMPARISON_IMPLEMENTATION_LOCK.md`。

## Source-level contract review

### PASS — provenance guards

Runner hard-locks：

```text
MOHI ZIP SHA256
Hand Landmarker model SHA256
both frozen Phase-0 identity artifact SHA256 values
Python 3.12.14
NumPy 2.5.3
OpenCV 5.0.0
MediaPipe 1.0.1 vs 1.0.0
150 manifest entries
148 unique source-byte representatives
known duplicate groups
```

It also compares the two runtime environments' non-MediaPipe `pip list --format=freeze` output after removing only the `mediapipe==...` line。

### PASS — one shared decode / pixel path

Controller alone decodes the JPEG source bytes and creates one contiguous `uint8 RGB` array per manifest entry。Both MediaPipe workers load the same prepared `.npy` array and verify the controller-recorded pixel SHA256 before inference。

This prevents runtime-specific JPEG filename decode / EXIF handling from being misclassified as detector geometry drift。

### PASS — EXIF boundary

EXIF orientation is read only as diagnostic metadata。The detector input contract does not ask either MediaPipe version to decode the JPEG file itself。

### PASS — detector options

Both workers use exactly：

```text
IMAGE
num_hands = 2
0.5 / 0.5 / 0.5 detection-presence-tracking
```

No result-dependent threshold adjustment exists in the runner。

### PASS — candidate-index boundary

Cross-runtime association does not declare list index to be target identity：

- `1 vs 1` is direct；
- `2 vs 2` evaluates both complete assignments using mean L0/L5/L17 raw-normalized anchor distance；
- best / second / gap are retained；
- numeric tie fails closed；
- candidate-count mismatch fails closed for fine geometry。

Worker indices remain stored only as local output bookkeeping。

### PASS — canonical normalization correction

The runner does **not** reuse the historical MOHI runner's `norm(L5-L17)` width denominator。It recomputes the current canonical contract：orthogonalized L5-L17 axis and projected palm width。

### PASS — duplicate and primary accounting

The runner preserves：

- all 150 manifest entries for execution accounting；
- 148 first-in-manifest unique source-byte representatives for primary distribution；
- duplicate groups separately for deterministic reproduction checks。

It does not silently drop candidate-count disagreements or unresolved associations。

### PASS — no compatibility threshold

No code path converts observed deltas into `compatible / incompatible` via a numeric cutoff。The output remains raw evidence + descriptive summaries。

## Static-review caveats

### Handedness remains metadata only

The runner stores MediaPipe handedness labels/scores and label agreement。These fields must not later be promoted into anatomical-side authority。

### `2 vs 2` best assignment is geometric association, not identity truth

A positive best-vs-second gap only selects the lower-cost scene-local association under the frozen anchor cost。It does not prove biological identity across candidates。The gap must remain visible in interpretation。

### Candidate-count mismatch intentionally suppresses fine geometry

For `1 vs 2`, `2 vs 1`, `0 vs 1`, etc., the runner preserves the transition but does not force a partial target match。This is conservative by design for first-round runtime portability evidence。

### Synthetic Phase-0 candidate count is not reused as a quality claim

Phase-0's disposable synthetic fixture returned zero candidates under both runtimes。The formal MOHI runner uses Phase-0 only as runtime/API provenance, not as evidence of hand-detection quality。

## What this review does NOT claim

This is source-level inspection only。At this point there is **no claim** that the exact runner has passed：

```text
python -m py_compile
CLI import / --help preflight
150-entry MediaPipe 1.0.1 execution
150-entry MediaPipe 1.0.0 execution
result JSON schema/accounting checks
raw result SHA freeze
```

Those are the next execution gates。

## Pre-execution decision

Source-level contract alignment：**PASS**。

Next allowed action：

1. `py_compile` exact runner；
2. basic CLI import preflight；
3. execute the full controlled 150-entry study under the already-frozen reconstructed environments；
4. inspect only execution accounting；
5. SHA256-freeze the raw result JSON；
6. record a result-freeze document；
7. only then inspect substantive cross-runtime metrics。

## Boundary

Static-review PASS is not an empirical runtime compatibility result and does not alter Palmistry routing/production authority。
