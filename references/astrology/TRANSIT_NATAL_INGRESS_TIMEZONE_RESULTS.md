# Transit-to-Natal / Ingress / Timezone-DST Results｜行運對本命／進入星座／時區 DST 研究結果

Status: **REFERENCE-ONLY / RESEARCH RESULT｜僅供參考／研究結果**

Playbook baseline at branch start: `masini1491/ai-divination-playbook@490e7440b2926738e305b8096f39082536ca9cff`

本檔延續 Astrology Cold research line，驗證：

```text
transit body → fixed natal longitude
zodiac ingress / retrograde return / re-ingress
local wall time → UTC resolution
DST gap / fold behavior
local-date search window → UTC interval
```

它不建立 production engine authority、production timezone policy、orb policy、interpretation policy 或 routing admission。

## 1. External reference architecture

Pinned reference:

```text
Shoresh613/astro-script@18f4a3e291a557b2ef47c7fb5e27b108f1bcf4b7
```

Reviewed tests / implementation show several useful responsibility patterns:

- `NatalAspectCondition` treats a natal planet / point as a fixed target while the transit body moves through the search window.
- Transit-to-natal angles and house cusps are treated separately from planet targets.
- A natal chart with unknown birth time may use a placeholder only for bounded planetary work, while house / cusp / angle dependent queries are rejected.
- Local timezone parsing explicitly rejects ambiguous / nonexistent local timestamps instead of silently guessing.
- Search output is normalized through UTC-aware datetimes.

These are reference patterns only. The source registry's unresolved AstroScript license discrepancy remains unchanged, so no source code is copied.

## 2. Local research runtime

Companion executable:

[`transit_natal_timezone_probe.py`](transit_natal_timezone_probe.py)

Runtime:

```text
pyswisseph: 2.10.03
requested flags: FLG_SWIEPH | FLG_SPEED = 258
effective returned flags: 260 = FLG_MOSEPH | FLG_SPEED
zodiac: tropical
center: geocentric
timezone implementation used by probe: Python zoneinfo
```

As in prior rounds, `.se1` files are unavailable in this runtime. Numeric astrology results below are therefore **Moshier fallback** results.

## 3. Transit to a fixed natal longitude

To avoid storing personal birth data, the probe uses a synthetic source-neutral natal target:

```text
target_type: natal_planet_longitude_fixture
longitude: 110.0°
moving body: Mercury
aspect: conjunction
search window: 2026-06-01..2026-08-10 UTC
```

The same fixed target is reached three times because Mercury changes direction:

| Passage | Exact UTC | Motion | Speed |
|---|---|---|---:|
| 1 | 2026-06-16 15:44:17.088 | direct | +0.913903°/day |
| 2 | 2026-07-14 03:53:27.175 | retrograde | −0.628341°/day |
| 3 | 2026-08-01 13:51:40.891 | direct | +0.858989°/day |

Angular residuals at the solved roots are on the order of `10^-9` degrees in this runtime.

### Research implication

A transit-to-natal event identity cannot be only:

```text
Mercury conjunct natal target
```

because one retrograde cycle may produce multiple exact passages.

A future event fact needs at least:

```text
moving_body
target_id / target_longitude
aspect_branch
exact_time_utc
motion_direction
passage identity / sequence
engine provenance
```

## 4. Natal-target uncertainty propagates into timing uncertainty

A separate **test parameter** widens the synthetic natal target from exactly `110.0°` to:

```text
109.5° .. 110.5°
```

This is not an adopted natal uncertainty rule. It only demonstrates propagation.

For the three Mercury passages:

| Center passage | Earliest possible root | Latest possible root | Timing span |
|---|---|---|---:|
| 2026-06-16 15:44 UTC | 2026-06-16 02:49 UTC | 2026-06-17 05:06 UTC | 26.28 h |
| 2026-07-14 03:53 UTC | 2026-07-13 08:59 UTC | 2026-07-14 23:16 UTC | 38.28 h |
| 2026-08-01 13:51 UTC | 2026-07-31 23:23 UTC | 2026-08-02 03:23 UTC | 28.00 h |

The retrograde passage has the largest timing spread because the moving body is slower in longitude near that passage.

### Research implication

If a natal target is uncertain, a future deterministic layer should not return one falsely precise exact transit time.

Candidate behavior:

```text
exact natal target
→ exact transit root

bounded natal target interval
→ bounded transit-time interval / uncertainty

target uncertainty crosses event topology or creates/removes passages
→ ambiguous / unavailable until resolved
```

This is especially relevant to unknown birth time and fast natal factors such as the Moon.

## 5. Zodiac ingress / retrograde return / re-ingress

The probe also searches a pure sign-boundary geometry case:

```text
body: Venus
boundary: tropical 210.0°
sign pair: Libra / Scorpio
```

Three crossings occur in 2026:

| Exact UTC | Direction | Semantic geometry |
|---|---|---|
| 2026-09-10 08:06:48.360 | direct | Libra → Scorpio |
| 2026-10-25 09:09:47.887 | retrograde | Scorpio → Libra |
| 2026-12-04 08:12:43.264 | direct | Libra → Scorpio |

This demonstrates that a sign boundary is not a one-time yearly event for a retrograding body.

### Candidate ingress fact

```text
IngressEvent
- body
- zodiac_system
- boundary_longitude
- from_sign
- to_sign
- exact_time_utc
- motion_direction
- event_kind:
    direct_ingress
    retrograde_return_to_previous_sign
    direct_reingress
- engine provenance
```

The language labels are derived from deterministic geometry + speed sign. Their interpretation remains separate.

## 6. UTC fact vs local-time rendering

One exact Mercury passage:

