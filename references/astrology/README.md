# Astrology Research｜占星研究線

Status: **REFERENCE-ONLY / RESEARCH V1 COMPLETE**

Production owner: [`../../ASTROLOGY.md`](../../ASTROLOGY.md)

Production admissions:

- [`../../ASTROLOGY_PRODUCTION_ADMISSION_V1.json`](../../ASTROLOGY_PRODUCTION_ADMISSION_V1.json)
- [`../../ASTROLOGY_PROVIDER_ADMISSION_V1.json`](../../ASTROLOGY_PROVIDER_ADMISSION_V1.json)
- [`../../ASTROLOGY_TRANSIT_PROVIDER_ADMISSION_V1.json`](../../ASTROLOGY_TRANSIT_PROVIDER_ADMISSION_V1.json)
- [`../../ASTROLOGY_PLACE_RESOLVER_ADMISSION_V1.json`](../../ASTROLOGY_PLACE_RESOLVER_ADMISSION_V1.json)

Production execution evidence:

- [`../../reports/astrology/ASTROLOGY_NATAL_PROVIDER_ADMISSION_RESULTS.md`](../../reports/astrology/ASTROLOGY_NATAL_PROVIDER_ADMISSION_RESULTS.md)
- [`../../reports/astrology/ASTROLOGY_CALCULATION_COMPLETION_RESULTS.md`](../../reports/astrology/ASTROLOGY_CALCULATION_COMPLETION_RESULTS.md)

Research maturity review: [`ASTROLOGY_RESEARCH_V1_MATURITY_REVIEW.md`](ASTROLOGY_RESEARCH_V1_MATURITY_REVIEW.md)

Integrated research execution evidence: [`ASTROLOGY_RESEARCH_V1_COMPLETION_EXECUTION_RESULTS.md`](ASTROLOGY_RESEARCH_V1_COMPLETION_EXECUTION_RESULTS.md)

Current coordination backlog: [`../../ASTROLOGY_BACKLOG.md`](../../ASTROLOGY_BACKLOG.md)

The backlog is coordination-only. It does not supersede this research owner, `ASTROLOGY.md`, admission manifests or production tools.

本目錄是 Astrology 的 **historical / ongoing research evidence surface**。Research v1 已完成；current production authority 另由 root owners 明確 admission。兩層不得互相覆蓋：

```text
references/astrology/**
→ research evidence / provenance / validators / claim registries
→ remains REFERENCE-ONLY unless boundedly selected by production policy

ASTROLOGY.md
+ ASTROLOGY_PRODUCTION_ADMISSION_V1.json
+ provider/resolver admission manifests
+ tools/astrology_place_resolver.py
+ tools/astrology_provider.py
+ tools/astrology_transit_provider.py
+ tools/astrology_runtime.py
→ production-v1 authority
```

Production admission **沒有**把本目錄所有研究來源或 claims 整體改成 production authority，也沒有改寫歷史 research-result 文件當時的狀態。

## 1. Scope

Research v1 涵蓋：

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

Production 與 research intent 明確分流：

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

1. 天文位置、宮位、相位與行運 exact events 不由 language model 手算後冒充 engine fact。
2. zodiac、house system、engine、timezone、location-resolution provenance 必須可追溯。
3. 出生時間未知時，houses / angles 等 time-sensitive facts fail closed。
4. astronomical facts 與 tradition-specific claims 分層。
5. interpretation 不得反向補造缺失 chart facts。
6. claim registries 的 preconditions 由 retrieval core fail closed。

詳細見 [`EVIDENCE_ARCHITECTURE.md`](EVIDENCE_ARCHITECTURE.md)。

## 3. Calculation / fact evidence

### Production natal provider

```text
tools/astrology_provider.py
provider_id = astronomy-engine-natal-v1
astronomy-engine==2.1.19
```

Admission/evidence：

- [`../../ASTROLOGY_PROVIDER_ADMISSION_V1.json`](../../ASTROLOGY_PROVIDER_ADMISSION_V1.json)
- [`../../reports/astrology/ASTROLOGY_NATAL_PROVIDER_ADMISSION_RESULTS.md`](../../reports/astrology/ASTROLOGY_NATAL_PROVIDER_ADMISSION_RESULTS.md)
- [`PRODUCTION_NATAL_PROVIDER_EVIDENCE.md`](PRODUCTION_NATAL_PROVIDER_EVIDENCE.md)

