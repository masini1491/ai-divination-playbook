# MediaPipe Runtime Compatibility — Candidate Lock

Status: **REFERENCE-ONLY / PRE-EXECUTION CANDIDATE LOCK / NO PORTABILITY RESULT YET**

## Purpose

本文件是 `MEDIAPIPE_RUNTIME_MODEL_COMPATIBILITY_PLAN.md` 的 runtime-only comparison candidate lock。

目標是把第一輪比較收斂成：

```text
baseline runtime family = MediaPipe Python 1.0.1
comparison runtime      = MediaPipe Python 1.0.0
same Hand Landmarker model bytes
same source image bytes
same explicit raw-frame contract
same detector options / thresholds
```

本 lock 不代表 baseline installed wheel identity 已完成 reconciliation，也不代表 1.0.0 已安裝或執行。

## Public package evidence

PyPI release history currently exposes：

```text
mediapipe 1.0.1
released 2026-08-14

mediapipe 1.0.0
released 2026-07-27
```

Both releases provide `py3-none-manylinux_2_28_x86_64` wheels, matching the existing x86_64 WSL/Linux research platform family。

### Candidate exact wheel identities

Baseline public-package candidate：

```text
filename
mediapipe-1.0.1-py3-none-manylinux_2_28_x86_64.whl

PyPI SHA256
121522251afc3c135e4b7b0c341dd5e050ad1ec87631127484f3c389ae385044
```

Comparison public-package candidate：

```text
filename
mediapipe-1.0.0-py3-none-manylinux_2_28_x86_64.whl

PyPI SHA256
07a449446bf888a8a2787dbf6fc1a33da4c47977313deec64d13c35bff41f6d2
```

These public hashes identify candidate wheel artifacts only。

The existing installed baseline environment must still prove whether its installed `mediapipe 1.0.1` came from the exact public wheel above；version-string equality alone is insufficient。

## GitHub / package-version reconciliation caveat

The public `google-ai-edge/mediapipe` repository has a GitHub release tag：

```text
v1.0.0
```

whose release note reports an internal MediaPipe version bump to `0.10.36` and Python Task API EXIF-orientation support。

A GitHub release lookup for：

```text
v1.0.1
```

currently does not resolve to a release tag。

Therefore the first study must preserve：

```text
PyPI distribution identity
!= automatically resolved GitHub tag / commit identity
```

For baseline package `1.0.1`：

```text
upstream_revision = unresolved
```

until a defensible package-to-repository mapping is established。

This is not a blocker for a wheel-to-wheel runtime comparison as long as wheel / installed-package identities and raw-frame behavior are explicit。

## Why 1.0.0 is selected

`1.0.0` is chosen as the first comparison target because it is：

1. the immediately adjacent public PyPI release before 1.0.1；
2. available as an exact x86_64 manylinux wheel；
3. close enough to test maintenance portability without jumping across a larger historical API boundary；
4. not a nightly / mutable latest target。

This selection is made before any MOHI cross-runtime result inspection。

## Runtime-only hold-fixed contract

The first empirical comparison must hold fixed：

```text
Hand Landmarker model SHA256
fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1

running mode = IMAGE
num_hands = 2
min detection = 0.5
min presence  = 0.5
min tracking  = 0.5

same MOHI source bytes
same selected source accounting
same duplicate handling
same target association policy
same canonical L0/L5/L17 implementation
```

No threshold adjustment is allowed because one runtime detects more / fewer candidates。

## Raw-frame / EXIF gate

Because upstream release notes explicitly mention EXIF-orientation behavior changes, runtime comparison must not feed each version an opaque filename and assume identical pixels。

Preferred runtime-only contract：

```text
source JPEG bytes
→ one explicit decode policy
→ one explicit RGB pixel array
→ construct MediaPipe image from the same pixel array
→ run both runtimes
```

The study must record：

- source file SHA256；
- decoded `[h,w]`；
- EXIF orientation presence；
- explicit decoder / orientation policy；
- pixel-array digest before MediaPipe；
- whether either runtime silently transforms the supplied pixel array。

If the two runtimes cannot consume the same explicit pixel frame without hidden reorientation, stop and classify as `raw_frame_policy_mismatch` before landmark comparison。

## Phase 0 still required locally

Before MOHI execution, the existing baseline environment must report at least：

```text
python version
platform / architecture
mediapipe.__version__
importlib.metadata distribution version
installed package location
RECORD / dist-info identity
wheel/source provenance if available
numpy version
opencv version
Task API import path
```

The 1.0.0 comparison environment must separately record the same fields plus the exact acquired wheel SHA256。

## Stop rules

Stop before cross-runtime inference if：

- baseline `1.0.1` identity cannot be distinguished from a mutable/unresolved install source；
- acquired 1.0.0 wheel hash differs from the locked PyPI SHA；
- same pinned Hand Landmarker model bytes cannot load under both runtimes；
- detector options cannot be held constant；
- raw input pixel frame cannot be held constant；
- comparison requires changing model bytes or threshold values；
- package import succeeds only after an unrecorded dependency substitution。

## Next allowed action

The next step is a **local runtime identity probe only**。

It should not yet execute the 150-entry MOHI study。

The probe should：

1. inspect the existing 1.0.1 environment；
2. create or inspect a separate 1.0.0 environment；
3. verify exact wheel / package identity；
4. load the same Hand Landmarker model in both；
5. run a disposable non-MOHI pixel-array smoke test；
6. freeze the runtime identities before any MOHI comparison result。

## Boundary

This candidate lock does not establish：

- that 1.0.0 and 1.0.1 are compatible；
- that their landmarks agree；
- a production upgrade policy；
- a compatibility threshold；
- anatomical truth；
- Palmistry prediction validity。

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**。
