# Palmistry Research Synthesis｜手相參考收斂

Status: **REFERENCE-ONLY｜僅供參考**

本檔只收斂 external / Cold evidence，不建立 production Palmistry capability，也不修改 `METHOD_ROUTING.md`、`PLAYBOOK_INDEX.json`、`CHAT_INIT.md` 或既有 Tarot / Meihua / Liuyao contract。

## Architecture conclusion

目前 evidence 支持：

```text
Scene / Target Selection Gate
→ Task-specific Image Quality Gate
→ Model Adapter
→ Raw-image Observation Geometry
→ Canonical Palm Coordinates
→ Palm Observation Fact
→ Tradition-specific Projection
→ Tradition-specific Interpretation
→ User-visible synthesis
```

責任邊界：detector preprocessing / mirror / resize 是 adapter implementation detail；detector output 要能 inverse 回 raw-image geometry，才可進 canonical observation；anatomical hand side 與 detector handedness / `mirrored_for_model` 分開；observation fact 與 tradition interpretation 分開；frame-level uncertainty 不能只看單 landmark confidence；traditional source 不取得 image observation authority；CV detector class 不取得 Chinese terminology authority。

## Source-neutral coordinate frame

Draft anchors：`L0 wrist`、`L5 index MCP`、`L17 little MCP`。wrist→MCP midpoint 定義 longitudinal axis；little→index MCP 的正交分量定義 transverse axis；palm height / width normalization。此 frame 只代表 geometry，不代表 Western line label 或中國掌宮。

Ideal synthetic invariant probe：`11 passed / 0 failed`。

Controlled simultaneous-anchor sensitivity sweep：

| Per-anchor bound | Axis angle | Width error | Height error | Max canonical drift |
|---:|---:|---:|---:|---:|
| 0.25% | 0.2865° | 0.500% | 0.500% | 0.527% |
| 0.50% | 0.5729° | 1.001% | 1.000% | 1.059% |
| 1.00% | 1.1458° | 2.005% | 2.000% | 2.135% |
| 2.00% | 2.2906° | 4.019% | 4.000% | 4.341% |
| 5.00% | 5.7106° | 10.112% | 10.000% | 11.445% |

這些只是 configured-grid synthetic evidence，不是 production thresholds。若 detector-only mirror 漏 inverse，在 canonical `x∈[-0.5,0.5]` frame 上可形成 100% max drift；mirror lineage 因此是 admission gate，不是 optional metadata。

## Real-image MediaPipe evidence

Pinned research baseline：

```text
MediaPipe 1.0.1
Python 3.12.14
OpenCV 5.0.0
Hand Landmarker float16/1
model SHA256 fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1
```

### Case A — single palm

`Right Hand Palm.png` / CC BY-SA 4.0。Max canonical drift：same pixels `0%`、rotate +10° `7.3708%`、rotate -10° `4.7228%`、scale 0.75× `1.0967%`、scale 1.25× `2.4488%`、crop 3% `1.6727%`、horizontal mirror `2.9833%`。Mirror handedness `Right → Left`。

### Case B — overlapping two-palm scene

`Open Palm of the Left Hand, Fingers.jpg` / CC BY-SA 4.0。Scene 視覺上有兩掌，但 baseline 與 transforms 都只回 1 candidate。Max canonical drift：same pixels `0%`、rotate +10° `2.1408%`、rotate -10° `8.8829%`、scale 0.75× `4.0574%`、scale 1.25× `1.6918%`、crop 3% `9.2687%`、horizontal mirror `77.3400%`。Mirror handedness `Left → Right`；不能解讀為 anatomical-side evidence。

### Public multi-hand bounded screen

[`MULTI_HAND_FIXTURE_SCREEN.md`](MULTI_HAND_FIXTURE_SCREEN.md) 用相同 pinned runtime/model 與固定 `0.5` thresholds 篩選 4 個視覺上有 2–3 hands 的 public scenes，baseline candidate counts 為 `0 / 1 / 1 / 0`。因此 human-visible hand count不能替代 detector candidate evidence；沒有為了湊 `>=2` 而降低 threshold。

### Case C — upstream MediaPipe multi-hand fixture

