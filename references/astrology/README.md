# Astrology Research｜占星研究線

Status: **REFERENCE-ONLY / RESEARCH V1 COMPLETE / NOT PRODUCTION-ROUTABLE**

Current maturity review: [`ASTROLOGY_RESEARCH_V1_MATURITY_REVIEW.md`](ASTROLOGY_RESEARCH_V1_MATURITY_REVIEW.md)

Canonical integrated execution evidence: [`ASTROLOGY_RESEARCH_V1_COMPLETION_EXECUTION_RESULTS.md`](ASTROLOGY_RESEARCH_V1_COMPLETION_EXECUTION_RESULTS.md)

本目錄建立 Astrology（星座／本命星盤／行運星象）的 research surface。它整理外部來源、計算／資料／解讀責任邊界、evidence architecture 與 bounded interpretation registries，**不建立 production Astrology method capability，也不加入目前正式 `METHOD_ROUTING.md` 的 ordinary auto-routing 候選**。

Root `RESEARCH_ROUTING.md` 可以在使用者**明確指定 Astrology research intent** 時導向本目錄；這是 discoverability integration，不是 production admission。

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

「星座」在此不是獨立 stochastic method；它優先被視為 Astrology chart facts 的簡化投影，例如 Sun sign / Moon sign / Ascendant。完整本命盤與行運需要更完整的時間、地點、計算設定與 provenance。

目前仍不納入 production：

- 不新增 `ASTROLOGY.md` canonical production method owner；
- 不加入 `METHOD_ROUTING.md` ordinary auto-selection；
- 不建立 Astrology cross-validation semantics；
- 不宣稱 Astrology 已可由一般占問 router 自動選用；
- 不把外部 repo 的 interpretation corpus 或程式碼直接複製成 canonical rule；
- 不自動將 research source / claim 升成 `PRODUCTION_ADMITTED`。

Root integration 只提供：

```text
RESEARCH_ROUTING.md explicit-intent discovery
PLAYBOOK_INDEX.json research.* pointers
CHAT_INIT.md explicit research-line handoff
```

上述 integration 不改變本目錄的 `REFERENCE-ONLY / RESEARCH / NOT PRODUCTION-ROUTABLE` authority。

## 2. Research decomposition

```text
L0 input + provenance
→ L1 astronomical / ephemeris facts
→ L2 deterministic derived chart facts
→ L3 tradition / policy projection
→ L4 sourced interpretation claims
→ L5 bounded synthesis
```

核心要求：

1. 天文位置、宮位、相位等可 deterministic 計算內容，不由 language model 自由手算後冒充 engine fact。
2. tropical / sidereal、house system、ayanamsa、node type、orb policy 等設定必須成為 provenance，而不是隱藏預設。
3. 出生時間未知時，不把 houses / angles 或其他 time-sensitive facts 當作已知。
4. astronomical fact 與 astrological tradition claim 分層；「程式能算」不等於「解讀主張已被證實」。
5. interpretation 只能消費已建立的 facts 與明確來源，不得反向補造缺失 chart facts。
6. v0.2 registries 可宣告 `retrieval_preconditions`，由 retrieval core 自動與 query requirements OR-compose 後 fail closed。

詳細分層見 [`EVIDENCE_ARCHITECTURE.md`](EVIDENCE_ARCHITECTURE.md)。

## 3. Calculation / fact evidence

### Engine cross-implementation comparison

- [`ENGINE_COMPARISON_RESULTS.md`](ENGINE_COMPARISON_RESULTS.md)
- [`engine_comparison_probe.py`](engine_comparison_probe.py)

第一輪比較使用 `kounkt/tri-horoscope` 的 fictional fixtures 作 Astronomy-Engine-family pinned output，與本地 `pyswisseph 2.10.03` 比較。

重要限制：該 runtime 雖要求 `FLG_SWIEPH`，實際 calculation flags 回報 `FLG_MOSEPH`，因此只能稱為：

```text
Swiss Ephemeris API / Moshier fallback
vs
Astronomy Engine family
```

不能稱為 `.se1` / DE441 Swiss comparison。

### Unknown birth-time sensitivity

- [`UNKNOWN_TIME_SENSITIVITY_RESULTS.md`](UNKNOWN_TIME_SENSITIVITY_RESULTS.md)
- [`unknown_time_sensitivity_probe.py`](unknown_time_sensitivity_probe.py)

