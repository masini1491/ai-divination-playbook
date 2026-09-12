# Capture / Mirroring / Anatomical-side Contract — Node Closure

Status: **REFERENCE-ONLY / BOUNDED NODE CLOSURE / REAL-CAMERA EMPIRICAL VALIDATION STILL OPEN**

## Closure statement

Palmistry B3 的 deterministic capture / mirroring / anatomical-side lineage contract subnode 現在可以 boundedly close。

Authority chain：

```text
CAPTURE_MIRRORING_ANATOMICAL_SIDE_CONTRACT_PLAN.md
→ capture_mirroring_contract_validator.py
→ CAPTURE_MIRRORING_CONTRACT_VALIDATOR_STATIC_REVIEW.md
→ CAPTURE_MIRRORING_CONTRACT_VALIDATION_RESULT_FREEZE.md
→ CAPTURE_MIRRORING_CONTRACT_VALIDATION_RESULTS.md
```

Frozen formal result：

```text
SHA256 cd7332c66b83c3d009f1e2f9d5f21adcad25b18e8e7d461fe12c96006f5e257f
```

Executed validator：

```text
Git blob f504354ce4af352deadbe1286499d8390b76b18c
```

## Why closure is justified

Predeclared closure criterion要求：

```text
all 12 cases deterministic PASS
all violation counters = 0
```

Formal result：

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

Substantive inspection也與 predeclared semantics一致，沒有發現 plan / validator discrepancy。

## Contract behavior now supported

### 1. Stored / preview / model / anatomy are distinct state layers

以下狀態不得合併成單一 mirror / handedness flag：

```text
stored pixel frame
preview mirror state
model-only mirror transform
anatomical hand side
```

Case B證明 preview mirror可變而 stored/raw/canonical geometry與 explicit anatomical side保持不變。

### 2. Model-only transform must be invertible and verified

Case D：verified model mirror round-trip residual：

```text
5.5511151231257827e-17 < 1e-12
```

Cases E/F：缺 inverse或 mirror state unknown時：

```text
raw_image_geometry       = unresolved
canonical_hand_geometry  = unresolved
```

高 detector score不得 rescue此 blocker。

### 3. EXIF transform is exactly-once and reflection-aware

Case G，EXIF 6 round-trip：

```text
5.5511151231257827e-17 < 1e-12
```

Case H，EXIF 6 double application：

```text
once_vs_twice_max_delta = 0.7134423592694787
```

因此 double application是 material frame error，必須 fail closed。

Case I，reflection-bearing EXIF codes：

```text
2 -> 5.5511151231257827e-17
5 -> 0.0
7 -> 5.5511151231257827e-17
```

支持完整 reflection-aware transform，而不是 rotation-only shortcut。

### 4. Detector handedness is metadata, not anatomical authority

Cases C/J：explicit side與 detector label衝突時，explicit side保留 authority，detector conflict被保存但不覆寫。

Case K：只有 detector handedness時：

```text
anatomical_side           = unresolved
tradition_side_projection = unresolved
```

因此 current evidence再次支持：

```text
hand_side != detector handedness
```

### 5. Side uncertainty is capability-specific

Case L：frame/model lineage完整但 side authority缺失時：

```text
raw_image_geometry        = admitted
canonical_hand_geometry   = admitted
anatomical_side           = unresolved
tradition_side_projection = unresolved
```

這與 uncertainty-composition closure一致：不能因 one capability unresolved就把 whole observation global-invalid。

## What is closed

Boundedly closed：

> deterministic representation and fail-closed behavior for capture / preview mirror / model mirror / EXIF transform / anatomical-side authority separation.

也就是說，在目前 research contract層，這些 state如何分離、何時 geometry可 admitted、何時 side-dependent projection必須 unresolved，已有 executable bounded evidence。

## What remains open

此 closure**不關閉** real-world capture portability。

仍 open：

- Android / iOS camera implementation behavior；
- front-camera preview-vs-file mirror behavior；
- OEM / app-specific EXIF handling；
- real-device orientation metadata correctness；
- user-provided left/right provenance quality；
- multi-device / distance / illumination / exposure repeatability；
- production capture normalization policy；
- production schema / routing。

這些應進入 B2 controlled device / capture-condition study，而不是重跑相同 synthetic contract cases。

## Research sequencing impact

B3 deterministic contract已不再阻擋 B2。

Next dependency-central research target：

```text
B2 controlled device / capture-condition repeatability
```

B2必須沿用本 node的 lineage fields，避免把 device effect與 preview/storage/model mirroring confound混在一起。

## Boundary

本 closure不建立：

- anatomical truth from detector metadata；
- biometric identity；
- production threshold；
- production routing；
- tradition interpretation validity。

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**。
