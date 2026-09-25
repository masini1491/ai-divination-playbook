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
manifest does not state an explicit Gregorian min/max. The current provider
first validates through Python `datetime`, so inputs outside Python's civil-date
range fail before the upstream calendar call; upstream success inside that
validator envelope is still a separate requirement and is not an admitted
range contract.

Pinned `lunar-python==1.4.8` itself has regression examples well outside the
modern birth-date window (including years 100, 1500, 3218, 9865 and lunar year
9997), but the upstream project does not publish one explicit public supported
year range. Therefore neither the dependency's broad executable examples nor
Python's date range may be silently promoted into this project's production
contract.

For engineering feasibility, the project has full machine parity evidence for
**1900-01-01 through 2100-12-31**. That same window is now explicitly selected
as the **candidate product-supported range** for option B. The selection is
narrower than production admission: the current option-A provider remains
authoritative until the later resolver/materialization + admission gate passes.

The exact candidate dataset is materialized at
`data/calendar/ziwei_tw_interval/v1/**`. It contains 202 Gregorian-year shards
for 1900..2101, where 2101 is the explicit policy-tail shard required to resolve
2100-12-31 at 23:00 under `next_day_at_23`. The selected dataset records 2,692
lunar-month intervals and 471,865 shard bytes. Its canonical shard aggregate
SHA-256 is
`4913a39e770afcd21eedc387523c572b8c4fc6469889c28f6ea75613f8984d79`.
The verified installed-source inventory SHA-256 for the pinned 34-file upstream
implementation is
`bf49ea69241171a8e5b5a85ca07748c88b00f5ce392f25c21617e398c9c9a712`.

This range decision does not claim that dates outside 1900..2100 are invalid in
the upstream library. It only bounds the dataset-backed candidate that this
project is preparing to admit.

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

### Full candidate-window parity evidence

Machine-readable result: `references/ziwei/ziwei_calendar_full_parity_1900_2100.json`.

Strongest completed run (`Zi Wei Calendar Full Parity Research` run
`36106002302`, head `ac9fdcad6898dec43dd652314e73592155698fc0`):

- candidate window: `1900-01-01..2100-12-31`;
- Gregorian days checked: **73,414**;
- total provider-vs-data comparisons: **204,716**;
- every day checked at ordinary time and 23:00;
- every Gregorian month-end additionally swept across all 24 civil hours;
- mismatches: **0**;
- generated month shards: **2,413**;
- shard bytes: min **3,259**, max **3,638**, mean **3532.9647741400745**;
- elapsed: **371.844698125 s** on the GitHub runner.

A later lower-cost verifier run (`36106241848`, head
`5da64d999c5fb2cb56689a7f7fda12b520419c7d`) also PASSed with zero
mismatches while checking every Gregorian date once, 2,756 focused 23:00
boundary cases, 8,376 full-hour cases, 148 leap-month day-15/16 dates and 201
lunar-year crossovers. It measured total generated shard bytes at
**8,525,044** for the same candidate window and completed in
**240.572740768 s**.

The initial research workflow run `36105951335` failed before parity execution
because the verifier had not inserted the repository root into `sys.path`.
That bootstrap failure was fixed before the two successful runs and is not
parity evidence.

These results establish high-confidence parity for the candidate window and
show bounded one-query payloads. They do **not** select the production-supported
date range and do not admit B into production.

## Storage encoding comparison

A second bounded POC evaluated a more compact encoding:

```text
Gregorian-year shard
→ 13-14 lunar-month intervals per year
→ each interval stores lunar year, signed lunar month, Gregorian start/end, day count
→ runtime derives lunar day from Gregorian date offset
```

This preserves the same project-owned policies (23:00 next-day shift,
split-after-day-15 and hour-branch mapping) while avoiding one stored record per
Gregorian date.

Machine-readable result:
`references/ziwei/ziwei_calendar_interval_parity_1900_2100.json`.

