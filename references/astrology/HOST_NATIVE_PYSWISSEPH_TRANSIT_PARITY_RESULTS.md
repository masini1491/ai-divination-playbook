# Host-Native PySwissEph Transit Parity Results

Status: **REFERENCE-ONLY / RESEARCH COMPLETE / NOT PRODUCTION-ROUTABLE**

Work item: `AST-P1-270 — Host-native PySwissEph transit parity feasibility`

Playbook revision tested:

```text
masini1491/ai-divination-playbook@be84d1e5582fc60e7219a2035f59730ef1f2e9a7
```

## 1. Research question

Can the ChatGPT host-native PySwissEph runtime act as a deterministic transit calculation backend closely enough to justify a later production-admission task, without changing the current `astronomy-engine-transit-v1` production route during research?

This is a provider-feasibility comparison, not a scientific-accuracy proof.

## 2. Execution provenance

The Astronomy Engine side was materialized from the exact-main GitHub Actions handoff artifact:

```text
artifact: astrology-core-handoff-be84d1e5582fc60e7219a2035f59730ef1f2e9a7
artifact id: 11647931489
artifact ZIP sha256: b710e83dfb0f4a26150f04963a87c6189a70554b8e7a073a3b23486cea7bd4b1
bundle verifier: tools/build_astrology_core_bundle.py
bundle verification: PASS
astronomy-engine: 2.1.19
Astronomy Engine source revision: 865d3da7d8112bbc7911238052c6af4aaf877181
```

Host runtime:

```text
Python: 3.13.5
PySwissEph: 2.10.03
requested flags: SWIEPH | SPEED (258)
observed effective backend: MOSEPH
```

All 370 pointwise PySwissEph calls returned `retflag = 260`, i.e. **MOSEPH + SPEED**. Therefore this result is:

> host-native PySwissEph / Moshier backend vs Astronomy Engine

and **not** file-backed Swiss Ephemeris data (`SWIEPH_ONLY`) vs Astronomy Engine.

## 3. Method

The companion probe reuses the current production transit search kernel and changes only its longitude/speed callback during the research process:

```text
same tools/astrology_transit_provider.py search algorithms
├─ Astronomy Engine: tools.astrology_provider._longitude_and_speed
└─ PySwissEph: calc_ut(..., FLG_SWIEPH | FLG_SPEED)
```

No production file, provider route, event definition, root tolerance, scan step, tangential-station tolerance, house-assignment algorithm or interpretation policy was changed.

Synthetic/source-neutral fixtures were taken from current production tests:

- Mercury fixed natal longitude `110.0°`;
- Mercury 2026 three-pass conjunction;
- Mercury 2026 stations;
- Saturn 2026 stations;
- Venus `210°` Libra/Scorpio ingress-return-reingress;
- synthetic Whole Sign house cusps `0°, 30°, ... 330°`;
- Sun House 12 → 1 ingress and point-in-time house context;
- Mercury tangential-station exact-contact stress case.

## 4. Comparison-policy boundary

No new production tolerance is admitted here.

Existing values are used only as reference bands:

```text
longitude reference ceiling:
  0.0167° from current swiss-host-natal-v1 validation
  → diagnostic reference only, not promoted to transit production tolerance

speed diagnostic band:
  0.001°/day
  → research discrepancy screen away from speed-zero roots
  → station parity is judged primarily by zero-crossing topology + root time

event-time reference bands:
  <= 90 s   = tight historical timing neighborhood
  <= 600 s  = existing Mercury three-pass production/reference ceiling
  > 600 s   = material timing discrepancy requiring event-family-specific review
```

The 600-second value is **not** generalized into a new all-transit acceptance threshold.

## 5. Pointwise longitude / speed parity

Sample:

```text
37 UTC timestamps across 2026
× Sun..Pluto (10 bodies)
= 370 comparisons
```

Results:

| Metric | Result |
|---|---:|
| Maximum longitude difference | 0.005659359° = 20.374″ |
| p95 longitude difference | 0.003430558° |
| p99 longitude difference | 0.004577491° |
| Maximum speed difference | 0.000380237°/day |
| p95 speed difference | 0.000194030°/day |
| p99 speed difference | 0.000285536°/day |

