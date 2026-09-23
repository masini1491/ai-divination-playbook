# Zi Wei Interpretation Claim Registry Schema v0

Authority：`REFERENCE-ONLY / RESEARCH SCHEMA / NOT PRODUCTION-ROUTABLE`

Schema name：`ziwei_interpretation_claim_registry`

Current version：`0.1.0-research`

This schema adapts the repository's proven Astrology claim-registry pattern to Zi Wei domain semantics. It does not reuse Astrology doctrine fields or grant production authority.

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

Required guards：

```text
schema_name = ziwei_interpretation_claim_registry
schema_version = 0.1.0-research
record_status = REFERENCE-ONLY
record_kind = ziwei_interpretation_claim_family_registry
production_routable = false
privacy.contains_real_birth_data = false
research_result.production_authority_granted = false
research_result.scientific_predictive_validity_claimed = false
```

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

`REFERENCE_ONLY` and `EVALUATION_ONLY` sources cannot be the sole authority of an admitted claim.

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

Allowed layers：`L4` only for this first interpretation registry.

Allowed assertion classes：

```text
historical_core
historical_conditional
named_tradition
practitioner_heuristic
case_inference
project_adoption
```

Allowed claim types for batch 1：

```text
star_core
star_conditional
methodology
```

Applicability is structured data, not prose inference. Supported batch-1 fields may include：

```text
requires[]
forbids[]
modifiers[]
palace_scope[]
topology_scope[]
temporal_scope
```

## Conflict groups

A conflict group preserves incompatible source/tradition claims. It must not average them into consensus.

Conflict record fields：

```text
conflict_group_id
conflict_class
resolution_status
claim_refs[]
external_claim_refs[]
notes[]
```

`external_claim_refs[]` may point to bounded evidence that is intentionally not copied into the registry because of license/admission boundaries.

## Provenance and storage

This registry stores normalized project-authored paraphrases plus locators. It does not vendor full source text. Every claim must resolve all `source_refs[]`, and every `source_locators[]` entry must be non-empty.

## Research / production boundary

Registry validation proves only structural research safety. It does not prove doctrine truth, scientific validity, predictive validity, user-perceived accuracy, or production readiness.