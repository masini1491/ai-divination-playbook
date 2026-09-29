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

## 5. Production boundary

Current production authority remains unchanged:

```text
astronomy-engine==2.1.19
→ project-owned Astrology providers
→ tools/astrology_runtime.py
→ admitted Astrology Fact Bundle
```

The host-native probe MUST NOT be inserted into ordinary production routing merely because it succeeds.

In particular:

```text
swisseph import PASS
→ NOT sufficient

Sun..Pluto + houses PASS
→ NOT sufficient

bounded parity PASS
→ still NOT sufficient

separate provider/license/admission closure
→ required before production use
```

## 6. License boundary

Existing project research records Swiss Ephemeris / PySwissEph as a dual-license / AGPL-sensitive family and explicitly forbids silently adding it as a production dependency.

This research adds a new architectural case:

```text
project distributes no Swiss code/data
+
host already exposes swisseph
+
project dynamically invokes host capability
```

Whether that case is acceptable for this public project's intended use must be resolved deliberately; this report does not provide legal advice or a production license conclusion.

Until resolved:

- do not add PySwissEph to production requirements;
- do not vendor Swiss source or `.se1` files;
- do not copy AGPL implementation into permissive production code;
- keep the host probe REFERENCE-ONLY.

## 7. Remaining technical admission gates

Before any host-native provider can emit canonical Astrology facts:

1. **Provenance schema** — preserve module/version, requested flags, actual `retflag`, effective backend and relevant configuration.
2. **Node parity** — compare like-for-like mean/true node definitions.
3. **Motion parity** — stress speed sign, retrograde boundaries and station timing.
4. **Transit parity** — compare exact transit-event timing under frozen tolerances.
5. **House edge behavior** — test high/polar latitudes and require explicit fail-closed semantics.
6. **Scope freeze** — prospectively define accepted dates, objects, zodiac/center/house systems and tolerance.
7. **Fact Bundle adapter** — only after admission, normalize host results through the existing runtime gate rather than creating a second fact schema.
8. **License/admission closure** — technical PASS and legal/license posture are independent gates.

## 8. Candidate future routing, not yet authorized

Only if AST-P2-030 later receives production admission could a route such as this be considered:

```text
verified canonical Astrology cache
→ admitted host-native provider available?
   → yes: execute admitted adapter + preserve backend provenance
   → no: existing GitHub artifact/materialization route
→ canonical Astrology runtime Fact Gate
```

Current route remains unchanged.

## 9. Decision

```text
Host-native PySwissEph/Moshier execution is FEASIBLE as a capability lane.
Existing bounded parity evidence is encouraging.
Production routing remains NOT ADMITTED.
```

The next useful work is not another proof that `swisseph` can import. It is admission-quality provenance + parity + license closure.


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
