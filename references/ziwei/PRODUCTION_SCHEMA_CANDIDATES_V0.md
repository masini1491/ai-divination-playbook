# Zi Wei Production Schema Candidates v0

> Supersession / current-state note (2026-09-24): these schemas remain research candidates and historical design evidence; they are not the current production API authority. A bounded Scope-A production runtime now exists, explicit Zi Wei routing is admitted, and the current runtime additionally exposes conditional activation evaluation semantics. Future typed request/result work is tracked separately in `ZIWEI_BACKLOG.md`.

Authority：`REFERENCE-ONLY / PRODUCTION-SCHEMA CANDIDATE / NOT PRODUCTION ADMISSION`

These schemas define fail-closed interfaces for a future production implementation. They do not imply that a Zi Wei calculation runtime/provider or production route exists.

## Version

`schema_version = 0.1.0-candidate`

Breaking semantic changes require a new version. Unknown fields may be rejected by a future strict implementation; consumers must not infer semantics from undeclared fields.

## Request candidate

Required identity:

```text
request_id
schema_version
interpretation_profile
requested_scope
input_provenance
birth_input
calculation_profile
```

`requested_scope` is one of `natal_baseline / decadal / yearly / monthly / daily / hourly`.

If requested scope requires an unadmitted runtime layer, the request is valid as data but execution must return an explicit unsupported/unavailable state rather than widening or falling back to natal prediction.

## Fact state candidate

Every material fact carries:

```text
fact_id
fact_type
state = known | unknown | not_computed | ambiguous | not_applicable
value?
profile_scope?
source_provenance[]
calculation_provenance?
ambiguity?
```

Rules:

- `known` requires a value and provenance;
- `unknown / not_computed / ambiguous` cannot satisfy a claim `requires[]`;
- profile-sensitive brightness requires `brightness_profile_id`;
- Four-Transformation facts require `sihua_profile_id`;
- temporal facts require exact temporal scope, target identity and boundary profile;
- absence is not equivalent to false.

## Fact Packet candidate

```text
packet_id
schema_version
request_id
interpretation_profile
calculation_profile
temporal_context
facts[]
topology
ambiguity[]
validation
provenance_map
```

A packet may be structurally valid while containing unavailable facts. Structural validity is not calculation completeness.

## Retrieval result candidate

```text
packet_id
selected_claims[]
omissions[]
conflicts[]
trace
production_authority_granted
```

Each selected claim preserves claim ID, matched fact IDs/tokens, source refs, applicability, specificity, conflict groups, adoption state and provenance.

Each omission preserves a stable reason such as:

```text
required_fact_missing
fact_not_known
profile_identity_missing
temporal_scope_mismatch
source_not_enabled
claim_not_admitted
unsupported_scope
registered_conflict_unresolved
```

## Interpretation Frame candidate

```text
frame_id
schema_version
packet_id
interpretation_profile
temporal_scope
selected_claim_ids[]
subject_claims
themes[]
conflicts[]
omissions[]
evidence_states[]
safety_flags[]
provenance_trace
rendering_boundary
production_authority_granted
```

The frame contains only admitted evidence. A renderer may improve language but cannot add chart facts or doctrine.

## Fail-closed invariants

```text
missing required fact        → omit dependent claim
unknown/not_computed fact    → does not satisfy requirement
ambiguous fact               → preserve ambiguity; no silent choice
missing profile identity     → skip profile-sensitive claim
unsupported temporal scope   → no natal fallback
unadmitted claim family      → no model-memory substitution
registered conflict          → preserve or explicit profile resolution
high-impact safety flag      → renderer must apply delivery boundary
production authority false   → cannot ordinary-route as production
```

## Scope compatibility

These candidates are intentionally compatible with a future bounded natal-first production scope. They also leave explicit extension points for brightness, Four Transformations and temporal facts without requiring those capabilities to be admitted now.

They do not choose production scope A/B/C, a brightness table, a calculation provider, dynamic runtime, or production routing.