Full-day sensitivity evidence supports fail-closed treatment for houses / angles and uncertainty-aware Moon handling when birth time is unknown.

### Transit / station / exact-aspect timing

- [`TRANSIT_TIMING_VALIDATION_RESULTS.md`](TRANSIT_TIMING_VALIDATION_RESULTS.md)
- [`transit_timing_validation_probe.py`](transit_timing_validation_probe.py)

Research covers exact-event roots, station speed zero-crossings, applying/separating geometry, orb entry/exact/exit, repeated passages and angular-wrap failure modes. Station timestamps remain bounded research evidence, not production cross-engine certification.

### Transit-to-natal / ingress / timezone-DST

- [`TRANSIT_NATAL_INGRESS_TIMEZONE_RESULTS.md`](TRANSIT_NATAL_INGRESS_TIMEZONE_RESULTS.md)
- [`TIMEZONE_DST_CONTRACT_DRAFT.md`](TIMEZONE_DST_CONTRACT_DRAFT.md)
- [`transit_natal_timezone_probe.py`](transit_natal_timezone_probe.py)

Research covers transit→fixed natal targets, retrograde multi-passage identity, ingress/re-ingress, UTC vs IANA-local rendering, DST ambiguous/nonexistent wall time and fixed-offset vs timezone identity.

### Structured Astrology Fact contract + executable validation

- [`STRUCTURED_ASTROLOGY_FACT_SCHEMA_DRAFT.md`](STRUCTURED_ASTROLOGY_FACT_SCHEMA_DRAFT.md)
- [`structured_astrology_fact_example.json`](structured_astrology_fact_example.json)
- [`validate_structured_astrology_fact.py`](validate_structured_astrology_fact.py)
- [`STRUCTURED_ASTROLOGY_FACT_VALIDATION_RESULTS.md`](STRUCTURED_ASTROLOGY_FACT_VALIDATION_RESULTS.md)

Research v1 now has an executable deterministic validator in addition to the Markdown contract and synthetic fixtures. The fact layer preserves availability state, provenance, requested/effective backend, unknown-time boundaries, event identity and L3/L4 exclusion. It is still a research contract, not a frozen production schema.

## 4. Interpretation / claim architecture

Research v1 includes:

```text
interpretation-source admission contract
v0.2 typed claim registry
tradition taxonomy
query/tradition resolution
source-admission filtering
conflict preservation
provenance bundle
L5 synthesis contract
registry-declared L2/L3 preconditions
```

Key files include:

- [`INTERPRETATION_SOURCE_ADMISSION_DRAFT.md`](INTERPRETATION_SOURCE_ADMISSION_DRAFT.md)
- [`INTERPRETATION_CLAIM_REGISTRY_SCHEMA_DRAFT.md`](INTERPRETATION_CLAIM_REGISTRY_SCHEMA_DRAFT.md)
- [`validate_interpretation_claim_registry.py`](validate_interpretation_claim_registry.py)
- [`retrieve_interpretation_claims.py`](retrieve_interpretation_claims.py)
- [`TRADITION_TAXONOMY_DRAFT.md`](TRADITION_TAXONOMY_DRAFT.md)

The research validator explicitly forbids production admission; `REFERENCE_ONLY` material cannot self-promote into an unqualified supported claim.

## 5. Research-v1 knowledge coverage

### Twelve houses

Bounded machine-readable research coverage now spans all six opposing axes:

```text
1 ↔ 7
2 ↔ 8
3 ↔ 9
4 ↔ 10
5 ↔ 11
6 ↔ 12
```

Evidence/registries include:

- [`FIRST_SEVENTH_HOUSE_AXIS_EVIDENCE.md`](FIRST_SEVENTH_HOUSE_AXIS_EVIDENCE.md)
- [`FOURTH_TENTH_HOUSE_AXIS_EVIDENCE.md`](FOURTH_TENTH_HOUSE_AXIS_EVIDENCE.md)
- [`REMAINING_HOUSE_AXES_EVIDENCE.md`](REMAINING_HOUSE_AXES_EVIDENCE.md)

Complete house-topic coverage does **not** choose a production house system, angle/cusp equivalence, turned-house policy or parent-signification rule.

### Essential dignity

Research coverage now distinguishes:

```text
domicile / rulership
triplicity / triangles
exaltation / depression / fall
terms / bounds
face terminology
later detriment / peregrine / reception framing
essential dignity != accidental strength
```

