# Astrology｜占星方法契約

Status: **PRODUCTION V1 / EXPLICIT-REQUEST ONLY**

本章是 Astrology 的 production method owner。Astrology v1 將 deterministic calculation 與 interpretation 分層：

```text
explicit Astrology request
→ raw birth data or supplied chart facts
→ deterministic provider / fact acquisition
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

若使用者明確指定 Astrology，不得因 fact acquisition 或 provider unavailable 就偷偷改用 Tarot / Meihua / Liuyao。

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

## 3. Production Natal Provider

Canonical provider：

```text
tools/astrology_provider.py
provider_id = astronomy-engine-natal-v1
provider_version = 1.0.0
```

Provider admission：

```text
ASTROLOGY_PROVIDER_ADMISSION_V1.json
```

Dependency：

```text
astronomy-engine==2.1.19
cosinekitty/astronomy@865d3da7d8112bbc7911238052c6af4aaf877181
MIT
```

Provider 可直接從 raw birth data 產生 natal Fact Bundle。最低輸入：

```text
local_datetime     # ISO local wall time, no embedded offset
timezone_name      # IANA timezone
latitude           # decimal degrees
longitude          # decimal degrees
house_system       # Whole Sign | Placidus
subject_ref
birth_time_certainty = exact | approximate
```

### Timezone / DST

IANA timezone 是 calculation provenance 的一部分。

```text
nonexistent local wall time → fail closed
ambiguous local wall time   → fail closed
fixed offset pretending timezone identity → reject
```

Provider 不自行 geocode place names。若使用者只提供地名，必須先由另一個明確 location-resolution step 取得座標與 timezone；不得讓 provider 隱藏 network/geocoding default。

### Unknown birth time

Raw-birth-data provider v1 不接受：

```text
birth_time_certainty = unknown
```

不得用 local noon 或其他 placeholder 冒充 exact chart。Unknown-time reading 仍可消費另行提供、且符合既有 uncertainty contract 的 structured facts，但 houses / angles 不可假裝可用。

### House systems

Production provider admitted：

```text
Whole Sign
Placidus
```

Placidus 在 production v1 對高緯度採 conservative fail-closed；`|latitude| > 66°` 不產生 Placidus houses。這是 runtime safety boundary，不是宣稱 66° 為唯一理論界線。

### Calculation provenance

Provider 產生：

```text
fact_source = approved_provider
calculation_verification = verified_provider
```

並保存：

- provider id/version；
- Astronomy Engine package/version/source revision；
- calculation reference revision；
- raw local wall time；
- IANA timezone；
- resolved local/UTC time；
- latitude / longitude；
- mean obliquity / sidereal-time / RAMC provenance。

## 4. Astrology Fact Bundle 1.0

Canonical validator：

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

Provider output 必須再通過 runtime gate；provider 自己產生資料不代表可以繞過 validator。

## 5. Reading Modes

目前 interpretation admitted：

```text
natal
transit
```

### Natal

Raw birth data 可以由 `tools/astrology_provider.py` 計算。

可解讀：

- 12-house topics；
- major essential dignity；
- admitted major-aspect claims；
- source-backed methodological / uncertainty claims。

### Transit

Transit interpretation 已 production-admitted，但 **transit event-search provider 尚未 admission**。

所以目前 transit 需要 externally supplied / previously verified deterministic transit facts，例如：

- transit-to-natal aspect；
- exact/applying/separating；
- station；
- ingress；
- repeated passage identity。

不得拿 natal provider 假裝它已擁有 transit-search authority。

目前不 admitted：

```text
synastry
composite
solar return
annual profection
eclipse / lunation prediction
time-lord systems
rectification
```

## 6. House Policy

```text
explicit house system required
→ Whole Sign or Placidus
→ preserve configuration provenance
→ no cross-system averaging
```

若同時比較兩套 house system，建立兩個 configuration views；不得混成一張盤。

Angles 與 house cusps 不做 method-neutral equivalence 假設。Parent-signification、turned houses、planetary joys 不作 project-wide default。

## 7. Essential Dignity Policy

Production v1 admitted major dignity：

```text
domicile
exaltation
detriment
fall
```

- dignity 描述 condition / resources / friction，不是道德好壞；
- 不使用 numeric dignity scoring。

Production v1 不啟用：

```text
triplicity table
terms / bounds
face / decan
peregrine scoring
full reception scoring
```

## 8. Aspect / Orb Policy

Major aspects only：

```text
conjunction  0°   max orb 8°
opposition 180°   max orb 8°
trine      120°   max orb 7°
square      90°   max orb 7°
sextile     60°   max orb 5°
```

`tools/astrology_provider.py` 與 `tools/astrology_runtime.py` 共用同一 production orb authority；provider 不另維護第二套 orb table。

- exact pair 有 admitted claim → 可用；
- 只有 general aspect geometry → 只解 method/general geometry layer；
- 沒有 admitted semantic claim → `unsupported_factor`；
- `REFERENCE_ONLY` pair module 不因能算出 aspect 就自動 production-admit。

## 9. Transit Policy

```text
natal baseline
→ supplied deterministic transit fact
→ exactness / phase / repetition
→ admitted timing claim
→ conditional synthesis
```

Production v1：

- 不自行推導尚未 supplied 的 station window；
- repeated passage 只有 supplied identity 才可形成 sequence；
- inner planets 可作短期 activator；
- timing window ≠ event guarantee。

不得由 transit 宣稱必然：death、pregnancy、medical diagnosis/outcome、accident、legal outcome、investment result、job loss、relationship ending。

## 10. Tradition / Source Admission

Interpretation admission manifest：

```text
ASTROLOGY_PRODUCTION_ADMISSION_V1.json
```

Provider admission manifest：

```text
ASTROLOGY_PROVIDER_ADMISSION_V1.json
```

Research registries 保留歷史 research authority，不因 production admission 回寫狀態。

Admitted interpretation evidence 必須：

1. 來自 production manifest 列出的 registry；
2. source admission 符合 `CLAIM_ELIGIBLE` / `POLICY_PROVENANCE_ELIGIBLE`；
3. `REFERENCE_ONLY` 不可偷偷混入 production claim；
4. conflict group 保留；
5. tradition / historical scope 不消失。

Default synthesis identity：

```text
traditional_western_v1
```

這是 bounded project policy，不代表所有西洋占星傳統皆同意。

## 11. Interpretation Order

### Natal

```text
1. identify user question
2. acquire facts: provider or supplied bundle
3. runtime fact gate
4. state provenance / uncertainty
5. relevant houses / angles
6. relevant major dignity
7. admitted major aspects
8. preserve tradition conflicts
9. minimum-sufficient synthesis
```

### Transit

```text
1. establish natal baseline
2. confirm supplied deterministic transit event
3. exact/applying/separating/repeated status
4. retrieve admitted timing claim
5. conditional timing synthesis
6. separate symbolism from observable reality
```

不要為了「完整」把整張盤所有 factor 一次全部傾倒。

## 12. Uncertainty / Safety

輸出區分：

```text
Chart fact
→ deterministic/provider-supplied

