# Method Routing｜占卜方法選擇

本章只處理一件事：**當使用者尚未指定占卜方法時，ChatGPT 應如何依主要 judgment function 選擇目前已正式支援的方法。**

目前 production-ready routing 支援：

```text
Tarot
Meihua
Liuyao
Tarot + Meihua（只有 distinct responsibilities 真正需要時）
```

本章不負責牌位設計、起卦算法、解讀、補占或交叉驗證細節：

- 題目怎麼問 → `QUESTION_DESIGN.md`
- Tarot-specific → `TAROT.md`
- Meihua-specific → `MEIHUA.md`
- Liuyao-specific → `LIUYAO.md`
- Tarot + Meihua 已存在後怎麼整合 → `CROSS_VALIDATION.md`
- 新題／承接／補占／重占 → `READING_LIFECYCLE.md`
- ChatGPT 自行抽牌／起卦 → `RUNTIME_DRAW.md`

核心原則：

> **先判斷使用者真正想知道的 judgment function，再選方法；不是先選流派，再把問題硬塞進去。**

> **Single-method first。Cross-validation 不是資訊越多越好。**

## Fast Path｜高信心命中就停止 routing

普通題先用這個最小路由：

```text
Psychology / Comparison
→ Tarot

Process / Evolution / Structure
→ Meihua

Outcome / Completion
→ Liuyao
```

具體化：

```text
主要問人物心理、互動、主觀感受、A/B/C 比較
→ Tarot

主要問事情怎麼變、轉折在哪、主客／體用結構
→ Meihua

主要問一件具體、外部可驗證的事情是否在 horizon 內完成／成立
→ Liuyao
```

若只有一個分支高信心命中，**立即選 method，停止讀本檔其餘 sections**；只有出現 collision、ambiguous function、使用者要求多方法或 completion／心理／演化混在同一句時，才繼續讀對應 gate。

## 1. User Method Override｜使用者已指定方法

若使用者已明確指定：

- 「用塔羅」→ 使用 Tarot；
- 「用梅花」→ 使用 Meihua；
- 「用六爻」→ 使用 Liuyao；
- 「兩個都看／交叉看」→ 先進 Cross-validation Responsibility Gate，不預設固定哪兩套。

原則上尊重使用者選擇，不因 ChatGPT 個人偏好自行換方法。

只有當指定方法與問題功能明顯不合、無法依該方法形成乾淨契約，或方法本身在本次 workflow 不可用時，才應簡短指出限制並推薦更合適方法。

若使用者已提供實際牌面／卦象／六爻 Cast Fact，直接依既有方法處理；不得為了「方法更適合」自行重抽、重卦或改系統。

## 2. Function Detection｜先辨識問題功能

方法選擇前，先辨識本題的**主要 judgment function**。

### 優先 Tarot

若主要功能是以下之一，優先使用 Tarot：

- 多選一／多情境的相對比較；
- 不同人物、對象、方案的比較；
- 人物可觀察反應、互動與關係動態；
- 主觀感受、心理／互動層面的象徵分析；
- 阻礙、助力、觸發因素的牌位拆解；
- 選項適配度、決策面向；
- 可被拆成清楚牌位的事件流程；
- 已定義離散時間窗之間的相對比較。

快速提示：

> **哪一個／哪個人／怎麼反應／不同因素怎麼比較 → Tarot 優先。**

### 優先 Meihua

若主要功能是以下之一，優先使用 Meihua：

- 一件事件目前如何變化；
- 主客／自身與外部的結構；
- 體用關係；
- 關鍵轉折、哪裡開始變；
- 主卦 → 互卦 → 變卦的發展結構；
- 近程節奏、事件 checkpoint；
- 問題本身由時間、數字、外應、聲音、物象等觸發，且起卦來源清楚。

快速提示：

> **事情怎麼變／轉折在哪／目前主客結構／何時進入下一階段 → Meihua 優先。**

### 優先 Liuyao

