# JPL DE440S Transit Oracle Adjudication

Status: **REFERENCE-ONLY / RESEARCH COMPLETE / PRODUCTION CORRECTNESS FOLLOW-UP REQUIRED**

Work item: `AST-P1-280 — JPL DE440S transit oracle adjudication`

Tested repository revision:

```text
masini1491/ai-divination-playbook@f5d540ec50ad4923a2841bcad15449e61bf3c59b
```

## 1. Question

AST-P1-270 established that host-native PySwissEph/MOSeph and the admitted Astronomy Engine transit provider are close for ordinary geometry but disagree materially in two cases:

- Venus tropical 210° retrograde return on 2026-10-25;
- Mercury tangential-station exact-contact geometry on 2026-06-29.

That comparison could not establish which backend was closer to an independent astronomical reference.

AST-P1-280 therefore asks a narrower question:

> For those two disputed 2026 cases, which result is closer to an independent JPL DE440S apparent geocentric ecliptic-of-date reference?

This task does not claim global provider superiority.

## 2. Independent oracle provenance

The oracle used a real **NASA/JPL DE440S binary SPK kernel**, not a rounded website ephemeris.

Source/execution path:

```text
ffalcinelli/astroceleste-engine@622693a0e49a622f955c3a298d7f09ed650e1382
GitHub Pages workflow run 37898071384
artifact id 11601197376
artifact digest sha256:0c95147d5fa44c977f7aa0c435db6c2468ac9b5fff92f1998dfc7c1d31d557cc

artifact
→ ephemeris/de440s-1950-2050.bsp
→ SHA-256 06524f5fc8c3ff2f91b841936c80363d54cfd6d261e8cd7642e25d521ab88165
→ size 10,890,240 bytes
```

The external build script generates that excerpt from the upstream JPL kernel URL:

```text
https://ssd.jpl.nasa.gov/ftp/eph/planets/bsp/de440s.bsp
```

The external engine states are independently validated at two levels:

1. SPK state evaluation is cross-checked against `jplephem`;
2. apparent-position reduction is cross-checked stage-by-stage against **Skyfield 1.55**.

The published reduction contract is:

```text
geocentric apparent position
+ light-time iteration
+ gravitational deflection by Sun/Jupiter/Saturn
+ aberration
+ IAU 2000A nutation
+ IAU 2006 precession
→ true ecliptic longitude/latitude of date
```

Its documented ecliptic longitude/latitude reduction tolerance against Skyfield is `1e-5 arcsec`.

This coordinate contract is materially aligned with the current repository transit longitude definition:

```text
geocentric
tropical
apparent
ecliptic of date
```

## 3. Mercury 2026-06-29 station

### 3.1 Oracle root method

The external engine's public `speed` convenience field is a one-hour forward difference. That field is **not** used as the oracle station root because its zero occurs roughly half a sampling interval early.

Instead, the DE440S apparent longitude itself was evaluated symmetrically:

```text
speed(t; h)
= signed_longitude_delta(lon(t-h), lon(t+h)) / (2h)
```

The zero root was solved with half-windows of 1, 10, 60, 600 and 3600 seconds.

Convergence:

| Symmetric half-window | Root UTC |
|---:|---|
| 1 s | 2026-06-29 17:35:55.146 |
| 10 s | 2026-06-29 17:35:55.148 |
| 60 s | 2026-06-29 17:35:55.148 |
| 600 s | 2026-06-29 17:35:55.152 |
| 3600 s | 2026-06-29 17:35:55.277 |

The root is numerically stable at the sub-second level.

DE440S station:

```text
UTC       2026-06-29T17:35:55.146Z
longitude 116.25735909103152°
```

### 3.2 Three-way comparison

| Backend | Station UTC | |Δt vs DE440S| | Station-longitude delta |
|---|---|---:|---:|
| DE440S oracle | 17:35:55.146 | — | — |
| PySwissEph / MOSEPH | 17:35:59.363 | **4.217 s** | **0.02182″** |
| Astronomy Engine | 17:37:07.787 | **72.641 s** | **1.83325″** |

