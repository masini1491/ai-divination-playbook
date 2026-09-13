# Astrology｜占星方法契約

Status: **PRODUCTION V1 / EXPLICIT-REQUEST ONLY**

本章是 Astrology 的 production method owner。Astrology v1 將 input resolution、deterministic calculation、runtime validation、evidence selection / interpretation handoff 與 final-output validation 分層。

Production 支援兩條相容的 composition-only reading path；兩者都必須先取得 admitted `astrology_reading_run@1.0.0`，且都不授權 deterministic runtime 自由理解自然語言：

```text
explicit Astrology request
→ ASTROLOGY_READING_REQUEST_V1.schema.json
→ optional offline place resolution
→ deterministic natal / transit provider
→ Astrology Fact Bundle 1.0
→ tools/astrology_runtime.py gate
→ tools/astrology_orchestrator.py
→ astrology_reading_run@1.0.0
→ [exact-reference path]
   ASTROLOGY_INTERPRETATION_REQUEST_V1.schema.json
   → tools/astrology_interpretation_handoff.py
→ [typed-selector path]
   ASTROLOGY_TYPED_EVIDENCE_SELECTION_REQUEST_V1.schema.json
   → tools/astrology_evidence_selector.py
   → astrology_typed_evidence_selection@1.0.0
   → ASTROLOGY_INTERPRETATION_REQUEST_V1.schema.json
   → tools/astrology_interpretation_handoff.py
→ bounded synthesis under ASTROLOGY.md + CHATGPT_OUTPUT.md
→ ASTROLOGY_OUTPUT_DRAFT_V1.schema.json
→ tools/astrology_output_guard.py
→ astrology_user_facing_output@1.0.0
```

Composition-only production entrypoints：

```text
tools/astrology_reading_pipeline.py        # legacy exact-reference path
tools/astrology_typed_reading_pipeline.py  # typed-selector path
```

Typed-selector path 的 caller（例如 ChatGPT）必須先把使用者問題整理成 explicit typed selectors；production selector **不做 free-text query resolution、不取得 natural-language understanding authority，也不自行決定 astrological meaning**。

普通未指定方法的占問仍走 `METHOD_ROUTING.md` 的 Tarot / Meihua / Liuyao Fast Path；Astrology **不參與 ordinary auto-routing**。

## 1. Routing Scope

Production reading intent：

```text
用占星幫我看
看我的本命盤
看這段行運
```

→ `ASTROLOGY.md`

Research intent：

```text
研究占星來源／engine／house-system／claim registry
```

→ `RESEARCH_ROUTING.md` → `references/astrology/**`

若使用者明確指定 Astrology，不得因 provider unavailable 就偷偷改用 Tarot / Meihua / Liuyao。

## 2. Deterministic Fact Boundary

下列內容屬 deterministic facts，不由 language model 自行心算、估算或憑記憶補造：

- planet / luminary longitude；
- sign assignment；
- motion / retrograde state；
- Ascendant / MC；
- house cusps / house placement；
- aspect geometry / orb；
- transit-to-natal exact contact；
- station / ingress / repeated passage。

禁止：

```text
raw birth data
→ model freehand calculation
→ pretend verified chart
```

允許：

1. admitted deterministic provider output；
2. user-supplied structured chart/export；
3. verified existing Astrology Fact Bundle / Reading Record。

## 3. Input Resolution｜地名解析不是天文 authority

Canonical offline resolver：

```text
tools/astrology_place_resolver.py
resolver_id = geonamescache-city-v1
```

Admission：

```text
ASTROLOGY_PLACE_RESOLVER_ADMISSION_V1.json
```

Dependency：

```text
geonamescache==3.0.2
software: MIT
city dataset origin: GeoNames
GeoNames data: CC-BY-4.0 attribution required
```

用途：

```text
city/locality name
→ latitude
→ longitude
→ IANA timezone
```

規則：

