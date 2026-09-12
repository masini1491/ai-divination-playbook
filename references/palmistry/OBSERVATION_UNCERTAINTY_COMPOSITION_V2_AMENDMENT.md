# Palm Observation Uncertainty Composition — V2 Amendment

Status: **REFERENCE-ONLY / PRE-EXECUTION AMENDMENT / NO PRODUCTION PROMOTION**

## Purpose

本文件是 `OBSERVATION_UNCERTAINTY_COMPOSITION_VALIDATION_V1_DISCREPANCY.md` 之後的正式 V2 amendment record。

V2 不覆寫 V1 frozen artifact，也不把 V1 靜默視為通過；它只修正 predeclared Cases A / J 缺失的 tradition dependency semantics。

## Baseline / source identity

V2 amendment branch baseline：

```text
b8f496914be028f9fb6c98b53261e5316cd95dca
```

V1 lower-layer validator retained：

```text
references/palmistry/observation_uncertainty_composition_validator.py
Git blob SHA = fe98e29bbcf3cb3d836b4409dfb29376ab9c7a51
```

V2 amendment validator：

```text
references/palmistry/observation_uncertainty_composition_validator_v2.py
Git blob SHA = b947d6211d6622bee74da619a8fdd7afe5961dfe
```

V2 imports V1 for the already-reviewed lower-layer capability rules and overrides only the missing tradition-dependency semantics plus the affected fixtures。

## Amendment 1 — Case A

V1 encoded：

```text
tradition state = unresolved
tradition requested = false
```

V2 changes the fixture to：

```text
tradition requested = true
tradition state = unresolved
required_capability = principal_line_geometry
```

Expected V2 behavior：

```text
raw / canonical / principal-line observation remains admitted
tradition_projection = unresolved
raw facts unchanged
```

This now matches the predeclared Case A intent。

## Amendment 2 — Case J

V1 validated only：

```text
color insufficient
→ color_observation insufficient
```

but did not request a color-dependent tradition projection。

V2 adds：

```text
tradition requested = true
tradition state = source_supported
required_capability = color_observation
```

Expected V2 behavior：

```text
raw geometry remains admitted
principal-line geometry remains admitted
color_observation = insufficient
tradition_projection = insufficient
```

This explicitly tests that a source-supported tradition rule still cannot execute when its required lower-layer capability is blocked。

## Dependency semantics

V2 makes the tradition layer capability-aware：

```text
tradition.state = source_supported
+ required_capability admitted
→ tradition_projection admitted

required_capability partial
→ tradition_projection partial

required_capability insufficient
→ tradition_projection insufficient

required_capability unresolved
→ tradition_projection unresolved
```

Independent higher-layer mapping states retain precedence：

```text
prohibited_assumption → insufficient
unresolved            → unresolved
conflicting           → unresolved
```

Target association unresolved also remains a blocker before tradition projection。

## What V2 does not change

V2 does not change the already-reviewed V1 lower-layer rules for：

- scene / target association；
- geometry quality；
- canonical frame provenance；
- principal-line presence vs geometry；
- line-detail hard blockers；
- local score non-rescue；
- candidate index non-identity；
- detector handedness non-authority；
- research metric non-promotion；
- reason lineage。

## Development qualification

The amended source was exercised as a development smoke test before formal result freezing；all 12 case fixtures executed without process failure。

That smoke test is not the formal V2 result artifact and is not used as the closure result。

The next allowed action is a fresh formal V2 execution followed immediately by SHA256 freeze before substantive interpretation。

## Boundary

This amendment is still research infrastructure only。

It does not establish：

- production admission policy；
- production routing；
- production thresholds；
- anatomical truth；
- biometric identity；
- Palmistry prediction validity；
- cross-tradition terminology equivalence。

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**。