### Production offline place resolver

```text
tools/astrology_place_resolver.py
resolver_id = geonamescache-city-v1
geonamescache==3.0.2
```

它只處理 city/locality name → coordinates + IANA timezone，並在同名多地時 fail closed；不是 astronomical authority。

### Production transit provider

```text
tools/astrology_transit_provider.py
provider_id = astronomy-engine-transit-v1
```

Bounded production scope：

- transit-to-natal exact major aspects；
- station roots；
- tropical ingress / retrograde return / re-ingress；
- retrograde multiple-passage identity；
- UTC canonical timing；
- search span ≤ 400 days。

Admission/evidence：

- [`../../ASTROLOGY_TRANSIT_PROVIDER_ADMISSION_V1.json`](../../ASTROLOGY_TRANSIT_PROVIDER_ADMISSION_V1.json)
- [`../../reports/astrology/ASTROLOGY_CALCULATION_COMPLETION_RESULTS.md`](../../reports/astrology/ASTROLOGY_CALCULATION_COMPLETION_RESULTS.md)

### Extended-object compact ephemeris research

Current provider-neutral feasibility work remains REFERENCE-ONLY:

- [`CHATGPT_ONLY_EXTENDED_EPHEMERIS_FEASIBILITY.md`](CHATGPT_ONLY_EXTENDED_EPHEMERIS_FEASIBILITY.md) — capability lanes and ChatGPT-only runtime constraints.
- [`ASTROLOGY_EXP1_SAMPLED_EPHEMERIS_FEASIBILITY.md`](ASTROLOGY_EXP1_SAMPLED_EPHEMERIS_FEASIBILITY.md) — AST-P1-010 measured sampled/Hermite candidate result.
- [`astrology_exp1_sampled_ephemeris_feasibility.json`](astrology_exp1_sampled_ephemeris_feasibility.json) — machine-readable metrics and frozen feasibility gates.

AST-P1-010 found **no passing 10/20/40-day sampled/Hermite variant** under its prospectively frozen engineering gate. This is negative research evidence, not a production admission and not evidence that every bundled-ephemeris representation is infeasible.

### Black Moon Lilith research

- Mean / AST-P1-020: [report](ASTROLOGY_EXP2_MEAN_LILITH_PARITY.md), [metrics](astrology_exp2_mean_lilith_iers2003_parity.json).
- Osculating / AST-P1-030: [report](ASTROLOGY_EXP3_OSCULATING_LILITH_STATE_VECTOR.md), [metrics](astrology_exp3_osculating_lilith_state_vector.json).

Both are REFERENCE-ONLY; production admission remains separate.

### Historical engine/timing research

- [`ENGINE_COMPARISON_RESULTS.md`](ENGINE_COMPARISON_RESULTS.md)
- [`TRANSIT_TIMING_VALIDATION_RESULTS.md`](TRANSIT_TIMING_VALIDATION_RESULTS.md)
- [`TRANSIT_NATAL_INGRESS_TIMEZONE_RESULTS.md`](TRANSIT_NATAL_INGRESS_TIMEZONE_RESULTS.md)
- [`TIMEZONE_DST_CONTRACT_DRAFT.md`](TIMEZONE_DST_CONTRACT_DRAFT.md)

這些歷史 probes 本身仍是 research evidence。Current production provider authority 來自獨立 admission manifests、runtime owners 與 production regressions，不是舊 probe 自動升格。

### Unknown birth-time sensitivity

- [`UNKNOWN_TIME_SENSITIVITY_RESULTS.md`](UNKNOWN_TIME_SENSITIVITY_RESULTS.md)
- [`unknown_time_sensitivity_probe.py`](unknown_time_sensitivity_probe.py)

Production raw-birth-data provider因此不以 local noon 取代 unknown birth time。

### Structured Astrology Fact

