# Liuyao｜六爻方法契約

本章是 **六爻（Liuyao / 六爻納甲）** 在本 Playbook 中的 method-specific authority。

本章不實作 RNG，也不自行維護完整排盤程式：

- stochastic 三錢起卦 → `masini1491/divination-casting-randomizer/randomizer.py`
- deterministic 排盤／納甲 → 必須由可驗證的 Liuyao engine 建立 Structured Method Fact
- 題目與方法選擇 → `METHOD_ROUTING.md`
- Runtime Cast governance → `RUNTIME_DRAW.md`
- 新題／承接／補占 → `READING_LIFECYCLE.md`
- 最終輸出 → `CHATGPT_OUTPUT.md`

目前優先採用的外部 deterministic engine reference 是 `kentang2017/ichingshifa`；採用範圍、license 與不採用項目見 `references/ichingshifa.md`。外部 reference 不因被採用就成為本 Playbook 的 policy authority。

核心原則：

> **Randomizer 決定六爻原始 6/7/8/9；deterministic engine 決定盤；Playbook 決定題目責任與解讀治理。**

> **Language model 不得手算後冒充 deterministic Liuyao engine output。**

## Section Router

- **判斷這題是否該用六爻** → §1～2
- **固定六爻 Input Contract** → §3
- **Runtime 三錢起卦** → §4 + `RUNTIME_DRAW.md`
- **建立本卦／變卦／納甲等 Structured Method Fact** → §5
- **正式解讀順序** → §6～8
- **engine unavailable / partial fact** → §9
- **保存與 provenance** → §10

## 1. Judgment Responsibility｜六爻主要回答什麼

六爻優先處理**單一、具體、可在現實中驗證結果的事件**，尤其當問題核心是：

- 這件事會不會成立／完成；
- 某個明確合作、申請、交易、邀約、回覆、交付是否落地；
- 事情卡在哪一個角色、條件或環節；
- 哪個因素是主要助力／阻力；
- 在已固定事件 identity 後，較具體的應期／時間訊號；
- 主客、世應、用神與動變關係能形成有責任邊界的事件判斷。

快速提示：

> **「這一件具體事情到底成不成、卡在哪、何時應」 → Liuyao 優先。**

六爻不是因為題目重要就自動取得優先權；它的優勢是把**一個明確事件**固定成可追蹤的 judgment node。

## 2. 與 Tarot / Meihua 的責任邊界

### 優先 Tarot，而不是 Liuyao

若主要問題是：

- 某人的主觀感受、心理狀態、互動傾向；
- 多人物／多方案相對比較；
- 選項適配度；
- 想把不同因素拆成獨立牌位比較。

例如：

```text
她現在怎麼評估我？
→ Tarot
```

### 優先 Meihua，而不是 Liuyao

若主要問題是：

- 事件目前如何演變；
- 結構／體用／主客如何變；
- 關鍵轉折在哪；
- 想看主卦 → 互卦 → 變卦的過程，而不是先裁決一個 completion outcome。

例如：

```text
這段合作接下來會怎麼發展？
→ Meihua
```

### 優先 Liuyao

若題目已有清楚 completion rule：

```text
截至月底前，雙方是否會就價格與工作範圍達成一致並正式開始有償合作？
→ Liuyao
```

關係題也一樣：

```text
她怎麼想我？
→ Tarot

這段關係接下來怎麼演變？
→ Meihua

她是否會在本週五以前主動傳訊息給我？
→ Liuyao
```

## 3. Liuyao Input Contract｜起卦前先固定

六爻至少固定：

```text
question
subject
judgment_function
horizon
completion_rule
context_facts
exclusions
casting_source
cast_method
line_order
```

若由 Runtime Cast 起卦，另外保存：

```text
raw_lines: [6|7|8|9] × 6
line_order: bottom-to-top
cast_timestamp
runtime provenance
```

若完整納甲／月日旺衰／六神等解讀需要時間基準，**cast timestamp 應使用同一次起卦實際時間**；不得看到結果後另挑較有利時間排盤。

題目必須先有單一主要 completion function。若同一句同時問：

```text
會不會成功 + 為什麼 + 何時 + 我該怎麼做
```

先固定 primary judgment；其他層只有在同一盤可以合法承擔且不混淆責任時才作 secondary analysis，否則拆成後續 judgment node。

## 4. Canonical Three-Coin Cast｜三錢法 Raw Cast Fact

本 Playbook 預設的 AI Runtime 六爻起卦方式是 `divination-casting-randomizer` 的 canonical three-coin cast：

```text
每爻 3 枚獨立公平二元抽樣
陰 = 2
陽 = 3

6 = 老陰，動
7 = 少陽，靜
8 = 少陰，靜
9 = 老陽，動

共六爻，由初爻至上爻（bottom-to-top）
```

CLI：

```text
python randomizer.py liuyao --method coins --format json
```

Raw Cast Fact 至少保留：

- 每爻 position；
- 每爻三枚 coin values／faces；
- 6/7/8/9 line value；
- yin / yang；
- changing / static；
- line order；
- Runtime source／version／timestamp。

**原始 6/7/8/9 一旦固定，不因後續 engine、解讀或喜好而修改。**

若使用者自行提供六爻 6/7/8/9，直接使用既有 Cast Fact；不得因 Runtime default 而重起。

## 5. Structured Method Fact Gate｜Raw Cast ≠ 完整六爻盤

六個 6/7/8/9 只代表 **Raw Cast Fact**。正式六爻納甲解讀前，應由 deterministic engine 建立 **Structured Method Fact**。

最低應能建立：

