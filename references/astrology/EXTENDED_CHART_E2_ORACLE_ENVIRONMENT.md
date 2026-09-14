# Astrology Extended Chart Facts — Phase E2 Oracle Environment

Status: **REFERENCE-ONLY / RESEARCH / NOT PRODUCTION-ADMITTED**

Playbook baseline reviewed: `masini1491/ai-divination-playbook@11a61f628b55f2bb83e2eca9b233eecd0566f03e`

This document continues Phase E2 after `EXTENDED_CHART_E2_EPHEMERIS_OBJECTS_RESEARCH.md`.

The purpose is to freeze a reproducible numerical-oracle environment for:

- Chiron
- Ceres
- Pallas
- Juno
- Vesta

without adding Swiss Ephemeris, pyswisseph, or ephemeris binaries to Production v1.

## 1. Research conclusion

Phase E2 numerical validation needs two distinct roles:

```text
Swiss-family oracle
→ primary compatibility oracle for the five extended objects

independent JPL Horizons oracle
→ independent apparent geocentric ecliptic-of-date cross-check
```

Neither becomes production authority merely by appearing in this research contract.

## 2. Swiss oracle identity

Pinned official repository state:

```text
repository: aloistr/swisseph
revision: 91339e55d2351f32548d8a8d5bca6aa93b4f6da7
path: ephe/seas_18.se1
blob_sha: 8f900cab7e557e4c41f758a6bf3a3c3967e7e3db
size_bytes: 223004
```

The official Swiss Ephemeris distribution tree contains this main-asteroid ephemeris file; the reviewed pyswisseph documentation requires `seas_18.se1` in its basic ephemeris test environment. The reviewed Swiss-family object mappings expose Chiron, Ceres, Pallas, Juno and Vesta as ephemeris-calculated objects.

### 2.1 Calculation contract

Use pinned `pyswisseph` behavior as the Python research adapter:

```text
repository: astrorigin/pyswisseph
revision: 91ec65631badc7faf4a4b913570c944a4c1b101d
```

Required flags:

```text
FLG_SWIEPH | FLG_SPEED
```

The reviewed pyswisseph programmer documentation describes the no-special-coordinate-mode result as apparent geocentric ecliptic polar coordinates relative to the true equinox of date, with tropical coordinates as default; `FLG_SPEED` adds high-precision speed.

Expected output fields retained by research fixtures:

```text
longitude_deg
latitude_deg
distance_au
longitude_speed_deg_per_day
latitude_speed_deg_per_day
distance_speed_au_per_day
returned_flags
```

### 2.2 Ephemeris file is part of provenance

A result is not considered reproducible merely because it says `pyswisseph`.

The fixture must retain:

```text
pyswisseph revision/version
Swiss source revision
seas_18.se1 path
seas_18.se1 blob SHA
calculation flags
input UTC/JD
object identifier
```

If the ephemeris file is unavailable or its identity is unknown, the result is `ORACLE_UNAVAILABLE`, not a substitute Moshier/other result.

## 3. License boundary

The pinned official Swiss Ephemeris license states a dual model:

```text
AGPL
or
Swiss Ephemeris Professional License
```

Therefore this research contract does not authorize:

- committing `seas_18.se1` into this repository;
- adding pyswisseph or Swiss Ephemeris to the Production v1 dependency set;
- deploying a public Swiss-backed service under the current production architecture without a separate license decision;
- copying AGPL implementation into project-owned production code.

Allowed research posture:

```text
pin source/data identity
+ run temporary/local compatibility oracle where legally appropriate
+ commit non-identifying numerical fixture results
+ preserve provenance
```

## 4. Independent JPL Horizons oracle

NASA/JPL Horizons is selected as an independent cross-check because it provides small-body ephemerides independently of the Swiss calculation library.

Research comparison contract:

```text
observer center: Earth geocenter = 500@399
EPHEM_TYPE: OBSERVER
QUANTITIES: 31
APPARENT: AIRLESS
TIME_TYPE: UT
EXTRA_PREC: YES
CSV_FORMAT: YES
```

