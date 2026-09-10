# Liuyao｜六爻方法契約

本章是 **六爻（Liuyao / 六爻納甲）** 在本 Playbook 中的 method-specific authority。

本章不實作 RNG；deterministic calculation 與 interpretation authority 明確分層：

- stochastic 三錢起卦 → `masini1491/divination-casting-randomizer/randomizer.py`
- deterministic 結構排盤 → `tools/liuyao_engine.py`
- calendar-dependent facts → 只有經可驗證 calendar provider 或已固定外部 facts 才可加入
- 題目與方法選擇 → `METHOD_ROUTING.md`
- Runtime Cast governance → `RUNTIME_DRAW.md`
- 新題／承接／補占 → `READING_LIFECYCLE.md`
- 最終輸出 → `CHATGPT_OUTPUT.md`

外部 repositories（包含 `yaomancy/liuyao-engine`、`bopo/najia`、`AdrienSterling/yigram-najia-rules`、`kentang2017/ichingshifa`）只作 reference / differential oracle；不因被採用就成為本 Playbook 的 policy authority 或 Runtime dependency。

核心原則：

> **Randomizer 決定六爻原始 6/7/8/9；deterministic engine 決定可驗證盤面 facts；Playbook 決定題目責任、用神 responsibility 與解讀治理。**

> **Language model 不得手算後冒充 deterministic Liuyao engine output。**

## Section Router

- **判斷這題是否該用六爻** → §1～2
- **固定六爻 Input Contract** → §3
- **Runtime 三錢起卦** → §4 + `RUNTIME_DRAW.md`
- **建立本卦／變卦／納甲等 Structured Method Fact** → §5
- **正式解讀順序** → §6～8
- **engine / calendar fact unavailable** → §9
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

### 5A. Canonical lightweight structural engine

本 Repository 的 production structural owner 是：

```text
tools/liuyao_engine.py
```

它是 zero-external-dependency deterministic core；輸入已固定的六爻 `6/7/8/9`，輸出目前已驗證的 structural facts：

```text
raw_lines
moving_positions
ben_gua / zhi_gua
64-gua identity
upper / lower trigram
palace / palace element / generation type
najia
five elements
six relatives
shi / ying
fu_shen
```

若 caller 已提供可靠 calendar facts，engine 亦可附加：

```text
six_spirits      # 需要 day_gan
xunkong flag     # 需要 xunkong
month-break flag # 需要 month_branch
day-clash flag   # 需要 day_branch
```

**這個 structural engine 不負責從 timestamp 自行推算節氣月建／日柱／旬空，也沒有 interpretation authority 或 yongshen-selection authority。**

### 5B. Calendar Fact Gate

完整六爻若要使用月建、日辰、旬空、六神與依賴這些資料的旺衰／應期，calendar facts 必須另外取得並驗證。

目前允許：

```text
A. 已由可信 deterministic calendar provider 產生並保留 provenance 的 facts
B. 使用者／既有 Reading Record 已提供、且本題明確固定的 verified calendar facts
```

目前不允許：

```text
Language model 心算／猜測干支、節氣、旬空
把 Gregorian 月份直接當月建
看到卦後才換時間基準
engine 沒算出來卻把欄位補成完整盤
```

Calendar provider 尚未通過 production validation 時，structural facts 仍有效；只在 calendar-dependent layer fail closed。

### 5C. Differential evidence

Lightweight structural core 的固定表／規則應以 external references 作 differential oracle，而不是 Runtime dependency。現有 reference set 包含：

```text
AdrienSterling/yigram-najia-rules
yaomancy/liuyao-engine
bopo/najia
```

已加入的 differential tests 至少覆蓋：

- 8 卦納甲地支 sequence；
- 八宮五行；
- 全 64 卦 palace / generation / 世應；
- 六親五行生剋 semantics。

Reference 自己標示 draft／unaudited 的資料不得因 test parity 就升格為唯一真理；重要 facts 仍應維持多來源或傳統規則交叉驗證。

### Authority boundary

```text
Divination Casting Randomizer
→ raw stochastic cast authority

Lightweight Liuyao engine
→ verified structural chart facts

Calendar provider
→ verified calendar-dependent facts only

LIUYAO.md
→ judgment responsibility + yongshen responsibility + interpretation governance
```

不得把 engine 自己的隨機起卦拿來覆蓋 Randomizer 已固定的 Raw Cast Fact；也不得讓 engine 的 category mapping 取代 Playbook 的 question contract。

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
4. 看月日等時間條件下的旺衰／可作用程度（只有 calendar facts 已驗證時）
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
- **Timing**：只有在盤面與方法規則有可辨識應期，且所需 calendar facts 已驗證時才提出。

不得把「某用神旺」直接等同「事件必然完成」，也不得把某個時間象徵偽裝成精確保證日期。

若 timing evidence 只能支持區間／相對節點，就保持該精度，不自行補到某日某時。

## 9. Engine / Structured Fact 不可用時

分層 fail closed：

```text
Raw Cast 成功 + structural engine 成功 + calendar unavailable
→ 保留 Raw + structural facts
→ 標記 calendar-dependent facts unavailable
→ 不使用月建／日辰／旬空／六神／旺衰／精細應期作證據

Raw Cast 成功 + structural engine unavailable
→ 保留 Raw Cast
→ LIUYAO STRUCTURED FACT UNAVAILABLE
→ 不手算冒充 engine
```

共同規則：

- Raw Cast Fact 仍然有效，不重起；
- 不得由語言模型手算納甲、六親、世應等再冒充 engine output；
- 若使用者只要求不依賴完整納甲的基礎《周易》卦義分析，可以在**明確降級並取得使用者意圖一致**的前提下處理；不得把降級分析叫做完整六爻納甲解讀；
- 不得因某 layer unavailable 就偷偷改成 Tarot／Meihua。若要改方法，必須清楚說明是 fallback，並建立新的 method/cast identity。

核心原則：

> **Cast succeeded ≠ every Liuyao layer succeeded。Preserve every verified fact; fail closed only at the missing layer。**

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
engine_version / source commit（可得時）
structured_fact fields actually used

calendar_provider / version / source ref（若使用）
calendar facts actually used

original interpretation
```

不要把 Randomizer provenance、structural engine provenance 與 calendar provenance 合併成一個模糊的 `source`。

後續 engine 更新，只代表新的 calculator revision；**不回頭改寫舊 reading 當時使用的 Raw Cast Fact 或 Structured Method Fact。**

## 11. Pre-Send Check

送出六爻解讀前快速確認：

- [ ] 原題是一個清楚、可驗證的事件 judgment node。
- [ ] Raw Cast 是既有 fact 或由 canonical Runtime 產生，不是模型自創。
- [ ] line order 明確為 bottom-to-top。
- [ ] 本卦／動爻／之卦／納甲等使用到的 structural facts 有 deterministic engine provenance。
- [ ] calendar-dependent evidence 只有在 calendar facts 已驗證時才使用。
- [ ] 用神 responsibility 在看結果前由 question contract 決定，不由 engine category mapping 代替。
- [ ] 沒有因不喜歡結果而重起。
- [ ] 沒有把 engine / calendar 缺失藏起來。
- [ ] outcome、obstacle、timing 沒有混成同一個無法驗證的敘事。