The maximum longitude residual is below the existing `0.0167°` natal reference ceiling, and the maximum speed residual is below the research-only `0.001°/day` diagnostic band. These observations do not by themselves establish transit event equivalence.

## 6. Transit-to-natal repeated passage

Synthetic target:

```text
Mercury → fixed natal Mercury longitude 110.0°
conjunction
2026-06-01 .. 2026-08-10 UTC
```

Both backends returned three passages with identical motion sequence:

```text
direct → retrograde → direct
```

| Passage | Astronomy Engine UTC | PySwissEph/Moshier UTC | |Δt| |
|---:|---|---|---:|
| 1 | 2026-06-16T15:43:55.565186Z | 2026-06-16T15:44:16.988526Z | 21.423 s |
| 2 | 2026-07-14T03:53:53.111573Z | 2026-07-14T03:53:27.073975Z | 26.038 s |
| 3 | 2026-08-01T13:52:55.213624Z | 2026-08-01T13:51:40.726319Z | 74.487 s |

Maximum three-pass delta: **74.487 s**.

All three remain well inside the existing Mercury-specific 600-second reference ceiling.

## 7. Station parity

### Mercury 2026

Both backends returned **6** stations with the same transition sequence.

| # | Astronomy Engine UTC | PySwissEph/Moshier UTC | |Δt| | Transition |
|---:|---|---|---:|---|
| 1 | 2026-02-26T06:47:02.113038Z | 2026-02-26T06:48:13.634034Z | 71.521 s | direct_to_retrograde |
| 2 | 2026-03-20T19:34:22.847901Z | 2026-03-20T19:32:54.188233Z | 88.660 s | retrograde_to_direct |
| 3 | 2026-06-29T17:37:08.082276Z | 2026-06-29T17:35:59.197999Z | 68.884 s | direct_to_retrograde |
| 4 | 2026-07-23T22:56:47.574464Z | 2026-07-23T22:57:55.469971Z | 67.896 s | retrograde_to_direct |
| 5 | 2026-10-24T07:15:19.500733Z | 2026-10-24T07:12:47.889405Z | 151.611 s | direct_to_retrograde |
| 6 | 2026-11-13T15:52:12.916260Z | 2026-11-13T15:53:57.066651Z | 104.150 s | retrograde_to_direct |

### Saturn 2026

Both backends returned **2** stations with the same transition sequence.

| # | Astronomy Engine UTC | PySwissEph/Moshier UTC | |Δt| | Transition |
|---:|---|---|---:|---|
| 1 | 2026-07-26T19:57:39.649659Z | 2026-07-26T19:56:47.574464Z | 52.075 s | direct_to_retrograde |
| 2 | 2026-12-10T23:23:22.130127Z | 2026-12-10T23:31:02.567139Z | 460.437 s | retrograde_to_direct |

Maximum station-time delta in these fixtures: **460.437 s**.

The event counts and direct/retrograde transitions agree, including the slow-body Saturn stress case.

## 8. Venus 210° ingress / return / re-ingress

Both backends returned the same topology:

```text
direct_ingress
→ retrograde_return
→ direct_reingress
```

| # | Event | Astronomy Engine UTC | PySwissEph/Moshier UTC | |Δt| |
|---:|---|---|---|---:|
| 1 | direct_ingress | 2026-09-10T08:12:43.385010Z | 2026-09-10T08:06:48.416749Z | 354.968 s |
| 2 | retrograde_return | 2026-10-25T08:56:57.572022Z | 2026-10-25T09:09:47.823486Z | 770.251 s |
| 3 | direct_reingress | 2026-12-04T08:14:35.445557Z | 2026-12-04T08:12:43.385010Z | 112.061 s |

The retrograde return differs by **770.251 s (~12.84 min)**.

This exceeds the existing Mercury-specific 600-second reference ceiling and is direct evidence that one global event-time tolerance should not be inferred from the current Mercury fixture.

## 9. Transit-house geometry

Synthetic Whole Sign cusp:

