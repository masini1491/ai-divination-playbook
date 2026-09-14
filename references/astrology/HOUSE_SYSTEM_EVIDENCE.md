# House-System Evidence｜宮位制歷史與方法證據

Status: **REFERENCE-ONLY / RESEARCH / POST-V1 EXTENSION / NOT PRODUCTION AUTHORITY**

Reviewed Playbook baseline: `masini1491/ai-divination-playbook@0f56ceedd58fbbad443eacd102842699c82eb899`

External evidence reviewed: `2026-09-15`

本檔延續 Astrology Research v1，專門整理 **house-system 的 deterministic identity、歷史證據、方法差異與 historiographic conflict**。它不修改 `ASTROLOGY.md`、不選出「唯一正確」宮位制，也不把研究來源升格成 production authority。

## 1. Scope

本輪研究只回答以下問題：

1. Whole Sign、Equal 與 quadrant/Placidus 在計算 identity 上有什麼不可混同的差異？
2. 現存古代資料對 sign-based places / degree-based / quadrant practice 能支持到什麼程度？
3. Ptolemy 與 later Placidus lineage 的歷史解讀有哪些實質爭議？
4. 這些 evidence 對本 Repo 的 provenance / interpretation boundary 有什麼研究含義？

本檔**不**回答：

- 哪個 house system「比較準」；
- 哪個 system 應成為新的 production default；
- 是否應擴大 Production v1 的 Placidus latitude boundary；
- 哪個古代作者能替現代 production policy 提供唯一 authority；
- astrology 的 scientific / predictive validity。

## 2. Existing repository evidence

現有 research architecture 已把 house system 視為 material configuration provenance，而不是顯示偏好：

```text
L0 configuration
→ explicit house_system
→ L2 cusps / house placement
→ L3/L4 interpretation under explicit tradition/policy
```

相關既有 evidence：

- [`EVIDENCE_ARCHITECTURE.md`](EVIDENCE_ARCHITECTURE.md)：house system 必須保存於 configuration provenance；house cusps / placements 屬 L2 deterministic derived facts。
- [`ASTROLOGY_RESEARCH_V1_MATURITY_REVIEW.md`](ASTROLOGY_RESEARCH_V1_MATURITY_REVIEW.md)：明確保留 whole-sign vs quadrant choice 為未被研究 v1 消除的 policy dispute。
- [`EXTENDED_CHART_E1_DERIVED_AXES_RESULTS.md`](EXTENDED_CHART_E1_DERIVED_AXES_RESULTS.md)：已驗證 angle facts 與 house cusps 必須分離；Whole Sign 下 DSC / IC 不得由 house 7 / house 4 cusp 代替。
- [`PRODUCTION_NATAL_PROVIDER_EVIDENCE.md`](PRODUCTION_NATAL_PROVIDER_EVIDENCE.md)：Production v1 的 Astronomy Engine 不擁有 astrology house-system semantics；Whole Sign 與 bounded Placidus derivation 由 project provider 自己負責。

因此本輪不是重做 calculation provider，而是補足 **house-system history / method evidence**。

## 3. Mechanical identity｜先分清三種不同問題

### 3.1 Whole Sign

研究 identity：

```text
Ascendant degree
→ identifies the rising zodiac sign
→ entire rising sign = house 1
→ subsequent signs = houses 2..12
→ house boundaries = 0° sign boundaries
```

結果：

- exact Ascendant 仍是獨立 angle fact；
- Ascendant 不必等於 house 1 的 0° boundary；
- exact MC 仍是獨立 angle fact；
- exact MC 不必等於 house 10 boundary，也可能落在不同 whole-sign house；
- DSC / IC 同樣不得和 Whole Sign cusp 7 / cusp 4 無條件等同。

這與本 Repo E1 的 deterministic angle/cusp boundary 一致。

### 3.2 Equal House

研究 identity：

```text
exact Ascendant degree = house 1 cusp
→ every following cusp = +30°
```

因此：

```text
Whole Sign != Equal House
```

即使兩者每宮都正好 30°，起點不同：Whole Sign 從 rising sign 的 0° 開始；Equal 從 exact Ascendant degree 開始。

### 3.3 Quadrant systems / Placidus

