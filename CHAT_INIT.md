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
2. 若使用者未指定方法，讀 `METHOD_ROUTING.md` 的 Fast Path，依主要 judgment function 自動選目前已支援的 Tarot / Meihua / Liuyao；single-method first。只有 Fast Path 無法唯一裁決時才繼續讀後續 tie-breaker。
3. 若沒有既有牌面／卦象／Cast Fact，也沒有要求自行抽／起，預設由 ChatGPT／AI 代抽／代起卦。
4. stochastic method 必須進 `RUNTIME_DRAW.md`；模型自行生成牌名、數字、6/7/8/9 不算 Runtime Draw / Cast。
5. Liuyao 若被選中，Raw Cast 後再讀 `LIUYAO.md`；完整納甲解讀只有在 Structured Method Fact engine capability 成立時才繼續。
6. 只有缺失資訊會 materially 改變 question identity、主要 judgment function、horizon、completion rule、position responsibility、casting method 或 execution viability 時才澄清；此時才讀 `INPUT_CONTRACT.md` 相關 sections。
7. `QUESTION_DESIGN.md` 只在真的需要拆題、設計牌位、條件世界、時間窗比較或修復 question-contract 缺陷時載入；普通清楚的新題不是它的固定 Hot Path。
8. 不先介紹整套 Playbook、文件架構或方法清單；routing 完成後直接處理。
9. 使用者當次明確指定的方法、抽牌／起卦來源、牌數、output 或其他有效限制優先於本節 default。
10. 已提供實際牌面／卦象／六爻 6/7/8/9 時，直接處理既有 fact；不得因 default Runtime 而重抽、重卦或換方法。

核心原則：

> **Natural language in; method routing and execution details are the Agent's job unless a material ambiguity really requires clarification。**

## Ordinary Reading Fast Path｜普通占問最低載入路徑

對 contract 已足夠、沒有承接／回測／正式保存等特殊需求的普通新題，優先使用：

```text
CHAT_INIT
→ METHOD_ROUTING Fast Path（method 未指定時）
→ selected method owner
→ RUNTIME_DRAW relevant sections（只有 AI 需要實際抽／起時）
→ CHATGPT_OUTPUT relevant sections
→ STOP
```

只有遇到具體 evidence gap 才擴張：

```text
contract materially ambiguous
→ INPUT_CONTRACT relevant sections

需要拆題／牌位／條件世界／時間窗設計
→ QUESTION_DESIGN relevant sections

承接／補占／重占／Reality Update／completion／backtest
→ READING_LIFECYCLE relevant sections

正式保存／跨聊天室／audit
→ READING_RECORD relevant sections
```

**不要因為「這是一個新題」就固定全文載入 `INPUT_CONTRACT.md` + `QUESTION_DESIGN.md`。**

## Repository Access Policy｜GitHub Connect 為唯一 GitHub 取得路徑

凡本 Playbook workflow 需要**從 GitHub 取得 repository 內容或 repository identity**，一律使用已連接的 **GitHub connector / GitHub Connect**。這是本專案的 canonical retrieval transport，不只是偏好順序。

本節的「GitHub 內容」包括但不限於：

- 本 Repository 的 `main`、branch／tag、commit SHA、diff、tree、canonical files／sections；
- `masini1491/divination-casting-randomizer` 的 source／ref／commit；
- Liuyao／未來 method engine 的 GitHub source、release、license、reference；
- `references/` 研究需要讀取的任何 GitHub repository；
- freshness probe、rename reconciliation、external GitHub comparison 或其他 GitHub-hosted evidence。

規則：

1. **GitHub Connect first and only**：需要 GitHub repository data 時，直接使用 connected GitHub connector 的 exact read/search/ref/commit operation。
2. 不以 generic Web search、GitHub public HTML、`raw.githubusercontent.com`、Python `requests`／`urllib`、shell `curl`／`wget`、`git clone` 或其他 direct network path 代替 GitHub connector 取得 GitHub 檔案。
3. 若 GitHub connector 尚未連接／不可用，而本次 task materially 依賴 GitHub current content，先提供最低必要的 connect recovery；在 connector 可用前進入 **`ACCESS BLOCKED`**，不要改走 public/raw/Web。
4. `ACCESS BLOCKED` 時不得用模型記憶、舊聊天室摘要、未驗證 cache 或曾經看過的 wording 冒充 current GitHub authority。
5. GitHub connector 可用後，從 exact owner／path／ref 開始 bounded read；**connector available ≠ full repo scan**。
6. 已知 exact path／section owner 時直接讀 target；router／README 只在 discovery 真有需要時使用。
7. 需要 latest／freshness 時，先用 GitHub connector 做 cheap ref／HEAD identity probe；只有 material change 才 bounded-read changed owners。
8. 需要 immutable provenance 時，使用 GitHub connector 把 moving ref resolve 成 exact commit SHA，再讀該 exact revision；不得拿 `main` 字串冒充 commit identity。
9. 已通過專門治理的 local verified cache（例如 `RUNTIME_DRAW.md` 的 Randomizer deterministic cache）可以依其 owner 規則直接 reuse；**local verified reuse 不算新的 GitHub acquisition**，因此不要求每題重新連 GitHub。
10. GitHub connector 只提供 repository retrieval capability；**retrieval authority ≠ Python execution authority ≠ repository write authority ≠ Reading Record storage authority**。
11. 對 GitHub 的 write／create／update／delete 仍需該 task 的明確 write authority；本節只規定「GitHub 檔案怎麼讀」，不自動授權修改任何 repository。
12. 若 connector 本身對 exact read 被 permission gate 擋住且可 request approval，只請求完成該 exact read 所需最低 read permission；不要擴張到 write 或其他 capability。

