# Astrology Research｜占星研究線

Status: **REFERENCE-ONLY / RESEARCH V1 COMPLETE**

Production owner: [`../../ASTROLOGY.md`](../../ASTROLOGY.md)

Production admission manifest: [`../../ASTROLOGY_PRODUCTION_ADMISSION_V1.json`](../../ASTROLOGY_PRODUCTION_ADMISSION_V1.json)

Production natal-provider admission: [`../../ASTROLOGY_PROVIDER_ADMISSION_V1.json`](../../ASTROLOGY_PROVIDER_ADMISSION_V1.json)

Production natal-provider execution evidence: [`../../ASTROLOGY_NATAL_PROVIDER_ADMISSION_RESULTS.md`](../../ASTROLOGY_NATAL_PROVIDER_ADMISSION_RESULTS.md)

Research maturity review: [`ASTROLOGY_RESEARCH_V1_MATURITY_REVIEW.md`](ASTROLOGY_RESEARCH_V1_MATURITY_REVIEW.md)

Integrated research execution evidence: [`ASTROLOGY_RESEARCH_V1_COMPLETION_EXECUTION_RESULTS.md`](ASTROLOGY_RESEARCH_V1_COMPLETION_EXECUTION_RESULTS.md)

本目錄是 Astrology 的 **historical / ongoing research evidence surface**。Research v1 已完成；Astrology Production v1 另由 root `ASTROLOGY.md` 明確 admission。兩層不得互相覆蓋：

```text
references/astrology/**
→ research evidence / provenance / validators / claim registries
→ remains REFERENCE-ONLY unless boundedly selected by production admission policy

ASTROLOGY.md
+ ASTROLOGY_PRODUCTION_ADMISSION_V1.json
+ ASTROLOGY_PROVIDER_ADMISSION_V1.json
+ tools/astrology_provider.py
+ tools/astrology_runtime.py
→ production-v1 authority
```

Production admission **沒有**把本目錄所有研究來源或 claims 整體改成 production authority，也沒有改寫任何歷史研究結果。

## 1. Scope

本研究線涵蓋：

```text
zodiac / placements
natal chart
transits / transit-to-natal
houses / angles / aspects
retrograde / motion state
structured chart facts
interpretation retrieval / synthesis boundary
tradition/source provenance
```

Production 與 research intent 現在明確分流：

```text
「用占星幫我看／看本命盤／看行運」
→ ASTROLOGY.md

「研究 Astrology 來源／架構／evidence／維護 references」
→ RESEARCH_ROUTING.md
→ references/astrology/README.md
```

Astrology Production v1 仍是 **explicit-request only**；普通未指定方法的占問不會自動選 Astrology。

## 2. Research decomposition

```text
L0 input + provenance
→ L1 astronomical / ephemeris facts
→ L2 deterministic derived chart facts
→ L3 tradition / policy projection
→ L4 sourced interpretation claims
→ L5 bounded synthesis
```

核心研究原則：

1. 天文位置、宮位、相位等 deterministic facts 不由 language model 手算後冒充 engine fact。
2. zodiac、house system、backend、timezone 等設定必須保存 provenance。
3. 出生時間未知時，houses / angles 等 time-sensitive facts fail closed。
4. astronomical facts 與 tradition-specific claims 分層。
5. interpretation 不得反向補造缺失 chart facts。
6. v0.2 claim registries 可宣告 `retrieval_preconditions`，由 retrieval core 與 query requirements OR-compose 後 fail closed。

詳細見 [`EVIDENCE_ARCHITECTURE.md`](EVIDENCE_ARCHITECTURE.md)。

## 3. Calculation / fact evidence

### Production natal provider

Current production provider：

```text
tools/astrology_provider.py
provider_id = astronomy-engine-natal-v1
astronomy-engine==2.1.19
```

Admission/evidence：

- [`../../ASTROLOGY_PROVIDER_ADMISSION_V1.json`](../../ASTROLOGY_PROVIDER_ADMISSION_V1.json)
- [`../../ASTROLOGY_NATAL_PROVIDER_ADMISSION_RESULTS.md`](../../ASTROLOGY_NATAL_PROVIDER_ADMISSION_RESULTS.md)
- [`PRODUCTION_NATAL_PROVIDER_EVIDENCE.md`](PRODUCTION_NATAL_PROVIDER_EVIDENCE.md)

