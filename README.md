# 塔羅 × 梅花易數提問設計實戰手冊

一套可重用的 **塔羅（Tarot）＋梅花易數（Meihua Yishu）提問設計、占問生命週期、ChatGPT Runtime Draw、正式 Reading Record 與解讀治理方法論**。

> **AI / ChatGPT 快速入口：** 實際使用本手冊時，直接從 [`CHAT_INIT.md`](CHAT_INIT.md) 開始並依 task routing 只讀最低必要文件／sections；不需要先完整閱讀本 README，也不要為了「熟悉手冊」掃描整個 Repository。
>
> **建議搭配 GitHub connector：** 若 ChatGPT 可連接 GitHub，建議啟用 GitHub connector，讓它能直接讀取本 Repository 的最新 `main` 與需要的 canonical files／sections，通常會比一般 Web fallback 更穩定、也更適合持續承接使用；但 connector 不是使用本手冊的必要條件。實際 repository access／fallback／freshness 規則仍以 [`CHAT_INIT.md`](CHAT_INIT.md) 為準。

本儲存庫不以整理完整牌義、卦辭或宣稱「算得準」為主要目的，而是處理更前面的問題：

> **怎麼把模糊、混合、容易被解讀污染的問題，改寫成可比較、可追蹤、可驗證、低歧義的占卜題目；並讓 ChatGPT 在自行抽牌、承接、補占、正式保存、現實更新與回測時仍維持原契約？**

本手冊把占卜視為**象徵性、反思性與結構化推理工具**；現實決策仍應以可驗證資訊、專業意見與實際條件為優先。

## 這套手冊主要解決什麼

常見失敗包括：

- 同一牌位同時承擔「發生可能性、好壞、滿意度、後果」多種功能。
- 把「牌很漂亮／卦很吉」直接當成事件機率最高。
- 尚未確認主分支，就繼續追問分支內的數值、時間或細節。
- 因不喜歡第一次結果而反覆重抽／重卦。
- 把同一卦批次套用到彼此獨立的新問題。
- 塔羅與梅花易數彼此硬投票，而沒有先分工。
- 把啟動、轉折、決策、完成等不同事件層級混在同一時間題。
- ChatGPT 把象徵推論講成已確認事實，或回答原題 `exclusions` 已排除的內容。
- 承接前占時，把「前一組較支持 X」逐步滑成「X 已經會發生」。
- 回測時用前置信號替代原本 `completion_rule`，或把事後重讀冒充當時主結論。
- 多人物平行題只給一份模板，要求使用者自行換名字。
- ChatGPT 沒有真正執行程式，卻自行報一組牌並聲稱是隨機抽牌。
- 保存紀錄時把原始解讀、後續現實與事後重讀混寫，導致後來無法知道「當時到底說了什麼」。
- 長聊天室沿用過時 Playbook 規則，或讓大量舊 reading branch 污染 current judgment。
- 把「抽了很多次都同方向」誤當成同等數量的獨立證據。

## 核心原則

### 1. 牌位先有契約，才抽牌

每一牌位只能有清楚、可回查的主要功能。不能抽完後再依牌面改功能。

### 2. 發生可能性不等於情境品質

> **最正面的牌，不必然等於最可能發生。**

若題目是純比較，應明確限制各選項只比較「實際落地的相對可能性」。

### 3. 先判斷主分支，再問分支細節

如果 B 問題成立依賴 A 問題，先處理 A。若只是想分析「假設 A 成立時」的內部情況，而 A 尚未被現實確認，使用**條件世界（Conditional World）**，不要把 A 偷偷升格成事實。

### 4. 一題只保留一個主要判斷功能

「會不會、何時、為什麼、好不好、怎麼辦」通常應拆題，而不是全部塞進同一牌陣／同一卦。

### 5. 占問有生命週期，不只是一次抽牌

```text
QUESTION DRAFT
  ↓
CONTRACT FIXED
  ↓
DRAW / CAST
  ↓
INTERPRETED
  ↓
WAITING FOR REALITY
  ├─ 新現實資訊 → 新 judgment node
  ├─ 明確 unresolved function → 合法 follow-up
  └─ completion rule / horizon 可判定 → RESOLVED
        ↓
      BACKTEST（需要時）
```

