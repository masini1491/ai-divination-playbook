# AST-P2-041 — Piecewise Chebyshev Five-Body Feasibility Contract

Status: **REFERENCE-ONLY / PROSPECTIVE RESEARCH CONTRACT / FROZEN BEFORE FIRST EXECUTION**

## Question

AST-P1-010 rejected the tested 10/20/40-day sampled-longitude Hermite variants under a prospectively frozen engineering gate. It did not test piecewise Chebyshev coefficients.

AST-P2-041 asks whether the same five E2 objects can instead use a bounded piecewise-Chebyshev longitude representation:

```text
Chiron
Ceres
Pallas
Juno
Vesta
```

This is a representation-feasibility experiment only. It cannot admit a production provider or extended object by itself.

## Oracle and coverage

Reuse the existing E2 research source contract:

```text
provider       NASA/JPL Horizons
center         500@399
EPHEM_TYPE     OBSERVER
QUANTITIES     31
APPARENT       AIRLESS
TIME_TYPE      UT
source grid    5 days
validation     existing 12 E2 F/H/V instants × 5 objects
window         1825-04-01 through 2350-10-01 UTC
```

The source collection may extend only far enough to complete a final full segment. Validation remains inside the declared window. Ordinary ChatGPT runtime must not depend on live Horizons.

## Frozen representation

Family:

```text
piecewise-chebyshev-wrapped-longitude-v0
```

For each object and segment:

1. acquire the 5-day Horizons apparent geocentric tropical ecliptic longitude samples;
2. locally unwrap longitude inside that segment;
3. map time to `x ∈ [-1,1]`;
4. fit the declared Chebyshev degree by ordinary least squares using all source samples in the segment;
5. store only float64 Chebyshev coefficients;
6. evaluate longitude from the selected segment and reduce modulo 360°;
7. derive speed analytically from the Chebyshev polynomial.

No segment blending, hidden fallback, post-result degree change, or post-result threshold change is allowed in this round.

## Frozen variants

| Variant | Degree | Segment width | Coefficients/query | Raw query bytes | Theoretical coefficient payload |
|---|---:|---:|---:|---:|---:|
| `cheb-d5-w45` | 5 | 45 d | 6 | 48 B | 1,023,840 B |
| `cheb-d7-w60` | 7 | 60 d | 8 | 64 B | 1,023,680 B |
| `cheb-d7-w80` | 7 | 80 d | 8 | 64 B | 768,000 B |
| `cheb-d7-w120` | 7 | 120 d | 8 | 64 B | 512,000 B |

The first two deliberately spend nearly the same 1 MiB budget using different degree/segment trade-offs.

## Frozen engineering gate

The first five gates are inherited unchanged from AST-P1-010:

| Metric | Gate |
|---|---:|
| longitude p95 | ≤ 10 arcsec |
| longitude max | ≤ 30 arcsec |
| speed max | ≤ 0.001 deg/day |
| float64 coefficient payload | ≤ 1,048,576 bytes |
| one-query raw coefficient payload | ≤ 64 bytes |
| boundary longitude jump max | ≤ 30 arcsec |
| boundary speed jump max | ≤ 0.001 deg/day |

The last two gates are added prospectively because an independently fitted piecewise representation must not hide discontinuities at segment boundaries.

These remain research feasibility thresholds, not Astrology production numeric admission tolerances.

## Validation and interpretation

Direct Horizons truth at the 12 existing E2 fixtures remains the accuracy oracle. Truth speed uses the existing ±1 hour central finite difference contract.

Report for every variant:

- binary coefficient bytes and digest;
- longitude p95 / max;
- speed max;
- boundary longitude / speed jump maxima;
- worst object + fixture/boundary;
- observed Horizons signature;
- failed gate list.

```text
all frozen gates pass
→ Chebyshev architecture feasibility PASS
→ AST-P2-040 may proceed to a separate production-admission review
→ production admission is still NOT automatic

one or more gates fail
→ that variant FAILS

all declared variants fail
→ close this declared Chebyshev candidate family as negative research
→ do not infer bounded SPK or every possible Chebyshev design is impossible
```

No gate may be widened after observing results.
