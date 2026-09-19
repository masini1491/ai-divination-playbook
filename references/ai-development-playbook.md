# 參考來源｜masini1491/ai-development-playbook

Repo: https://github.com/masini1491/ai-development-playbook

授權：MIT（以來源 Repo 當下 LICENSE 為準）

Last reviewed source revision：`50c16aa7cf3c497ed7e0099a006f49acbd07956d`

Relationship：`reference / adapted source`；不是 live moving-policy dependency。本 Repo 只有在 current governance 明確採納後才吸收上游規則，不因來源 `main` 前進而自動改變本 Repo authority。

## 類型

ChatGPT＋Codex＋GitHub 的 AI 協作開發方法論。其主要價值不在占卜內容，而在 **authority、routing、最低充分上下文、scope control、completion evidence、輸出交付與 policy ownership** 等治理設計。

## Authority boundary

本來源只作為 **AI／ChatGPT 行為治理方法論** 參考：

- 不提供塔羅牌義、梅花卦義或術數權威。
- 不覆蓋本 Repo 的 `INPUT_CONTRACT.md`、`QUESTION_DESIGN.md`、`TAROT.md`、`MEIHUA.md`、`CROSS_VALIDATION.md`。
- Codex、Git、CI、Repository mutation、模型成本等工程專屬規則不移植到占卜方法論。

## 值得吸收

### ADAPTED｜調整後採用 — Project AI mode 與 lower-level authority 分離

來源把 Project AI mode 視為 actor topology，而不是 path/action write permission。本 Repo 因此以 `Project AI mode: ChatGPT-Only` 宣告主要 AI actor，同時在 `AGENTS.md` 另外維護 current task / writable target / permission / capability 的 mutation boundary。

### ADAPTED｜調整後採用 — Capability ≠ authority

connector、runtime、write-capable tool 或 host compatibility 只證明 capability；不單獨建立 repository mutation、Reading Record storage 或其他 durable authority。

### ADAPTED｜調整後採用 — External inference / data-egress boundary

來源把 model／provider／router 切換視為可能的 disclosure boundary change。本 Repo 只吸收其中與私人 reading context、birth data、palm images、private company information 等敏感 Context 有關的最低充分原則；不建立通用企業資料分類框架。



### ADAPTED｜調整後採用 — Canonical policy owner

來源將不同責任分配到不同 canonical 文件，其他文件只 routing，避免同一規則重複造成 drift。

本手冊吸收為：

- `CHATGPT_OUTPUT.md` 專門控制 ChatGPT 出題與解讀輸出。
- `TAROT.md`／`MEIHUA.md` 專注證據如何判讀。
- `CHAT_INIT.md` 只負責最低必要 routing。

### ADAPTED｜調整後採用 — Progressive Reading

來源要求先辨識任務，再只讀最低必要主題文件，不為「熟悉手冊」完整掃描所有內容。

本手冊吸收為 `CHAT_INIT.md` 的任務路由，降低舊規則、無關 reference 或過多上下文干擾當次題目。

### ADAPTED｜調整後採用 — Scope expansion guard

來源禁止 ChatGPT／agent 因為「順便發現」其他問題就自動擴張目前 Stage。

本手冊吸收為：

> 原題、牌位／起卦契約與 `exclusions` 是 ChatGPT 輸出硬邊界；模型能聯想到的旁支，不因此取得輸出權限。

### ADAPTED｜調整後採用 — Completion Evidence Guard

來源要求 completion claim 必須由 canonical evidence 支持，不能只接受自然語言聲稱「已完成」。

本手冊吸收為：

> 預測題只有在現實事件真正符合事前 `completion_rule` 時，才能宣告完成或用於完整命中評估；前置信號不能替代完成事實。

### ADAPTED｜調整後採用 — Evidence levels

來源強調 evidence 與 inference 分離，以及證據不足時允許 `INSUFFICIENT OBSERVABILITY`，不為了完成回答而硬猜。

本手冊吸收為：

- `CONFIRMED FACT`
- `DRAW / CAST FACT`
- `METHOD RULE`
- `SYMBOLIC INFERENCE`
- `UNRESOLVED`

並要求 ChatGPT 的語氣與證據層級相稱。

### ADAPTED｜調整後採用 — One Prompt = One Copy Surface

來源要求一份真正要交給 Codex 執行的 Prompt 必須能一次完整複製，不讓使用者重新拼接散落內容。

本手冊轉化為：

> **One Question = One Copy Surface。**

當 ChatGPT 產生讓使用者自己抽牌／起卦的正式題目時，每題各自一個 fenced code block；連續多題不得塞在同一個 block。

### ADAPTED｜調整後採用 — Lowest-sufficient output

來源不以 Prompt／Context 長度作為品質指標，而要求只帶完成任務的最低充分內容。

本手冊吸收為：

- 不輸出牌義字典或萬物類象清單後再任意套用；
- 只解與原題及牌位／卦象證據角色直接相關的最低充分內容；
- 心理、時間、建議、補占等輸出層按題型啟用，不固定全部輸出。

## Not adopted as divination workflow

下列工程／coding-agent 機制不因本次 review 自動移植為占卜方法或 reading workflow：

- Codex root / child model ladder、delegation、parallel-agent routing；
- usage-budget scheduling；
- `Resource-Exhaustion Root Fallback` 作為 Codex workflow；
- external-service deployment / credential operation rules；
- AI 開發手冊自身的 TASKS / BACKLOG maintenance model。

若未來本 Repo 真正需要 alternate inference provider，先處理 current capability、user choice 與 data-egress boundary；不因此建立 Codex execution policy。

## Do not assume

不得因採用此來源而推定：

- 工程開發的 authority hierarchy 可以逐字套用到占卜；本手冊已改寫成符合現實事實、Input Contract、牌／卦資料與 references 的權威順序。
- Codex Prompt、TASKS、CI、Git validation 或 model-cost 規則與塔羅／梅花方法本身有直接關係。
- 「evidence」一詞會讓象徵推論自動取得科學或統計驗證地位；本手冊仍把占卜視為象徵性、結構化推理工具。

## 已影響主文件

- `CHAT_INIT.md`
- `CHATGPT_OUTPUT.md`
- `AGENTS.md`
- `TAROT.md`
- `CROSS_VALIDATION.md`
