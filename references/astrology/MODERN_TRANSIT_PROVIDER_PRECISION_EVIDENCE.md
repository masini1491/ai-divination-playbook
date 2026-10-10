# Modern-Range Transit Provider Precision Evidence

Status: **REFERENCE-ONLY / AST-P0-003 CORRECTNESS EVIDENCE / NOT INTERPRETATION AUTHORITY**

Tested playbook baseline:

```text
masini1491/ai-divination-playbook@be92edac39675ec76213697a22670bc370395063
```

Purpose: determine the minimum safe remediation after AST-P1-280 showed that two admitted/validated 2026 transit exact-event cases were materially farther from JPL DE440S under the portable Astronomy Engine model than under host-native PySwissEph/MOSeph.

## Oracle provenance

The independent oracle is the same NASA/JPL DE440S binary path documented by `JPL_DE440S_TRANSIT_ORACLE_ADJUDICATION.md`:

```text
external engine: ffalcinelli/astroceleste-engine@622693a0e49a622f955c3a298d7f09ed650e1382
GitHub Pages workflow run: 37898071384
artifact id: 11601197376
artifact digest: sha256:0c95147d5fa44c977f7aa0c435db6c2468ac9b5fff92f1998dfc7c1d31d557cc

kernel: ephemeris/de440s-1950-2050.bsp
size: 10,890,240 bytes
sha256: 06524f5fc8c3ff2f91b841936c80363d54cfd6d261e8cd7642e25d521ab88165
```

The external engine's SPK evaluation is independently checked against `jplephem`; its apparent reduction is checked stage-by-stage against Skyfield 1.55. The comparison coordinate contract is apparent geocentric true ecliptic longitude of date.

## Root-cause localization

The disputed Venus and Mercury instants were recomputed with the exact-main Astronomy Engine path while toggling aberration and ecliptic conversion variants.

The material residual persists before/after the correction-layer comparison. The evidence does **not** support a root-search, aberration, or ecliptic-of-date conversion defect as the primary source.

The portable dependency itself documents an engineering accuracy target of approximately ±1 arcminute and uses truncated VSOP87 planetary series. Therefore:

```text
0.5-second transit root tolerance
≠
0.5-second independent astronomical accuracy
```

The current root solver can converge tightly inside a planetary model whose absolute longitude differs by arcseconds to tens of arcseconds from DE440S.

## 2026 pointwise benchmark

Design:

```text
37 UTC timestamps in 2026
× Sun..Pluto
= 370 apparent geocentric tropical longitude comparisons
```

Results versus DE440S:

| Metric | Astronomy Engine 2.1.19 | host PySwissEph/MOSeph |
|---|---:|---:|
| maximum error | 20.462″ | 1.328″ |
| p95 error | 11.968″ | 0.459″ |
| p99 error | 16.433″ | 0.906″ |
| median error | 1.710″ | 0.052″ |
| closer samples | 2 / 370 | 368 / 370 |

The two samples where Astronomy Engine was closer were both sub-0.02″-scale differences; they do not reverse the aggregate result.

## 1950–2049 cross-era pointwise benchmark

Design:

```text
100 years
× 4 seasonal UTC timestamps per year
× Sun..Pluto
= 4,000 apparent-longitude comparisons
```

All observed PySwissEph core-planet calls returned:

```text
retflag = 260
effective backend = MOSEPH|SPEED
```

Results:

| Metric | Astronomy Engine 2.1.19 | host PySwissEph/MOSeph |
|---|---:|---:|
| maximum error | 20.462″ | 2.845″ |
| p95 error | 11.482″ | 0.794″ |
| p99 error | 16.595″ | 1.446″ |
| median error | 1.576″ | 0.087″ |
| closer samples | 298 / 4,000 | 3,702 / 4,000 |

Maximum longitude error by body:

| Body | Astronomy Engine | PySwissEph/MOSeph |
|---|---:|---:|
| Sun | 1.985″ | 0.190″ |
| Moon | 12.662″ | 2.845″ |
| Mercury | 10.113″ | 0.289″ |
| Venus | 20.462″ | 0.464″ |
| Mars | 11.249″ | 1.087″ |
| Jupiter | 9.461″ | 0.515″ |
| Saturn | 12.792″ | 0.601″ |
| Uranus | 11.960″ | 0.496″ |
| Neptune | 18.431″ | 1.144″ |
| Pluto | 4.981″ | 0.800″ |

## Cross-era event-root benchmark

Five representative years were sampled:

```text
1950, 1975, 2000, 2025, 2049
```

For each year:

- one Mercury station;
- one Saturn station;
- one Venus tropical ingress.

DE440S station roots were solved from a symmetric derivative of the oracle apparent longitude, not from the external engine's one-hour forward-difference convenience `speed` field.

All **15 / 15** sampled event roots were closer to DE440S under host PySwissEph/MOSeph than under Astronomy Engine.

| Year | Event | PySwiss | Astronomy Engine |
|---:|---|---:|---:|
| 1950 | Mercury station | 5.54 s | 283.67 s |
| 1950 | Saturn station | 18.86 s | 227.84 s |
| 1950 | Venus ingress | 0.07 s | 37.48 s |
| 1975 | Mercury station | 3.54 s | 447.66 s |
| 1975 | Saturn station | 7.27 s | 330.44 s |
| 1975 | Venus ingress | 0.39 s | 51.65 s |
| 2000 | Mercury station | 4.81 s | 350.65 s |
| 2000 | Saturn station | 27.89 s | 167.47 s |
| 2000 | Venus ingress | 0.66 s | 3.46 s |
| 2025 | Mercury station | 4.48 s | 197.12 s |
| 2025 | Saturn station | 18.37 s | 131.42 s |
| 2025 | Venus ingress | 0.18 s | 59.34 s |
| 2049 | Mercury station | 1.48 s | 72.84 s |
| 2049 | Saturn station | 21.78 s | 222.33 s |
| 2049 | Venus ingress | 3.66 s | 41.72 s |

## Remediation judgment

The evidence supports this bounded production architecture:

```text
ChatGPT host
+ host-preinstalled PySwissEph probe PASS
+ entire transit search window within 1950-01-01 .. 2050-01-01
→ paired swiss-host-natal-v1 + pyswisseph-host-transit-v1

otherwise
→ paired astronomy-engine-natal-v1 + astronomy-engine-transit-v1
```

The same transit search kernel remains authoritative for root/search semantics. Only the longitude/speed backend and provider provenance differ.

The portable Astronomy Engine route remains useful and admitted, but its `root_tolerance_seconds` is a **numerical convergence tolerance inside the Astronomy Engine model**, not an assertion of equivalent accuracy to DE440S.

## Limits

This evidence does **not** establish:

- global PySwissEph superiority for all dates;
- accuracy outside the DE440S excerpt's 1950–2050 validation window;
- file-backed SWIEPH superiority (the observed host backend was MOSEPH);
- a scientific/objective predictive-validity claim for astrology;
- permission to install/vendor PySwissEph or Swiss Ephemeris data;
- permission to mix a PySwiss transit backend with an Astronomy Engine natal-target baseline.

The admission must therefore remain host-conditional, modern-range bounded, retflag-provenanced, and pair-atomic.
