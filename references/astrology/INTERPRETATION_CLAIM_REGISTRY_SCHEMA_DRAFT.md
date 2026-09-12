# Astrology Interpretation Claim Registry Schema Draft

Status: **REFERENCE-ONLY / RESEARCH SCHEMA / NOT PRODUCTION-ROUTABLE**

Schema name: `interpretation_claim_registry`

Schema version: `0.1.0-research`

This document freezes the first canonical research shape for Astrology interpretation claim-family registries. It does not choose a production tradition, interpretation doctrine, orb policy, or scientific-validity position.

## 1. Why freeze a schema now

The first two real claim-family registries proved the source-admission architecture, but they were authored during different research rounds and therefore used different field names and metadata depth.

Observed legacy differences included:

```text
admission_state        vs admission_status
statement              vs normalized_statement
confidence             vs confidence_status
conflict_group_refs    vs conflict_group_ids
author                 vs author_or_org
revision               vs immutable_revision
compact storage labels vs storage-mode arrays
```

The executable validator showed that both current registries are structurally sound. The schema freeze therefore addresses future drift rather than repairing invalid evidence.

## 2. Compatibility policy

Two modes are supported by the research validator:

```text
unversioned legacy registry
→ accepted through bounded aliases for regression / migration compatibility

versioned registry
→ must follow 0.1.0-research canonical field names and shapes
```

Legacy compatibility is transitional. New claim-family registries should be versioned.

## 3. Top-level record

Canonical shape:

```text
schema_name
schema_version
record_status
record_kind
record_id
production_routable
sources[]
claims[]
conflict_groups[]
privacy
```

Optional family-specific metadata may be added, for example:

```text
claim_family
subject
branch_baseline
lineage_rules
research_result
non_admitted_claims
retrieval_contract
notes
```

Required values for this research version:

```text
schema_name       = interpretation_claim_registry
schema_version    = 0.1.0-research
record_status     = REFERENCE-ONLY
record_kind       = interpretation_claim_family_registry
production_routable = false
privacy.contains_real_birth_data = false
```

A versioned record must explicitly carry the production and privacy guards instead of relying on omission.

## 4. Source record

Minimum canonical source fields:

```text
source_id
source_role
admission_status[]
storage_mode[]
independence_status
```

Recommended provenance fields when known:

```text
title
author_or_org
source_kind
tradition_tags[]
publication_or_release_date
edition
immutable_revision
locator
language
license_status
license_identifier
copyright_status
verification_status[]
admission_scope[]
excluded_scope[]
upstream_source_refs[]
derivative_relationship
notes[]
```

### 4.1 Canonical naming

Versioned registries use:

```text
author_or_org
immutable_revision
admission_status
```

not:

```text
author
revision
admission_state
```

The validator may continue reading legacy aliases only for unversioned historical fixtures.

### 4.2 `source_role`

Accepted research roles remain:

```text
PRIMARY_TEXT
SCHOLARLY_SECONDARY
PRACTITIONER_REFERENCE
REFERENCE_IMPLEMENTATION
UNVERIFIED_WEB_SOURCE
PROJECT_SYNTHESIS
```

A source may have one role as a string or multiple roles as a string array.

### 4.3 `admission_status[]`

Versioned records always use an array, even when there is one value.

Candidate values remain:

```text
REJECTED
REFERENCE_ONLY
CLAIM_ELIGIBLE
POLICY_PROVENANCE_ELIGIBLE
CORPUS_STORAGE_ELIGIBLE
PRODUCTION_ADMITTED
```

For this research schema, `PRODUCTION_ADMITTED` is rejected by the validator.

### 4.4 `storage_mode[]`

Versioned records always use an array.

Canonical modes:

```text
metadata_only
metadata_plus_locator
normalized_paraphrase
short_excerpt_with_citation
licensed_module_copy
public_domain_text_copy
project_authored_synthesis
```

Legacy compact labels remain validator-compatible only for unversioned records.

### 4.5 lineage

`upstream_source_refs[]` must resolve to source IDs in the same registry and cannot self-reference.

`independence_status` records the evidence relationship, not the prestige of the source.

The current accepted research vocabulary includes:

```text
independent_evidence
likely_derivative
explicit_derivative
shared_upstream
unknown
```

Legacy lineage labels remain readable for unversioned fixtures but should not be introduced into new versioned registries.

## 5. Claim record

Minimum canonical claim fields:

```text
claim_id
layer
claim_type
normalized_statement
source_refs[]
confidence_status
support_status
conflict_group_ids[]
```

Recommended contextual fields:

