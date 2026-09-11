# Palmistry References

本目錄保存手相（Palmistry）相關的外部 GitHub repository、paper、dataset、computer-vision implementation、真實影像 validation 與傳統判讀資料之 Cold source dossier。

## Authority boundary

放入本目錄的資料預設皆為 `REFERENCE-ONLY`：

- 不自動取得 canonical policy authority；
- 不自動代表 Playbook 已支援該方法或規則；
- 不自動進入 ordinary reading Hot Path；
- 不因 source 看起來合理、熱門或技術可行就直接寫入 `PALMISTRY.md` 的 production rule。

正式採用前應至少記錄 source/ref、license、用途、可驗證 observation 能力、interpretation scope、流派差異與 not-adopted boundary。

## Research synthesis

- [`SYNTHESIS.md`](SYNTHESIS.md) — source comparison、architecture implication、validation state 與 remaining evidence gaps。
- [`CHINESE_RULE_NORMALIZATION.md`](CHINESE_RULE_NORMALIZATION.md) — 《神相全編》／《太清神鑑》／《神相鐵關刀》的 rule-family normalization、lineage guard、術語 namespace 與中西 mapping boundary。
- [`OBSERVATION_SCHEMA_DRAFT.md`](OBSERVATION_SCHEMA_DRAFT.md) — source-neutral Palm Observation Fact draft；scene/target selection、task-specific quality、geometry、unknown semantics、tradition projection 與 privacy boundary。
- [`PHOTO_VALIDATION.md`](PHOTO_VALIDATION.md) — 代表性真實照片 field-coverage / fail-closed validation。
- [`NORMALIZATION_CONTRACT_DRAFT.md`](NORMALIZATION_CONTRACT_DRAFT.md) — raw image → model adapter → raw geometry → canonical palm basis 的 deterministic normalization contract draft。
- [`normalization_probe.py`](normalization_probe.py) — Cold synthetic invariant probe；驗 translation / rotation / scale / mirror / inverse-transform / fail-closed properties，不是 production tool。
- [`SENSITIVITY_SWEEP.md`](SENSITIVITY_SWEEP.md) — L0/L5/L17 controlled perturbation 與 mirror-convention sensitivity；不是 production tolerance。
- [`normalization_sensitivity_probe.py`](normalization_sensitivity_probe.py) — 16-direction / 4096-combination bounded sensitivity executable。
- [`REAL_IMAGE_REPEATABILITY.md`](REAL_IMAGE_REPEATABILITY.md) — MediaPipe Case A/B 真實影像 controlled-transform 結果、provenance、fail-closed interpretation 與 remaining gaps。
- [`MULTI_HAND_FIXTURE_SCREEN.md`](MULTI_HAND_FIXTURE_SCREEN.md) — 固定 MediaPipe baseline 的 public multi-hand fixture bounded screen；記錄 4 個視覺多手場景實際只得到 0/1 candidates 的負面 evidence 與 stop decision。
- [`UPSTREAM_MULTI_HAND_ASSOCIATION.md`](UPSTREAM_MULTI_HAND_ASSOCIATION.md) — MediaPipe 官方 `right_hands.jpg` Case C；實際 baseline/所有 transforms 都輸出 2 candidates，驗 scene-local association、candidate reorder 與 best-vs-second-best separation。
- [`ASSOCIATION_AMBIGUITY_STRESS.md`](ASSOCIATION_AMBIGUITY_STRESS.md) — Case C 衍生的 synthetic twin-hand proximity stress；實測 candidate collapse / reappearance、非單調 multi-candidate behavior 與 fail-closed implication。
- [`RETAINED_TWO_CANDIDATE_NEAR_TIE.md`](RETAINED_TWO_CANDIDATE_NEAR_TIE.md) — 對稱 twin-hand composite；實測兩 candidates 保留、best/second score gap縮至 4.375% palm-width 且 ranking swap。
- [`GTEA_NATURAL_TWO_HAND_REPRODUCTION.md`](GTEA_NATURAL_TWO_HAND_REPRODUCTION.md) — GTEA `s2_coffee` direct-XML Left+Right natural sequence；36 個 GT-two-hand annotation samples 中實測 candidate retention/loss/transition，將 candidate-count instability 從 synthetic evidence 延伸到 natural capture。
- [`GTEA_NATURAL_FEATURE_STUDY.md`](GTEA_NATURAL_FEATURE_STUDY.md) — 556 個 direct-XML GTEA 雙手候選池中的 bounded 240-frame full Hand Landmarker study；比較 retained-2 vs lost-0/1 的面積平衡、較小手尺寸、距離、邊界、亮度與模糊度等自然影像特徵。
- [`GTEA_SEQUENCE_HELDOUT_PLAN.md`](GTEA_SEQUENCE_HELDOUT_PLAN.md) — 在看 held-out 結果前預先凍結 whole-sequence validation 的單位、方向假設、停止規則與 evidence boundary。
- [`GTEA_SEQUENCE_HELDOUT_RESULTS.md`](GTEA_SEQUENCE_HELDOUT_RESULTS.md) — 556 eligible frames / 25 sequences 的 frozen whole-sequence validation；`area_ratio` 在 22/24 informative sequences 維持 retained>lost，`min_area_frac` 為 18/24，保留 sequence-level heterogeneity 且不建立 numeric cutoff。
- [`GTEA_NATURAL_NEARTIE_SCREEN.md`](GTEA_NATURAL_NEARTIE_SCREEN.md) — 170 個 natural retained-two frames 的 XML-polygon geometry association screen；170/170 最佳配對的兩個 palm centers 都落在對應 polygon，最小 best-vs-second assignment gap 為 `0.1721` image diagonal，未重現 synthetic near-tie；candidate-index A/B flips 明確列為 non-evidence。
- [`real_image_repeatability_probe.py`](real_image_repeatability_probe.py) — detector-agnostic metric harness；接收 L0/L5/L17 + inverse transform，計算 anchor / canonical-frame drift。
- [`mediapipe_repeatability_runner.py`](mediapipe_repeatability_runner.py) — Cold research runner；下載 pinned official model + public fixtures、執行 controlled transforms 與 scene-local candidate association；不是 production runtime owner。
- [`association_ambiguity_probe.py`](association_ambiguity_probe.py) — Cold synthetic-composite ambiguity stress runner；不是自然影像分布、不是 biometric identity、不是 production gate。
- [`association_near_tie_probe.py`](association_near_tie_probe.py) — Cold retained-two-candidate near-tie probe；區分 requested composition geometry 與 post-detector observations。