[`UPSTREAM_MULTI_HAND_ASSOCIATION.md`](UPSTREAM_MULTI_HAND_ASSOCIATION.md) 使用 MediaPipe 官方 `right_hands.jpg` test fixture：upstream revision `8dd04551858308f3003ace87632d7308d6a62212`、fixture SHA256 `4b5134daa4cb60465535239535f9f74c2842aba3aa5fd30bf04ef5678f93d87f`、research run `34614749960`。

Pinned Python runtime 得到 baseline 2 candidates，7 個 controlled variants也全部 2 candidates。Candidate index會在 rotate / crop / mirror 後從 baseline index `0` 變成 selected index `1`，所以 list position不能當 scene-local identity。Best-vs-second-best separation約 `3.93–3.97 palm widths`；Case C是乾淨 association正例，但不是 ambiguity stress case。

### Candidate-count instability stress

[`ASSOCIATION_AMBIGUITY_STRESS.md`](ASSOCIATION_AMBIGUITY_STRESS.md) 以 Case C來源手建立 synthetic twin-hand composite，固定 detector thresholds。Research run `34615812360`。

Requested duplicate separation與 detector candidate count：

```text
2.50W → 2
2.00W → 2
1.50W → 1
1.25W → 2
1.00W → 1
0.75W and below → 1
```

因此 candidate collapse / recovery非單調。這支持 qualitative fail-closed principle：expected multi-target scene + detector candidate-count instability / collapse → association unresolved → target-specific fine geometry fail closed。這不是 production numeric threshold。

### Retained-two-candidate near-tie stress

[`RETAINED_TWO_CANDIDATE_NEAR_TIE.md`](RETAINED_TWO_CANDIDATE_NEAR_TIE.md) 使用同一 source hand的兩份 identical copies，requested pair separation固定 `2.00W`，只掃 pair center bias。Research run `34616780936`。

Requested composition geometry與 detector post-execution observations分開保存。Requested `2.00W`不是 measured actual；detector實測 pair distance約在 `2.020–2.043W`。

所有 11個 bias points都保留 2 candidates。最小 observed score gap出現在 requested center bias `0.00W`：

```text
observed pair distance      ≈ 2.0216W
best mean distance          ≈ 0.9901W
second-best mean distance   ≈ 1.0339W
score gap                   ≈ 0.04375W
candidate count             = 2
```

在 `+0.05W`時仍保留 2 candidates，score gap約 `0.05205W`，但 best index由 `0`變成 `1`。因此 retained-two-candidate ambiguity family已真正 exercised。

### Natural GTEA two-hand reproduction

[`GTEA_NATURAL_TWO_HAND_REPRODUCTION.md`](GTEA_NATURAL_TWO_HAND_REPRODUCTION.md) 以 GTEA `s2_coffee` direct XML `Left hand + Right hand`定義 36個 GT-two-hand annotation samples。Palm-detector stage實測 `0/1/2 candidates = 1/18/17`，相鄰 selected samples有 18次 count transition；corrected full Hand Landmarker run也確認同一批 samples同時存在 `>=2` retention、`<2` loss與 count transition。Candidate-count instability因此不再只是 synthetic-composite artifact。

### Natural feature study

[`GTEA_NATURAL_FEATURE_STUDY.md`](GTEA_NATURAL_FEATURE_STUDY.md) 從 556個 direct-XML GTEA雙手候選池中 deterministic sample 240 frames，使用相同 pinned full Hand Landmarker。Final candidate distribution：

```text
0 candidates = 42
1 candidate  = 129
2 candidates = 69
```

Retained-2 vs lost-0/1的 strongest univariate signals：

```text
area_ratio median          0.719 vs 0.512   (AUC≈0.682)
smaller-hand area fraction 4.69% vs 3.66%   (AUC≈0.657)
```

相反地，centroid separation、全圖 brightness與 blur在此 bounded sample的單變量分離能力很弱；因此不能把「越近／越暗／越模糊就越容易 candidate loss」提升成單調規則。

### Sequence-held-out natural observability validation

[`GTEA_SEQUENCE_HELDOUT_RESULTS.md`](GTEA_SEQUENCE_HELDOUT_RESULTS.md) 已用完整 556 eligible frames / 25 sequences做 whole-sequence validation。24個 informative sequences中：

