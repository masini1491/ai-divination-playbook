# Astrology Query Resolution / Routing Contract Draft

Status: **REFERENCE-ONLY / RESEARCH DRAFT / NOT PRODUCTION-ROUTABLE**

Schema name: `astrology_query_resolution`

Schema version: `0.1.0-research`

This contract defines the boundary between natural-language question understanding and deterministic Astrology interpretation retrieval. It does not authorize free-form astrology interpretation, production routing, private-motive inference, clinical claims, or high-stakes prediction.

## 1. Pipeline

```text
user question
→ query-resolution stage
→ validated query-resolution envelope
→ deterministic interpretation-claim selector
→ retrieval provenance bundle
→ L5 synthesis envelope
→ user-facing prose renderer
```

The query-resolution stage may use language understanding, but it must not directly select source claims or generate astrology meanings.

Its only authority is to produce a bounded, auditable routing decision.

## 2. Separation of responsibilities

### Query resolver owns

```text
question intent classification
claim-family / registry target
claim-type requirements
tradition scope
applicability scope
whether L2 facts are required
whether L3 policy is required
unresolved material slots
risk classification
routing provenance
```

### Query resolver does not own

```text
astronomical calculation
L1/L2 fact invention
orb-policy invention
source admission upgrade
L4 claim invention
conflict resolution by averaging
clinical diagnosis
private-motive assertions
predictive certainty
final L5 prose
```

## 3. Envelope identity

Required research envelope:

```text
schema_name = astrology_query_resolution
schema_version = 0.1.0-research
record_status = REFERENCE-ONLY
production_routable = false
```

Candidate top-level fields:

```text
query_id
user_question
resolution_status
question_risk_class
target_registry_record_id
route
routing_assumptions[]
unresolved_slots[]
clarification_question
unsupported_reason
reference_only_justification
```

## 4. Resolution statuses

```text
resolved
needs_clarification
unsupported
```

### `resolved`

May proceed to deterministic retrieval only when all material routing fields are sufficiently grounded and no prohibited risk class applies.

### `needs_clarification`

Used when a material slot is unresolved and choosing a value would change claim-family, tradition, applicability, or required fact/policy context.

Examples:

```text
which tradition?
natal or transit?
which transit direction?
which chart configuration?
```

A `needs_clarification` envelope must not emit an executable route.

### `unsupported`

Used when the requested use is outside this research contract, including prohibited high-stakes or private-state inference.

An unsupported request must not be converted into a weaker-looking astrology route merely to produce an answer.

## 5. Risk classification

Research vocabulary:

```text
normal_symbolic
private_motive_inference
clinical_or_diagnostic
high_stakes_external_outcome
```

Only `normal_symbolic` may use:

```text
resolution_status = resolved
```

Examples that must not resolve into astrology retrieval under this contract include requests to establish:

```text
another person's hidden/private motives as fact
clinical diagnosis or trauma as fact
pregnancy / death / illness outcomes
legal outcomes
investment outcomes
guaranteed relationship outcomes
guaranteed external events
```

This is a routing boundary, not a scientific-validity claim.

## 6. Deterministic route payload

When `resolution_status = resolved`, `route` must be an executable query specification compatible with `retrieve_interpretation_claims.py`:

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

The route must preserve the same `query_id` as the resolution envelope.

## 7. Material uncertainty fails closed

If L2 facts are required:

```text
requires_l2_facts = true
→ l2_fact_refs[] must be non-empty
```

If L3 policy is required:

```text
requires_l3_policy = true
→ l3_policy_refs[] must be non-empty
```

A resolver must not invent a fact reference or policy reference to avoid clarification.

Likewise, a material unresolved semantic slot belongs in:

```text
unresolved_slots[]
```

and the resolution must become `needs_clarification` rather than silently defaulting.

## 8. Routing provenance

Every non-empty semantic route field must have an auditable `routing_assumptions[]` entry.

Current semantic route fields:

```text
claim_types
tradition_tags_any
applies_to_all
```

Candidate assumption shape:

```text
field
basis
evidence_spans[]
evidence_refs[]
```

Candidate basis vocabulary:

```text
user_text
upstream_context
research_fixture
research_policy
```

### `user_text`

