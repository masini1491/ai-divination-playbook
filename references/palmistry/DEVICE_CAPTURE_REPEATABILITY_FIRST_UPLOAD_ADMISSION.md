# Device / Capture Repeatability — First Upload Admission

Status: **REFERENCE-ONLY / PRE-INFERENCE PILOT ADMISSION / NOT FORMAL THREE-SESSION CLOSURE DATA**

## Purpose

本文件在任何 MediaPipe inference 前，固定第一批真實 two-device palm upload 的可用範圍，避免因資料已收集完成後再把 capture chronology 強行重命名成原先 plan 所要求的三個 independent sessions。

這批資料可用於 **two-device / repeated-reposition pilot characterization**，但**不滿足** `DEVICE_CAPTURE_REPEATABILITY_PLAN.md` 中 `3 true repositioned sessions` 的 formal B2 closure criterion。

## User-provided anatomical-side authority

本批 30 張照片由使用者明確表示全部是：

```text
anatomical_side = left
side_authority = explicit_bodily_self_report
```

Detector handedness 不得覆寫此欄位。

## Collection structure

Private upload contains：

```text
Google Pixel 5      = 15 still photos
Google Pixel 10 Pro = 15 still photos
Total               = 30 source entries
```

User additionally clarified the operational capture behavior：

```text
before every photo:
hand lowered
→ hand raised again
→ angle / framing slightly changed
→ one still photo captured
```

因此這不是一個 frozen pose 的 burst / video-frame extraction；每張都有 intentional reposition component。

但 source chronology顯示每個 device 的 15 張仍集中在短時間 collection block內，沒有足夠 evidence 支持把 `1–5 / 6–10 / 11–15` 宣稱為三個真正 independent sessions。

## Admitted interpretation

正式採用：

```text
study role = first-upload pilot
capture unit = independent still photo with per-capture reposition
physical devices = 2
entries per device = 15
true independent session count = 1 short collection block per device
```

可建立三個 ordinal strata：

```text
B1 = ordinal 01–05
B2 = ordinal 06–10
B3 = ordinal 11–15
```

但 `B1/B2/B3` 只能作：

- temporal / ordinal drift diagnostic；
- balanced descriptive stratification；
- reproducible grouping for debugging。

它們**不得**被稱為 `S1/S2/S3`，也不得用來回答 formal cross-session repeatability。

## Allowed pilot contrasts

本批資料可回答 bounded pilot questions：

### P0 — within-device repeated-reposition spread

每個 device 15 captures 之間的 all-pairs：

```text
C(15,2) = 105 pairs per device
2 devices = 210 within-device pairs
```

### P1 — cross-device same-collection spread

兩 device 各 15 張的 all-pairs：

```text
15 × 15 = 225 cross-device pairs
```

### P2 — ordinal-stratum diagnostics

可分別描述 B1/B2/B3，但不得把它們 promotion 成 independent session evidence。

## Not allowed from this upload

不得宣稱：

- three-session repeatability complete；
- session-held-out device effect；
- formal B2 closure criterion satisfied；
- production threshold；
- arbitrary multi-device portability；
- biometric identity / authentication capability。

若未來補真正分離的 S2 / S3 collections，可另建 formal three-session dataset；不覆寫本 pilot 身份。

## Quality / framing admission

Pre-inference visual QC supports：

- palm-facing capture；
- whole palm / MCP region / wrist base broadly visible；
- no obvious severe target ambiguity；
- natural per-capture pose variation present；
- no obvious material palm-ROI occlusion that requires global exclusion。

此 QC 只決定是否可進 detector pilot，並不代表 every fine-line / color capability admitted。

## Privacy / metadata boundary

Original private source files contain task-irrelevant EXIF metadata beyond orientation. Research artifacts must not preserve or publish：

- GPS values；
- exact capture location；
- device serial or account identifiers；
- complete EXIF dumps。

Only task-relevant metadata such as orientation code, dimensions, source hashes, device-family label, ordinal grouping, and capture-lineage state may be retained.

## Next step

Before substantive geometry inspection：

1. freeze source archive identity；
2. freeze privacy-minimized integrity manifest identity；
3. implement a pilot runner against the already pinned MediaPipe 1.0.1 + Hand Landmarker model contract；
4. static-review runner；
5. execute all 30 entries；
6. hash raw result before substantive metric inspection。

No threshold may be selected after seeing the pilot distributions。

## Boundary

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**。