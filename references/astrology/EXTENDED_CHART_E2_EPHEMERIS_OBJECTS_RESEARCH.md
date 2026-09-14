# Astrology Extended Chart Facts Phase E2｜Ephemeris-required Objects

Status: **REFERENCE-ONLY / RESEARCH COMPLETE WITH REJECTED GLOBAL TOLERANCE / NOT PRODUCTION-ADMITTED**

Reviewed Playbook baseline: `masini1491/ai-divination-playbook@ed639c52d64556339e2848dc93ae5722dbc771c1`

Architecture owner: [`EXTENDED_CHART_FACTS_RESEARCH_ARCHITECTURE.md`](EXTENDED_CHART_FACTS_RESEARCH_ARCHITECTURE.md)

Measured oracle contract: [`EXTENDED_CHART_E2_ORACLE_ENVIRONMENT.md`](EXTENDED_CHART_E2_ORACLE_ENVIRONMENT.md)

Machine evidence: [`extended_chart_e2_measured_validation.json`](extended_chart_e2_measured_validation.json)

## 1. Scope

Phase E2 studies deterministic calculation requirements for:

```text
Chiron
Ceres
Pallas
Juno
Vesta
```

These objects are not derivable from current Production v1 parent facts. No production dependency or schema change is admitted by E2.

## 2. Current Production v1 capability

Current `tools/astrology_provider.py` uses Astronomy Engine for the admitted core object set and does not expose Chiron / Ceres / Pallas / Juno / Vesta.

The reviewed Astronomy Engine revision does not provide sufficient evidence for these five objects. Therefore:

```text
current production astronomy core
→ remains unchanged
→ E2 objects remain unsupported in Production v1
```

## 3. Resolved object identities

Swiss-family mappings independently reviewed through pyswisseph / Immanuel references and then exercised in the live E2 probe:

```text
Chiron → swe.CHIRON
Ceres  → swe.CERES
Pallas → swe.PALLAS
Juno   → swe.JUNO
Vesta  → swe.VESTA
```

Recommended semantic taxonomy remains:

```text
Chiron → centaur / special minor body
Ceres  → asteroid
Pallas → asteroid
Juno   → asteroid
Vesta  → asteroid
```

Do not collapse all five into `planet` merely because a wrapper stores them beside planets.

## 4. Ephemeris dependency characterization

Initial local execution established that the objects require Swiss ephemeris data rather than package constants alone.

Subsequent live execution refined that finding:

```text
seas_18.se1 only
→ insufficient for intended geocentric Swiss-mode result
→ returned flags showed fallback

seas_18.se1 + matching sepl_18.se1
→ required Swiss mode retained
→ returned_flags = 258 (FLG_SWIEPH | FLG_SPEED)
```

Pinned data identities:

```text
aloistr/swisseph@91339e55d2351f32548d8a8d5bca6aa93b4f6da7

seas_18.se1
  blob 8f900cab7e557e4c41f758a6bf3a3c3967e7e3db
  size 223004

sepl_18.se1
  blob 786702cd04506371ee6223af1ebac02d54c848b8
  size 484061
```

Both file identities are part of the E2 numerical provenance contract.

## 5. Independent numerical oracle

NASA/JPL Horizons was used as the independent comparison source:

```text
Earth geocenter: 500@399
EPHEM_TYPE: OBSERVER
QUANTITIES: 31
APPARENT: AIRLESS
TIME_TYPE: UT
EXTRA_PREC: YES
CSV_FORMAT: YES
```

Observed live API signature during the measured runs:

```text
source: NASA/JPL Horizons API
version: 1.2
```

Longitude speed was derived independently with a central finite difference at `t - 1h` and `t + 1h`.

## 6. Measured evidence layers

Three layers were executed with five objects per instant:

```text
Calibration: 4 instants / 20 object-time rows
Holdout:     4 instants / 20 object-time rows
Prospective: 4 instants / 20 object-time rows
```

Calibration residual envelope:

```text
max longitude ≈ 1.220 arcsec
max speed     ≈ 5.148e-6 deg/day
```

Holdout residual envelope:

```text
max longitude ≈ 2.965 arcsec
max speed     ≈ 5.559e-6 deg/day
```

## 7. Prospective tolerance test

After calibration and holdout characterization, the following candidate threshold was frozen before the prospective dates were executed:

```text
longitude <= 5 arcsec
speed     <= 1e-5 deg/day
```

The candidate failed at the far-future `2350-05-23T21:00:00Z` validation instant:

```text
Ceres longitude ≈ 5.791 arcsec; speed ≈ 3.195e-5 deg/day
Juno  longitude ≈ 7.805 arcsec
Vesta longitude ≈ 6.091 arcsec
```

The other 17 prospective rows remained inside the frozen candidate threshold.

Research rule:

> Do not widen a failed prospective threshold after seeing its failures and then relabel the wider value as prospectively validated.

Therefore E2 does **not** admit one universal cross-engine numeric tolerance over the full tested 1825–2350 span.

## 8. Required provenance for future E2 facts

Any future deterministic E2 fact needs at least:

```text
object_id
calculation_provider_id
provider_version
provider_source_revision
ephemeris file/data identities
UTC instant
center / coordinate convention
longitude_deg
latitude_deg when available
speed_deg_per_day when available
motion
availability
```

If a required ephemeris file is missing, mismatched, or calculation flags show fallback, fail closed.

## 9. License boundary

Current research posture remains:

```text
pyswisseph / Swiss Ephemeris
→ REFERENCE-ONLY validation oracle
→ no production dependency adoption in E2
```

Swiss Ephemeris licensing/deployment consequences require a separate production decision. Kerykeion and Immanuel remain architecture / compatibility references and gain no production authority from feature coverage.

## 10. E2 exit-criteria assessment

1. ephemeris-data-complete research environment — **PASS**
2. public/synthetic fixtures for all five objects — **PASS**
3. exact provider/data revisions pinned — **PASS**
4. independent-oracle comparison executed — **PASS**
5. numeric tolerance documented — **PASS AS REJECTED GLOBAL HYPOTHESIS; NO UNIVERSAL ADMISSION**
6. missing/mismatched data failure behavior tested — **PASS**
7. license/deployment implications recorded — **PASS**

The distinction in item 5 is material: research characterization is complete, but the minimum production gate for an admitted numeric tolerance is still unmet.

## 11. E2 conclusion

```text
Chiron identity / Swiss mapping          RESOLVED
Ceres identity / Swiss mapping           RESOLVED
Pallas identity / Swiss mapping          RESOLVED
Juno identity / Swiss mapping            RESOLVED
Vesta identity / Swiss mapping           RESOLVED
asteroid ephemeris dependency            RESOLVED
planetary ephemeris dependency           RESOLVED
binary provenance                         RESOLVED
independent numerical comparison          COMPLETE
calibration / holdout characterization    COMPLETE
prospective tolerance experiment          COMPLETE / FAILED AS EVIDENCE
universal 1825-2350 tolerance             REJECTED
E2 research characterization              COMPLETE
production admission                      NOT GRANTED
```

A future production review must choose a bounded epoch/object tolerance policy and validate that policy prospectively. E2 itself does not make that product-policy choice.