- offline only；不依賴 public geocoding API；
- exact name / alternate-name match；
- 可用 ISO alpha-2 `country_code` disambiguate；
- 同名多地 → fail closed + candidates；
- 不以人口最大者偷偷替使用者決定；
- not found → fail closed；
- 不做 street / postal-code / building-level geocoding。

Resolver output 是 **input-resolution provenance**，不是 astronomical fact，也不保證 GeoNames location accuracy。

## 4. Production Natal Provider

Canonical provider：

```text
tools/astrology_provider.py
provider_id = astronomy-engine-natal-v1
provider_version = 1.0.0
```

Admission：

```text
ASTROLOGY_PROVIDER_ADMISSION_V1.json
```

Dependency：

```text
astronomy-engine==2.1.19
cosinekitty/astronomy@865d3da7d8112bbc7911238052c6af4aaf877181
MIT
```

最低輸入：

```text
local_datetime     # ISO local wall time, no embedded offset
timezone_name      # IANA timezone
latitude
longitude
house_system       # Whole Sign | Placidus
subject_ref
birth_time_certainty = exact | approximate
```

### Timezone / DST

```text
nonexistent local wall time → fail closed
ambiguous local wall time   → fail closed
fixed offset pretending timezone identity → reject
```

### Unknown birth time

Raw-birth-data provider v1 不接受 `birth_time_certainty = unknown`。不得用 local noon 或其他 placeholder 冒充 exact chart。

### House systems

Production admitted：

```text
Whole Sign
Placidus
```

Placidus production v1 對 `|latitude| > 66°` fail closed。這是 conservative runtime boundary，不是唯一理論界線。

### Natal provider provenance

Provider output：

```text
fact_source = approved_provider
calculation_verification = verified_provider
```

並保留 provider/version、Astronomy Engine revision、IANA timezone、resolved UTC、座標與 house configuration。

## 5. Production Transit Provider

Canonical provider：

```text
tools/astrology_transit_provider.py
provider_id = astronomy-engine-transit-v1
provider_version = 1.0.0
```

Admission：

```text
ASTROLOGY_TRANSIT_PROVIDER_ADMISSION_V1.json
```

Input：

```text
admitted natal Astrology Fact Bundle
UTC search interval
moving body / bodies
natal target / targets
major aspect / aspects
```

Production v1 支援：

- exact transit-to-natal major-aspect roots；
- Mercury/Venus/etc. retrograde multiple exact passages；
- station roots；
- tropical zodiac ingress / retrograde return / re-ingress。

Search policy：

```text
canonical event time = UTC
max search span       = 400 days
root tolerance        = 0.5 s
normal scan step      = 3 h
station scan step     = 6 h
```

Retrograde 造成多次 exact roots 時不得合併成一筆；需保留 `passage_index` / `passage_count`。

目前不 admitted：

- unbounded search；
- transit-house search；
- sidereal ingress；
- topocentric transit geometry；
- provider 內部直接做 interpretation。

## 6. Astrology Fact Bundle 1.0

Canonical validator：

```text
tools/astrology_runtime.py
```

Canonical schema：

```text
astrology_fact_bundle@1.0.0
```

Production fact sources：

```text
approved_provider
user_supplied_structured_export
existing_verified_record
```

Forbidden：

```text
model_calculated
memory_inferred
```

Configuration v1：

```text
zodiac_system = tropical
center = geocentric
house_system = Whole Sign | Placidus | null
```

所有 provider output 都必須再過 runtime gate；provider 不可繞過 validator。

## 7. Reading Modes

目前 interpretation admitted：

```text
natal
transit
```

### Natal

Raw birth data 可由 `tools/astrology_provider.py` 計算。若只有 city/locality name，可先由 `tools/astrology_place_resolver.py` 解析；歧義必須解決後才可計算。

可解讀：

- 12-house topics；
- major essential dignity；
- admitted major-aspect claims；
- source-backed methodological / uncertainty claims。

### Transit

Transit 可由 `tools/astrology_transit_provider.py` 從 admitted natal bundle 搜尋 exact events，再由 runtime gate 驗證後解讀。

