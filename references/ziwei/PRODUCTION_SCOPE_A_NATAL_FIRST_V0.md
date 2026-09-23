# Zi Wei Production Scope A — Bounded Natal First Layer v0

Authority：`PRODUCT-SCOPE DECISION / READINESS CONTRACT / NOT PRODUCTION ADMISSION`

## Decision

The selected minimum product scope is:

```text
A. bounded natal first layer only
```

This decision fixes the minimum target used by production-readiness analysis. It does not itself admit a production runtime, renderer, method owner or ordinary route.

## Included interpretation scope

```text
temporal scope              = natal_baseline
major-star subjects         = 14
major-star claims           = 28
palace subjects             = 12
palace claims               = 24
combined admitted claims    = 52
retrieval/composition       = bounded first-layer behavior
conflict handling           = preserve registered conflicts
uncertainty/safety          = bounded delivery contract
```

The 52 admitted claims are the complete interpretation corpus required by Scope A. G3 is therefore satisfied for this product scope.

## Required calculation facts

Scope A requires only deterministic natal facts needed to support the admitted first layer:

- normalized birth/calendar provenance;
- natal Life/Body and twelve-palace geometry needed by the chart packet;
- Five-Element Bureau and major-star placement needed to derive the 14 major-star natal placements;
- structural topology required by the admitted first-layer retrieval contract;
- explicit calculation/profile identity and provenance.

A future implementation may calculate additional facts, but those facts do not become Scope-A interpretation authority automatically.

## Explicitly out of Scope A

The following are not production blockers for Scope A:

- project-wide brightness table/profile;
- brightness-conditioned interpretation;
- auxiliary/minor-star interpretation corpus;
- broader star×palace contextual claim families;
- Four-Transformation interpretation beyond the admitted first-layer dependency boundary;
- decadal/yearly/monthly/daily/hourly interpretation;
- dynamic calculation/runtime;
- dynamic claim corpus.

If a future product requirement needs one of these capabilities, it must reopen the corresponding gate and move beyond Scope A.

## Fail-closed behavior

Scope A must not substitute unsupported broader behavior:

```text
brightness unavailable      → no brightness-conditioned claim
auxiliary context present   → no unadmitted auxiliary interpretation
dynamic request             → unsupported scope; no natal fallback
unadmitted contextual rule  → omit; no model-memory fill
ambiguous natal fact        → preserve ambiguity / omit dependent claim
```

## Remaining production blockers under Scope A

After this scope decision:

```text
G1 natal calculation authority                 BLOCKED
G2 production schema candidates                RESEARCH-CLOSED
G3 required interpretation coverage            SATISFIED FOR SCOPE A
G4 retrieval/composition                       RESEARCH-CLOSED
G5 executable behavioral validation            RESEARCH-CLOSED
G6 uncertainty/safety delivery contract         RESEARCH-CLOSED
G7 production binding + explicit admission      BLOCKED
G8 ordinary routing                             BLOCKED
```

G1 must be narrowed to a natal-only deterministic runtime/provider with explicit profile/provenance identity. It must not be blocked by brightness or dynamic capability that Scope A does not consume.

G7 remains separate: research closures must be bound and validated against the admitted natal runtime before production admission.

G8 remains last: `ZIWEI.md`, `METHOD_ROUTING.md`, `PLAYBOOK_INDEX.json` and unspecified-user routing cannot precede production admission.

## Reopen triggers

Scope A is reopened only if:

- the user/project explicitly selects Scope B or C;
- admitted first-layer behavior is shown to require a currently excluded fact family;
- production validation reveals a material dependency not represented here;
- a source/profile correction changes a required natal calculation fact.

Do not expand scope merely because additional Zi Wei features are available.
