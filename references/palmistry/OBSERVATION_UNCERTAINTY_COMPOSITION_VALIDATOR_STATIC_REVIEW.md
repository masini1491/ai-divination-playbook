# Palm Observation Uncertainty Composition — Validator Static Review

Status: **REFERENCE-ONLY / PRE-EXECUTION STATIC REVIEW / NO PRODUCTION PROMOTION**

## Scope

本文件只做 `observation_uncertainty_composition_validator.py` 對 `OBSERVATION_UNCERTAINTY_COMPOSITION_VALIDATION_PLAN.md` 的 source-level contract review。

不宣稱正式 validation artifact 已 freeze，也不建立 production admission policy。

## Repository identity

Validator branch baseline：

```text
b080a42d54b5f8e82475974b69c8999de2127c43
```

Validator Git blob SHA：

```text
fe98e29bbcf3cb3d836b4409dfb29376ab9c7a51
```

## Static review result

Source-level alignment：**PASS**。

### 1. Frozen capability vocabulary

Runner explicit covers：

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

符合 validation plan 第一輪 capability set。

### 2. Predeclared case family

Runner preserves 12 named cases A–L covering：

- clean single-palm bounded observation；
- insufficient / partial line detail；
- ambiguous multi-hand target；
- raw-frame / mirror lineage unresolved；
- model non-detection；
- high local score under hard quality blocker；
- detector disagreement evidence without calibrated cutoff；
- prohibited / conflicting tradition mapping；
- unreliable color；
- handedness metadata without anatomical authority。

### 3. No scalar confidence composition

Runner does not calculate：

```text
weighted global confidence
mean of heterogeneous uncertainty metrics
production cutoff
```

Capability states remain categorical and separate。

### 4. Hard fail-closed ordering

Source rules make target association、geometry quality、frame provenance與 line-detail quality explicit dependencies。

In particular：

```text
line_detail = insufficient
```

cannot become admitted principal-line geometry merely because：

```text
model present = true
local score = high
```

### 5. Model presence semantics

Model presence is retained only as feature-extraction evidence。

Model non-detection under otherwise sufficient image quality is represented as partial/unresolved observation rather than anatomical absence。

### 6. Tradition isolation

Tradition projection is evaluated after raw observation states and has no source path that mutates raw geometry, frame provenance, or feature output。

`prohibited_assumption` and `conflicting` remain higher-layer blockers only。

### 7. Handedness / candidate identity safeguards

Runner separately checks that：

- detector handedness metadata is not anatomical-side authority；
- scene-local candidate index is not physical identity。

### 8. Detector-disagreement evidence semantics

A detector-disagreement evidence reference can be preserved while compatibility assessment remains unresolved if no calibrated cutoff exists。

The runner does not promote research mean / p95 / minimum into pass/fail boundaries。

### 9. Reason lineage

Any derived `partial / insufficient / unresolved` state must carry non-empty reason lineage；missing lineage becomes a validation failure。

### 10. Top-level admission expressiveness test

Runner records whether a case contains mixed capability states rather than collapsing them prematurely。

The formal execution may therefore determine whether one authoritative top-level admission state is expressive enough or should remain summary-only。

## Runtime-dependent items still open

Static review does not prove：

1. Python execution succeeds；
2. all 12 cases pass；
3. result JSON is deterministic under the committed validator；
4. result artifact SHA256 has been frozen before interpretation。

These remain the next allowed steps。

## Boundary

This review establishes only source-level alignment with the predeclared validation contract。

It does not establish：

- production schema；
- production threshold；
- anatomical truth；
- biometric identity；
- Palmistry prediction validity；
- Chinese/Western terminology equivalence。

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**。
