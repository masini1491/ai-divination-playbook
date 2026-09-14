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
2. 若使用者明確指定 **production Astrology**（例如「用占星幫我看／看本命盤／看行運」），直接讀 `ASTROLOGY.md`；不要先把它改寫成 Tarot / Meihua / Liuyao，也不要誤送 research router。
3. 若使用者明確要求 **Astrology research**（來源研究、維護 research dossier、比較研究架構）或 Palmistry／手相等已登錄 research line，先讀 `RESEARCH_ROUTING.md`，保留其 research authority。
4. 若使用者未指定方法且屬 ordinary reading，讀 `METHOD_ROUTING.md` 的 Fast Path，依主要 judgment function 自動選目前已支援的 Tarot / Meihua / Liuyao；Astrology v1 不參與 ordinary auto-routing。
5. 若沒有既有牌面／卦象／Cast Fact，也沒有要求自行抽／起，stochastic method 預設由 ChatGPT／AI 代抽／代起卦。
6. stochastic method 必須進 `RUNTIME_DRAW.md`；模型自行生成牌名、數字、6/7/8/9 不算 Runtime Draw / Cast。
7. Liuyao 若被選中，Raw Cast 後再讀 `LIUYAO.md`；完整納甲解讀只有在 Structured Method Fact engine capability 成立時才繼續。
8. Astrology 若被指定，依 `ASTROLOGY.md` 先過 deterministic Fact Gate；raw birth data 不授權模型自行手算 planets / houses / aspects。
9. 只有缺失資訊會 materially 改變 question identity、主要 judgment function、horizon、completion rule、position responsibility、casting/fact source 或 execution viability 時才澄清；此時才讀 `INPUT_CONTRACT.md` 相關 sections。
10. `QUESTION_DESIGN.md` 只在真的需要拆題、設計牌位、條件世界、時間窗比較或修復 question-contract 缺陷時載入；普通清楚的新題不是它的固定 Hot Path。
11. 不先介紹整套 Playbook、文件架構或方法清單；routing 完成後直接處理。
12. 使用者當次明確指定的方法、research line、抽牌／起卦／Astrology fact source、牌數、output 或其他有效限制優先於本節 default。
13. 已提供實際牌面／卦象／六爻 6/7/8/9／Astrology structured facts 時，直接處理既有 fact；不得因 default Runtime 而重抽、重卦、重算或換方法。

核心原則：

> **Natural language in; explicit production Astrology stays Astrology, explicit research intent stays research, ordinary unspecified method routing and execution details are the Agent's job unless a material ambiguity really requires clarification。**

## Ordinary Reading Fast Path｜普通占問最低載入路徑

對 contract 已足夠、沒有承接／回測／正式保存等特殊需求的普通新題，優先使用：

```text
CHAT_INIT
→ explicit Astrology? ASTROLOGY.md
→ otherwise METHOD_ROUTING Fast Path（method 未指定時）
→ selected method owner
→ RUNTIME_DRAW relevant sections（只有 stochastic method 且 AI 需要實際抽／起時）
→ CHATGPT_OUTPUT relevant sections
→ STOP
```

明確 research intent 時不走 production Fast Path，改走：

```text
CHAT_INIT
→ RESEARCH_ROUTING.md
→ named research owner
→ minimum relevant research contracts / evidence
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
- legacy `masini1491/divination-casting-randomizer` 的歷史 provenance、rollback、migration 或尚未完成 Phase 4 的 deployment-compatibility source／ref／commit evidence；current stochastic runtime source 則由本 Repository 的 `runtime/casting/randomizer.py` 擁有；
- Liuyao／Astrology provider／未來 method engine 的 GitHub source、release、license、reference；
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

1. 判斷本次 task：production method selection、新題、解讀、承接／補占、Reality Update、Runtime Draw / Cast、Astrology Fact Gate、Reading Record、Backtest、behavioral eval、explicit research-line request 或 external reference research。
2. 使用者明確指定 production Astrology reading → `ASTROLOGY.md`；不進 ordinary auto-routing。
3. 使用者明確指定 research task / research line → `RESEARCH_ROUTING.md`；只載入 named research owner。
4. 普通新題先走 `Ordinary Reading Fast Path`；不要先載入所有 owner。
5. ordinary reading 方法未指定且需要選方法 → `METHOD_ROUTING.md` Fast Path；只有無法唯一裁決才擴張 tie-breaker。
6. 建立 Active Context：本次訊息、confirmed reality、本題必要前提、使用者明確承接的 reading；其他歷史預設 Historical。
7. Contract 不完整且會 material 改變 judgment → `INPUT_CONTRACT.md` relevant sections；若題目已清楚，不為形式重讀。
8. 需要拆題／牌位／條件世界／時間窗設計 → `QUESTION_DESIGN.md` relevant sections；普通新題不預設載入。
9. 同題／新題、補占／重占、Reality Update／completion／backtest → `READING_LIFECYCLE.md`。
10. ChatGPT 代抽／代起卦 → `RUNTIME_DRAW.md` relevant sections。
11. 選到 Liuyao → `LIUYAO.md`；Raw Cast 與 Structured Method Fact 分層處理。
12. Astrology → `ASTROLOGY.md`；需要解讀前先由 `tools/astrology_runtime.py` 或等價 admitted gate 驗證 structured facts。
13. 正式保存／跨聊天室／audit → `READING_RECORD.md`。
