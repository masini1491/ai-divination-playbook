# Zi Wei Dou Shu｜紫微斗數方法契約

Status: **PRODUCTION SCOPE-A V1 + GREGORIAN INPUT V1 + OPTIONAL BRIGHTNESS / M0 AUXILIARY / SIHUA FACTS V1 / EXPLICIT-REQUEST ONLY**

本檔是 Zi Wei Dou Shu 的 root production method owner。Production authority 僅涵蓋已 admission 的 **bounded natal first layer**；typed production composition 由 `tools/ziwei_runtime.py` 擁有；deterministic fact providers 與 machine admission truth 分別由 `tools/ziwei_*_provider.py` 與 admission manifests 擁有。Research history 仍由 `references/ziwei/**` 擁有，不因 production admission 回寫其歷史 authority。

## 1. Activation / Routing

Zi Wei Scope-A v1 不參與 ordinary auto-routing。只有使用者明確要求「紫微／紫微斗數／看紫微命盤」等 production intent 才啟動。

```text
explicit Zi Wei production
→ ZIWEI.md
→ Gregorian birth datetime (Asia/Taipei; CE or explicit 民國 year notation) → admitted year-notation/calendar adapters
   OR already-normalized lunar input + provenance
→ tools/ziwei_runtime.py (`run_ziwei`)
→ admitted natal_baseline facts
→ allowlisted 52-claim first-layer retrieval
→ bounded conflict / uncertainty / safety delivery
→ CHATGPT_OUTPUT.md
```

研究排盤規則、來源、未 admission 的四化解讀、輔星或 dynamic architecture → `RESEARCH_ROUTING.md` → `references/ziwei/**`。若使用者明確要求廟旺／亮度、M0 輔星 facts 或生年四化 facts，可啟動對應 optional module；未要求時維持原 Scope-A 行為。

## 2. Production Scope

IN:

- `natal_baseline` only;
- 14 major-star first-layer claims;
- 12 palace first-layer claims;
- 52 admitted claims total;
- admitted deterministic natal provider facts;
- Gregorian birth datetime input via `ziwei.calendar.tw_v1` for `Asia/Taipei` civil time within the admitted 1900-01-01..2100-12-31 range; explicit 民國年份 notation is deterministically converted by `tools/ziwei_year_notation.py` (`民國 N 年 → CE N+1911`) before the same Gregorian calendar adapter;
- explicit provenance, omission, conflict and safety delivery.

OPTIONAL / explicit add-on:

- `brightness_v1`: 14 主星 profile-bound brightness facts（廟／旺／得／利／平／不／陷），只用來滿足既有 admitted claim 的 dignity applicability；不得生成 brightness-only doctrine。
- `m0_auxiliary_v1`: 左輔／右弼／文昌／文曲四星的 profile-bound natal placement + self/sanfang modifier facts；只 admission 4 個 bounded auxiliary-role **policy** claims 與既有 major-star conditional activation，不代表 blanket minor-star admission，也不代表四星各自 historical semantic core 已 production admission。
- `sihua_v1`: `sihua.default_v1` profile-bound 生年四化 deterministic facts；只 admission calculation facts，**新增 interpretation claims = 0**。不得由四化 label 自動推導通用吉凶，也不得跨 profile 平均；transformed-star interpretation 需另有 source-explicit claim admission。

OUT / fail closed:

- non-M0 auxiliary / minor-star interpretation;
- Four-Transformation interpretation beyond separately admitted source-explicit transformed-star claims (currently none);
- broader contextual star×palace claim corpus;
- decadal / yearly / monthly / daily / hourly / other dynamic prediction.

Unsupported layers不得用模型記憶、手算、research-only claims 或其他方法偷偷補齊。

## 3. Deterministic Fact Boundary

Language model 不得把 raw birth data 自由手算成 production chart facts。已 normalization 的農曆輸入仍可直接走 Scope-A；西元生日則必須先經 admitted `tools/ziwei_calendar_provider.py`。若使用者明確使用民國紀年，必須先以 `tools/ziwei_year_notation.py` 做 deterministic 年份 notation conversion（`民國 N 年 = 西元 N+1911 年`），保留 source/converted facts，再送入同一 Gregorian provider；不得由模型心算或把民國誤當另一種 lunar calendar。Calendar v1 僅 admission `Asia/Taipei` civil time與 1900-01-01..2100-12-31 Gregorian input range，使用 `data/calendar/ziwei_tw_interval/v1/**` 的 admitted exact dataset；保留 raw lunar conversion，再明確套用 `next_day_at_23` 與 `split_after_day_15` Zi Wei policy。31 December 23:00 可讀下一年的 policy-tail shard，但不擴張 user-input range。不得由模型自行換農曆、猜 timezone 或偷偷套真太陽時。

