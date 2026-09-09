# 新聊天室初始化（Chat Initialization）

本檔只負責建立 fresh session 的最低必要 bootstrap、repository access、task routing 與 handoff gate；不重複保存完整方法規則。

## Default Interaction Profile｜只給 Repo 也能直接使用

當使用者明確要求「依本 Repository／本 Playbook 規則進行占卜」，即啟用本節預設模式。

使用者可以直接說：

```text
我想占……
```

預設規則：

1. 使用者以自然語言提問；Agent 自行正規化最低必要 Input Contract，不把 schema 當表單。
2. 若使用者未指定方法，讀 `METHOD_ROUTING.md`，依主要 judgment function 自動選目前已支援的 Tarot / Meihua / Liuyao；single-method first。
3. 若沒有既有牌面／卦象／Cast Fact，也沒有要求自行抽／起，預設由 ChatGPT／AI 代抽／代起卦。
4. stochastic method 必須進 `RUNTIME_DRAW.md`；模型自行生成牌名、數字、6/7/8/9 不算 Runtime Draw / Cast。
5. Liuyao 若被選中，Raw Cast 後再讀 `LIUYAO.md`；完整納甲解讀只有在 Structured Method Fact engine capability 成立時才繼續。
6. 只有缺失資訊會 materially 改變 question identity、主要 judgment function、horizon、completion rule、position responsibility、casting method 或 execution viability 時才澄清。
7. 不先介紹整套 Playbook、文件架構或方法清單；routing 完成後直接處理。
8. 使用者當次明確指定的方法、抽牌／起卦來源、牌數、output 或其他有效限制優先於本節 default。
9. 已提供實際牌面／卦象／六爻 6/7/8/9 時，直接處理既有 fact；不得因 default Runtime 而重抽、重卦或換方法。

核心原則：

> **Natural language in; method routing and execution details are the Agent's job unless a material ambiguity really requires clarification。**

## Repository Access Policy｜最新版規則的取得方式

當本 Repository 被指定為規則來源時，Agent 應以最低成本取得 canonical current content，不依賴模型記憶、舊聊天室摘要或 cached wording 冒充 latest。

存取優先序：

1. 有 connected GitHub tool／connector → 優先 exact read `main` 上本次需要的 canonical files / sections。
2. connector unavailable 且產品支援 Plugin / Connector discovery → 非阻塞式建議一次連接 GitHub；不要等待使用者完成才繼續合法 fallback。
3. exact read 被 permission gate 擋住且環境能 request approval → 只請求完成該 exact read 所需最低 read permission；核准後重試原操作一次。
4. connector 不可用／失敗後，若 public repository 可讀 → 立即嘗試 GitHub public / raw / Web。
5. public / raw / Web 成功 → 依 bounded routing 繼續；同一聊天室不重複 connector 推銷。
6. connector + public/raw/Web 都不能可靠取得 canonical current content → `ACCESS BLOCKED`。
7. `ACCESS BLOCKED` 時不得用 memory、舊摘要或未驗證 cache 冒充 `main`；若 connector recovery 仍可能成立，可再提供一次明確連接入口。
8. 使用者完成 GitHub connection 後，重新從 `CHAT_INIT.md` rehydrate；不要求重貼原問題。
9. 若 connector unsupported／declined／still fails → 保持 `ACCESS BLOCKED`。
10. 不把「請使用者貼整個 Repo」當第一 recovery；最後只能手動時，只要求本 task 最低必要 owner／section。
11. 同一 permission/network mechanism 已證明被擋，不做無界等價重試。
12. Connector 可用 ≠ full repo scan；仍只讀最低充分 canonical surfaces。
13. 已知 exact path／section owner → 直接讀 target，不繞 README ceremony。
14. Web fallback 只改 access mechanism，不改 authority。

簡化：

```text
GitHub connector
  ↓ unavailable / exact read blocked
minimum read recovery if supported
  ↓ still unavailable
one non-blocking connect suggestion
  ↓ continue
public / raw / Web
  ↓ success
bounded canonical routing

all fail
→ ACCESS BLOCKED
```

核心原則：

> **Prefer connector, recover only minimum read authority, continue public fallback when possible, never fall back to memory as canonical truth。**

## Playbook Freshness Probe｜長聊天室的版本新鮮度

第一次讀過 `main` 不代表永久 current。若 workflow 跟隨 floating `main`／latest，只有 material trigger 才做 cheap revision probe。

### Trigger

- 使用者明確說 Playbook 已更新／要求 latest；
- 出現 stale evidence；
- 即將進入 current-rule-sensitive judgment，例如新的重要 method routing、Runtime governance、Reading Record／Backtest 或 Playbook mutation；
- session 已出現 concrete stale-owner／routing risk，且 correctness 依賴 current rule。

**時間經過本身不是 trigger。** 不建立固定分鐘 polling。

### Probe result

```text
HEAD unchanged
→ reuse confirmed working contract

HEAD changed
→ bounded diff
→ only reload material changed owners

changed but irrelevant
→ update observed identity only

probe unavailable + currentness required
→ FRESHNESS UNAVAILABLE / STOP boundary
```

Pinned SHA／tag 本身就是固定 authority，除非使用者要求升級，不跟著 upstream `main` 漂移。

Freshness 只處理規則 identity，不擴張 Runtime、write、Reading Record storage 或其他 authority。

## 啟動順序

