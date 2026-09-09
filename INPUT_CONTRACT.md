# 占卜輸入契約（Input Contract）

本章定義一個占卜題目在抽牌／起卦前，最低限度應保存哪些資訊。目的不是把占卜變成表單，而是避免後續因上下文缺失、牌位漂移、起卦規則不明、Raw Cast／Structured Method Fact 混淆或來源不清而無法回看。

本章只負責**保存題目身份與方法輸入**；「這次變化是否真的構成新題、能否承接／補占／重占、何時完成與回測」統一由 [`READING_LIFECYCLE.md`](READING_LIFECYCLE.md) 判定。

## Section Router｜只讀本題需要的段落

- **普通自然語言題，contract 已足夠** → 不必全文讀本檔；直接由 Agent 正規化。
- **缺欄位、需要確認最低 contract** → §1～2。
- **預測／completion／時間窗** → §3～5。
- **Runtime provenance** → §1、§6。
- **正式保存／跨聊天室／audit** → §1、§6～8。
- **Liuyao** → §1、§5～6，method-specific 細節回 [`LIUYAO.md`](LIUYAO.md)。

若 current task 已由使用者自然語言與 method owner 唯一固定，**不要為形式載入整份 Input Contract**。

## 1. 最小輸入欄位

建議至少記錄：

```text
question:        實際要判斷的問題
question_type:   比較 / 時間 / 流程 / 原因 / 人物 / 狀態 / 校正 / outcome
subject:         誰／什麼是主要判斷對象
horizon:         時間範圍；若不適用寫 N/A
completion_rule: 何種現實事件才算「發生／完成」；若不適用寫 N/A
method:          Tarot / Meihua / Liuyao / Tarot+Meihua
context_facts:   已確認、會改變判斷的現實資訊
exclusions:      明確不要求判斷的事項
```

若使用 Tarot，再補：

```text
deck:            牌組；未指定時標示預設系統
reversals:       是否使用逆位
spread:          牌陣或自訂牌位
positions:       每一牌位的唯一語意
cards_source:    使用者提供 / 實體抽牌 / divination-casting-randomizer / chatgpt-runtime / 其他工具
seed_or_record:  若工具支援可重現亂數，保存 seed、draw id 或 runtime record
```

若使用 Meihua，再補：

```text
casting_source:  時間 / 數字 / 聲音 / 物象 / 方位 / 外應 / divination-casting-randomizer / chatgpt-runtime / 其他
casting_rule:    此次實際採用的算法
calendar_rule:   若使用時間起卦，記錄曆法與時辰／跨日慣例
raw_input:       原始時間、數字或外應資料
perspective:     體／用與吉凶相對於誰、哪個事件與何種有利方向判定
```

若使用 Liuyao，再補：

```text
casting_source:  使用者提供 / 實體起卦 / divination-casting-randomizer / chatgpt-runtime / 其他
cast_method:     three-coins / 其他已明確指定的方法
raw_lines:       6 個 6/7/8/9，由初爻至上爻
line_order:      bottom-to-top
cast_timestamp:  實際起卦時間；完整納甲若使用月日條件時尤其重要
engine_name:     deterministic engine；若尚未執行可寫 N/A
engine_ref:      可驗證版本／commit；未知時 unknown
```

完整六爻 Structured Method Fact（本卦、之卦、納甲、六親、世應、六神、伏神、月建／日辰／旬空等）由 [`LIUYAO.md`](LIUYAO.md) 與 deterministic engine 管理；**不要把 engine 計算結果混進 Raw Cast Fact。**

若 `cards_source = chatgpt-runtime` 或 `casting_source = chatgpt-runtime`，表示 ChatGPT／AI **實際執行** canonical Runtime Draw / Cast tool，而不是語言模型自行報出牌名、數字或 6/7/8/9。詳細執行條件與 fail-closed 規則見 [`RUNTIME_DRAW.md`](RUNTIME_DRAW.md)。

Runtime 建議額外保存：

