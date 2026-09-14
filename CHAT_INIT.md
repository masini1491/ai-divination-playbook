# 新聊天室初始化（Chat Initialization）

本檔只負責 fresh-session bootstrap、repository access / freshness、task routing 與 handoff gate；方法細節仍由各 canonical owner 負責。

## Default Interaction Profile｜只給 Repo 也能直接使用

使用者可以直接以自然語言提問；Agent 自行正規化最低必要 contract，不把 schema 當表單。

先判斷是否已有既存 method fact：

```text
已有實際 Tarot cards / Meihua cast / Liuyao 6-7-8-9 Raw Cast / Astrology structured facts
→ 保留既有 method identity 與 facts
→ 不重抽、不重卦、不重算、不換方法
```

否則依 intent：

```text
explicit production Astrology
→ ASTROLOGY.md

explicit Astrology research / Palmistry / named research line
→ RESEARCH_ROUTING.md
→ named research owner

explicit Tarot / Meihua / Liuyao
→ corresponding method owner

ordinary reading, method unspecified
→ METHOD_ROUTING.md Fast Path
→ high-confidence hit 時立即停止 routing
```

普通 stochastic reading 若需要 ChatGPT／AI 代抽／代起：

```text
method + minimum question contract fixed
→ RUNTIME_DRAW.md hot path / verified cache
→ actual canonical runtime execution
→ Draw / Cast Fact fixed
→ method owner interpretation
```

**Language-model generation ≠ Runtime Draw / Cast。** 模型自行產生牌名、A/B 數字或 6/7/8/9 不算合法 runtime fact。

其他最低規則：

- Astrology v1 是 explicit-request only；不得因題目看起來像星盤題就加入 ordinary auto-routing。
- Astrology raw birth data 在 interpretation 前必須通過 admitted deterministic Fact Gate；模型不得手算 planets / houses / aspects 冒充 engine facts。
- Liuyao Raw Cast 與 deterministic Structured Method Fact 分層；engine unavailable 時保留 Raw Cast，不重起、不手算冒充 engine。
- 只有缺失資訊會 materially 改變 question identity、主要 judgment function、horizon、completion rule、position responsibility、casting/fact source 或 execution viability 時才澄清。
- `QUESTION_DESIGN.md` 只在真的需要拆題、牌位、條件世界或時間窗設計時讀。
- `READING_LIFECYCLE.md` 只在承接／補占／重占／Reality Update／completion／backtest 時讀。
- `READING_RECORD.md` 只在保存／跨聊天室／audit 時讀。
- 最終輸出先回答原題，再給最低充分 evidence；不因模型能延伸就回答未被問的內容。

## ChatGPT Load Pack Fast Path｜one retrieval cache

`CHATGPT_LOAD_PACK.json` 是由 canonical owner sections deterministic 產生的 **derived retrieval cache**，用來減少 GitHub connector round trips；不是 policy authority。

Fresh session 的建議 hot path：

```text
GitHub Connect resolve requested/current ref → exact commit
→ read AGENTS.md at that exact commit
→ ordinary / stochastic eligible profile?
   ├─ yes → fetch CHATGPT_LOAD_PACK.json once at the same exact commit
   │        → use covered bootstrap / ordinary routing / runtime fast-path / output-core excerpts
   └─ no  → bounded-read CHAT_INIT.md only as needed
→ read selected method owner or named research owner at the same exact commit
→ only fetch additional canonical sections when the task actually needs them
→ STOP
```

目前 pack 主要優化 ordinary Tarot / Meihua / Liuyao、explicit stochastic method 與 stochastic continuation。Explicit Astrology 與 explicit research 若載入整包反而增加無關 payload，可直接 bypass pack，從 bounded `CHAT_INIT.md` 進其 canonical owner。

Load-pack 使用規則：

1. canonical owner 永遠優先；pack 只能重用其中的 verbatim hot excerpts。
2. selected method owner / named research owner 在實際 interpretation 或 research judgment 前仍必須讀；pack 不取代它們。
3. pack 只在與本次 resolved Playbook revision 相同的 revision 使用；CI 以 `tools/build_chatgpt_load_pack.py --check` 保證 excerpts 同步。
4. pack 缺失、格式不合法、profile 不涵蓋本題、或內容與已讀 canonical owner衝突 → 直接 fallback canonical reads；不得猜。
5. 同 revision、pack valid 時，不為形式重新抓 pack 已涵蓋的 hot sections；只有 task 超出 fragment coverage 才讀完整 owner。Explicit Astrology / research 等未列入 pack profiles 的 intent 不為形式載入 pack。
6. `PLAYBOOK_INDEX.json` 可做 machine owner discovery；已知 owner 時不為形式再讀 index。
7. Load pack 不改變 GitHub-only retrieval、runtime execution、write、Reading Record storage 或 privacy authority。

## 最低必要路由

一般 ordinary reading：

```text
load pack
→ selected method owner
→ RUNTIME_DRAW additional sections only on cache/acquisition/audit need
→ INPUT_CONTRACT / QUESTION_DESIGN only on material contract/design gap
→ READING_LIFECYCLE only on continuation/backtest need
→ READING_RECORD only on durable storage/audit need
```

