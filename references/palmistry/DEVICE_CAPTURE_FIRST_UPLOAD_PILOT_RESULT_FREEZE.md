# Device / Capture First-upload Pilot — Raw Result Freeze

Status: **REFERENCE-ONLY / RAW RESULT FROZEN BEFORE SUBSTANTIVE GEOMETRY INSPECTION / NO PRODUCTION AUTHORITY**

## Purpose

本文件固定第一批 two-device / repeated-reposition 左手 pilot 的正式 raw inference artifact identity、execution accounting 與已知 wrapper discrepancy。建立本文件時，不解讀 Pixel 5 與 Pixel 10 Pro 的 geometry distribution，也不建立任何 production cutoff。

Authority chain：

```text
DEVICE_CAPTURE_REPEATABILITY_FIRST_UPLOAD_ADMISSION.md
→ DEVICE_CAPTURE_REPEATABILITY_FIRST_UPLOAD_SOURCE_FREEZE.md
→ DEVICE_CAPTURE_FIRST_UPLOAD_PILOT_IMPLEMENTATION_LOCK.md
→ DEVICE_CAPTURE_FIRST_UPLOAD_PILOT_RUNNER_STATIC_REVIEW.md
→ 本 raw-result freeze
```

## Execution source identity

Formal execution observed：

```text
repository HEAD = b3a1f83a96201a2d4d3e1befe67b23b3f0531d68
runner Git blob = 4e2cdc757333753b133e568fae84f7c339712a06
```

Pre-execution gates reported：

```text
frozen ZIP gate = PASS
WSL ZIP path gate = PASS
runner source gate = PASS
MediaPipe version = 1.0.1
py_compile = PASS
model SHA gate = PASS
```

## Frozen source / model provenance

```text
source archive SHA256 = b5854b545f3ff0193b51cc02278efdbca25e1e3d1147a8559c7bb042ff2b7ca0
Hand Landmarker model SHA256 = fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1
MediaPipe Tasks runtime = 1.0.1
```

Anatomical-side authority remains：

```text
anatomical_side = left
side_authority = explicit_bodily_self_report
```

Detector handedness does not replace this authority.

## Formal execution accounting

The runner completed the 30-image inference pass and wrote the raw result artifact. Runner stdout reported：

```text
source_entries = 30
unique_source_sha256 = 30
duplicate_groups = 0

device_counts:
D1 = 15
D2 = 15

candidate_distribution:
1 candidate = 30

usable_entries = 30
unresolved_entries = 0

within_device_pairs_expected = 210
cross_device_pairs_expected = 225
ordinal_strata_are_sessions = false
```

因此本次 first-upload pilot 的 source / detector accounting 是完整的 30/30 single-candidate execution。此 accounting 只表示 target resolution 與 pair denominator 完整，不表示 geometry spread 已達任何品質或 production 標準。

## Raw result identity

Private/local artifact：

```text
/home/user/palm-detector-study/results/B2_left_first_upload_pilot_raw.json
```

Frozen identity：

```text
size_bytes = 210926
SHA256 = fda53f7f9cbee5ee1322fe7b13fe7128f3a953a6b17e999fc1aaf69d526387e3
```

此 raw JSON 不 commit 到 public repository。後續 substantive interpretation 必須明確引用上述 SHA；若 artifact bytes 改變，需另建 freeze，不得沿用本結果身份。

## Execution warnings

MediaPipe / TensorFlow Lite runtime emitted informational / warning messages including XNNPACK delegate initialization、feedback tensor support disabled，以及 `NORM_RECT without IMAGE_DIMENSIONS` warning。

Formal runner仍正常完成並寫出 raw artifact；本 freeze只記錄它們為 execution provenance。不能僅因 runner完成，就把這些 runtime warnings解釋為「對 geometry 沒有任何影響」。若後續結果出現可疑系統性偏差，這些 warnings仍可作 diagnostic context。

## Post-inference wrapper quoting discrepancy

Inference本身完成後，外層 Windows PowerShell wrapper 的額外 accounting-only Python `-c` 檢查因 quote transmission 失真而觸發 Python `SyntaxError`：

```text
encoding=utf-8
...
SyntaxError: '(' was never closed
```

這個錯誤發生在 raw JSON 已寫出之後，且未執行第二次 detector inference。

因此處理方式固定為：

```text
formal inference result = retained
runner stdout accounting = retained
failed wrapper-only assertion = not treated as inference failure
raw JSON = hash-frozen before geometry inspection
```

後續沒有為了修復 wrapper quoting 而重新跑 inference，避免產生不必要的第二份 raw artifact。

## Inspection discipline

在本 freeze 建立前，允許查看的資訊僅限：

- source / model / runner provenance；
- source entry / duplicate accounting；
- candidate-count distribution；
- usable / unresolved accounting；
- expected pair accounting；
- result file size / SHA256；
- `ordinal_strata_are_sessions = false`。

尚未把下列 substantive metrics 用於 interpretation：

```text
raw_21_mean / median / max
anchor_mean / max
axis_angle_deg
width_rel
height_rel
canonical_mean / max
within-device geometry distributions
cross-device geometry distributions
B1/B2/B3 ordinal diagnostic geometry
```

本文件 merge 後，才可開始 inspect frozen raw JSON 的上述 geometry metrics。

## Scope boundary

本 result freeze 不建立：

- formal three-session B2 closure；
- arbitrary-device portability；
- detector handedness anatomical authority；
- z-coordinate portability；
- biometric identity / authentication；
- production threshold；
- production routing。

Ordinal `B1/B2/B3` remains **diagnostic-only, not sessions**。

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**。
