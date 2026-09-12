# Palmistry Evidence Gap Reprioritization — 2026-09-13

Status: **REFERENCE-ONLY / COLD RESEARCH ROADMAP / NO PRODUCTION PROMOTION**

## Purpose

本文件在以下兩個新 bounded closures之後重新排序 Palmistry observation research：

1. Palm Observation uncertainty-composition contract validation；
2. MediaPipe `1.0.1` vs `1.0.0` runtime-only MOHI portability study。

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

#### B2. Device-to-device / capture-condition repeatability — OPEN / HIGH VALUE

MOHI已提供 same-palm multi-session repeated-capture evidence，但沒有 controlled multi-device identity。

需要：

- same palm under multiple known devices；
- controlled distance / pose / illumination / exposure families；
- device/session-held-out summaries；
- capture provenance；
- no biometric identity claims。

#### B3. Camera / selfie mirroring reconciliation + anatomical-side contract — OPEN / DEPENDENCY-CENTRAL

目前已有概念原則：

```text
hand_side != detector handedness
hand_side != mirrored_for_model
```

但缺可執行 capture-lineage contract：

```text
sensor orientation
+ display rotation
+ preview mirror
+ stored-file mirror
+ EXIF orientation
+ detector-only mirror
→ observation frame
→ anatomical-side evidence state
```

這個 contract應在 B2 大規模 device study前先固定，否則跨-device capture可能把 mirror/orientation confound混進 repeatability。

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

目前 dependency-centrality最高、且不需要先找新 dataset 的下一個 bounded node：

> **Camera / selfie mirroring reconciliation + anatomical-side evidence contract**

理由：

1. detector handedness已多次被證明只能當 metadata，不是 anatomical authority；
2. runtime-only portability已排除目前 pinned runtime pair造成的 2D geometry drift；
3. 下一個真正大的 portability問題是 capture/device lineage；
4. 在做 multi-device repeatability前，必須先知道 stored image frame如何由 sensor / preview / EXIF / app mirror轉成 observation frame；
5. 這個 contract可以先用 synthetic asymmetric-hand geometry與 explicit transform cases驗證 fail-closed behavior，不需要等待新的 palm dataset。

建議順序：

```text
B3 capture/mirroring contract validation
→ B2 controlled device/capture repeatability
→ B1b model-artifact portability（只有實際 candidate model出現時）
→ A1 natural low-quality calibration
```

## Boundary

本 roadmap不建立 production rule，也不把 exact-zero runtime result外推成 general MediaPipe certification。

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**。
