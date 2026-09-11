# Palmistry Research Synthesis｜手相參考收斂

Status: **REFERENCE-ONLY｜僅供參考**

Reviewed target baseline: `masini1491/ai-divination-playbook@8621f095cf68366cf67cc0e6b7e10b3e076fd0e4`

本檔只收斂外部研究結論，不建立 production Palmistry capability，也不修改 `METHOD_ROUTING.md`、`PLAYBOOK_INDEX.json`、`CHAT_INIT.md` 或既有 Tarot / Meihua / Liuyao contract。

## Research question

要讓 Palmistry 未來能安全加入本 Playbook，至少要分清兩種完全不同的責任：

```text
Palm image
→ objective / reproducible observation
→ structured Palm Observation Fact
→ tradition-specific interpretation
```

研究重點不是「找一個會算命的 App」，而是確認：

1. 掌紋／掌型的 observation 是否已有可重用技術；
2. interpretation 是否有可追溯的傳統來源；
3. 如何把 source-specific terminology 正規化而不製造無證據的中西對照；
4. 哪些來源只能作技術或產品參考，不能升格成規則 authority。

## Current conclusion

### Observation / computer vision

目前最值得保留的兩個技術 reference：

- `samuelwbarber/palm-line-reader`：適合參考三大主線（heart / head / life）的輕量 segmentation、browser ONNX deployment、MediaPipe palm crop 與 line-mask evaluation。
- `yeonsumia/palmistry`：適合參考 tilted-palm rectification、MediaPipe landmarks、principal-line detection / classification / length measurement 的 pipeline decomposition。

`lakshay102/Palm-Astro-Application` 可提供 length / curvature / angle / intersection / coverage 等 geometry feature extraction 概念，但其部分 palm-reading classification 是明示 synthetic rule，且未確認標準開源 license，因此只保留概念性參考，不重用程式或判讀標籤。

`TencentYoutuResearch/Palm-Applications` 的 `celina-PalmDestiny` 可參考應用整合與「visual description + CV features + LLM reading」的產品流程，但其 image observation prompt 已混入傳統解釋，CV 主線辨識又使用近似 Hough heuristic，因此不適合直接成為 Palm Observation Fact authority。

### Traditional interpretation — Western

`GITenberg/Palmistry-for-All_20480` 保存 Cheiro 的 *Palmistry for All*，來源 metadata 指向 Project Gutenberg，內容涵蓋 Head / Life / Fate / Sun / Heart / Health lines、minor lines、timing、hand shapes、thumb、fingers、nails 與 mounts。

這可以作為**西方 Cheiro palmistry tradition** 的 interpretation reference，但不得冒充中國傳統手相，也不得冒充科學或統計驗證。

### Traditional interpretation — Chinese

中國傳統 source anchors 已建立，詳見 [`chinese-traditional-sources.md`](chinese-traditional-sources.md)：

- 中文維基文庫《古今圖書集成》藝術典第 640 卷所收《神相全編》掌部；
- 《神相鐵關刀》掌部；
- 《太清神鑑》卷五；
- `look-fate/lookfate-book` 只作 GitHub bounded retrieval / cross-check；
- `youngzs/xuanxue` 只作 discovery / comparison。

第三輪 normalization 進一步確認：

- `SXQ-640` 與 `TQ-V5` 在三紋、深細／粗淺、破紋、縱橫理等段落高度近似，因此不能自動當成兩個獨立 rule origins；
- `TGKD` 的掌部較強調八卦／掌宮、掌色與身面掌配合，但仍不能在沒有文本譜系研究時宣稱來源完全獨立；
- 同名詞可能跨 anatomical scope，例如 `玉柱` 可出現在不同相術部位；因此 terminology 必須帶 source / section / anatomical scope。

詳見 [`CHINESE_RULE_NORMALIZATION.md`](CHINESE_RULE_NORMALIZATION.md)。

## Architecture implication

目前 evidence 支持維持：

```text
Image Quality Gate
→ Objective Observation
→ Palm Observation Fact
→ Tradition-specific Projection
→ Tradition-specific Interpretation
→ User-visible synthesis
```

這比原本五層再多明確拆出 **Tradition-specific Projection**：先把 source-neutral visual geometry 映射到某一本古籍／某一流派的術語，再允許 interpretation。

核心 boundary：

- CV / vision layer 只擁有 observation responsibility；
- traditional source 只擁有 interpretation vocabulary / rule responsibility；
- source-local term mapping 不得覆寫 raw visual fact；
- 中西術語相似只能先標 `GEOMETRICALLY_SIMILAR`，不能直接宣告等同。

## Palm Observation Fact draft

已新增 [`OBSERVATION_SCHEMA_DRAFT.md`](OBSERVATION_SCHEMA_DRAFT.md)，目前 draft 至少要求：

- hand side / view / orientation；
- image quality / focus / lighting / glare / occlusion / crop；
- color reliability；
- palm / finger geometry；
- source-neutral line path / length / orientation / continuity / branches / intersections；
- palm vs dorsal-hand anatomical scope；
- unknown / not-observable / unresolved-mapping semantics；
- tradition-specific projection with source provenance；
- biometric / privacy boundary。

這個 schema 仍只是 research draft，沒有升格到 `PALMISTRY.md`。

## Remaining evidence gaps

目前仍不足以把 Palmistry promotion 到 production routing：

1. `Palm Observation Fact` schema 尚未以實際 hand images 做 field coverage / pose / left-right validation；
2. 三大主線之外的 fate line、minor lines、fork / island / star / mount 等 observation 尚未找到足夠可靠的 validated detector；
3. image-quality / occlusion / hand-side gate 尚未實作或建立 deterministic validator；
4. 中國傳統 rule normalization 已有第一版 matrix，但 named patterns / illustrated marks 尚有大量 unresolved mapping；
5. 中西術語仍未建立 production-safe mapping；目前 `天／人／地紋 ↔ heart／head／life` 與 `玉柱紋 ↔ fate line` 都是 `PROHIBITED_ASSUMPTION`；
6. 尚未建立 Palmistry behavioral regression，證明加入後不影響既有 Tarot / Meihua / Liuyao routing。

## Adoption decision

目前所有外部來源與新增 schema / matrix 仍為：

**REFERENCE-ONLY｜僅供參考**

因此 production method set 不變；下一個合理 research node 是 **以實際手掌影像驗證 Observation Schema coverage + image-quality gate**，仍不是先把 Palmistry 加進 router。
