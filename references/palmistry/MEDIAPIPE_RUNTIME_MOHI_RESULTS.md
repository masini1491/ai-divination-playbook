# MediaPipe Runtime-only MOHI — Substantive Results

Status: **REFERENCE-ONLY / BOUNDED RUNTIME-PORTABILITY EVIDENCE / NO PRODUCTION THRESHOLD**

## Purpose

本文件解讀已先行 freeze 的 controlled MediaPipe `1.0.1` vs `1.0.0` MOHI runtime-only result。

Formal raw artifact：

```text
/home/user/palm-detector-study/results/MOHI_mediapipe_runtime_101_vs_100.json
SHA256 = bcee8126b3c5ce4b01a7dcf921edac627961351423121e6a975c2462142ade9d
```

Formal runner：

```text
references/palmistry/mediapipe_runtime_mohi_compare_runner.py
Git blob = b4cd51d0b7c793ab5107e6b84047521d40fdee0d
```

本結果只回答：在兩個 controlled reconstructed WSL/Linux Python `3.12.14` environment 中，固定相同 non-MediaPipe packages、同一 Hand Landmarker model bytes、同一 controller-decoded RGB pixel bytes、同一 detector options 時，MediaPipe Tasks runtime package `1.0.1` 與 `1.0.0` 是否產生不同的 2D hand-landmark / canonical-palm observation geometry。

它不回答 model artifact version portability，也不是 production upgrade policy。

## Frozen execution accounting

Formal execution：

```text
image entries                              = 150
primary unique source-byte representatives = 148
duplicate groups                           = 2
MediaPipe 1.0.1 inferences                 = 150
MediaPipe 1.0.0 inferences                 = 150
stop                                       = false
```

Substantive inspection前重新驗證 raw-result SHA256，結果 PASS。

## Primary 148 unique-source result

### Candidate-count behavior

```text
entries                          = 148
candidate-count equal            = 148 / 148
candidate-count agreement rate   = 1.0
candidate transition             = 1 -> 1 for all 148
geometry resolved                = 148 / 148
geometry unresolved              = 0
association mode                 = single-single for all 148
```

因此此 bounded sample 沒有出現：

- `0 -> 1` / `1 -> 0` detection transition；
- `1 -> 2` / `2 -> 1` count mismatch；
- two-by-two association ambiguity；
- unresolved cross-runtime target association。

### 2D raw landmark geometry

所有 primary entries 的下列 descriptive distributions 全部為 exact zero：

```text
raw_21_mean
raw_21_median
raw_21_max
anchor_mean       # L0/L5/L17
anchor_max
```

對每一 metric：

```text
n      = 148
mean   = 0
median = 0
p90    = 0
p95    = 0
min    = 0
max    = 0
std    = 0
```

在 runner 保存的 detector-normalized 2D x/y coordinates 中，`1.0.1` 與 `1.0.0` 對這 148 個 unique-source representatives 沒有觀察到任何數值差異。

### Canonical palm geometry

使用 current projected-width canonical contract 重新計算後，下列 metrics 也全部 exact zero：

```text
axis_angle_deg
width_rel
height_rel
canonical_mean
canonical_max
```

每一 metric 同樣為：

```text
n      = 148
mean   = 0
median = 0
p90    = 0
p95    = 0
min    = 0
max    = 0
std    = 0
```

因此本次 runtime package change 沒有在此 sample 中產生可見的 canonical-frame drift。

### Handedness metadata label

```text
resolved entries              = 148
label agreement entries       = 148
label agreement rate          = 1.0
```

沒有任何 primary entry 發生 handedness label disagreement。

此結果只支持 label behavior 在本 bounded comparison 中一致；handedness 仍不是 anatomical-side authority。

## Secondary all-150 result

保留 duplicate manifest entries 的 secondary distribution 也完全一致：

```text
candidate-count agreement = 150 / 150
candidate transition      = 1 -> 1 for all 150
geometry resolved         = 150 / 150
handedness label agreement= 150 / 150
```

所有 raw 2D / anchor / axis / width / height / canonical metrics 仍為 exact zero across mean / median / p90 / p95 / min / max / std。

因此 duplicate manifest entries 沒有改變 substantive conclusion；primary authority仍是 148 unique-source representatives。

## Per-person / per-session heterogeneity

所有 `P001`–`P010`、S1–S3 primary groups 的：

```text
raw_21_mean
anchor_mean
axis_angle_deg
canonical_mean
```

group mean 均為 `0.0`。

