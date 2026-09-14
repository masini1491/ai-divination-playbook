# Astrology Extended Chart Facts Phase E2｜Ephemeris-required Objects

Status: **REFERENCE-ONLY / RESEARCH / E2 PARTIAL**

Reviewed Playbook baseline: `masini1491/ai-divination-playbook@b03c24a57c4ecf711e93d80c9cb49f402308bc75`

Architecture owner: [`EXTENDED_CHART_FACTS_RESEARCH_ARCHITECTURE.md`](EXTENDED_CHART_FACTS_RESEARCH_ARCHITECTURE.md)

## 1. Scope

Phase E2 studies deterministic calculation requirements for:

```text
Chiron
Ceres
Pallas
Juno
Vesta
```

These are not derivable from current Production v1 parent facts. They require an external ephemeris-capable calculation authority or a separately implemented and validated astronomical model.

No production dependency or schema change is admitted by this file.

## 2. Current Production v1 capability

Current `tools/astrology_provider.py` uses Astronomy Engine for the admitted core object set and does not expose Chiron / Ceres / Pallas / Juno / Vesta.

Repository search of pinned `cosinekitty/astronomy@865d3da7d8112bbc7911238052c6af4aaf877181` found no direct support for these five object names in the reviewed source surface.

Research conclusion:

```text
existing Astronomy Engine production core
→ sufficient for currently admitted bodies
→ not sufficient evidence for E2 objects
```

Do not silently invent these positions from language-model memory.

## 3. Swiss Ephemeris family evidence

Pinned `astrorigin/pyswisseph@91ec65631badc7faf4a4b913570c944a4c1b101d` documents:

- asteroid/extended-body calculation through Swiss Ephemeris;
- an explicit ephemeris file path;
- test-suite dependency on `seas_18.se1` plus other ephemeris resources;
- AGPL-3.0 for pyswisseph and a dual-license boundary for underlying Swiss Ephemeris.

Pinned `theriftlab/immanuel-python@eba98099b7724598064113ffa1322e78dc4bccf6` explicitly maps:

```text
Chiron → swe.CHIRON
Ceres  → swe.CERES
Pallas → swe.PALLAS
Juno   → swe.JUNO
Vesta  → swe.VESTA
```

and calls `swe.calc_ut()` for their ecliptic positions.

This is strong architecture evidence that the five E2 objects can share one ephemeris-object fact family while retaining distinct object ids.

## 4. Local availability probe

A local research probe using installed `pyswisseph 2.10.03` at synthetic Julian date J2000 attempted:

```text
swe.CHIRON
swe.CERES
swe.PALLAS
swe.JUNO
swe.VESTA
```

All five calls failed closed with the same material dependency error:

```text
SwissEph file 'seas_18.se1' not found
```

This is a useful research result, not a defect in the five object identities.

It proves that a future E2 oracle environment must govern not only Python package version but also ephemeris-data availability/provenance.

## 5. Required provenance for E2 facts

A future deterministic object fact should preserve at least:

```text
object_id
calculation_provider_id
provider_version
provider_source_revision
ephemeris_data_family / revision when material
utc instant
center / coordinate convention
longitude_deg
latitude_deg when available
speed_deg_per_day when available
motion
availability
```

If an external ephemeris file is required, the file/data-family identity belongs to provenance rather than being treated as an invisible machine-local detail.

## 6. Candidate object taxonomy

Recommended research taxonomy:

```text
Chiron → centaur / special minor body
Ceres  → asteroid
Pallas → asteroid
Juno   → asteroid
Vesta  → asteroid
```

Do not force all five into `planet` merely because an external astrology package stores them beside planets.

The production schema may later choose a broader generic type, but semantic identity should remain explicit.

## 7. Cross-engine validation requirement

Production admission should not be based on a single Swiss-family wrapper agreeing with another Swiss-family wrapper because those are not independent numerical authorities.

Preferred evidence pattern:

```text
Swiss Ephemeris result
+ independent ephemeris / trusted published oracle where feasible
+ repeatable synthetic/public fixtures
```

At minimum, distinguish:

```text
same underlying Swiss engine, different wrapper
vs
independent astronomical calculation
```

when assigning evidence independence.

## 8. Tolerance research

No final E2 tolerance is admitted yet.

Future fixtures should measure angular differences separately for:

```text
Chiron
major asteroids
speed / retrograde sign
house-placement boundary sensitivity
```

A generic planet tolerance should not be copied blindly.

## 9. License boundary

Current research posture remains:

```text
pyswisseph / Swiss Ephemeris
→ REFERENCE-ONLY validation-oracle candidate
→ no production dependency adoption in E2
```

Any production adoption requires explicit resolution of AGPL / Professional License consequences and ephemeris-data redistribution/deployment requirements.

Kerykeion and Immanuel remain architecture / compatibility references and do not gain production authority from feature coverage.

## 10. E2 exit criteria

E2 can move from PARTIAL to COMPLETE only after:

1. an ephemeris-data-complete research environment exists;
2. synthetic/public fixtures are generated for all five objects;
3. exact provider/data revisions are pinned;
4. cross-engine or independent-oracle comparison is executed;
5. longitude/speed tolerance is documented;
6. failure behavior for missing ephemeris data is tested;
7. license/deployment implications are recorded.

## 11. Current conclusion

```text
Chiron identity / Swiss mapping: RESOLVED
Ceres identity / Swiss mapping: RESOLVED
Pallas identity / Swiss mapping: RESOLVED
Juno identity / Swiss mapping: RESOLVED
Vesta identity / Swiss mapping: RESOLVED
required ephemeris-data dependency: RESOLVED
numerical fixture validation: BLOCKED pending ephemeris data / independent oracle
production admission: NOT GRANTED
```

Next safe action inside E2 is to establish a research-only ephemeris-data-complete oracle environment or obtain equivalent independent numerical fixtures. Until then, fail closed rather than fabricate values.
