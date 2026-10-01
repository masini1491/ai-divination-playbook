# Civil-Time Normalization Contract

Authority: **CROSS-METHOD DETERMINISTIC INPUT CONTRACT / NO METHOD CALCULATION OR INTERPRETATION AUTHORITY**

This contract defines the shared civil-time identity and normalization semantics that deterministic divination methods may consume. It does **not** admit any Astrology or Zi Wei calculation by itself, does not choose a birthplace from free text, and does not authorize true-solar-time correction.

## 1. Scope

The shared boundary is:

```text
local civil datetime
+ explicit/admitted IANA timezone identity
+ optional explicit ambiguity evidence
→ validated local civil datetime
+ resolved UTC instant
+ timezone provenance
```

The contract answers only:

- whether the supplied wall time exists in the named timezone;
- whether it is unique or DST-ambiguous;
- which exact UTC instant corresponds to the admitted local civil time;
- which provenance must survive into downstream method-specific calculation.

Method owners remain responsible for how those validated facts are used.

## 2. Input identity

Minimum input:

```text
local_datetime  = naive ISO-8601 local civil wall time
timezone_name   = explicit/admitted IANA timezone identity
```

Rules:

1. `local_datetime` must not carry its own UTC offset when `timezone_name` owns resolution.
2. A numeric fixed offset such as `+08:00` or `-05:00` is not, by itself, an admitted civil-time timezone identity because it does not encode historical/future transition rules.
3. Birthplace→timezone resolution is a separate resolver responsibility. A method/runtime must not silently guess an IANA timezone from a place string.
4. If a method has an admitted place resolver that returns an IANA timezone, that resolved identity may feed this contract with its resolver provenance preserved.
5. Method-specific accepted date ranges remain owned by the consuming method/provider.

## 3. DST-safe local wall-time resolution

An implementation must distinguish three states by checking the named timezone's actual civil-time rules:

### UNIQUE

Exactly one UTC instant round-trips to the supplied local wall time.

→ admit the local civil time and its resolved UTC instant.

### NONEXISTENT

No UTC instant round-trips to the supplied wall time, as during a forward DST gap.

→ fail closed.

The implementation must not silently shift the wall time forward/backward to the nearest valid instant.

### AMBIGUOUS

Two distinct UTC instants round-trip to the same supplied wall time, as during a backward DST fold.

Default behavior:

→ fail closed unless the caller supplies an explicitly admitted disambiguation input.

Future disambiguation may use an explicit fold identity, historical UTC offset, or other deterministic evidence, but the accepted selector/schema and validation rules require separate implementation/admission. A model must not choose a fold from context or probability.

## 4. Required normalized facts

A shared normalizer should preserve enough information for downstream methods to prove what was resolved:

```text
source_local_datetime
validated_local_datetime
timezone_name
resolved_utc_offset
resolved_utc_instant
fold / ambiguity state
timezone-rule provenance when materially required for reproducibility
```

The normalized result must keep **local civil identity** and **UTC instant identity** as separate facts. Converting to UTC does not erase or replace the original validated local calendar fields.

If exact reproducibility materially depends on the timezone database, the implementation/admission layer must expose the applicable timezone-data source/version or another deterministic identity sufficient to reproduce the resolution. This contract does not prescribe one runtime packaging strategy.

## 5. Method consumption boundary

### Astrology

Astrology may use the resolved UTC instant for astronomical calculations while preserving the validated local civil datetime and timezone provenance.

Current Astrology production already provides evidence for the core semantics of this contract:

- IANA timezone input;
- `Australia/Sydney` production fixture;
- DST-nonexistent `America/New_York` wall time fails closed;
- DST-ambiguous `America/New_York` wall time fails closed;
- fixed offset is not accepted as timezone identity.

Those method-local behaviors remain regression precedent/evidence; the canonical shared implementation is `tools/civil_time_normalizer.py` under `admissions/shared/CIVIL_TIME_NORMALIZER_ADMISSION_V1.json`.

### Zi Wei

Zi Wei must consume the **validated local civil Gregorian fields** when performing Gregorian→lunar normalization.

The resolved UTC instant is provenance / identity evidence; it must **not** replace the local Gregorian year/month/day/hour before lunar conversion merely because UTC is canonical for instant identity.

Therefore:

```text
shared civil-time validation
→ validated local Gregorian datetime
→ Zi Wei Gregorian→lunar adapter
→ Zi Wei-specific rat-hour / leap-month / other admitted policies
```

Zi Wei may consume this contract only through its own production admission. Current Zi Wei Gregorian admission binds validated local Gregorian fields to the method-owned Gregorian→lunar layer; the resolved UTC instant remains provenance and is not used to rebase calendar fields.

## 6. True-solar-time separation

Ordinary civil-time normalization and true-solar-time correction are different policies.

This contract:

- does not calculate longitude-based solar-time correction;
- does not choose apparent/mean solar time;
- does not silently replace civil time with true solar time.

Zi Wei true-solar-time work remains separately owned by `ZW-P2-040` and requires explicit profile/policy/evidence.

## 7. Production implementation / consumer admission boundary

Canonical shared implementation:

```text
tools/civil_time_normalizer.py
admissions/shared/CIVIL_TIME_NORMALIZER_ADMISSION_V1.json
adapter: civil-time-zoneinfo-v1@1.0.0
```

Current consumer admission is intentionally asymmetric:

- Astrology: **PRODUCTION_ADMITTED consumer** through `tools/astrology_provider.py`; the provider keeps its existing output contract while delegating local wall-time resolution to the shared adapter.
- Zi Wei: **NOT_ADMITTED consumer** until `ZW-P2-030` separately validates overseas Gregorian→lunar coverage/parity and updates its method-owned admission.

Shared adapter admission does **not**:

- move Astrology astronomical calculation or interpretation authority into this file;
- grant Zi Wei calculation/interpretation authority by itself;
- admit DST-fold disambiguation;
- admit birthplace timezone guessing;
- change true-solar-time policy.

The shared adapter preserves validated local civil identity and resolved UTC identity; each method remains responsible for its downstream use.

## 8. Coordination ownership

Canonical shared coordination owner:

```text
ASTROLOGY_BACKLOG.md#AST-SHARED-003
```

Reason: Astrology already carries production evidence for the shared IANA/DST semantics and is the first implementation consumer/extractor.

Zi Wei records only a pointer/dependency from `ZW-P2-030`; it must not maintain a divergent copy of the shared contract status.
