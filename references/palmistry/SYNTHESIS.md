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

[`MULTI_HAND_FIXTURE_SCREEN.md`](MULTI_HAND_FIXTURE_SCREEN.md) 用相同 pinned runtime/model 與固定 `0.5` thresholds 篩選 4 個視覺上有 2–3 hands 的 public scenes，baseline candidate counts 為 `0 / 1 / 1 / 0`。因此 human-visible hand count 不能替代 detector candidate evidence；沒有為了湊 `>=2` 而降低 threshold。

### Case C — upstream MediaPipe multi-hand fixture

[`UPSTREAM_MULTI_HAND_ASSOCIATION.md`](UPSTREAM_MULTI_HAND_ASSOCIATION.md) 使用 MediaPipe 官方 `right_hands.jpg` test fixture：upstream revision `8dd04551858308f3003ace87632d7308d6a62212`、fixture SHA256 `4b5134daa4cb60465535239535f9f74c2842aba3aa5fd30bf04ef5678f93d87f`、research run `34614749960`。

Pinned Python runtime 得到 baseline 2 candidates，7 個 controlled variants 也全部 2 candidates。Candidate index 會在 rotate / crop / mirror 後從 baseline index `0` 變成 selected index `1`，所以 list position 不能當 scene-local identity。Best-vs-second-best separation 約 `3.93–3.97 palm widths`；Case C 是乾淨 association 正例，但不是 ambiguity stress case。

### Candidate-count instability stress

[`ASSOCIATION_AMBIGUITY_STRESS.md`](ASSOCIATION_AMBIGUITY_STRESS.md) 以 Case C 來源手建立 synthetic twin-hand composite，固定 detector thresholds。Research run `34615812360`。

Requested duplicate separation 與 detector candidate count：

```text
2.50W → 2
2.00W → 2
1.50W → 1
1.25W → 2
1.00W → 1
0.75W and below → 1
```

因此 candidate collapse / recovery 非單調。這支持 qualitative fail-closed principle：expected multi-target scene + detector candidate-count instability / collapse → association unresolved → target-specific fine geometry fail closed。這不是 production numeric threshold。

### Retained-two-candidate near-tie stress

[`RETAINED_TWO_CANDIDATE_NEAR_TIE.md`](RETAINED_TWO_CANDIDATE_NEAR_TIE.md) 使用同一 source hand 的兩份 identical copies，requested pair separation 固定 `2.00W`，只掃 pair center bias。Research run `34616780936`。

Requested composition geometry 與 detector post-execution observations分開保存。Requested `2.00W` 不是 measured actual；detector實測 pair distance約在 `2.020–2.043W`。

所有 11 個 bias points 都保留 2 candidates。最小 observed score gap 出現在 requested center bias `0.00W`：

```text
observed pair distance      ≈ 2.0216W
best mean distance          ≈ 0.9901W
second-best mean distance   ≈ 1.0339W
score gap                   ≈ 0.04375W
candidate count             = 2
```

在 `+0.05W` 時仍保留 2 candidates，score gap約 `0.05205W`，但 best index由 `0` 變成 `1`。因此 retained-two-candidate ambiguity family 已真正 exercised。

### Natural GTEA two-hand reproduction

[`GTEA_NATURAL_TWO_HAND_REPRODUCTION.md`](GTEA_NATURAL_TWO_HAND_REPRODUCTION.md) 以 GTEA `s2_coffee` direct XML `Left hand + Right hand` 定義 36 個 GT-two-hand annotation samples。Palm-detector stage 實測 `0/1/2 candidates = 1/18/17`，相鄰 selected samples有 18 次 count transition；corrected full Hand Landmarker run也確認同一批 samples 同時存在 `>=2` retention、`<2` loss與 count transition。Candidate-count instability 因此不再只是 synthetic-composite artifact。

### Natural feature study

