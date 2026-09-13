# Astrology｜占星方法契約

Status: **PRODUCTION V1 / EXPLICIT-REQUEST ONLY**

本章是 Astrology 在本 Playbook 中的 production method owner。

Astrology Production v1 的核心定位是：**對已取得、可追溯的 deterministic chart facts 做來源受控的象徵解讀；不由 language model 自行計算星體位置、宮位、相位或行運事件。**

目前 production scope 刻意收斂：

```text
user explicitly requests Astrology / natal chart / transit
→ obtain or receive Astrology Fact Bundle 1.0
→ deterministic runtime gate
→ admitted research-backed interpretation claims
→ bounded synthesis
→ user-facing uncertainty / high-stakes guardrails
```

普通未指定方法的占問仍由 `METHOD_ROUTING.md` 的 Tarot / Meihua / Liuyao Fast Path 處理；Astrology v1 **不是 ordinary auto-routing candidate**。

---

## Section Router

- 使用者是否真的指定 Astrology → §1
- 缺 chart facts 時怎麼辦 → §2～3
- Production Fact Bundle / runtime authority → §4
- natal / transit 支援範圍 → §5
- house / dignity / aspect / transit policy → §6～9
- tradition / source admission → §10
- interpretation order → §11
- uncertainty / safety → §12
- unsupported factor → §13
- provenance / recording → §14

---

## 1. Production Routing Scope｜只處理明確 Astrology intent

Production v1 只有在使用者明確指定下列意圖時啟用：

```text
占星 / Astrology
本命盤 / natal chart
星盤
行運 / transit
用星盤看……
```

若使用者只是：

```text
幫我占……
她怎麼想？
這件事怎麼發展？
月底前會不會完成？
```

而沒有指定 Astrology，仍走 `METHOD_ROUTING.md` 的 ordinary production routing。

如果使用者明確說「用占星」，不得因缺 calculator 就偷偷改用 Tarot / Meihua / Liuyao；應留在 Astrology Fact Gate，說明缺失 facts。

Research intent 與 production reading 仍要區分：

```text
「研究占星來源／維護 Astrology research」
→ RESEARCH_ROUTING.md → references/astrology/**

「用占星幫我看」
→ ASTROLOGY.md
```

---

## 2. Deterministic Fact Boundary｜模型不得手算星盤

Astrology 的天文與幾何層屬 deterministic facts，包括但不限於：

- planet / luminary longitude；
- sign assignment；
- retrograde / motion state；
- Ascendant / MC / house cusps；
- house placement；
- aspect geometry / orb / applying-separating；
- transit-to-natal exact contact；
- station / ingress / repeated passage。

**Language model 不得自行心算、估算、憑記憶或從生日直接補出上述 facts，然後把它們冒充 deterministic engine output。**

允許的 fact acquisition：

1. approved deterministic provider 的 structured output；
2. 使用者提供的既有 chart/export，逐項視為 user-supplied facts；
3. 已存在且 provenance 完整的 Astrology Fact Bundle / Reading Record。

不允許：

```text
raw birth data
→ language model 手算 planets / houses / aspects
→ 假裝是 verified chart
```

若只有 raw birth data 而本次 session 沒有 approved provider：

```text
FACT ACQUISITION UNAVAILABLE
```

保留 Astrology method identity；不自動換方法。

---

## 3. Calculation Provider Policy｜Production v1 不綁未解 license backend

本 repository 目前**不內建 production ephemeris calculator**。

研究階段使用過 `pyswisseph` / Swiss Ephemeris API，但其 backend、ephemeris asset 與 dual-license boundary 尚不適合作為本 repository 的隱藏 production dependency。因此：

- research probes 不升格為 production runtime；
- `wvanderen/astrology-skill` 的 MIT wrapper 也不因 wrapper permissive license 就消除其 `pyswisseph` dependency boundary；
- future provider 可以是 external process / connector / service / local deterministic tool，但必須另做 explicit provider admission。

Production v1 可以解讀使用者已提供的 structured chart facts；此時必須清楚說明：

> 以下依你提供的星盤資料解讀；我沒有在本次流程中獨立重算其天文位置。

---

## 4. Astrology Fact Bundle 1.0｜Production Runtime Gate

Canonical runtime owner：

```text
tools/astrology_runtime.py
```

Canonical schema：

```text
astrology_fact_bundle@1.0.0
```

最低欄位：

```text
schema_name
schema_version
method
reading_mode
fact_source
calculation_verification
subject_ref
birth_time_certainty
configuration
facts
```