The evidence span must occur in the original `user_question` text.

The validator can verify literal span presence. It does not claim that the semantic mapping is objectively correct; that remains an upstream language-understanding judgment.

### `upstream_context`

Used for facts or policy references already resolved by an earlier deterministic/context stage. It requires explicit `evidence_refs[]`.

### `research_fixture`

Used only in synthetic/research regression cases.

### `research_policy`

Used when a routing decision is an explicit research policy rather than a user semantic claim.

## 9. No model-memory fallback

If the resolver cannot ground a material route decision, it must not use general model memory as a hidden authority.

Allowed outcomes are:

```text
resolved with provenance
needs_clarification
unsupported
```

Not allowed:

```text
silently invent tradition
silently choose natal vs transit
silently choose an orb policy
silently add a source family
silently convert an unsupported private-motive request into a symbolic claim
```

## 10. Registry target

A resolved envelope must name exactly one:

```text
target_registry_record_id
```

The deterministic validator may be supplied with the currently available registry IDs and must reject a route to an unavailable registry.

This keeps claim-family routing explicit rather than allowing a selector to scan unrelated registries opportunistically.

## 11. REFERENCE_ONLY evidence opt-in

The default route is:

```text
allow_reference_only_qualified = false
```

If the resolver enables qualified `REFERENCE_ONLY` evidence, the envelope must include:

```text
reference_only_justification
```

This justification documents the research reason for widening evidence admission. It does not upgrade the source to project doctrine.

The downstream selector still requires the claim itself to remain qualified / tradition-bounded.

## 12. Clarification contract

A `needs_clarification` envelope requires:

```text
unresolved_slots[] != []
clarification_question
route = null | omitted
```

The clarification should target only the material ambiguity needed to continue.

The contract does not require clarification for every optional preference. It is specifically for ambiguity that materially changes routing or claim eligibility.

## 13. Unsupported contract

An `unsupported` envelope requires:

```text
unsupported_reason
route = null | omitted
```

It may still preserve the original user question and risk classification for auditability, but it must not create a retrieval path.

## 14. Privacy / repository fixtures

Runtime query envelopes may necessarily contain the user's question. Repository regression fixtures should remain synthetic, fictional, or otherwise non-identifying.

Do not commit real private natal data or private user conversations as regression fixtures.

## 15. Query-resolution validator

`validate_astrology_query_resolution.py` checks only deterministic contract invariants, including:

```text
schema identity
REFERENCE-ONLY / production guard
resolution status
risk-class gating
route/query identity
known target registry when catalog supplied
L2/L3 preconditions
REFERENCE_ONLY opt-in justification
unresolved-slot rules
clarification / unsupported requirements
routing-assumption shape
literal user-text span presence
upstream-context reference presence
semantic route provenance coverage
```

It does not validate whether the natural-language semantic interpretation itself is correct.

## 16. L5 boundary

A successful route does not authorize free-form synthesis.

The downstream sequence remains:

```text
validated resolution
→ deterministic selector
→ retrieval provenance bundle
→ deterministic synthesis envelope
→ L5 prose constrained by that envelope
```

Any user-facing semantic assertion must be traceable to a registered claim or clearly labeled as synthesis. Registered conflict, caution, source-admission status, and guardrails must not be dropped.

## 17. Regression targets

Initial research regression should cover at least:

```text
valid symbolic route
missing L2 fact
missing L3 policy
unknown registry
ungrounded tradition/applicability
invalid user-text evidence span
REFERENCE_ONLY opt-in without justification
needs-clarification path
private-motive request blocked from resolved routing
clinical/diagnostic request blocked from resolved routing
```

## 18. Non-goals

This contract does not establish:

```text
production NLU quality
canonical astrology intent taxonomy
canonical tradition taxonomy
scientific predictive validity
clinical validity
truth of source interpretations
full privacy detection
production user-facing wording
```

## 19. Promotion gap

After query-resolution and L5 envelope regression, remaining gaps include:

```text
broader claim-family routing fixtures
explicit tradition taxonomy
user-facing citation renderer
human-readable L5 wording regression
cross-family conflict regression
production owner / routing admission
```

**Current state: REFERENCE-ONLY / RESEARCH / NOT PRODUCTION-ROUTABLE.**
