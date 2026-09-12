# Capture / Mirroring / Anatomical-side Contract — Validation Results

Status: **REFERENCE-ONLY / BOUNDED CONTRACT EVIDENCE / NO REAL-CAMERA VALIDATION / NO PRODUCTION AUTHORITY**

## Purpose

本文件解讀已先行 freeze 的 deterministic capture / mirroring / anatomical-side contract formal result。

Frozen raw artifact：

```text
/home/user/palm-detector-study/results/CAPTURE_mirroring_anatomical_side_validation.json
SHA256 = cd7332c66b83c3d009f1e2f9d5f21adcad25b18e8e7d461fe12c96006f5e257f
```

Executed validator：

```text
references/palmistry/capture_mirroring_contract_validator.py
Git blob = f504354ce4af352deadbe1286499d8390b76b18c
```

Companion plan / pre-execution review：

```text
CAPTURE_MIRRORING_ANATOMICAL_SIDE_CONTRACT_PLAN.md
CAPTURE_MIRRORING_CONTRACT_VALIDATOR_STATIC_REVIEW.md
CAPTURE_MIRRORING_CONTRACT_VALIDATION_RESULT_FREEZE.md
```

本 node只驗證 transform lineage、capability-specific fail-closed behavior與 anatomical-side authority boundary；不驗證真實 camera vendor / Android / iOS / selfie app behavior。

## Formal accounting

Formal run在 substantive inspection前先 hash freeze，之後重新驗證 SHA PASS。

```text
cases_total                                = 12
cases_pass                                 = 12
cases_fail                                 = 0
transform_round_trip_failures              = 0
hard_blocker_rescue_failures               = 0
detector_handedness_authority_violations   = 0
preview_to_stored_frame_leakage_violations = 0
side_uncertainty_overblocking_violations   = 0
```

Tolerance：

```text
1e-12
```

## Case-by-case substantive result

### Case A — identity capture + explicit side authority

Observed：

```text
stored_frame_geometry      = admitted
raw_image_geometry         = admitted
canonical_hand_geometry    = admitted
anatomical_side            = right
tradition_side_projection  = admitted
detector_handedness        = Right
metadata conflict          = false
```

Result：PASS。正常 lineage可同時 admitted source-neutral geometry與 explicit anatomical side。

### Case B — preview mirror only

`preview_mirrored = true` 時：

```text
stored_frame_geometry   = admitted
raw_image_geometry      = admitted
canonical_hand_geometry = admitted
anatomical_side         = right
```

Result：PASS。Preview mirror沒有 leak 回 stored/raw/canonical geometry，也沒有把 explicit right改成 left。

### Case C — known stored-file mirror

Observed：

```text
stored_file_mirror_state = mirrored
canonical_hand_geometry   = admitted
anatomical_side           = right
detector_handedness       = Left
metadata conflict         = true
```

Result：PASS。已知 stored mirror沒有讓 detector handedness取得 anatomical authority；explicit side仍保留 authority，衝突只保存為 metadata conflict。

### Case D — detector-only mirror with verified inverse

Round-trip diagnostic：

```text
model_mirror_round_trip_max_delta = 5.5511151231257827e-17
```

小於 predeclared tolerance `1e-12`。

Observed：

```text
model_lineage_ok          = true
raw_image_geometry        = admitted
canonical_hand_geometry   = admitted
```

Result：PASS。Model-only horizontal mirror在 verified inverse後可安全回到 source frame；floating-point residual僅為 arithmetic round-off，沒有形成 semantic inversion。

### Case E — detector-only mirror without inverse

Observed：

```text
model_lineage_ok          = false
raw_image_geometry        = unresolved
canonical_hand_geometry   = unresolved
```

即使 fixture提供高 detector score，geometry仍 fail closed。

Result：PASS。Hard blocker沒有被 model confidence rescue。

### Case F — detector mirror state unknown

Observed：

```text
stored_file_mirror_state  = unknown
model_lineage_ok          = false
raw_image_geometry        = unresolved
canonical_hand_geometry   = unresolved
anatomical_side           = right
```

Result：PASS。Unknown model-mirror state不允許 silent assumption；同時 explicit anatomical side可以獨立存在，證明 geometry lineage與 side authority不是同一欄位。

### Case G — EXIF orientation 6 exactly once

Diagnostic：

