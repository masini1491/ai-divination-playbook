# AI 占卜提問與治理實戰手冊

一套可重用的 **AI 占卜提問設計、方法路由、占問生命週期、Runtime Draw / Cast、正式 Reading Record 與解讀治理方法論**。

目前已完成 canonical method owner 與 production routing 的方法：

```text
Tarot
Meihua
Liuyao
```

其中 Tarot + Meihua 已有正式 cross-validation contract；Liuyao 已完成 method routing、canonical three-coin Raw Cast 與 method-specific governance，但若要使用完整納甲／六親／世應等 structured facts，仍需要 deterministic Liuyao engine capability 成立。

> **AI / ChatGPT 快速入口：** 實際使用本手冊時，直接從 [`CHAT_INIT.md`](CHAT_INIT.md) 開始並依 task routing 只讀最低必要文件／sections；不需要先完整閱讀本 README，也不要為了「熟悉手冊」掃描整個 Repository。
>
> **GitHub Connect 是本專案唯一 GitHub repository retrieval transport：** 只要需要讀取本 Repo、Randomizer、外部 method engine、GitHub reference、branch／commit／diff／license 等 GitHub-hosted evidence，一律使用 connected GitHub connector。若 connector 不可用而 task materially 依賴 current GitHub content，停在 `ACCESS BLOCKED`；不改走 public HTML、raw URL、generic Web、Python HTTP、`curl`／`wget`／`git clone`。完整規則以 [`CHAT_INIT.md`](CHAT_INIT.md) 為準。

本儲存庫不以整理完整牌義、卦辭或宣稱「算得準」為主要目的，而是處理更前面的問題：

> **怎麼把自然語言占問轉成低歧義、可比較、可追蹤、可驗證的 judgment contract；讓 AI 自動選擇適合的方法，取得可信 Draw / Cast / Structured Method Fact，並在承接、補占、現實更新與回測時維持原契約？**

本手冊把占卜視為**象徵性、反思性與結構化推理工具**；現實決策仍應以可驗證資訊、專業意見與實際條件為優先。

## 一句話使用

啟用本 Repo 後，正常互動可以只有：

```text
我想占……
```

Agent 依 `CHAT_INIT.md` 自動完成：

```text
自然語言問題
→ judgment function detection
→ method routing
→ minimum Input Contract
→ Draw / Cast / Structured Method Fact
→ interpretation
→ 必要時 Reading Record / Reality Update / Backtest
```

使用者不需要先知道 Tarot、Meihua 或 Liuyao 哪一套比較適合。

## 目前方法覆蓋

| 方法 | 主要 judgment responsibility | stochastic source | method owner |
| --- | --- | --- | --- |
| Tarot | 人物心理／互動、選項比較、主觀適配、牌位拆解 | `divination-casting-randomizer` | [`TAROT.md`](TAROT.md) |
| Meihua | 事件演化、主客／體用、轉折、節奏與象徵應期 | `divination-casting-randomizer` | [`MEIHUA.md`](MEIHUA.md) |
| Liuyao | 單一具體事件是否成立、阻礙來源、較具體 outcome / timing | `divination-casting-randomizer` three-coin Raw Cast | [`LIUYAO.md`](LIUYAO.md) |

### Routing 核心差異

```text
她現在怎麼評估我？
→ Tarot

這段關係接下來怎麼演變？
→ Meihua

她會不會在本週五以前主動傳訊息？
→ Liuyao
```

```text
A/B/C 哪個方案比較適合？
→ Tarot

這個合作局勢接下來怎麼轉？
→ Meihua

截至月底前，雙方是否會談妥價格並正式開始合作？
→ Liuyao
```

完整判斷規則見 [`METHOD_ROUTING.md`](METHOD_ROUTING.md)。

## Authority boundary

整套架構刻意分層：

```text
METHOD_ROUTING
→ 決定 judgment function 與 method

CASTING / INPUT ACQUISITION
→ 隨機型方法使用 canonical Randomizer

METHOD ENGINE / CONTRACT
→ 建立 method-specific fixed facts

PLAYBOOK INTERPRETATION GOVERNANCE
→ 解讀、承接、紀錄、Reality Update、Backtest
```

### Randomizer 負責什麼

配套 Repo：

```text
masini1491/divination-casting-randomizer
```

目前支援：

```text
Tarot draw
Meihua A/B cast
Liuyao three-coin raw cast
```

Python CLI：

```text
python randomizer.py tarot --count 6 --format json
python randomizer.py plum --format json
python randomizer.py liuyao --method coins --format json
```

Randomizer 只負責 stochastic acquisition；不負責 AI interpretation，也不把完整六爻納甲邏輯塞進 RNG layer。

### Liuyao 的額外一層

六爻 Raw Cast 只固定：

```text
6 / 7 / 8 / 9 × 6
bottom-to-top
```

完整六爻判斷若需要：

```text
本卦
之卦
納甲
五行
六親
世應
六神
伏神
月建／日辰／旬空等
```