```text
Sun crosses 0° cusp
House 12 → House 1
2026-03-19 .. 2026-03-22 UTC
```

Both backends returned one House 12 → 1 crossing.

Time difference: **24.390 s**.

Point-in-time house context at `2026-03-20T12:00:00Z`:

```text
Astronomy Engine house = 12
PySwissEph house        = 12
longitude difference    = 0.000282499°
```

No house-assignment disagreement occurred in this fixture.

## 10. Material discrepancy: tangential exact contact is backend-sensitive

Current production transit validation explicitly admits a tangential exact hit at station using:

```text
TANGENTIAL_STATION_ANGLE_TOLERANCE_DEG = 0.0001
= 0.360″
```

For the Mercury direct→retrograde station near 2026-06-29:

```text
Astronomy Engine station longitude:
  116.257868326457°

Astronomy Engine vs PySwissEph station-longitude difference:
  0.000515296543°
  = 1.855″
```

Using the **same fixed natal target**, defined as the Astronomy Engine station longitude:

```text
Astronomy Engine exact events = 1
root kind                     = tangential_station

PySwissEph/Moshier exact events = 0
```

The cross-engine station-longitude difference (**1.855″**) is more than five times the admitted tangential detector tolerance (**0.360″**).

Therefore a fixed natal longitude can produce:

```text
backend A → exact tangential event exists
backend B → exact tangential event does not exist
```

even while ordinary crossing topology, sign motion and most event times remain close.

This is a **material event-identity difference**, not merely a timing residual.

## 11. Evidence synthesis

Positive feasibility evidence:

1. host-native PySwissEph can provide longitude + speed without repository installation;
2. 370 pointwise Sun..Pluto samples remained close to Astronomy Engine at arcsecond-to-tens-of-arcseconds scale;
3. Mercury three-pass topology matched 3/3;
4. Mercury station topology matched 6/6;
5. Saturn station topology matched 2/2;
6. Venus ingress/return/re-ingress topology matched 3/3;
7. synthetic transit-house ingress and point-in-time house assignment matched.

Material limitations:

1. current host effective backend is MOSEPH, so this does not establish file-backed `SWIEPH_ONLY` transit parity;
2. one Venus ingress-family timing delta is 770.251 s, showing the current Mercury 600-second benchmark cannot be generalized;
3. tangential station exact-contact identity is backend-sensitive under the current `0.0001°` detector tolerance;
4. current production accepts natal bundles from multiple admitted provenance paths; therefore a future transit backend cannot assume its moving-body ephemeris is automatically paired with natal target longitudes produced by the same backend.

## 12. AST-P1-270 conclusion

**Decision: retain Astronomy Engine-only production transit for the current architecture.**

This is not a finding that PySwissEph transit calculation is unusable. It is a narrower architecture/admission judgment:

> host-native PySwissEph/Moshier is numerically feasible for ordinary transit geometry, but current evidence does not support treating it as a drop-in production replacement/fallback for `astronomy-engine-transit-v1`.

No production route, provider admission or transit semantics should change from AST-P1-270.

A future independent production-admission task becomes reasonable only if it explicitly resolves:

- natal-target provenance/backend pairing;
- tangential-station event identity across backends;
- event-family-specific timing acceptance rather than a single global threshold;
- per-calculation `retflag` and effective backend provenance;
- a fresh host probe, including `SWIEPH_ONLY` evidence if file-backed Swiss Ephemeris data is specifically claimed.

Possible future architectures remain open:

```text
A. keep Astronomy Engine-only production transit
B. admit a host PySwissEph transit provider for explicitly compatible natal-target provenance
C. introduce a shared ephemeris backend seam with explicit backend identity
```

AST-P1-270 does not choose B or C.

## 13. Authority boundary

```text
this report / companion probe / JSON
→ REFERENCE-ONLY research evidence

ASTROLOGY_TRANSIT.md
+ admissions/astrology/ASTROLOGY_TRANSIT_PROVIDER_ADMISSION_V1.json
+ tools/astrology_transit_provider.py
→ current production authority
```

**Current production result remains: `astronomy-engine-transit-v1`.**