[`GTEA_NATURAL_FEATURE_STUDY.md`](GTEA_NATURAL_FEATURE_STUDY.md) 從 556 個 direct-XML GTEA 雙手候選池中 deterministic sample 240 frames，使用相同 pinned full Hand Landmarker。Final candidate distribution：

```text
0 candidates = 42
1 candidate  = 129
2 candidates = 69
```

Retained-2 vs lost-0/1 的 strongest univariate signals：

```text
area_ratio median          0.719 vs 0.512   (AUC≈0.682)
smaller-hand area fraction 4.69% vs 3.66%   (AUC≈0.657)
```

這支持「可見手尺寸平衡」與「較小手是否足夠大」作為未來 observability gate 的候選 feature family，但不支持任何 numeric cutoff。

相反地，本 sample 中：

```text
centroid separation median 0.37408 vs 0.37455 image diagonals
frame brightness           111.30 vs 111.98
blur                       101.22 vs 99.78
```

幾乎沒有單變量分離能力。`min_poly_gap_diag` 甚至在 retained-2 組更小（`0.0743` vs `0.0954`），因此不能把「兩手越近越容易 collapse」提升成單調規則。Reported p-values 只是 exploratory / uncorrected，而且 temporal frames 並非 independent-IID observations。

## Cross-case conclusions

目前 executable / real-image / stress evidence 支持：

1. same-pixels deterministic 不等於 transform invariant；
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
13. 即使 candidate count穩定，best/second gap也可能縮小到 near-tie，且 ranking可在小 perturbation後 swap；
14. requested composition input與 detector-observed actual必須保持 evidence boundary，不得混寫；
15. natural two-hand observability較值得優先追蹤 relative smaller-hand scale / visible-area balance，而不是單獨依賴 centroid separation、全圖亮度或 blur；
16. exploratory feature association不能直接變成 production quality threshold，仍需 sequence-held-out calibration。

## Traditional interpretation boundary

中國與西方 source normalization維持：Cheiro只代表 Western tradition；`SXQ-640` / `TQ-V5` / `TGKD` 為中國傳統 provenance anchors；`SXQ-640` 與 `TQ-V5` 的近似段落不能機械視為獨立 corroboration；`天／人／地紋 ↔ heart/head/life`、`玉柱紋 ↔ fate line` 仍為 `PROHIBITED_ASSUMPTION`；named pattern 必須保留 source / anatomical scope / geometry basis。

## Remaining evidence gaps

目前仍不足以 promotion：

1. sequence-held-out validation：size balance / smaller-hand scale / truncation feature family是否跨 GTEA sequence 維持 ordering；
2. natural retained-two-candidate near-tie / ranking-swap distribution；
3. predeclared ambiguity admission contract與可辯護 threshold；
4. 多張不同 hand shapes / capture contexts 的 transform-consistency distribution；
5. same hand / multiple captures 的 pose / distance / lighting / device repeatability；
6. camera/selfie mirroring reconciliation 與 anatomical side contract；
7. MediaPipe model/runtime version compatibility；
8. detector-to-detector agreement；
9. branch / island / star / minor lines / mounts 等 detector evidence；
10. palm-line segmentation uncertainty 與 landmark-frame uncertainty 的合成方式；
11. Bagua / palm-palace source-specific projection geometry；
12. named patterns / illustrated marks unresolved mapping；
13. production numeric admission thresholds；
14. Palmistry behavioral regression，證明 promotion 不影響 Tarot / Meihua / Liuyao routing。

## Adoption decision

所有 Palmistry external sources、schema、normalization contracts、synthetic probes、MediaPipe runners與 real-image results 仍為 **REFERENCE-ONLY / DRAFT**；production method set 不變。

Association ambiguity family A（candidate-count collapse / instability）現在已有 synthetic 與 natural evidence；family B（retained-two-candidate near-tie / ranking swap）目前仍只有 controlled synthetic evidence。下一個 bounded research node應優先做 **sequence-held-out natural observability validation**，並從 retained-two natural frames screen near-tie / ranking stability；現在仍不建立 production threshold，也不 promotion Palmistry routing。
