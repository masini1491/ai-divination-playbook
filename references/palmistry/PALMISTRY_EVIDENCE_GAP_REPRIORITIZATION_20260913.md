# Palmistry Evidence Gap Reprioritization — 2026-09-13

Status: **REFERENCE-ONLY / COLD RESEARCH ROADMAP / NO PRODUCTION PROMOTION**

## Purpose

本文件在以下三個 bounded closures之後重新排序 Palmistry observation research：

1. Palm Observation uncertainty-composition contract validation；
2. MediaPipe `1.0.1` vs `1.0.0` runtime-only MOHI portability study；
3. capture / mirroring / anatomical-side deterministic lineage contract validation。

它是 2026-09-12 roadmap 的後續 snapshot，不回寫歷史文件內容，也不建立 production routing / threshold。

## Newly closed / materially advanced since 2026-09-12

### A2. Observation uncertainty composition — BOUNDEDLY CLOSED

`OBSERVATION_UNCERTAINTY_COMPOSITION_NODE_CLOSURE.md` 已完成 V2 deterministic validation：

```text
cases_total = 12
cases_pass  = 12
cases_fail  = 0
```

已 validated：

- capability-specific state為 authoritative；
- top-level admission只能 summary-only；
- hard blockers不可被 local/model scores rescue；
- tradition layer不可回寫 observation layer；
- candidate index不是 physical identity；
- detector handedness不是 anatomical-side authority；
- research metrics不得自動升格成 cutoff。

因此原 roadmap 的 A2 不再是 open。

### B1a. MediaPipe runtime package portability — BOUNDEDLY CLOSED FOR 1.0.1 VS 1.0.0

`MEDIAPIPE_RUNTIME_MOHI_RESULTS.md` 與 `MEDIAPIPE_RUNTIME_COMPATIBILITY_NODE_CLOSURE.md` 已完成 controlled runtime-only comparison。

Primary 148 unique-source representatives：

```text
candidate count agreement = 148 / 148
candidate transitions     = 1 -> 1 for all
resolved geometry         = 148 / 148
handedness label agreement= 148 / 148
```

Tracked raw 2D / anchor / canonical metrics全部 exact zero across mean / median / p90 / p95 / min / max / std。

因此在 pinned Hand Landmarker model、same prepared pixels、same Python / NumPy / OpenCV / non-MediaPipe package contract下，MediaPipe `1.0.1` vs `1.0.0` 沒有觀察到 runtime-dependent 2D/canonical geometry drift。

這只關閉 runtime package pair，不關閉 model artifact version portability。

### B3a. Capture / mirroring / anatomical-side deterministic contract — BOUNDEDLY CLOSED

`CAPTURE_MIRRORING_CONTRACT_VALIDATION_RESULTS.md` 與 `CAPTURE_MIRRORING_ANATOMICAL_SIDE_NODE_CLOSURE.md` 已完成 predeclared 12-case deterministic validation。

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

Validated bounded behavior：

- preview mirror不改寫 stored/raw/canonical geometry；
- model-only mirror需要 verified inverse；
- unknown / missing inverse時 detector-derived geometry fail closed；
- EXIF orientation必須 exactly-once；
- reflection-bearing EXIF 2/5/7需要 reflection-aware transform；
- detector handedness不能建立或覆寫 anatomical-side authority；
- side unresolved不應 overblock source-neutral geometry；
- side-dependent tradition projection在 side unresolved時保持 unresolved。

此 closure只屬 deterministic transform / capability-state contract；real-camera empirical lineage仍 open並移入 B2。

## Current priority map

### Priority A — Admission / uncertainty

#### A1. Task-specific line-detail quality calibration — OPEN AS CALIBRATION / NATURAL-FIELD FOLLOW-UP

第一輪 necessity / sensitivity node已 boundedly closed；仍 open：

- natural low-quality photos；
- glare / uneven illumination / JPEG / crop / occlusion；
- held-out admission calibration；
- production sufficient / partial / insufficient boundaries。

目前不應在既有 9-source synthetic degradation結果上 post-hoc挑 threshold。

