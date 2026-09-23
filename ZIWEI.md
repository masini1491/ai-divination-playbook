# Zi Wei Dou Shu｜紫微斗數方法契約

Status: **PRODUCTION SCOPE-A V1 / EXPLICIT-REQUEST ONLY**

本檔是 Zi Wei Dou Shu 的 root production method owner。Production authority 僅涵蓋已 admission 的 **bounded natal first layer**；deterministic implementation 與 machine admission truth 由 `tools/ziwei_scope_a_pipeline.py`、`tools/ziwei_natal_provider.py` 與 `ZIWEI_PRODUCTION_ADMISSION_V1.json` 擁有。Research history 仍由 `references/ziwei/**` 擁有，不因 production admission 回寫其歷史 authority。

## 1. Activation / Routing

Zi Wei Scope-A v1 不參與 ordinary auto-routing。只有使用者明確要求「紫微／紫微斗數／看紫微命盤」等 production intent 才啟動。

```text
explicit Zi Wei production
→ ZIWEI.md
→ admitted normalized natal input + provenance
→ tools/ziwei_scope_a_pipeline.py
→ admitted natal_baseline facts
→ allowlisted 52-claim first-layer retrieval
→ bounded conflict / uncertainty / safety delivery
→ CHATGPT_OUTPUT.md
```

研究排盤規則、來源、四化、brightness、輔星或 dynamic architecture → `RESEARCH_ROUTING.md` → `references/ziwei/**`。

## 2. Production Scope

IN:

- `natal_baseline` only;
- 14 major-star first-layer claims;
- 12 palace first-layer claims;
- 52 admitted claims total;
- admitted deterministic natal provider facts;
- explicit provenance, omission, conflict and safety delivery.

OUT / fail closed:

- brightness-conditioned interpretation;
- auxiliary / minor-star interpretation;
- Four-Transformation interpretation;
- broader contextual star×palace claim corpus;
- decadal / yearly / monthly / daily / hourly / other dynamic prediction.

Unsupported layers不得用模型記憶、手算、research-only claims 或其他方法偷偷補齊。

## 3. Deterministic Fact Boundary

Language model 不得把 raw birth data 自由手算成 production chart facts。Scope-A production 必須使用 admitted provider/pipeline 所要求的 normalized input boundary與 provenance；provider 不支援的 normalization／calendar conversion不得猜測。

Production runtime:

```text
tools/ziwei_natal_provider.py
→ tools/ziwei_scope_a_pipeline.py
→ ZIWEI_PRODUCTION_ADMISSION_V1.json
```

若 deterministic boundary 不成立，停在 Fact Gate；不得改用 Tarot / Meihua / Liuyao 冒充 Zi Wei reading。

## 4. Interpretation / Evidence Boundary

Production v1 只可使用 pipeline allowlist 選出的 admitted claims。Research registry 的歷史 `production_routable=false` 不被改寫；production authority 來自獨立 admission manifest與 production wrapper。

- no admitted claim → omit / insufficient;
- missing fact → do not guess;
- registered conflict → preserve and present separately;
- source-backed / project-adopted / profile-specific state不得混成無來源 certainty;
- final prose不得創造新的 Zi Wei doctrine。

## 5. Uncertainty / Safety

紫微是 symbolic interpretation method，不是 scientific predictive-validity、medical、legal、financial 或 safety decision authority。

不得把 Scope-A interpretation 寫成 death、疾病診斷／結果、法律結果、投資報酬／損失、懷孕／生育、暴力／重大傷害等必然結果。High-impact topic 必須遵守既有 bounded delivery contract。

## 6. Output Boundary

輸出先回答使用者在 Scope-A 內真正問的 natal question，再提供最低充分 admitted evidence。清楚區分：

```text
normalized input / chart fact
→ admitted claim
→ conflict / omission / uncertainty
→ bounded symbolic synthesis
```

不得把未支援的 dynamic timing 或 broader contextual inference包裝成 production Zi Wei 結論。

## 7. Research / Production Separation

```text
production reading
→ ZIWEI.md + ZIWEI_PRODUCTION_ADMISSION_V1.json

research / source / architecture maintenance
→ RESEARCH_ROUTING.md → references/ziwei/**
```

Research evidence 詳細不代表自動 production-admitted；production admission 也不回寫 research history。

## 8. Authority Map

```text
ZIWEI.md
→ root production method owner / activation / scope / interpretation boundary

ZIWEI_PRODUCTION_ADMISSION_V1.json
→ machine admission truth

tools/ziwei_natal_provider.py
→ admitted Scope-A deterministic natal provider

tools/ziwei_scope_a_pipeline.py
→ production composition / retrieval / delivery binding

references/ziwei/**
→ research evidence and historical research contracts

CHATGPT_OUTPUT.md
→ final output / Pre-Send owner
```

核心原則：**Explicit Zi Wei → bounded natal Scope-A production；unspecified reading → ordinary router；unsupported Zi Wei layers → fail closed。**