P001/S3 與 P005/S3 因已知 duplicate-byte grouping 各只有 4 個 primary representatives；其餘 person/session groups各 5 個。沒有任何 subgroup 顯示 runtime-dependent 2D geometry drift。

## Duplicate determinism

兩個已知 byte-identical source groups：

```text
P001/S3/03 == P001/S3/05
P005/S1/01 == P005/S3/02
```

在 MediaPipe `1.0.1` 與 `1.0.0` 各自內部均得到：

```text
candidate_count_equal  = true
candidates_exact_equal = true
input_pixel_sha_equal  = true
all_exact              = true
```

這再次支持 runner / runtime 在同 bytes、同 prepared pixels下具 deterministic reproduction；duplicate entries不得當作 independent recapture evidence。

## Worst-case screen

因所有 tracked 2D / canonical metrics 都為 exact zero，`canonical_mean`、`raw_21_mean`、`axis_angle_deg` 的排序沒有真正 worst-case heterogeneity；top entries只是 stable sort 下的任意 zero-valued entries。

因此不能把 top-10 list解讀為較差案例。

## Interpretation

本 study最直接的 bounded結論是：

> 在本次 controlled reconstructed environment、固定同一 Hand Landmarker model artifact、相同 prepared RGB pixel bytes 與相同 detector options 下，MediaPipe Tasks runtime package `1.0.1` 與 `1.0.0` 對 MOHI 148 個 unique-source representatives 的 tracked 2D landmark geometry、L0/L5/L17 anchor geometry、projected-width canonical geometry、candidate count及 handedness label 產生完全一致的觀察結果。

這比「差異很小」更強：對 runner 實際量測的 2D/canonical quantities，observed delta distribution 是 exact zero。

但這仍是 bounded empirical evidence，不是版本家族的一般定理。

## Important scope limits

### 1. Runtime package only

本研究固定同一 Hand Landmarker model SHA256：

```text
fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1
```

所以沒有測試：

- 不同 Hand Landmarker model artifact；
- model revision / task-bundle revision；
- different model quantization / architecture。

`runtime compatibility` 與 `model artifact compatibility` 必須分開。

### 2. Controlled reconstructed environment

比較的是兩個 purpose-built WSL/Linux Python `3.12.14` environments；不是歷史 MOHI execution runtime的 forensic replay。

歷史 artifact只證明當時記錄 `mediapipe = 1.0.1`，不能反推出 original Python / OS identity。

### 3. Tracked geometry is 2D x/y

Formal comparison的 geometry / canonical metrics使用 x/y。Worker也保存 normalized z，但本輪 aggregate substantive metrics沒有把 z 納入 compatibility distribution。

因此不得把「2D geometry exact-equal」擴張成「所有 MediaPipe candidate fields bitwise identical across runtime versions」。

### 4. Handedness score magnitude不是 authority

本輪確認 handedness label一致；未把 score magnitude差異變成 anatomy claim或 admission rule。

### 5. Sample scope

MOHI仍是 bounded repeated-capture sample；它不是 arbitrary scene、multi-hand field capture、device-to-device或 long-term longitudinal portability benchmark。

## Inspection wrapper anomaly

Substantive extraction在所有 intended sections與下列 marker都已印出後：

```text
SUBSTANTIVE_INSPECTION_EXTRACTION = COMPLETE
NO COMPATIBILITY CUTOFF WAS APPLIED
```

因 PowerShell/Bash here-document terminator 被當成 Python source留下 literal `PY`，最後額外出現：

```text
NameError: name 'PY' is not defined
```

這是 inspection wrapper termination anomaly，不是 frozen result artifact failure。所有上列 substantive values已在該 exception之前輸出；raw artifact SHA也在 inspection開始前再次驗證 PASS。沒有重跑 inference，也沒有修改 frozen JSON。

## Decision

MediaPipe `1.0.1` vs `1.0.0` **runtime-only 2D geometry portability subnode can be boundedly closed for this pinned model / environment contract**。

仍 open：

- Hand Landmarker model-artifact version portability；
- z-coordinate / ancillary field exactness若未來 observation contract需要；
- broader runtime families / future MediaPipe versions；
- device / OS / capture-condition portability；
- production upgrade policy。

No compatibility cutoff was created or needed to characterize this exact-zero result。

## Boundary

本結果不建立 production routing、future-version guarantee、anatomical truth、biometric identity、Palmistry interpretation validity或 general MediaPipe compatibility certification。

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**。