- [`STRUCTURED_ASTROLOGY_FACT_SCHEMA_DRAFT.md`](STRUCTURED_ASTROLOGY_FACT_SCHEMA_DRAFT.md)
- [`validate_structured_astrology_fact.py`](validate_structured_astrology_fact.py)
- [`STRUCTURED_ASTROLOGY_FACT_VALIDATION_RESULTS.md`](STRUCTURED_ASTROLOGY_FACT_VALIDATION_RESULTS.md)

Production v1 沒有把 research schema retroactively 改名升格，而是使用獨立 `astrology_fact_bundle@1.0.0` gate。

## 4. Interpretation / claim architecture

Research v1 包含 source admission、v0.2 typed claim registry、tradition taxonomy、query/tradition resolution、conflict preservation、provenance bundle、L5 synthesis contract 與 registry-declared preconditions。

主要 owners：

- [`INTERPRETATION_SOURCE_ADMISSION_DRAFT.md`](INTERPRETATION_SOURCE_ADMISSION_DRAFT.md)
- [`INTERPRETATION_CLAIM_REGISTRY_SCHEMA_DRAFT.md`](INTERPRETATION_CLAIM_REGISTRY_SCHEMA_DRAFT.md)
- [`validate_interpretation_claim_registry.py`](validate_interpretation_claim_registry.py)
- [`retrieve_interpretation_claims.py`](retrieve_interpretation_claims.py)
- [`TRADITION_TAXONOMY_DRAFT.md`](TRADITION_TAXONOMY_DRAFT.md)

Research validator 繼續禁止 registry 自行宣告 `PRODUCTION_ADMITTED`；Production v1 透過獨立 manifest bounded-admit。

## 5. Research-v1 knowledge coverage

12-house opposing axes `1↔7 / 2↔8 / 3↔9 / 4↔10 / 5↔11 / 6↔12` 已有 bounded research coverage。

Essential dignity research涵蓋 domicile、triplicity、exaltation/fall、terms/bounds、face/decan terminology gap，以及 later detriment/peregrine/reception framing；Production v1 只 bounded-admit major dignity policy。

Planet/aspect research包含 Saturn–Moon family 與 additional exemplars；REFERENCE_ONLY pair-specific wording不因 deterministic geometry可計算就自動升格。

Transit interpretation research要求 deterministic facts + explicit timing policy，並排除 high-stakes event certainty。

## 6. Historical integrated validation

Research completion evidence：[`ASTROLOGY_RESEARCH_V1_COMPLETION_EXECUTION_RESULTS.md`](ASTROLOGY_RESEARCH_V1_COMPLETION_EXECUTION_RESULTS.md)

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

歷史 maturity 結論保存在 [`ASTROLOGY_RESEARCH_V1_MATURITY_REVIEW.md`](ASTROLOGY_RESEARCH_V1_MATURITY_REVIEW.md)。該文件當時記錄 `production admission: NOT GRANTED` 是正確的時間點 evidence，不 retroactively 改寫。

Current state：

```text
research evidence                     REFERENCE-ONLY / RESEARCH V1 COMPLETE
production method owner               ASTROLOGY.md
production admission                  bounded Astrology v1
activation                            explicit request only
ordinary auto-routing                 NO
offline city/locality resolver        YES
natal provider                        astronomy-engine-natal-v1
raw birth data → natal bundle         YES, exact/approximate time
transit event-search provider         astronomy-engine-transit-v1
exact transit search                  YES, bounded ≤400 days
street/building geocoding             NO
scientific validity claim             NO
```

## 8. Root integration boundary

Production natal：

```text
explicit Astrology reading intent
→ ASTROLOGY.md
→ optional offline place resolver
→ tools/astrology_provider.py
→ Astrology Fact Bundle
→ tools/astrology_runtime.py
```

Production transit：

```text
admitted natal bundle
→ tools/astrology_transit_provider.py
→ transit Astrology Fact Bundle
→ tools/astrology_runtime.py
→ ASTROLOGY.md
```

Research：

```text
explicit Astrology research intent
→ RESEARCH_ROUTING.md
→ references/astrology/**
```

Ordinary unspecified divination：

```text
→ METHOD_ROUTING.md ordinary Fast Path
→ Tarot / Meihua / Liuyao
```

目前沒有 canonical Astrology × Tarot / Meihua / Liuyao cross-validation semantics。Palmistry仍是獨立 research line，也不因 Astrology admission而取得任何 production promotion。