## 8. House Policy

```text
explicit house system required
→ Whole Sign or Placidus
→ preserve configuration provenance
→ no cross-system averaging
```

若同時比較兩套 house system，建立兩個 configuration views；不得混成一張盤。

Angles 與 house cusps 不做 method-neutral equivalence 假設。Parent-signification、turned houses、planetary joys 不作 project-wide default。

## 9. Essential Dignity Policy

Production v1 admitted major dignity：

```text
domicile
exaltation
detriment
fall
```

- dignity 描述 condition / resources / friction，不是道德好壞；
- 不使用 numeric dignity scoring。

不啟用：triplicity table、terms/bounds、face/decan、peregrine scoring、full reception scoring。

## 10. Aspect / Orb Policy

Major aspects only：

```text
conjunction  0°   max orb 8°
opposition 180°   max orb 8°
trine      120°   max orb 7°
square      90°   max orb 7°
sextile     60°   max orb 5°
```

Natal provider 與 runtime 共用同一 production orb authority。Transit provider 的 **exact event search** 求解 aspect exact roots；interpretation 的 admitted pair meaning 仍由 source/claim policy決定。

- exact pair 有 admitted claim → 可用；
- 只有 general aspect geometry → 只解 method/general geometry layer；
- 沒有 admitted semantic claim → `unsupported_factor`；
- `REFERENCE_ONLY` pair module 不因能算出 aspect 就自動 production-admit。

## 11. Transit Interpretation Policy

```text
natal baseline
→ deterministic transit event search
→ exactness / motion / repetition
→ admitted timing claim
→ conditional synthesis
```

Production v1：

- exact event time 用 UTC 保存；
- local civil time 由 explicit IANA timezone 衍生顯示；
- repeated passage 必須保留 sequence；
- timing window ≠ event guarantee；
- deterministic event geometry ≠ event outcome certainty。

不得由 transit 宣稱必然：death、pregnancy、medical diagnosis/outcome、accident、legal outcome、investment result、job loss、relationship ending。

## 12. Tradition / Source Admission

Interpretation admission：`ASTROLOGY_PRODUCTION_ADMISSION_V1.json`

Calculation/input admissions：

```text
ASTROLOGY_PROVIDER_ADMISSION_V1.json
ASTROLOGY_TRANSIT_PROVIDER_ADMISSION_V1.json
ASTROLOGY_PLACE_RESOLVER_ADMISSION_V1.json
```

Research registries 保留歷史 research authority，不因 production admission 回寫狀態。

Admitted interpretation evidence 必須保留 source admission、tradition/historical scope 與 conflict groups。Default synthesis identity `traditional_western_v1` 是 bounded project policy，不代表所有西洋占星傳統皆同意。

## 13. Interpretation Order

### Natal

```text
1. identify user question
2. resolve city/locality only if needed
3. calculate/admit natal facts
4. runtime fact gate
5. state provenance / uncertainty
6. relevant houses / dignity / aspects
7. preserve tradition conflicts
8. minimum-sufficient synthesis
```

### Transit

```text
1. establish admitted natal baseline
2. fix UTC search window + targets
3. deterministic transit event search
4. runtime fact gate
5. exact/motion/repeated-passage state
6. retrieve admitted timing claim
7. conditional timing synthesis
8. separate symbolism from observable reality
```

不要為了「完整」把整張盤所有 factor 一次全部傾倒。

## 14. Production Evidence Selection / Interpretation Handoff / User-Facing Output

Calculation admission、evidence selection 與 semantic interpretation 必須分離。Production v1 保留兩條相容路徑。

### Exact-reference path

Caller 已有 exact fact / claim references 時，可直接建立 `ASTROLOGY_INTERPRETATION_REQUEST_V1.schema.json`：