Quadrant systems 使用 horizon / meridian 所建立的 angular frame，再依各自算法決定 intermediate cusps。不同 quadrant method 不應被壓成同一 calculation identity。

Placidus 的研究 identity可概括為：

```text
local horizon + meridian + diurnal/nocturnal semi-arc timing
→ intermediate house boundaries
```

本 Repo 的 current Production v1 是 **bounded project implementation**；其數值 domain / convergence / latitude fail-closed 規則仍由 production provider owner 決定，不能由本研究文件放寬。

## 4. Evidence cluster A｜sign-based places in surviving ancient material

### Robert Hand, 2007

Robert Hand 的〈Signs as Houses (Places) in Ancient Astrology〉以 `Greek Horoscopes` 與 Oxyrhynchus papyri 等存世 chart material 為核心，提出一個明確 historiographic thesis：大量古代資料較合理地解釋為直接以 zodiacal signs 作為 places，而不是普遍另外計算一套獨立的 twelve-fold quadrant/equal cusps。

其文中另指出，在 `Greek Horoscopes` 的 168 份 literary charts 中，只有 27 份同時給 Ascendant 與 Midheaven/IC，而只有 2 份給 intermediate cusps。這是支持其 thesis 的 material evidence，但「缺少 MC/cusps」如何解釋仍包含歷史推論，不是單靠數量就能變成唯一結論。

Research classification：

```text
surviving-chart data point       material evidence
signs-as-places explanation      scholarly thesis
unique/original-system claim     NOT established by this fact alone
predictive superiority           NOT addressed
```

### Chris Brennan, 2019/2020 transcript

Chris Brennan 對 Hellenistic chart examples 的整理同樣主張：只保存 rising sign、沒有 exact Ascendant / MC 的 chart，在資訊層面只能支持 sign-based whole-sign reconstruction，不能據此重建 Equal 或 quadrant cusps。

其 broader historical synthesis進一步主張 Whole Sign 在許多 Hellenistic literary examples 中占主要位置，同時也承認 later material 中 degree-based / quadrant evidence 增加，而且「這代表後來才發展，或只是 surviving evidence bias」不能簡單視為已解決。

Research implication：

- `Whole Sign widely represented in surviving Hellenistic material` 有相當二手史料支持；
- `Whole Sign was the single original and universally used system` 是更強的 claim，不能由目前 evidence 直接升格；
- surviving-sample inference 必須和 deterministic house-system definition 分開。

## 5. Conflict cluster｜Ptolemy does not settle the dispute cleanly

### Primary textual anchor — *Tetrabiblos* III.10

Ptolemy 在討論 length-of-life / prorogative places 時，描述 horoscope 周圍的一個 zodiacal twelfth-part，並以 horizon、midheaven、sextile/quartile/trine/opposition regions 建立權重。

這段文字有兩個重要限制：

1. 它位於特定的 longevity / prorogation context；
2. 它沒有提供一個可無歧義映射成現代「Whole Sign」或「Placidus」的通用 house-system specification。

因此本研究不允許：

```text
Ptolemy III.10 exists
→ therefore Ptolemy unequivocally teaches Whole Sign
```

也不允許：

```text
Ptolemy III.10 exists
→ therefore modern Placidus is directly and uniquely Ptolemaic
```

### Deborah Houlding’s contrary reading

Deborah Houlding 對 Ptolemy 的解讀明確反對把上述 passage 直接化約為 simple Whole Sign。她強調 Ptolemy 對 horizon / MC / angular power 的處理，以及「places of heaven」與 zodiacal parts 可能是不同 reference frames。

這提供本研究需要保留的 genuine conflict：

```text
Hand / Brennan line
→ substantial sign-based / whole-sign evidence in surviving ancient practice

Houlding line
→ Ptolemy and classical house evidence are more ambiguous;
   simple whole-sign-origin narratives can overstate the case
```

本 Repo 不在本輪裁決這個 historiographic conflict；它應被保存成 source/tradition disagreement，而不是平均成一個模糊 consensus。

## 6. Coexistence / layered-use hypothesis

Brennan 對 Valens 等作者的解讀提出一個具有研究價值、但仍屬 interpretation 的模型：

```text
Whole Sign
→ topical place framework

quadrant / degree-based divisions or exact angles
→ angularity / dynamical-strength or specialized timing framework
```