1. 判斷本次 task：method selection、新題、解讀、承接／補占、Reality Update、Runtime Draw / Cast、Reading Record、Backtest、behavioral eval 或 external reference research。
2. 方法未指定且需要選方法 → `METHOD_ROUTING.md`。
3. 建立 Active Context：本次訊息、confirmed reality、本題必要前提、使用者明確承接的 reading；其他歷史預設 Historical。
4. Contract 不完整且會 material 改變 judgment → `INPUT_CONTRACT.md`；若題目已清楚，不為形式重讀。
5. 同題／新題、補占／重占、Reality Update、completion／backtest → `READING_LIFECYCLE.md`。
6. ChatGPT 代抽／代起卦 → `RUNTIME_DRAW.md`。
7. 選到 Liuyao → `LIUYAO.md`；Raw Cast 與 Structured Method Fact 分層處理。
8. 正式保存／跨聊天室／audit → `READING_RECORD.md`。
9. cold-start／behavioral regression → `BEHAVIORAL_EVAL.md` + scenario 所指 owner。
10. machine consumer owner discovery → 可選 `PLAYBOOK_INDEX.json`，命中後仍回 canonical Markdown owner。
11. 先讀最可能否決後續工作的高槓桿前提；若 method、contract、runtime、engine 或 authority 已不成立，先停在正確 boundary。
12. 不為「熟悉手冊」掃 full repo、references、cases 或 old readings。

## 最低必要路由

### 未指定方法

```text
METHOD_ROUTING.md
→ 選 method
→ 對應 method owner
```

### 新題／重寫題目

```text
METHOD_ROUTING（若 method 未定）
+ INPUT_CONTRACT
+ QUESTION_DESIGN
+ CHATGPT_OUTPUT relevant sections
```

### Tarot

```text
TAROT.md
+ CHATGPT_OUTPUT.md
+ RUNTIME_DRAW.md only if AI draws
```

### Meihua

```text
MEIHUA.md
+ CHATGPT_OUTPUT.md
+ RUNTIME_DRAW.md only if AI casts
```

### Liuyao

```text
LIUYAO.md
+ CHATGPT_OUTPUT.md
+ RUNTIME_DRAW.md if AI performs three-coin Raw Cast
```

若完整六爻判斷需要 deterministic chart facts：

```text
Raw Cast Fact
→ LIUYAO Structured Method Fact Gate
→ deterministic engine
→ Interpretation
```

Engine unavailable 時保留 Raw Cast，不重起，也不由模型手算後冒充 engine。

### Tarot + Meihua cross-validation

```text
TAROT.md
+ MEIHUA.md
+ CROSS_VALIDATION.md
+ CHATGPT_OUTPUT.md
```

目前 Liuyao 與其他方法可以形成 distinct readings / derived synthesis，但尚未自動套用 `CROSS_VALIDATION.md` 的 Tarot × Meihua semantics。

### Runtime Draw / Cast

```text
method fixed
→ minimum contract fixed
→ RUNTIME_DRAW.md
→ actual canonical execution
→ method owner
→ output
```

### Reading Record / Backtest / continuation

依需要加入：

```text
READING_RECORD.md
READING_LIFECYCLE.md
RUNTIME_DRAW.md provenance sections
method owner
```

## Context Admission｜舊占不預設進入當前題

資訊分兩類：

- **Active Context**：本次訊息、confirmed reality、本題 Contract／Draw-Cast Fact／Structured Method Fact、使用者明確指定承接的必要 reading。
- **Historical Context**：未被本題引用的舊占、舊排序、其他人物／事件、已失效窗口、old memory。

Persistence ≠ default loading。只有使用者明確承接／比較／回看，或本題以舊 reading 作必要條件前提時，才升為 Active。

## Session Continuity / Handoff Gate｜長聊天室交接

聊天室長本身不是 trigger；真正問題是 observable stale-premise / retrieval risk。

Material signals：

- 反覆找錯 reading identity / completion rule / confirmed reality；
- 使用者重複糾正已明確成立的 material fact；
- session 跨大量獨立 readings／人物／時間窗，而下一步只需很小 working set；
- bounded reconciliation 後仍快速出現 stale assumption；
- 下一步是高影響 Backtest／Record reconciliation／Playbook mutation，而 session risk 已會改變 correctness。

規則：

- 不捏造 context meter；
- length alone ≠ handoff trigger；
- 能 bounded reconcile 就先 reconcile；
- material risk 仍在才建立最低充分 checkpoint；
- checkpoint 是 retrieval index，不是 reality authority／Reading Record；
- fresh session 重新確認 current Playbook 與 active reading evidence；
- handoff 不自動建立新 reading、重抽、補占權或 repository write authority。

需要 checkpoint 時使用 `SESSION_HANDOFF.md`。

## 權威順序

1. 使用者當次明確指示
2. 已確認現實事實
3. 抽牌／起卦前固定的 Input Contract
4. 本 Repository current canonical rules
5. 實際 Draw / Cast Fact
6. deterministic Structured Method Fact（若方法需要）
7. 原始 Interpretation
8. external references
9. old chat impression / memory

新的現實事實可以更新下一題前提，但不能回頭修改舊題 Contract、Raw Cast 或當時 interpretation。

核心原則：

> **Natural-language activation → bounded method routing → actual facts → method-specific interpretation; preserve identity, preserve provenance, fail closed at the exact missing layer。**