For this station:

> **PySwissEph/MOSeph is materially closer to DE440S than Astronomy Engine.**

This does not establish that PySwissEph is globally superior.

## 4. Mercury tangential exact-contact implication

Current transit production admits tangential exact detection with:

```text
TANGENTIAL_STATION_ANGLE_TOLERANCE_DEG = 0.0001°
                                          = 0.36″
```

The Astronomy Engine station longitude used by the current synthetic fixture is:

```text
116.257868326455°
```

The DE440S station longitude is:

```text
116.257359091032°
```

Difference:

```text
1.83325″
```

That is over five times the admitted tangential detector tolerance.

Therefore the Astronomy-Engine-defined fixed natal target is **not** tangent to the independently computed DE440S Mercury station within the current exact-event tolerance.

This explains the AST-P1-270 event-identity split:

```text
Astronomy Engine
→ tangential_station exact event exists

PySwissEph/MOSeph
→ no exact tangential hit
```

The independent DE440S result supports the **PySwissEph no-hit classification for that fixed target**.

This is a confirmed correctness concern for the current synthetic tangential-station production regression; it is not merely provider timing noise.

## 5. Venus 210° retrograde return

Event definition:

```text
Venus apparent tropical geocentric longitude
= 210.000000°
retrograde crossing
2026-10-25
```

DE440S root:

```text
UTC       2026-10-25T09:09:47.792Z
longitude 209.999999994137°
```

Three-way comparison:

| Backend | Root UTC | |Δt vs DE440S| |
|---|---|---:|
| DE440S oracle | 09:09:47.792 | — |
| PySwissEph / MOSEPH | 09:09:47.887 | **0.095 s** |
| Astronomy Engine | 08:56:57.680 | **770.112 s** |

At the DE440S root instant:

```text
Astronomy Engine longitude residual ≈ -19.593″
PySwissEph/MOSeph residual          ≈ +0.00242″
```

For this ingress-family event:

> **PySwissEph/MOSeph is essentially coincident with DE440S, while Astronomy Engine is about 12.84 minutes early.**

## 6. Adjudication

These two disputed cases now have independent-oracle resolution:

```text
Mercury station
→ PySwissEph/MOSeph closer to DE440S

Venus 210° retrograde return
→ PySwissEph/MOSeph dramatically closer to DE440S
```

However the correct architecture conclusion is **not**:

```text
switch all production transit to PySwissEph
```

because this bounded study does not establish:

- all-body/all-date provider superiority;
- SWIEPH file-backed parity (the current host still returned MOSEPH);
- unknown-time/natal-target provenance compatibility;
- global station/ingress/aspect timing tolerances;
- dependency/routing/product reliability for host-native PySwissEph.

## 7. Production implication

The independent oracle changes the status of the problem.

AST-P1-270 concluded only:

```text
provider difference exists
→ keep current production route pending stronger evidence
```

AST-P1-280 now establishes:

```text
for two admitted/validated 2026 transit cases,
Astronomy Engine is materially farther from DE440S than PySwissEph/MOSeph
→ production correctness follow-up is required
```

The current production route must **not** be silently changed by this research task.

Instead, open a separate P0 correctness item to determine the minimum safe remedy. Candidate remedies may include:

1. correct the Astronomy Engine coordinate/event model where the discrepancy originates;
2. narrow or remove affected exact-event admission until corrected;
3. admit a different deterministic ephemeris backend under a separately validated contract.

The remedy must be chosen by the new correctness task, not assumed by this report.

## 8. Authority boundary

```text
this report + companion JSON
→ REFERENCE-ONLY research evidence

current production authority
→ ASTROLOGY_TRANSIT.md
→ admissions/astrology/ASTROLOGY_TRANSIT_PROVIDER_ADMISSION_V1.json
→ tools/astrology_transit_provider.py
```

**AST-P1-280 conclusion: PySwissEph/MOSeph wins both disputed DE440S adjudication cases; production correctness remediation is required, but no provider/routing mutation is authorized by this research result.**
