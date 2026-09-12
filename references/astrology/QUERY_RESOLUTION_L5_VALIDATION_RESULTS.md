# Astrology Query Resolution + L5 Synthesis Validation Results

Status: **REFERENCE-ONLY / RESEARCH VALIDATION / NOT PRODUCTION-ROUTABLE**

Baseline repository main when this round began:

`ff321aecee1889e0e13cf320f56e6f4caadd2d64`

Runtime used for the isolated contract regression:

- Python `3.13.5`
- standard library only
- no network dependency
- no repository checkout

## 1. Scope

This round closes two research gaps left after deterministic interpretation retrieval:

```text
natural-language question
→ auditable query-resolution contract
→ deterministic retrieval
→ provenance bundle
→ deterministic L5 synthesis envelope
```

The work intentionally stops before free-form user-facing prose generation.

## 2. Added artifacts

```text
QUERY_RESOLUTION_ROUTING_CONTRACT_DRAFT.md
validate_astrology_query_resolution.py
L5_SYNTHESIS_ENVELOPE_CONTRACT_DRAFT.md
compose_interpretation_synthesis.py
test_query_resolution_l5_synthesis.py
test_query_resolution_l5_integration.py
QUERY_RESOLUTION_L5_VALIDATION_RESULTS.md
```

All files remain under `references/astrology/**`.

## 3. Query-resolution contract

Machine identity:

```text
schema_name = astrology_query_resolution
schema_version = 0.1.0-research
record_status = REFERENCE-ONLY
production_routable = false
```

Resolution statuses:

```text
resolved
needs_clarification
unsupported
```

Risk classes:

```text
normal_symbolic
private_motive_inference
clinical_or_diagnostic
high_stakes_external_outcome
```

Only `normal_symbolic` may produce a resolved executable route.

The validator therefore prevents query resolution itself from silently turning a request for private motives, diagnosis, or high-stakes outcome certainty into an Astrology retrieval route.

## 4. Routing provenance

The route remains compatible with `retrieve_interpretation_claims.py`:

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

Every non-empty semantic route field currently requires a corresponding `routing_assumptions[]` entry.

The assumption record can identify provenance as:

```text
user_text
upstream_context
research_fixture
research_policy
```

For `user_text`, the validator checks that the declared literal evidence span actually exists in the original question.

For `upstream_context`, an explicit evidence reference is required.

This is not proof that semantic interpretation is correct. It is an audit trail showing what evidence the resolver claims to have used.

## 5. Material ambiguity behavior

The contract fails closed when material routing state is missing.

Examples:

```text
required L2 fact but no fact ref
→ invalid resolution

required L3 policy but no policy ref
→ invalid resolution

material unresolved tradition / context
→ needs_clarification
→ no executable route

unsupported risk class
→ unsupported
→ no executable route
```

No model-memory fallback is authorized.

## 6. REFERENCE_ONLY evidence widening

Default route:

```text
allow_reference_only_qualified = false
```

When set to true, query resolution must also supply:

```text
reference_only_justification
```

The downstream selector still applies its existing qualified / tradition-bounded admission rule.

This keeps evidence widening explicit at both the routing and retrieval layers.

## 7. L5 synthesis envelope

Machine identity:

```text
schema_name = interpretation_synthesis_envelope
schema_version = 0.1.0-research
record_status = REFERENCE-ONLY
production_routable = false
```

The deterministic composer does not write final reading prose.

It packages one synthesis unit per selected registry claim and checks that the retrieval bundle belongs to the same route.

## 8. Cross-layer provenance checks

Before `ready_for_l5`, exact agreement is required for:

```text
query_id
registry_record_id
L2 fact refs
L3 policy refs
selected claim refs
conflict-group refs
```

Any mismatch returns:

```text
blocked_provenance_mismatch
```

Other blocking states include:

```text
blocked_resolution_not_resolved
blocked_bundle_schema
blocked_bundle_not_research_safe
blocked_query_mismatch
blocked_registry_mismatch
blocked_provenance_incomplete
blocked_retrieval_status
blocked_empty_claims
blocked_claim_statement_missing
```

This prevents a stale or mismatched retrieval result from being silently synthesized against a different query route.

## 9. Synthesis units

Each selected claim preserves:

```text
claim_id
normalized source-backed statement
statement SHA-256
claim type
tradition tags
applicability
scope
confidence/support status
source-admission mode
cautions
conflict refs
citation source refs
```

The `statement_sha256` is a deterministic fingerprint of the exact registered statement passed toward L5.

It is not a trust or truth signature. It simply makes silent mutation detectable by later tooling.

## 10. Citation behavior

Citation metadata are deduplicated using source identity plus locator / revision / edition context while preserving:

```text
source_id
title
author_or_org
source_role
admission_status
locator
edition
immutable_revision
publication date
license status
copyright status
```

Missing locator blocks L5 preparation as provenance incomplete.

## 11. Conflict / caution / guardrail preservation

The composer carries retrieval conflicts forward unchanged.

It also preserves claim cautions and registry guardrails.

`required_disclosures[]` are automatically extended when the bundle contains:

```text
claim cautions
registered conflicts
non-admitted-claim guardrails
qualified REFERENCE_ONLY provenance
```

The composer does not resolve or average those constraints.

## 12. Executed isolated regression

The implementation payload was first exercised in an isolated Python runtime before repository mutation.

Observed result:

```text
Ran 30 tests
OK
```

Breakdown:

- 17 query-resolution contract cases.
- 13 synthesis-envelope cases.
- 0 failures.
- 0 errors.
- 0 skips.

Covered cases include:

```text
valid symbolic resolution
schema / production guards
private-motive route block
clinical route block
high-stakes route block
unknown registry
query-id mismatch
missing L2 / L3 refs
REFERENCE_ONLY opt-in justification
literal user-text evidence verification
semantic route provenance coverage
needs-clarification behavior
unsupported behavior
ready-for-L5 composition
resolution / query / registry mismatch blocks
L2 / claim provenance mismatch blocks
no-match behavior
provenance-incomplete block
caution preservation
conflict preservation
guardrail preservation
citation locator preservation
statement hash stability
REFERENCE_ONLY disclosure
citation deduplication
```

After mutation, the GitHub branch versions of the validator, composer, and regression file were bounded-read back and matched the intended implementation shape.

## 13. Repo-local actual-registry integration regression

A separate committed file:

```text
test_query_resolution_l5_integration.py
```

is designed to run inside a repository checkout / CI workspace and directly reads:

```text
saturn_moon_aspect_claim_family_registry.json
```

It tests the complete chain:

```text
resolved Moon-Saturn question
→ validate query resolution against actual registry ID
→ retrieve actual claim registry
→ select claim:greene-moon-saturn-parent-image
→ compose L5 envelope
→ preserve parent-symbol-vs-biography conflict
→ preserve registry guardrails
→ preserve citation metadata
→ preserve L2/L3 route provenance
```

There are 4 such repo-local integration cases.

They were **not executed in this isolated runtime**, because the environment used for this round did not contain a GitHub repository checkout. They therefore are not included in the `30 tests / OK` execution claim.

This evidence boundary is intentional.

## 14. What was not validated

This round does **not** validate:

```text
natural-language resolver accuracy in the wild
whether the chosen claim type is semantically perfect
whether an astrology interpretation is true
scientific predictive validity
clinical validity
production safety policy completeness
full privacy detection
final user-facing prose quality
canonical tradition taxonomy
canonical orb policy
```

The deterministic validator can confirm that routing provenance is present and internally coherent; it cannot prove that an LLM's semantic mapping from language is philosophically or empirically correct.

## 15. Research conclusion

The interpretation pipeline now has explicit audit boundaries on both sides of deterministic retrieval:

```text
user question
→ auditable resolution envelope
→ deterministic selector
→ provenance bundle
→ deterministic synthesis envelope
→ later prose
```

The most important new constraint is:

```text
language understanding may propose a route
!= language understanding may invent evidence

retrieval may select a claim
!= L5 may silently strengthen or de-scope it
```

The remaining major gap is no longer the internal evidence trace. It is the controlled user-facing renderer and broader routing coverage across more claim families / tradition contexts.

## 16. Next gap

Recommended next research sequence:

```text
user-facing L5 renderer contract
→ citation rendering regression
→ broader claim-family routing fixtures
→ explicit tradition taxonomy
→ cross-family conflict regression
→ production admission decision
```

**Current state: REFERENCE-ONLY / RESEARCH / NOT PRODUCTION-ROUTABLE.**