```text
source_locator_refs[]
tradition_tags[]
policy_refs[]
applies_to[]
configuration_assumptions[]
scope
cautions[]
storage_origin
```

### 5.1 Canonical naming

Versioned registries use:

```text
normalized_statement
confidence_status
conflict_group_ids
```

not:

```text
statement
confidence
conflict_group_refs
```

### 5.2 layers

This registry covers sourced policy / interpretation evidence only:

```text
L3
L4
```

L1/L2 deterministic astronomy facts belong in the Structured Astrology Fact layer. L5 user-facing synthesis is not stored as a source claim.

### 5.3 confidence

Accepted labels:

```text
supported
qualified
provisional
conflicted
unsupported
```

These labels describe evidence support inside the declared scope. They are not numeric outcome probabilities.

### 5.4 support status

Accepted labels:

```text
single_source_supported
multi_source_supported
tradition_bounded
qualified
conflicted
historical_only
architecture_only
unsupported
```

`multi_source_supported` requires at least two distinct source IDs and at least two evidence roots after declared upstream lineage is considered.

Repeated downstream copies do not create independent evidence.

### 5.5 REFERENCE_ONLY guard

A claim backed only by sources whose sole admission is `REFERENCE_ONLY` cannot be marked as unqualified `supported` / `single_source_supported` / `multi_source_supported`.

Qualified or tradition-bounded use remains possible when explicitly scoped.

## 6. Conflict group

Canonical shape:

```text
conflict_group_id
conflict_class[]
claim_refs[]
tradition_contexts[]
configuration_contexts[]
resolution_status
resolution_note
```

Only `conflict_group_id` is structurally indispensable in every research case, but versioned records should provide enough context to explain why the claims are not collapsed.

Conflict classes remain:

```text
tradition_difference
policy_difference
historical_development
translation_difference
source_disagreement
scope_difference
configuration_difference
precision_difference
unresolved
```

Resolution statuses remain:

```text
coexist
scope_separated
historically_sequenced
one_source_superseded_for_specific_claim
insufficient_evidence
unresolved
```

The schema does not permit an averaging operation that invents consensus from incompatible doctrines.

## 7. Privacy guard

Every versioned registry must include:

```json
{
  "privacy": {
    "contains_real_birth_data": false
  }
}
```

Claim-family evidence registries should use synthetic, source-level, fictional, or lawful-public fixtures. Personal natal data are unnecessary for source-admission evidence.

The current validator checks only this explicit marker. It does not claim semantic PII detection.

## 8. Production guard

Every versioned record must include:

```text
record_status = REFERENCE-ONLY
production_routable = false
```

The validator also rejects:

```text
PRODUCTION_ADMITTED
production_authority_granted = true
scientific_predictive_validity_claimed = true
```

This is a research integrity contract, not production admission.

## 9. Migration rule

Migration from an unversioned registry must preserve claim semantics and evidence provenance.

Permitted normalization includes:

```text
field rename
scalar → one-element array where the canonical field is array-valued
legacy lineage label → canonical lineage label when the evidence relationship is unchanged
adding explicit production/privacy guards
adding explicit source locator / caution / storage-origin metadata already supported by the dossier
```

Migration must not silently:

```text
upgrade source admission
upgrade confidence
invent source independence
resolve an unresolved doctrine conflict
add predictive / clinical authority
change a historical claim into a production rule
```

If a semantic change is needed, it requires a separate evidence decision rather than being hidden inside schema migration.

## 10. Validator behavior

For unversioned records, the validator remains backward-compatible with the first two research-era styles.

For `0.1.0-research` records, it additionally enforces:

```text
schema_name / schema_version
explicit production_routable=false
explicit privacy.contains_real_birth_data=false
canonical admission_status[]
canonical storage_mode[]
canonical source naming
canonical normalized_statement
canonical confidence_status
canonical support_status
canonical conflict_group_ids[]
```

This allows the repository to retain regression coverage for early research artifacts while preventing new schema drift.

## 11. Versioning policy

`0.1.0-research` is not a production semantic version promise.

A future schema change should increase the research version when it changes required field meaning, accepted canonical shapes, or validation behavior for versioned records.

Adding optional metadata that does not alter existing semantics may remain within the same research version until the next deliberate review.

## 12. Current decision

The project now has a bounded schema-freeze decision:

```text
legacy compatibility retained
+
new versioned canonical shape frozen
+
strict checks apply to versioned records
+
no production authority granted
```

**Current state: REFERENCE-ONLY / RESEARCH / NOT PRODUCTION-ROUTABLE.**