若主要功能是**一個單一、具體、外部可驗證事件的成立／不成立**，優先使用 Liuyao，尤其是：

- 某個合作、交易、申請、邀約、回覆、交付是否會成立；
- 已有明確 completion rule，想看 outcome 支持度；
- 想進一步辨識具體事件卡在哪個角色／條件／環節；
- 在同一事件 identity 下，需要用神、世應、動變等結構處理 outcome / obstacle / timing；
- 問題本身可以自然寫成「截至某 horizon，X 是否完成？」。

快速提示：

> **這一件具體事情到底成不成／卡在哪／何時應 → Liuyao 優先。**

例如：

```text
她現在怎麼評估我？
→ Tarot

這段關係接下來怎麼演變？
→ Meihua

她會不會在本週五以前主動傳訊息給我？
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

## 3. Outcome vs Evolution Gate｜Liuyao 與 Meihua 的核心分界

這是最重要的 tie-breaker：

```text
核心是「會不會完成這件具體事情？」
→ Liuyao

核心是「事情接下來怎麼變？」
→ Meihua
```

同一現實事件可以合法產生不同 judgment node，但不要把兩個功能混成同一題：

```text
Node A：月底前合作是否正式成立？
→ Liuyao

Node B：如果繼續推進，合作關係的結構與轉折怎麼發展？
→ Meihua
```

不要因 Meihua 也能談吉凶／應期，就把明確 completion outcome 永遠留給 Meihua；也不要因 Liuyao 能看動變，就拿它取代所有事件演化題。

## 4. Psychology vs Observable Event Gate｜Liuyao 與 Tarot 的分界

```text
核心是主觀感受／心理／互動品質
→ Tarot

核心是外部可驗證行動是否發生
→ Liuyao
```

例如：

```text
她有沒有想主動找我？
若問內在傾向／心理 → Tarot

她是否會在 7 天內主動傳出一則訊息？
→ Liuyao
```

如果使用者自然語言同時包含心理與行動，先依 completion rule 判斷主要 judgment function；必要時拆成兩個節點，不用一套方法硬包全部。

## 5. Single-Method Sufficiency Gate｜單方法充分性

辨識主要功能後，先問：

> **一套方法是否已能乾淨回答本題主要功能？**

- 若 **是** → 使用單一方法。
- 若 **否** → 才考慮 Cross-validation Responsibility Gate。

不要因為題目重要、資訊很多、使用者焦慮、第一套結果不夠漂亮，或「多一套可能比較準」就自動追加第二套。

**問題同時碰到人物與時間，不代表一定要雙占。** 若其中一層只是附帶資訊，仍以主要 judgment function 決定單一方法。

## 6. Cross-validation Responsibility Gate｜需要第二套方法時

目前已完整定義的 cross-validation owner 是 `CROSS_VALIDATION.md` 的 Tarot × Meihua reconciliation。

Liuyao 納入 routing 後，**不因此自動宣告所有 Liuyao + Tarot／Meihua 組合都已具備 production-ready cross-validation contract**。

若要在同一使用者請求中追加第二套方法，至少必須：

1. 兩套方法承擔不同、可先寫出的 judgment responsibilities；
2. Primary Method 已由主要 judgment function 決定；
3. Secondary Method 不得只是「再確認一次」；
4. 若目前沒有對應 canonical reconciliation contract，應保持為兩個獨立 readings，再作明確標示的 derived synthesis，不假裝已有正式 cross-validation owner。

例如：

```text
Primary Liuyao responsibility:
月底前合作是否正式成立

