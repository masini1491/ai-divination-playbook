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

本 lock 不代表 historical MOHI installed wheel identity 已完成 reconciliation，也不代表 1.0.0 已安裝或執行。

## Public package evidence

PyPI release history currently exposes：

```text
mediapipe 1.0.1
released 2026-08-14

mediapipe 1.0.0
released 2026-07-27
```

Both releases provide `py3-none-manylinux_2_28_x86_64` wheels, matching the chosen x86_64 Linux/WSL reconstruction platform family。

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

This is not a blocker for a wheel-to-wheel runtime comparison as long as wheel identities and raw-frame behavior are explicit。

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

## Post-scan provenance amendment

A read-only local provenance scan found：

```text
frozen MOHI artifact:
mediapipe = 1.0.1
model SHA256 = resolved
source ZIP SHA256 = resolved
result JSON SHA256 = a4fbe499b6070a75e179c07de91cc3eef52d63392164d8288eb9065f5054bac0

current Windows Python 3.13.15:
mediapipe 1.0.1 present with dist-info / RECORD

current WSL Conda envs:
no mediapipe package present
```

The MOHI artifact does **not** store Python/platform/wheel identity, so the current Windows install cannot be attributed as the historical MOHI executor merely because its MediaPipe version matches。

Likewise, separate GitHub Actions runs that recorded Python 3.12.14 / MediaPipe 1.0.1 / OpenCV 5.0.0 cannot be retroactively assigned to the MOHI artifact。

Full boundary is recorded in [`MEDIAPIPE_RUNTIME_PROVENANCE_RECONCILIATION.md`](MEDIAPIPE_RUNTIME_PROVENANCE_RECONCILIATION.md)。

Therefore Phase 0 is now defined as a **controlled reconstructed wheel-to-wheel comparison identity gate** rather than discovery of a presumed surviving historical local baseline environment。

## Corrected Phase 0

Before MOHI cross-runtime execution, create two new isolated environments with identical non-MediaPipe contracts。

Preferred reconstruction candidate：

```text
platform family = x86_64 Linux / WSL
Python          = 3.12.14, if reproducibly obtainable
baseline wheel  = locked MediaPipe 1.0.1 manylinux wheel
comparison wheel= locked MediaPipe 1.0.0 manylinux wheel
```

The exact Python patch and all non-MediaPipe dependency versions must be frozen before result inspection。

Each environment must report：

```text
python version
platform / architecture
mediapipe.__version__
importlib.metadata distribution version
installed package location
RECORD / dist-info identity
exact wheel SHA256
numpy version
opencv version
Task API import path
```

A disposable same-pixel-array smoke test must pass under both environments before MOHI is admitted。

## Stop rules

Stop before cross-runtime inference if：

- exact reconstruction identities cannot be durable-recorded；
- acquired 1.0.1 or 1.0.0 wheel hash differs from the locked PyPI SHA；
- same pinned Hand Landmarker model bytes cannot load under both runtimes；
- detector options cannot be held constant；
- raw input pixel frame cannot be held constant；
- comparison requires changing model bytes or threshold values；
- package import succeeds only after an unrecorded dependency substitution；
- the study is described as an exact replay of the historical MOHI host environment despite missing historical Python/platform provenance。

## Next allowed action

The next step is a **controlled reconstruction Phase-0 identity probe only**。

It should not yet execute the 150-entry MOHI study。

The probe should：

1. create two fresh isolated environments with the same Python and dependency contract；
2. install the exact locked 1.0.1 / 1.0.0 wheel bytes separately；
3. record complete environment identities；
4. load the same Hand Landmarker model in both；
5. run a disposable non-MOHI pixel-array smoke test；
6. freeze both runtime identities before any MOHI comparison result。

## Boundary

This candidate lock does not establish：

- that 1.0.0 and 1.0.1 are compatible；
- that their landmarks agree；
- exact reproduction of the historical MOHI host environment；
- a production upgrade policy；
- a compatibility threshold；
- anatomical truth；
- Palmistry prediction validity。

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**。
