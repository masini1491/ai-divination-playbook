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

### 4.1 Post-Reading Gap Escalation Gate

本 gate 只回答「一次實際 broad natal reading 已暴露具體問題時，是否值得產生 Repo 工作」。它不是長期 evaluation harness，也不建立 accuracy KPI、重跑同盤、theme-stability score 或永久 audit queue。

**Eligible trigger** 只有：

1. 使用者指出可定位到具體 passage 的：
   - `too_generic`
   - `repetitive`
   - `tension_not_integrated`
   - `unsupported_leakage`
2. Pre-Send / regression 已能重現同一 failure pattern。

只有「覺得不準／不夠準」但無法定位 passage → **no_repo_work**。主觀回饋只能作 locator，不是 semantic evidence。

觸發後只分兩條 lane：

```text
output_contract_gap
→ 只有 synthetic regression 可重現時
→ bounded synthesis / output-guard fix

semantic_resolution_gap
→ references/astrology/EXACT_CLAIM_ADMISSION_POLICY_V1.md
→ composition_adequate / research_candidate / exact_claim_admitted / unsupported
→ 只有 research_candidate 才可建立 bounded exact-claim research
```

Privacy / persistence：

- 真實私人 reading、可識別出生資料與原始對話不得寫入 public repo；
- Repo 只保存抽象 failure pattern、去識別化 contract wording 或 synthetic regression；
- 沒有 reproducible gap → 不產生 mutation；
- 本 gate 不新增 semantic、claim-admission、calculation 或 routing authority。

Machine-enforced shape與 provenance gate 由：

- `ASTROLOGY_PRODUCTION_ADMISSION_V1.json`
- `schemas/astrology/ASTROLOGY_OUTPUT_DRAFT_V1.schema.json`
- `schemas/astrology/ASTROLOGY_USER_FACING_OUTPUT_V1.schema.json`
- `tools/astrology_output_guard.py`

負責；本檔不重複其欄位細節。