這個 provider 是 root production authority 的一部分，不會把本目錄其他 research probes 一併升格。它目前只 admission natal raw-birth-data calculation；transit event search仍是獨立未 admission scope。

### Historical engine comparison

- [`ENGINE_COMPARISON_RESULTS.md`](ENGINE_COMPARISON_RESULTS.md)
- [`engine_comparison_probe.py`](engine_comparison_probe.py)

Research runtime 曾比較 Swiss Ephemeris API / Moshier fallback 與 Astronomy Engine-family fixtures。這些歷史 probes 本身仍只是 research evidence；目前 production provider 的 authority 來自獨立 provider admission manifest、runtime owner與 production regression，而不是由舊 probe 自動升格。

### Unknown birth-time sensitivity

- [`UNKNOWN_TIME_SENSITIVITY_RESULTS.md`](UNKNOWN_TIME_SENSITIVITY_RESULTS.md)
- [`unknown_time_sensitivity_probe.py`](unknown_time_sensitivity_probe.py)

結果支持 houses / angles 對未知出生時間 fail closed，Moon 亦需 uncertainty-aware handling。Production raw-birth-data provider因此不以 local noon 取代 unknown birth time。

### Transit / station / ingress

- [`TRANSIT_TIMING_VALIDATION_RESULTS.md`](TRANSIT_TIMING_VALIDATION_RESULTS.md)
- [`TRANSIT_NATAL_INGRESS_TIMEZONE_RESULTS.md`](TRANSIT_NATAL_INGRESS_TIMEZONE_RESULTS.md)
- [`TIMEZONE_DST_CONTRACT_DRAFT.md`](TIMEZONE_DST_CONTRACT_DRAFT.md)

Research 已涵蓋 exact-event roots、station、applying/separating、retrograde repeated passages、ingress/re-ingress、timezone/DST ambiguity 等；它們目前**尚未形成 production transit event-search provider**。

### Structured Astrology Fact

- [`STRUCTURED_ASTROLOGY_FACT_SCHEMA_DRAFT.md`](STRUCTURED_ASTROLOGY_FACT_SCHEMA_DRAFT.md)
- [`structured_astrology_fact_example.json`](structured_astrology_fact_example.json)
- [`validate_structured_astrology_fact.py`](validate_structured_astrology_fact.py)
- [`STRUCTURED_ASTROLOGY_FACT_VALIDATION_RESULTS.md`](STRUCTURED_ASTROLOGY_FACT_VALIDATION_RESULTS.md)

Research v1 已有 executable deterministic validator。Production v1 沒有直接把 research schema 改名升格，而是建立獨立 `astrology_fact_bundle@1.0.0` gate，保留版本／authority boundary。

## 4. Interpretation / claim architecture

Research v1 包含：

```text
source-admission architecture
v0.2 typed claim registry
tradition taxonomy
query/tradition resolution
source-admission filtering
conflict preservation
provenance bundle
L5 synthesis contract
registry-declared L2/L3 preconditions
```

主要 owners：

- [`INTERPRETATION_SOURCE_ADMISSION_DRAFT.md`](INTERPRETATION_SOURCE_ADMISSION_DRAFT.md)
- [`INTERPRETATION_CLAIM_REGISTRY_SCHEMA_DRAFT.md`](INTERPRETATION_CLAIM_REGISTRY_SCHEMA_DRAFT.md)
- [`validate_interpretation_claim_registry.py`](validate_interpretation_claim_registry.py)
- [`retrieve_interpretation_claims.py`](retrieve_interpretation_claims.py)
- [`TRADITION_TAXONOMY_DRAFT.md`](TRADITION_TAXONOMY_DRAFT.md)

Research validator 繼續禁止 registry 自行宣告 `PRODUCTION_ADMITTED`。Production v1 透過獨立 manifest 做 bounded admission，避免 retroactive mutation。

## 5. Research-v1 knowledge coverage

### Twelve houses

