# Astrology Extended Chart Facts — Phase E2 Oracle Environment

Status: **REFERENCE-ONLY / RESEARCH CHARACTERIZED / NOT PRODUCTION-ADMITTED**

Playbook baseline reviewed: `masini1491/ai-divination-playbook@ed639c52d64556339e2848dc93ae5722dbc771c1`

This document freezes the measured Phase E2 oracle environment for Chiron, Ceres, Pallas, Juno and Vesta. It does not add Swiss Ephemeris, pyswisseph, or ephemeris binaries to Production v1.

## 1. Oracle roles

```text
Swiss-family oracle
→ primary compatibility oracle for the five extended objects

NASA/JPL Horizons
→ independent apparent geocentric ecliptic-of-date cross-check
```

Neither source becomes production authority merely because it is used here.

## 2. Swiss oracle identity

Pinned official repository state:

```text
repository: aloistr/swisseph
revision: 91339e55d2351f32548d8a8d5bca6aa93b4f6da7

main-asteroid file:
  path: ephe/seas_18.se1
  blob_sha: 8f900cab7e557e4c41f758a6bf3a3c3967e7e3db
  size_bytes: 223004

planetary file:
  path: ephe/sepl_18.se1
  blob_sha: 786702cd04506371ee6223af1ebac02d54c848b8
  size_bytes: 484061
```

### 2.1 Important dependency correction from live execution

The initial research contract pinned only `seas_18.se1`. Live execution showed that this is insufficient for the intended **geocentric** extended-object calculation.

With only `seas_18.se1`, the calculation returned flags `260`, indicating fallback away from the requested Swiss ephemeris calculation. Once the matching `sepl_18.se1` planetary ephemeris was also supplied, the five-object calculations returned flags `258` (`FLG_SWIEPH | FLG_SPEED`) throughout the measured fixture set.

Therefore the reproducible E2 Swiss oracle is:

```text
pinned Swiss source revision
+ exact seas_18.se1 identity
+ exact sepl_18.se1 identity
+ FLG_SWIEPH | FLG_SPEED
```

A future oracle run that cannot prove both binary identities must fail closed.

### 2.2 Python research adapter

```text
repository: astrorigin/pyswisseph
revision: 91ec65631badc7faf4a4b913570c944a4c1b101d
measured execution version: pyswisseph==2.10.3.2
```

Expected output retained by research observations:

```text
longitude_deg
latitude_deg
distance_au
longitude_speed_deg_per_day
latitude_speed_deg_per_day
distance_speed_au_per_day
returned_flags
```

## 3. License boundary

Swiss Ephemeris uses the reviewed dual-license model:

```text
AGPL
or
Swiss Ephemeris Professional License
```

This research contract does **not** authorize:

- committing Swiss ephemeris binaries into this repository;
- adding pyswisseph / Swiss Ephemeris to Production v1 dependencies;
- deploying a Swiss-backed public production service without a separate license decision;
- copying AGPL implementation into project-owned production code.

The measured probe used `immanuel==1.6.0` package data only as a temporary binary carrier after byte identity was verified against the pinned official Git blobs. That carrier has no authority of its own.

## 4. NASA/JPL Horizons contract

Measured live requests used:

```text
provider: NASA/JPL Horizons API
observed API signature version: 1.2
EPHEM_TYPE: OBSERVER
CENTER: 500@399
QUANTITIES: 31
APPARENT: AIRLESS
TIME_TYPE: UT
EXTRA_PREC: YES
CSV_FORMAT: YES
```

Object selectors:

```text
Ceres   -> 1;
Pallas  -> 2;
Juno    -> 3;
Vesta   -> 4;
Chiron  -> 2060;
```

The observed API signature is execution provenance, not a promise that the public API will never change version.

### 4.1 Longitude and speed comparison

Longitude comparison:

```text
Swiss apparent geocentric tropical ecliptic longitude
vs
Horizons quantity 31 observer ecliptic-of-date longitude from 500@399
```

Horizons longitude speed was independently derived as:

```text
lon_before = ObsEcLon(t - 1 hour)
lon_after  = ObsEcLon(t + 1 hour)
signed_delta = shortest_signed_delta(lon_before, lon_after)
speed_deg_per_day = signed_delta * 12
```

## 5. Measured fixture layers

Calibration:

```text
E2-F01 2000-01-01T12:00:00Z
E2-F02 1980-06-01T00:00:00Z
E2-F03 2026-09-14T00:00:00Z
E2-F04 2099-12-31T00:00:00Z
```

Independent holdout:

```text
E2-H01 1850-03-20T06:00:00Z
E2-H02 1955-11-05T18:00:00Z
E2-H03 2050-07-01T06:00:00Z
E2-H04 2200-02-28T18:00:00Z
```

Prospective validation, selected before its first result was observed:

```text
E2-V01 1825-08-17T03:00:00Z
E2-V02 1925-02-14T15:00:00Z
E2-V03 2075-10-09T09:00:00Z
E2-V04 2350-05-23T21:00:00Z
```

Each layer contains five objects per instant.

## 6. Residual characterization

Calibration, 20 samples:

```text
max longitude residual ≈ 1.220 arcsec
max speed residual     ≈ 5.148e-6 deg/day
```

Holdout, 20 samples:

```text
max longitude residual ≈ 2.965 arcsec
max speed residual     ≈ 5.559e-6 deg/day
```

The evidence justified testing the following **prospective**, frozen-before-execution candidate threshold:

```text
longitude <= 5 arcsec
speed     <= 1e-5 deg/day
```

That candidate **failed** prospective validation. At `E2-V04` (`2350-05-23T21:00:00Z`):

```text
Ceres longitude ≈ 5.791 arcsec; speed ≈ 3.195e-5 deg/day
Juno  longitude ≈ 7.805 arcsec
Vesta longitude ≈ 6.091 arcsec
```

The other 17 prospective object/time rows were within the frozen threshold.

## 7. Tolerance conclusion

The failed threshold is evidence, not something to repair by widening it after seeing the result.

Therefore:

```text
NO_UNIVERSAL_PROSPECTIVELY_VALIDATED_TOLERANCE_OVER_TESTED_1825_2350_RANGE
```

A future production threshold must instead name its scope explicitly, for example:

```text
epoch range
object set
coordinate contract
source revisions
threshold
new prospective validation set
```

No production threshold is admitted by E2.

## 8. Fail-closed classes

```text
ORACLE_UNAVAILABLE
  missing calculation adapter or required ephemeris data

DATA_IDENTITY_MISMATCH
  either seas_18 or sepl_18 identity differs from the manifest

EPHEMERIS_FALLBACK
  returned flags do not retain the required Swiss ephemeris mode

TARGET_IDENTITY_MISMATCH
  Horizons target selector does not resolve the expected numbered object

CONFIGURATION_MISMATCH
  center/frame/apparent/ecliptic mode differs

OUT_OF_COVERAGE
  requested time is outside the admitted research data range

NUMERIC_OBSERVATION
  both sources returned comparable values; residual is retained as evidence
```

## 9. E2 research status

```text
object identities                    RESOLVED
Swiss object mappings                RESOLVED
asteroid data dependency             RESOLVED
planetary data dependency            RESOLVED
binary provenance                    RESOLVED
license boundary                     RESOLVED
independent oracle                   RESOLVED
live calibration matrix              COMPLETE
live holdout matrix                  COMPLETE
prospective threshold validation     COMPLETE / FAILED AS EVIDENCE
universal numeric tolerance          REJECTED FOR TESTED RANGE
research characterization            COMPLETE
production admission                 NOT GRANTED
```

Machine-readable measured evidence is retained in `extended_chart_e2_measured_validation.json`.