他也討論 Valens 某些例子中 exact MC/IC 像 floating sensitive points，可能把 10th/4th-house-like topics 帶入其實際落入的 Whole Sign house；later Rhetorius material則顯示更明顯的 Whole Sign + intermediate-cusp coexistence。

這支持的最低結論是：

> 古代 practice 不應先驗地被壓成「一張 chart 只能存在一種 house-derived structure」。

但它**不**授權本 Repo 自動把 Whole Sign topics + Placidus strength 混成 production synthesis。若未來要採 layered policy，必須另有 explicit tradition/policy admission 與 regression。

## 7. Placidus evidence｜mechanics, lineage, and latitude boundary

### Semi-arc mechanics

Michael Wackford 對 Placidus/semi-arc method 的說明把 intermediate boundaries 建立在 local horizon、meridian 與 diurnal/nocturnal semi-arc 的 time division 上。這與 Whole Sign / Equal 的 zodiac-longitude partition identity 明顯不同。

Research conclusion：

```text
Placidus
!= 30° sign partition
!= 30° exact-Asc partition
```

因此不同 house systems 的 cusp/placement facts 不應互相當作等價輸出。

### Historical lineage caution

Wackford 與 Houlding 都指出 Placidus de Titis 並不是最早出現此類 semi-arc method 的人；早於 Placidus 的文獻/工具已有相關方法。然而「這就證明 Ptolemy 本人明確使用後世完整 Placidus system」仍是 historiographic interpretation，而不是無爭議的 primary-source fact。

### High-latitude boundary

部分 practitioner / geometry literature 提出 circumpolar 的 semi-arc 延伸解法，並反對簡單說「Placidus 在極區必然完全不存在」。這與本 Repo Production v1 的 conservative boundary 不衝突，因為兩者 authority 不同：

```text
external theoretical / practitioner proposal
→ REFERENCE-ONLY research evidence

current project Production v1
→ |latitude| > 66° fail closed
→ remains unchanged
```

本研究因此只得出：

> 「高緯度 Placidus」本身存在 definition / implementation dispute；不能把外部理論方案當成理由，無審核地放寬 current production domain。

## 8. Research confidence / conflict matrix

| Claim | Research classification | Reason |
| --- | --- | --- |
| Whole Sign 與 Equal House 是不同 calculation identity | **HIGH** | 起算點可明確形式化 |
| Whole Sign / Equal / Placidus 可改變 L2 cusps / house placements | **HIGH** | deterministic configuration consequence |
| exact ASC/MC/DSC/IC 與 Whole Sign cusps 是不同 fact families | **HIGH** | repo E1 已直接建立此 boundary |
| surviving Hellenistic material 中 sign-based places 很常見 | **MODERATE-HIGH** | Hand + Brennan 提供 material/survey support |
| Whole Sign 是唯一原始、唯一古典、或唯一正確 system | **CONTESTED / NOT ESTABLISHED** | stronger historical/normative claim exceeds evidence |
| Ptolemy 清楚教導 modern Whole Sign | **CONTESTED** | III.10 text/context有多種解讀 |
| Ptolemy 清楚教導 modern Placidus | **CONTESTED** | later lineage attribution ≠ unambiguous primary specification |
| Whole Sign topical + quadrant dynamical layer 是所有古典作者通則 | **CONTESTED / SOURCE-SPECIFIC** | useful synthesis hypothesis, not universal fact |
| Placidus 在高緯度只有一個 universally accepted behavior | **NOT ESTABLISHED** | theoretical/implementation treatments differ |
| 任一 house system 具有較高 scientific / predictive validity | **UNSUPPORTED HERE** | current sources do not establish this |
| production 應自動選某一 house system | **NOT AUTHORIZED** | belongs to production policy, not this dossier |

## 9. Research handling rules derived from this evidence

以下只屬 research evidence-handling implication，不修改 production owner：

