# Zi Wei Temporal-Context Interpretation Research v0

Authority：`REFERENCE-ONLY / RESEARCH CONTRACT / NOT PRODUCTION-ROUTABLE`

## Decision summary

```text
temporal context as one flat current-state label   REJECTED
natal / decadal / yearly / monthly / daily / hourly scopes  RESEARCH-ADOPTED
dynamic fact without boundary/profile provenance   INSUFFICIENT
natal claim auto-promoted to current prediction    FORBIDDEN
model-memory reconstruction of flow chart          FORBIDDEN
dynamic calculation runtime/provider               NOT ADMITTED
production authority                               false
```

## Scope model

Temporal interpretation is layered. The minimum research scopes are:

```text
natal_baseline
decadal
yearly
monthly
daily
hourly
```

Minute/second scopes and specialist cycle systems remain deferred unless separately admitted.

## Dynamic fact boundary

A temporal interpretation may consume only already-computed dynamic facts. A usable temporal fact packet must preserve:

```text
target timestamp / calendar identity
temporal scope
parent scope identity when applicable
calculation profile
boundary profile / flow-limit policy
sihua / auxiliary profile identities where applicable
engine/revision
fact state
provenance
```

`current year`, `this month`, or a bare flow-star label without boundary/profile identity is insufficient.

## Contiguous stack rule

Implementations such as iztro and ziwei-lite demonstrate a Decade → Year → Month → Day → Hour dynamic stack. The research contract adopts the **scope separation**, not either implementation as doctrine authority.

Interpretation may combine layers only when the required parent/child facts are present and compatible. A daily or hourly conclusion must not be fabricated when only yearly facts exist.

## Claim applicability

Current machine-readable first-layer claims use `temporal_scope = natal_baseline`. That means:

```text
natal claim exists
≠ automatically admitted decadal/yearly/monthly/daily/hourly prediction
```

A dynamic claim requires explicit temporal applicability or a separately admitted synthesis rule that states how a natal semantic baseline may constrain, but not substitute for, the dynamic claim.

## Boundary preservation

Temporal facts are especially sensitive to boundary/profile choices. The project already records that year and flow boundaries can differ by subsystem. Therefore retrieval must preserve those identities and may not silently coerce incompatible dynamic facts into one timeline.

## Cycle / flow stars

`MINOR_STAR_ADMISSION_TAXONOMY_V0.md` routes cycle/flow star families to this temporal owner. Their presence in an implementation does not admit them. They require temporal identity, placement provenance and source-normalized interpretation evidence before any L4 admission.

## Fail-closed behavior

```text
dynamic fact not computed
→ no flow interpretation

boundary/profile unresolved
→ preserve ambiguity / skip dependent claim

requested scope finer than available facts
→ do not infer missing lower-level layer

only natal claim available
→ do not render it as a current-event forecast

no admitted dynamic claim
→ no generic '流年吉凶' filler from model memory
```

## Research closure

```text
temporal-context interpretation responsibility = CLOSED — RESEARCH
scope taxonomy                           = CLOSED — RESEARCH
dynamic fact provenance contract         = CLOSED — RESEARCH
dynamic calculation runtime/provider     = NOT ADMITTED
dynamic claim corpus                     = NOT ADMITTED
executable retrieval/composition         = SEPARATE GATE
production authority                     = false
```

This closes the ChatGPT-side research continuation list without creating a Zi Wei production runtime or executable interpretation engine.
