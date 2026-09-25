# Zi Wei Calendar Data Architecture POC

Authority: **RESEARCH / ARCHITECTURE EVIDENCE ONLY — NOT PRODUCTION ADMISSION**

This note records the method-scoped calendar A/B evaluation under the repository
topology owned by `REPOSITORY_ARCHITECTURE.md`. It does not create a second
repository-layer architecture policy.

## Current production dependency audit

At the evaluated baseline, `tools/ziwei_calendar_provider.py` imports only
`Solar` from `lunar_python`. The production call surface is:

```text
Solar.fromYmdHms(...)
→ Solar.getLunar()
→ Lunar.getYear()
→ Lunar.getMonth()
→ Lunar.getDay()
→ Lunar.getTimeZhi()

23:00 policy only:
Solar.nextDay(1)
```

Current production outputs actually consumed by the natal runtime are:

```text
lunar_year
normalized lunar_month
lunar_day
hour_branch
calendar_provenance
leap_month_identity
```

The calendar adapter also exposes raw/policy lunar records for provenance and
debugging. It does not currently consume solar terms, JieQi, BaZi, EightChar,
true-solar time, automatic timezone lookup, or an upstream year Gan/Zhi API.
The natal provider derives the year stem/branch project-side from the normalized
lunar year.

Project-owned policy remains separate from Gregorian→lunar conversion:

- `Asia/Taipei` civil-time acceptance;
- `next_day_at_23`;
- `split_after_day_15`;
- hour-branch mapping;
- no true-solar-time correction.

## A/B engineering comparison

### A — execute upstream implementation in production

Current A is already production-admitted and deterministic. Its main cost is
transport/runtime breadth rather than semantic necessity: the ChatGPT Zi Wei
bundle currently carries 34 `lunar_python` runtime files. The evaluated bundle
contains 373,725 dependency bytes; the full uncompressed archive is 515,239
bytes and the generated bundle JSON is about 242 KB.

A remains the production fallback until B passes a separate admission gate.

### B — build-time upstream → repo-local deterministic calendar data

The current provider's required upstream result can be represented by one
date-keyed record:

```json
{
  "lunar_year": 2023,
  "signed_lunar_month": -2,
  "lunar_day": 15
}
```

The sign preserves leap-month identity. Hour branch, 23:00 date shifting and
the split-after-day-15 logical month remain project-owned runtime policy, so
they do not multiply the dataset by hour/minute/second.

The POC therefore uses Gregorian month shards:

```text
data/calendar/ziwei_tw_poc_v0/
  years/YYYY/MM.json
```

Ordinary lookup needs one shard. A 23:00 lookup that crosses a Gregorian month
boundary needs at most two shards. Missing shard, missing date, duplicate date,
schema mismatch or status mismatch fails closed.

## POC result / decision

**B is selected as the target calendar architecture, but is not yet production
admitted.** The current A runtime remains authoritative until the B admission
gate below is satisfied.

Reason for selecting B as target:

1. the production upstream API surface is narrow and date-deterministic;
2. current Zi Wei-specific boundary policies are already project-owned and can
   remain executable logic rather than data;
3. data growth is linear by Gregorian day, not by time-of-day;
4. bounded retrieval is one monthly shard in the ordinary case and two at the
   23:00 cross-month edge;
5. ordinary production would no longer need to import or materialize
   `lunar_python`; the package can become a build/parity dependency;
6. the current full dependency transport cost is materially larger than the
   expected one-query data payload.

This decision does **not** justify vendoring `third_party/lunar-python/**`.

## Dataset contract candidate

Current POC contract:

- source identity: `lunar_python==1.4.8`,
  `6tail/lunar-python@000c8a3d74eed098d6256a28fdd51b869324c559`;
- timezone scope: production input remains `Asia/Taipei` civil time; stored
  calendar records are Gregorian-date keyed;
- shard key: Gregorian `YYYY/MM`;
- record key: Gregorian day-of-month;
- leap representation: signed lunar month, negative means leap month;
- logical Zi Wei month: computed project-side by `split_after_day_15`;
- 23:00 boundary: project-side next-Gregorian-day query;
- hour branch: project-side deterministic mapping;
- serialization: UTF-8 JSON, sorted keys, stable trailing newline;
- integrity: per-shard SHA-256 plus deterministic aggregate hash;
- failure mode: missing/corrupt/mismatched shard or record → fail closed;
- generator: project-owned `tools/ziwei_calendar_data_poc.py`;
- runtime resolver: the same POC module demonstrates dependency-free lookup.

The committed fixture shards are deliberately partial and remain
`RESEARCH_POC_NOT_PRODUCTION`.

## Supported date range

Production range is **not changed by this POC**. The existing production
manifest does not state an explicit Gregorian min/max even though its typed
input validates a Python `datetime` before invoking the dependency.

For feasibility testing only, the POC parity suite probes a candidate
1900-01-01 through 2100-12-31 window, including both edges plus a deterministic
random corpus. That window is not an admission decision and must not silently
narrow or broaden current production behavior.

Before B production admission, choose and document one explicit range based on
product requirements plus verified provider parity. If preserving a broader
current execution range is required, generator/runtime cost must be measured
for that broader range rather than inferred from the POC window.

## Parity gate before production admission

The B replacement gate must include machine-generated comparison against the
current admitted provider for:

- ordinary dates;
- Gregorian month/year crossover;
- lunar month boundaries;
- lunar-year crossover;
- leap months;
- leap-month day 15/16 boundary;
- 23:00 next-day behavior;
- all 24 civil hours / all 12 hour branches;
- selected historical edge fixtures;
- explicit supported-range edges;
- deterministic random corpus;
- shard missing/corrupt/duplicate fail-closed behavior;
- deterministic rebuild and aggregate-hash verification.

The first POC test intentionally generates temporary month shards from the
pinned build-time dependency and resolves them through the dependency-free data
path before comparing normalized facts with the current admitted provider.

## Production migration gate

Only after parity/range/size evidence is sufficient should a later bounded
admission change:

```text
production:
data/calendar/<admitted-version>/**
+ project-owned calendar resolver

build / parity validation:
lunar_python==1.4.8
```

At that point update the existing calendar admission manifest, materialization
contract/bundle, requirements classification and production tests together.
Until then, `ZIWEI_CALENDAR_ADMISSION_V1.json` and
`tools/ziwei_calendar_provider.py` remain current production authority.

This work is independent from `ZW-P1-020` Four Transformations admission.
