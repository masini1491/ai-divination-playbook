# Zi Wei Executable Retrieval / Composition v0

Authority：`REFERENCE-ONLY / RESEARCH EXECUTABLE / NOT PRODUCTION-ROUTABLE`

## Admitted executable scope

This Stage implements the smallest deterministic bridge from the currently admitted machine-readable first layer to an L5 interpretation frame.

```text
inputs:
  research FactPacket subset
  interpretation_profile
  temporal_scope
  explicit fact tokens
  optional subject/source gates

claim corpus:
  Batch 1 major stars
  Batch 2 major stars
  Twelve Palaces v0
  = 52 admitted first-layer L4 claims

outputs:
  selected claim records
  explicit omissions
  registered conflict identities
  specificity ordering
  provenance-preserving L5 frame
```

It does not render user-facing doctrine prose and does not create new L4 claims.

## Matching contract

A claim is eligible only when:

1. registry remains `production_routable=false`;
2. interpretation profile matches;
3. `adoption_state = RESEARCH_CLAIM_ELIGIBLE`;
4. enabled source gate, when supplied, intersects the claim source refs;
5. `temporal_scope` matches exactly;
6. all machine-readable `requires[]` facts are present;
7. no `forbids[]` fact is present.

Missing facts cause omission, not inference.

## Specificity

Current first-layer deterministic order:

```text
star_conditional
> palace_conditional
> star_core
> palace_domain
> methodology
```

This is only an ordering among already eligible claims. It does not override source/tradition policy and does not manufacture star×palace overrides.

## Composition boundary

The composer emits an L5 frame containing selected claim IDs grouped by subject plus conflict and omission metadata.

```text
star claim + palace claim
→ may coexist in one L5 frame
→ does NOT become a new sourced star×palace L4 claim
```

The prose renderer remains outside this executable Stage.

## Fail-closed boundaries

```text
dynamic scope != natal_baseline → no current first-layer claim selected
missing required brightness/dignity fact → dependent claim skipped
missing admitted Four-Transformation claim → no generic transformation outcome
missing auxiliary/minor-star claim → no model-memory substitution
source gate excludes authority → claim skipped
registered conflict → preserved in output
```

## Validation

The executable contract has deterministic unit coverage for:

- star core/conditional selection;
- missing-required-fact omission;
- star + palace coexistence without Cartesian L4 invention;
- conflict preservation;
- dynamic-scope fail closed;
- source gating.

## Boundary

This executable research component does **not** create:

- a deterministic Zi Wei chart calculation runtime/provider;
- a dynamic claim corpus;
- a complete contextual claim corpus;
- production `ZIWEI.md`;
- `METHOD_ROUTING.md` integration;
- ordinary auto-routing;
- scientific/predictive-validity claims;
- production admission.
