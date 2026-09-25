# AST-P1-040 — Vertex / Equatorial Ascendant Geometry Research

Status: **REFERENCE-ONLY / RESEARCH COMPLETE / GEOMETRY PASS / NOT PRODUCTION-ADMITTED**

## 1. Candidate identities

```text
Vertex
fact id       vertex_prime_vertical_ecliptic_v0
definition    western intersection of local prime-vertical plane and ecliptic plane

Equatorial Ascendant
fact id       equatorial_ascendant_ra_plus_90_v0
definition    ecliptic point whose right ascension is ARMC + 90°
```

These are distinct derived geometry facts. Neither is an alias for ASC/DSC/MC/IC.

## 2. Project input convention

The project-owned research path uses:

```text
date/time/location
→ astronomy-engine==2.1.19 SiderealTime()
→ east-positive longitude
→ project mean-obliquity convention
→ ARMC / obliquity / latitude
→ local spherical geometry
```

Output is tropical ecliptic longitude normalized modulo 360°. The research implementation adds no ephemeris body dependency.

## 3. Geometry definitions

Vertex is calculated as the line of intersection between the local prime-vertical plane and the ecliptic plane, selecting the western branch.

Equatorial Ascendant is the ecliptic point satisfying:

```text
right ascension = ARMC + 90°
```

The vector/coordinate formulation avoids identifying either point through a house cusp or an unrelated angle.

## 4. Prospective validation contract

Before first Actions execution, temporary PR #187 froze:

```text
synthetic geometry-plane residual       <= 1e-12
Equatorial Ascendant RA identity        <= 1e-10°
same ARMC/obliquity Swiss parity        <= 1e-8°
project input path vs Swiss             <= 0.05°
```

Synthetic latitude fixtures included 0°, ±25/33°, ±65° and ±89°. Public real-location fixtures were Greenwich, Sydney, Quito, Tromsø and Ushuaia.

Temporary execution:

```text
PR                 #187
head               13691feef30bb076068961c1f45b29e66f6b4ac5
workflow run       36095412306
validate job       107946545846
merged             NO
```

No threshold was widened after execution.

## 5. Reference paths

| Role | Source | Revision |
|---|---|---|
| same-input formula oracle | `aloistr/swisseph` | `9083a12d59e98034fb2337061481ac8800c16e64` |
| project sidereal-time input | `cosinekitty/astronomy` | `865d3da7d8112bbc7911238052c6af4aaf877181` |
| named East Point compatibility | `CruiserOne/Astrolog` | `5bf172ea231c4b6ea3d7e09ca307571354a41e8a` |

The Swiss revision above is the exact source used by this experiment; it does not retroactively rewrite older E4 historical pinning.

## 6. Measured result

| Measurement | Frozen gate | Observed | Result |
|---|---:|---:|---|
| synthetic plane residual max | 1e-12 | 5.5511e-17 | PASS |
| Equasc RA identity residual max | 1e-10° | 2.8422e-14° | PASS |
| same-input Swiss residual max | 1e-8° | 2.8422e-14° | PASS |
| project-input Swiss residual max | 0.05° | 0.00164467° | PASS |

The project-input maximum split was:

```text
Vertex                 0.0016446705°
Equatorial Ascendant   0.0003416486°
```

So the project formula identity passes near machine precision under the same ARMC/obliquity inputs, while the existing project sidereal-time/mean-obliquity convention remains comfortably within the prospectively frozen end-to-end research gate.

## 7. East Point boundary

Pinned Astrolog evidence labels its `EP` field “East Point” and assigns it from Swiss `SE_EQUASC`. This establishes a **named consumer compatibility mapping**:

```text
Astrolog "East Point"
→ Swiss SE_EQUASC
→ Equatorial Ascendant
```

It does not establish:

```text
"East Point" = universal canonical mathematical name
or
production alias admission
```

Canonical research identity remains `equatorial_ascendant_ra_plus_90_v0`. Any future user-facing `East Point` alias requires a separate explicit compatibility/admission policy.

## 8. Closure boundary

```text
research geometry PASS
≠ production calculation admission
≠ semantic interpretation admission

named East Point compatibility evidence
≠ canonical mathematical identity
≠ production alias admission
```

This research does not modify `tools/**`, `runtime/**`, the Astrology Fact Gate, production manifests, interpretation registries, or aspect policies.

## 9. Durable files

- research implementation: `special_points_geometry_research.py`
- machine evidence: `astrology_exp4_special_points_geometry.json`