```text
runtime_tool:              divination-casting-randomizer-python
runtime_algorithm_version: tool output 中的 algorithm_version
runtime_schema_version:    tool output 中的 schema_version
runtime_source_commit:     已知的 randomizer.py commit SHA；未知時明確寫 unknown
runtime_generated_at:      tool output timestamp
```

上述 provenance 欄位不是每次都必須對使用者完整展示，但若要正式記錄、回測或跨聊天室接續，應盡量保留。

`divination-casting-randomizer` 指配套專案 `masini1491/divination-casting-randomizer`。若工具未提供 seed 或 draw id，也至少應保存題目、時間與實際 Draw / Cast Fact。

若 Meihua `casting_source = divination-casting-randomizer` 或 `chatgpt-runtime` 且實際使用其 canonical 雙數工具，應把當次 A、B 原始數字與固定雙數起卦規則一併視為 canonical input；解讀端不應另行取數或切換起卦法。

若 Liuyao `casting_source = divination-casting-randomizer` 或 `chatgpt-runtime`，六個 `6/7/8/9` 一旦形成 Raw Cast Fact 即固定；deterministic engine 只能基於既有 raw lines 排盤，不得重新起卦。

## 2. Contract 是 Agent 的正規化目標，不是使用者表單

上述欄位主要是**內部保存契約**，不是要求使用者在每次占卜前逐欄填寫。

ChatGPT／AI 應採用 progressive contract admission：

1. 先從使用者當次訊息、已確認現實事實與明確承接的 Active Context 中提取可確定欄位；
2. 能由題意安全判定為 `N/A`、既定預設或既有 canonical method contract 的欄位，直接正規化，不為形式重新詢問；
3. 只有缺少的資訊會**實質改變 question identity、主要 judgment function、horizon、completion rule、牌位責任、起卦方式、line order、engine requirement 或可否執行**時，才需要澄清；
4. 澄清時只問最小必要問題，優先一次一個短問題，不把 schema 原樣丟給使用者；
5. 若資訊不足但仍可在明確縮小範圍後安全處理，應採 reduced scope 並標出未判斷部分，而不是要求無關資料；
6. 若使用者已提供足以形成乾淨契約的自然語言問題，直接整理並進入下一步，不要求他再用固定格式重填一次。

例如使用者說：

> 「幫我看從現在到年底，她會不會主動重新聯絡我；有傳訊息、回限動、主動分享事情或提出見面都算。」

Agent 可以自行正規化出 `subject`、`horizon` 與 `completion_rule`；不應再把完整 Input Contract 表單丟回去要求填寫。

核心原則：

> **Schema completeness is an agent responsibility; user friction should be proportional only to genuinely missing, decision-changing information。**

除非使用者要求 audit、正式紀錄或 copy-ready technical contract，否則不必把內部 YAML／schema 全部展示給使用者。

## 3. 背景與真正問題必須分開

背景資訊可以很多，但真正問題只能有一個主要判斷功能。

錯誤：

> 我現在工作很忙、主管如何、公司十月調薪、也可能轉職，請看會不會升職、加多少、何時離職、去哪家公司。

較佳做法：

- `context_facts` 保存背景。
- `question` 只問這一輪真正要判斷的事。
- 其他問題拆成後續階段。

## 4. 預測題必須有時間範圍

凡涉及「會不會發生／何時發生」，至少要定義：

- 起始時間；
- 結束時間或候選窗口；
- 何種現實事件算完成。

「今年會不會跳槽」仍可能太模糊，因為「開始看職缺」與「新公司報到」是不同事件。

若主要功能已經是「截至某 horizon，X 是否完成」的單一外部可驗證 outcome，未指定方法時回 [`METHOD_ROUTING.md`](METHOD_ROUTING.md)，通常由 Liuyao 承擔主要 judgment responsibility。

## 5. 牌位／起卦契約必須在結果出現前固定

### Tarot

牌位語意先寫，再抽牌。

### Meihua

