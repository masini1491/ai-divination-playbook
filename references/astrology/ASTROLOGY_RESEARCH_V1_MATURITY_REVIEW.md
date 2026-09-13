# Astrology Research v1 — Maturity Review

Status: **RESEARCH V1 COMPLETE / REFERENCE-ONLY / NOT PRODUCTION-ROUTABLE**

## Executive assessment

Astrology research v1 has reached a coherent **research-complete** state for the architecture and bounded knowledge coverage originally needed to evaluate whether Astrology can be represented safely and deterministically inside this repository.

Research v1 is no longer blocked by missing basic plumbing. The project now has:

```text
source / rights / evidence architecture
→ deterministic L0/L1/L2 fact boundary
→ unknown-time / timezone fail-closed behavior
→ structured fact contract + executable validation
→ typed tradition taxonomy
→ source-admitted L3/L4 claim registries
→ deterministic retrieval
→ conflict / provenance preservation
→ L5 synthesis contract
→ registry-declared L2/L3 retrieval preconditions
→ bounded twelve-house interpretation coverage
→ bounded dignity coverage
→ representative natal/aspect coverage
→ bounded transit interpretation coverage
```

This is sufficient to close **research v1**. It is not sufficient to silently declare production readiness.

## 1. Calculation and provenance maturity

### Established

- ephemeris/astronomy source comparison architecture;
- requested-vs-effective backend provenance;
- tropical/sidereal and other configuration fields represented as provenance responsibilities;
- house system recorded rather than hidden;
- unknown birth time fails closed for houses/angles;
- timezone/DST ambiguity handled explicitly;
- transit-to-natal, station, ingress and repeated-passage identity researched;
- L0/L1/L2 facts kept separate from tradition interpretation.

### Remaining before production

- choose and freeze a production calculation authority / adapter policy;
- define acceptable cross-engine tolerance where production needs it;
- decide required ephemeris assets/backends and fallback behavior;
- freeze production input/location/timezone contract.

These are **production-admission tasks**, not missing research-v1 architecture.

## 2. Structured fact maturity

### Established

- Structured Astrology Fact contract;
- synthetic fixtures;
- executable deterministic validator;
- availability / bounded / ambiguous states;
- provenance and fact-lineage boundaries;
- transit/station/ingress fact classes;
- L3/L4 exclusion from source-neutral facts.

### Remaining before production

- freeze a production schema version;
- establish production engine-adapter mapping and compatibility policy;
- establish upgrade/deprecation rules.

## 3. Tradition and source-admission maturity

### Established

- source roles and admission states;
- licence/storage authority separated from doctrinal authority;
- v0.2 typed tradition contexts;
- historical context and meta perspective separated from doctrine selectors;
- no silent tradition fallback;
- conflicts preserved rather than averaged;
- REFERENCE_ONLY claims require explicit qualified opt-in;
- research validator forbids `PRODUCTION_ADMITTED`.

### Coverage currently demonstrated

- Ptolemaic/Hellenistic claims;
- broad Hellenistic lineage claims;
- early-modern historical context without inventing a doctrine ID;
- contemporary traditional-practitioner framing;
- modern psychological-school routing where separately evidenced;
- history-of-astrology meta context.

### Remaining before production

A production method would have to explicitly decide which tradition(s) are admitted for which reading modes. Research v1 deliberately leaves that choice unresolved.

## 4. Twelve-house interpretation maturity

Research v1 now has bounded machine-readable coverage for all twelve houses through six opposing-axis research families:

```text
1 ↔ 7    self/body/native ↔ marriage/partner/direct other
2 ↔ 8    own resources ↔ inheritance/debt/transferred resources/loss
3 ↔ 9    kin/messages/local movement ↔ religion/knowledge/distant travel
4 ↔ 10   home/roots/land ↔ occupation/rank/public standing
5 ↔ 11   children/pleasure/generation ↔ friends/benefactors/hopes
6 ↔ 12   illness/labor/service ↔ confinement/hidden adversity/isolation
```

### Important unresolved production policies

- whole-sign vs quadrant house choice;
- whether and when angles are equated with specific house cusps;
- turned-house policy;
- planetary-joy production policy;
- parent-signification policy;
- how much modern psychological house language is admitted.

These are explicit decisions, not facts implied by complete twelve-house coverage.

## 5. Essential dignity maturity

### Established research coverage

- domicile/rulership;
- Ptolemaic triplicity/triangle distinction;
- exaltation/depression/fall configuration;
- multiple historical terms/bounds systems;
- explicit term-system policy conflict;
- terminology gap between Ptolemy's `proper face` and later/common decan/face dignity;
- later practitioner framing for detriment, peregrine and reception;
- essential dignity kept separate from accidental strength.

### Remaining before production

Production must choose or constrain:

- dignity tradition/table;
- bounds/terms system;
- triplicity system;
- decan/face table and terminology;
- detriment policy;
- reception mechanics;
- whether any numeric scoring exists.

Research v1 intentionally does not freeze these.

## 6. Planet/aspect interpretation maturity

### Established

