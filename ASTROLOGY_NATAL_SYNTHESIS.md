# Astrology Natal Synthesis｜本命盤主題整合契約

Status: **PRODUCTION V1 CONDITIONAL OUTPUT OWNER**

本檔只在 broad natal synthesis 啟用 `evidence-bounded-concrete-natal-v1` 時載入。窄 natal、單因子題與 transit 不讀本檔。它只規範已 admitted evidence 的整合與呈現，**沒有 semantic interpretation、claim admission 或 calculation authority**。

## 1. Theme contract

Broad natal synthesis 預設輸出 **3–5 個 major themes**，避免逐項傾倒 factor dictionary。每個 theme 必須：

- 綁定至少一個 admitted natal fact 與一個 admitted semantic claim；
- statement 不得超越所引用 claim；
- concrete manifestation 只能把已引用語義具體化成「可能如何表現」，不得寫成固定人格診斷或現實必然；
- deterministic fact-only geometry 不得被包裝成人格／心理語意。

## 2. Tension / limiting condition

若另一組 admitted evidence materially 拉向不同方向，應以 limiting condition / tension 說明，而不是用「有時 X、有時 Y」抹平成 Barnum statement。

Tension / limiting condition 必須有自己的 admitted fact + semantic claim refs；不得由模型常識補寫。沒有 material counter-pull 時不必為形式硬加 tension。

## 3. Evidence and unsupported boundary

- exact admitted claim 與 bounded composition 都只是 evidence input；
- 本 profile 不改變 `ASTROLOGY_NATAL.md` §5.1 precedence；
- unsupported factor 保持 unsupported，不為了讓主題完整而補洞；
- 使用者要求更短／更長只改 prose 密度，不得移除 material evidence lineage、unsupported boundary 或 material tension。

## 4. Evaluation boundary

品質檢查只看：specificity、traceability、tension handling、scope fidelity 與是否避免不必要重複。不得建立 synthetic「準確度分數」，也不得把使用者主觀「覺得準」當成 source / semantic admission evidence。

Machine-enforced shape與 provenance gate 由：

- `ASTROLOGY_PRODUCTION_ADMISSION_V1.json`
- `schemas/astrology/ASTROLOGY_OUTPUT_DRAFT_V1.schema.json`
- `schemas/astrology/ASTROLOGY_USER_FACING_OUTPUT_V1.schema.json`
- `tools/astrology_output_guard.py`

負責；本檔不重複其欄位細節。
