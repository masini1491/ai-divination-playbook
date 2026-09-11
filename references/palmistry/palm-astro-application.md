# Source Dossier｜lakshay102/Palm-Astro-Application

Status: **REFERENCE-ONLY｜僅供參考**

Repository: `lakshay102/Palm-Astro-Application`

Reviewed revision: `8cce4c7cb6a1e55a38cb813ef549608160cf3f98`

License / reuse status: **UNRESOLVED for code reuse**. At the reviewed revision, README 的 `License` 段只說此 project 用於 educational purposes 並要求遵守 local regulations；本輪未確認標準 open-source license file。因此只做概念性研究，不重用 source code。

## What it is

此專案把三大主線 segmentation 與 geometry feature extraction 串在一起：

- Life / Head / Heart 4-class segmentation；
- line length；
- curvature / tortuosity；
- line angle；
- intersections；
- line coverage。

README 也加入 dominant line、palm type 與 career-shift 等 rule-based classification。

## Relevant value

可借鑑的是「先把 segmentation 轉成結構化幾何 observation」的方向：

```text
segmentation masks
→ measurable geometry
→ structured features
```

這比直接把 image 丟給 LLM 後要求同時觀察與解讀，更接近本 Playbook 想要的 evidence boundary。

## Synthetic-rule boundary

`utils/feature_extraction.py` 明確把部分 classification 寫成 heuristic / synthetic rule。例如：

- palm type 由平均 curvature threshold 分類；
- career shift indicator 由 head-line angle 與 intersection count 產生，並在 source comment 中標示為 `Simple synthetic prediction`。

因此：

- geometry extraction concept 可以研究；
- synthetic labels / thresholds 不取得傳統手相 authority；
- 不得把固定 0.7 / 0.6 confidence 當作統計驗證；
- 不得把 `Curved/Expressive`、`Straight/Practical` 等分類直接移植成 canonical interpretation。

## Do not assume

- README 的 target metrics 不等於本輪已驗證實際 model performance。
- dummy / recommended datasets 不等於 repository 已提供足夠 production dataset provenance。
- educational-purpose wording 不等於 permissive software license。

## Adoption

**REFERENCE-ONLY**

只保留 geometry feature design 參考；code reuse、threshold、synthetic palm-reading labels 均不採用。