必須由 deterministic engine 建立 Structured Method Fact。Preferred reference 與採用邊界見 [`references/ichingshifa.md`](references/ichingshifa.md)。

核心原則：

> **Randomizer 決定原始 stochastic result；engine 決定 deterministic chart facts；Playbook 決定怎麼問與怎麼解。**

## 核心治理原則

### 1. Contract before result

題目、completion rule、position／method responsibility 必須在看到結果前固定。

### 2. One judgment function first

「會不會、何時、為什麼、好不好、怎麼辦」通常不應全部混進同一 judgment node。

### 3. Draw / Cast Fact 與 interpretation 分離

```text
Question Contract fixed
→ Draw / Cast
→ raw fact fixed
→ Structured Method Fact（需要時）
→ Interpretation
```

不得看到不喜歡的結果後重抽、重起或更換算法。

### 4. Runtime 必須是真執行

> **Language-model generation ≠ random draw / cast。**

ChatGPT 只有實際執行 canonical Runtime tool，才能把結果標為 `chatgpt-runtime`。能力不足時 fail closed。

詳見 [`RUNTIME_DRAW.md`](RUNTIME_DRAW.md)。

### 5. Symbolic consistency ≠ independent reality evidence

不同抽牌／卦象同方向可以說 symbolic consistency，但不能因抽了三次就宣稱三份獨立現實證據。

### 6. Reading history append-only

正式 Reading Record 至少區分：

```text
QUESTION / CONTRACT FACT
DRAW / CAST FACT
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
| [`CHAT_INIT.md`](CHAT_INIT.md) | fresh chat bootstrap、repository access、freshness、task routing、handoff gate |
| [`PLAYBOOK_INDEX.json`](PLAYBOOK_INDEX.json) | machine-readable routing-only owner index |
| [`METHOD_ROUTING.md`](METHOD_ROUTING.md) | Tarot / Meihua / Liuyao method selection |
| [`INPUT_CONTRACT.md`](INPUT_CONTRACT.md) | 題目與 method input / provenance contract |
| [`QUESTION_DESIGN.md`](QUESTION_DESIGN.md) | 問題拆解與牌位／功能設計 |
| [`TAROT.md`](TAROT.md) | Tarot-specific contract |
| [`MEIHUA.md`](MEIHUA.md) | Meihua-specific contract |
| [`LIUYAO.md`](LIUYAO.md) | Liuyao judgment、Raw Cast → Structured Fact、解讀與 fail-closed contract |
| [`RUNTIME_DRAW.md`](RUNTIME_DRAW.md) | Runtime Draw / Cast、cache、source、provenance、fail closed |
| [`CROSS_VALIDATION.md`](CROSS_VALIDATION.md) | 目前正式 Tarot × Meihua reconciliation / evidence lineage |
| [`READING_LIFECYCLE.md`](READING_LIFECYCLE.md) | 新題、承接、條件世界、補占、重占、現實更新、完成、回測 |
| [`READING_RECORD.md`](READING_RECORD.md) | durable reading identity、append-only evidence layers、storage boundary |
| [`CHATGPT_OUTPUT.md`](CHATGPT_OUTPUT.md) | user-visible output / Copy-ready / Pre-Send |
| [`BEHAVIORAL_EVAL.md`](BEHAVIORAL_EVAL.md) | cold-start / behavioral regression |
| [`SESSION_HANDOFF.md`](SESSION_HANDOFF.md) | fresh-session rehydration checkpoint adapter |
| [`references/`](references/) | Cold external source dossiers / license / adoption boundary |

## Cross-validation 現況

目前完整 canonical reconciliation owner 仍是：

```text
Tarot + Meihua
```

Liuyao 可以與其他 readings 並列成 distinct readings，也可以形成 derived synthesis；但在新增專門 reconciliation contract 前，不要把 `Liuyao + Tarot` 或 `Liuyao + Meihua` 宣稱為已 canonical 化的 cross-validation pair。

這保留一個重要原則：

> **新增方法先補 judgment gap，不是先增加投票數。**

## 下一階段方法

未來若加入 Qimen、Da Liu Ren 等方法，仍遵循：

```text
method owner
→ input / casting / deterministic engine authority
→ routing
→ runtime / provenance
→ behavioral regression
→ 才算正式支援
```

Repository 名稱泛化不代表 AI 可以自行發明未定義的方法流程。

## 隱私與公開安全

本 Repo 是公開方法論 repository，不保存：

- 真實姓名與可識別感情／關係細節
- 出生日期、時間與地點等可識別資料
- 健康、性相關私人紀錄
- 私人公司未公開人事、薪資、客戶或專案資訊
- 完整私人 Reading Record / session handoff payload
- secrets / credentials

真實 Reading Record 不得寫入本公開 Playbook。

## 狀態

持續演進中。優先從真實使用中反覆出現的 judgment gap、routing collision、Runtime execution、record integrity 與 backtest 問題反向萃取規則，而不是追求文件數量或術數數量。
