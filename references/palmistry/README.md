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
- [`MULTICAPTURE_DATASET_GATE.md`](MULTICAPTURE_DATASET_GATE.md) — independent multi-capture / device repeatability 的 dataset qualification owner；區分 public availability、runtime acquisition、data-use permission 與 capture-domain fit。Tongji/XINHUA 為 contactless multi-session 首選但 permission 尚未閉合；THUPALMLAB 研究用途明確但為 scanner-domain control；MPW-180 是未來 mobile/device 候選但目前 release surface 尚未完成。
- [`THUPALMLAB_DOMAIN_COMPATIBILITY.md`](THUPALMLAB_DOMAIN_COMPATIBILITY.md) — user-supplied THUPALMLAB subject-1 left-palm 8 impressions 的 bounded runtime probe；pinned MediaPipe 1.0.1 / 0.5 / IMAGE baseline 在 8/8 影像皆輸出 0 candidates，因此此 scanner sample 對目前 full-hand canonical observation runtime 為 negative compatibility result；不得外推為 dataset-wide failure。
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

Normalization / observation research 目前已完成 source-neutral contract、synthetic invariants / sensitivity、真實影像 controlled-transform repeatability、multi-hand candidate / association ambiguity、GTEA natural two-hand reproduction / feature study / sequence-held-out validation，以及 natural retained-two near-tie negative reproduction screen。

Multi-capture dataset qualification 已完成第一輪：Tongji 與 XINHUA 提供最合適的 contactless multi-session 結構但 reuse permission 尚未閉合；MPW-180 最接近 multi-device mobile capture，但目前 repository 的 dataset DOI/link 仍未發布、README 所述 dataset-license artifact 亦尚不存在。THUPALMLAB 已有明確 non-commercial research / education permission，且現在已取得 user-supplied sample；但 pinned MediaPipe 1.0.1 baseline 對 subject-1 left-palm 的 8 次 scanner impressions 實測為 `0 candidates = 8/8`，因此只建立 bounded scanner-domain runtime incompatibility evidence，不能外推成 THUPALMLAB dataset-wide detector failure。

目前仍不能直接設 production threshold。主要 remaining gaps：真正 permission-qualified 的 contactless multi-capture / device repeatability、detector-to-detector agreement、line-segmentation uncertainty、可辯護的 predeclared admission calibration 與 behavioral regression。Palmistry 仍不進 router。