簡化：

```text
Need GitHub repository data
→ GitHub connector / GitHub Connect
   ├─ available → bounded exact read / ref / commit / diff
   └─ unavailable / blocked
        → minimum connect/read recovery
        → still unavailable
        → ACCESS BLOCKED
```

禁止的替代路徑：

```text
GitHub public HTML
raw.githubusercontent.com
Web search as repository fetch
Python direct HTTP
curl / wget / git clone
memory / stale cache pretending to be current
```

核心原則：

> **All GitHub repository acquisition goes through GitHub Connect. Local verified runtime reuse may avoid a GitHub fetch; when a GitHub fetch is actually needed, no alternate transport substitutes for the connector。**

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

Freshness probe 的 GitHub ref／commit／diff 取得同樣服從前節：**只用 GitHub connector**。

Pinned SHA／tag 本身就是固定 authority，除非使用者要求升級，不跟著 upstream `main` 漂移。

Freshness 只處理規則 identity，不擴張 Runtime、write、Reading Record storage 或其他 authority。

## 啟動順序

1. 判斷本次 task：method selection、新題、解讀、承接／補占、Reality Update、Runtime Draw / Cast、Reading Record、Backtest、behavioral eval 或 external reference research。
2. 普通新題先走 `Ordinary Reading Fast Path`；不要先載入所有 owner。
3. 方法未指定且需要選方法 → `METHOD_ROUTING.md` Fast Path；只有無法唯一裁決才擴張 tie-breaker。
4. 建立 Active Context：本次訊息、confirmed reality、本題必要前提、使用者明確承接的 reading；其他歷史預設 Historical。
5. Contract 不完整且會 material 改變 judgment → `INPUT_CONTRACT.md` relevant sections；若題目已清楚，不為形式重讀。
6. 需要拆題／牌位／條件世界／時間窗設計 → `QUESTION_DESIGN.md` relevant sections；普通新題不預設載入。
7. 同題／新題、補占／重占、Reality Update、completion／backtest → `READING_LIFECYCLE.md`。
8. ChatGPT 代抽／代起卦 → `RUNTIME_DRAW.md` relevant sections。
9. 選到 Liuyao → `LIUYAO.md`；Raw Cast 與 Structured Method Fact 分層處理。
10. 正式保存／跨聊天室／audit → `READING_RECORD.md`。
11. cold-start／behavioral regression → `BEHAVIORAL_EVAL.md` + scenario 所指 owner。
12. machine consumer owner discovery → 可選 `PLAYBOOK_INDEX.json`，命中後仍回 canonical Markdown owner。
13. 先讀最可能否決後續工作的高槓桿前提；若 method、contract、runtime、engine 或 authority 已不成立，先停在正確 boundary。
14. 不為「熟悉手冊」掃 full repo、references、cases 或 old readings。

## 最低必要路由

### 未指定方法

```text
METHOD_ROUTING.md Fast Path
→ 若唯一命中：選 method → STOP routing
→ 若 collision / ambiguity：再讀對應 tie-breaker sections
→ selected method owner
```

### 普通清楚的新題

```text
METHOD_ROUTING Fast Path（若 method 未定）
→ selected method owner
→ RUNTIME_DRAW relevant sections（只有 AI 實際抽／起時）
→ CHATGPT_OUTPUT relevant sections
```

不要僅因「新題」固定加入 `INPUT_CONTRACT.md` 或 `QUESTION_DESIGN.md`。

### 需要修題／重寫題目

```text
INPUT_CONTRACT relevant sections（只有 contract gap）
+ QUESTION_DESIGN relevant sections（只有 design gap）
+ CHATGPT_OUTPUT copy-ready sections（若要交付題目）
```

### Tarot

```text
TAROT.md
+ CHATGPT_OUTPUT relevant sections
+ RUNTIME_DRAW relevant sections only if AI draws
```

### Meihua

```text
MEIHUA.md
+ CHATGPT_OUTPUT relevant sections
+ RUNTIME_DRAW relevant sections only if AI casts
```

### Liuyao

```text
LIUYAO.md
+ CHATGPT_OUTPUT relevant sections
+ RUNTIME_DRAW relevant sections if AI performs three-coin Raw Cast
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
+ CHATGPT_OUTPUT relevant sections
```

目前 Liuyao 與其他方法可以形成 distinct readings / derived synthesis，但尚未自動套用 `CROSS_VALIDATION.md` 的 Tarot × Meihua semantics。

### Runtime Draw / Cast

```text
method fixed
→ minimum contract fixed
→ RUNTIME_DRAW relevant sections
→ actual canonical execution
→ method owner
→ output
```

### Reading Record / Backtest / continuation

依需要加入：

```text
READING_RECORD.md relevant sections
READING_LIFECYCLE.md relevant sections
RUNTIME_DRAW.md provenance sections（需要時）
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
