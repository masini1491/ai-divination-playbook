# Palm Capture / Mirroring / Anatomical-side Contract — Validation Plan

Status: **REFERENCE-ONLY / PREDECLARED RESEARCH PLAN / NO PRODUCTION AUTHORITY**

## Purpose

本 node驗證 Palmistry observation pipeline 中四個經常被混為一談的狀態是否能 deterministic、fail-closed 地分開：

```text
capture / stored-image frame
preview mirroring
model-only mirroring
anatomical hand side
```

研究問題不是「能否靠 MediaPipe handedness猜左右手」，而是：

> 在明確的 capture / orientation / mirror lineage下，哪些 observation capability可以 admitted，哪些只能 unresolved；以及 detector handedness metadata 是否會被錯誤提升成 anatomical-side authority。

本 plan不建立 production schema，也不要求真實使用者照片。

## Existing evidence being composed

本 validation只整合既有 bounded evidence，不改寫其 authority：

- `NORMALIZATION_CONTRACT_DRAFT.md`：`hand_side`與`mirrored_for_model`必須分開；model transform需 inverse回 raw-image geometry；
- `SENSITIVITY_SWEEP.md`：漏掉 detector-only mirror inverse會造成 canonical `x -> -x` semantic frame inversion，不是 small noise；
- `OBSERVATION_UNCERTAINTY_COMPOSITION_NODE_CLOSURE.md`：detector handedness不是 anatomical-side authority，hard blocker不得被 model score rescue；
- GTEA natural multi-hand evidence：detector handedness可出現 `[Left,Left]` / `[Right,Right]`而 scene geometry仍可正確 association；
- MediaPipe runtime-only MOHI result：在 pinned 1.0.1 vs 1.0.0 runtime pair下 handedness label一致，但這不提升 anatomical authority。

## Contract layers

### L0. Stored pixel frame

記錄 observation實際收到的 pixel frame，而不是假設 camera physical frame：

```text
stored_pixel_frame_id
exif_orientation_present
exif_orientation_code: 1..8 | unknown
exif_transform_applied: true | false | unknown
stored_file_mirror_state: mirrored | not_mirrored | unknown
```

`stored_file_mirror_state`只描述已知 capture/export lineage，不從 detector handedness反推。

### L1. Preview / UI frame

```text
preview_mirrored: true | false | unknown | not_applicable
```

Preview state只有在使用者是依螢幕方向做 side assertion時才可能影響 anatomical-side provenance；它不應自動改寫 stored-image geometry。

### L2. Detector adapter frame

```text
mirrored_for_model: true | false | unknown
inverse_model_mirror_applied: true | false | unknown
orientation_transform_applied_for_model: explicit transform | none | unknown
inverse_mapping_verified: true | false | unknown
```

若 detector-only transform不能可靠 inverse：

```text
raw_image_geometry = unresolved
canonical geometry that depends on mapped detector output = unresolved
```

不得用高 detector confidence rescue。

### L3. Anatomical-side evidence

`left / right` anatomical side必須有獨立 evidence lineage。

候選 evidence source：

```text
explicit_bodily_self_report
trusted_capture_annotation
trusted_dataset_annotation
clinically / procedurally controlled label
unknown
```

以下不得單獨取得 authority：

```text
detector handedness label
candidate list index
screen-left / screen-right position
preview appearance without mirror provenance
```

## Capability-specific output

Validation output至少分開：

```text
stored_frame_geometry
raw_image_geometry
canonical_hand_geometry
anatomical_side
tradition_side_projection
```

允許 mixed states。例如：

```text
stored_frame_geometry = admitted
canonical_hand_geometry = admitted
anatomical_side = unresolved
tradition_side_projection = unresolved
```

這比把整張照片判成 global invalid更符合 uncertainty-composition closure。

## Transform model for synthetic validator

使用 unit-square normalized coordinate frame：

```text
0 <= x <= 1
0 <= y <= 1
```

定義 asymmetric labeled points，避免 mirror / rotation後誤碰巧重合：

```text
wrist        = (0.46, 0.88)
index_mcp    = (0.72, 0.48)
little_mcp   = (0.24, 0.53)
index_tip    = (0.82, 0.11)
little_tip   = (0.13, 0.20)
thumb_tip    = (0.91, 0.57)
mark_a       = (0.64, 0.67)
```

Validator實作：

- EXIF orientation codes `1..8` 的 deterministic normalized-coordinate transforms；
- 每一 transform的 inverse；
- detector-only horizontal mirror `x -> 1-x`；
- composed transform / inverse round-trip；
- labeled-point exact/tolerance comparison。

Synthetic geometry只驗證 transform contract，不證明 camera metadata真實可信。

## Predeclared cases

### Case A — identity capture, explicit side authority

```text
EXIF = 1
stored mirror = not_mirrored
preview mirror = false
mirrored_for_model = false
explicit anatomical side = right
```

