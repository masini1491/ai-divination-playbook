# Device / Capture First-upload Pilot Runner — Static Review

Status: **REFERENCE-ONLY / PRE-EXECUTION STATIC REVIEW / FORMAL INFERENCE NOT YET RUN**

## Reviewed source

```text
references/palmistry/device_capture_first_upload_pilot_runner.py
Git blob = 4e2cdc757333753b133e568fae84f7c339712a06
```

Companion lock：

```text
DEVICE_CAPTURE_FIRST_UPLOAD_PILOT_IMPLEMENTATION_LOCK.md
```

## Review outcome

**PASS for formal pilot execution.**

本 review只確認 exact source的 syntax / source-level contract / frozen-source compatibility；沒有執行 MediaPipe inference，也沒有查看任何 landmark geometry distribution。

## Exact-source verification performed

Git blob以 exact source bytes重算一致：

```text
4e2cdc757333753b133e568fae84f7c339712a06
```

Exact source完成：

```text
python -m py_compile = PASS
```

因此 formal run仍必須再於 execution environment做相同 blob gate與 py_compile，不能用此 static review代替 runtime verification。

## Frozen archive structural dry validation

在不執行 detector的情況下，以 frozen private upload驗證 source parser：

```text
archive SHA256 = b5854b545f3ff0193b51cc02278efdbca25e1e3d1147a8559c7bb042ff2b7ca0
source rows = 30
D1 Google Pixel 5 = 15
D2 Google Pixel 10 pro = 15
```

Runner的 minimal JPEG EXIF parser在 exact 30 sources上得到：

```text
Orientation 1 = 30 / 30
```

這只驗證 task-relevant Orientation extraction，沒有讀取或保存 GPS values / unrelated EXIF fields。

## Source freeze fidelity

Runner hard-lock：

```text
EXPECTED_ARCHIVE_SHA256 = b5854b545f3ff0193b51cc02278efdbca25e1e3d1147a8559c7bb042ff2b7ca0
EXPECTED_TOTAL = 30
EXPECTED_PER_DEVICE = 15
```

因此無法把另一個 archive靜默當成本 frozen upload。

Byte-identical duplicates在 inference後仍由 source SHA再次檢查；任何 duplicate group會中止而不是 silently count as independent captures。

## Runtime / model provenance

Source要求：

```text
MediaPipe __version__ == 1.0.1
model SHA256 == fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1
```

Detector options與既有 pinned contract一致：IMAGE / num_hands 2 / thresholds 0.5 / 0.5 / 0.5。

沒有 network model download path，因此 execution不會因遠端 model更新而靜默換 artifact。

## Stored-pixel / EXIF behavior

Source使用 OpenCV `IMREAD_IGNORE_ORIENTATION` when available，先保留 stored-pixel frame；且本 frozen source要求 Orientation exactly `1`。

若 orientation不是 `1`，entry標記 unresolved，不做 silent auto-rotation或 handedness-based correction。

這與已 boundedly closed的 B3 capture/mirror contract一致：orientation lineage不明時不得用 downstream confidence rescue。

## Target association behavior

Source-level review確認：

```text
1 candidate → usable
0 candidates → unresolved
>1 candidates → unresolved
```

Multi-hand情形不使用 candidate index、screen position或 detector handedness猜 target，因此沒有重新引入先前已禁止的 identity assumption。

## Canonical contract fidelity

Runner的 `canonical_basis()` 使用：

```text
projected = (L5-L17) - dot(L5-L17, ey) * ey
ex = normalize(projected)
width = dot(L5-L17, ex)
```

與 current normalization contract / runtime comparison corrected implementation一致；沒有退回 historical `norm(L5-L17)` width。

## 2D-only claim boundary

Pair metrics只使用 x/y：

- raw normalized 21-point distances；
- L0/L5/L17 anchor distances；
- axis angle；
- width / height relative difference；
- canonical 21-point distances。

Detector `z`與 handedness score雖可留在 private raw entry，aggregate pilot geometry不使用它們。因此未來結果不得描述為 z-coordinate portability / depth repeatability。

## Pair accounting review

若全部 30 entries usable：

```text
within-device all-pairs = 105 × 2 = 210
cross-device all-pairs  = 15 × 15 = 225
```

若某 entry unresolved，runner仍保留 expected pair records並將相應 pair標成 unresolved；不因缺值縮小 expected denominator而假裝完整。

## Ordinal strata boundary

Runner將每 device依檔名時間排序分成：

```text
B1 = 01–05
B2 = 06–10
B3 = 11–15
```

但 result schema明確標記：

```text
role = ordinal_diagnostic_only_not_session
ordinal_strata_are_sessions = false
formal_three_session_b2_closure_data = false
```

所以這批資料不會被 source code層誤升格成 S1/S2/S3。

## Anatomical side boundary

Runner固定使用者提供的：

```text
anatomical_side = left
side_authority = explicit_bodily_self_report
```

Detector handedness只統計 label distribution / pairwise metadata agreement，不參與 anatomical-side authority或 target rescue。

## Output / inspection discipline

Raw JSON包含完整 local evidence以支援後續 freeze，但 stdout只輸出：

- provenance hash / runtime；
- source accounting；
- candidate-count accounting；
- usable / unresolved accounting；
- expected pair counts；
- `ordinal_strata_are_sessions = false`。

不在 formal run stdout印 geometry summary，允許先 SHA freeze raw result，再 substantive inspection。

## Known scope limits

Static review不證明：

- 30 張都一定回傳單一 candidate；
- Pixel 5與Pixel 10 Pro geometry spread大小；
- cross-device variability是否高於 within-device variability；
- three-session repeatability；
- arbitrary device / camera app portability。

這些只能在 formal run / frozen result後回答。

## Decision

Exact runner source可進入 formal first-upload pilot execution。

下一步：

```text
fresh merged main
→ exact blob gate
→ py_compile
→ execute frozen 30-entry archive
→ hash raw JSON before substantive metric inspection
```

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**。