```text
UTC               2026-07-14 03:53:27.175
Asia/Taipei       2026-07-14 11:53:27.175 +08:00
Europe/Stockholm  2026-07-14 05:53:27.175 +02:00
```

These are three renderings of the **same instant**.

Research boundary:

```text
event exactness
→ store / compare in UTC

user-facing display
→ render from UTC through an explicit IANA timezone
```

Local display must never become a second independent event fact.

## 7. DST gap / fold classification

The probe classifies local wall times by round-tripping both `fold=0` and `fold=1` through UTC.

### Nonexistent local time

```text
Europe/Stockholm
2026-03-29 02:30
→ nonexistent
```

Neither fold candidate round-trips to the original wall time.

Therefore a fail-closed input contract should reject it rather than silently shifting to 01:30 or 03:30.

### Ambiguous local time

```text
Europe/Stockholm
2026-10-25 02:30
→ ambiguous
```

Two valid instants exist:

```text
fold 0 → 2026-10-25 00:30 UTC  (+02:00)
fold 1 → 2026-10-25 01:30 UTC  (+01:00)
```

The system cannot choose one without an explicit disambiguation rule or user-provided resolution.

### Unique local time

```text
Europe/Stockholm 2026-07-01 12:00
→ unique
→ 2026-07-01 10:00 UTC
→ effective offset +02:00
```

and:

```text
Asia/Taipei 2026-09-12 23:18
→ unique
→ 2026-09-12 15:18 UTC
→ effective offset +08:00
```

## 8. Fixed UTC offset is not an IANA timezone

For:

```text
2026-07-01 12:00 local
```

the two interpretations differ:

```text
Europe/Stockholm
→ UTC 10:00
→ summer offset +02:00

fixed +01:00
→ UTC 11:00
```

Difference:

```text
1 hour
```

Therefore:

> A fixed offset may describe one instant, but it does not encode timezone transition rules for historical / future dates or search windows.

A future input contract should not replace an IANA timezone with a guessed fixed offset when the civil location/timezone is known.

## 9. Local-date windows are not always 24 hours

For search requests such as:

```text
"that day"
"today"
"on 2026-03-29"
```

the deterministic search interval should be:

```text
[local midnight, next local midnight)
→ convert both boundaries to UTC
```

Observed `Europe/Stockholm` windows:

| Local date | UTC start | UTC end exclusive | Duration |
|---|---|---|---:|
| 2026-03-29 | 2026-03-28 23:00 | 2026-03-29 22:00 | 23 h |
| 2026-10-25 | 2026-10-24 22:00 | 2026-10-25 23:00 | 25 h |
| 2026-07-14 | 2026-07-13 22:00 | 2026-07-14 22:00 | 24 h |

`Asia/Taipei` on 2026-07-14 is a normal 24-hour interval:

```text
2026-07-13 16:00 UTC
→ 2026-07-14 16:00 UTC
```

Research implication:

```text
local date + zone
!= UTC date
!= always 24 hours
```

## 10. Candidate provenance additions

The current evidence supports adding these fields to a future Structured Astrology Fact / TransitEvent design:

```text
time_input:
  input_kind: utc_instant | local_wall_time | local_date_window
  local_value
  iana_timezone
  resolved_utc
  utc_offset_at_resolved_time
  fold: null | 0 | 1
  resolution_status: unique | ambiguous | nonexistent
  timezone_source
  tzdb_version_if_available

natal_target:
  target_type
  target_id
  longitude
  uncertainty_interval
  birth_time_dependency
  source_engine / source_revision

event:
  exact_time_utc
  passage_index / passage_identity
  motion_direction
  local_renderings: derived-only
```

## 11. Failure modes exposed by this round

### 11.1 Fixed target treated as known when it is uncertain

A transit root can move by many hours when target longitude changes by fractions of a degree.

### 11.2 Retrograde collapses multiple passages

Deduplicating only by body + aspect + natal target loses real event structure.

### 11.3 Sign ingress assumes monotonic direct motion

A retrograde body can leave the sign and later re-enter it.

### 11.4 DST gap silently normalized

A nonexistent civil time must not be auto-corrected without provenance.

### 11.5 DST fold silently picks one instant

An ambiguous wall time needs explicit disambiguation.

### 11.6 Search window assumed to be 24 hours

DST local days can be 23 or 25 hours.

### 11.7 UTC offset treated as timezone identity

`+01:00` and `Europe/Stockholm` are not equivalent across the calendar.

## 12. What this round supports

Current evidence supports:

1. transit-to-natal planet geometry can use an immutable natal target fact;
2. transit event identity needs passage identity because retrogrades can create three exact roots;
3. uncertainty in the natal target must propagate into timing uncertainty;
4. sign ingress / retrograde return / re-ingress can be deterministic event facts;
5. exact event time should be canonicalized in UTC;
6. user-facing civil time should use an explicit IANA timezone;
7. nonexistent local times should fail closed;
8. ambiguous local times require explicit disambiguation;
9. local-date search windows must be resolved from local midnights, not forced to 24 hours;
10. fixed offsets must not silently substitute for IANA timezone rules.

## 13. Remaining evidence gaps

Still open:

```text
cross-engine transit-to-fixed-natal timing benchmark
cross-engine ingress timing benchmark
.se1-backed SWIEPH rerun
natal Moon uncertainty propagation from unknown birth time
natal angle / cusp timing with known-time fixtures
historical timezone / pre-standard-time provenance
tzdb version provenance across runtime environments
sidereal ingress / ayanamsa contract
topocentric transit-to-natal cases where relevant
event-time tolerance selection
```

No production tolerance or production timezone policy is selected by this result.

**Current state: REFERENCE-ONLY / RESEARCH / NOT PRODUCTION-ROUTABLE**
