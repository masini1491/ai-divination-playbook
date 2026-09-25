# AST-P1-120 Special Pattern Policy Decision

Status: **PRODUCTION POLICY DECISION / NO INTERPRETATION AUTHORITY**

This note records the bounded product-policy choices used by `AST-P1-120`. It does not claim one universal astrology standard and does not claim exact compatibility with 唐綺陽 or any consumer product.

## Selected v1 geometry policy

```text
aspect_policy_id = pattern-aspects-yod-quintile-v1
orb_policy_id = pattern-aspect-orbs-yod-quintile-v1

conjunction = 0° ± 8°
sextile     = 60° ± 5°
quincunx    = 150° ± 3°
quintile    = 72° ± 2°
biquintile  = 144° ± 2°
```

The existing production major-aspect policy remains unchanged. These values exist only under the explicit special-pattern selector.

External evidence used as a policy input, not as universal authority:

- Astrodienst Astrowiki, **Quincunx**: identifies the 150° aspect and states an orb up to 3°.
- Astrodienst Astrowiki, **Quintile** and **Biquintile**: identify 72° / 144° and describe 2–3° orbs.
- The project deliberately chooses the conservative 2° end for quintile/biquintile v1.

## Selected v1 topology policy

```text
pattern_policy_id = special-pattern-topology-yod-stellium-grand-quintile-v1

Yod:
  3 conjunction-normalized vertices
  1 sextile base
  2 quincunx edges

Grand Quintile:
  5 conjunction-normalized vertices
  5 quintile perimeter edges
  5 biquintile diagonal edges
```

These templates follow the already reviewed E6 graph-topology research and remain deterministic geometry only.

## Selected Stellium v1 policy

```text
stellium_policy_id = stellium-planets-same-sign-span10-min3-v1

eligible objects:
  Sun, Moon, Mercury, Venus, Mars,
  Jupiter, Saturn, Uranus, Neptune, Pluto

minimum count = 3
maximum longitude span = 10°
sign boundary = all members must remain inside one zodiac sign
nodes / angles / lots = excluded from Stellium membership
```

Astrodienst Astrowiki describes a Stellium as a conjunction of more than two planets while noting that some astrologers require more than three, and says it may cross a house cusp while remaining within one sign. Because definitions vary, the repository does **not** claim this v1 policy is universal.

## Authority boundary

```text
qualified deterministic facts
→ explicit participant policy
→ explicit special aspect/orb policy
→ explicit topology / Stellium policy
→ deterministic pattern projection
```

No symbolic pattern meaning is admitted by this decision. Exact consumer/唐綺陽 compatibility remains unverified and must not be claimed.