```text
astrology_reading_run@1.0.0
→ explicit exact fact_refs / claim_requests
→ tools/astrology_interpretation_handoff.py
→ astrology_interpretation_handoff@1.0.0
→ ChatGPT bounded semantic synthesis
→ astrology_output_draft@1.0.0
→ tools/astrology_output_guard.py
→ astrology_user_facing_output@1.0.0
```

`tools/astrology_reading_pipeline.py` 是這條路徑的 composition-only adapter；不新增 calculation、semantic-selection、final-text 或 Reading Record storage authority。

### Typed-selector path

Caller 可先把自然語言問題整理成 explicit typed selectors，再交給 deterministic selector：

```text
astrology_reading_run@1.0.0
+ astrology_typed_evidence_selection_request@1.0.0
→ tools/astrology_evidence_selector.py
→ astrology_typed_evidence_selection@1.0.0
→ ASTROLOGY_INTERPRETATION_REQUEST_V1.schema.json
→ tools/astrology_interpretation_handoff.py
→ astrology_interpretation_handoff@1.0.0
→ ChatGPT bounded semantic synthesis
→ astrology_output_draft@1.0.0
→ tools/astrology_output_guard.py
→ astrology_user_facing_output@1.0.0
```

Typed request / result contracts：

```text
ASTROLOGY_TYPED_EVIDENCE_SELECTION_REQUEST_V1.schema.json
ASTROLOGY_TYPED_EVIDENCE_SELECTION_V1.schema.json
ASTROLOGY_TYPED_READING_PIPELINE_RUN_V1.schema.json
```

`tools/astrology_evidence_selector.py` 只做 deterministic evidence selection：

- 只接受 explicit typed fact / claim selectors；
- fact selector 可依 object、house、aspect、transit event 等結構欄位匹配 admitted reading-run facts；
- claim selector 只在 admitted production registries / sources 內匹配；
- fact selector 與 claim applicability 必須 deterministic binding；不得只靠 caller 自由指定 selector id 偷渡不相符的 claim；
- zero match、multiple match、fact/claim applicability mismatch、unadmitted registry/source 均 fail closed；
- selected exact refs 仍交由既有 interpretation handoff 重新驗證 source admission / provenance boundary；
- 不做 free-text query resolution；
- 不取得 natural-language understanding、astrological-meaning、source-admission、final-prose authority。

因此 production typed-selector path 的責任分工是：

```text
ChatGPT / caller
→ understand the user question
→ author explicit typed selectors

production deterministic selector
→ resolve those explicit selectors to exact admitted facts / claims
→ fail closed on ambiguity or mismatch
```

`tools/astrology_typed_reading_pipeline.py` 只把 admitted reading run → typed selection → existing handoff → guarded output 串成 composition-only execution path；它不新增 free-text NLU、semantic-selection、final-text 或 Reading Record storage authority。Legacy exact-reference path 必須維持可用。

`references/astrology/**` 中的 query-resolution research contract 仍是 **REFERENCE_ONLY / NOT PRODUCTION-ROUTABLE**；typed-selector admission 不等於把 research free-text query resolver promotion 到 production。

### Shared handoff / output boundaries

`tools/astrology_interpretation_handoff.py` 只做：

- 驗證 selected Fact Bundle refs 確實存在於 admitted reading run；
- 驗證 registry / claim 已由 production manifest bounded-admit；
- 套用 production source policy；
- 保留 source provenance、cautions、conflicts、required disclosures、unsupported factors；
- 不選擇使用者問題的答案，也不撰寫 interpretation prose。

`tools/astrology_output_guard.py` 只做：

- 驗證 draft question identity 與 handoff 相同；
- 驗證所有 fact/claim refs 均在 handoff boundary 內；
- 驗證 closed-world draft contract；
- 要求 `CHATGPT_OUTPUT.md` 的 Pre-Send semantic checks 顯式 attest；
- preserve unsupported factors / required disclosures / conflicts / source provenance；
- 不自動判斷自然語言 interpretation 是否「占星上正確」，也不替 ChatGPT 生成 final prose。

