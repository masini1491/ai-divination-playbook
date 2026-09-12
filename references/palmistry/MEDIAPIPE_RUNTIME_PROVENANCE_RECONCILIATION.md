# MediaPipe Runtime Provenance Reconciliation

Status: **REFERENCE-ONLY / PHASE-0 PROVENANCE RECONCILED WITH LIMITATION / NO PORTABILITY RESULT**

## Purpose

本文件記錄 `MEDIAPIPE_RUNTIME_MODEL_COMPATIBILITY_PLAN.md` / `MEDIAPIPE_RUNTIME_COMPATIBILITY_CANDIDATE_LOCK.md` 在第一次 local Phase-0 probe 前後發現的 baseline provenance 問題。

核心結論：

> 現有 MOHI repeatability artifact 能固定 `mediapipe = 1.0.1`、source ZIP SHA256 與 Hand Landmarker model SHA256，但**不能從 artifact 本身證明當次 MOHI execution 的 Python / OS / installed-wheel identity**。

因此不得把其他研究 run 的 Python / platform metadata retroactively 指派給 MOHI。

## Frozen MOHI artifact observed in local provenance scan

Operator-provided read-only scan observed：

```text
file:
C:\Users\user\Documents\X\MOHI_repeatability_results.json

status:
REFERENCE-ONLY / MOHI PINNED REPEATABILITY

mediapipe recorded:
1.0.1

Hand Landmarker model SHA256:
fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1

MOHI sample ZIP SHA256:
6309f2390b0013858928c6c77344b4aa869edc8c0aeb9a61db93b73ae83feec2

image entries:
150

result JSON SHA256:
a4fbe499b6070a75e179c07de91cc3eef52d63392164d8288eb9065f5054bac0
```

這些欄位是 artifact 自身或 artifact file hash 可直接保存的 provenance。

## What the MOHI artifact does not establish

`mohi_mediapipe_repeatability.py` 的 frozen result schema 保存：

```text
mediapipe version string
model SHA256
ZIP SHA256
image-level detector / geometry results
```

但沒有 durable-record：

```text
Python version
OS / platform
architecture
OpenCV version
NumPy version
installed wheel filename
RECORD / dist-info digest
pip source channel
upstream repository revision
```

所以 historical MOHI execution 的完整 runtime identity目前為：

```text
mediapipe version family = 1.0.1
model bytes              = resolved
source bytes             = resolved
Python identity          = unresolved
platform identity        = unresolved
installed wheel identity = unresolved
```

## Local environment scan

Read-only local scan observed one current Windows Python installation that can import MediaPipe：

```text
Python executable:
C:\Users\user\AppData\Local\Programs\Python\Python313\python.exe

Python:
3.13.15

mediapipe.__version__:
1.0.1

importlib.metadata distribution version:
1.0.1

site-packages:
C:\Users\user\AppData\Local\Programs\Python\Python313\Lib\site-packages

RECORD present:
C:\Users\user\AppData\Local\Programs\Python\Python313\Lib\site-packages\mediapipe-1.0.1.dist-info\RECORD
```

Current WSL/Conda environments observed：

```text
base         Python 3.14.7   mediapipe absent
palm-detector Python 3.9.18  mediapipe absent
palm-lines    Python 3.11.16 mediapipe absent
```

This local scan proves only **current environment availability**。

It does **not** prove that the Windows Python 3.13.15 installation generated the frozen MOHI artifact；the frozen MOHI artifact lacks the required Python/platform fields for that attribution。

## Existing GitHub Actions evidence must stay separate

Other Palmistry research runs independently recorded：

```text
Python 3.12.14
MediaPipe 1.0.1
OpenCV 5.0.0
```

Those GitHub Actions runs provide a reproducible public runtime family for other bounded studies。

They do **not** prove that the local MOHI artifact was generated under Python 3.12.14 or GitHub Actions Linux。

Therefore future documents must distinguish：

```text
historical MOHI artifact provenance
!= other GitHub Actions MediaPipe provenance
!= newly reconstructed controlled compatibility environment
```

## Corrected Phase-0 interpretation

The originally attempted Phase-0 workflow assumed that Conda env `palm-lines` was the historical MediaPipe 1.0.1 baseline environment。

The read-only scan falsified that assumption：`palm-lines` currently contains no MediaPipe package。

This is an **environment-assumption failure before experiment execution**, not a runtime-compatibility result。

No MOHI cross-runtime inference was executed during either failed Phase-0 attempt。

## Controlled reconstruction path

The runtime-only study remains scientifically answerable, but it must be framed as a **controlled reconstructed wheel-to-wheel comparison** rather than exact replay of the historical MOHI process environment。

Preferred controlled reconstruction：

```text
platform family: x86_64 Linux / WSL
Python:          3.12.x, pinned identically in both envs
baseline:        MediaPipe 1.0.1 exact locked public wheel
comparison:      MediaPipe 1.0.0 exact locked public wheel
model:           same SHA256-pinned Hand Landmarker bytes
source:          same SHA256-pinned MOHI ZIP bytes
pixel input:     one explicit decoder policy -> same RGB pixel-array bytes
options:         identical IMAGE / num_hands / confidence settings
```

The exact Python patch version and non-MediaPipe dependency set must be frozen before any MOHI comparison result is inspected。

Because existing GitHub Actions evidence reproducibly used Python 3.12.14 with MediaPipe 1.0.1, `Python 3.12.14` is a reasonable **reconstruction candidate**；it is not retroactive proof of the historical MOHI environment。

## Consequence for interpretation

A successful future 1.0.1 vs 1.0.0 controlled study may support：

> 在同一個新建、可重現的 Python/platform/dependency contract 下，只替換 MediaPipe wheel 時，兩個 pinned runtime 對同一 MOHI pixel arrays 的 observation geometry 差異分布。

It may **not** support：

- exact reproduction of the original MOHI host environment；
- proof that current Windows Python 3.13.15 generated the frozen MOHI artifact；
- proof that historical MOHI ran on Python 3.12.14；
- production upgrade policy；
- a universal compatibility cutoff。

## Next allowed action

Before any 150-entry MOHI cross-runtime inference：

1. create two new isolated reconstruction environments；
2. pin the same Python patch version and same non-MediaPipe dependencies；
3. install exact locked `1.0.1` and `1.0.0` wheel bytes separately；
4. run the runtime identity probe in both；
5. freeze both Phase-0 identity artifacts；
6. only then admit the 150-entry runtime-only comparison。

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**。
