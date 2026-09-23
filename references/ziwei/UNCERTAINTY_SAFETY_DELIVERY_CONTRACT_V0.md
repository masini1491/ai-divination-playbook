# Zi Wei Uncertainty / Safety Delivery Contract v0

Authority：`REFERENCE-ONLY / DELIVERY CONTRACT CANDIDATE / NOT PRODUCTION ADMISSION`

## Purpose

Define what a future Zi Wei renderer must disclose or suppress when evidence is incomplete, profile-specific, conflicted or high-impact. This contract governs delivery semantics; it does not create doctrine, chart facts, or production routing.

## Evidence states

Allowed delivery states:

```text
source_backed
project_adopted
profile_specific
conflicted
insufficient
case_inference_only
```

A claim may carry more than one state. The renderer must not convert these qualitative states into invented numeric confidence.

## Required disclosures

A frame must expose a bounded disclosure when any material condition applies:

- required chart fact is unknown, not computed or ambiguous;
- profile-sensitive fact lacks admitted profile identity;
- requested temporal scope is unsupported;
- relevant claim family is unadmitted;
- registered conflict is unresolved;
- selected interpretation is explicitly profile/tradition-specific;
- evidence is case-inference-only.

Omission disclosure should explain the missing dependency category without filling the gap from model memory.

## Conflict delivery

Registered conflicts must be:

1. preserved as separate perspectives; or
2. resolved only by an explicit admitted profile/source policy.

Forbidden:

- averaging traditions into a new compromise;
- silently selecting the more dramatic outcome;
- hiding the conflict while presenting certainty.

## Certainty boundary

The renderer may summarize admitted claims, but must not upgrade:

```text
tendency → certainty
conditional claim → guaranteed event
source tradition → objective truth
research candidate → production fact
symbolic/divination interpretation → scientific prediction
```

## High-impact safety classes

The following require bounded, non-deterministic delivery:

```text
health / disease / death
legal / imprisonment
financial ruin / guaranteed wealth
pregnancy / fertility
violence / severe harm
other irreversible high-impact outcomes
```

Historical/source claims may remain in provenance. Ordinary user-facing prose must not present them as diagnosis, guaranteed occurrence, professional advice, or deterministic fate.

## Delivery action candidate

For each frame/claim, a future renderer may apply:

```text
ALLOW
ALLOW_WITH_PROFILE_DISCLOSURE
ALLOW_WITH_UNCERTAINTY_DISCLOSURE
PRESENT_CONFLICT_SEPARATELY
OMIT_INSUFFICIENT
BOUND_HIGH_IMPACT
BLOCK_UNSUPPORTED_SCOPE
```

The strongest applicable boundary wins. `ALLOW` never overrides a safety/conflict/insufficiency condition.

## Minimum output trace

A future rendered response should be traceable back to:

- interpretation profile;
- temporal scope;
- selected claim IDs;
- material omitted dependencies;
- conflict IDs;
- evidence states;
- safety actions;
- production-authority state.

User-facing prose need not dump raw IDs unless trace/debug mode is requested, but the frame must retain them.

## No scientific-validity implication

The renderer must not imply that project admission, deterministic calculation, source agreement, user-perceived fit, benchmark behavior or CI success demonstrates scientific predictive validity.

## Production boundary

This contract is a research/readiness closure only. Binding it to a production renderer, API response or ordinary routing requires separate production implementation and admission.