明確指定 production Astrology：

直接讀 `ASTROLOGY.md`，不經 ordinary auto-routing；raw birth data 不授權模型自行手算。

```text
bounded CHAT_INIT bootstrap
→ ASTROLOGY.md
→ Astrology deterministic Fact Gate
→ only required provider / schema / evidence owner
→ output
```

Explicit research：

```text
bounded CHAT_INIT bootstrap
→ RESEARCH_ROUTING.md
→ named research owner
→ minimum relevant evidence
```

不要因為「新題」固定全文載入 `INPUT_CONTRACT.md` + `QUESTION_DESIGN.md`，也不要為熟悉手冊掃 full repo、`references/`、`CASE_STUDIES/` 或 old readings。

## Repository Access Policy｜GitHub Connect only

凡 workflow 需要從 GitHub 取得 repository identity、ref、commit、tree、diff、file、section、workflow 或 external GitHub source，一律使用 GitHub connector / GitHub Connect。

禁止替代路徑：

```text
GitHub public HTML
raw.githubusercontent.com
generic Web search
Python requests / urllib
curl / wget
git clone
memory / stale unverified cache
```

connector unavailable／exact read permission blocked且 current task materially 依賴 current GitHub content：

```text
minimum connector/read recovery
→ still unavailable
→ ACCESS BLOCKED
```

不要改走 public/raw/Web。

已通過專門治理的 local verified runtime cache（例如 Randomizer fixed cache）可依 `RUNTIME_DRAW.md` reuse；這不算新的 GitHub acquisition。GitHub retrieval capability 不代表 Python execution、repository write 或 Reading Record storage authority。

## Playbook Freshness Probe｜只在 material trigger

跟隨 floating `main` / latest 時，第一次讀過不代表永久 current。只有以下 material trigger 才 probe：

- 使用者要求 latest／表示 Playbook 已更新；
- stale evidence；
- 即將做 current-rule-sensitive judgment 或 Playbook mutation；
- concrete stale-owner / routing risk。

流程：

```text
cheap HEAD/ref probe
├─ unchanged → reuse confirmed working contract
└─ changed
   → bounded diff
   → reload only material changed owners / current load pack
```

時間經過本身不是 trigger。Pinned SHA / immutable tag 不因 upstream main 漂移而自動更新。

## Task Exceptions｜按需載入

- contract materially ambiguous → `INPUT_CONTRACT.md` relevant sections。
- 需要拆題／牌位／條件世界／時間窗 → `QUESTION_DESIGN.md`。
- continuation / Reality Update / completion / backtest → `READING_LIFECYCLE.md`。
- durable save / cross-chat / audit → `READING_RECORD.md`。
- Tarot × Meihua reconciliation → `CROSS_VALIDATION.md`。
- behavioral regression → `BEHAVIORAL_EVAL.md` + selected scenarios。
- machine owner discovery → `PLAYBOOK_INDEX.json`。
- material session-health risk → `SESSION_HANDOFF.md`。

若 high-leverage prerequisite 已否決後續工作，在正確 boundary 停止，不為形式繼續載入。

## Context Admission｜Historical ≠ Active

- **Active Context**：本次訊息、confirmed reality、本題必要前提、current Input Contract / Draw-Cast Fact / Structured Method Fact / Astrology Fact Bundle，以及使用者明確承接的必要 reading。
- **Historical Context**：未被本題引用的舊占、舊排序、其他人物／事件、已失效窗口、old memory。

Persistence ≠ default loading。只有使用者明確承接／比較／回看，或舊 reading 是本題必要前提時，才升為 Active。

## Session Continuity / Handoff Gate

聊天室長度本身不是 trigger。只有 observable stale-premise / retrieval risk 會 materially 影響 correctness 時才考慮 handoff，例如：

- 反覆找錯 reading identity / completion rule / confirmed reality；
- 使用者重複糾正已成立的重要 fact；
- bounded reconciliation 後仍快速出現 stale assumption；
- 下一步是高影響 Backtest／Record reconciliation／Playbook mutation，而 session risk 已 materially 影響 correctness。

能 bounded reconcile 就先 reconcile；material risk 仍在才使用 `SESSION_HANDOFF.md`。Handoff 是 retrieval index，不是 reality authority / Reading Record，也不自動授權新 reading、重抽、補占或 repository write。

## Authority Order

1. 使用者當次明確指示
2. 已確認現實事實
3. 抽牌／起卦前固定的 Input Contract
4. 本 Repository current canonical rules
5. 實際 Draw / Cast Fact / supplied Astrology Fact Bundle
6. deterministic Structured Method Fact
7. 原始 Interpretation
8. admitted external reference / research evidence
9. old chat impression / memory

新的現實事實可以更新下一題前提，但不能回頭修改舊題 Contract、Raw Cast、Astrology Fact Bundle 或當時 interpretation。

核心原則：

> **Resolve current authority once, load the derived hot cache once, read the selected canonical owner, then expand only on a real evidence gap。**
