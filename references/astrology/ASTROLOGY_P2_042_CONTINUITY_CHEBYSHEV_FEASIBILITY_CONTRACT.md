# AST-P2-042 — Continuity-Constrained / Overlap Chebyshev Feasibility Contract

Status: **REFERENCE-ONLY / PROSPECTIVE RESEARCH CONTRACT / FROZEN BEFORE FIRST EXECUTION**

## Why this experiment exists

AST-P2-041 found a narrow failure mode:

- D5/W45, D7/W60 and D7/W80 passed the frozen fixture longitude, fixture speed, artifact-size, query-size and boundary-longitude gates;
- all three failed only the frozen segment-boundary speed-continuity gate;
- the rejected topology was independently fitted Chebyshev segments with a hard switch and no continuity constraint.

AST-P2-042 tests whether the boundary failure can be removed **without** increasing ordinary query payload beyond the existing 64-byte gate.

Runtime two-segment blending is deliberately excluded from this round because it would require 96 bytes for D5/W45 and 128 bytes for D7/W60.

## Source and scope

Reuse the same E2 research authority and objects:

```text
NASA/JPL Horizons API / observer ephemeris
center       500@399
QUANTITIES   31
APPARENT     AIRLESS
TIME_TYPE    UT

Chiron
Ceres
Pallas
Juno
Vesta
```

Coverage and direct fixture validation remain:

```text
1825-04-01 through 2350-10-01 UTC
5-day source grid
12 existing E2 F/H/V instants × 5 objects
fixture speed truth = direct Horizons t-1h / t+1h central difference
```

The complete in-window 5-day source grid is additionally used as a longitude-only anti-drift validation surface.

## Frozen candidates

| Candidate | Mechanism | Degree | Core width | Build-time padding | Runtime coeffs/query | Raw query |
|---|---|---:|---:|---:|---:|---:|
| `c1-cheb-d5-w45` | sequential equality-constrained LS; left value + speed fixed to prior segment end | 5 | 45 d | 0 | 6 | 48 B |
| `c1-cheb-d7-w60` | sequential equality-constrained LS; left value + speed fixed to prior segment end | 7 | 60 d | 0 | 8 | 64 B |
| `overlap-cheb-d5-w45-p10` | overlap-trained OLS; hard core switch | 5 | 45 d | ±10 d | 6 | 48 B |
| `overlap-cheb-d7-w60-p15` | overlap-trained OLS; hard core switch | 7 | 60 d | ±15 d | 8 | 64 B |

### C1 candidate rule

The first segment uses ordinary least squares. Each subsequent segment is fit to its core source samples while imposing exact left-boundary constraints:

```text
P_new(-1)        = P_previous(+1)
dP_new/dt(-1)    = dP_previous/dt(+1)
```

The constraints are part of the stored coefficients. Runtime still evaluates one segment only.

### Overlap-trained candidate rule

The polynomial coordinate remains defined by the core segment `[-1,1]`, but build-time least squares may include the declared neighboring 5-day samples outside the core interval. Runtime still uses one core segment with a hard switch and stores no overlap-specific payload.

## Frozen gates

Inherited unchanged from AST-P2-041:

| Metric | Gate |
|---|---:|
| fixture longitude p95 | ≤ 10 arcsec |
| fixture longitude max | ≤ 30 arcsec |
| fixture speed max | ≤ 0.001 deg/day |
| coefficient binary payload | ≤ 1,048,576 bytes |
| one-query raw coefficient payload | ≤ 64 bytes |
| boundary longitude jump max | ≤ 30 arcsec |
| boundary speed jump max | ≤ 0.001 deg/day |

New prospective anti-drift gates:

| Metric | Gate |
|---|---:|
| full 5-day source-grid longitude p95 | ≤ 10 arcsec |
| full 5-day source-grid longitude max | ≤ 30 arcsec |

These are engineering-feasibility gates, not production numeric-admission tolerances.

## Completion rule

For every frozen variant report:

- coefficient payload bytes + digest;
- fixture longitude p95/max;
- fixture speed max;
- full source-grid longitude p95/max;
- boundary longitude/speed jump maxima;
- worst fixture/grid/boundary object and time;
- observed Horizons signature;
- exact failed-gate list.

```text
one complete variant passes every frozen gate
→ AST-P2-042 architecture feasibility PASS
→ AST-P2-040 may move to a separate production-admission review
→ no automatic production admission

all four variants fail
→ reject only this declared single-segment-query continuity/overlap family
→ bounded SPK remains unevaluated
```

No candidate parameter or gate may be changed after first execution.
