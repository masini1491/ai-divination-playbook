# Host-Native PySwissEph Capability｜ChatGPT host 占星 runtime 可用性研究

Status: **REFERENCE-ONLY / RESEARCH / NOT PRODUCTION-ROUTABLE**

Research baseline: `masini1491/ai-divination-playbook@1bb1eb2fcb94933eae4ea0a98ab076c25a0a5648`

Purpose: determine whether a ChatGPT Python host that already exposes `swisseph` can be treated as a bounded execution capability without making Swiss Ephemeris a mandatory project dependency or bypassing the current Astrology production admission boundary.

## 1. Trigger

Interactive ChatGPT Python sessions have demonstrated that `swisseph` may already exist in the host environment before any repository runtime materialization.

The important product distinction is:

```text
host module/runtime available
!=
repo dependency admitted
!=
Astrology production provider admitted
```

Plan/tier must not be used as a proxy for runtime capability. Probe the current session.

## 2. Observed capability shape

A representative 2026-09-29 host runtime exposed:

```text
Python             3.13.5
PySwissEph         2.10.03
Sun..Pluto         executable
Placidus houses    executable
Ascendant / MC     executable
Mean Node          executable
True Node          executable
```

When `FLG_SWIEPH | FLG_SPEED` was requested for the core planets, returned flags identified `MOSEPH | SPEED` rather than file-backed `SWIEPH`.

This confirms a critical provenance rule:

> requested ephemeris flags are not sufficient evidence of the effective backend; the returned `retflag` must be preserved and decoded.

A host may also contain some `.se1` files without containing the planetary/lunar file set required for file-backed SWIEPH calculation. File presence therefore does not establish the actual backend used for any returned fact.

## 3. Existing parity evidence already in this Repo

[`ENGINE_COMPARISON_RESULTS.md`](ENGINE_COMPARISON_RESULTS.md) already compared PySwissEph 2.10.03 using effective `MOSEPH` against reviewed Astronomy-Engine-family fixtures under tropical/geocentric/Placidus configuration.

Across three fixtures, that bounded research observed:

```text
30 Sun..Pluto sign comparisons        0 disagreements
30 planetary house placements        0 disagreements
maximum planetary longitude diff     14.178 arcsec
maximum Placidus cusp diff             6.954 arcsec
```

This is useful feasibility evidence, but it is not a production tolerance or an accuracy proof.

## 4. Reproducible host capability probe

Use:

```bash
python references/astrology/host_native_swisseph_probe.py
```

Optionally, if the host exposes an explicit Swiss Ephemeris data directory:

```bash
python references/astrology/host_native_swisseph_probe.py --ephe-path <directory>
```

The probe:

- dynamically imports `swisseph`; the repository does not declare it as a dependency;
- requests `SWIEPH | SPEED` but records the effective returned backend for every calculated object;
- checks Sun..Pluto, Mean Node, True Node and Chiron separately;
- checks Placidus houses, Ascendant and MC;
- can report presence of `sepl_18.se1`, `semo_18.se1` and `seas_18.se1` only when an explicit ephemeris directory is supplied;
- always reports `production_authority: false`.

Current research classifications:

```text
UNAVAILABLE
MODULE_ONLY
PARTIAL_EXECUTION
MOSHIER_NATAL_BASELINE
SWIEPH_NATAL_BASELINE
JPL_NATAL_BASELINE
MIXED_NATAL_BASELINE
```

These labels describe host execution capability only.

## 5–9. Historical pre-admission record — SUPERSEDED

Sections 5–9 of the original capability study described the state **before** host-native production admission. Their earlier conclusions such as `Current production authority remains unchanged`, `Current route remains unchanged`, and `Production routing remains NOT ADMITTED` are historical only and MUST NOT be used as current routing authority.

Current machine truth is owned by:

- `ASTROLOGY_PROVIDER_ROUTING_V1.json`;
- `ASTROLOGY_SWISS_PROVIDER_ADMISSION_V1.json`;
- `ASTROLOGY_PRODUCTION_ADMISSION_V1.json#/natal_provider_routing`;
- `tools/astrology_provider_selector.py`.

The retained research evidence still establishes the bounded feasibility background: host-native PySwissEph may execute with mixed effective backends, actual `retflag` must be preserved, and repository installation/vendoring of Swiss remains forbidden. Current production outcome is recorded in §10 below.

## 10. Host-native production admission outcome

The project admits one deliberately narrow production lane:

```text
ChatGPT execution surface
+ exact/approximate known-time natal
+ host-preinstalled swisseph capability probe PASS
→ swiss-host-natal-v1
```

The repository does not install, declare, vendor, redistribute, or download Swiss/PySwissEph or Swiss ephemeris data. This contract makes no assertion about the platform provider's licensing arrangement; it records only the repository boundary.

All other cases route to the portable Astronomy Engine provider:

- non-ChatGPT execution;
- unknown birth time;
- transit;
- missing/broken host `swisseph`;
- any request that would require installing or vendoring Swiss.

The Swiss provider preserves actual `retflag` and effective backend per calculated object, so requested SWIEPH silently falling back to MOSEPH remains visible in provenance.
