# Zi Wei Production Readiness Gap Analysis v0

> Current-state reconciliation (2026-09-24): this file is a point-in-time readiness analysis. Current production authority is now `ZIWEI.md` + admission manifests + production tools. Explicit Zi Wei routing is admitted; ordinary unspecified auto-routing remains intentionally false. Gregorian input (`ziwei.calendar.tw_v1`), optional brightness (`ziwei.brightness.iztro_v1`) and deterministic materialization are also admitted. Historical G8 wording below must not be read as saying that no production Zi Wei route exists.

Authority：`REFERENCE-ONLY / READINESS ANALYSIS / NOT PRODUCTION ADMISSION`

## Purpose

This document converts the current Zi Wei research state into explicit production-readiness gates. It does not authorize production implementation or ordinary routing.

## Current baseline

```text
calculation research preset          = ziwei.baseline.tw_v1 (research candidate)
interpretation profile              = ziwei.interpretation.tw_v1
major-star first layer              = 14 subjects / 28 claims
palace first layer                  = 12 subjects / 24 claims
combined first layer                = 52 claims
executable retrieval/composition    = ADMITTED — RESEARCH-ONLY V0
production runtime                  = ADMITTED — SCOPE-A V1
production routing                  = NOT ADMITTED
```

## Gate matrix

| Gate | Current evidence | State | Next owner |
| --- | --- | --- | --- |
| G1 Calculation authority | `tools/ziwei_natal_provider.py` implements the bounded natal facts required by Scope A with pinned parity + fail-closed tests | ADMITTED — SCOPE-A NATAL | production binding remains G7 |
| G2 Production request/fact/frame schemas | versioned fail-closed schema candidates + validator regressions | RESEARCH-CLOSED | production binding remains separate |
| G3 Claim coverage | Scope A selects the admitted 52 natal first-layer claims as the complete required interpretation corpus | SATISFIED — SCOPE A | reopen only if product scope expands |
| G4 Executable retrieval/composition | deterministic research-only v0 + unit regressions | RESEARCH-CLOSED | production hardening requires separate gate |
| G5 Dependency / behavioral validation | architecture fixtures + machine-readable executable mapping + regressions | RESEARCH-CLOSED | production dependency validation remains separate |
| G6 User-facing uncertainty / safety | bounded delivery contract + deterministic action regressions | RESEARCH-CLOSED | production renderer binding remains separate |
| G7 Production admission | Scope-A provider + 52-claim allowlist + deterministic retrieval + delivery contract bound by `ZIWEI_PRODUCTION_ADMISSION_V1.json` and `tools/ziwei_scope_a_pipeline.py` | ADMITTED — SCOPE-A V1 | G8 routing remains separate |
| G8 Ordinary routing | no ZIWEI.md / METHOD_ROUTING integration | BLOCKED | separate post-G7 routing gate |

## G1 — calculation authority

`tools/ziwei_natal_provider.py` is admitted as the deterministic **Scope-A natal calculation authority**. This admission is intentionally narrower than a full Zi Wei production method and does not grant G7/G8.

Admitted G1 boundary for Scope A:

- normalized traditional-lunar input + provenance is required;
- Life/Body, twelve-palace geometry/stems, Five-Element Bureau, Zi Wei start, fourteen-major-star placement and topology are deterministic provider facts;
- provider/profile identity is explicit as `ziwei-scope-a-natal-python@0.1.0` / `ziwei.scope_a.natal_v0`;
- documented variants remain identity-bearing and are not flattened.

Not Scope-A blockers:

- project-wide brightness table/profile;
- dynamic calculation/runtime;
- auxiliary/minor-star calculation beyond required natal first-layer facts;
- the two historical facsimile image gaps, unless new evidence materially changes a required natal fact.

A production runtime must expose component/profile identity and provenance rather than hiding these choices behind a single opaque `default`.

## G2 — production-grade schemas

`PRODUCTION_SCHEMA_CANDIDATES_V0.md` now defines versioned fail-closed request/fact/retrieval/frame candidates and `validate_production_schema_candidates_v0.py` provides bounded deterministic validation. The candidate covers:

- normalized request/input provenance;
- calculation/profile identity;
- fact state (`known / unknown / not_computed / ambiguous / not_applicable`);
- natal chart facts and topology;
- optional profile-bound brightness / transformation / temporal facts;
- retrieval trace and omissions;
- conflict and safety state;
- interpretation frame and provenance trace.

