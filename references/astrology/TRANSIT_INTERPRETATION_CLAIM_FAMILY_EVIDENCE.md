# Transit Interpretation Claim-Family Evidence

Status: **REFERENCE-ONLY / RESEARCH / NOT PRODUCTION-ROUTABLE**

## Scope

This dossier connects already-tested L2 transit mechanics to a bounded L3/L4 interpretation contract for:

```text
transit → natal contacts
station emphasis
zodiac ingress
exact / applying / separating timing
retrograde repeated passages
```

The purpose is not to add another ephemeris engine. It is to prevent interpretation from outrunning the computed facts.

## Project execution/provenance sources

### `TRANSIT_TIMING_VALIDATION_RESULTS.md`

Existing research validated bounded station/exact-aspect timing architecture and records requested vs effective ephemeris backend. The documented local numeric results use Moshier fallback where `.se1` files were unavailable and must not be mislabeled as Swiss `.se1` / DE441 results.

### `TRANSIT_NATAL_INGRESS_TIMEZONE_RESULTS.md`

Existing research covers:

- transit to a synthetic fixed natal longitude target;
- repeated exact passages under retrograde motion;
- zodiac ingress identity;
- timezone/DST handling;
- fail-closed treatment of ambiguous/nonexistent local timestamps.

These are L2/provenance capabilities, not interpretations.

### Structured Astrology Fact architecture

The existing fact schema recognizes transit-to-natal aspect, ingress, station and exact-aspect event records. Interpretation must consume these facts rather than freely reconstructing them in language-model prose.

## Reference interpretation source

`wvanderen/astrology-skill@a9339b3c7151313530aa5002572c6612a2cfd59f`

Locator:

`references/reading_types/transit.md`

The reviewed module establishes a useful qualified interpretation pattern:

1. establish natal topic/promise before timing;
2. keep natal factor and active transit as separate steps before synthesis;
3. use exactness, applying/separating state, station and repeated passes as timing qualifiers when supplied;
4. treat station points as emphasis/time-window extenders rather than proof of a specific event;
5. preserve birth-time limits for angular/house contacts;
6. use windows and conditional language instead of event promises;
7. do not predict pregnancy, death, illness, accidents, legal outcomes, investments, job loss or relationship endings as transit-derived certainty.

This is a modern reference implementation and remains `REFERENCE_ONLY` for pair/timing interpretation authority.

## L2 → L3 → L4 boundary

```text
L2
computed transit fact
  - target object
  - natal target
  - aspect / ingress / station identity
  - exact time / orb / phase when available
  - engine/backend/timezone provenance

L3
explicit timing policy
  - orb
  - applying/separating semantics
  - station window policy
  - repeated-pass grouping
  - house/angle availability policy

L4
qualified symbolic interpretation
  - pressure / opportunity / emphasis / review / maturation / activation
  - never a guaranteed external event
```

No L4 claim may manufacture a missing L2 exact time, station, ingress, house contact or natal target.

## Station boundary

A station can legitimately be represented as a high-emphasis timing fact because the body lingers/reverses near a degree. The interpretation layer may describe an extended or emphasized symbolic window **only when the station/contact facts are supplied**.

It may not infer:

```text
station → guaranteed event
station → objectively stronger fate
station → exact outcome
```

## Retrograde repeated-pass boundary

Repeated exact passages can be grouped as a sequence when L2 facts establish the passes. Descriptions such as introduction/review/finalization are practitioner heuristics, not deterministic laws; they remain qualified and must not be used to invent pass dates.

## Natal-promise boundary

The research contract adopts a conservative rule:

```text
transit activates / emphasizes supplied natal topics
!=
transit creates an unsupported life topic from nothing
```

This reduces free-form overreach and keeps synthesis tied to sourced natal factors.

## Birth-time boundary

When birth time is unknown or unreliable:

- planet-to-planet transit contacts may remain usable when their natal positions are sufficiently stable;
- Asc/Desc/MC/IC, house-cusp and angular-house claims fail closed when unavailable;
- no sign-based substitute is allowed to masquerade as a missing house/angle fact.

## Retrieval preconditions

The companion registry declares:

```json
{"retrieval_preconditions":{"requires_l2_facts":true,"requires_l3_policy":true}}
```

Both calculated timing facts and an explicit interpretation/timing policy are therefore required before retrieval reaches interpretation claims.

## Non-goals

This family does not:

- select production orb values;
- establish a universal station-window duration;
- assign inevitable meaning to retrograde passes;
- guarantee concrete events;
- establish astrological scientific validity;
- alter production routing.

Companion registry:

`transit_interpretation_claim_family_registry.json`

Regression:

`test_transit_interpretation_registry.py`
