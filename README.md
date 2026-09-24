# AI 占卜提問與治理實戰手冊

一套可重用的 **AI 占卜提問設計、方法路由、占問生命週期、Runtime Draw / Cast、deterministic method facts、Reading Record 與解讀治理方法論**。

目前 production-ready methods：

```text
Tarot
Meihua
Liuyao
Astrology（explicit-request only）
Zi Wei Dou Shu / 紫微斗數（explicit-request only；Scope-A natal first layer）
```

其中：

- Tarot / Meihua / Liuyao 參與 ordinary method routing；
- Astrology Production v1 已正式可用，但只在使用者明確要求「用占星／看本命盤／看行運」時啟用，不加入 ordinary auto-routing；
- Zi Wei Scope-A Production v1 已正式可用，但只在使用者明確要求「用紫微／看紫微命盤」時啟用，不加入 ordinary auto-routing；目前支援 bounded natal first layer、Asia/Taipei 西元生日輸入與 optional brightness facts；
- Tarot + Meihua 已有 canonical cross-validation contract；其他 method pair 在沒有專門 reconciliation contract 前，不宣稱為正式 cross-validation。

> **AI / ChatGPT 快速入口：** 實際使用本手冊時，直接從 [`CHAT_INIT.md`](CHAT_INIT.md) 開始並依 task routing 只讀最低必要文件／sections；不需要先完整閱讀本 README，也不要為了「熟悉手冊」掃描整個 Repository。
>
> **Pre-retrieval warning：** 如果 AI 目前只看得到 GitHub public page、URL preview／snippet 或 search preview，而 GitHub Connect 尚未連上，**不得**把該 public surface 當成 current repository authority，也不得據此聲稱「已確認目前 Repo／最新版規則」。需要 current GitHub content 時先建立 GitHub Connect retrieval；若最低必要 connector/read recovery 仍失敗，停在 `ACCESS BLOCKED`。Canonical policy 仍由 [`CHAT_INIT.md`](CHAT_INIT.md) 擁有，README 不取得 repository-access authority。
>
> **GitHub Connect 是本專案唯一 GitHub repository retrieval transport：** 只要需要讀取本 Repo、Randomizer、外部 method engine、GitHub reference、branch／commit／diff／license 等 GitHub-hosted evidence，一律使用 connected GitHub connector。若 connector 不可用而 task materially 依賴 current GitHub content，停在 `ACCESS BLOCKED`；完整規則以 [`CHAT_INIT.md`](CHAT_INIT.md) 為準。

本儲存庫不以整理完整牌義、卦辭、星座關鍵字或宣稱「算得準」為主要目的，而是處理更前面的問題：

> **怎麼把自然語言占問轉成低歧義、可比較、可追蹤、可驗證的 judgment contract；讓 AI 選擇合適的方法、取得可信 Draw / Cast / deterministic facts，並在解讀、承接、現實更新與回測時維持原契約與 provenance？**

本手冊把占卜視為**象徵性、反思性與結構化推理工具**；現實決策仍應以可驗證資訊、專業意見與實際條件為優先。

## 與 AI 開發手冊的關係