### Observation / CV references

- [`palm-line-reader.md`](palm-line-reader.md) — `samuelwbarber/palm-line-reader`；三大主線 segmentation、shipped ONNX inference contract、reconstructed preprocessing caveat、Reddit-derived training provenance。
- [`yeonsumia-palmistry.md`](yeonsumia-palmistry.md) — `yeonsumia/palmistry`；21-landmark homography rectification、principal-line detection/classification/measurement pipeline，以及 project-specific template / threshold boundary。
- [`palm-astro-application.md`](palm-astro-application.md) — geometry feature concepts；synthetic interpretation 與 unresolved code license 不採用。
- [`tencent-palm-applications.md`](tencent-palm-applications.md) — multimodal product-flow reference；prompt contamination、approximate CV heuristic 與 license inconsistency boundary。

### Interpretation references

- [`palmistry-for-all.md`](palmistry-for-all.md) — Cheiro 的 *Palmistry for All*；Western tradition reference，非中國手相 authority。
- [`chinese-traditional-sources.md`](chinese-traditional-sources.md) — 中國傳統手相 provenance baseline；以《古今圖書集成》所收《神相全編》掌部、《神相鐵關刀》、《太清神鑑》為主要古籍來源。

## Current promotion state

Palmistry 目前仍是 `PALMISTRY.md` 所定義的 **Cold scaffold / not production-routable**。

本目錄增加不修改：

```text
METHOD_ROUTING.md
PLAYBOOK_INDEX.json
CHAT_INIT.md production method set
README production support list
```

Normalization / observation research 目前已完成：

