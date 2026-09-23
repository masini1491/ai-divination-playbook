# Zi Wei Interpretation Architecture v0

Authority：`REFERENCE-ONLY / RESEARCH CONTRACT / NOT PRODUCTION-ROUTABLE`

Status：

```text
ARCHITECTURE RESEARCH-ADOPTED
FULL CLAIM CORPUS NOT ADMITTED
STAR + PALACE FIRST-LAYER CLAIMS ADMITTED
```

## Decision

Primary interpretation architecture：`contextual_composition`

Rejected as primary model：`flat_dictionary`

Flat star/palace dictionaries may remain low-level retrieval/index aids, but they cannot directly generate default readings.

## Default research candidate

```text
profile_id = ziwei.interpretation.tw_v1
authority = research-candidate
production_admitted = false

architecture = contextual_composition
historical_semantic_baseline = nanyang_quanshu
modern_named_school.zhongzhou = reference-only
practitioner.nihai = reference-only
modern_claim_adoption = explicit_only
case_inference = non_generalizable_by_default
conflict_policy = preserve_no_implicit_average
presentation = contemporary_language_preserve_rule_semantics
```

Default means project source-policy, not monolithic school identity.

## Source roles

### Nanyang / Quanshu

Role：`historical_semantic_baseline`

Used for historical star/palace semantics, conditions, topology-aware methodology and rule-specific interpretation evidence where actually sourced. It is not declared the only authentic Zi Wei lineage.

### Zhongzhou modern

Role：`named_tradition_reference`

Useful for tradition comparison and modern composition research. Modern copyrighted source material is not vendored into this repository merely because the tradition is relevant.

### Nihai Tianji

Reference：`Renhuai123/nihai-tianji-corpus@c90006168195c0650328b7199669eb6a2d0cac93`

Role：`structured_practitioner_reference + conflict_detector`

Data/docs licensing is CC BY-NC-SA 4.0 and original course rights remain separately reserved. The corpus stays REFERENCE-ONLY; project docs do not vendor its 4,886 entries.

### MingLi-Bench

Reference：`DestinyLinker/MingLi-Bench@b7433280fd86d7a7c27debbc47d0303c218f0bfd`

Role：`evaluation_only`

Competition answers may test reasoning behavior; they are not source authority for doctrine.

## Claim architecture

Future normalized claim record should be able to represent：

```text
claim_id
source_id
source_locator
tradition_profile
assertion_class
claim_type
subject
semantic_predicate
applicability
effect
confidence_scope
conflict_group_id
source_evidence_level
license_boundary
adoption_state
```

Assertion classes should separate `historical_core`, `historical_conditional`, `named_tradition`, `practitioner_heuristic`, `case_inference`, and `project_adoption`. Practitioner or case inference must not be silently absorbed into historical core.

## Composition dimensions

Research prototypes support composition from：

```text
star_core
× palace_domain
× dignity / brightness
× transformation
× same-palace combination
× opposite
× Sanfang-Sizheng
× body-palace overlay
× temporal context
```

The fourteen-star and twelve-palace prototypes validated the architecture. Batch 1 + Batch 2 now admit 28 first-layer major-star claims, and Twelve Palaces v0 admits 24 first-layer palace claims. Star×palace composition policy is research-closed: exhaustive 14×12 dictionary expansion is rejected, while sparse source-explicit overrides remain future on-demand evidence work. Brightness interpretation responsibility is also research-closed as a profile-bound modifier contract; the project-wide brightness table remains unselected. Four-Transformation interpretation responsibility is also research-closed as a profile-preserving modifier/claim gate; source-explicit transformed-star overrides remain on-demand. Other contextual layers remain incomplete.

## Star × palace composition policy

`STAR_PALACE_COMBINATION_RESEARCH_V0.md` admits bounded composition of separately sourced star and palace evidence at L5 while forbidding that synthesis from being relabeled as a new L4 historical claim. Dedicated star×palace L4 overrides require source-explicit or separately admitted project/named-tradition evidence; exhaustive Cartesian coverage is not required.

## Brightness modifier policy

`BRIGHTNESS_INTERPRETATION_RESEARCH_V0.md` treats brightness as a profile-bound chart fact consumed by sourced claim applicability. Generic brightness-only doctrine is not created automatically; unknown/not-computed brightness skips dependent claims, and no project-wide brightness table is selected by this interpretation-stage decision.

## Four-Transformation interpretation policy

`FOUR_TRANSFORMATION_INTERPRETATION_RESEARCH_V0.md` keeps calculation-table identity separate from interpretation doctrine. Transformation facts retain `sihua_profile_id`; generic transformation labels do not create guaranteed outcome claims; dedicated transformed-star L4 claims require explicit source/admission support.

## Specificity

Within the same source/profile authority chain：

```text
exact conditional combination
> star + palace + condition
> star + palace
> star conditional
> star core
> palace domain core
```

Specificity does not cross tradition boundaries automatically.

## Conflict preservation

Current architecture-significant conflict identities include：

```text
CG-TIANJI-RELIEF-001
CG-TIANFU-RELIEF-001
CG-TIANXIANG-AUTHORITY-001
CG-FUDE-SCOPE-001
CG-NUPU-SCOPE-001
```

These preserve research differences and block implicit averaging; they do not decide which tradition is objectively true.

## Modern claim admission gate

A modern claim does not enter the project default merely because it is vivid or popular. Review named source, historical separability, conflict status, case-inference status, modern explanatory value, fixture safety, license/reuse boundary, high-risk wording, and explicit project adoption.

## Rejected shortcuts

Do not treat practitioner heuristics such as `Career Palace = public sector`, `Wealth Palace = private business`, `Tian Xiang = always high position without authority`, `Fortune Palace = universally second Spouse Palace`, or a fixed travel-distance threshold as universal defaults without explicit admission.

## Safety boundary

Historical claims about disease, death, imprisonment, financial ruin or similar high-impact outcomes can remain historical/source evidence, but are not default user-facing certainty. Safety handling occurs before final synthesis.

## Non-goals

This document does not establish scientific predictive validity, a complete claim corpus, production routing, a Zi Wei runtime/provider, or blanket project adoption of Zhongzhou/Nihai doctrine.

## Machine-readable registry status

Canonical machine-readable owners:

- `INTERPRETATION_CLAIM_REGISTRY_SCHEMA_V0.md` — v0.1/v0.2 research schema contract
- `validate_interpretation_claim_registry.py` — dual-version deterministic validator
- `ziwei_interpretation_claim_registry_batch1.json` — first six major stars
- `ziwei_interpretation_claim_registry_batch2.json` — remaining eight major stars
- `ziwei_interpretation_claim_registry_palaces_v0.json` — twelve palaces
- `INTERPRETATION_CLAIM_BATCH1_ADMISSION.md`
- `INTERPRETATION_CLAIM_BATCH2_ADMISSION.md`
- `INTERPRETATION_CLAIM_PALACES_V0_ADMISSION.md`

All are research-only and do not change production routing.
