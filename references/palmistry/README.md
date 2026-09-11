# Palmistry References

本目錄保存手相（Palmistry）相關的外部 GitHub repository、paper、dataset、computer-vision implementation 與傳統判讀資料之 Cold source dossier。

## Authority boundary

放入本目錄的資料預設皆為 `REFERENCE-ONLY`：

- 不自動取得 canonical policy authority；
- 不自動代表 Playbook 已支援該方法或規則；
- 不自動進入 ordinary reading Hot Path；
- 不因 source 看起來合理、熱門或技術可行就直接寫入 `PALMISTRY.md` 的 production rule。

正式採用前應至少記錄 source/ref、license、用途、可驗證 observation 能力、interpretation scope、流派差異與 not-adopted boundary。

## 第一輪研究

- [`SYNTHESIS.md`](SYNTHESIS.md) — 第一輪 source comparison、architecture implication、remaining evidence gaps。

### Observation / CV references

- [`palm-line-reader.md`](palm-line-reader.md) — `samuelwbarber/palm-line-reader`；三大主線 segmentation、MediaPipe crop、browser ONNX；注意 Reddit-derived training provenance。
- [`yeonsumia-palmistry.md`](yeonsumia-palmistry.md) — `yeonsumia/palmistry`；view rectification、principal-line detection / classification / measurement pipeline。
- [`palm-astro-application.md`](palm-astro-application.md) — `lakshay102/Palm-Astro-Application`；geometry feature extraction concept；synthetic interpretation 與 unresolved code license 不採用。
- [`tencent-palm-applications.md`](tencent-palm-applications.md) — `TencentYoutuResearch/Palm-Applications` / PalmDestiny；multimodal product-flow reference；prompt contamination、approximate CV heuristic 與 license inconsistency boundary。

### Interpretation references

- [`palmistry-for-all.md`](palmistry-for-all.md) — Cheiro 的 *Palmistry for All*（GITenberg / Project Gutenberg lineage）；西方 palmistry tradition reference，非中國手相 authority。

## Current promotion state

Palmistry 目前仍是 `PALMISTRY.md` 所定義的 **Cold scaffold / not production-routable**。

本目錄的增加不修改：

```text
METHOD_ROUTING.md
PLAYBOOK_INDEX.json
CHAT_INIT.md production method set
README production support list
```

只有在 observation schema、tradition-specific interpretation source、fail-closed rules 與 behavioral regression 都足夠後，才評估 promotion。
