# Palm Observation Uncertainty Composition — V1 Validation Discrepancy

Status: **REFERENCE-ONLY / POST-FREEZE IMPLEMENTATION DISCREPANCY / FORMAL V1 RESULT NOT SUFFICIENT FOR PLAN CLOSURE**

## Purpose

本文件記錄 `OBSERVATION_UNCERTAINTY_COMPOSITION_VALIDATION_RESULT_FREEZE.md` 建立後，第一次 substantive inspection 所暴露的 validator-to-plan mismatch。

此問題不修改已 frozen 的 V1 result SHA，也不把 V1 result 靜默重跑成「同一個結果」。

## Frozen V1 artifact remains unchanged

V1 formal artifact SHA256：

```text
81a9d35406b06c5854bb425084809f2b331e40ff1a0e85e8e133621811a66408
```

Validator Git blob SHA：

```text
fe98e29bbcf3cb3d836b4409dfb29376ab9c7a51
```

The V1 process exited successfully and produced a deterministic artifact, but successful execution is not sufficient if the executable does not cover the predeclared case semantics exactly。

## Discrepancy 1 — Case A did not exercise unresolved tradition projection

The predeclared plan states Case A as a clean single-palm observation where raw observation remains usable **even though tradition projection is unresolved**。

V1 validator encoded：

```text
tradition.state = unresolved
tradition.requested = false
```

and expected：

```text
tradition_projection = not_applicable
```

Therefore V1 did not actually test the plan's intended condition：

```text
tradition requested
+ mapping unresolved
→ raw observation admitted
+ tradition projection unresolved
```

This is a validator fixture mismatch, not a failure of the intended contract。

## Discrepancy 2 — Case J did not exercise color-dependent tradition blocking

The predeclared plan states Case J as：

```text
geometry sufficient
line detail sufficient
color insufficient / unreliable
```

with expected behavior including：

```text
geometry / principal-line capabilities may remain admitted
color observation = insufficient
source-specific palm-color projection = blocked
```

V1 validator encoded color insufficiency but left：

```text
tradition.requested = false
```

so it validated only color observation isolation, not the required downstream tradition-projection block。

## Root cause

V1 `tradition_projection` input was too coarse：

```text
requested
state
```

It did not preserve which lower-layer capability a tradition projection depends on。

That makes it impossible to distinguish, for example：

```text
principal-line tradition projection
vs
palm-color tradition projection
```

when one lower-layer capability is admitted and another is insufficient。

## V1 interpretation boundary

The following V1 observations remain useful implementation evidence：

- deterministic execution path works；
- reason-lineage checks work；
- hard line-detail blocker cannot be rescued by high local model score；
- candidate index is not used as identity；
- detector handedness metadata is not promoted to anatomical authority；
- mixed capability states are representable；
- higher-layer code path does not mutate raw input facts。

However V1 **must not** close the full predeclared validation node because Cases A and J did not test the intended tradition-dependency semantics。

## Required amendment before V2

The next validator revision must be created in a separate branch and add explicit dependency provenance for tradition projection, for example：

```text
tradition.required_capability
```

or equivalent structured representation。

At minimum V2 must make these cases explicit：

```text
Case A:
tradition requested = true
tradition state = unresolved
required capability = principal_line_geometry
expected tradition projection = unresolved
raw observation unchanged

Case J:
tradition requested = true
tradition state = source_supported
required capability = color_observation
color_observation = insufficient
expected tradition projection = insufficient / blocked
geometry and principal-line facts unchanged
```

V2 must receive a new validator identity、new formal result artifact、new SHA freeze before interpretation。

## Boundary

This record does not establish production semantics or invalidate unrelated Palmistry evidence。

It only marks V1 uncertainty-composition validation as **implementation-incomplete relative to the predeclared plan** and prevents false closure。

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**。