本 Repository 正式採用 [`masini1491/ai-development-playbook`](https://github.com/masini1491/ai-development-playbook) 作為 **common AI engineering baseline**：

```text
Playbook baseline: main
Project AI mode: ChatGPT-Only
```

這是規則分層，不是把兩個 Repository 合併成同一份 authority：

```text
ai-development-playbook
→ 跨專案共通 AI / repository engineering governance

ai-divination-playbook
→ project-native bootstrap + divination methods / runtime /
   deterministic facts / interpretation / reading lifecycle
```

**Adoption ≠ unconditional activation。** 普通 Tarot／Meihua／Liuyao／Astrology／Zi Wei 使用、reading continuation 與方法解讀維持本 Repo 的短 hot path，不為形式載入 shared Playbook；只有 repository maintenance、governance／AI workflow、GitHub operations、source/tests/tooling/workflow mutation 或 validation architecture 等工程工作才解析 declared baseline、進入其 `CHAT_INIT.md` 並載入最低充分 owner。

本 Repo 的 project-specific governance 與 technical source of truth 仍優先；尤其 **GitHub Connect-only** repository authority、公開 Repo privacy、Reading Record storage boundary 與各 divination method/runtime owner 都是 local rules／overrides，不因 shared baseline 的 generic default 而放寬。採用與 override 紀錄見 [`references/ai-development-playbook.md`](references/ai-development-playbook.md)。

## 快速安裝／第一次使用

第一次使用時，不需要下載整個 Repository、複製大段 Prompt 或先學會選方法。

1. 連接 GitHub Connect。
2. 告訴 ChatGPT：`讀取 masini1491/ai-divination-playbook`。
3. ChatGPT 應從 `CHAT_INIT.md` 開始做 minimum-sufficient routing。
4. 直接說你想占什麼；若要 Astrology，明確說「用占星／看本命盤／看行運」；若要 Zi Wei，明確說「用紫微／看紫微命盤」。

一般占問例如：

```text
我想占從現在到月底，這個合作是否會正式談成並開始執行？
```

ordinary auto-routing 會在 Tarot / Meihua / Liuyao 中依主要 judgment function 選擇方法。

Astrology 例如：

```text
用占星看我最近這段工作的行運影響。
看我的本命盤。
用本命盤 + 行運看接下來三個月。
```

這些要求直接交給 [`ASTROLOGY.md`](ASTROLOGY.md)，不先改寫成 Tarot / Meihua / Liuyao，也不送到 research router。

Zi Wei 例如：

```text
用紫微看我的本命盤。
2000/01/01 00:00，Asia/Taipei，用紫微看命盤。
用紫微看命盤，並加入廟旺／亮度。
```

這些要求直接交給 [`ZIWEI.md`](ZIWEI.md)。西元生日可經 admitted calendar adapter 轉成 normalized lunar input；若明確要求廟旺／亮度，才啟用 optional brightness module。

## 一句話使用

一般占問可以只有：

```text
我想占……
```

Agent 依 `CHAT_INIT.md`：

```text
自然語言問題
→ judgment function detection
→ ordinary method routing（Tarot / Meihua / Liuyao）
→ minimum Input Contract
→ Draw / Cast / deterministic Structured Method Fact
→ interpretation
→ 必要時 Reading Record / Reality Update / Backtest
```

若使用者明確指定 Astrology：

```text
explicit Astrology request
→ deterministic input resolution / natal or transit calculation
→ Astrology Fact Gate
→ admitted evidence selection / interpretation handoff
→ bounded synthesis
→ output guard
```

若使用者明確指定 Zi Wei：

```text
explicit Zi Wei request
→ Gregorian Asia/Taipei birth datetime
   OR admitted normalized lunar input
→ deterministic calendar / natal provider
→ Scope-A Fact Gate
→ allowlisted 52-claim retrieval
→ optional brightness_v1（明確要求時）
→ bounded synthesis
```

## 各個方法負責什麼

本專案不是把所有術數混成同一套算法，而是把不同 judgment responsibility 分開。

ordinary auto-routing 的簡化記憶方式：

```text
Psychology / Comparison
→ Tarot

Process / Evolution / Structure
→ Meihua

Outcome / Completion
→ Liuyao
```

Astrology 與 Zi Wei 都是 explicit user override：

```text
用占星／看本命盤／看行運
→ Astrology

用紫微／看紫微命盤
→ Zi Wei
```

這只是 README overview；真正 routing authority 仍以 [`METHOD_ROUTING.md`](METHOD_ROUTING.md)、[`CHAT_INIT.md`](CHAT_INIT.md) 與各 method owner 為準。

### Tarot｜人物、心理、互動與比較

Tarot 優先處理：

- 人物主觀感受、心理與互動傾向；
- 不同人物／方案／情境的相對比較；
- 選項適配度、阻礙、助力與觸發因素；
- 可拆成清楚牌位的事件流程；
- 已定義時間窗之間的相對支持度比較。

快速理解：

```text
哪一個？
哪個人？
對方怎麼想／怎麼反應？
A / B / C 哪個比較適合？
→ Tarot
```

### Meihua｜事件演化、主客結構與轉折

Meihua 優先處理：

- 一件事情目前如何演變；
- 主客／自身與外部的結構；
- 體用關係；
- 關鍵轉折與階段變化；
- 主卦 → 互卦 → 變卦的發展脈絡；
- 近程節奏、checkpoint 與象徵性應期。

快速理解：

```text
事情接下來怎麼變？
轉折在哪？
目前主客關係怎麼樣？
→ Meihua
```

### Liuyao｜單一具體事件的 outcome、阻礙與應期

Liuyao 優先處理**一個單一、具體、外部可驗證的事件**：

- 合作、交易、申請、邀約、回覆、交付是否成立；
- 已有明確 `completion_rule` 的成功／失敗問題；
- 事件卡在哪個角色、條件或環節；
- 用神、世應、動變等結構下的 outcome / obstacle；
- 在同一事件 identity 下進一步看較具體 timing／應期訊號。

Production deterministic path 已由本 Repo 維護：

```text
fixed Raw Cast
→ tools/liuyao_calendar.py
→ tools/liuyao_engine.py
→ tools/liuyao_runtime.py
→ LIUYAO.md
```

Randomizer 只負責產生 raw `6 / 7 / 8 / 9 × 6`；deterministic engine / calendar / runtime 再建立完整 Structured Method Fact。Language model 不得自行手算後冒充 engine output。

### Astrology｜本命盤與行運（Production v1 / explicit-request only）

Astrology Production v1 適合使用者明確要求：

```text
用占星幫我看
看我的本命盤
看這段行運
用本命盤 + 行運看某段時間
```

目前 admitted production scope 包括：

- Tropical / geocentric natal calculation；
- Whole Sign / Placidus houses；
- planets / luminaries、ASC / MC、houses、major aspects；
- retrograde / speed；
- exact transit-to-natal aspects；
- stations、tropical ingresses / re-ingresses、repeated passages；
- offline city/locality → coordinates + IANA timezone resolution；
- deterministic Fact Gate；
- exact-reference 與 typed-selector evidence selection paths；
- interpretation handoff 與 final output guard。

主要 production flow：

```text
explicit Astrology request
→ optional tools/astrology_place_resolver.py
→ tools/astrology_provider.py / tools/astrology_transit_provider.py
→ Astrology Fact Bundle 1.0
→ tools/astrology_runtime.py
→ tools/astrology_orchestrator.py
→ admitted evidence selection / interpretation handoff
→ bounded synthesis under ASTROLOGY.md + CHATGPT_OUTPUT.md
→ tools/astrology_output_guard.py
```

重要邊界：

- Astrology **不參與 ordinary auto-routing**；
- raw birth data 不授權 language model 自行手算 planets / houses / aspects；
- birth time、timezone 或 location identity 有 material ambiguity 時必須 fail closed；
- Research Astrology 與 Production Astrology 分離：來源／架構／evidence 研究走 [`RESEARCH_ROUTING.md`](RESEARCH_ROUTING.md) → `references/astrology/**`。

Production owner：[`ASTROLOGY.md`](ASTROLOGY.md)。

### Zi Wei Dou Shu｜紫微斗數（Scope-A Production v1 / explicit-request only）

Zi Wei 目前是 bounded natal production method，適合使用者明確要求：

```text
用紫微幫我看本命盤
看我的紫微命盤
2000/01/01 00:00，Asia/Taipei，用紫微看命盤
用紫微看命盤，加入廟旺／亮度
```

目前 admitted production scope 包括：

- `natal_baseline` only；
- 14 主星 first-layer facts / claims；
- 12 宮 first-layer claims；
- 52 admitted claims；
- 命宮、身宮、五行局、14 主星 placement 等 deterministic natal facts；
- `Asia/Taipei` civil-time Gregorian birth datetime → normalized lunar input；
- `23:00` 晚子時採 `next_day_at_23`；
- 閏月採 `split_after_day_15`；
- optional `brightness_v1`：14 主星廟／旺／得／利／平／不／陷 facts，只在明確要求廟旺／亮度時啟用；
- provenance、omission、conflict、uncertainty 與 safety delivery。

主要 production flow：

```text
explicit Zi Wei request
→ tools/ziwei_calendar_provider.py（若輸入西元生日）
→ tools/ziwei_gregorian_pipeline.py
→ tools/ziwei_natal_provider.py
→ tools/ziwei_scope_a_pipeline.py
→ optional tools/ziwei_brightness_pipeline.py
→ ZIWEI.md bounded synthesis
```

重要邊界：

- Zi Wei **不參與 ordinary auto-routing**；
- current production 仍不包含四化、輔／雜星 interpretation、broader star×palace corpus 或大限／流年／流月／流日／流時；
- raw birth data 不授權 language model 自行手算農曆、命身宮、主星 placement 或 brightness；
- Research Zi Wei 與 Production Zi Wei 分離：research 走 [`RESEARCH_ROUTING.md`](RESEARCH_ROUTING.md) → `references/ziwei/**`；
- ChatGPT local runtime 缺少 `lunar_python` 或 Zi Wei source 時，先依 [`ZIWEI_MATERIALIZATION.md`](ZIWEI_MATERIALIZATION.md) 嘗試 verified same-commit bundle materialization；local package miss 不等於 method unavailable。

Production owner：[`ZIWEI.md`](ZIWEI.md)。

## Runtime 與 deterministic calculation

### Divination Casting Randomizer

Canonical stochastic core 與 full Runtime adapter：

```text
runtime/casting/core.py        # canonical stochastic core
runtime/casting/randomizer.py  # full API / CLI adapter，delegate to core.py
```

正式 stochastic execution entrypoint 是 `core.execute_stochastic()`。

目前負責：

```text
Tarot draw
Meihua A/B cast
Liuyao three-coin Raw Cast
```

`core.py` 決定 canonical stochastic raw result；`randomizer.py` 提供 full API / CLI transport 並 delegate 到同一 core，不負責 interpretation。logical runtime identity 仍為 `divination-casting-randomizer-python`；legacy `masini1491/divination-casting-randomizer` 僅保留歷史 provenance、rollback 與 compatibility / historical deployment reference。current Runtime Draw 與 production authority 均位於本 Repo 的 `runtime/casting/**`。

### Liuyao deterministic engine

```text
Raw Cast
→ calendar facts
→ structural chart facts
→ deterministic runtime payload
```

Canonical implementation：

```text
tools/liuyao_calendar.py
tools/liuyao_engine.py
tools/liuyao_runtime.py
```

### Zi Wei deterministic providers / ChatGPT materialization

Canonical production implementation：

```text
tools/ziwei_calendar_provider.py
tools/ziwei_gregorian_pipeline.py
tools/ziwei_natal_provider.py
tools/ziwei_scope_a_pipeline.py
tools/ziwei_brightness_provider.py
tools/ziwei_brightness_pipeline.py
```

ChatGPT cold-start transport：

```text
runtime/ziwei/CHATGPT_DETERMINISTIC_TOOL_BUNDLE.json
→ 11 repo-local Zi Wei runtime/retrieval artifacts
→ 34 pinned lunar_python==1.4.8 runtime files
→ exact MIT LICENSE
→ chunk/archive/per-file verification
→ materialize verified runtime
→ execute without requiring pip/network afterward
```

Transport bundle 只是 derived cache；canonical calculation / interpretation authority 仍在 providers、pipelines、admission manifests 與 [`ZIWEI.md`](ZIWEI.md)。

### Astrology deterministic providers

Canonical production implementation：

```text
tools/astrology_place_resolver.py
tools/astrology_provider.py
tools/astrology_transit_provider.py
tools/astrology_runtime.py
tools/astrology_orchestrator.py
tools/astrology_evidence_selector.py
tools/astrology_interpretation_handoff.py
tools/astrology_reading_pipeline.py
tools/astrology_typed_reading_pipeline.py
tools/astrology_output_guard.py
```

核心原則：

> **Randomizer 決定 stochastic fact；deterministic engine/provider 決定可驗證 method facts；method owner 決定 interpretation governance。**

## 目前方法覆蓋

| 方法 | 主要 responsibility | Fact acquisition / calculation | method owner |
| --- | --- | --- | --- |
| Tarot | 人物心理／互動、選項比較、主觀適配、牌位拆解 | Canonical stochastic core (`runtime/casting/core.py`) via full Runtime adapter (`runtime/casting/randomizer.py`) | [`TAROT.md`](TAROT.md) |
| Meihua | 事件演化、主客／體用、轉折、節奏與象徵應期 | Canonical stochastic core (`runtime/casting/core.py`) via full Runtime adapter (`runtime/casting/randomizer.py`) | [`MEIHUA.md`](MEIHUA.md) |
| Liuyao | 單一具體事件是否成立、阻礙來源、較具體 outcome / timing | local Randomizer three-coin Raw Cast + local deterministic engine/calendar/runtime | [`LIUYAO.md`](LIUYAO.md) |
| Astrology | 本命盤、行運與 admitted natal/transit factors；explicit-request only | local deterministic place resolver + natal/transit providers + Fact Gate | [`ASTROLOGY.md`](ASTROLOGY.md) |
| Zi Wei | bounded natal first layer；52 admitted claims；optional brightness；explicit-request only | Gregorian calendar adapter + local natal provider/pipeline + verified ChatGPT transport bundle | [`ZIWEI.md`](ZIWEI.md) |

## Authority boundary

整套架構刻意分層：

```text
CHAT_INIT / METHOD_ROUTING
→ 決定 task identity、ordinary method routing 或 explicit Astrology / Zi Wei override

CASTING / INPUT RESOLUTION
→ stochastic methods 使用 canonical Randomizer
→ Astrology 可使用 admitted place resolver
→ Zi Wei 可使用 admitted Gregorian calendar adapter

DETERMINISTIC ENGINE / PROVIDER
→ 建立 method-specific fixed facts

METHOD OWNER
→ interpretation policy、unsupported-factor boundary、fail-closed rules

CHATGPT_OUTPUT
→ user-visible output governance
```

README 只負責人類 overview，不建立第二份 routing 或 method policy authority。

## 核心治理原則

### 1. Contract before result

題目、completion rule、position／method responsibility 必須在看到結果前固定。

### 2. One judgment function first

「會不會、何時、為什麼、好不好、怎麼辦」通常不應全部混進同一 judgment node。

### 3. Fact 與 interpretation 分離

```text
Question Contract fixed
→ stochastic Draw / Cast 或 deterministic calculation
→ raw / structured fact fixed
→ Interpretation
```

不得看到不喜歡的結果後重抽、重起、重算或偷偷換方法。

### 4. Runtime / calculation 必須是真執行

> **Language-model generation ≠ random draw / cast / deterministic chart calculation。**

能力不足時 fail closed；不得用模型自由生成結果冒充 runtime / provider output。

### 5. Symbolic consistency ≠ independent reality evidence

不同 readings 同方向可以說 symbolic consistency，但不能把多次占問直接宣稱為多份獨立現實證據。

### 6. Reading history append-only

正式 Reading Record 至少區分：

```text
QUESTION / CONTRACT FACT
DRAW / CAST / ASTROLOGY / ZI WEI FACT
STRUCTURED METHOD FACT（若有）
ORIGINAL INTERPRETATION
REALITY UPDATE
RETROSPECTIVE INTERPRETATION
BACKTEST JUDGMENT
```

後續現實不回頭改寫原始 reading。

## 文件架構

| 文件 | 主要責任 |
| --- | --- |
| [`AGENTS.md`](AGENTS.md) | repository governance / project AI mode / maintenance boundary |
| [`CHAT_INIT.md`](CHAT_INIT.md) | fresh chat bootstrap、repository access、freshness、task routing、handoff gate |
| [`PLAYBOOK_INDEX.json`](PLAYBOOK_INDEX.json) | machine-readable routing-only owner index |
| [`METHOD_ROUTING.md`](METHOD_ROUTING.md) | ordinary Tarot / Meihua / Liuyao method selection；Astrology / Zi Wei explicit override boundary |
| [`RESEARCH_ROUTING.md`](RESEARCH_ROUTING.md) | explicit research-line discovery / research vs production separation |
| [`INPUT_CONTRACT.md`](INPUT_CONTRACT.md) | 題目與 method input / provenance contract |
| [`QUESTION_DESIGN.md`](QUESTION_DESIGN.md) | 問題拆解與牌位／功能設計 |
| [`TAROT.md`](TAROT.md) | Tarot-specific contract |
| [`MEIHUA.md`](MEIHUA.md) | Meihua-specific contract |
| [`LIUYAO.md`](LIUYAO.md) | Liuyao judgment、Raw Cast → Structured Fact、解讀與 fail-closed contract |
| [`ASTROLOGY.md`](ASTROLOGY.md) | Astrology Production v1 method owner、Fact Gate、interpretation / unsupported-factor governance |
| [`ZIWEI.md`](ZIWEI.md) | Zi Wei Scope-A Production v1 method owner、Gregorian input、brightness / unsupported-layer boundary |
| [`ZIWEI_MATERIALIZATION.md`](ZIWEI_MATERIALIZATION.md) | Zi Wei ChatGPT deterministic bundle、verification、cache / fail-closed materialization contract |
| [`RUNTIME_DRAW.md`](RUNTIME_DRAW.md) | Runtime Draw / Cast、cache、source、provenance、fail closed |
| [`CROSS_VALIDATION.md`](CROSS_VALIDATION.md) | 目前正式 Tarot × Meihua reconciliation / evidence lineage |
| [`READING_LIFECYCLE.md`](READING_LIFECYCLE.md) | 新題、承接、條件世界、補占、重占、現實更新、完成、回測 |
| [`READING_RECORD.md`](READING_RECORD.md) | durable reading identity、append-only evidence layers、storage boundary |
| [`CHATGPT_OUTPUT.md`](CHATGPT_OUTPUT.md) | user-visible output / Copy-ready / Pre-Send |
| [`BEHAVIORAL_EVAL.md`](BEHAVIORAL_EVAL.md) | cold-start / behavioral regression |
| [`SESSION_HANDOFF.md`](SESSION_HANDOFF.md) | fresh-session rehydration checkpoint adapter |
| [`references/astrology/`](references/astrology/) | Astrology research evidence；不是 production owner |
| [`references/ziwei/`](references/ziwei/) | Zi Wei research evidence / source-policy history；不是 production owner |
| [`references/palmistry/`](references/palmistry/) | Palmistry research line；目前不是 production method |
| [`reports/astrology/`](reports/astrology/) | Astrology production admission / execution evidence reports |
| [`schemas/astrology/`](schemas/astrology/) | Astrology Production v1 machine contracts |

## Cross-validation 現況

目前完整 canonical reconciliation owner 仍是：

```text
Tarot + Meihua
```

Liuyao、Astrology 與 Zi Wei 都已是 production methods，但 **production-ready 不等於已存在任意 pairwise cross-validation contract**。

在新增專門 reconciliation contract 前，不把下列組合宣稱為 canonical cross-validation：

```text
Liuyao + Tarot
Liuyao + Meihua
Astrology + Tarot
Astrology + Meihua
Astrology + Liuyao
Zi Wei + Tarot
Zi Wei + Meihua
Zi Wei + Liuyao
Zi Wei + Astrology
```

可以在同一使用者請求中形成 distinct readings 或 bounded derived synthesis，但必須保留各自 responsibility 與 evidence lineage。

## Research lines 與 production methods

Research discoverability 不等於 production admission。

目前：

- Astrology：Research v1 evidence 保留於 `references/astrology/**`；另外已有獨立的 Production v1 authority。
- Zi Wei：Research evidence / architecture history 保留於 `references/ziwei/**`；另外已有獨立的 Scope-A Production v1 authority、Gregorian input adapter、optional brightness 與 ChatGPT deterministic transport。
- Palmistry：已有 bounded research line，但目前仍不是 ordinary production method。

任何 research line 未來進 production，仍需完整完成 method owner、fact/runtime authority、routing、provenance、behavioral regression 與 explicit admission。

## 下一階段方法

未來若加入 Qimen、Da Liu Ren 等方法，仍遵循：

```text
judgment gap
→ method owner
→ input / casting / deterministic authority
→ routing
→ runtime / provenance
→ behavioral regression
→ explicit admission
```

Repository 名稱泛化不代表 AI 可以自行發明未定義的方法流程。

## 隱私與公開安全

本 Repo 是公開方法論 repository，不保存：

- 真實姓名與可識別感情／關係細節；
- 出生日期、時間與地點等可識別個人資料；
- 健康、性相關私人紀錄；
- 私人公司未公開人事、薪資、客戶或專案資訊；
- 完整私人 Reading Record / session handoff payload；
- secrets / credentials。

真實 Reading Record 與個人 Astrology / Zi Wei birth data 不得寫入本公開 Playbook。

## 狀態

持續演進中。現在的 production surface 已涵蓋 Tarot、Meihua、Liuyao、explicit-request Astrology Production v1 與 explicit-request Zi Wei Scope-A Production v1；後續仍以真實使用中反覆出現的 judgment gap、routing collision、runtime / deterministic calculation、record integrity 與 backtest 問題反向萃取規則，而不是追求文件數量或術數數量。