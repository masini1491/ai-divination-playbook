# Device / Capture First-upload Pilot — Implementation Lock

Status: **REFERENCE-ONLY / PRE-EXECUTION IMPLEMENTATION LOCK / NO PRODUCTION AUTHORITY**

## Purpose

本文件固定第一批 two-device / repeated-reposition 左手資料的 pilot runner identity 與 execution contract。此 runner 只服務已 pre-inference freeze 的 first-upload pilot，不把 ordinal strata 升格成三個 independent sessions。

Authority chain：

```text
DEVICE_CAPTURE_REPEATABILITY_FIRST_UPLOAD_ADMISSION.md
→ DEVICE_CAPTURE_REPEATABILITY_FIRST_UPLOAD_SOURCE_FREEZE.md
→ device_capture_first_upload_pilot_runner.py
→ 本 implementation lock
```

## Exact runner identity

```text
references/palmistry/device_capture_first_upload_pilot_runner.py
Git blob = 4e2cdc757333753b133e568fae84f7c339712a06
```

Formal execution前必須驗證此 blob；若 source改動，需另建 amendment / new lock，不得把舊結果歸到新 source。

## Frozen private input identity

```text
archive name = 左手.zip
SHA256 = b5854b545f3ff0193b51cc02278efdbca25e1e3d1147a8559c7bb042ff2b7ca0
```

Runner hard-lock此 SHA，並要求 archive structure exactly：

```text
Google Pixel 5      = D1 = 15 JPEGs
Google Pixel 10 pro = D2 = 15 JPEGs
total               = 30
```

30 張來源影像仍是 private/local evidence，不 commit 到 public repository。

## Detector / model lock

```text
MediaPipe Tasks runtime = 1.0.1
Hand Landmarker model SHA256 = fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1
running_mode = IMAGE
num_hands = 2
min_hand_detection_confidence = 0.5
min_hand_presence_confidence = 0.5
min_tracking_confidence = 0.5
max detector work dimension = 1600
```

Runner不下載 model；formal execution必須明確提供既有 model path並通過 SHA gate。

## Capture / side contract

User-provided authority：

```text
anatomical_side = left
side_authority = explicit_bodily_self_report
```

Detector handedness只保存為 metadata；不得覆寫 anatomical side。

EXIF處理只讀 Orientation tag。Frozen source預期：

```text
EXIF Orientation = 1 for all 30
```

若 formal runner看到非 `1` / missing orientation，該 entry fail closed為 unresolved；runner不讀取或輸出 GPS values / complete EXIF dump。

## Target resolution rule

每張影像：

```text
candidate_count = 1 → usable
candidate_count = 0 → unresolved
candidate_count > 1 → unresolved; candidate index不得猜 target
```

因此 multi-candidate不靠 handedness / list index rescue。

## Canonical geometry lock

沿用 current projected-width contract：

```text
L0  = wrist
L5  = index MCP
L17 = little MCP
M   = midpoint(L5, L17)
ey  = normalize(M - L0)
raw_ex = L5 - L17
projected = raw_ex - dot(raw_ex, ey) * ey
ex = normalize(projected), pointing toward index side
width = dot(L5 - L17, ex)
height = norm(M - L0)
```

Canonical coordinates：

```text
x = dot(P - L0, ex) / width
y = dot(P - L0, ey) / height
```

No historical unprojected-width fallback。

## Metrics

Pair-level metrics：

```text
raw_21_mean
raw_21_median
raw_21_max
anchor_mean
anchor_max
axis_angle_deg
width_rel
height_rel
canonical_mean
canonical_max
```

Aggregate summary per metric：

```text
n / mean / median / p10 / p90 / p95 / min / max / std
```

`z`與 handedness score可保留在 local raw record，但本 pilot repeatability metrics只使用 2D x/y geometry；不得由此聲稱 z portability。

## Pair families

### Within-device repeated-reposition

```text
C(15,2) = 105 per device
2 devices = 210 expected pairs
```

### Cross-device same-collection

```text
15 × 15 = 225 expected pairs
```

### B1 / B2 / B3

Ordinal 01–05 / 06–10 / 11–15可作 diagnostic strata；runner明確輸出：

```text
ordinal_strata_are_sessions = false
```

不得把 strata結果描述為 cross-session repeatability。

## Result discipline

Runner stdout只揭露 provenance / accounting / candidate-count / pair-count accounting，不印 substantive geometry distributions。

Formal順序：

```text
verify exact runner blob
→ py_compile
→ verify archive SHA / model SHA / runtime version
→ execute all 30
→ raw JSON SHA freeze
→ only then inspect geometry metrics
```

## Boundary

本 implementation lock不建立：

- formal three-session B2 closure；
- arbitrary-device portability；
- detector handedness anatomical authority；
- biometric identity / authentication；
- production threshold；
- production routing。

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**。