起卦來源、算法與判斷視角先寫，再看卦。

### Liuyao

先固定 question identity、horizon／completion rule、cast method 與 line order，再產生六個 6/7/8/9；Raw Cast 固定後才交 deterministic engine 建 Structured Method Fact。

看到結果後才改規則，等同改變題目。

若由 ChatGPT 使用 Runtime Draw / Cast，順序仍必須是：

```text
Question Contract fixed
→ Runtime execution
→ DRAW / CAST FACT fixed
→ Structured Method Fact（需要時）
→ Interpretation
```

不能先由程式抽出結果，再倒推問題、牌位、completion rule 或用神責任。

## 6. 可重現性與 provenance

若工具能保存亂數種子（seed）、抽牌紀錄識別碼（draw id）、時間戳、原始數字、raw lines、起卦算法、runtime tool version、schema version、source commit 或 engine ref，應一併保存。

這不是為了證明占卜具有客觀預測力，而是為了：

- 避免「重抽／重起到滿意為止」；
- 能回查同一結果是否被不同方式重新解讀；
- 區分「同一題重占」與「新事實出現後的新題」；
- 區分實際程式執行與模型自行生成結果；
- 區分 stochastic Raw Cast authority 與 deterministic engine authority。

## 7. Question Identity 由生命週期規則判斷

本檔保存 `question`、`subject`、`horizon`、`completion_rule`、`context_facts`、`exclusions` 與方法輸入，但不在這裡重複定義「何時算新題」。

若出現：

- 現實前提改變；
- 新的子問題／條件分支；
- 判斷對象改變；
- 時間窗或完成標準重定義；
- 原契約缺陷需要修正版；

是否因此構成新的 judgment node，以及能否重新抽牌／起卦，依 [`READING_LIFECYCLE.md`](READING_LIFECYCLE.md) 的 Question Identity Gate。

## 8. 建議保存格式

Tarot：

```yaml
question: "..."
question_type: comparison
subject: "..."
horizon: "2026-09-01 to 2026-12-31"
completion_rule: "..."
method: tarot
context_facts:
  - "..."
exclusions:
  - "不判斷結果好壞，只比較發生可能性"
tarot:
  deck: RWS-compatible
  reversals: true
  spread: custom-5
  positions:
    1: option-a-likelihood
    2: option-b-likelihood
    3: option-c-likelihood
    4: option-d-likelihood
    5: adjudicator
  cards_source: chatgpt-runtime
  runtime_tool: divination-casting-randomizer-python
  runtime_algorithm_version: "2"
  runtime_schema_version: "4"
  runtime_source_commit: "unknown"
```

Meihua：

```yaml
method: meihua
meihua:
  casting_source: chatgpt-runtime
  casting_rule: "A÷8→上卦；B÷8→下卦；(A+B)÷6→動爻；餘0分別視為坤／第6爻"
  raw_input: "574, 393"
  runtime_tool: divination-casting-randomizer-python
  runtime_algorithm_version: "2"
  runtime_schema_version: "4"
  perspective:
    subject: "求問者本人"
    event: "某事件的演化"
    favorable_means: "依本題固定視角判定"
```

Liuyao：

```yaml
method: liuyao
horizon: "..."
completion_rule: "..."
liuyao:
  casting_source: chatgpt-runtime
  cast_method: three-coins
  line_order: bottom-to-top
  raw_lines: [7, 8, 9, 6, 7, 8]
  cast_timestamp: "..."
  runtime_tool: divination-casting-randomizer-python
  runtime_algorithm_version: "2"
  runtime_schema_version: "4"
  runtime_source_commit: "unknown"
  engine_name: "..."
  engine_ref: "unknown"
```

上方 YAML 是供工具與代理辨識的技術欄位，因此保留英文鍵名；其語意與使用規則以本文件的繁中說明為準。

這份結構化紀錄是後續解讀、生命週期判斷、交叉驗證／derived synthesis 與案例研究的共同輸入。