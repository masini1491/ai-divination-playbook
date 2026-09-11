# Palmistry References

本目錄保存手相（Palmistry）相關的外部 GitHub repository、paper、dataset、computer-vision implementation 與傳統判讀資料之 Cold source dossier。

## Authority boundary

放入本目錄的資料預設皆為 `REFERENCE-ONLY`：

- 不自動取得 canonical policy authority；
- 不自動代表 Playbook 已支援該方法或規則；
- 不自動進入 ordinary reading Hot Path；
- 不因 source 看起來合理、熱門或技術可行就直接寫入 `PALMISTRY.md` 的 production rule。

正式採用前應至少記錄 source/ref、license、用途、可驗證 observation 能力、interpretation scope、流派差異與 not-adopted boundary。

## Research synthesis

- [`SYNTHESIS.md`](SYNTHESIS.md) — source comparison、architecture implication、remaining evidence gaps。
- [`CHINESE_RULE_NORMALIZATION.md`](CHINESE_RULE_NORMALIZATION.md) — 《神相全編》／《太清神鑑》／《神相鐵關刀》的 rule-family normalization、lineage guard、術語 namespace 與中西 mapping boundary。
- [`OBSERVATION_SCHEMA_DRAFT.md`](OBSERVATION_SCHEMA_DRAFT.md) — source-neutral Palm Observation Fact draft；scene/target selection、task-specific quality、geometry、unknown semantics、tradition projection 與 privacy boundary。
- [`PHOTO_VALIDATION.md`](PHOTO_VALIDATION.md) — 代表性真實照片 field-coverage / fail-closed validation。
- [`NORMALIZATION_CONTRACT_DRAFT.md`](NORMALIZATION_CONTRACT_DRAFT.md) — raw image → model adapter → raw geometry → canonical palm basis 的 deterministic normalization contract draft。
- [`normalization_probe.py`](normalization_probe.py) — Cold、standard-library-only synthetic probe；驗 translation / rotation / scale / mirror / inverse-transform / fail-closed properties，不是 production tool。

### Observation / CV references

- [`palm-line-reader.md`](palm-line-reader.md) — `samuelwbarber/palm-line-reader`；三大主線 segmentation、shipped ONNX inference contract、reconstructed preprocessing caveat、Reddit-derived training provenance。
- [`yeonsumia-palmistry.md`](yeonsumia-palmistry.md) — `yeonsumia/palmistry`；21-landmark homography rectification、principal-line detection/classification/measurement pipeline，以及 project-specific template / threshold boundary。
- [`palm-astro-application.md`](palm-astro-application.md) — `lakshay102/Palm-Astro-Application`；geometry feature extraction concept；synthetic interpretation 與 unresolved code license 不採用。
- [`tencent-palm-applications.md`](tencent-palm-applications.md) — `TencentYoutuResearch/Palm-Applications` / PalmDestiny；multimodal product-flow reference；prompt contamination、approximate CV heuristic 與 license inconsistency boundary。

### Interpretation references

- [`palmistry-for-all.md`](palmistry-for-all.md) — Cheiro 的 *Palmistry for All*（GITenberg / Project Gutenberg lineage）；西方 palmistry tradition reference，非中國手相 authority。
- [`chinese-traditional-sources.md`](chinese-traditional-sources.md) — 中國傳統手相 provenance baseline；以《古今圖書集成》所收《神相全編》掌部、《神相鐵關刀》、《太清神鑑》為主要古籍來源，GitHub mirrors 只作 bounded retrieval / cross-check。

## Current promotion state

Palmistry 目前仍是 `PALMISTRY.md` 所定義的 **Cold scaffold / not production-routable**。

本目錄的增加不修改：

```text
METHOD_ROUTING.md
PLAYBOOK_INDEX.json
CHAT_INIT.md production method set
README production support list
```

目前 normalization 已有 source-specific contract draft，並完成第一輪 synthetic deterministic probe（11 passed / 0 failed）；但尚未建立真實 landmark noise tolerance、camera-mirroring compatibility、cross-device repeatability 或 behavioral regression，因此仍不進 router。