```text
area_ratio retained>lost direction      22 / 24 = 91.7%
min_area_frac retained>lost direction   18 / 24 = 75.0%
```

因此 visible-area balance目前是較強的 natural observability feature family；smaller-hand relative scale是次要、較 sequence-dependent的 signal。結果仍有 heterogeneity，沒有建立 numeric cutoff。

### Natural retained-two association screen

[`GTEA_NATURAL_NEARTIE_SCREEN.md`](GTEA_NATURAL_NEARTIE_SCREEN.md) 對 170個 exactly-two-candidate natural frames做 scene-local association screen：

```text
best-assigned palm centers inside XML polygons = 170 / 170
minimum best-vs-second assignment gap          = 0.1721273612 image diagonals
10th percentile gap                            = 0.2751062265
median gap                                     = 0.4410073321
```

此 natural GTEA screen沒有重現 synthetic near-tie family。這是 negative natural reproduction result，不是 threshold；candidate list A/B reorder仍不能解讀成 identity swap。

### MOHI same-palm multi-session repeatability

[`MOHI_REPEATABILITY_RESULTS.md`](MOHI_REPEATABILITY_RESULTS.md) 已完成 10 dataset person IDs × 3 sessions × 5 captures = 150 image entries的 bounded multi-session study，且 duplicate-content integrity audit已閉合。

代表性 pooled mean：

```text
anchor mean drift       0.05056 within → 0.07216 cross-session
canonical mean drift    0.05882 within → 0.07599 cross-session
axis angle delta        7.14° within   → 10.26° cross-session
```

因此 same-palm recapture並非 perfect invariant，session change帶來額外 observation variation。此結果不是 device-to-device或 biometric identity evidence。

### Detector-to-detector agreement

[`DETECTOR_AGREEMENT_RESULTS.md`](DETECTOR_AGREEMENT_RESULTS.md) 已完成 corrected raw-image frame下的 MediaPipe 1.0.1 vs MMPose 1.3.2 / RTMPose-m Hand5 comparison。

兩 detector對 gross palm-axis direction相對接近，但 palm width、height與 canonical shape保留 material detector-dependent差異；因此 `detector_id / detector_version / model artifact / raw-frame policy`必須保留，兩套 geometry不能靜默互換。

### Principal-line segmentation evidence node

[`LINE_SEGMENTATION_EVIDENCE_NODE_CLOSURE.md`](LINE_SEGMENTATION_EVIDENCE_NODE_CLOSURE.md) 已關閉 shipped `heart_line / head_line / life_line`是否只是 generic crease activation的 bounded question。

Frozen blind single-observer manual audit在 8 px tolerance下：

| class | mean harmonic coverage | median | wrong-class exceeds correct |
|---|---:|---:|---:|
| `heart_line` | 0.9036458631 | 0.9735923680 | 0 / 10 |
| `head_line` | 0.9137675861 | 0.9572269111 | 0 / 10 |
| `life_line` | 0.7906154111 | 0.8158573054 | 0 / 10 |

P001因影像過於模糊、人工 trace部分依推測完成，已另以 post-hoc sensitivity保存，不能視為 clean model-failure case。此節點支持 bounded class-specific spatial alignment，不建立 anatomical truth或 Palmistry interpretation validity。

## Cross-case conclusions

目前 executable / real-image / stress evidence支持：