### fact_source

Production v1 支援：

```text
approved_provider
user_supplied_structured_export
existing_verified_record
```

禁止：

```text
model_calculated
memory_inferred
```

### calculation_verification

```text
verified_provider
user_asserted
verified_existing_record
```

`user_asserted` 可解讀，但不得描述成「本系統已驗證天文計算正確」。

### configuration

Production v1：

```text
zodiac_system = tropical
center = geocentric
house_system = Whole Sign | Placidus | null
```

若使用 houses / angles：

- house system 必須明確；
- 目前只 admitted `Whole Sign`、`Placidus`；
- 不做 hidden default。

未知出生時間：

```text
birth_time_certainty = unknown
→ angles unavailable
→ houses unavailable
→ house-dependent claims unavailable
```

---

## 5. Reading Modes｜Production v1

目前 admitted：

```text
natal
transit
```

### Natal

可用 source-admitted factors：

- 12-house topics（只有 reliable house facts 存在時）；
- major essential dignity policy；
- admitted aspect claim families；
- source-backed methodological / uncertainty claims。

### Transit

需先有 natal base，再消費 supplied transit facts：

- transit-to-natal aspect；
- exact/applying/separating state；
- station；
- ingress；
- repeated passage（只有 provider 已提供 identity 時）。

Production v1 不 production-admit：

```text
synastry
composite
solar return
annual profection
eclipse / lunation prediction
time-lord systems
rectification
```

這些 future scopes 必須另行 admission。

---

## 6. House Policy｜宮位政策

Production v1 不宣稱某一 house system 是「唯一正確」。政策是：

```text
explicit house system required
→ Whole Sign or Placidus only
→ preserve provenance
→ no cross-system averaging
```

若同一資料同時給兩套 house system：

- 不把 placements 混成單一 chart；
- 若使用者要比較，建立兩個 configuration views；
- 清楚標示差異來自 policy/configuration，而不是事件本身變動。

Angles 與 house cusps 不做 method-neutral equivalence 假設。

Parent-signification、turned houses、planetary joys 目前不作 project-wide production default。

---

## 7. Essential Dignity Policy｜Production v1

Production v1 只 admitted **major dignity layer**：

```text
domicile
exaltation
detriment
fall
```

規則：

- domicile / detriment 使用 classical visible-planet domicile scheme；
- exaltation / fall 使用 research-admitted Ptolemaic configuration lineage；
- dignity 描述 condition / resources / friction，不是道德好壞；
- 不使用 numeric dignity scoring。

Production v1 **不啟用**：

```text
triplicity table
terms / bounds table
face / decan table
peregrine scoring
full reception scoring
```

原因不是研究不存在，而是這些仍有 table / terminology / policy plurality；future production version 可另行 freeze。

---

## 8. Aspect / Orb Policy｜Production v1

只處理 major aspects：

```text
conjunction  0°   max orb 8°
opposition 180°   max orb 8°
trine      120°   max orb 7°
square      90°   max orb 7°
sextile     60°   max orb 5°
```

Production runtime 只消費已 supplied 的 aspect geometry；不從兩顆星的位置自行重算缺失 aspect。

若 supplied `orb_deg` 超過上述上限：

```text
factor_not_admitted
```

不因文字敘述看起來很像某 aspect 就硬解。

目前 pair-specific production meaning 只允許 manifest 實際 admitted 的 source-backed claims。`REFERENCE_ONLY` pair modules 不因存在於 research registry 就自動升格。

因此：

- 若 exact pair 有 admitted claim → 可用；
- 若只有 general aspect geometry → 只解幾何／方法層，不 invent pair-specific personality meaning；
- 若沒有 admitted semantic claim → 明確說此 factor 目前未 admission。

---

## 9. Transit Policy｜Production v1

核心順序：

```text
natal baseline
→ supplied transit fact
→ exactness / phase / repetition
→ source-admitted timing claim
→ conditional synthesis
```

Production v1：

- 不用 transit 創造 natal chart 沒有的 topic；
- station 只在 provider 已供應 station fact 時作 emphasis；
- 不自行推導 station window；
- repeated retrograde/direct passage 只有已 supplied identity 才可形成 sequence；
- inner planets 可作短期 activator，但不因一個快速 transit 就蓋掉更長期 evidence；
- 不把 transit timing window 寫成事件保證。

高風險事項不得由 transit 宣稱必然：

```text
death
pregnancy
medical diagnosis / illness outcome
accident
legal outcome
investment return / financial loss
job loss
relationship ending
```

