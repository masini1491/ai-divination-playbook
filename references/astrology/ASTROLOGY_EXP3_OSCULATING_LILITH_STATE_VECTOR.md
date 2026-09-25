# AST-P1-030 — Osculating / True Black Moon Lilith State-Vector Research

Status: **REFERENCE-ONLY / RESEARCH COMPLETE / STABILITY PASS / NOT PRODUCTION-ADMITTED**

## 1. Explicit candidate identity

```text
fact id          black_moon_lilith_osculating_lrl_aengine_v0
definition       instantaneous lunar osculating apogee via LRL eccentricity vector
state source     astronomy-engine==2.1.19 GeoMoonState()
state frame      J2000 mean equatorial (EQJ), geocentric
state units      position AU; velocity AU/day
output frame     true ecliptic / equinox of date (ECT)
normalization    mod 360 degrees
Earth-Moon μ     8.997011546044162e-10 AU^3/day^2
```

The LRL eccentricity vector

```text
e = ((|v|² - μ/|r|) r - (r·v) v) / μ
```

points toward lunar perigee. The osculating apogee is the antipodal direction.

Mean Black Moon Lilith, Osculating/True Black Moon Lilith, and Interpolated Black Moon Lilith remain distinct fact identities. A bare `Lilith` alias is not introduced.

## 2. Research input authority versus production authority

The candidate uses pinned Astronomy Engine `GeoMoonState()` as a **research input capability**. Its documented state is geocentric EQJ position and velocity in AU / AU/day.

This does not mean that Cartesian Moon state vectors are currently admitted as user-visible production Astrology facts:

```text
pinned dependency can calculate Moon state
≠ production Astrology fact schema admits Moon state vectors
≠ production Osculating Lilith calculation admission
```

The current production provider may use Astronomy Engine internally while still exposing only its separately admitted fact surface.

The LRL calculation is performed in the inertial EQJ state frame. Only the derived eccentricity direction is then rotated to true ecliptic-of-date. This avoids treating a rotating-of-date frame as if its coordinate derivative were an inertial orbital velocity.

## 3. Prospective research contract

Before the first Actions execution, temporary PR #185 froze:

```text
research T window                 -0.5 through +0.5 Julian centuries
approx calendar window            1950-2050
fixtures                          17
fixture spacing                   0.0625 Julian century

state vs 0.05d finite difference  <= 0.25 degrees
0.025/0.05/0.1d FD step spread   <= 0.50 degrees

Swiss SE_OSCU_APOG                report only; no gate
```

The window is research validation coverage, not a production-admitted date window. No numerical threshold was widened after observing the result.

Temporary execution evidence:

```text
PR                 #185
head               2a3abfe70788a85db5cb5beb0dfc91ea6050d594
workflow run       36093918723
validate job       107941989048
merged             NO
```

## 4. Pinned reference paths

| Role | Source | Revision |
|---|---|---|
| Moon state research input | `cosinekitty/astronomy` | `865d3da7d8112bbc7911238052c6af4aaf877181` |
| independent LRL architecture / μ cross-check | `vedika-io/xalen-ephemeris` | `cc6edbec1f748ebdc4950ae6198f575c5ada73fa` |
| Swiss compatibility only | `astrorigin/pyswisseph` | `91ec65631badc7faf4a4b913570c944a4c1b101d` |

Research runtime versions were `astronomy-engine 2.1.19` and `pyswisseph 2.10.03`.

## 5. Measured result

| Measurement | Frozen gate | Observed | Result |
|---|---:|---:|---|
| exact state vs 0.05-day finite difference max | 0.25° | 0.0736443° | PASS |
| finite-difference step spread max | 0.50° | 0.277176° | PASS |
| Earth-only μ sensitivity max | none | 16.910631° | MODEL SENSITIVITY |
| Swiss `SE_OSCU_APOG` compatibility | none | 0.011866°–0.152423° | REPORT ONLY |

Overall frozen-gate research stability: **PASS**.

At J2000 the candidate produced `252.9604426°`; the 0.05-day finite-difference path differed by about `0.015595°`. Swiss reported about `252.9781237°`, a `0.017681°` compatibility residual at that fixture.

## 6. Model sensitivity

Changing only the gravitational parameter from the Earth–Moon system value to an Earth-only value moved the derived apogee direction by as much as **16.910631°** in the research fixtures.

Therefore μ is not an implementation detail:

```text
osculating-apogee fact identity
→ Moon state model
+ state frame and units
+ gravitational parameter
+ LRL derivation
+ output-frame transformation
```

must stay explicit.

The close Swiss residual observed in this bounded probe is useful compatibility evidence, but it does not establish a universal same-definition identity or exact Swiss compatibility. No Swiss gate was prospectively frozen.

## 7. Research closure boundary

```text
research stability PASS
≠ production calculation admission
≠ semantic interpretation admission
```

This work does not modify `tools/**`, `runtime/**`, the Astrology Fact Gate, provider admission manifests, interpretation registries, aspect participant policies, or a production date window.

Required state input fails closed in the retained reference implementation. Any future production admission must separately decide provider/API ownership, state-vector authority, exact date window, public schema identity, regression policy, and semantic interpretation admission.

## 8. Durable files

- research implementation: `osculating_lilith_state_research.py`
- machine evidence: `astrology_exp3_osculating_lilith_state_vector.json`
