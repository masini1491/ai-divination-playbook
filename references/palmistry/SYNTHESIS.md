# Palmistry Research Synthesis｜手相參考收斂

Status: **REFERENCE-ONLY｜僅供參考**

Reviewed target baseline: `masini1491/ai-divination-playbook@b68f0be26a3e622ce21123bfe23886962fd909c9`

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
3. 哪些來源只能作技術或產品參考，不能升格成規則 authority。

## Current conclusion

### Observation / computer vision

目前最值得保留的兩個技術 reference：

- `samuelwbarber/palm-line-reader`：適合參考三大主線（heart / head / life）的輕量 segmentation、browser ONNX deployment、MediaPipe palm crop 與 line-mask evaluation。
- `yeonsumia/palmistry`：適合參考 tilted-palm rectification、MediaPipe landmarks、principal-line detection / classification / length measurement 的 pipeline decomposition。

`lakshay102/Palm-Astro-Application` 可提供 length / curvature / angle / intersection / coverage 等 geometry feature extraction 概念，但其部分 palm-reading classification 是明示 synthetic rule，且未確認標準開源 license，因此只保留概念性參考，不重用程式或判讀標籤。

`TencentYoutuResearch/Palm-Applications` 的 `celina-PalmDestiny` 可參考應用整合與「visual description + CV features + LLM reading」的產品流程，但其 image observation prompt 已混入傳統解釋，CV 主線辨識又使用近似 Hough heuristic，因此不適合直接成為 Palm Observation Fact authority。

### Traditional interpretation — Western

`GITenberg/Palmistry-for-All_20480` 保存 Cheiro 的 *Palmistry for All*，來源 metadata 指向 Project Gutenberg，內容涵蓋 Head / Life / Fate / Sun / Heart / Health lines、minor lines、timing、hand shapes、thumb、fingers、nails 與 mounts。

這可以作為**西方 Cheiro palmistry tradition** 的 interpretation reference，但不得：

- 冒充中國傳統手相；
- 冒充科學或統計驗證；
- 因為是歷史文本就直接升格成 current canonical rule；
- 忽略 Project Gutenberg 對美國以外 copyright status 的保留說明。

### Traditional interpretation — Chinese

第二輪研究已補到可追溯的中國傳統 source anchors，詳見 [`chinese-traditional-sources.md`](chinese-traditional-sources.md)。目前最有價值的 primary / secondary provenance surfaces：

- 中文維基文庫《古今圖書集成》藝術典第 640 卷：收錄《神相全編》「論手／論掌紋／手背紋／玉掌記」等手相內容；
- 《神相鐵關刀》：有多段 `相掌秘訣`、掌形、掌紋、八卦／掌宮內容；
- 《太清神鑑》卷五：有論手、相掌紋、掌上三紋等內容；
- `look-fate/lookfate-book`：可檢索的 GitHub mirror，用於 bounded search / cross-check，不替代古籍 provenance；
- `youngzs/xuanxue`：可作 discovery / comparison，但本輪未確認清楚 root license / edition provenance，不作 reuse authority。

因此原本的「缺中國手相傳統來源」gap 已縮小。現在真正的 gap 是：**如何把各文本的 source-specific vocabulary、位置定義與 rule family 正規化，而且不把後世／西方術語硬做一對一對應。**

### Screened out as rule authority

`Adamya-Gupta/HastAI-PalmReader` 主要把手掌圖片直接交給 Gemini，再以 prompt 要求 Fate / Head / Life / Heart / Career / Love / Future。README 的 Palm Reading 基礎參考是 WikiHow；沒有獨立 observation schema 或可追溯 rule library。

因此不為它建立正式 source dossier；它只證明「prompt-only palm reader」不是本 Playbook 要採用的 architecture。

## Architecture implication

目前 evidence 支持維持 `PALMISTRY.md` 已建立的分層：

```text
Image Quality Gate
→ Objective Observation
→ Palm Observation Fact
→ Tradition-specific Interpretation
→ User-visible synthesis
```

其中：

- segmentation / landmarks / geometry tool 只能取得 observation responsibility；
- 傳統書籍／規則庫只能取得 interpretation responsibility；
- 任一 LLM prompt 不得同時自行宣告「看到了什麼」與「傳統上代表什麼」而沒有中間 fact boundary；
- 不同流派的 interpretation 要保留 tradition / source provenance，不能合併成無來源的 generic palmistry truth。

## Remaining evidence gaps

目前仍不足以把 Palmistry promotion 到 production routing：

1. 尚未定義 canonical `Palm Observation Fact` schema 與 confidence / unknown semantics；
2. 三大主線之外的 fate line、minor lines、fork / break / island / star / mount 等 observation 尚未找到足夠可靠的 validated detector；
3. 尚未建立 image-quality / occlusion / hand-side fail-closed gate；
4. 中國傳統 sources 已有 provenance anchors，但尚未完成 source-specific rule normalization / conflict handling；
5. 中西術語尚未建立安全 mapping；不得預設 `天／人／地紋 == heart／head／life line`；
6. 尚未建立 Palmistry behavioral regression，證明加入後不影響既有 Tarot / Meihua / Liuyao routing。

## Adoption decision

目前所有外部來源仍為：

**REFERENCE-ONLY｜僅供參考**

因此 production method set 不變；下一個合理 research node 是 **source-specific rule normalization matrix + Palm Observation Fact schema draft**，不是先把 Palmistry 加進 router。
