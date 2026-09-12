# Palmistry Evidence Gap Reprioritization — 2026-09-12

Status: **REFERENCE-ONLY / COLD RESEARCH ROADMAP / NO PRODUCTION PROMOTION**

## Purpose

本文件在 principal-line segmentation bounded evidence node 關閉後，重新盤點 Palmistry observation research 的 evidence gaps。

本盤點只依既有 repository evidence 分類 `closed / partially addressed / open`，不把研究結果提升為 production rule，也不修改 ordinary reading routing。

## Newly closed or materially advanced nodes

### 1. Natural two-hand observability sequence-held-out validation — CLOSED AS BOUNDED EVIDENCE

`GTEA_SEQUENCE_HELDOUT_RESULTS.md` 已完成 556 eligible frames / 25 sequences 的 whole-sequence validation。

Primary directional preservation：

- `area_ratio`: 22 / 24 informative sequences = 91.7%
- `min_area_frac`: 18 / 24 informative sequences = 75.0%

此結果支持 visible-area balance 是目前較強的 natural observability feature family，但不建立 numeric admission threshold。

### 2. Natural retained-two association near-tie screen — CLOSED AS NEGATIVE NATURAL REPRODUCTION

`GTEA_NATURAL_NEARTIE_SCREEN.md` 已檢查 170 exactly-two-candidate natural frames。

- best assignment geometric inside-check = 170 / 170 frames；
- minimum best-vs-second assignment gap = 0.1721273612 image diagonals；
- 本 GTEA screen 未重現 controlled synthetic near-tie family。

因此 ambiguity family B 目前 evidence 變成：synthetic 可重現 near-tie / ranking swap，但此 natural GTEA screen 沒有重現 obvious near-tie。仍不得建立 cutoff。

### 3. Same-palm multi-session repeatability — PARTIALLY CLOSED

`MOHI_REPEATABILITY_RESULTS.md` 已完成 10 dataset person IDs × 3 sessions × 5 captures = 150 image entries 的 bounded same-palm multi-session study。

Cross-session pooled means高於 within-session，證明 session change 會增加 observation variation；duplicate-content caveat 亦已 audit closure。

這關閉了「是否有 bounded same-hand repeated-capture evidence」這個問題，但**沒有**關閉 device-to-device、長期 longitudinal、任意 field capture 的 repeatability。

### 4. Detector-to-detector agreement — CLOSED AS BOUNDED EVIDENCE

`DETECTOR_AGREEMENT_RESULTS.md` 已完成 MediaPipe 1.0.1 vs MMPose 1.3.2 / RTMPose-m Hand5 的 corrected raw-frame comparison。

結果支持 detector provenance 必須保留，尤其 palm scale / canonical shape 仍有 material detector-dependent difference；不支持把兩個 detector output 當可互換 ground truth。

### 5. Principal-line segmentation class-specificity — CLOSED AS BOUNDED EVIDENCE NODE

`LINE_SEGMENTATION_EVIDENCE_NODE_CLOSURE.md` 已關閉 shipped `heart_line / head_line / life_line` 是否只是 generic crease activation 的窄問題。

Blind single-observer manual audit 支持 class-specific spatial alignment；P001 blur caveat 以 post-hoc sensitivity 另行保存，不修改 frozen artifact。

## Reclassified remaining gaps

### Priority A — Observation admission / uncertainty composition

#### A1. Task-specific line-detail quality gate — OPEN / HIGHEST VALUE NEXT NODE

`PHOTO_VALIDATION.md` 已證明 global quality flag 不足，必須分 geometry / line-detail / surface-detail / color。

P001 manual-audit caveat 又提供直接 evidence：即使 pipeline 可以執行，模糊影像仍可能使 human reference 本身不可 defensibly trace。

下一步應研究：

- blur / focus / glare / low contrast / partial crop 對 principal-line observability 的影響；
- image-level `line_detail = sufficient / partial / insufficient` 的 fail-closed contract；
- human-observable 與 model-output presence 必須分開，不得用 model activation 自動 rescue 低品質照片；
- 先建立 feature family / protocol，再談 threshold。

