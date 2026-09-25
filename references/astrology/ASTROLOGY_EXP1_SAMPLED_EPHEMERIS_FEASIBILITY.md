# AST-P1-010 — Sampled Five-Body Ephemeris Feasibility Result

Status: **REFERENCE-ONLY / RESEARCH COMPLETE / CANDIDATE REJECTED / NOT PRODUCTION-ADMITTED**

## 1. Question

AST-P1-010 asks whether the five E2 bodies can use a compact local representation without making a live third-party API an ordinary ChatGPT runtime dependency:

```text
Chiron
Ceres
Pallas
Juno
Vesta
```

This experiment evaluates one listed candidate family:

```text
sampled wrapped longitude
+ bounded local interpolation
```

It does **not** evaluate bounded SPK excerpts, piecewise Chebyshev storage or multi-epoch osculating elements.

## 2. Research execution

Temporary non-merge probe:

```text
PR                 #181
head               1e4c8e64d7eec1ec86b0af8e9db4d3d0ba3698eb
workflow run       36086788978
validate job       107920351813
merged             NO
```

The temporary test used NASA/JPL Horizons only inside GitHub Actions research execution. It was closed without merge after evidence collection.

Source contract:

```text
provider           NASA/JPL Horizons
API signature      NASA/JPL Horizons API / 1.2
center             500@399
EPHEM_TYPE         OBSERVER
QUANTITIES         31
APPARENT           AIRLESS
TIME_TYPE          UT
```

The candidate runtime representation itself requires no live network.

## 3. Candidate representation

```text
id                 sampled-wrapped-longitude-hermite-v0
source grid        10 days
tested spacing     10 / 20 / 40 days
lookup window      4 samples for one object
interpolation      cubic Hermite
slope estimate     centered finite difference from the same local four-sample window
coverage           1825-04-01 through 2350-10-01 UTC
validation         12 fixed E2 F/H/V instants × 5 objects = 60 rows / variant
```

This is not a Keplerian propagation shortcut. Chiron is measured and reported separately from direct Horizons samples, so the experiment does not hide its perturbation sensitivity behind a one-epoch orbital model.

## 4. Frozen engineering-feasibility gate

The following thresholds were encoded in the temporary probe **before first execution**:

| Metric | Frozen gate |
|---|---:|
| longitude p95 | ≤ 10 arcsec |
| longitude max | ≤ 30 arcsec |
| speed max | ≤ 0.001 deg/day |
| float64 artifact payload | ≤ 1,048,576 bytes |
| one-query raw sample payload | ≤ 64 bytes |

These are feasibility gates only. They are **not** Astrology production numeric admission tolerances.

No threshold was widened after the result.

## 5. Results

| Spacing | Binary payload | Canonical JSON | Lon p95 | Lon max | Speed p95 | Speed max | Result |
|---|---:|---:|---:|---:|---:|---:|---|
| 10 d | 767,760 B | 1,110,382 B | 4.340″ | 25.284″ | 0.00101448 °/d | 0.00207455 °/d | FAIL |
| 20 d | 383,880 B | 555,210 B | 28.960″ | 204.040″ | 0.00773924 °/d | 0.01235967 °/d | FAIL |
| 40 d | 191,960 B | 277,711 B | 961.745″ | 3091.834″ | 0.02064801 °/d | 0.04072932 °/d | FAIL |

All variants use 32 raw bytes for the four float64 lookup samples for one object. The measured compact JSON lookup envelope was 74–75 bytes.

### Closest candidate: 10-day spacing

10-day spacing satisfied:

- binary artifact size;
- raw query payload;
- global longitude p95;
- global longitude max.

It failed the frozen speed gate:

```text
required speed max <= 0.001 deg/day
observed speed max  = 0.0020745450001214694 deg/day
worst object        = Vesta
worst fixture       = E2-F03
```

Per-object maximums for the 10-day candidate:

| Object | Longitude max | Speed max |
|---|---:|---:|
| Chiron | 1.330″ | 0.000246475 °/d |
| Ceres | 4.968″ | 0.000713005 °/d |
| Pallas | 25.284″ | 0.002003345 °/d |
| Juno | 6.526″ | 0.001895499 °/d |
| Vesta | 3.951″ | 0.002074545 °/d |

The worst longitude row was Pallas at E2-F01: 25.284″.

## 6. Decision

```text
sampled-wrapped-longitude-hermite-v0
→ evaluated under the frozen bounded E2 fixture set
→ NO PASSING 10/20/40-day variant
→ REJECT for current feasibility gate
```

This is a valid negative research result. It does not justify changing the gate after observing the data.

The result also does not establish that every bundled-ephemeris design is infeasible. The other AST-P1-010 candidate families were not evaluated here:

```text
bounded SPK excerpt
piecewise Chebyshev coefficients
multi-epoch osculating elements
```

They remain unevaluated research alternatives, not implied follow-up commitments and not production-admitted capabilities.

## 7. Authority boundary

```text
this report + astrology_exp1_sampled_ephemeris_feasibility.json
→ research evidence only

NASA/JPL Horizons network access
→ build/research authority used by temporary Actions probe only

ordinary ChatGPT Astrology runtime
→ no new network dependency

production calculation admission
→ unchanged / NOT GRANTED
```

Machine-readable evidence: `astrology_exp1_sampled_ephemeris_feasibility.json`.

