# MediaPipe Runtime Identity Probe — Static Review

Status: **REFERENCE-ONLY / PRE-EXECUTION STATIC REVIEW / NO COMPATIBILITY RESULT**

## Scope

本文件只檢查 `mediapipe_runtime_identity_probe.py` 是否符合 `MEDIAPIPE_RUNTIME_MODEL_COMPATIBILITY_PLAN.md` 與 `MEDIAPIPE_RUNTIME_COMPATIBILITY_CANDIDATE_LOCK.md` 的 Phase-0 identity requirements。

No baseline/comparison runtime execution is claimed here。

## Source identity

Probe Git blob SHA：

```text
6d06187deb457f5f74ae9359581abf959e121d7f
```

## Static review result

Source-level alignment：**PASS**。

### 1. Runtime identity coverage

Probe records：

- Python version / implementation；
- executable path；
- platform / machine / system / kernel release；
- `mediapipe.__version__`；
- installed distribution version；
- package location / distribution root；
- installed file count。

### 2. Installed-package provenance

Probe records dist-info evidence without assuming version-string identity is sufficient：

- `RECORD` path and SHA256；
- `METADATA` digest；
- `WHEEL` metadata digest；
- `direct_url.json` presence / digest if available。

This is intentionally an installed-package identity, not a claim that the original wheel bytes can always be reconstructed from an installed environment。

### 3. Dependency context

Probe records NumPy version and attempts OpenCV import/version without making OpenCV availability a prerequisite for the in-memory API smoke test。

### 4. Hand Landmarker model lock

Probe requires the existing pinned model SHA256：

```text
fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1
```

Model drift causes hard failure before the smoke test。

### 5. Same API options

The disposable smoke test constructs the Task API with：

```text
running mode = IMAGE
num_hands = 2
min detection = 0.5
min presence  = 0.5
min tracking  = 0.5
```

matching the frozen MOHI baseline options。

### 6. Explicit pixel-array path

The smoke fixture is created as an in-memory `256×256×3 uint8` RGB array and passed through：

```text
mp.Image(image_format=SRGB, data=array)
```

No filename-based decode is used by MediaPipe in this probe。

The input pixel SHA256 is recorded so baseline and comparison runtime smoke tests can verify identical bytes。

### 7. Candidate count is non-authoritative

The synthetic fixture may legitimately return zero or another candidate count；the probe labels it descriptive only。

Therefore the Phase-0 smoke test checks API/model execution, not hand-domain accuracy。

### 8. No MOHI inference

The output boundary explicitly records：

```text
mohi_inference_executed = false
compatibility_result = false
production_threshold = false
production_upgrade_policy = false
```

## Runtime-dependent items still open

Static review cannot establish：

1. which environment reproduces the historical 1.0.1 baseline；
2. exact installed-package RECORD identity under that environment；
3. successful 1.0.0 environment installation；
4. exact acquired 1.0.0 wheel SHA；
5. same model loading under both runtimes；
6. identical synthetic pixel digest / successful Task API smoke on both；
7. any MOHI cross-runtime result。

## Next allowed action

Run this probe separately under：

```text
historical / reconstructed MediaPipe 1.0.1 baseline environment
comparison MediaPipe 1.0.0 environment
```

and freeze both JSON artifacts before MOHI runtime-comparison execution。

## Boundary

This review does not establish runtime compatibility, a production upgrade policy, or any landmark-agreement result。

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**。
