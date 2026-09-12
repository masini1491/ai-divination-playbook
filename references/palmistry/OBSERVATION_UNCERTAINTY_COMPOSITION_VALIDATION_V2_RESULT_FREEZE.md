# Palm Observation Uncertainty Composition — V2 Validation Result Freeze

Status: **REFERENCE-ONLY / FORMAL V2 ARTIFACT FROZEN BEFORE SUBSTANTIVE INSPECTION**

## Purpose

本文件固定 V2 uncertainty-composition validator 的 formal execution identity。

V2 是在 `OBSERVATION_UNCERTAINTY_COMPOSITION_VALIDATION_V1_DISCREPANCY.md` 已先記錄後，透過獨立 amendment branch 修正 Cases A / J tradition dependency semantics 的新正式 execution。

## Repository / validator identity

Formal V2 execution began only after amendment merge into `main` at：

```text
7e545501d91a2f5bdb2872944dfef1d94e2256b9
```

V1 lower-layer validator：

```text
references/palmistry/observation_uncertainty_composition_validator.py
Git blob SHA = fe98e29bbcf3cb3d836b4409dfb29376ab9c7a51
```

V2 amendment validator：

```text
references/palmistry/observation_uncertainty_composition_validator_v2.py
Git blob SHA = b947d6211d6622bee74da619a8fdd7afe5961dfe
```

## Formal V2 execution artifact

Observed before substantive result inspection：

```text
process exit code = 0
output artifact created = yes
output bytes = 44,673
```

Formal V2 result SHA256：

```text
1d88fdec8f9cbaf34e213af5319900a4cd71a23120812578fcd1443d805bbd7f
```

The hash was computed immediately after execution。

## Inspection boundary

Before this freeze record：

- formal V2 case-level summary was not used for interpretation；
- no expected case outcome was altered after seeing formal V2 output；
- no case was removed；
- no production threshold / routing rule was introduced；
- no global scalar confidence was introduced。

Development smoke testing had already verified that the amended source could execute, but that development run is not this frozen V2 artifact。

## V2 plan-coverage amendment under test

V2 specifically restores the two missing V1 checks：

```text
Case A:
tradition requested
+ mapping unresolved
+ principal-line observation otherwise admissible
→ tradition projection unresolved
→ raw observation unchanged

Case J:
color observation insufficient
+ source-supported color-dependent tradition projection requested
→ tradition projection blocked / insufficient
→ geometry and principal-line observation unchanged
```

All other predeclared lower-layer cases remain inherited from the V1 validator and are rerun in V2。

## Next allowed action

Substantive inspection may now determine：

- total case pass/fail；
- whether Cases A / J now match the predeclared contract；
- hard-dependency fail-closed behavior；
- no-rescue behavior；
- reason lineage；
- tradition isolation；
- candidate-index / handedness safeguards；
- whether mixed capability states make one authoritative top-level admission state insufficient。

## Reproducibility note

The formal JSON artifact itself is not promoted as a production artifact。The frozen SHA above remains the identity for exact regeneration against the committed V1 + V2 validator sources。

Any future non-matching regeneration must be treated as drift rather than silently replacing this result。

## Boundary

This freeze establishes only formal V2 artifact identity。

It does not establish：

- production admission policy；
- production thresholds；
- production routing；
- anatomical truth；
- biometric identity；
- Palmistry prediction validity；
- cross-tradition terminology equivalence。

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**。