完整規則見 [`READING_LIFECYCLE.md`](READING_LIFECYCLE.md)。

### 6. 塔羅與梅花先分工，再交叉驗證

- **塔羅**：選項比較、人物／關係動態、事件流程、阻礙、相對適配度。
- **梅花易數**：事件結構、主客／體用、轉折、動爻、外應與應期。

交叉驗證是 reconciliation，不是多一票；**Draw count ≠ independent evidence count**。同一題、近義重抽、derived summary 或多次同方向結果不能只靠數量灌高 confidence。見 [`CROSS_VALIDATION.md`](CROSS_VALIDATION.md)。

### 7. 輸入契約先於解讀

抽牌／起卦前至少固定：

- `question`
- `question_type`
- `subject`
- `horizon`
- `completion_rule`
- `context_facts`
- `exclusions`
- 塔羅牌位／牌面來源，或梅花起卦來源／算法／原始輸入／判斷視角

見 [`INPUT_CONTRACT.md`](INPUT_CONTRACT.md)。

### 8. ChatGPT 自己抽牌必須是真正 Runtime Draw

如果使用者要求：

> 「你直接幫我抽。」

ChatGPT 只有在本次環境能**實際執行 Python**，並執行 `masini1491/tarot-plum-randomizer/randomizer.py` 或與其明確同步的 canonical runtime tool 時，才可以把結果標記為 `chatgpt-runtime`。

> **Language-model generation ≠ random draw。**

沒有 runtime、程式取得失敗或執行失敗時，必須 fail closed：改用 Web Randomizer／使用者自行抽牌，不能由模型自行想一組牌冒充隨機結果。

完整規則見 [`RUNTIME_DRAW.md`](RUNTIME_DRAW.md)。

### 9. 正式紀錄不改寫歷史

若一次占問需要跨聊天室保存、等待現實驗證或未來回測，建立正式 Reading Record，至少保留：

```text
stable reading identity
+ lifecycle status
+ QUESTION / CONTRACT FACT
+ DRAW / CAST FACT
+ ORIGINAL INTERPRETATION
+ REALITY UPDATE
+ RETROSPECTIVE INTERPRETATION
+ BACKTEST JUDGMENT
```

後來的現實與事後重讀用 append-only 追加，不回頭改寫原始 Contract、牌／卦或當時主結論。

> **Interpretation is not reality evidence; retrospective insight is not original prediction。**

完整規則見 [`READING_RECORD.md`](READING_RECORD.md)。真實 Reading Record 不得寫入本公開 Playbook，即使 Agent 對 Repo 有寫入權限也一樣。

### 10. 長聊天室要處理 freshness 與 handoff，不靠猜 Context

若同一聊天室長期使用浮動 `main`，只有在使用者明確說規則已更新、出現 stale evidence 或 current-rule-sensitive decision 時才做便宜的 HEAD/ref probe；**時間經過本身不是 freshness trigger**。HEAD 變更後只重讀 material changed owners，不為任何 commit 全庫重掃。

若長 session 出現可觀察 stale-premise／retrieval risk，先 bounded reconciliation；風險仍在時才建立最低充分 checkpoint 並建議 fresh session。Handoff 只攜帶 pointer 與 current working state，不是新的 authority。見 [`CHAT_INIT.md`](CHAT_INIT.md) 與 [`SESSION_HANDOFF.md`](SESSION_HANDOFF.md)。

### 11. ChatGPT 的輸出也要有契約

ChatGPT 必須：

- 守住原題與 `exclusions`；
- 區分已確認現實事實、抽牌／起卦事實、方法規則與象徵推論；
- 證據不足時允許 `UNRESOLVED`／「無法可靠區分」；
- 不把塔羅／梅花直接換算成偽精確百分比；
- 只有原題需要時才輸出心理、時間、建議或補占；
- 送出前做 bounded Pre-Send check。

若產生讓使用者自己抽牌／起卦的正式題目：

> **One Question = One Copy Surface。**

多人物平行題即使只有名字不同，也必須每個人物完整展開一題，不要求使用者自行替換名稱。

