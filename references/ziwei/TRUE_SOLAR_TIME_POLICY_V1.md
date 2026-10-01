# Zi Wei True-Solar-Time Policy v1

Authority: **RESEARCH EVIDENCE + PRODUCTION POLICY RATIONALE**

This record closes the research/policy decision behind `ZW-P2-040`. Production
authority is owned separately by `admissions/ziwei/ZIWEI_TRUE_SOLAR_TIME_ADMISSION_V1.json`,
`admissions/ziwei/ZIWEI_CALENDAR_ADMISSION_V1.json` and the production runtime.

## Decision

Civil time remains the default Zi Wei clock. True solar time is an explicit,
optional profile only:

```text
profile_id = ziwei.true_solar.noaa_fractional_year_v1
clock_identity = local_apparent_solar_time
activation = explicit profile + explicit longitude
default = false
```

The profile is not activated from a birthplace name. It does not infer
longitude or timezone, and it does not claim that true solar time is the unique
traditional Zi Wei rule.

## Technical model

The admitted profile uses the NOAA Global Monitoring Laboratory fractional-year
equation-of-time approximation. Longitude is east-positive.

```text
gamma = 2*pi/N * (day_of_year - 1 + (fractional_hour - 12)/24)

eqtime_minutes =
  229.18 * (
    0.000075
    + 0.001868*cos(gamma)
    - 0.032077*sin(gamma)
    - 0.014615*cos(2*gamma)
    - 0.040849*sin(2*gamma)
  )

longitude_correction_minutes =
  4*longitude_deg - 60*resolved_utc_offset_hours

true_solar_offset_minutes =
  eqtime_minutes + longitude_correction_minutes
```

The result is rounded to the nearest second, half away from zero.

This is **local apparent solar time**: longitude correction plus equation of
time. A longitude-only local-mean-solar-time profile is not admitted by v1.

## Pipeline boundary

```text
source Gregorian civil wall time + explicit IANA timezone
→ shared civil-time-zoneinfo-v1 validation
→ validated local civil fields + resolved UTC offset
→ explicit longitude + true-solar profile
→ local apparent solar Gregorian fields
→ existing Gregorian→lunar interval dataset
→ Zi Wei next_day_at_23 / split_after_day_15
→ existing natal / temporal runtime
```

The resolved UTC instant remains civil-time provenance. It is not recomputed
from the apparent-solar clock, because apparent solar time is a calculation
coordinate rather than a second civil timezone identity.

## Input and provenance

Required only when the optional profile is enabled:

- exact supported profile id;
- explicit longitude in decimal degrees, east positive;
- an already-valid explicit IANA timezone.

Latitude and elevation are not required by this clock correction. They remain
outside this profile.

The output must preserve both the source civil local datetime and corrected
apparent-solar local datetime, together with longitude, resolved UTC offset,
equation-of-time value and total correction.

## Boundary behavior

The corrected solar datetime owns the Gregorian date/hour passed to the lunar
lookup and the later Zi Wei Rat-hour policy. Therefore a correction may cross
midnight and may change both the lunar date and hour branch. This is intended
and must be observable in provenance.

If the corrected Gregorian date leaves the admitted 1900-01-01..2100-12-31
calendar-data range, execution fails closed.

DST is not a separate solar-time rule. The profile consumes the UTC offset
already resolved by the shared civil-time normalizer for the exact local civil
input. Nonexistent/ambiguous civil wall times therefore fail before solar
correction.

## Non-goals

- no birthplace → longitude resolver;
- no birthplace → timezone resolver;
- no latitude/elevation solar-position model;
- no local-mean-solar-time alternative in v1;
- no claim that true solar time improves scientific or predictive validity;
- no silent migration of existing civil-time readings to this profile.

## Evidence interpretation

The NOAA formula is technical astronomy/timekeeping evidence for a reproducible
apparent-solar clock correction. It is **not** evidence that one Zi Wei
tradition is historically unique or objectively more accurate.

The project admission is therefore a named optional calculation profile, not a
universal doctrinal default.
