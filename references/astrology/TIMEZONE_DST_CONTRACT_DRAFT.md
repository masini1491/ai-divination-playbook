# Timezone / DST Input Contract Draft｜時區與夏令時間輸入契約草案

Status: **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**

This document is a research candidate only. It does not modify the Playbook's production input contract or method routing.

## 1. Purpose

Astrology calculation is highly time-sensitive. A civil timestamp such as:

```text
2026-10-25 02:30
```

is not a complete instant until timezone resolution succeeds.

The contract candidate separates:

```text
civil-time input
→ timezone resolution
→ canonical UTC instant / interval
→ ephemeris calculation
→ local-time rendering
```

Timezone resolution belongs before astronomical calculation.

## 2. Accepted candidate input forms

### A. Exact UTC instant

Example:

```text
2026-07-14T03:53:27Z
```

Candidate status:

```text
unambiguous
```

No local-time resolution is required.

### B. Offset-aware instant

Example:

```text
2026-07-14T11:53:27+08:00
```

This resolves one exact instant.

Boundary:

> The offset does not by itself identify the civil timezone rules for other dates.

If future local-date searches or historical conversion are needed, an IANA zone should also be supplied.

### C. Local wall time + IANA timezone

Example:

```text
local_wall_time: 2026-07-01 12:00
iana_timezone: Europe/Stockholm
```

Resolution may yield:

```text
unique
ambiguous
nonexistent
```

Only `unique` may proceed without additional disambiguation.

### D. Local date + IANA timezone

Example:

```text
local_date: 2026-03-29
iana_timezone: Europe/Stockholm
```

Resolve to:

```text
[start local midnight, next local midnight)
→ convert both boundaries to UTC
```

Do not assume duration = 24 hours.

## 3. Fail-closed states

### Nonexistent wall time

A spring-forward gap may contain local timestamps that never occurred.

Candidate behavior:

```text
resolution_status = nonexistent
resolved_utc = null
calculation_allowed = false
```

Do not silently normalize forward or backward.

### Ambiguous wall time

A fall-back fold may map one local wall time to two UTC instants.

Candidate behavior:

```text
resolution_status = ambiguous
candidates = [instant_1, instant_2]
calculation_allowed = false
```

Proceed only after explicit disambiguation, such as:

```text
fold = 0 | 1
```

or another user/source value that uniquely identifies the intended instant.

## 4. Canonical storage candidate

After successful resolution:

```text
TimeProvenance
- input_kind
- original_local_value
- iana_timezone
- fold
- resolved_utc
- utc_offset_at_resolved_time
- resolution_status
- timezone_source
- tzdb_version_if_available
```

The engine should calculate from `resolved_utc`, not by reinterpreting the original display string independently.

## 5. Fixed-offset boundary

A fixed offset is sufficient to encode an exact instant when the local time and offset are both explicit.

It is not sufficient to model:

- DST changes;
- historical timezone transitions;
- future local-date search windows;
- ambiguous / nonexistent wall times;
- location-based civil-time rules.

Therefore:

```text
offset != timezone identity
```

Do not infer an IANA zone from an offset alone.

## 6. Local-day search candidate

For a user-facing local date:

```text
D @ zone Z
```

derive:

```text
start = D 00:00 in Z
end   = (D + 1 day) 00:00 in Z
search_interval = [start_utc, end_utc)
```

This preserves 23-hour and 25-hour DST days.

## 7. Event storage vs presentation

Candidate rule:

```text
exact event fact
→ UTC

display
→ UTC converted to requested IANA timezone
```

Do not store independently-calculated local and UTC event times as equal authorities.

The local value is a rendering of the UTC fact plus timezone provenance.

## 8. Birth-time application

The same resolution rules apply to natal birth time.

A birth record containing:

```text
date
clock time
place
```

still requires an explicit timezone-resolution step.

If the civil time is ambiguous or nonexistent under the selected timezone rules:

```text
natal instant unresolved
→ downstream angle / house calculation unavailable
```

The model must not guess a fold.

## 9. Unknown birth time boundary

Unknown birth time is different from timezone ambiguity.

```text
unknown birth time
→ civil clock time missing

ambiguous DST fold
→ civil clock time known but maps to two instants
```

These states must not share one generic `unknown` flag.

Candidate status families:

```text
birth_time_certainty:
  exact
  bounded
  unknown

timezone_resolution:
  unique
  ambiguous
  nonexistent
  not_applicable
```

## 10. Runtime provenance

Timezone behavior can change when a runtime's timezone database changes.

A future implementation should preserve when available:

```text
timezone library / resolver
IANA timezone key
tzdb source
tzdb version
```

This is particularly important for historical charts and reproducibility across environments.

## 11. User-facing error semantics

Research candidate messages should be precise:

```text
nonexistent:
"The local time falls inside a daylight-saving transition gap and does not map to a real instant."

ambiguous:
"The local time occurred twice because clocks moved backward. A fold/offset choice is required."
```

Avoid silently choosing an instant and presenting the chart as exact.

## 12. Evidence basis

This draft is supported by:

- the executable results in [`TRANSIT_NATAL_INGRESS_TIMEZONE_RESULTS.md`](TRANSIT_NATAL_INGRESS_TIMEZONE_RESULTS.md);
- the companion [`transit_natal_timezone_probe.py`](transit_natal_timezone_probe.py);
- pinned AstroScript behavior that rejects ambiguous/nonexistent natal or search timestamps rather than guessing.

It remains a Cold research contract and has no production authority.

**Current state: REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**
