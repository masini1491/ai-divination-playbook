# Astrology Production v1 Admission Results

Status: **PRODUCTION ADMISSION EVIDENCE / BOUNDED ASTROLOGY V1**

Baseline:

`masini1491/ai-divination-playbook@d7fdb4b2c4ca6a615e95723166c507acc8b9421f`

Production branch:

`production/astrology-v1-admission-20260913`

Pull request:

`#29 — production: admit bounded Astrology v1`

## 1. Admission decision

Astrology Production v1 is admitted with a bounded authority model:

```text
activation                 explicit user request only
ordinary auto-routing      no
reading modes              natal + transit
built-in ephemeris         no
LLM chart calculation      forbidden
fact runtime               tools/astrology_runtime.py
method owner               ASTROLOGY.md
admission manifest         ASTROLOGY_PRODUCTION_ADMISSION_V1.json
```

This admission does not claim scientific or predictive validity.

## 2. Calculation-provider boundary

Production v1 deliberately does not bundle or silently promote a research ephemeris backend.

Research examined `pyswisseph` / Swiss Ephemeris API behavior and an external MIT wrapper, but the underlying calculation dependency retains licensing/backend-selection considerations. Therefore research probes and wrappers remain evidence/reference surfaces rather than hidden production calculation authority.

Production v1 consumes only a structured `astrology_fact_bundle@1.0.0` whose source is one of:

```text
approved_provider
user_supplied_structured_export
existing_verified_record
```

The runtime rejects:

```text
model_calculated
memory_inferred
```

and requires source/verification pair consistency.

When only raw birth data is available and no admitted deterministic provider is configured:

```text
FACT ACQUISITION UNAVAILABLE
```

The method remains Astrology; it must not silently switch to another divination method or ask the language model to hand-calculate a chart.

## 3. Production policy frozen for v1

### Configuration

```text
zodiac          tropical
center          geocentric
house systems   Whole Sign | Placidus | null
```

House facts require an explicit admitted house system. Unknown birth time forbids production house and angle facts.

### Reading modes

Admitted:

```text
natal
transit
```

Not admitted in v1:

```text
synastry
composite
solar return
annual profection
rectification
eclipse/lunation prediction
time-lord systems
```

### Essential dignity

Production v1 admits the major layer:

```text
domicile
exaltation
detriment
fall
```

Minor/contested tables and scoring remain outside v1:

```text
triplicity tables
terms / bounds
face / decan tables
peregrine scoring
numeric dignity scoring
full reception scoring
```

### Major aspect geometry

```text
conjunction   max 8°
opposition    max 8°
trine         max 7°
square        max 7°
sextile       max 5°
```

The runtime consumes supplied aspect facts and rejects unknown refs, unsupported aspect types and over-policy orbs. It does not calculate missing aspects from planet longitudes.

### Transit

Production interpretation requires supplied transit-to-natal / station / ingress facts. Station windows and repeated-pass sequences are not invented when missing. Timing is conditional and does not guarantee concrete events.

## 4. Research-to-production source boundary

Research registries remain historically `REFERENCE-ONLY`; no registry was rewritten to pretend it had always been production-authoritative.

Production authority is added separately through:

```text
ASTROLOGY.md
ASTROLOGY_PRODUCTION_ADMISSION_V1.json
```

The manifest records admitted registry families and a source policy requiring `CLAIM_ELIGIBLE` / `POLICY_PROVENANCE_ELIGIBLE` evidence for production use. `REFERENCE_ONLY` sources do not self-promote.

The high-value exact-pair registry remains `qualified_only`: its pair-specific modern wording is **not** production-admitted merely because the research module exists. General supplied major-aspect geometry remains usable as a deterministic fact.

Conflict/tradition provenance must remain visible; production synthesis does not average incompatible source traditions into false consensus.

## 5. Routing decision

Production routing is now:

```text
explicit Astrology production reading
→ ASTROLOGY.md
→ Astrology Fact Gate
→ admitted interpretation scope

explicit Astrology research
→ RESEARCH_ROUTING.md
→ references/astrology/**

ordinary unspecified divination
→ METHOD_ROUTING.md
→ Tarot / Meihua / Liuyao
```

Astrology v1 is not an ordinary auto-selection candidate.

No canonical Astrology × Tarot / Meihua / Liuyao cross-validation contract is created by this admission.

## 6. Behavioral coverage

`BEHAVIORAL_EVAL.md` adds:

```text
TAROT-BEH-016  explicit production Astrology → ASTROLOGY.md
TAROT-BEH-017  raw birth data without provider → Fact Gate fail closed
TAROT-BEH-018  Astrology research vs production intent separation
```

`evals/regression_matrix.json` includes `astrology-production` and routes future relevant changes to these scenarios.

## 7. First CI attempt — assertion wording failure, not admission evidence

`Validate Playbook #215`

```text
run id: 34756624652
job id: 103721983395
feature head: a1493b37ac0810bbf41c7c8d0e4d5cd0d53f4ad5
PR merge-ref: 8a81971ee2912dc4d947d80fcac3e29510a7480c
```

Environment:

```text
Ubuntu 24.04.5 LTS
CPython 3.12.14
git 2.55.0
runner 2.337.0
```

Result:

```text
Ran 53 tests
52 PASS / 1 FAIL
```

The sole failure was a brittle string assertion in `test_research_router_keeps_astrology_research_separate`: the test expected a literal phrase not present in the canonical router even though the router already expressed the same research/source-of-truth boundary.

No runtime, routing behavior, fact-gate or provenance implementation regression was shown by this failure. The test was corrected to assert the actual semantic boundary. Because the unit-test step failed, the workflow's structural-check step was skipped.

Run #215 is therefore **not** success/admission evidence.

## 8. Canonical successful execution

`Validate Playbook #216`

```text
run id: 34756670323
job id: 103722109390
feature head: 99e274bbf5d77bab17101b4f5dbedde9e1796718
PR merge-ref: 782ba4755514c65e6f69ba352b872c2d8b40d96e
```

Environment:

```text
Ubuntu 24.04.5 LTS
CPython 3.12.14
git 2.55.0
runner 2.337.0
```

Actual result from GitHub Actions logs:

```text
Astrology production contract tests   8 / 8 PASS
Astrology runtime gate tests         15 / 15 PASS
new Astrology production tests       23 / 23 PASS
whole root unittest suite            53 / 53 PASS
playbook structure                   PASS
```

The successful root suite also confirms the existing Liuyao/runtime/checker tests remained green under the production-routing changes.

## 9. What this establishes

The execution establishes that the repository now has tested production contracts for:

- explicit Astrology routing;
- research-vs-production separation;
- a machine-readable bounded admission manifest;
- provider-neutral Fact Bundle validation;
- forbidden LLM/model-calculated chart sources;
- source/verification provenance consistency;
- unknown-time house/angle fail-closed behavior;
- explicit Whole Sign / Placidus house policy;
- major-aspect type/orb/reference validation;
- natal/transit mode boundary;
- behavioral regression selection metadata;
- root structural integrity.

## 10. What this does not establish

It does not establish:

- scientific validity of astrology;
- a built-in ephemeris provider;
- independent verification of user-asserted chart calculations;
- production support for every research claim family;
- synastry/composite/solar-return/profection/rectification;
- automatic cross-validation with other divination methods;
- deterministic guarantees for health, death, pregnancy, legal, financial, accident, employment or relationship outcomes.

## 11. Privacy / repository boundary

All production fixtures are synthetic. No real birth data or personal reading records are stored in this public Playbook.

Palmistry is outside this production-admission change and remains untouched.
