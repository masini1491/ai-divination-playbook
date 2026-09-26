# AST-P2-041 — Piecewise Chebyshev Five-Body Feasibility Result

Status: **REFERENCE-ONLY / RESEARCH COMPLETE / CANDIDATE FAMILY REJECTED / NOT PRODUCTION-ADMITTED**

## Execution identity

```text
pre-execution frozen contract  2ac7a91e743fd460a639095d12dd470d72a51634
temporary non-merge PR          #236
probe head                      47e5b052a22b2d9dd59dcf3af09b77364106b523
Validate Playbook               run #832 / 36216994624
validate job                    108334821215
unit tests                      PASS
structural checker              PASS
Horizons signature              NASA/JPL Horizons API / 1.2
```

The frozen thresholds were not widened after observing results.

## Result

| Variant | Binary bytes | Lon p95 | Lon max | Fixture speed max | Boundary lon jump | Boundary speed jump | Result |
|---|---:|---:|---:|---:|---:|---:|---|
| D5 / 45 d | 1,023,840 | 0.737″ | 1.408″ | 0.000293 °/d | 2.075″ | 0.001493 °/d | FAIL |
| D7 / 60 d | 1,023,680 | 0.892″ | 1.195″ | 0.000216 °/d | 0.369″ | 0.002457 °/d | FAIL |
| D7 / 80 d | 768,000 | 1.956″ | 2.674″ | 0.000424 °/d | 3.216″ | 0.003652 °/d | FAIL |
| D7 / 120 d | 512,000 | 2.830″ | 13.856″ | 0.003374 °/d | 52.138″ | 0.018494 °/d | FAIL |

Frozen gates:

```text
longitude p95            <= 10 arcsec
longitude max            <= 30 arcsec
fixture speed max        <= 0.001 deg/day
binary payload           <= 1,048,576 bytes
single-query raw payload <= 64 bytes
boundary longitude jump  <= 30 arcsec
boundary speed jump      <= 0.001 deg/day
```

No variant passed every gate.

## Main finding

The most important result is narrower than "Chebyshev failed".

D5/W45, D7/W60 and D7/W80 all passed:

- fixture longitude p95/max;
- fixture speed max;
- coefficient payload size;
- one-query coefficient payload;
- boundary longitude continuity.

They failed **only** the prospectively frozen boundary-speed continuity gate.

Therefore the tested polynomial approximation is already sufficiently accurate at the 60 validation rows. The rejected architecture is specifically:

```text
independently fitted segments
+ hard segment switch
+ no continuity constraint / no blending
```

The 120-day segment also becomes too coarse for the frozen speed and boundary-longitude gates.

## Decision

```text
piecewise-chebyshev-wrapped-longitude-v0
→ NO PASSING VARIANT
→ reject this independent-segment candidate family
→ AST-P2-040 remains blocked
```

This does **not** establish that Chebyshev coefficients in general are infeasible. A separately declared continuity-constrained or overlap/blended Chebyshev representation may address the observed failure mode, but it requires a new prospective contract and must not reuse this result as if it had already passed.

Bounded SPK and multi-epoch osculating representations also remain unevaluated.

## Authority boundary

No production provider, calculation fact, ordinary-runtime network dependency, numeric admission tolerance, aspect participation or interpretation semantics are changed by this result.
