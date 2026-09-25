# Cross-validation｜跨方法 reconciliation

本章是 production cross-validation / reconciliation 的 canonical owner。目前正式支援兩組 pair：

```text
Tarot × Meihua
Astrology natal × Zi Wei natal baseline
```

其他 method pair 若沒有本檔明確 contract，仍只能保持 distinct readings + derived synthesis，不得宣稱為正式 cross-validation。

本檔只定義**不同方法已各自合法產生結果後，如何分工、比對、保留衝突與 evidence lineage**；不改寫任何 method owner 的 calculation、interpretation admission 或 routing authority。

新題／承接／補占／現實更新／完成／舊占回測等跨方法生命週期，統一以 [`READING_LIFECYCLE.md`](READING_LIFECYCLE.md) 為 authority；ChatGPT 最終呈現格式與信心語言則依 [`CHATGPT_OUTPUT.md`](CHATGPT_OUTPUT.md)。

## 1. 先各自回答，再綜合

任何已 admission 的 pair 都必須先完成各自方法內的判讀，再進 reconciliation。塔羅與梅花不應互相強迫一致；Astrology 與 Zi Wei 亦同。

推薦流程：

1. 先依塔羅原牌位契約完成判讀。
2. 再依梅花易數原起卦契約完成判讀。
3. 最後只整理：一致、互補、衝突、仍未知。

不要在第一套結果尚未獨立完成時，就用第二套系統的結果反向修改第一套解讀。

## 2. 一致不等於「更真」

兩套系統出現同方向訊號，可以提高**象徵上的一致性**，但仍不能取代現實證據，也不能因此自動提升成客觀機率。

兩套系統都支持某方向，只能說：

- 兩套象徵結構方向一致；
- 該方向在這次交叉閱讀中較穩定。

不能直接改寫成「所以一定會發生」。

### 2.1 Evidence Lineage / Independence Guard｜抽得多不等於證據獨立

**Draw count ≠ independent evidence count。** 多次牌面／卦象／不同呈現方式看起來是多份結果，不代表它們形成同等數量的獨立證據。

一般規則：

- 同一 question identity 因不滿意結果、想再確認或只換近義題目而重抽／重卦，本來就不應取得新的方法論權重；若不符合 `READING_LIFECYCLE.md` 的 Follow-up Gate，先判定為不合法重問，而不是把多次結果拿來計票。
- 即使多個 reading 都合法成立，只要它們共享高度相同的 subject、現實前提、判斷功能、來源方法或由同一先前 reading 衍生，仍應保留其 lineage；不要把「結果數量」直接翻成「獨立 corroboration 數量」。
- 塔羅與梅花是兩套不同象徵方法，可以形成 cross-method reconciliation，但它們仍不是現實世界的 empirical evidence；兩套一致不會自動變成客觀機率或現實證明。
- 同一 reading 的 summary、ranking、comparison、再次排版、不同敘述版本只是 derived view，不形成新的 source evidence。
- 若真的存在彼此獨立的現實 observation，例如後續正式通知、實際見面、可驗證時間紀錄，應把這些放回 Reality Update／現實 evidence 層；不要讓象徵結果數量取代現實證據。
- Lineage 無法可靠判定時，寧可標示「象徵結果多次同向，但獨立性未建立」，不要宣稱「多份獨立證據一致」。

核心原則：**同向結果可以描述 symbolic consistency；confidence 不能只靠 draw count 膨脹。**

## 3. 衝突時不要投票

若兩套方法不一致，不採「二比一」、「平均分數」或「哪套比較準」處理。

先檢查：

- 是否其實回答不同層級？
- 是否一個在講啟動、另一個在講完成？
- 是否一個在講人物／心理動態、另一個在講事件結構？
- 是否一個在比較選項、另一個在描述勝出分支後的流程？
- 兩次占卜的 `subject`、`horizon`、`completion_rule` 或現實前提是否一致？
- 題目前提是否在兩次占卜間已因現實事件改變？

若檢查後仍不足以可靠統一，保留 `UNRESOLVED`／「無法可靠整合」，不要為了形成漂亮故事而硬合併。

## 4. 常見互補模式

### 塔羅比較選項，梅花看事件走向

例如：

- 塔羅：A／B／C 哪個較可能
- 梅花：最強分支進入後如何發展

這時兩套系統不是在投同一張票，而是在回答不同 function。

### 塔羅看人物，梅花看時機／結構

例如：

- 塔羅：某人是否適合作為人脈入口
- 梅花：這條人脈線的主客結構、轉折或時機

### 塔羅看時間窗，梅花辨識窗口性質

例如：

- 塔羅：哪個月份／窗口較強
- 梅花：該窗口較像啟動、阻滯、轉折或完成

### 塔羅看主觀動態，梅花看外部變化

例如：

- 塔羅：某人可能呈現的互動反應
- 梅花：事件本身的結構與後續變化

## 5. 交叉驗證前先確認「比較的是同一題嗎」

只有在兩套系統的問題身份可對齊時，才適合把它們放進同一個 cross-validation summary。

至少檢查：

- `subject` 是否一致；
- 事件層級是否一致；
- 時間範圍是否可比較；
- `completion_rule` 是否相同或清楚知道差異；
- 一套是否其實已經是前一套結果之後的新條件分支。

如果其中一套是新的 judgment node，就應把它當**承接／互補**，而不是假裝兩套在回答完全相同問題。新 judgment node 的判斷依 `READING_LIFECYCLE.md`。