```text
EXIF code = 6
round_trip_max_delta = 5.5511151231257827e-17
```

小於 `1e-12`。

Observed：raw / canonical geometry均 admitted。

Result：PASS。Exactly-once EXIF transform + inverse在 synthetic asymmetric geometry上可 round-trip。

### Case H — EXIF orientation 6 accidentally applied twice

Diagnostic：

```text
once_vs_twice_max_delta = 0.7134423592694787
```

此差異遠大於 tolerance。

Observed：

```text
exif_state_ok            = false
raw_image_geometry       = unresolved
canonical_hand_geometry  = unresolved
```

Result：PASS。Double-application沒有被當成微小 noise，而是 frame reconciliation hard blocker。

### Case I — reflection-bearing EXIF path 2 / 5 / 7

Round-trip diagnostics：

```text
EXIF 2 = 5.5511151231257827e-17
EXIF 5 = 0.0
EXIF 7 = 5.5511151231257827e-17
```

全部小於 `1e-12`。

Observed：

```text
canonical_hand_geometry = admitted
anatomical_side          = left
detector_handedness      = Right
metadata conflict        = true
```

Result：PASS。Reflection-bearing EXIF transform不能簡化成 rotation-only；完整 transform lineage可回復 geometry，而 detector label conflict不改寫 explicit anatomical side。

### Case J — detector handedness conflicts with explicit side authority

Observed：

```text
anatomical_side      = right
detector_handedness  = Left
metadata conflict    = true
```

Result：PASS。Detector handedness沒有覆寫 higher-authority explicit side evidence。

### Case K — detector handedness is the only side evidence

Observed：

```text
raw_image_geometry        = admitted
canonical_hand_geometry   = admitted
anatomical_side           = unresolved
tradition_side_projection = unresolved
detector_handedness       = Right
```

Result：PASS。Detector handedness單獨不能建立 anatomical side，也不能啟動 side-dependent tradition projection。

### Case L — geometry admitted while side remains unresolved

Observed：

```text
raw_image_geometry        = admitted
canonical_hand_geometry   = admitted
anatomical_side           = unresolved
tradition_side_projection = unresolved
stored_file_mirror_state  = unknown
model_lineage_ok          = true
```

Result：PASS。Side uncertainty沒有 overblock source-neutral geometry；capability-specific state可同時表達「geometry usable / side unresolved」。

## Cross-case conclusions

本 12-case contract validation支持以下 bounded conclusions：

1. `preview_mirrored`、`stored_file_mirror_state`、`mirrored_for_model`、`anatomical_side`可以分開保存，不必壓成單一 handedness / mirror flag。
2. Detector-only mirror若 inverse完整且 verified，可回到 raw/stored frame；缺 inverse或 mirror state unknown時，detector-derived raw/canonical geometry必須 fail closed。
3. EXIF orientation需 exactly-once；double application會產生 material geometry error，而不是可忽略 noise。
4. EXIF reflection-bearing codes需要完整 reflection-aware transform，不能當成 pure rotation family。
5. Detector handedness只可作 metadata / conflict signal；不能單獨建立或覆寫 anatomical-side authority。
6. Anatomical-side unresolved不應摧毀 source-neutral geometry capability；只有需要 side的 tradition projection應保持 unresolved。
7. 高 detector confidence不能 rescue transform-lineage hard blocker。

## Boundary retained by the frozen artifact

Formal result明確保存：

```text
real_camera_pipeline_empirically_validated = false
detector_handedness_anatomical_authority   = false
production_threshold                       = false
production_routing                         = false
biometric_identity_claim                   = false
```

因此本結果不證明：

- camera vendor一定正確寫 EXIF；
- Android / iOS Camera API一定符合某 mirror behavior；
- selfie app preview與stored image一定同向；
- 使用者 self-report左右手一定正確；
- MediaPipe handedness accuracy；
- production capture policy。

## Decision

依 predeclared closure criterion，12/12 cases deterministic PASS且所有 violation counters為零，因此：

> **capture / mirror / anatomical-side lineage contract subnode can be boundedly closed at the deterministic transform / capability-state level.**

仍 open的是**real-device / real-camera empirical capture lineage**，應與後續 B2 controlled device / capture-condition repeatability一起驗證，而不是把 synthetic contract PASS外推成 field-camera truth。

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**。
