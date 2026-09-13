# Astrology｜占星方法契約

Status: **PRODUCTION V1 / EXPLICIT-REQUEST ONLY**

本章是 Astrology 的 production method owner。Astrology v1 將 input resolution、deterministic calculation、runtime validation 與 interpretation 分層：

```text
explicit Astrology request
→ raw birth data / supplied chart facts
→ optional offline place resolution
→ deterministic natal / transit provider
→ Astrology Fact Bundle 1.0
→ tools/astrology_runtime.py gate
→ admitted interpretation claims
→ bounded synthesis
```

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

## 14. Uncertainty / Safety

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

## 15. Unsupported-Factor Behavior

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

## 16. Provenance / Recording

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

## 17. Authority Summary

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

ASTROLOGY_*_ADMISSION_V1.json
→ bounded production admissions

references/astrology/**
→ historical research evidence; not automatically production authority
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
raw birth data → natal bundle        YES (exact/approximate time)
exact transit event search           YES (bounded ≤400 days)
street/building geocoding            NO
LLM chart/timing calculation         FORBIDDEN
research auto-promotion              FORBIDDEN
```
