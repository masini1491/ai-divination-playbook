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


## Source-explicit transformed-star evidence batch v0

A first bounded research registry now exists at:

```text
references/ziwei/ziwei_interpretation_claim_registry_sihua_v0.json
```

It contains **3** `star_conditional` claims and remains
`production_routable=false` / `production_authority_granted=false`.

The batch intentionally admits only cases where the primary witness supplies a
specific transformed-star condition that can be represented as machine facts:

1. `貪狼 × 化祿` in the four-grave branches — retained as a conditionality
   claim, not a wealth/success guarantee;
2. `太陽 × 化忌` in 寅／卯／辰／巳／午 — retained as a source-recorded
   exception to a universal adverse reading;
3. `太陰 × 化忌` in 酉／戌／亥／子 — retained under the same exception
   boundary.

Source locators are the identified Nanyang-Hall digital-text witness pages.
Every claim requires both:

```text
fact_available:sihua
fact_available:star_locations
```

and additionally matches:

```text
sihua_profile:sihua.default_v1
+ exact sihua:<stem>:<transform>:<star> fact
+ exact star_branch:<star>:<branch> predicate
```

This is deliberate: a transformed-star label without profile and location facts
must remain `not_computed` / `unsatisfied`.

Rejected during this pass:

- generic `化祿／化權／化科／化忌` outcome dictionaries;
- practitioner case examples as general doctrine;
- REFERENCE_ONLY practitioner material as sole claim authority;
- source passages whose transformation identity cannot be unambiguously bound
  to the natal `sihua.default_v1` fact identity.

The production-admission work described above was subsequently completed for
this exact bounded batch: star-location retrieval facts are exposed, the
`sihua.default_v1` provider/profile is bound through optional module `sihua_v1`,
all 3 source-explicit claims are separately admitted, and conditional activation
is regression-covered. This research registry itself remains historical
`production_routable=false`; production authority comes from the admission
manifest + runtime binding, not from this research file.
