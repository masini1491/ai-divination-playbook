# Astrology L5 Synthesis Envelope Contract Draft

Status: **REFERENCE-ONLY / RESEARCH DRAFT / NOT PRODUCTION-ROUTABLE**

Schema name: `interpretation_synthesis_envelope`

Schema version: `0.1.0-research`

This contract defines the deterministic handoff between retrieval provenance and later user-facing L5 prose. It does not itself generate a reading.

## 1. Pipeline

```text
validated query resolution
→ retrieval provenance bundle
→ deterministic synthesis envelope
→ user-facing prose renderer
```

The synthesis envelope exists to prevent a prose generator from silently dropping or rewriting the evidence boundaries already established upstream.

## 2. Required research identity

```text
record_status = REFERENCE-ONLY
production_routable = false
```

The envelope is a research intermediate artifact only.

## 3. Input identity must agree

The composer requires exact agreement across:

```text
query_id
registry_record_id
L2 fact refs
L3 policy refs
selected claim refs
conflict-group refs
```

Any mismatch produces a blocked synthesis status.

This prevents an L5 answer from being composed from a retrieval bundle that belongs to another route or from stale/tampered provenance.

## 4. Accepted retrieval state

Normal composition requires:

```text
retrieval_status = citation_ready
```

Special case:

```text
retrieval_status = no_match
→ synthesis_status = no_supported_claims
```

No-match is not permission for model-memory completion.

Blocked examples:

```text
provenance_incomplete
invalid_query
precondition_failed
registry_not_research_safe
```

## 5. Synthesis units

Each selected claim becomes one `synthesis_unit` carrying:

```text
claim_id
statement
statement_sha256
claim_type
tradition_tags[]
applies_to[]
scope
confidence_status
support_status
source_admission_mode
cautions[]
conflict_group_ids[]
citation_source_ids[]
semantic_policy = registered_claim_only
```

The statement is the registry's normalized claim statement, not newly invented prose.

`statement_sha256` provides a cheap deterministic fingerprint so later tooling can detect accidental or silent mutation of the source-backed statement before rendering.

## 6. No hidden semantic expansion

The deterministic composer must not:

```text
invent a new interpretation
combine claims into a stronger claim
convert symbolic language into biography
convert historical doctrine into modern psychology
remove tradition scope
remove applicability scope
upgrade confidence
upgrade source admission
```

Its job is packaging and integrity checking only.

Any later prose renderer must remain constrained by these synthesis units.

## 7. Citation units

Every synthesis unit references `citation_source_ids[]`.

The envelope deduplicates citation metadata by source identity + locator + immutable revision / edition, while retaining:

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

Missing source locator blocks composition as `blocked_provenance_incomplete`.

## 8. Conflict preservation

The envelope copies registered conflict records from retrieval unchanged.

If conflicts are present, `required_disclosures[]` includes an explicit instruction to preserve them and not average them into consensus.

A prose renderer may explain a conflict, but may not erase its existence.

## 9. Caution preservation

Every claim's `cautions[]` remain attached to the synthesis unit.

If any caution exists, `required_disclosures[]` requires later prose to preserve claim cautions.

Examples include:

```text
symbolic parent image != literal parental biography
historical doctrine != scientific validation
qualified practitioner meaning != project-canonical doctrine
```

## 10. Registry guardrails

`guardrails[]` are copied from the retrieval bundle.

If present, the envelope requires the renderer not to assert registered non-admitted claims.

This is stronger than relying on a keyword filter because the negative boundary remains source-family specific and explicitly registered.

## 11. REFERENCE_ONLY provenance

If any selected claim uses:

```text
qualified_reference_only
mixed_claim_eligible_and_reference_only
```

then the envelope adds a required disclosure that `REFERENCE_ONLY` provenance is present and must remain explicitly qualified.

This does not change the source's admission status.

## 12. Route snapshot

The envelope stores the route snapshot:

```text
claim_types[]
tradition_tags_any[]
applies_to_all[]
l2_fact_refs[]
l3_policy_refs[]
```

It also preserves `resolution_provenance[]` from the query-resolution envelope.

This allows later review to answer both:

```text
why was this claim selected?
```

and:

```text
why was this route chosen from the user's question?
```

## 13. Synthesis status vocabulary

Research statuses include:

```text
ready_for_l5
no_supported_claims
blocked_resolution_not_resolved
blocked_bundle_schema
blocked_bundle_not_research_safe
blocked_query_mismatch
blocked_registry_mismatch
blocked_provenance_mismatch
blocked_provenance_incomplete
blocked_retrieval_status
blocked_empty_claims
blocked_claim_statement_missing
```

Only `ready_for_l5` authorizes a later prose renderer to synthesize from the included units.

`no_supported_claims` authorizes only a bounded statement that no supported claim matched the resolved route; it does not authorize fallback interpretation.

## 14. Required disclosures

Every envelope starts with:

```text
REFERENCE-ONLY / RESEARCH / NOT PRODUCTION-ROUTABLE
Source-backed claims and L5 synthesis must remain distinguishable.
```

Additional disclosures are appended when needed for:

```text
cautions
conflicts
non-admitted-claim guardrails
qualified REFERENCE_ONLY provenance
```

## 15. User-facing rendering boundary

This round does not freeze final prose wording.

A future renderer should consume only:

```text
synthesis_units
citation_units
conflicts
guardrails
required_disclosures
route_snapshot
resolution_provenance
synthesis_provenance
```

The renderer may improve readability, but it must not change evidence authority.

## 16. Regression targets

Initial regression covers:

```text
valid ready-for-L5 envelope
unresolved query block
query/registry mismatch block
L2/L3/claim/conflict provenance mismatch block
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

## 17. Non-goals

This contract does not establish:

```text
final user-facing writing style
scientific predictive validity
clinical validity
canonical tradition taxonomy
canonical weighting of competing claims
production citation UI
production routing
```

## 18. Current decision

The research pipeline now has an explicit integrity boundary:

```text
natural-language resolution
→ validated route
→ deterministic retrieval
→ provenance bundle
→ deterministic synthesis envelope
→ later prose
```

A prose layer no longer needs to infer which provenance constraints to preserve; the envelope carries them explicitly.

**Current state: REFERENCE-ONLY / RESEARCH / NOT PRODUCTION-ROUTABLE.**
