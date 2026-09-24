# Zi Wei Interpretation Claim Registry Schema v0

Authority：`REFERENCE-ONLY / RESEARCH SCHEMA / NOT PRODUCTION-ROUTABLE`

Schema name：`ziwei_interpretation_claim_registry`

Supported versions：

```text
0.1.0-research  historical major-star first-layer registry schema
0.1.1-research  hardens conditional activation metadata for major-star claims
0.2.0-research  historical palace-domain extension
0.2.1-research  hardens conditional activation metadata for palace-capable registries
```

`0.2.x-research` remains backward-compatible at the validator level with v0.1 claim types. Historical `0.1.0` / `0.2.0` files remain validator-readable; the production-admitted 52-claim corpus now uses `0.1.1` / `0.2.1` so conditional activation is explicit.

## Top-level contract

Required：

```text
schema_name
schema_version
record_status
record_kind
record_id
production_routable
interpretation_profile
sources[]
claims[]
conflict_groups[]
privacy
research_result
```

Required guards for all supported versions：

```text
schema_name = ziwei_interpretation_claim_registry
record_status = REFERENCE-ONLY
record_kind = ziwei_interpretation_claim_family_registry
production_routable = false
privacy.contains_real_birth_data = false
research_result.production_authority_granted = false
research_result.scientific_predictive_validity_claimed = false
```

## Versioned claim types

### v0.1.x

```text
star_core
star_conditional
methodology
```

### v0.2.x

```text
star_core
star_conditional
palace_domain
palace_conditional
methodology
```

A v0.1.x registry must not use palace claim types. Hardened palace registries declare `0.2.1-research`.

## Source record

Minimum fields：

```text
source_id
source_role
admission_status[]
storage_mode[]
independence_status
locator
```

Supported source roles：

```text
PRIMARY_TEXT
SCHOLARLY_SECONDARY
PRACTITIONER_REFERENCE
REFERENCE_IMPLEMENTATION
PROJECT_SYNTHESIS
```

Research admission statuses：

```text
REFERENCE_ONLY
CLAIM_ELIGIBLE
EVALUATION_ONLY
REJECTED
```

`REFERENCE_ONLY` and `EVALUATION_ONLY` sources cannot be the sole authority of a research-admitted claim.

## Claim record

Required：

```text
claim_id
layer
claim_type
subject
assertion_class
normalized_statement
source_refs[]
source_locators[]
applicability
confidence_status
support_status
conflict_group_ids[]
adoption_state
```

Allowed layer：`L4`.

Allowed assertion classes：

```text
historical_core
historical_conditional
named_tradition
practitioner_heuristic
case_inference
project_adoption
```

Applicability is structured data rather than prose inference. Fields may include：

```text
requires[]
forbids[]
modifiers[]
palace_scope[]
topology_scope[]
temporal_scope
conditional_activation {
  mode = context_only | fact_gated
  availability_requires[]
  satisfies_all[]
  satisfies_any[]
  forbids[]
}
```

For hardened `0.1.1-research` / `0.2.1-research`, every `star_conditional` / `palace_conditional` claim declares `conditional_activation`.

- `context_only`: methodology/profile/safety/context rule; chart-condition demonstration is not required and predicate arrays remain empty.
- `fact_gated`: availability facts first prove the relevant deterministic domain was computed. Missing availability is `not_computed`; available data that does not satisfy declared predicates is `unsatisfied`; only a demonstrated match is `satisfied`.
- Rule relevance is not condition demonstration. `modifiers[]` remains descriptive metadata and is never globally promoted to `requires[]`.

## Palace semantics

`palace_domain` records bounded historical domain scope. `palace_conditional` records topology, empty-palace handling, dignity/benefic/malefic conditions, safety requirements, or source-profile scope differences.

Historical labels and modern aliases must remain distinguishable. In particular, historical `奴僕宮` must not silently become universal `交友宮` semantics.

Body Palace is an overlay and is not admitted as a thirteenth ordinary palace claim family by this schema revision.

## Conflict groups

Conflict records：

```text
conflict_group_id
conflict_class
resolution_status
claim_refs[]
external_claim_refs[]
notes[]
```

v0.1 resolution statuses：

```text
PRESERVE_CONFLICT
RESOLVED_BY_PROFILE
```

v0.2 additionally permits：

```text
PRESERVE_SCOPE_DIFFERENCE
```

`PRESERVE_SCOPE_DIFFERENCE` means historical and modern source scopes overlap only partially and must not be collapsed into one universal semantic domain.

## Provenance and storage

Registries store normalized project-authored paraphrases plus source locators. They do not vendor full historical or practitioner text. Every claim must resolve all `source_refs[]`; every source locator must be non-empty.

## Research / production boundary

Structural validation does not prove doctrine truth, scientific validity, predictive validity, user-perceived accuracy, or production readiness.