Horizons quantity 31 is used for observer-centered Earth-ecliptic-of-date longitude/latitude. The comparison intent is to align as closely as practical with Swiss default apparent geocentric ecliptic-of-date coordinates before interpreting residuals.

### 4.1 Unambiguous target selectors

Use numbered-small-body syntax, preserving the semicolon identity:

```text
Ceres   -> 1;
Pallas  -> 2;
Juno    -> 3;
Vesta   -> 4;
Chiron  -> 2060;
```

### 4.2 Longitude comparison

At each fixture time `t`:

```text
Swiss apparent geocentric tropical ecliptic longitude at t
vs
Horizons quantity 31 observer ecliptic-of-date longitude at t from 500@399
```

Do not compare heliocentric coordinates to Swiss geocentric longitude.

### 4.3 Speed comparison

If the selected Horizons output does not directly expose ecliptic-longitude speed, derive an independent finite-difference speed:

```text
lon_before = Horizons observer ecliptic longitude(t - 1 hour)
lon_after  = Horizons observer ecliptic longitude(t + 1 hour)
signed_delta = shortest_signed_delta(lon_before, lon_after)
speed_deg_per_day = signed_delta / 2 hours * 24 hours/day
```

This is research-only comparison logic and is not a production event-search authority.

## 5. Fixture design

Phase E2 numerical completion requires multiple public/synthetic times, not one natal chart.

Minimum fixture set:

```text
E2-F01 2000-01-01T12:00:00Z  J2000 neighborhood
E2-F02 1980-06-01T00:00:00Z  modern historical
E2-F03 2026-09-14T00:00:00Z  current-era
E2-F04 2099-12-31T00:00:00Z  future within seas_18 era
```

For each of five objects, record:

```text
Swiss longitude / speed / returned flags
Horizons longitude
Horizons finite-difference speed
circular longitude delta
speed delta
source revisions
```

No real person's birth data is required.

## 6. Tolerance policy

No production tolerance is declared in this document.

Reason:

- Swiss and Horizons may use differing small-body orbit solutions and update cadences;
- both may change their underlying data independently;
- Chiron and main-belt asteroids should not be assumed to exhibit identical cross-system residuals;
- an arbitrary tolerance chosen before observing fixtures would manufacture a pass criterion.

Research sequence:

```text
collect residuals across fixtures
→ inspect definition/configuration mismatches
→ characterize stable residual envelope by object
→ propose bounded research tolerance
→ rerun on holdout fixtures
→ only then consider an admission threshold
```

Until that sequence is complete, comparisons report numeric deltas without PASS/FAIL by tolerance.

## 7. Fail-closed classes

```text
ORACLE_UNAVAILABLE
  missing pyswisseph or seas_18.se1

DATA_IDENTITY_MISMATCH
  Swiss file/source identity differs from manifest

TARGET_IDENTITY_MISMATCH
  Horizons target selector did not resolve expected numbered object

CONFIGURATION_MISMATCH
  center/frame/apparent-vs-geometric/ecliptic mode differs

OUT_OF_COVERAGE
  requested time falls outside pinned ephemeris-file coverage

NUMERIC_OBSERVATION
  both sources returned comparable values; residual retained without premature admission
```

## 8. Current E2 status after this contract

```text
object identities                 RESOLVED
Swiss object mappings             RESOLVED
main asteroid data dependency     RESOLVED
Swiss file revision/blob identity RESOLVED
license boundary                  RESOLVED
independent oracle selection      RESOLVED
coordinate-comparison contract    RESOLVED
fixture times                     DEFINED
numerical residual collection     PENDING
production tolerance              NOT DEFINED
production admission              NOT GRANTED
```

This advances Phase E2 from an environment-unknown block to a reproducible oracle specification. Numerical E2 completion still requires execution with the pinned Swiss binary data and recorded Horizons responses.
