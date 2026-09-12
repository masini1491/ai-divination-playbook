# Astrology Retrieval / Output Provenance Contract Draft

Status: **REFERENCE-ONLY / RESEARCH DRAFT / NOT PRODUCTION-ROUTABLE**

This contract defines a deterministic boundary between a resolved Astrology interpretation query and later L5 synthesis. It does not perform natural-language understanding, select a production tradition, or generate an astrology reading.

## 1. Pipeline boundary

```text
user question
→ upstream query resolution
→ available L1/L2 facts
→ explicit L3 policy / tradition context
→ deterministic registry selector
→ retrieval provenance bundle
→ L5 ChatGPT synthesis
```

The selector in this research round owns only:

```text
resolved query specification
+
versioned interpretation registry
→
selected L3/L4 claims + provenance + conflicts + guardrails
```

It does **not** own:

- astronomical calculation;
- natural-language intent classification;
- policy selection;
- free-form semantic similarity search;
- final prose generation;
- production routing.

## 2. Query specification

Candidate resolved query fields:

```text
query_id
claim_types[]
tradition_tags_any[]
applies_to_all[]
requires_l2_facts
l2_fact_refs[]
requires_l3_policy
l3_policy_refs[]
allow_reference_only_qualified
include_registry_guardrails
```

`claim_types[]` is required.

`tradition_tags_any[]` is an OR-filter over explicitly stored claim tradition tags.

`applies_to_all[]` is an AND-filter: every requested applicability token must be present in the claim.

The selector deliberately avoids fuzzy matching in this research version.

## 3. Preconditions fail closed

When a query declares that L2 facts are required but supplies no `l2_fact_refs[]`:

```text
retrieval_status = precondition_failed
```

Likewise, if an explicit L3 policy is required but no `l3_policy_refs[]` are supplied, retrieval fails closed.

A missing fact or policy does not authorize the selector to infer, calculate, or invent one.

## 4. Exact selection behavior

A claim is considered only when all required filters pass:

```text
claim_type match
tradition overlap when tradition filter is supplied
applicability superset match
all source_refs resolve
source admission rule passes
```

Unknown or unrepresented tradition:

```text
retrieval_status = no_match
```

There is no model-memory fallback inside the selector.

## 5. Source-admission behavior

Default behavior is conservative.

### All cited sources claim-eligible

If every cited source has at least one of:

```text
CLAIM_ELIGIBLE
POLICY_PROVENANCE_ELIGIBLE
```

then the selected claim uses:

```text
source_admission_mode = claim_eligible
```

### REFERENCE_ONLY involvement

A claim whose source provenance includes a source whose sole admission is `REFERENCE_ONLY` is not selected by default.

It may be selected only when:

```text
allow_reference_only_qualified = true
```

and the claim remains bounded by both:

```text
confidence_status ∈ qualified | provisional | conflicted
support_status    ∈ tradition_bounded | qualified | architecture_only | conflicted
```

Possible modes:

```text
qualified_reference_only
mixed_claim_eligible_and_reference_only
```

This prevents a claim-eligible companion source from silently laundering a `REFERENCE_ONLY` source into the result.

## 6. Conflict preservation

Every selected claim retains `conflict_group_ids[]`.

For each used conflict group, the bundle records:

```text
conflict_group_id
conflict_class
resolution_status
resolution_note
selected_claim_refs[]
external_claim_refs[]
```

`external_claim_refs[]` are claims participating in the same registered conflict but not selected by the current query.

This is intentional. The output must be able to say, in effect:

```text
this claim was selected for this scope
but the registry also records a conflicting / differently scoped claim
```

The selector never averages conflicting claims into a synthetic consensus.

## 7. Citation readiness

Each selected claim carries `source_provenance[]`.

Candidate provenance fields:

```text
source_id
title
author_or_org
source_role
admission_status
locator
edition
immutable_revision
publication_or_release_date
license_status
copyright_status
```

A selected claim is `citation_ready = true` only when every cited source has a non-empty locator.

Bundle status:

```text
citation_ready
```

requires all selected claims to be citation-ready.

Otherwise:

```text
retrieval_status = provenance_incomplete
```

This does not mean a user-facing citation has already been formatted. It means sufficient source locator provenance exists for the later output layer to construct or verify citations.

## 8. Synthesis provenance

Every successful selected bundle records:

```text
synthesis_provenance:
  l2_fact_refs[]
  l3_policy_refs[]
  claim_refs[]
  conflict_group_refs[]
```

The desired trace is:

```text
L2 deterministic fact
→ explicit L3 policy
→ selected L4 claim
→ preserved conflict context
→ source provenance
→ L5 synthesis
```

L5 output should not introduce a semantic assertion that cannot be traced to the bundle or clearly labeled as synthesis.

## 9. Guardrails

A registry may expose `non_admitted_claims[]`.

When the resolved query requests registry guardrails, they are copied into the provenance bundle unchanged.

This allows later synthesis to retain explicit negative evidence boundaries, for example:

```text
symbolic parent-image interpretation
!= literal parental biography
!= trauma diagnosis
```

The selector does not implement brittle keyword censorship. It preserves structured / explicitly registered guardrails.

## 10. Retrieval status vocabulary

Research statuses:

```text
invalid_query
registry_not_research_safe
precondition_failed
no_match
citation_ready
provenance_incomplete
```

Meaning:

- `invalid_query`: malformed deterministic query contract.
- `registry_not_research_safe`: registry violates version/status/production/privacy guards.
- `precondition_failed`: required L2 or L3 references are absent.
- `no_match`: valid request but no eligible claim survived exact filters.
- `citation_ready`: one or more selected claims and all selected source locators are present.
- `provenance_incomplete`: claims were selected but source locator provenance is incomplete.

## 11. Output bundle identity

Candidate machine identity:

```text
schema_name    = interpretation_retrieval_provenance_bundle
schema_version = 0.1.0-research
record_status  = REFERENCE-ONLY
production_routable = false
```

This bundle is a research intermediate artifact, not a production user-facing reading.

## 12. Regression families

The first executable regression set uses the two existing real claim families.

### Domicile

Regression questions include:

```text
classical domicile configuration
southern-hemisphere historical applicability conflict
```

Expected behavior:

- retrieve only the exact claim type/applicability requested;
- preserve the southern-hemisphere conflict group;
- do not choose a reversal/non-reversal doctrine for the project.

### Moon–Saturn

Regression questions include:

```text
modern psychological natal Moon-Saturn opposition
reference-implementation opposition framing
unknown/unrepresented tradition
```

Expected behavior:

- natal query selects the claim explicitly applicable to natal opposition;
- reference-only implementation evidence is not selected by default;
- explicit qualified opt-in is required when `REFERENCE_ONLY` provenance participates;
- parent-symbol vs literal-biography conflict remains visible;
- unrepresented tradition returns `no_match`, not a memory-generated interpretation.

## 13. Non-goals

This contract does not establish:

- semantic completeness of the registries;
- a canonical Western/classical/modern tradition taxonomy;
- a canonical orb policy;
- whether any astrology claim is scientifically true;
- clinical validity;
- predictive validity;
- outcome probabilities;
- another person's private motives;
- production readiness.

## 14. Promotion gap

After retrieval regression, the next gaps remain:

```text
query-resolution / routing contract
→ broader conflict regression across more claim families
→ user-facing citation rendering contract
→ L5 synthesis regression
→ explicit tradition taxonomy
→ production admission
```

**Current state: REFERENCE-ONLY / RESEARCH / NOT PRODUCTION-ROUTABLE.**