此節點優先於繼續增加相同 10-image segmentation rerun。

#### A2. Landmark-frame uncertainty + line-mask uncertainty composition — OPEN / HIGH VALUE

目前已有：

- landmark / canonical-frame transform sensitivity；
- same-palm repeatability；
- cross-detector disagreement；
- principal-line segmentation repeatability與 manual alignment。

但這些 uncertainty 仍各自存在，尚未定義一個 Palm Observation Fact 如何保留／合成：

```text
raw-image frame provenance
+ target-selection uncertainty
+ landmark-frame uncertainty
+ line-mask / line-center uncertainty
+ task-specific image-quality state
```

下一步應先定義 uncertainty provenance schema 與 fail-closed semantics，不要直接壓成單一 confidence score。

### Priority B — Runtime / capture portability

#### B1. MediaPipe runtime / model version compatibility — OPEN

目前所有核心 geometry evidence高度依賴 pinned MediaPipe 1.0.1 + pinned model SHA。

尚未回答不同 MediaPipe Tasks runtime 或 model artifact 版本是否保持：

- candidate counts；
- L0/L5/L17 geometry；
- canonical axis / width / height；
- transform sensitivity；
- handedness metadata behavior。

這是未來可維護性的重要 evidence node，但不需要搶在 quality-gate / uncertainty composition 之前。

#### B2. Device-to-device / capture-condition repeatability — OPEN

MOHI 已提供 multi-session repeated-capture evidence，但目前不是明確的 same-palm multi-device controlled study。

仍需：

- same palm across multiple known devices；
- distance / lighting / exposure / pose families；
- preferably held-out by device or capture session；
- 不使用 person ID 做 biometric identity claim。

#### B3. Camera/selfie mirroring reconciliation + anatomical side contract — PARTIALLY ADDRESSED / OPEN

Normalization contract 已建立 `mirrored_for_model` 與 anatomical side 分離，且 real-image / GTEA evidence 一再顯示 detector handedness 不是 anatomical authority。

尚缺 capture-pipeline 層級的 explicit reconciliation：

```text
raw sensor/display orientation
+ app preview mirror state
+ stored-file mirror state
+ detector-only mirror
→ anatomical side evidence
```

### Priority C — Interpretation-layer expansion

#### C1. Chinese source-specific projection geometry — OPEN

Bagua / palm-palace 等 projection 仍缺 source-specific executable geometry。這不應由 Western CV classes 推導。

#### C2. Named patterns / minor marks detector evidence — OPEN

branch / island / star / fate line / mounts 等仍缺足夠 observation detector evidence。主線模型的成功不得外推到這些 feature。

#### C3. Western ↔ Chinese terminology mapping — OPEN / PROHIBITED ASSUMPTION REMAINS

`heart/head/life` 不得自動映射成 `天／人／地紋`；任何 mapping 必須另有 tradition-specific authority 與 anatomical scope evidence。

### Priority D — Promotion-only gates

以下目前不應成為下一個研究節點，因為上游 observation contract 尚未足夠成熟：

- production numeric admission thresholds；
- production routing；
- Palmistry behavioral regression against Tarot / Meihua / Liuyao；
- production cutoff calibration。

這些只有在明確 promotion candidate 存在後才有意義。

## Recommended next node

目前最高 value / dependency-centrality 的下一個 bounded node：

> **Principal-line / Palm Observation task-specific image-quality admission study**

理由：

1. `PHOTO_VALIDATION.md` 已在 schema 層預告 task-specific quality gate；
2. P001 blur caveat 已實際證明「pipeline 可跑」與「可 defensibly observe」不是同一件事；
3. principal-line segmentation class-specificity 已有 bounded positive evidence，下一個 bottleneck 不再是 class identity，而是何時應拒絕／降級 observation；
4. quality state 是後續 uncertainty composition、device portability、production threshold 的前置依賴。

第二順位為 **uncertainty composition contract**；第三順位為 **runtime/model compatibility matrix**。

## Boundary

本 roadmap 不建立任何 production threshold，也不 promotion Palmistry routing。

Palmistry 維持：

**REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**。
