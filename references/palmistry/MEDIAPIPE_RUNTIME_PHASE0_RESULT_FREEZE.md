# MediaPipe Runtime Phase-0 — Controlled Reconstruction Result Freeze

Status: **REFERENCE-ONLY / CONTROLLED PHASE-0 IDENTITY FROZEN / NO MOHI PORTABILITY RESULT YET**

## Purpose

本文件只凍結 controlled reconstructed MediaPipe `1.0.1` vs `1.0.0` Phase-0 identity + synthetic smoke 結果。

它不是 MOHI cross-runtime landmark comparison 結果，也不建立 compatibility threshold。

## Execution boundary

Phase-0 使用兩個新建且互相隔離的 WSL/Linux environment：

```text
baseline env
/home/user/palm-detector-study/runtime-compat/recon-mp101

comparison env
/home/user/palm-detector-study/runtime-compat/recon-mp100
```

兩者共同固定：

```text
Python = 3.12.14
NumPy = 2.5.3
OpenCV = 5.0.0
same non-MediaPipe pip package list
same Hand Landmarker model bytes
same synthetic RGB pixel bytes
```

唯一刻意改變的 Python package：

```text
baseline   MediaPipe = 1.0.1
comparison MediaPipe = 1.0.0
```

## OS shared-library prerequisite

第一次 controlled attempt 因缺少 `libGLESv2.so.2` 在 native library load 前停止。之後依既有 GitHub Actions research environment 的 prerequisite family 補齊 `libegl1`、`libgl1`、`libgles2`。

operator output顯示 Ubuntu Jammy 上：

```text
libegl1 = 1.4.0-1 (already installed)
libgl1  = 1.4.0-1 (already installed)
libgles2= 1.4.0-1 (newly installed)
```

兩個 reconstructed env 對 `libGLESv2.so.2`、`libEGL.so.1`、`libGL.so.1` 的 `ctypes.CDLL` load 均 PASS。這個 system dependency set 是兩個 runtime 共用，不是版本專屬調參。

## Locked wheel identities

```text
MediaPipe 1.0.1 wheel SHA256
121522251afc3c135e4b7b0c341dd5e050ad1ec87631127484f3c389ae385044

MediaPipe 1.0.0 wheel SHA256
07a449446bf888a8a2787dbf6fc1a33da4c47977313deec64d13c35bff41f6d2
```

Acquired wheel hashes matched the predeclared candidate lock exactly。

## Probe / model identity

```text
references/palmistry/mediapipe_runtime_identity_probe.py
Git blob = 6d06187deb457f5f74ae9359581abf959e121d7f

Hand Landmarker model SHA256
= fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1
```

Both were verified before smoke execution。

## Frozen Phase-0 artifacts

```text
baseline 1.0.1
/home/user/palm-detector-study/runtime-compat/recon-mp101-identity.json
SHA256 = cc31a3d5120663f36b5f6ae47206d53465a38cdf861dd8d3b0f6f46cc023f357

comparison 1.0.0
/home/user/palm-detector-study/runtime-compat/recon-mp100-identity.json
SHA256 = e1fb2836891b863bbe8fd5edb311c00482cd7e6c1d950d3666bf2bed330d7485
```

These hashes were printed immediately after both probes completed and before any MOHI inference。

## Baseline identity summary

```text
Python                = 3.12.14
mediapipe distribution= 1.0.1
mediapipe.__version__ = 1.0.1
NumPy                 = 2.5.3
OpenCV                = 5.0.0
RECORD SHA256          = e27ddc42df14e14f60d5ba49a8ac6059182aa09411c09620842592fbc56acb7a
METADATA SHA256        = 5ea0016039f80d34f1d4d262efe79535ae0c2519168181518faaffca6942a7e2
WHEEL metadata SHA256  = 8328a548a58008c5d799be3d36190b0e17f1c4d60a4de26445a88135d6b540ae
direct_url metadata present = true
```

## Comparison identity summary

```text
Python                = 3.12.14
mediapipe distribution= 1.0.0
mediapipe.__version__ = 1.0.0
NumPy                 = 2.5.3
OpenCV                = 5.0.0
RECORD SHA256          = f9839414f9463581c07bf30fd22af7df7a2a94c44e78a6204352054aacd9d827
METADATA SHA256        = 3311b8b43b6e1b1291e7e699d7fb03f21a591c331f99166d2b3b6229439daa79
WHEEL metadata SHA256  = 8328a548a58008c5d799be3d36190b0e17f1c4d60a4de26445a88135d6b540ae
direct_url metadata present = true
```

`WHEEL metadata SHA256`相同只代表 dist-info `WHEEL` metadata file內容相同；不能替代完整 `.whl` artifact SHA256。

## Synthetic smoke identity

Both runtimes consumed the same synthetic in-memory RGB pixel bytes：

```text
input pixel SHA256
= 71328cb5976d0b73da4f9c27b186aec7b8dbb2978ef4122b561b8c5dd70d226d
```

Both used the same Hand Landmarker model SHA256。Smoke outcome：

```text
MediaPipe 1.0.1 API smoke = PASS
MediaPipe 1.0.0 API smoke = PASS
candidate_count 1.0.1 = 0
candidate_count 1.0.0 = 0
```

The disposable synthetic fixture is not intended to contain a valid palm target；`candidate_count = 0`不解讀為 detection quality evidence。此 smoke 只證明兩 runtime 能建立相同 in-memory image、載入相同 model、執行相同 Task API path 並正常返回。

## Cross-artifact assertions

Operator execution explicitly passed：

```text
SAME PYTHON = PASS
SAME NUMPY = PASS
SAME OPENCV = PASS
SAME MODEL BYTES = PASS
SAME SYNTHETIC PIXEL BYTES = PASS
BOTH API SMOKES = PASS
NO MOHI INFERENCE = PASS
```

Non-MediaPipe pip package list equality also passed before the probes。

## Phase-0 decision

Controlled Phase 0 is **admitted** for the next research stage：

> Build a dedicated runtime-only MOHI comparison runner that executes both frozen reconstructed runtime identities against the same explicit decoded RGB frame contract and the same Hand Landmarker model bytes/options。

This admission does **not** mean `1.0.0` and `1.0.1` are geometrically compatible；it means the controlled runtime-only experiment can now be executed without known Python-package, model-byte, or synthetic-input confounding。

## Next-stage requirements

- run all 150 image entries under both runtimes；
- primary distribution remains 148 unique source-byte representatives；
- preserve byte-identical duplicate groups for deterministic checks；
- use one explicit decoder / RGB pixel-array path shared across runtimes；
- keep `IMAGE`, `num_hands=2`, thresholds `0.5 / 0.5 / 0.5`；
- do not use candidate list index as identity；
- preserve unresolved associations rather than dropping them；
- freeze raw result artifact SHA256 before interpretation；
- no automatic compatibility cutoff。

## Boundary

This Phase-0 freeze does not establish runtime geometric agreement、production upgrade safety、future-version compatibility、anatomical truth、biometric identity或 Palmistry interpretation validity。

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**。