Transit user-facing regression 必須至少證明：

```text
explicit transit request
→ natal baseline
→ bounded deterministic transit search
→ runtime gate
→ selected transit event fact
→ production-admitted interpretation claim or explicit unsupported_factor
→ guarded user-facing output
```

Typed transit path 還必須保留 selector provenance，並從 structured event fields 選出 exact admitted event；caller 不需要預先知道 fact id。

能計算出 transit exact event **不等於** pair-specific semantic meaning 自動 admitted；未 admitted meaning 仍必須 fail closed 或明確列為 unsupported。

## 15. Uncertainty / Safety

輸出區分：

```text
Input-resolution fact
→ place resolver / user-supplied location

Chart / timing fact
→ deterministic provider-supplied

Astrology interpretation
→ source/tradition-backed symbolic claim

Synthesis
→ project/LLM derived explanation
```

若 facts 是 `user_asserted`，必須簡短說明本流程沒有獨立重算。

Astrology 不是 medical / legal / financial / safety decision authority；高風險決策以實際專業 evidence 為主。

## 16. Unsupported-Factor Behavior

```text
unsupported_factor
→ say outside current admitted scope
→ state minimum missing fact/source/provider when useful
→ do not fill from model memory
```

尤其禁止：

- 無 source-backed planet-in-sign family 就輸出固定人格模板；
- 無 admitted pair claim 就從 REFERENCE_ONLY module 偷渡；
- 無 house fact就從 Sun sign 猜 house；
- 超過 provider scope 就自行補算；
- research detail ≠ production authority。

## 17. Provenance / Recording

Reading Record 至少保存：

```text
method = Astrology
production_method_version = astrology-v1
reading_mode
question identity
fact_bundle identity / source
place-resolution provenance（若適用）
provider id/version
calculation_verification
configuration
birth_time_certainty
search window / event refs（transit）
used claim refs
unsupported / unavailable factors
interpretation
reality updates
```

真實 birth data / chart data 仍服從 `READING_RECORD.md` storage boundary；不得寫入本公開 Playbook。

## 18. Authority Summary

```text
ASTROLOGY.md
→ production method / interpretation policy owner

tools/astrology_place_resolver.py
→ offline city/locality input resolution only

tools/astrology_provider.py
→ admitted raw-birth-data natal calculation provider

tools/astrology_transit_provider.py
→ admitted bounded transit event-search provider

tools/astrology_runtime.py
→ Fact Bundle validation + deterministic admission gate

tools/astrology_orchestrator.py
→ reading-request normalization + stage composition only

tools/astrology_evidence_selector.py
→ deterministic typed fact/claim selection only; no free-text NLU or meaning authority

tools/astrology_interpretation_handoff.py
→ admitted fact/claim provenance packaging only

tools/astrology_output_guard.py
→ provenance + Pre-Send draft validation only

tools/astrology_reading_pipeline.py
→ exact-reference production reading composition only

tools/astrology_typed_reading_pipeline.py
→ typed-selector production reading composition only

ASTROLOGY_*_ADMISSION_V1.json
→ bounded production admissions

CHATGPT_OUTPUT.md
→ final output / Pre-Send owner

references/astrology/**
→ historical research evidence; query-resolution research remains non-production unless separately admitted
```

Production status：

```text
Astrology v1                         ADMITTED
activation                           explicit user request only
reading modes                        natal + transit
ordinary auto-routing                NO
offline city/locality resolver       YES
built-in natal provider              YES
transit event-search provider        YES
request orchestration                YES
deterministic typed evidence selector YES
interpretation evidence handoff      YES
user-facing output guard             YES
exact-reference end-to-end pipeline  YES
typed-selector end-to-end pipeline   YES
production free-text query resolver  NO
raw birth data → natal bundle        YES (exact/approximate time)
exact transit event search           YES (bounded ≤400 days)
street/building geocoding            NO
LLM chart/timing calculation         FORBIDDEN
research auto-promotion              FORBIDDEN
```
