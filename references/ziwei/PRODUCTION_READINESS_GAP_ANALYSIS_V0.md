# Zi Wei Production Readiness Gap Analysis v0

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
production runtime                  = NOT ADMITTED
production routing                  = NOT ADMITTED
```

## Gate matrix

| Gate | Current evidence | State | Next owner |
| --- | --- | --- | --- |
| G1 Calculation authority | Matched-profile research exists; baseline is componentized; brightness table open; dynamic runtime unadmitted | BLOCKED | source/profile + implementation gate |
| G2 Production request/fact/frame schemas | Research-facing conceptual contracts only | OPEN | ChatGPT can define bounded schema candidates |
| G3 Claim coverage | 52 natal first-layer claims; contextual/dynamic/auxiliary corpora incomplete | PARTIAL | evidence/admission, on material need |
| G4 Executable retrieval/composition | deterministic research-only v0 + unit regressions | RESEARCH-CLOSED | production hardening requires separate gate |
| G5 Dependency / behavioral validation | architecture fixtures + machine-readable executable mapping + regressions | RESEARCH-CLOSED | production dependency validation remains separate |
| G6 User-facing uncertainty / safety | research safety principles exist; no production delivery contract | OPEN | ChatGPT can define bounded contract |
| G7 Production admission | explicitly not granted | BLOCKED | separate explicit admission decision |
| G8 Ordinary routing | no ZIWEI.md / METHOD_ROUTING integration | BLOCKED | only after G1–G7 |

## G1 — calculation authority

Current research is strong enough to identify a candidate componentized profile, but not enough to call it a production calculation authority.

Material blockers:

- no admitted deterministic Zi Wei chart runtime/provider;
- project-wide brightness table/profile remains unselected;
- dynamic calculation/runtime remains unadmitted;
- documented profile/witness variants remain identity-bearing and must not be flattened;
- two historical facsimile image gaps remain open but are not by themselves reasons to rerun broad research.

A production runtime must expose component/profile identity and provenance rather than hiding these choices behind a single opaque `default`.

## G2 — production-grade schemas

The current Fact Packet / Retrieval / Frame documents are conceptual research contracts. Production readiness needs versioned machine-readable schemas for at least:

- normalized request/input provenance;
- calculation/profile identity;
- fact state (`known / unknown / not_computed / ambiguous / not_applicable`);
- natal chart facts and topology;
- optional profile-bound brightness / transformation / temporal facts;
- retrieval trace and omissions;
- conflict and safety state;
- interpretation frame and provenance trace.

These schemas can be researched before a production runtime exists, but must not pretend unavailable facts are computable.

## G3 — claim coverage

The admitted 52 claims are sufficient for bounded first-layer research behavior, not for a claim of complete Zi Wei interpretation coverage.

Production admission must explicitly decide whether minimum viable scope is:

```text
A. bounded natal first layer only
or
B. broader contextual natal interpretation
or
C. natal + dynamic interpretation
```

Do not silently treat B/C as required merely because the domain can support them.

## G4 — executable retrieval/composition

Research-only v0 is admitted and unit-tested. It is not production authority.

Production hardening would require stable schema inputs, dependency validation, stronger malformed/ambiguous-input handling, compatibility/version policy, and behavioral regression against admitted fixtures.

## G5 — dependency / behavioral validation

Architecture-level synthetic fixtures now have a machine-readable executable-v0 mapping in `ziwei_executable_behavioral_fixtures_v0.json` with deterministic regression coverage. Each fixture is classified as:

- executable now with admitted facts/claims;
- fail-closed because a required fact/profile is unavailable;
- blocked because an L4 claim family is not admitted;
- architecture-only because the fixture assumes unsupported modifiers.

Passing means correct bounded behavior, including correct refusal/omission. It does not require manufacturing unsupported output. G5 is therefore research-closed for the current 52-claim executable v0; production dependency/behavioral validation must be reopened against the eventual production schemas/runtime.

## G6 — uncertainty / safety

Production delivery needs a machine-checkable/user-facing contract covering at least:

- source-backed vs project-adopted vs profile-specific vs conflicted vs insufficient;
- missing-fact and omitted-claim disclosure;
- conflict preservation;
- no certainty inflation;
- health/death/legal/financial high-impact boundaries;
- no scientific/predictive-validity implication.

This can be designed before production routing.

## G7 / G8 — admission and routing

Production admission is a separate explicit decision after evidence from preceding gates. Only after that decision may ordinary routing artifacts such as `ZIWEI.md`, `METHOD_ROUTING.md`, `PLAYBOOK_INDEX.json`, loader/routing caches or production smoke expectations be considered.

## ChatGPT-direct continuation

Under current ChatGPT-Only mode, the following readiness work can proceed without crossing production authority:

1. production-schema candidate design with unavailable fields fail-closed;
2. uncertainty/safety delivery contract;
3. readiness matrix reconciliation after each closure.

Executable behavioral validation over the admitted fixtures is **CLOSED — RESEARCH**.

The following remain separate gates:

- choosing/admitting a production calculation profile/runtime;
- selecting a project-wide brightness table when required;
- admitting dynamic calculation/claims;
- production implementation/admission;
- ordinary routing integration.