#### A2. Uncertainty composition — BOUNDEDLY CLOSED

不需重跑相同 12-case validator；若未來 schema promotion才另開 production validation。

### Priority B — Runtime / capture portability

#### B1a. MediaPipe 1.0.1 vs 1.0.0 runtime package portability — BOUNDEDLY CLOSED

Pinned-model controlled 2D geometry node已關閉。

#### B1b. Hand Landmarker model artifact version portability — OPEN

目前仍只固定：

```text
SHA256 fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1
```

若要升級 model artifact，必須把 model bytes當 primary variable另做 comparison，不能用 runtime-only結果代替。

#### B1c. Broader/future MediaPipe runtime versions — OPEN / DEFER UNTIL NEEDED

沒有必要在沒有 upgrade需求時無限掃版本。應在實際 runtime migration candidate出現時再 predeclare pairwise study。

#### B2. Device-to-device / capture-condition repeatability — OPEN / HIGHEST-VALUE NEXT EMPIRICAL NODE

MOHI已提供 same-palm multi-session repeated-capture evidence，但沒有 controlled multi-device identity。

B3a現在已先固定 deterministic mirror/orientation contract，因此 B2可以沿用明確 lineage fields，不再把以下因素混成未知 confound：

```text
stored-file mirror
preview mirror
EXIF orientation
model-only mirror
anatomical-side evidence
```

B2仍需要：

- same palm under multiple known devices；
- controlled distance / pose / illumination / exposure families；
- explicit stored/preview/EXIF/model transform lineage；
- device/session-held-out summaries；
- capture provenance；
- no biometric identity claims。

B2也應承接 real-camera empirical mirror/orientation validation，例如：

- Android / iOS front-camera preview-vs-file behavior；
- OEM / app-specific EXIF correctness；
- real-device orientation metadata correctness。

#### B3a. Camera / selfie mirroring + anatomical-side deterministic contract — BOUNDEDLY CLOSED

Synthetic asymmetric-geometry / capability-state validator已達 predeclared closure criterion。

不要重跑同一 12-case validator來替代 real-device evidence。

#### B3b. Real-camera capture lineage — OPEN / FOLDED INTO B2

仍未 empirical驗證：

```text
sensor / device orientation metadata
front-camera preview mirror
stored-file mirror
EXIF implementation correctness
app export behavior
user side-assertion provenance
```

此部分應與 B2一起做 controlled capture study。

### Priority C — Feature / tradition expansion

#### C1. Chinese source-specific projection geometry — OPEN

不得由 Western CV class直接推導掌宮 / 八卦等幾何。

#### C2. Minor lines / named patterns — OPEN

branch / island / star / fate line / mounts等仍缺 observation detector evidence。

#### C3. Western ↔ Chinese terminology mapping — OPEN / PROHIBITED ASSUMPTION

`heart/head/life`不得自動等同`天／人／地紋`。

### Priority D — Promotion-only

仍 defer：

- production admission threshold；
- production routing；
- behavioral regression；
- cross-divination production arbitration。

## Recommended next node

目前 dependency-centrality最高、且真正需要新增 empirical evidence 的下一個 bounded node：

> **B2 controlled device / capture-condition repeatability with explicit capture-lineage recording**

理由：

1. A2 uncertainty composition已 boundedly closed；
2. B1a pinned runtime pair已排除目前 1.0.1 vs 1.0.0 的 2D geometry drift；
3. B3a已固定 deterministic mirror / EXIF / anatomical-side contract；
4. 下一個主要未知量因此集中到 real device / capture pipeline，而不是 schema semantics；
5. B2可以同時驗證 device-to-device repeatability與 B3b real-camera lineage assumptions。

建議順序：

```text
B2 controlled device/capture repeatability + real-camera lineage
→ B1b model-artifact portability（只有實際 candidate model出現時）
→ A1 natural low-quality calibration
→ C-level feature/tradition expansion
```

## Boundary

本 roadmap不建立 production rule，也不把 exact-zero runtime result或 12-case synthetic transform result外推成 general field-camera certification。

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**。