```text
raw_lines
ben_gua            # 本卦
changed_lines      # 動爻
zhi_gua            # 之卦／變卦
```

若本題要使用完整納甲判斷，還應由 engine 建立可驗證欄位，例如：

```text
najia              # 納甲干支
five_elements      # 五行
six_relatives      # 六親
shi_ying           # 世應
six_spirits        # 六神／六獸
fu_shen            # 伏神（若適用）
calendar_context   # 月建、日辰、旬空等本題實際使用的時間條件
engine_provenance
```

初始 preferred reference：

```text
kentang2017/ichingshifa
```

其公開 API 支援將六位 `6/7/8/9` 字串作手動 line input，例如 `mget_bookgua_details('789789')`；也提供納甲相關能力。具體採用狀態見 `references/ichingshifa.md`。

### Authority boundary

```text
Divination Casting Randomizer
→ raw stochastic cast authority

Liuyao deterministic engine
→ structured chart/calculation authority

LIUYAO.md
→ judgment responsibility + interpretation governance
```

不得把外部 engine 自己的隨機起卦拿來覆蓋 Randomizer 已固定的 Raw Cast Fact。

## 6. Interpretation Gate｜先定用神責任，再看吉凶

正式納甲解讀前，先依**原題的 judgment function**固定本題主要觀察對象／用神 responsibility；不要看到哪一個六親旺、哪個動爻漂亮後，才反過來挑最有利的用神。

至少先回答：

```text
Primary target / 用神 responsibility: <本題主要代表什麼>
Secondary role(s): <只有原題真的需要才設定>
```

若一題無法在結果出現前清楚說明「主要觀察哪個事件角色」，代表題目可能仍太混合，先回 `QUESTION_DESIGN.md`／`INPUT_CONTRACT.md` 修題。

本 Playbook 不把一張完整六爻盤當成可以無限制回答所有延伸問題的資料庫。**同一 Cast Fact 有固定 question identity。**

## 7. 建議解讀順序

在有足夠 Structured Method Fact 時，採固定方向，避免挑訊號：

```text
1. 重述原題與 completion rule
2. 確認 primary target / 用神 responsibility
3. 看世應／主客位置與本題角色
4. 看月日等時間條件下的旺衰／可作用程度
5. 看動爻與其作用方向
6. 看變爻／之卦是否支持、改變或阻斷 primary outcome
7. 看空破、合沖、生剋、伏神等只有本題需要且 engine 已可靠提供的訊號
8. 最後才形成 outcome / obstacle / timing judgment
```

不是每題都必須把所有術語印給使用者；內部判斷可以完整，使用者輸出只保留與原題相關的 evidence path。

## 8. Outcome / Obstacle / Timing 要分層

六爻常同時提供多種信號，但最終輸出仍要分清：

- **Outcome**：原 `completion_rule` 是否受支持；
- **Obstacle / Cause**：哪個角色／條件阻礙或促成；
- **Timing**：只有在盤面與方法規則有可辨識應期時才提出。

不得把「某用神旺」直接等同「事件必然完成」，也不得把某個時間象徵偽裝成精確保證日期。

若 timing evidence 只能支持區間／相對節點，就保持該精度，不自行補到某日某時。

## 9. Engine / Structured Fact 不可用時

若 Raw Cast 已成功，但 deterministic engine 不可取得、執行失敗，或所需 Structured Method Fact 缺失：

- Raw Cast Fact 仍然有效，不重起；
- 不得由語言模型手算納甲、六親、世應等再冒充 engine output；
- 標記 `LIUYAO STRUCTURED FACT UNAVAILABLE` 或等價 boundary；
- 若使用者只要求不依賴納甲的基礎《周易》卦義分析，可以在**明確降級並取得使用者意圖一致**的前提下處理；不得把降級分析叫做完整六爻納甲解讀；
- 不得因 engine unavailable 就偷偷改成 Tarot／Meihua。若要改方法，必須清楚說明是 fallback，並建立新的 method/cast identity。

核心原則：

> **Cast succeeded ≠ full Liuyao chart succeeded。Preserve raw fact; fail closed at the missing layer。**

## 10. Provenance / Reading Record

正式保存時，至少區分：

```text
casting_source
cast_method
raw_lines
line_order
runtime_tool / runtime version / runtime source commit
cast timestamp

engine_name
engine_source_ref / commit / version（可得時）
structured_fact fields actually used

original interpretation
```

不要把 Randomizer provenance 與 Liuyao engine provenance 合併成一個模糊的 `source`。

若外部 engine source commit 不可確認，保存 `unknown`／`unverified`；不得捏造 SHA。

後續若 engine 更新，只代表新的 calculator revision；**不回頭改寫舊 reading 當時使用的 Raw Cast Fact 或 Structured Method Fact。**

## 11. Pre-Send Check

送出六爻解讀前快速確認：

- [ ] 題目是否是一個清楚、可驗證的事件 identity？
- [ ] completion rule / horizon 是否固定？
- [ ] 6/7/8/9 是否來自實際 Cast Fact，而非模型自行生成？
- [ ] line order 是否為 bottom-to-top 且沒有在轉換時顛倒？
- [ ] 完整納甲判斷所用欄位是否真的來自 deterministic engine？
- [ ] primary target / 用神 responsibility 是否在看到吉凶後才偷換？
- [ ] outcome、obstacle、timing 是否分層？
- [ ] 是否把象徵支持講成客觀保證？
- [ ] engine unavailable 時是否保留 Raw Cast、停止在正確 boundary，而不是重起／手算冒充？

核心原則：**One concrete event, one fixed cast, deterministic chart facts, then interpretation。**
