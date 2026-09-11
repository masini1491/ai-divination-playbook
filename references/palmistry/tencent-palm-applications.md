# Source Dossier｜TencentYoutuResearch/Palm-Applications / PalmDestiny

Status: **REFERENCE-ONLY｜僅供參考**

Repository: `TencentYoutuResearch/Palm-Applications`

Reviewed revision: `ab9b99db5ae20bf3f2bd5932ce902340effc7804`

Relevant component: `celina-PalmDestiny`

License evidence: repository / subproject `LICENSE` files at reviewed revision are Apache-2.0. The PalmDestiny README also displays / states MIT, so license metadata is internally inconsistent; do not assume MIT without reconciling upstream.

## What it is

PalmDestiny 是一個 AI 掌紋算命 Web application：攝影機取得 palm image，結合 image preprocessing / CV features 與 vision-capable LLM，再產生娛樂性手相報告；另外包含八字、星座、生肖與可選的掌紋身份識別整合。

## Relevant value

可作為**產品流程與責任拆分的反例 / integration reference**：

```text
image acquisition
→ preprocessing / approximate CV features
→ multimodal visual description
→ LLM interpretation
→ user-facing report
```

它也展示如何把 CV-derived feature summary 傳給文字模型生成 reading。

## Important boundary: observation prompt is contaminated by interpretation

`qwen_cloud_client.py` 的 visual-description prompt 雖要求客觀描述，但同一 prompt 已直接嵌入傳統解釋，例如把生命線弧度與精力／體質、感情線弧度與感情／理性連在一起；因此該 prompt 不能直接作為本 Playbook 的 Objective Observation contract。

reading-generation prompt 又要求模型以中國傳統相師身分解讀，並聲稱熟讀多部經典。這些書名出現在 prompt 中，不等於 repository 已提供、驗證或建立那些文本的 source lineage，也不能當成 citation authority。

## CV limitation

`image_processing.py` 主要採 OpenCV threshold / contour / HoughLinesP，再以近似位置與角度 heuristic 嘗試辨識：

- upper longest horizontal → heart line；
- middle longest horizontal → head line；
- longest diagonal → life line；
- central vertical → fate line。

這適合當 prototype / feature-extraction reference，不應直接升格為 validated Palm Observation Fact detector。

## Do not assume

- 不把 LLM 看圖描述當 deterministic observation。
- 不把 prompt 中的傳統說法視為已驗證 source rule。
- 不把掌紋 identity / biometric API 與 divination observation 混為同一 capability。
- 不因 README 標示 MIT 就忽略 reviewed `LICENSE` files 的 Apache-2.0 evidence；若未來 reuse code，先重新做 license reconciliation。

## Adoption

**REFERENCE-ONLY**

保留 product-flow / multimodal integration / failure-boundary 參考；不採用其 prompt、CV heuristic 或 interpretation wording 作 canonical Palmistry rule。