1. same-pixels deterministic不等於 transform invariant；
2. exact inverse transform只能消除已知 image-space transform，不能消除 detector sensitivity；
3. rotation / crop / scale error具有 image/context dependency；
4. detector handedness / mirror output不是 anatomical hand-side fact；
5. overlapping-hand context可極大放大 mirror instability；
6. synthetic sensitivity numbers不能直接當 real-image cutoff；
7. human-visible hand count不能替代 detector candidate evidence；
8. candidate list index不能當 scene-local hand identity；
9. best / second-best inverse-mapped distance與 separation應被保留；
10. association uncertainty不能只靠 score gap，因為第二 candidate可能直接消失；
11. candidate-count instability / disappearance / reappearance本身是獨立 uncertainty signal，且已在 natural capture重現；
12. hand proximity與 detector ambiguity不是單調函數；
13. controlled synthetic near-tie / ranking swap可重現，但 natural GTEA retained-two screen未重現 obvious near-tie；
14. requested composition input與 detector-observed actual必須保持 evidence boundary，不得混寫；
15. natural two-hand observability以 visible-area balance目前具有最穩定的 cross-sequence方向 evidence，但仍不是 production gate；
16. same-palm multi-session evidence顯示 cross-session variation高於 within-session，不能把單次 geometry當 invariant；
17. cross-detector evidence顯示 palm-axis方向可近似一致，但 scale / canonical shape仍有 detector provenance依賴；
18. principal-line segmentation在 bounded blind audit中具有 class-specific spatial alignment，不符合純 generic crease detector的較弱解釋；
19. `pipeline executes`不等於 `observation is defensible`：P001 blur caveat直接暴露 line-detail quality gate的重要性；
20. observation uncertainty目前仍分散在 target selection、landmark frame、line mask與 image quality，不能直接壓成單一 confidence score。

## Traditional interpretation boundary

中國與西方 source normalization維持：Cheiro只代表 Western tradition；`SXQ-640` / `TQ-V5` / `TGKD`為中國傳統 provenance anchors；`SXQ-640`與 `TQ-V5`的近似段落不能機械視為獨立 corroboration；`天／人／地紋 ↔ heart/head/life`、`玉柱紋 ↔ fate line`仍為 `PROHIBITED_ASSUMPTION`；named pattern必須保留 source / anatomical scope / geometry basis。

## Evidence-gap status after 2026-09-12 closure

詳細排序見 [`PALMISTRY_EVIDENCE_GAP_REPRIORITIZATION_20260912.md`](PALMISTRY_EVIDENCE_GAP_REPRIORITIZATION_20260912.md)。

### Closed / materially advanced bounded nodes

- sequence-held-out natural observability validation：**closed as bounded evidence**；
- natural retained-two near-tie screen：**closed as negative natural reproduction**；
- same-palm multi-session repeatability：**partially closed**，device-to-device仍 open；
- detector-to-detector agreement：**closed as bounded evidence**；
- principal-line segmentation class-specificity：**closed as bounded evidence node**。

### Priority A — observation admission / uncertainty

1. **Task-specific line-detail image-quality gate**：open，最高優先；
2. **landmark-frame uncertainty + line-mask uncertainty composition**：open，高優先。

### Priority B — portability

3. MediaPipe runtime / model-version compatibility matrix：open；
4. same-palm device-to-device / capture-condition repeatability：open；
5. camera/selfie mirroring reconciliation + anatomical-side contract：partially addressed / open。

### Priority C — interpretation-layer expansion

6. Bagua / palm-palace source-specific projection geometry：open；
7. branch / island / star / minor lines / mounts等 detector evidence：open；
8. Western `heart/head/life` ↔ Chinese terminology mapping：open，且 prohibited assumption持續有效；
9. named patterns / illustrated marks mapping：open。

### Promotion-only gates

10. production numeric admission thresholds；
11. production cutoff calibration；
12. Palmistry behavioral regression與 production routing。

上述 promotion-only項目現在不是下一個研究節點；只有明確 promotion candidate存在後才值得執行。

## Adoption decision

所有 Palmistry external sources、schema、normalization contracts、synthetic probes、MediaPipe runners、MOHI/GTEA studies、detector-agreement與 principal-line segmentation evidence仍為 **REFERENCE-ONLY / DRAFT**；production method set不變。

Association ambiguity family A已有 synthetic + natural candidate-loss evidence並完成 sequence-held-out方向驗證；family B已有 synthetic near-tie正例與 natural GTEA negative reproduction screen。Principal-line segmentation的 class-specificity bounded question亦已 closure。

目前下一個 dependency-central bounded research node改為：

> **Principal-line / Palm Observation task-specific image-quality admission study**

其後依序為：

1. uncertainty composition contract；
2. MediaPipe runtime/model compatibility matrix；
3. controlled device-to-device repeatability。

現在仍不建立 production threshold，也不 promotion Palmistry routing。