Completed research run `36108735951` at head
`4c15473da646eff0fa931bbeebfc365060c58b9c`:

- candidate window: `1900-01-01..2100-12-31`;
- every Gregorian date checked at ordinary time: **73,414**;
- New-Year 24-hour cases: **4,824**;
- 23:00 Gregorian-year-edge cases: **202**;
- mismatches: **0**;
- generated Gregorian-year shards: **202**;
- total lunar-month interval records: **2,692**;
- interval records per shard: min **13**, max **14**, mean **13.326732673267326**;
- total dataset bytes: **471,865**;
- shard bytes: min **2,284**, max **2,444**, mean **2335.9653465346537**;
- one-query file bound remains **1 ordinary / 2 at 23:00 cross-year edge**;
- elapsed: **215.04164281 s**.

Compared with the daily-record monthly-shard POC for the same candidate window
(**8,525,044 bytes**), interval encoding reduces generated dataset bytes by
approximately **94.46%** (about **18.07x smaller**) while preserving zero-mismatch
parity in the tested window and the same bounded file-count lookup contract.

**Architecture decision for the B candidate:** prefer Gregorian-year shards of
lunar-month intervals over daily Gregorian records. The candidate product range
is now selected as **1900-01-01..2100-12-31**, and the exact interval dataset is
materialized and deterministically verified. None of those steps by themselves
admit B into production.

The remaining data-admission work is now:

1. migrate the production calendar resolver to the selected repo-local interval
   dataset with fail-closed supported-range handling;
2. remove ordinary production dependence on `lunar_python` while retaining it
   as the pinned build/parity dependency;
3. update deterministic materialization/runtime transport so ordinary Zi Wei
   production no longer carries the full calendar implementation;
4. update `ZIWEI_CALENDAR_ADMISSION_V1.json`, production tests and regression
   evidence together in one bounded admission gate.

## Deterministic interval dataset build / verification mechanism

The interval candidate now has a range-parameterized research materialization
toolchain:

```text
tools/build_ziwei_calendar_interval_dataset.py
→ requested Gregorian year range
→ year shards + end-year+1 policy-tail shard
→ per-shard SHA-256
→ canonical aggregate hash
→ deterministic MANIFEST.json

tools/validate_ziwei_calendar_interval_dataset.py
→ manifest / dependency provenance / shard contract validation
→ exact shard inventory
→ per-shard hash + byte-count + interval-count validation
→ aggregate-hash validation
→ optional clean-room deterministic rebuild and byte-identical manifest check
```

The builder records the pinned build dependency
`lunar_python==1.4.8` / `6tail/lunar-python@000c8a3d74eed098d6256a28fdd51b869324c559`
and keeps `production_admitted=false`. Before generation it verifies the
installed dependency bytes against the existing pinned 34-file upstream
Git-blob inventory owned by `tools/build_ziwei_tool_bundle.py`; a package
version string alone is not accepted as source identity.

For the selected 1900..2100 candidate, the builder additionally writes
`MANIFEST.json`, `provenance.json` and `ATTRIBUTION.md` beside the 202 year
shards. Targeted regression coverage proves:

- explicit selected-vs-unselected range classification;
- pinned dependency source-byte identity;
- deterministic rebuild of the same range;
- fail-closed missing or extra shard;
- fail-closed modified shard/metadata hash;
- fail-closed dependency-provenance tampering;
- invalid range rejection;
- explicit policy-tail materialization for `end_year + 1`.

GitHub Actions run `36119128011` built the selected candidate, ran 9 targeted
tests and validated a byte-identical clean rebuild. The selected dataset was
then promoted through an isolated temporary workflow bridge; run
`36123559237` passed generation, clean rebuild, fixed hash/inventory assertions
and bounded-diff checks before creating the final dataset commit. The temporary
workflow is not present in the final tree.

This closes product-range selection, exact dataset materialization, source
identity, hash accounting and deterministic rebuild evidence. It does **not**
close the later production resolver/materialization migration or calendar
admission update.

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