Expected：

```text
stored_frame_geometry = admitted
raw_image_geometry = admitted
canonical_hand_geometry = admitted
anatomical_side = admitted:right
tradition_side_projection = admitted_for_side_dependency_only
```

### Case B — preview mirror only

```text
stored file unmirrored
preview mirrored = true
model mirror = false
explicit bodily self-report = right
```

Expected：preview mirror不得改變 stored/raw/canonical geometry，也不得把 right改成 left。

### Case C — known stored-file mirror

```text
stored mirror = mirrored
explicit bodily side = right
model mirror = false
```

Expected：

- stored-frame geometry admitted；
- canonical source-neutral geometry可 admitted；
- anatomical side仍由 independent side evidence決定；
- detector handedness不能因 mirrored stored frame取得 authority。

### Case D — detector-only mirror with verified inverse

```text
mirrored_for_model = true
inverse_model_mirror_applied = true
inverse_mapping_verified = true
```

Expected：detector output round-trip回 stored/raw frame；geometry admitted。

### Case E — detector-only mirror without inverse

```text
mirrored_for_model = true
inverse_model_mirror_applied = false
```

Expected：raw/canonical geometry unresolved；不得用 detector score rescue。

### Case F — detector mirror state unknown

```text
mirrored_for_model = unknown
```

Expected：若 detector-derived geometry需要 inverse mapping，raw/canonical geometry unresolved。

### Case G — EXIF orientation code 6 applied exactly once

Expected：EXIF transform + inverse round-trip到 original stored-pixel coordinates within tolerance；geometry admitted。

### Case H — EXIF orientation code 6 accidentally applied twice

Expected：synthetic labeled geometry不等於 baseline；frame reconciliation fail closed。

### Case I — mirrored EXIF orientation code 2 / 5 / 7 path

至少覆蓋一個含 reflection的 EXIF transform與 inverse，證明 rotation-only logic不足。

Expected：exact transform lineage時 round-trip PASS；若把 reflection當成 rotation則 FAIL。

### Case J — detector handedness conflicts with explicit side authority

```text
explicit side = right
detector handedness = Left
```

Expected：

```text
anatomical_side = right
metadata_conflict = true
```

不得讓 detector label覆寫 explicit side authority。

### Case K — detector handedness is only side evidence

```text
explicit/trusted side authority absent
detector handedness = Right
```

Expected：

```text
anatomical_side = unresolved
tradition_side_projection = unresolved
```

### Case L — target geometry admitted but side unresolved

Frame transforms完整、geometry round-trip完整，但沒有 independent side authority。

Expected：

```text
stored_frame_geometry = admitted
raw_image_geometry = admitted
canonical_hand_geometry = admitted
anatomical_side = unresolved
tradition_side_projection = unresolved
```

用來證明 side uncertainty不能不必要地摧毀 source-neutral geometry capability。

## Assertions

Formal validator至少必須輸出：

```text
cases_total
cases_pass
cases_fail
transform_round_trip_failures
hard_blocker_rescue_failures
detector_handedness_authority_violations
preview_to_stored_frame_leakage_violations
side_uncertainty_overblocking_violations
```

Formal PASS要求：

```text
cases_fail = 0
all violation counters = 0
```

## Fail-closed rules under test

1. model-only mirror inverse缺失 → detector-derived raw/canonical geometry unresolved；
2. unknown model mirror state → no silent assumption；
3. detector handedness不能建立 anatomical side；
4. detector handedness衝突不能覆寫 higher-authority explicit/trusted side evidence；
5. preview mirror不得自動 mutate stored pixels；
6. EXIF transform必須 exactly-once；
7. reflection-bearing EXIF code不得降格成 pure rotation；
8. anatomical side unresolved不應 overblock source-neutral geometry；
9. tradition rule若需要 side，side unresolved時 projection fail closed。

## What this node does not test

- camera vendor是否正確寫 EXIF；
- Android / iOS特定 Camera API implementation；
- real selfie app是否保存 mirror；
- user是否會正確 self-report left/right；
- MediaPipe handedness accuracy；
- biometric identity；
- production threshold；
- tradition meaning。

## Result discipline

1. plan先 merge；
2. validator source建立後做 static review；
3. formal run前固定 validator Git blob；
4. formal result先 SHA freeze；
5. 再 substantive interpretation；
6. 若 plan / validator discrepancy，保留舊 artifact並以 amendment處理，不覆寫歷史結果。

## Closure criterion

若所有 predeclared cases deterministic PASS，可 boundedly close：

> capture / mirror / side lineage可以 capability-specific、fail-closed地表示，且 detector handedness不取得 anatomical authority。

仍不代表 real camera pipeline已被 empirical驗證；那會是後續 B2 device/capture study的一部分。

## Boundary

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**。