Unavailable facts remain explicit states and cannot be treated as computable. G2 remains research-closed at the schema-candidate artifact level. Scope-A v1 binds the required request/provenance/frame semantics through the G7 production pipeline contract; the candidate document itself is not rewritten as historical production authority.

## G3 — claim coverage

The admitted 52 claims are sufficient for bounded first-layer research behavior, not for a claim of complete Zi Wei interpretation coverage.

Production scope has now explicitly selected:

```text
A. bounded natal first layer only  ← SELECTED
B. broader contextual natal interpretation
C. natal + dynamic interpretation
```

For Scope A, the admitted 52 claims satisfy G3. B/C capabilities are not blockers and must not be silently pulled into the production path.

## G4 — executable retrieval/composition

Research-only v0 is admitted and unit-tested. It is not production authority.

For Scope-A v1, G7 supplies the bounded production wrapper and contract tests over this retriever. The research executable remains historically research-only and is not itself relabeled as production authority.

## G5 — dependency / behavioral validation

Architecture-level synthetic fixtures now have a machine-readable executable-v0 mapping in `ziwei_executable_behavioral_fixtures_v0.json` with deterministic regression coverage. Each fixture is classified as:

- executable now with admitted facts/claims;
- fail-closed because a required fact/profile is unavailable;
- blocked because an L4 claim family is not admitted;
- architecture-only because the fixture assumes unsupported modifiers.

Passing means correct bounded behavior, including correct refusal/omission. G5 remains research-closed for executable v0; Scope-A v1 adds production contract tests against the admitted provider/pipeline without rewriting the research fixture artifact.

## G6 — uncertainty / safety

`UNCERTAINTY_SAFETY_DELIVERY_CONTRACT_V0.md` now defines a bounded delivery contract with deterministic action validation covering:

- source-backed vs project-adopted vs profile-specific vs conflicted vs insufficient;
- missing-fact and omitted-claim disclosure;
- conflict preservation;
- no certainty inflation;
- health/death/legal/financial high-impact boundaries;
- no scientific/predictive-validity implication.

G6 remains research-closed at the delivery-contract artifact level. Scope-A v1 binds its deterministic delivery actions in the G7 pipeline; final prose remains outside pipeline authority.

## G7 / G8 — admission and routing

G7 is admitted for Scope-A v1 by `ZIWEI_PRODUCTION_ADMISSION_V1.json` + `tools/ziwei_scope_a_pipeline.py`. The binding allowlists the historically non-routable 52-claim research registries, uses the admitted G1 provider, preserves conflicts/omissions, and applies the bounded delivery contract. It grants no final-prose authority and no scientific-validity claim.

G8 remains blocked. Production admission does not create `ZIWEI.md`, modify `METHOD_ROUTING.md`, or enable unspecified-user auto-routing.


Production admission is now complete for bounded Scope-A v1. The only next production gate is G8: ordinary routing artifacts such as `ZIWEI.md`, `METHOD_ROUTING.md`, `PLAYBOOK_INDEX.json`, loader/routing caches and production smoke expectations require a separate routing decision.

## ChatGPT-direct continuation

The currently admitted ChatGPT-direct readiness closures are complete:

- G2 production-schema candidate design — **CLOSED — RESEARCH**;
- G5 executable behavioral validation — **CLOSED — RESEARCH**;
- G6 uncertainty/safety delivery contract — **CLOSED — RESEARCH**;
- readiness owner reconciliation — **CLOSED — RESEARCH**.

There is no remaining automatically admitted ChatGPT-direct readiness Stage. Further work requires a new current-scope decision rather than continuing by inertia.

The following remain separate gates:

- choosing/admitting a production calculation profile/runtime;
- selecting a project-wide brightness table when required;
- admitting dynamic calculation/claims;
- production implementation/admission;
- ordinary routing integration.

## Next decision gate

The minimum product scope decision is now:

```text
A. bounded natal first layer only  ← SELECTED
B. broader contextual natal interpretation
C. natal + dynamic interpretation
```

`PRODUCTION_SCOPE_A_NATAL_FIRST_V0.md` owns this decision. G3 claim expansion, project-wide brightness selection, auxiliary claim expansion and dynamic runtime are not Scope-A blockers. G1 is now admitted for the facts Scope A actually consumes. Production binding/admission (G7) and ordinary routing (G8) remain separate later gates.