1. **`house_system` 必須保留 provenance**：不能只保存最後的 `house_number` 而丟掉 calculation identity。
2. **禁止 Whole Sign / Equal / Placidus 結果互換**：同一 planet 在不同 configuration 下的 house placement 應是不同 view。
3. **angles 與 cusps 分層**：ASC/MC/DSC/IC 的 exact longitude 不應因 house system 改變 identity；其與 house cusp 的 equality 必須由 system-specific geometry 證明。
4. **比較不等於平均**：若比較兩套 system，應產生 parallel configuration views，而不是把 house numbers 混合成一個 consensus fact。
5. **歷史 doctrine claims 要帶 source/conflict metadata**：尤其是 `Ptolemy → house system`、`Valens → layered usage`、`original system` 等 claim。
6. **popular / ancient / mathematically elegant != validated**：歷史普及度、年代、幾何構造都不能直接推出 predictive superiority。
7. **research evidence 不改 production boundary**：目前 Production v1 的 admitted house systems、Placidus latitude boundary、unsupported behavior仍由 root production owners決定。

## 10. Source ledger

### Primary / historical text

**Claudius Ptolemy, *Tetrabiblos*, Book III §10**  
Robbins translation mirrored by LacusCurtius / University of Chicago.  
URL: <https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Ptolemy/Tetrabiblos/3B*.html>

Role:

- primary textual anchor for Ptolemy’s prorogative-place wording;
- demonstrates why modern house-system identification from this passage requires interpretation.

Not authority for:

- choosing current production house system;
- claiming modern Placidus or Whole Sign is unambiguously specified there.

### Scholarly / historiographic secondary source

**Robert Hand, “Signs as Houses (Places) in Ancient Astrology,” *Culture and Cosmos* 11 (2007), 135–162.**  
URL: <https://www.cultureandcosmos.org/pdfs/11/11_Hand_Signs_as_Houses_Vol11.pdf>

Role:

- chart-corpus-based signs-as-places thesis;
- distinction between Equal House and sign-based places;
- surviving-chart statistics and ancient/medieval context.

Limitation:

- historical thesis, not scientific validation of astrology;
- stronger claims about universal/original practice require conflict-aware treatment.

### Contemporary historical synthesis

**Chris Brennan, “Origins of the House Division Debate in Ancient Astrology,” The Astrology Podcast, episode 227 transcript.**  
URL: <https://theastrologypodcast.com/transcripts/ep-227-transcript-origins-of-the-house-division-debate-in-ancient-astrology/>

Role:

- survey/synthesis of surviving Hellenistic examples;
- explicit Whole Sign / Equal / quadrant distinction;
- evidence for coexistence/layered-use interpretation.

Limitation:

- practitioner-historian synthesis; individual historical conclusions remain arguments, not method-neutral facts.

### Contrary / conflict-aware historical interpretation

**Deborah Houlding, “The Problems of House Division — Part 5: Ptolemy’s Stance.”**  
URL: <https://www.skyscript.co.uk/houprob5.html>

Companion context:  
<https://www.skyscript.co.uk/houprob4.html>

Role:

- preserves a materially different reading of Ptolemy and classical house evidence;
- useful conflict source against overconfident simple-origin narratives.

Limitation:

- practitioner/historical interpretation; not a scientific validation source.

### Placidus / semi-arc practitioner-technical source

**Michael Wackford, “Placido & the Semi-Arc Method of House Division.”**  
URL: <https://www.skyscript.co.uk/placido.html>

Role:

- mechanical explanation of semi-arc division;
- historical lineage discussion;
- illustrates that polar/high-latitude treatment has competing theoretical proposals.

Limitation:

- practitioner technical argument;
- its polar extension does not override this Repo’s production fail-closed boundary.

## 11. Result

本輪 evidence 支持以下 bounded conclusion：

```text
House-system identity                 RESOLVED as material provenance
Whole Sign vs Equal distinction      RESOLVED mechanically
Whole Sign angle/cusp substitution   REJECTED
Whole Sign vs quadrant history       evidence-rich but historiographically CONTESTED
Ptolemy → one modern system           NOT RESOLVED
Placidus historical lineage          multi-stage / attribution-sensitive
High-latitude Placidus behavior      implementation/theory-sensitive
Predictive superiority               NOT ESTABLISHED
Production policy change             NOT AUTHORIZED
```

因此目前最安全的 research architecture 仍是：

```text
same raw birth input
→ explicit house_system configuration
→ separate deterministic L2 view
→ source/tradition-qualified L3/L4 interpretation
→ never average conflicting house-system outputs into one fact
```

這份 dossier 補上 Research v1 maturity review 當時明確留下的 house-system evidence gap，但保持 historical research record 與 current production authority 分離。