- Saturn–Moon bounded family with historical/modern distinctions;
- major aspect geometry separated from pair-specific meanings;
- five additional high-value exact pair exemplars:
  - Sun square Saturn;
  - Venus square Mars;
  - Mars opposition Saturn;
  - Mercury trine Jupiter;
  - Venus square Saturn;
- natal/transit/synastry applicability represented;
- sect/dignity/reception contextualization preserved where supplied;
- pair-specific modern reference meanings remain qualified, not universal doctrine.

### Remaining before production

Coverage is representative, **not exhaustive**. A production method must decide whether it:

1. admits only specifically sourced pair modules;
2. composes unsourced pairs from planet + aspect primitives under a tested synthesis rule; or
3. requires further claim-family expansion before unsupported pairs can be interpreted.

Research v1 does not pretend every possible pair/aspect has equivalent source depth.

## 7. Transit interpretation maturity

### Established

- transit facts must precede interpretation;
- natal topic/promise and transit activation remain separate stages;
- station may be handled as a supplied emphasis/window fact without event certainty;
- repeated retrograde/direct passages can be represented when actually supplied;
- unknown-time angular/house transit claims fail closed;
- exact/applying/separating context is consumed only when supplied;
- high-stakes event certainty is explicitly excluded;
- timing is framed as conditional symbolic windows rather than guarantees.

### Remaining before production

- canonical orb policy;
- station window policy;
- transit prioritization/ranking policy;
- repeated-pass grouping policy;
- treatment of eclipses/lunations/time-lord interactions if production scope includes them;
- user-facing uncertainty language contract.

## 8. Retrieval and synthesis maturity

### Established

Canonical typed research path:

```text
validate query/tradition resolution
→ validate full v0.2 registry
→ apply registry + query L2/L3 preconditions
→ source-admission filtering
→ tradition-safe selection
→ provenance/conflict bundle
→ L5 synthesis contract
```

Registry metadata can now declare:

```json
{
  "retrieval_preconditions": {
    "requires_l2_facts": true,
    "requires_l3_policy": true
  }
}
```

Effective requirements are OR-composed with explicit query requirements. Registries that omit the metadata preserve legacy behavior.

This closes the earlier research gap where callers had to remember all precondition booleans manually.

## 9. Validation maturity

Canonical integrated execution evidence:

`ASTROLOGY_RESEARCH_V1_COMPLETION_EXECUTION_RESULTS.md`

Observed on GitHub Actions #209:

```text
new completion regressions   33 / 33 PASS
maintained Astrology suites  87 / 87 PASS
dedicated Astrology total   120 / 120 PASS
whole repository            150 / 150 PASS
playbook structure          PASS
```

This establishes deterministic contract behavior at the tested feature head. It does not establish external scientific truth.

## 10. What “Research v1 Complete” means

It means:

- there is enough deterministic architecture to calculate/store/route evidence without letting the language model invent missing facts;
- the source-admission/tradition machinery has been exercised by multiple qualitatively different claim families;
- all twelve houses have bounded sourced research coverage;
- dignity, aspects and transit interpretation have representative sourced structures;
- preconditions can be declared by registries and fail closed automatically;
- the architecture has current direct execution evidence.

It does **not** mean:

- every astrological tradition has been exhaustively encoded;
- every planet/aspect combination has a dedicated primary-source dossier;
- every house-system dispute is resolved;
- astrology has been scientifically validated;
- ordinary divination routing may automatically select Astrology;
- any current research source is `PRODUCTION_ADMITTED`.

## 11. Production-admission gate

A future production phase should be a new, explicit decision and should begin with a written production target, not by mutating research registries in place.

Minimum production-admission work should include:

```text
1. define intended user-facing Astrology scope
2. choose calculation authority / backend / tolerance
3. freeze input + timezone/location contract
4. choose house-system policy
5. choose tradition and dignity policies
6. choose aspect/orb/transit policies
7. define unsupported-factor behavior
8. define user-facing uncertainty / high-stakes guardrails
9. establish production runtime + fixtures
10. establish behavioral regressions and rollback boundary
11. explicitly admit selected sources/claims
12. only then consider METHOD_ROUTING integration
```

Research evidence must remain historically traceable; production admission should not rewrite old research records to pretend they were production authority.

## 12. Final research-v1 classification

```text
Astrology architecture:            research-mature
L0/L1/L2 deterministic boundary:   research-mature
unknown-time safety:               research-mature
structured fact validation:        research-mature
typed tradition routing:           research-mature
claim registry/retrieval:          research-mature
12-house knowledge skeleton:       complete for research v1
essential dignity coverage:        sufficient for research v1
aspect coverage:                    representative / intentionally non-exhaustive
transit interpretation contract:   sufficient for research v1
metadata preconditions:             implemented + regression-tested
production policy:                  NOT SELECTED
production admission:               NOT GRANTED
ordinary auto-routing:              NOT ENABLED
scientific validity claim:          NOT MADE
```

**Conclusion: Astrology Research v1 is complete as a research line and should remain `REFERENCE-ONLY / NOT PRODUCTION-ROUTABLE` unless a separate production-admission phase is explicitly authorized.**
