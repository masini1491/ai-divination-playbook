# Zi Wei Interpretation Runtime Contracts v0

Authority：`REFERENCE-ONLY / RESEARCH CONTRACT / NOT PRODUCTION-ROUTABLE`

This document defines research-facing handoff contracts. It does not create executable production schemas or runtime authority.

## Pipeline

```text
normalized birth input
→ deterministic calculation profile
→ chart facts
→ Zi Wei Fact Packet v0
→ interpretation profile
→ Claim Retrieval v0
→ conflict + safety gates
→ Interpretation Frame v0
→ prose renderer
```

Every stage may narrow or compose admitted evidence; it must not invent a missing chart fact or doctrine rule.

## 1. Zi Wei Fact Packet v0

Conceptual shape：

```text
schema_version
packet_id
identity
input_provenance
chart
topology
temporal_context?
facts[]
ambiguity[]
validation
provenance_map
```

Fact state must be explicit: `known`, `unknown`, `not_computed`, `ambiguous`, `not_applicable`. Absence must not silently mean false. If brightness is not computed/admitted, brightness-dependent claims are skipped.

Profile-sensitive facts retain `profile_scope` and provenance. A bare profile-dependent fact without identity is insufficient. For brightness this includes `brightness_profile` plus rule/engine provenance; a label such as `廟` or `陷` without that identity is not a sufficient research fact.

## 2. Claim Retrieval v0

Input concept：

```text
fact_packet_id
interpretation_profile
requested_domains[]
temporal_scope
enabled_source_sets[]
trace_mode
safety_context
```

Retrieval performs fact matching + profile/source gating + applicability matching + specificity ordering + conflict detection. It is not fuzzy prose search and does not allow LLM-memory fallback.

Future claim applicability should be machine-matchable for star-in-palace, dignity, transformations, same-palace, benefics/malefics, opposite, sanfang, body overlay and temporal scope. A transformation-dependent match additionally requires the transformed-star fact's `sihua_profile_id`; the label alone is insufficient.

Each selected claim should preserve claim ID, matched fact IDs, applicability result, specificity level, source, tradition, assertion class, conflict group, adoption state and provenance.

## 3. Specificity contract

Within one authority chain：

```text
exact conditional combination
> star + palace + condition
> star + palace
> star conditional
> star core
> palace domain core
```

Across traditions, profile/source policy is resolved first; specificity alone cannot override another tradition.

## 4. Conflict gate

If a registered conflict has no explicit profile resolution: `resolution_state = unresolved_cross_tradition_conflict`. Allowed behavior is selecting the explicitly chosen tradition or exposing perspectives separately. Averaging into a new compromise is forbidden.

## 5. Interpretation Frame v0

Before prose rendering, produce a bounded frame containing packet/profile identity, themes, selected claim IDs, supporting fact IDs, modifiers, conflicts, bounded conclusions, evidence states, omissions, safety flags and provenance trace.

## 6. Theme clustering

Default themes may include identity/temperament, career/responsibility, relationships, money/resources, mobility/environment and inner life. Prefer a small number of high-specificity non-duplicative claims instead of dumping every matching rule.

## 7. Evidence state

Use qualitative research states such as `source_backed`, `project_adopted`, `profile_specific`, `conflicted`, `insufficient`, `case_inference_only`; do not invent pseudo-precise confidence numbers.

## 8. Fail-closed behavior

```text
missing fact → skip dependent claim
not_computed → do not guess
no supported claim → no generic horoscope filler
missing requested tradition → do not substitute another tradition
registered conflict → do not average
```

## 9. Safety gate

High-impact health/death/legal/financial claims remain bounded source evidence and are not converted into diagnostic, guaranteed or deterministic real-world predictions in ordinary user-facing synthesis.

## 10. Rendering boundary

Default prose is conditional and context-aware. The renderer improves readability only; it does not recalculate the chart or create new doctrine.

## 11. Production boundary

Production still requires versioned machine-readable schemas, executable validators/selectors/composers, a canonical calculation runtime, fixtures/regressions, explicit source/claim admission and explicit production admission.