---

## 10. Tradition / Source Admission｜哪些研究 claim 可進 Production

Machine-readable admission manifest：

```text
ASTROLOGY_PRODUCTION_ADMISSION_V1.json
```

Production v1 不修改 research registries 的歷史狀態。

Admitted interpretation evidence必須：

1. 來自 manifest 列出的 registry；
2. claim 所有 source refs 都必須具有 `CLAIM_ELIGIBLE` 或 `POLICY_PROVENANCE_ELIGIBLE`；
3. `REFERENCE_ONLY` source 不得單獨或混合成 production claim；
4. conflict group 必須保留；
5. historical / tradition scope 不得消失；
6. project synthesis 只能在 manifest 明確 admission 的 methodological / safety scope 使用。

Production v1 的 default synthesis identity：

```text
traditional_western_v1
```

它不是「所有西洋占星都同意」；而是本 project 明確定義的 bounded production synthesis：

- Hellenistic / Ptolemaic source-backed configuration；
- early-modern / traditional-practitioner house meanings只在其 admitted scope；
- conflict不平均；
- modern psychological wording只有另有 admitted claim才可用。

---

## 11. Interpretation Order｜固定 evidence path

### Natal

```text
1. identify reading mode / user question
2. runtime fact gate
3. list unavailable / bounded facts first
4. establish chart configuration provenance
5. relevant houses / angles（if available）
6. major dignity（only if relevant）
7. admitted major aspects
8. resolve source / tradition conflicts
9. synthesize only the factors needed for the question
```

### Transit

```text
1. establish natal baseline relevant to question
2. identify supplied transit contact/event
3. exact/applying/separating/repeated status
4. retrieve admitted timing claim
5. state window / pressure / opportunity conditionally
6. separate symbolic interpretation from observable reality
```

不要做「整張盤所有 factor 一次全部講完」的資訊傾倒；先依使用者問題做 minimum-sufficient retrieval。

---

## 12. Uncertainty / User-Facing Safety Contract

輸出至少區分：

```text
Chart fact
→ deterministic/provider-supplied data

Astrology interpretation
→ admitted tradition/source-backed symbolic claim

Synthesis
→ project/LLM derived explanation
```

若 `calculation_verification = user_asserted`，應加一句簡短 provenance caveat。

未知出生時間：

- 不講 Ascendant / MC；
- 不講 houses；
- 不以 local-noon placeholder 冒充 exact Moon/angles；
- 使用仍穩定的 supplied planet-to-planet facts。

Astrology 不是 medical / legal / financial / safety decision authority；遇高風險問題，以實際專業 evidence 為主。

---

## 13. Unsupported-Factor Behavior｜不能補造 coverage

如果使用者問的 factor 沒有 Production v1 admission：

```text
unsupported_factor
→ say the factor is outside current admitted scope
→ optionally describe what fact/source would be needed
→ do not fill from model memory
```

尤其禁止：

- 沒有 source-backed planet-in-sign family 就輸出固定人格模板；
- 沒有 admitted exact pair claim 就從 REFERENCE_ONLY module偷渡；
- 沒有 house fact就從 Sun sign 猜 house；
- 沒有 transit exact event就自行補日期；
- research result detailed 就等於 production authority。

---

## 14. Provenance / Recording

如果建立 Reading Record，至少保存：

```text
method = Astrology
production_method_version = astrology-v1
reading_mode
question identity
fact_bundle identity / source
calculation_verification
configuration
birth_time_certainty
used fact refs
used claim refs
conflict refs
unsupported / unavailable factors
interpretation
reality updates（後續）
```

真實 birth data / chart data 仍服從 `READING_RECORD.md` storage boundary；不得因本公開 Playbook 有 write permission 就提交個人星盤。

---

## 15. Authority Summary

```text
ASTROLOGY.md
→ production method / interpretation policy owner

tools/astrology_runtime.py
→ Production Fact Bundle validation + deterministic admission gate

ASTROLOGY_PRODUCTION_ADMISSION_V1.json
→ admitted research registry / claim-source policy

references/astrology/**
→ historical research evidence; not automatically production authority

external calculator/provider
→ chart calculation authority only when separately approved or user-supplied facts are explicitly treated as user assertions
```

Production status：

```text
Astrology v1                 ADMITTED
activation                   explicit user request only
reading modes                natal + transit
ordinary auto-routing        NO
built-in ephemeris provider  NO
LLM chart calculation        FORBIDDEN
research auto-promotion      FORBIDDEN
```