見 [`CHATGPT_OUTPUT.md`](CHATGPT_OUTPUT.md)。

## 文件架構

| 文件 | 主要責任 |
| --- | --- |
| [`CHAT_INIT.md`](CHAT_INIT.md) | 新聊天室 bootstrap、repository access、Playbook freshness、Context admission、task routing、session handoff gate |
| [`PLAYBOOK_INDEX.json`](PLAYBOOK_INDEX.json) | machine-readable routing-only capability／owner index；不是 policy/state authority |
| [`SESSION_HANDOFF.md`](SESSION_HANDOFF.md) | 長聊天室最低充分 checkpoint／rehydration adapter |
| [`METHOD_ROUTING.md`](METHOD_ROUTING.md) | 未指定方法時，依 judgment function 選 Tarot／Meihua／Both |
| [`INPUT_CONTRACT.md`](INPUT_CONTRACT.md) | 抽牌／起卦前要保存哪些題目、方法輸入與 provenance |
| [`QUESTION_DESIGN.md`](QUESTION_DESIGN.md) | 問題怎麼拆、牌位怎麼定、高頻 Question Patterns |
| [`READING_LIFECYCLE.md`](READING_LIFECYCLE.md) | 新題、承接、條件世界、補占、重占、現實更新、完成、horizon、回測 |
| [`READING_RECORD.md`](READING_RECORD.md) | 正式 Reading Record 的 identity、status、六層證據、append-only 與 storage boundary |
| [`RUNTIME_DRAW.md`](RUNTIME_DRAW.md) | ChatGPT 自行程式抽牌／起卦、canonical tool、capability gate、fail-closed |
| [`TAROT.md`](TAROT.md) | Tarot-specific 牌位、牌陣與解讀規則 |
| [`MEIHUA.md`](MEIHUA.md) | Meihua-specific 起卦、主互變、體用、動爻、外應與應期 |
| [`CROSS_VALIDATION.md`](CROSS_VALIDATION.md) | Tarot × Meihua 分工、同題對齊、衝突 reconciliation、evidence lineage |
| [`CHATGPT_OUTPUT.md`](CHATGPT_OUTPUT.md) | ChatGPT 出題／解讀、信心語言、Copy-ready、Pre-Send |
| [`BEHAVIORAL_EVAL.md`](BEHAVIORAL_EVAL.md) | Cold：fresh／bounded behavioral regression scenarios |
| [`evals/regression_matrix.json`](evals/regression_matrix.json) | Behavioral regression change-class selection metadata |
| [`tools/behavioral_eval.py`](tools/behavioral_eval.py) | Eval record／matrix deterministic metadata validator |
| [`CASE_STUDIES/`](CASE_STUDIES/) | Cold：匿名失敗案例與方法演進 |
| [`references/`](references/) | Cold：外部 GitHub 來源、採用狀態、授權、authority boundary |
| [`AGENTS.md`](AGENTS.md) | 薄 governance / maintenance router |

## AI 最小讀取方式

不要每次完整掃描全部文件。從 `CHAT_INIT.md` 進入，再依工作 bounded-read：

- **方法未定** → `METHOD_ROUTING`
- **出新題** → `INPUT_CONTRACT` + `QUESTION_DESIGN` + `CHATGPT_OUTPUT` 出題 sections
- **一般塔羅解讀** → `TAROT` + `CHATGPT_OUTPUT` 解讀 sections
- **一般梅花解讀** → `MEIHUA` + `CHATGPT_OUTPUT` 解讀 sections
- **ChatGPT 自行抽牌／起卦** → 再加入 `RUNTIME_DRAW`
- **正式保存／跨聊天室承接／audit record** → 再加入 `READING_RECORD`
- **承接／補占／重占／現實更新／回測** → 再加入 `READING_LIFECYCLE`
- **塔羅＋梅花整合** → 再加入 `CROSS_VALIDATION`
- **長聊天室 stale/retrieval risk** → `SESSION_HANDOFF`
- **machine routing discovery** → 可選讀 `PLAYBOOK_INDEX.json`，命中後仍回 canonical owner
- **behavioral regression** → `BEHAVIORAL_EVAL`；machine selection／record validation 可用 `evals/` + `tools/`
- `CASE_STUDIES/`、`references/`、未被指定的舊占預設不載入