六條 opposing axes 均有 bounded machine-readable research coverage：

```text
1 ↔ 7
2 ↔ 8
3 ↔ 9
4 ↔ 10
5 ↔ 11
6 ↔ 12
```

主要 evidence：

- [`FIRST_SEVENTH_HOUSE_AXIS_EVIDENCE.md`](FIRST_SEVENTH_HOUSE_AXIS_EVIDENCE.md)
- [`FOURTH_TENTH_HOUSE_AXIS_EVIDENCE.md`](FOURTH_TENTH_HOUSE_AXIS_EVIDENCE.md)
- [`REMAINING_HOUSE_AXES_EVIDENCE.md`](REMAINING_HOUSE_AXES_EVIDENCE.md)

### Essential dignity

Research coverage包含 domicile、triplicity、exaltation/fall、terms/bounds、face/decan terminology gap，以及 later detriment/peregrine/reception framing。Production v1 只 bounded-admit major dignity policy；較有 plurality 的 minor dignity tables仍留在 research。

### Planet / aspect families

Research v1 有 Saturn–Moon family 與五個 additional high-value pair exemplars。這些 coverage 是 representative，不是所有 possible pair 的 universal corpus。REFERENCE_ONLY pair-specific wording不因 Production v1 存在就自動升格。

### Transit interpretation

[`TRANSIT_INTERPRETATION_CLAIM_FAMILY_EVIDENCE.md`](TRANSIT_INTERPRETATION_CLAIM_FAMILY_EVIDENCE.md) 與 companion registry要求 supplied facts + explicit timing policy，並排除 high-stakes event certainty。

## 6. Research-v1 integrated validation

Canonical research completion evidence：

[`ASTROLOGY_RESEARCH_V1_COMPLETION_EXECUTION_RESULTS.md`](ASTROLOGY_RESEARCH_V1_COMPLETION_EXECUTION_RESULTS.md)

GitHub Actions #209：

```text
new research-v1 completion tests   33 / 33 PASS
maintained Astrology tests         87 / 87 PASS
dedicated Astrology total         120 / 120 PASS
whole repository                  150 / 150 PASS
playbook structure                PASS
```

這只證明 tested internal contracts，沒有建立 scientific/predictive validity。

## 7. Current authority boundary

Research v1 的歷史 maturity 結論保存在：

[`ASTROLOGY_RESEARCH_V1_MATURITY_REVIEW.md`](ASTROLOGY_RESEARCH_V1_MATURITY_REVIEW.md)

該文件在當時正確記錄 `production admission: NOT GRANTED`；它是**時間點 evidence**，不應 retroactively 改寫。

目前 current state 已演進為：

```text
research evidence                     REFERENCE-ONLY / RESEARCH V1 COMPLETE
production method owner               ASTROLOGY.md
production admission                  bounded Astrology v1
activation                            explicit request only
ordinary auto-routing                 NO
built-in natal ephemeris provider     YES
natal provider                        astronomy-engine-natal-v1
raw birth data → natal bundle         YES, exact/approximate time + coordinates + IANA timezone
transit event-search provider         NO
provider-owned geocoding              NO
scientific validity claim             NO
```

Production v1 的 current policy請讀 root `ASTROLOGY.md`；不要從 research result docs 反推 current production state。

## 8. Root integration boundary

Research request：

```text
explicit Astrology research intent
→ RESEARCH_ROUTING.md
→ references/astrology/**
```

Production natal reading：

```text
explicit Astrology reading intent
→ ASTROLOGY.md
→ tools/astrology_provider.py when raw birth data is complete
→ Astrology Fact Bundle
→ Astrology Fact Gate
```

Production transit reading：

```text
explicit Astrology transit intent
→ ASTROLOGY.md
→ requires supplied / separately verified transit facts
→ current natal provider does not search transit events
```

Ordinary unspecified divination：

```text
→ METHOD_ROUTING.md ordinary Fast Path
→ Tarot / Meihua / Liuyao
```

目前沒有 canonical Astrology × Tarot / Meihua / Liuyao cross-validation semantics。Palmistry仍是獨立 research line，也不因 Astrology admission而取得任何 production promotion。