- source-neutral contract draft；
- ideal synthetic invariant probe：11 passed / 0 failed；
- controlled landmark perturbation / mirror sensitivity sweep；
- detector-agnostic repeatability harness self-test；
- pinned MediaPipe `1.0.1` + official Hand Landmarker model 的兩個 public real-image controlled-transform studies；
- public multi-hand fixture bounded screen：4 個視覺上有 2–3 hands 的 fixtures 實際 baseline candidate counts 為 `0 / 1 / 1 / 0`；
- MediaPipe upstream `right_hands.jpg` Case C：baseline 與 7 個 controlled variants 全部穩定輸出 2 candidates，實際 exercised best/second-best association branch；
- candidate index 已證明不是 stable identity：rotate / crop / mirror 可由 baseline index `0` 變成 selected index `1`；
- Case C 的 best-vs-second-best separation 約 `3.93–3.97 palm widths`，因此是乾淨 association 正例；
- synthetic twin-hand proximity stress 已實測 candidate collapse / reappearance：`2.50W→2`、`2.00W→2`、`1.50W→1`、`1.25W→2`、`1.00W 以下→1`，顯示 detector behavior 非單調；
- symmetric retained-two-candidate stress 已實測真正 near-tie：center bias `0.00W` 時仍有 2 candidates，observed pair distance 約 `2.022W`，best/second 約 `0.990W / 1.034W`，score gap約 `0.04375W`；`+0.05W` 時 best index由 `0` 換成 `1`；
- GTEA `s2_coffee` natural sequence 已以 direct XML `Left hand + Right hand` 定義 36 個 GT-two-hand annotation samples；palm-detector stage 實測 `0/1/2 candidates = 1/18/17` 且相鄰 selected samples 有 18 次 count transition；full Hand Landmarker corrected research run 亦確認同一 36 samples 同時存在 `>=2` retention、`<2` loss 與 count transition；
- 擴展 natural feature study 從 556 個 direct-XML GTEA 雙手候選中 deterministic sampling 240 frames；full Hand Landmarker 得 `0/1/2 = 42/129/69`。Retained-2 最強單變量訊號為左右手可見 polygon 面積平衡 (`area_ratio` median `0.719` vs `0.512`) 與較小手面積比例 (`4.69%` vs `3.66%`)；centroid separation、全圖亮度與 blur 幾乎無區分力。這些仍是 exploratory signal，不是 production gate；
- frozen whole-sequence validation 覆蓋全部 556 eligible frames / 25 sequences，final candidate distribution `0/1/2 = 110/276/170`。24 個 informative sequences 中，`area_ratio` 有 `22/24 = 91.7%` 維持 retained>lost 方向，`min_area_frac` 有 `18/24 = 75%`；sequence-level exceptions 被保留，不建立 universal rule；
- natural retained-two association screen 覆蓋全部 170 個 exactly-two frames；geometry-based best assignment 在 170/170 frames 皆有兩個 palm centers 落於各自 XML polygon。Best-vs-second gap 最小 `0.1721`、p10 `0.2751`、median `0.4410` image diagonal，因此此 GTEA screen 未重現 synthetic near-tie。Workflow 中 79 次 candidate-index A/B label flip 不構成 ranking/identity evidence。

真實影像與 stress evidence 已證明：same-pixels deterministic 不代表 rotate / scale / crop / mirror invariant；人眼看到多手不能替代 detector candidate evidence；detector candidate list position 不能當 hand identity；association uncertainty 既要保存 candidate-count instability，也要保存 retained-two-candidate best/second score gap與 ranking stability；candidate-count instability 已不再只是 synthetic-composite artifact。Natural feature evidence 也不支持把「兩手越近越容易 collapse」當單調規則。Natural retained-two GTEA screen 則提供 negative reproduction evidence：在目前 geometry metric 下沒有接近 synthetic near-tie 的案例。

目前仍不能直接設 production threshold。主要 remaining gaps：多 capture / device repeatability、detector-to-detector agreement、line-segmentation uncertainty、可辯護的 predeclared admission calibration 與 behavioral regression。Natural retained-two near-tie 已完成一輪 GTEA negative reproduction screen，但不能外推為自然影像不存在 near-tie。Palmistry 仍不進 router。
