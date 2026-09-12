# Astrology Evidence Architecture｜占星證據架構

Status: **REFERENCE-ONLY / DRAFT｜僅供參考／草案**

Reviewed Playbook baseline: `masini1491/ai-divination-playbook@6bd58ea5bb61849c2464f4e485bc4f7917f64862`

本檔只定義 Astrology 研究階段的 evidence/source architecture。它不建立 production method、engine authority、router entry 或 interpretation policy。

## 1. Research objective

目標不是先回答「哪套占星解讀最準」，而是先建立一條可稽核、可失敗關閉的資料鏈：

```text
input / provenance
→ astronomical facts
→ derived chart facts
→ tradition projection
→ interpretation claims
→ synthesized reading
```

每一層都要能回答：

- 這個 fact / claim 從哪裡來？
- 哪些設定會改變它？
- 哪些輸入缺失會使它 unavailable？
- 它是 deterministic fact、tradition-derived fact，還是 interpretation？

## 2. Evidence layers

### L0 — Input / provenance fact

包含：

- event type：natal / transit / transit-to-natal / later candidate types；
- civil date/time；
- timezone / UTC offset / timezone resolution method；
- latitude / longitude；
- birth-time certainty / uncertainty；
- location resolution provenance；
- requested zodiac mode；
- requested house system；
- engine name / version / revision；
- calculation timestamp when relevant。

L0 不包含任何占星解讀。

### L1 — Astronomical fact

由 deterministic astronomy / ephemeris engine 產生，例如：

- geocentric / topocentric coordinates；
- ecliptic longitude / latitude；
- speed / motion direction；
- Sun / Moon / planetary positions；
- lunar phase angle；
- astronomical event times。

候選來源包括 Swiss Ephemeris family 與 Astronomy Engine family。

L1 的 engine claim 不能由 language model 補算或猜測。

### L2 — Derived chart fact

由明確設定與 deterministic derivation 產生，例如：

- tropical sign placement；
- sidereal placement under explicit ayanamsa；
- house cusps / Ascendant / Midheaven；
- house placement；
- aspects and exact angular separation；
- applying / separating where algorithmically defined；
- transit-to-natal aspect；
- ingress / station / exact-aspect event。

L2 必須保存足以重現結果的設定。

### L3 — Tradition-specific projection

這一層開始包含占星 tradition 的選擇，例如：

- rulership scheme；
- dignity scheme；
- sect；
- orb policy；
- aspect inclusion policy；
- house-topic mapping；
- transit weighting / prioritization；
- specific traditional / modern interpretive doctrine。

L3 不應偽裝成純天文事實。

同一 L1 / L2 facts 可以在不同 tradition 下得到不同 L3 projection；差異應保留，而不是強制合併成單一真值。

### L4 — Interpretation claim

例如：

```text
transiting Saturn square natal Venus
→ 某傳統來源如何描述其主題、限制、時間感或關係議題
```

L4 應保留：

- source / tradition；
- claim scope；
- applicable premises；
- uncertainty；
- not-supported extensions。

不能從「有相位」直接跳成無來源的具體現實預測。

### L5 — Synthesized reading

AI 將多個 L2/L3/L4 evidence 做 retrieval / ranking / synthesis 的 user-facing layer。

L5 不可：

- 改寫 L0/L1/L2 raw facts；
- 補造缺失出生時間；
- 把 model intuition 冒充 ephemeris output；
- 把不同 tradition 的衝突藏起來；
- 將象徵性 interpretation 升格成可驗證現實事實。

## 3. Configuration provenance

未來 Structured Astrology Fact 至少應考慮顯式保存：

```text
zodiac_system: tropical | sidereal
ayanamsa: null | lahiri | ...
house_system: placidus | whole_sign | ...
center: geocentric | topocentric
node_type: true | mean | ...
aspect_set: [...]
orb_policy: explicit policy id / values
coordinate_frame / epoch when material
engine: name + exact version/revision
```

任何 engine hidden default 若會 materially 改變結果，都應被提升為 provenance。

