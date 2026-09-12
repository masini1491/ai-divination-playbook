# Palm Observation Uncertainty Composition — Validation Result Freeze

Status: **REFERENCE-ONLY / FORMAL CONTRACT-VALIDATION ARTIFACT FROZEN BEFORE SUBSTANTIVE INSPECTION**

## Purpose

本文件只固定 `OBSERVATION_UNCERTAINTY_COMPOSITION_VALIDATION_PLAN.md` 的 deterministic validator 正式 execution artifact identity。

此 freeze 不先解讀 case-level outcome；後續 interpretation 必須以本文件固定的 validator / result identity 為準。

## Repository / validator identity

Formal execution was opened only after the validator and static review had been fast-forwarded into `main` at：

```text
74586d9ae7811efd506a629fc54b638241cc9e4c
```

Validator：

```text
references/palmistry/observation_uncertainty_composition_validator.py
```

Git blob SHA：

```text
fe98e29bbcf3cb3d836b4409dfb29376ab9c7a51
```

The validator is stdlib-only and does not call CV models, external services, ephemerides, or user palm images。

## Formal execution artifact

The deterministic validator was executed in an isolated Python runtime with an output-file path rather than stdout inspection。

Observed execution accounting before substantive result inspection：

```text
process exit code = 0
output artifact created = yes
output bytes = 43,619
```

Formal result SHA256：

```text
81a9d35406b06c5854bb425084809f2b331e40ff1a0e85e8e133621811a66408
```

This hash was computed immediately after execution。

## Inspection boundary

Before this freeze record：

- the formal result artifact was not used for case-level interpretation；
- no case was removed or edited based on formal output；
- no expected outcome was changed；
- no production threshold / routing decision was made；
- no scalar confidence was introduced。

The validator source had undergone development smoke testing before formal execution; that is implementation qualification, not the formal frozen result artifact itself。

## Predeclared execution contract

The committed validator preserves the validation-plan case family：

```text
A B C D E F G H I J K L
```

and the capability vocabulary：

```text
scene_fact
raw_hand_geometry
canonical_hand_geometry
principal_line_presence
principal_line_geometry
fine_line_detail
surface_mark_detail
color_observation
tradition_projection
```

Formal interpretation may now inspect whether：

- all predeclared cases pass；
- hard blockers remain fail-closed；
- local/model scores fail to rescue hard blockers；
- tradition projection remains isolated from raw observation；
- candidate index / detector handedness remain non-authoritative；
- mixed capability states demonstrate whether one top-level admission state is expressive enough。

## Reproducibility note

The formal JSON artifact itself is not committed as a canonical production artifact. The committed deterministic validator is intended to regenerate the artifact exactly under ordinary compatible Python stdlib execution；the frozen SHA above is the comparison identity for such regeneration。

If future regeneration does not reproduce this SHA, treat that as implementation/runtime drift and do not silently substitute the new result。

## Boundary

This freeze establishes only artifact identity and execution completion。

It does not establish：

- production admission policy；
- production threshold；
- anatomical truth；
- biometric identity；
- Palmistry prediction validity；
- Chinese/Western terminology equivalence；
- runtime/model portability。

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**。