Secondary Tarot responsibility:
我目前提出條件與對方主觀接受度／互動阻力
```

這可以是兩個 distinct readings，但目前不要稱為已 canonical 化的 `Liuyao + Tarot Cross-validation`。

## 7. Generic / Unspecified Request｜使用者只說「幫我占」

若使用者沒有指定方法，但問題功能已足以判斷，ChatGPT 應直接選擇，不需要每次反問方法。

預設：

- 人物、選項、主觀感受、相對比較 → Tarot；
- 事件演變、主客結構、轉折、節奏 → Meihua；
- 單一具體事件 outcome／completion → Liuyao；
- 只有真正存在兩個 distinct functions 時才考慮第二套方法。

只有在**不同方法會實質改變題目功能，而現有資訊不足以知道使用者真正想問哪一層**時，才做一次最小澄清。

例如：

```text
「幫我看這個合作」
```

無法知道是要看：

```text
對方怎麼想 → Tarot
接下來怎麼發展 → Meihua
月底前會不會正式成立 → Liuyao
```

此時才需要最小澄清。

## 8. Tie-breaker｜同時命中多種方法

依以下順序裁決：

1. 使用者明確指定的方法；
2. 主要 judgment function；
3. 是否有清楚、外部可驗證的 completion rule；
4. 單方法是否已充分；
5. 需要第二套時，是否能在結果出現前寫出不同 responsibility；
6. 沒有 canonical reconciliation contract 時，保持獨立 readings，而不是硬創新的 Both semantics。

### 簡化決策樹

```text
是否主要問人物心理／關係主觀／選項比較？
→ yes: Tarot

否，是否主要問一個明確事件如何演變／轉折？
→ yes: Meihua

否，是否主要問一個具體、可驗證事件是否完成／成立？
→ yes: Liuyao

仍不清楚
→ 最小澄清
```

## 9. Method Selection 與題目設計分離

Method Routing 只決定「用哪套」。選完後才進行正式題目契約：

```text
RAW USER QUESTION
→ FUNCTION DETECTION
→ METHOD ROUTING
→ minimum contract normalization
→ QUESTION_DESIGN only if a design gap remains
→ DRAW / CAST
→ STRUCTURED METHOD FACT（需要時）
→ INTERPRETATION
```

不要先抽牌／起卦，再根據結果反推「其實這題比較適合另一套」。

若題目本身有契約缺陷，才補讀 `INPUT_CONTRACT.md`／`QUESTION_DESIGN.md` relevant sections；**普通清楚的新題不因為是新題就固定全文載入兩份文件。**

## 10. Runtime / Engine Capability 不影響方法選擇

技術 capability 只決定選定方法後能不能執行，不決定本題理論上該用哪個方法。

正確順序：

```text
先選方法
→ 固定題目契約
→ 確認 casting / engine capability
→ 執行或 fail closed
```

尤其 Liuyao：

```text
Randomizer 可起六爻
≠
完整納甲 engine 一定可用
```

若 Liuyao 是最佳方法，但 Structured Method Fact engine 不可用，依 `LIUYAO.md` fail closed 在缺失層；不得只因 Tarot 比較容易執行就偷偷改方法。

## 11. 建議的 Agent-facing 最小輸出

方法選擇通常可以在內部完成，不必每次展示完整 routing reasoning。

若需要向使用者說明：

```text
建議方法：Liuyao
理由：本題有清楚的完成條件與期限，核心是判斷單一具體事件是否成立。
```

或：

```text
建議方法：Meihua
理由：本題核心是事情接下來怎麼演變與在哪裡轉折，不是先裁決一個單一完成結果。
```

不要把方法選擇包裝成「哪一套比較準」；這是**問題功能與方法責任的匹配**。

## 12. Pre-Route Check

送入正式出題／抽牌前，快速確認：

- [ ] 使用者是否已指定方法？
- [ ] 主要 judgment function 是什麼？
- [ ] 是否有清楚的 completion rule / horizon？
- [ ] 這題是在問心理、演化，還是單一 outcome？
- [ ] 一套方法是否已足夠？
- [ ] 若追加第二套，是否能在結果出現前寫出不同 responsibility？
- [ ] 是否已有實際牌面／卦象／Cast Fact，因此不得重新 routing 成另一套？

核心原則：**Psychology/comparison → Tarot; evolution/turning point → Meihua; concrete outcome/completion → Liuyao。**