## 4. Unknown birth-time contract candidate

第一輪 evidence 支持 fail-closed，而不是「用中午代替後把所有結果當真的」。

候選原則：

```text
known date + unknown birth time
→ date-insensitive or bounded planetary facts may remain available
→ time-sensitive facts explicitly unavailable / uncertain
```

通常需特別警戒：

- Ascendant / MC / IC / DC；
- house cusps；
- house placements；
- fast Moon position when time uncertainty is material；
- angle aspects；
- house-based transit conditions。

若某 engine 使用 local noon 只為 deterministic placeholder，placeholder state 必須保留，且不得升格為 known birth time。

未來需要實測不同 birth-time uncertainty 對 Moon、angles、houses 與 aspect boundary 的 sensitivity，再決定更細的 availability contract。

## 5. Transit evidence architecture

「行運星象」應避免只輸出自然語言敘述。候選事件模型：

```text
TransitEvent
- moving_body
- target_type: transit_body | natal_body | natal_angle | natal_cusp
- target
- aspect / condition
- exact_time
- orb_at_query_time
- applying / separating
- search_window
- zodiac / house / engine configuration
- availability / uncertainty
```

對時間窗研究，可另外保存：

```text
entry_time
exact_time
exit_time
```

但「orb window 如何定義」屬 tradition / policy，不是純天文事實，應與 exact geometry 分層。

## 6. Engine comparison architecture

未來比較引擎時，不應只看「輸出看起來差不多」。最低比較單位應固定相同 input + configuration：

```text
same UTC instant
same coordinates
same center
same zodiac definition
same house system where supported
same node definition
same body set
```

候選比較：

```text
Swiss Ephemeris-based result
vs
Astronomy Engine-based / independent result
```

至少比較：

- planetary longitudes；
- Moon longitude；
- retrograde / speed sign；
- major aspect angular separation；
- angles / house cusps（若兩邊算法可比）；
- exact transit event times。

任何差異都先分類為：

```text
input mismatch
configuration mismatch
algorithm / model difference
implementation defect
expected numerical tolerance
unresolved
```

## 7. Source architecture

來源角色分開：

```text
Astronomy / ephemeris source
→ 支持 L1 calculation

Astrology calculation implementation
→ 支持 L2 derivation / schema ideas

Tradition / interpretive source
→ 支持 L3/L4 claims

AI workflow source
→ 支持 retrieval / synthesis governance
```

禁止用一個 repo 同時無條件取得所有 authority。例如一個 astrology app 能算 planet positions，不代表其 interpretation text 也自動取得 canonical authority。

## 8. License boundary

Source registry 已顯示至少兩種架構：

### Swiss-Ephemeris family

優勢：成熟、占星生態廣、精度與功能豐富。

主要 constraint：AGPL / Professional License boundary 必須在任何實作採用前先解決。

### Permissive astronomy family

以 MIT astronomy engine 加上自有 / 可審計 astrology derivation。

優勢：license 較寬鬆、責任可拆細。

主要 constraint：需要更多自有 validation；不能因 MIT 就假設 astrology-specific derivation 正確。

目前不選邊。

## 9. Privacy boundary

本公開 Repo 不保存可識別個人的出生日期 + 出生時間 + 出生地點組合。

Validation 優先使用：

- fictional fixtures；
- 明確公開且可合法使用的 historical/public examples；
- synthetic timestamps / coordinates。

即使來源 repo 使用名人範例，也不代表本研究需要複製該個資型 fixture。

## 10. Admission gates before production consideration

至少需要：

1. source registry / license discrepancy resolution；
2. engine candidate(s) exact revision pin；
3. reproducible comparison fixtures；
4. timezone / DST / location resolution contract；
5. unknown-time sensitivity evidence；
6. configuration provenance schema；
7. Structured Astrology Fact draft；
8. interpretation-source architecture with tradition separation；
9. failure-mode tests；
10. explicit production-admission decision。

在此之前，Astrology 維持：

**REFERENCE-ONLY / RESEARCH / NOT PRODUCTION-ROUTABLE**