資訊被保存，不代表每一題都要付 Context cost。

## 兩種抽牌工作流

### A. 使用者自己抽

```text
ChatGPT 設計題目／牌位
→ 每題獨立 copy surface
→ 使用者貼進 Randomizer
→ 使用者回貼實際結果
→ ChatGPT 解讀
```

### B. ChatGPT Runtime Draw

```text
ChatGPT 設計／確認題目契約
→ Runtime Capability Gate
→ 執行 canonical randomizer.py
→ 固定 raw DRAW / CAST FACT
→ 依原契約解讀
```

能執行程式不會改變 `READING_LIFECYCLE.md` 的重抽紀律；同一題不能因為 Python 很方便就反覆重抽。

## 配套抽牌／起卦工具

本手冊搭配 **Tarot + Plum Randomizer**：

- 線上工具：`https://tarot-plum-randomizer-masini1491-9205.vercel.app/`
- Repo：`https://github.com/masini1491/tarot-plum-randomizer`

Randomizer 有兩個入口：

```text
index.html      → Web / 手機使用
randomizer.py   → Python / ChatGPT / AI runtime CLI
```

Python CLI 只使用標準庫，支援：

```text
python randomizer.py tarot --count 6
python randomizer.py plum
python randomizer.py both --count 6
python randomizer.py batch --counts 5,5,6,3 --format json
```

核心契約：

- 完整 78 張牌；
- 單題 1～24 張且不重複；
- 每個 question identity 重新洗完整牌組；
- 每張正逆位獨立隨機；
- 梅花雙數：A÷8→上卦、B÷8→下卦、(A+B)÷6→動爻，餘 0 視為坤／第 6 爻；
- AI integration 優先 JSON output。

責任分工：

- **本 Playbook**：怎麼問、何時允許 Runtime Draw、怎麼承接／回測、正式紀錄要保存哪些語意、怎麼控制 ChatGPT。
- **Tarot + Plum Randomizer**：RNG、抽牌／起卦實作、CLI/Web 與結果格式化。

## 高頻實戰模式

`QUESTION_DESIGN.md` 包含：

- 主分支 → 分支細節
- 條件世界
- 已發生事件分析
- 承接前占但不重新比較
- 多人物／多對象平行題
- 純時間窗比較
- 現實事件出現後由抽象題切換成具體題

生命週期身份與是否能另抽，仍由 `READING_LIFECYCLE.md` 判定。

## 外部來源與案例

主文件只保存已被整理成穩定、可執行的規則。

- `references/` 保存外部來源 dossier、採用狀態、授權與限制。
- `CASE_STUDIES/` 保存匿名化失敗案例，用來說明「為什麼規則存在」。

兩者預設都是 Cold Context，不因存在就每次載入。

## 本手冊不保存什麼

這是公開方法論 repository，因此不保存：

- 真實姓名與可識別感情／關係細節
- 出生日期、時間與地點等可識別資料
- 健康、性相關私人紀錄
- 私人公司未公開人事、薪資、客戶或專案資訊
- 完整私人占卜日誌／Reading Record／實際 session handoff payload
- secrets / credentials

案例一律匿名化，只保留足以說明方法問題的最低必要結構。

## 與一般塔羅／梅花專案的差異

GitHub 上已有許多抽牌、起卦、牌義、卦義或 AI 解讀專案；本 Repo 專注在另一層：

> **題目設計 / 輸入契約 / Question identity / Reading lifecycle / Reading record / Runtime Draw governance / ChatGPT output governance / Cross-validation / Evidence lineage / Session continuity / Backtest discipline**

也就是不只「怎麼解」，而是讓一個問題從提出、抽牌／起卦、正式保存、承接、程式執行到現實驗證都有可回查的契約。

## 狀態

持續演進中。優先從真實使用中反覆出現的題型、生命週期、Runtime Draw、正式保存與輸出失敗案例反向萃取規則，而不是追求文件數量或堆疊更多象徵資料庫。
