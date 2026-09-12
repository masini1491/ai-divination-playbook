# Palmistry Evidence Gap Reprioritization — 2026-09-12

Status: **REFERENCE-ONLY / COLD RESEARCH ROADMAP / NO PRODUCTION PROMOTION**

## Purpose

本文件在 principal-line segmentation bounded evidence node 與第一輪 line-detail quality-sensitivity node 關閉後，重新盤點 Palmistry observation research 的 evidence gaps。

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

### 6. Principal-line line-detail quality sensitivity — CLOSED AS FIRST BOUNDED QUALITY NODE

`LINE_DETAIL_QUALITY_GATE_RESULTS.md` 已完成 P002–P010 共 9 張 primary sources × 10 conditions = 90 inference conditions。

第一輪 controlled degradation 支持：

- blur / effective-resolution destruction 可造成 class presence collapse 與 manual-reference agreement materially下降；
- contrast factor 0.25 即使 heart/head/life 均仍 9/9 present，heart/head agreement 與 centerline-distance 已明顯惡化；
- 因此 `model class present` 不能當成自己的 image-quality certificate；
- Laplacian / Tenengrad / Sobel 與 RMS contrast 應作不同 evidence families 保存，而不是壓成單一未驗證 score。

此 node **沒有**建立 production quality cutoff。

## Reclassified remaining gaps

### Priority A — Observation admission / uncertainty composition

#### A1. Task-specific line-detail quality gate — BOUNDEDLY CLOSED / CALIBRATION REMAINS OPEN

第一輪 bounded quality-sensitivity question 已由 `LINE_DETAIL_QUALITY_GATE_RESULTS.md` 回答。

已支持：

- task-specific `line_detail` evidence 是必要的；
- model presence 不得 override quality gate；
- focus/detail 與 photometric contrast 應保留為不同 evidence families；
- severe blur / severe resolution destruction 可形成 clear bounded failure regimes。

仍未回答：

- held-out numeric threshold calibration；
- natural low-quality photo validation beyond P001 descriptive evidence；
- glare / uneven illumination / JPEG / crop / occlusion families；
- production `sufficient / partial / insufficient` boundaries。

因此不再把「是否需要 line-detail gate」列為 open，但 calibration / natural-field validation 仍保留 open。

#### A2. Landmark-frame uncertainty + line-mask uncertainty composition — OPEN / HIGHEST VALUE NEXT NODE

目前已有：

- scene / target-selection ambiguity evidence；
- task-specific quality schema與第一輪 line-detail sensitivity results；
- landmark / canonical-frame transform sensitivity；
- same-palm repeatability；
- cross-detector disagreement；
- principal-line segmentation repeatability與 manual alignment。

現在 bottleneck 變成如何把這些 heterogenous uncertainty 保存在一個 Palm Observation Fact，而不產生偽精確的 single confidence score：

```text
raw-image frame provenance
+ target-selection uncertainty
+ task-specific image-quality state
+ landmark-frame uncertainty
+ line-mask / line-center uncertainty
+ tradition-projection uncertainty
```

`OBSERVATION_UNCERTAINTY_COMPOSITION_DRAFT.md` 已建立 conceptual contract；下一個 bounded node 應做 schema/behavior validation，而不是再回頭重跑相同 segmentation sample。

### Priority B — Runtime / capture portability

#### B1. MediaPipe runtime / model version compatibility — OPEN / PREDECLARED

`MEDIAPIPE_RUNTIME_MODEL_COMPATIBILITY_PLAN.md` 已建立 predeclared plan，但 empirical compatibility execution 尚未完成。

目前所有核心 geometry evidence高度依賴 pinned MediaPipe 1.0.1 + pinned model SHA。

尚未回答不同 MediaPipe Tasks runtime 或 model artifact 版本是否保持：

- candidate counts；
- L0/L5/L17 geometry；
- canonical axis / width / height；
- transform sensitivity；
- handedness metadata behavior；
- raw-frame / EXIF orientation semantics。

此 node 仍是高價值 portability 問題，但順位低於 uncertainty composition contract validation。

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

> **Palm Observation uncertainty-composition contract validation**

理由：

1. line-detail quality necessity 已有 bounded empirical support，不需要再把同一 9-source synthetic degradation node擴大成 threshold hunt；
2. scene-target、quality、landmark-frame、feature-extraction uncertainty 已各自有 evidence，但還沒有經過 behavior/schema validation 的 composition contract；
3. 未來任何 production admission、device portability 或 tradition projection 都需要先知道 uncertainty 如何 fail closed、如何保持 provenance、哪些 layer 不可互相 rescue；
4. `OBSERVATION_UNCERTAINTY_COMPOSITION_DRAFT.md` 已有 draft，可直接轉成下一個 predeclared validation node。

第二順位為 **MediaPipe runtime/model compatibility execution**；第三順位為 **device-to-device / capture-condition repeatability**。

Line-detail 下一輪若要重開，應以 **natural low-quality / held-out calibration** 為新 node，而不是在目前 9-source結果上直接挑 cutoff。

## Boundary

本 roadmap 不建立任何 production threshold，也不 promotion Palmistry routing。

Palmistry 維持：

**REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**。
