# Planet / Sign Composable Semantics Evidence

Status: **REFERENCE-ONLY research evidence; bounded claims separately admitted through the production manifest**

## Goal

Close the production gap where deterministic Natal can supply a planet's admitted sign, including unknown-time invariant-only charts, but no source-backed semantic family exists to interpret that fact.

This work does **not** introduce fixed personality templates and does not claim scientific predictive or psychometric validity.

## External repository comparison

### wvanderen/astrology-skill @ a9339b3c7151313530aa5002572c6612a2cfd59f

Observed architecture:

- separate planet core modules under `references/planets/`;
- separate sign modules under `references/signs/`;
- sparse exact `planet_in_sign` modules only where a specific pair has been authored;
- retrieval guidance prefers the most specific implemented module, otherwise falls back to broader implemented modules;
- modules explicitly caution that a sign is a style/context rather than a complete placement or personality.

Adopted architectural lesson: compose a planet-function claim and sign-style claim from the same admitted object fact. Do not create 120 mandatory planet×sign templates.

Not adopted: the external prose corpus, its full doctrine, its reading workflow, or repository-level policy authority.

### theriftlab/immanuel-python @ 46190726ebe012f43c93d163745682e806975759

Observed architecture:

- chart objects serialize sign, longitude, house, motion and dignity as structured facts;
- interpretation prose is not the responsibility of the serialized chart object.

Adopted architectural lesson: preserve the fact/meaning boundary. The fact bundle continues to own the actual sign; semantic retrieval consumes that fact rather than recomputing or copying it.

Not adopted: AGPL code, schema, dignity scoring, or Swiss-Ephemeris dependency.

### kounkt/tri-horoscope @ 11318426c52c222eea108583ca45420c864825ca

Observed architecture:

- computation intentionally excludes interpretation and prose;
- unknown-time behavior is treated as a degraded fact mode with explicit boundaries.

Adopted architectural lesson: keep deterministic calculation/runtime separate from semantic claims and retain fail-closed behavior when a semantic family is unavailable.

Not adopted: its noon-based unknown-time implementation or any interpretation layer.

## Production design

```text
admitted natal object fact
  object_id = Sun
  sign = Pisces
        |
        +--> object_core applicability --> planet_function: Sun
        |
        +--> sign_style applicability  --> sign_style: Pisces
        |
        +--> object_sign_pair          --> only if a separately admitted pair-specific claim exists
```

The caller chooses only the applicability **scope**. The selector derives the actual object/sign values from the matched admitted fact. This prevents a caller from redirecting a Sun-in-Pisces fact to an Aries semantic claim.

North Node is deliberately excluded from `sign_style` binding because the current fact model classifies it as a point, not a planet, and no separate node semantic claim family has been admitted.

## Source/admission boundary

The external repository remains REFERENCE-ONLY in `SOURCE_REGISTRY.md`. The companion registry grants CLAIM_ELIGIBLE status only to the bounded, reviewed, normalized claims with immutable locators.

All claims retain cautions:

- symbolic interpretation is not scientific personality measurement;
- sign style is not a complete personality template;
- retrieval failure does not authorize model-memory invention;
- pair-specific meaning requires separate source admission.

Companion registry:

`planet_sign_composable_semantics_claim_family_registry.json`


## Corrective production selection boundary

The reviewed modules are a modern/contemporary reference implementation with blended source-local tags. The project taxonomy intentionally does **not** treat broad `modern` or `blended` labels as a canonical doctrine.

Therefore production use of this registry requires an explicit project semantic profile:

```text
semantic_profile = composable-symbolic-modern-v1
```

This profile is a bounded project synthesis setting, **not** a named astrology school and not a scientific/psychometric model. Every claim is additionally scoped with:

```text
historical_context_refs = [context:modern_contemporary]
```

A typed request that omits or mismatches the required profile fails closed. This prevents the registry from becoming a silent default tradition when the user has not selected an interpretive framework.