Production runtime:

```text
typed Zi Wei request
→ tools/ziwei_runtime.py / run_ziwei()
→ Gregorian birth → tools/ziwei_calendar_provider.py
   OR normalized traditional-lunar birth
→ tools/ziwei_natal_provider.py
→ optional_modules includes brightness_v1
   → tools/ziwei_brightness_provider.py
→ optional_modules includes m0_auxiliary_v1
   → tools/ziwei_m0_auxiliary_provider.py
→ optional_modules includes sihua_v1
   → tools/ziwei_sihua_provider.py (facts only; 0 new interpretation claims)
→ tools/ziwei_claim_retrieval.py
→ tools/ziwei_delivery.py
→ typed Zi Wei result

legacy run_scope_a_* entrypoints
→ compatibility adapters
→ tools/ziwei_runtime.py
```

`schemas/ziwei/ZIWEI_READING_REQUEST_V1.schema.json` 與 `schemas/ziwei/ZIWEI_READING_RESULT_V1.schema.json` 定義 closed-world v1 interface。Unsupported temporal scope、optional module 或 profile 必須 fail closed；不得再為每個 module/input 組合新增 `with_x_and_y` canonical runtime。

若 local runtime、calendar manifest 或 required year shard 缺失，先依 `ZIWEI_MATERIALIZATION.md` 嘗試同 exact-commit deterministic bundle + query-bounded calendar-data materialization；ordinary production 不依賴 `lunar_python` runtime。只有 admitted materialization/direct-source paths 都失敗才停在 Fact Gate；不得改用 Tarot / Meihua / Liuyao 冒充 Zi Wei reading。

## 4. Interpretation / Evidence Boundary

Production v1 只可使用 pipeline allowlist 選出的 admitted claims。Research registry 的歷史 `production_routable=false` 不被改寫；production authority 來自獨立 admission manifest與 production wrapper。

- no admitted claim → omit / insufficient;
- missing fact → do not guess;
- conditional rule relevance ≠ demonstrated chart condition;
- `context_only` conditional rules may remain active as methodology/profile/safety context;
- `fact_gated` conditional claims enter selected claims only when activation = `satisfied`; `not_computed` / `unsatisfied` remain explicit omissions/evaluations;
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

ZIWEI_CALENDAR_ADMISSION_V1.json
→ Gregorian input/calendar normalization admission truth

tools/ziwei_runtime.py + schemas/ziwei/ZIWEI_READING_{REQUEST,RESULT}_V1.schema.json
→ canonical typed request / composition / result owner

tools/ziwei_year_notation.py + tools/ziwei_calendar_provider.py + tools/ziwei_gregorian_pipeline.py
→ 民國年份 deterministic notation adapter + Gregorian normalization provider + legacy compatibility adapter

tools/ziwei_natal_provider.py
→ admitted Scope-A deterministic natal provider

tools/ziwei_scope_a_pipeline.py
→ legacy normalized-lunar compatibility adapter

tools/ziwei_claim_retrieval.py + tools/ziwei_delivery.py
→ production claim retrieval / conditional activation / bounded delivery execution

tools/ziwei_brightness_provider.py + tools/ziwei_brightness_pipeline.py
→ optional profile-bound brightness facts + legacy compatibility adapter

tools/ziwei_m0_auxiliary_provider.py + ZIWEI_M0_AUXILIARY_ADMISSION_V1.json
→ optional M0 左輔／右弼／文昌／文曲 placement / modifier facts + bounded auxiliary-role policy claim admission; independent historical star semantics remain outside this admission

tools/ziwei_sihua_provider.py + ZIWEI_SIHUA_ADMISSION_V1.json
→ optional profile-bound 生年四化 facts only; no transformed-star interpretation corpus is admitted by this module

ZIWEI_BRIGHTNESS_ADMISSION_V1.json
→ optional brightness production admission truth

ZIWEI_MATERIALIZATION.md + runtime/ziwei/CHATGPT_DETERMINISTIC_TOOL_BUNDLE.json
→ ChatGPT cold-start runtime + calendar-manifest transport；year shards依輸入 query-bounded same-commit取得；derived cache only

references/ziwei/**
→ research evidence and historical research contracts

CHATGPT_OUTPUT.md
→ final output / Pre-Send owner
```

核心原則：**Explicit Zi Wei 可直接給 Asia/Taipei 西元生日，由 admitted calendar adapter 正規化後進 Scope-A；optional facts modules 必須明確啟用且保留 profile/provenance；sihua_v1 只提供四化 facts、不自動創造四化斷語；unspecified reading → ordinary router；unsupported Zi Wei layers → fail closed。**
