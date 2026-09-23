# Zi Wei Four-Transformation Interpretation Research v0

Authority：`REFERENCE-ONLY / RESEARCH DECISION / NOT PRODUCTION-ROUTABLE`

## Decision summary

```text
Four-Transformation fact identity           PROFILE-BOUND
bare transformed-star fact                  INSUFFICIENT WITHOUT sihua_profile
generic 祿/權/科/忌 outcome dictionary       REJECTED
transformed-star L4 claim                   SOURCE/ADMISSION REQUIRED
sihua.default_v1 calculation identity       PRESERVED / NOT RESELECTED
cross-profile interpretation averaging      FORBIDDEN
production authority                        false
```

## Responsibility boundary

The variant registry already owns the question **which star receives 祿／權／科／忌 under a given profile**. Interpretation must not recompute or normalize that result.

Research pipeline:

```text
year/stem + sihua_profile
→ profile-scoped transformed-star fact
→ source-backed transformation-conditioned L4 claim, when admitted
→ contextual L5 synthesis
```

Calculation-table identity and interpretation doctrine remain separate responsibilities.

## Generic-label policy

`化祿`、`化權`、`化科`、`化忌` may be useful retrieval dimensions, but the project does not admit a universal rule such as:

```text
化祿 = guaranteed money
化權 = guaranteed power
化科 = guaranteed fame
化忌 = guaranteed disaster
```

A transformation label alone is not sufficient for a deterministic real-world conclusion.

## Transformed-star claims

A dedicated L4 claim such as `star X + 化忌` or `star Y + 化祿` requires:

1. explicit source identity and locator;
2. transformation/star applicability;
3. tradition/profile scope when relevant;
4. conflict identity when another admitted tradition differs;
5. bounded semantic effect rather than guaranteed event prediction.

Existing major-star claims that mention 四化 only as modifiers remain valid as first-layer claims; mentioning a transformation in a modifier list does not itself admit a complete transformed-star claim family.

## Profile preservation

`FOUR_TRANSFORMATION_VARIANT_REGISTRY.md` already documents materially different witness/tradition tables. Therefore a usable fact must retain at least:

```text
year_stem
transform_kind
star
sihua_profile_id
profile_revision
source/evidence provenance
engine/revision
fact state
```

Retrieval must not merge claims across incompatible `sihua_profile_id` values merely because the transform label is the same.

## Project default boundary

`sihua.default_v1` remains the current research calculation-profile candidate selected on the recorded user-perceived-fit basis. This interpretation stage does not reselect it and does not convert that design decision into historical or scientific authority.

## Fail-closed behavior

```text
transformation fact missing
→ skip transformation-dependent claim

sihua profile missing / ambiguous
→ preserve ambiguity; do not guess table

no sourced transformed-star claim
→ compose only from already admitted non-transformation evidence

cross-tradition disagreement
→ preserve conflict / source scope; do not average
```

## Research closure

```text
Four-Transformation interpretation responsibility = CLOSED — RESEARCH
generic transformation outcome dictionary          = REJECTED
full transformed-star claim corpus                  = NOT REQUIRED FOR ARCHITECTURE CLOSURE
source-explicit transformed-star overrides          = FUTURE ON-DEMAND
sihua.default_v1                                    = UNCHANGED
production authority                                = false
```

This stage closes interpretation responsibility without changing the calculation profile or claiming predictive validity.