Astrology interpretation
→ source/tradition-backed symbolic claim

Synthesis
→ project/LLM derived explanation
```

若 facts 是 `user_asserted`，必須簡短說明本流程沒有獨立重算。

Astrology 不是 medical / legal / financial / safety decision authority；高風險決策以實際專業 evidence 為主。

## 13. Unsupported-Factor Behavior

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
- 無 deterministic transit event 就自行補日期；
- research detail ≠ production authority。

## 14. Provenance / Recording

Reading Record 至少保存：

```text
method = Astrology
production_method_version = astrology-v1
reading_mode
question identity
fact_bundle identity / source
provider id/version（若適用）
calculation_verification
configuration
birth_time_certainty
used fact refs
used claim refs
conflict refs
unsupported / unavailable factors
interpretation
reality updates
```

真實 birth data / chart data 仍服從 `READING_RECORD.md` storage boundary；不得寫入本公開 Playbook。

## 15. Authority Summary

```text
ASTROLOGY.md
→ production method / interpretation policy owner

tools/astrology_provider.py
→ admitted raw-birth-data natal calculation provider

tools/astrology_runtime.py
→ Fact Bundle validation + deterministic admission gate

ASTROLOGY_PROVIDER_ADMISSION_V1.json
→ provider/dependency/input/calculation admission

ASTROLOGY_PRODUCTION_ADMISSION_V1.json
→ interpretation/research-registry admission

references/astrology/**
→ historical research evidence; not automatically production authority
```

Production status：

```text
Astrology v1                     ADMITTED
activation                       explicit user request only
reading modes                    natal + transit
ordinary auto-routing            NO
built-in natal provider          YES
provider                         astronomy-engine-natal-v1
raw birth data → natal bundle    YES (exact/approximate time)
transit event-search provider    NO
geocoding owned by provider      NO
LLM chart calculation            FORBIDDEN
research auto-promotion          FORBIDDEN
```