## 6. 新現實資訊出現在兩次占卜之間

如果塔羅與梅花之間已出現足以改變前提的現實新資訊，原則上不再做乾淨的「同題交叉驗證」。

較好的處理是：

1. 保留第一套占卜的原契約；
2. 把新現實資訊記為新的 `CONFIRMED FACT`；
3. 重新定義第二套占卜的問題身份；
4. 最後只說明兩者如何形成時間上的前後承接，而不是宣稱它們彼此驗證。

## 7. Astrology natal × Zi Wei natal baseline reconciliation

此 pair 只有在**同一 subject 的 natal baseline**都已依各自 production owner 合法完成時，才取得 canonical reconciliation authority：

```text
Astrology
→ ASTROLOGY.md
→ ASTROLOGY_NATAL.md
→ admitted deterministic facts / claims
→ independent natal reading

Zi Wei
→ ZIWEI.md
→ admitted natal_baseline facts / claims
→ independent natal reading

兩邊都完成
→ 本節 reconciliation
```

### 7.1 Distinct evidence responsibilities

兩套方法不需要把技術語彙翻成彼此的等價物。reconciliation 比較的是**已由各自 method owner 支持的上位 natal themes / question-relevant conclusions**，而不是原始因子名稱。

可比較：

- 同一使用者原題下，兩套 natal reading 是否對某個高階主題呈現相同方向；
- 一套提供的 admitted natal layer 是否補充另一套沒有回答的不同面向；
- 兩套對同一高階主題是否有實質 tension；
- 哪些問題仍因任一側 scope / claim / fact 不足而未知。

不可自行建立：

- Astrology house ↔ Zi Wei palace 的一對一等價表；
- planet / sign / aspect ↔ 主星／宮位／亮度／輔星的一對一映射；
- 「第七宮 = 夫妻宮」等未另行 admission 的 cross-system semantic identity；
- 由兩套方法同向而推導客觀 probability、empirical validity 或較高現實證據等級。

### 7.2 Comparable scope gate

目前 canonical comparable scope 是：

```text
Astrology natal
×
Zi Wei natal_baseline
```

下列不屬於本 contract：

- Astrology transit × Zi Wei natal baseline；
- Astrology dynamic timing × 未 production-admitted 的 Zi Wei dynamic timing；
- Astrology research-only claim × Zi Wei production claim；
- Zi Wei unsupported dynamic / broader contextual layer × Astrology production interpretation。

若使用者同時要求 Astrology transit 與 Zi Wei，目前可以：

1. 保留 Astrology transit 為獨立 dynamic reading；
2. 保留 Zi Wei natal baseline 為獨立 natal reading；
3. 只對各自已回答的不同責任作 bounded derived synthesis；
4. **不得稱為正式 Astrology × Zi Wei cross-validation。**

### 7.3 Reconciliation states

對每個實際被比較的上位主題，只能使用下列狀態：

- `AGREEMENT`：兩套已 admitted readings 對同一高階主題方向相容；
- `COMPLEMENT`：回答的是不同但可共同理解原題的面向，沒有形成同題 corroboration；
- `TENSION`：兩套對同一高階主題存在實質差異，但不足以宣告哪套勝出；
- `UNRESOLVED`：scope、fact、claim、question identity 或 comparability 不足；
- `NOT_COMPARABLE`：層級不同（例如 transit vs natal）或需要未 admission cross-system mapping 才能比較。

`AGREEMENT` 只代表 symbolic / interpretive consistency。不得把兩套方法算成兩票、平均 confidence、提高成客觀機率或現實證明。

### 7.4 Conflict handling

若出現 `TENSION`：

1. 先確認 subject / question scope 相同；
2. 確認 Astrology 使用的是 natal owner，不是 transit／research-only layer；
3. 確認 Zi Wei 只使用 admitted natal Scope-A + 明確啟用的 optional module；
4. 檢查是否其實是 `COMPLEMENT` 或 `NOT_COMPARABLE`；
5. 若仍衝突，保留兩條 source lineage，輸出 `TENSION` / `UNRESOLVED`。

禁止：

- 投票；
- score averaging；
- 以其中一套覆寫另一套；
- 為了消除衝突新增未 admitted cross-system semantic mapping；
- 用一套方法的 unsupported layer由另一套補洞後再宣稱「兩邊一致」。

### 7.5 Astrology × Zi Wei output template

不要求固定逐欄輸出，但最低語義結構應可辨識：

```text
Astrology natal 主結論：
Zi Wei natal 主結論：
可比較的共同主題：
AGREEMENT：
COMPLEMENT：
TENSION / UNRESOLVED：
NOT_COMPARABLE：
仍不能共同推出的事項：
evidence lineage / scope boundary：
```

如果沒有真正可比較的共同主題，不為了完成模板硬產生 `AGREEMENT`。

## 8. 交叉驗證內容模板

以下只是內容欄位參考，不要求每次固定全部輸出；實際呈現依 `CHATGPT_OUTPUT.md`。

```text
塔羅主結論：
梅花主結論：
兩者是否回答同一層級：
一致訊號：
互補訊號：
衝突／不確定：
證據 lineage／是否獨立：
現實驗證點：
```

若兩套系統其實回答不同 function，可直接標示：

```text
塔羅負責：
梅花負責：
共同支持的上位結構：
仍不能由兩者共同推出的事項：
```

核心原則：**Cross-validation 是責任分工後的 reconciliation，不是多一套方法就多一票；沒有 admission 的跨系統映射，不得為了漂亮整合而現場創造。**
