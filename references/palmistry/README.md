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
- [`real_image_repeatability_probe.py`](real_image_repeatability_probe.py) — detector-agnostic metric harness；接收 L0/L5/L17 + inverse transform，計算 anchor / canonical-frame drift。
- [`mediapipe_repeatability_runner.py`](mediapipe_repeatability_runner.py) — Cold research runner；下載 pinned official model + public fixtures、執行 controlled transforms 與 scene-local candidate association；不是 production runtime owner。

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
- normal repository validation workflow PASS（已驗證前一個 real-image evidence baseline；本次 final commit 另以當次 workflow 為準）。

真實影像 evidence 已證明：same-pixels deterministic 不代表 rotate / scale / crop / mirror invariant；overlapping-hand Case B 在 mirror 後甚至出現約 77.34% canonical drift。Multi-hand screen 又證明「人眼看到多手」不能替代 detector candidate evidence。因此目前不能直接設 production threshold，也不能宣稱 multi-candidate association 已驗證。

主要 remaining gaps：來源可控且 baseline 穩定輸出 ≥2 detector candidates 的 fixture、多種手型/照片、多 capture / device repeatability、detector-to-detector agreement、line-segmentation uncertainty 與 behavioral regression。Palmistry 仍不進 router。