See:

- [`DOMICILE_CLAIM_FAMILY_EVIDENCE.md`](DOMICILE_CLAIM_FAMILY_EVIDENCE.md)
- [`ESSENTIAL_DIGNITY_EXPANSION_EVIDENCE.md`](ESSENTIAL_DIGNITY_EXPANSION_EVIDENCE.md)

Research v1 intentionally does not flatten competing term systems or silently equate Ptolemy's `proper face` terminology with later decan/face dignity tables.

### Planet / aspect families

Research v1 includes the established Saturn–Moon family plus five additional high-value exact pair exemplars:

```text
Sun square Saturn
Venus square Mars
Mars opposition Saturn
Mercury trine Jupiter
Venus square Saturn
```

See:

- [`SATURN_MOON_ASPECT_CLAIM_FAMILY_EVIDENCE.md`](SATURN_MOON_ASPECT_CLAIM_FAMILY_EVIDENCE.md)
- [`HIGH_VALUE_PLANET_ASPECTS_EVIDENCE.md`](HIGH_VALUE_PLANET_ASPECTS_EVIDENCE.md)

This is representative, intentionally non-exhaustive coverage. Pair-specific modern reference language remains qualified `REFERENCE_ONLY` unless separately admitted.

### Transit interpretation

- [`TRANSIT_INTERPRETATION_CLAIM_FAMILY_EVIDENCE.md`](TRANSIT_INTERPRETATION_CLAIM_FAMILY_EVIDENCE.md)
- [`transit_interpretation_claim_family_registry.json`](transit_interpretation_claim_family_registry.json)

Interpretation consumes supplied L2 facts and explicit L3 timing policy. Station/repeated-pass language remains conditional; high-stakes event certainty is explicitly excluded.

## 6. Research-v1 integrated validation

Canonical completion evidence:

[`ASTROLOGY_RESEARCH_V1_COMPLETION_EXECUTION_RESULTS.md`](ASTROLOGY_RESEARCH_V1_COMPLETION_EXECUTION_RESULTS.md)

GitHub Actions #209 directly executed the integrated Astrology suites at the recorded feature head:

```text
new research-v1 completion tests   33 / 33 PASS
maintained Astrology tests         87 / 87 PASS
dedicated Astrology total         120 / 120 PASS
whole repository                  150 / 150 PASS
playbook structure                PASS
```

These results establish internal research-contract behavior, not scientific validity.

## 7. Research v1 completion boundary

Detailed assessment:

[`ASTROLOGY_RESEARCH_V1_MATURITY_REVIEW.md`](ASTROLOGY_RESEARCH_V1_MATURITY_REVIEW.md)

Current classification:

```text
Astrology architecture:            research-mature
L0/L1/L2 deterministic boundary:   research-mature
unknown-time safety:               research-mature
structured fact validation:        research-mature
typed tradition routing:           research-mature
claim registry/retrieval:          research-mature
12-house knowledge skeleton:       complete for research v1
essential dignity coverage:        sufficient for research v1
aspect coverage:                   representative / intentionally non-exhaustive
transit interpretation contract:   sufficient for research v1
metadata preconditions:            implemented + regression-tested
production policy:                 NOT SELECTED
production admission:              NOT GRANTED
ordinary auto-routing:             NOT ENABLED
scientific validity claim:         NOT MADE
```

## 8. Production admission remains separate

Research completion does not infer production readiness. A future production phase must explicitly choose and validate, among other things:

```text
user-facing Astrology scope
calculation authority / backend / tolerance
input / timezone / location contract
house-system policy
tradition + dignity-table policy
aspect / orb / transit policies
unsupported-factor behavior
user-facing uncertainty / high-stakes guardrails
production runtime + fixtures
behavioral regressions / rollback boundary
explicit source/claim admission
METHOD_ROUTING integration only after admission
```

Historical research records should remain traceable and must not be retroactively rewritten as production authority.

## 9. Root integration boundary

Astrology is discoverable through root research routing when the user explicitly asks for Astrology research:

```text
explicit Astrology intent
→ research routing
→ references/astrology/**
→ REFERENCE-ONLY result
```

It is **not**:

```text
ordinary unspecified divination
→ auto-select Astrology
```

and it is **not**:

```text
research regression passes
→ production admission
```

Palmistry remains a separate research line; root discoverability does not create automatic cross-validation or mutual promotion.
