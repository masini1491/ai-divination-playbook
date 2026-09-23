# Zi Wei Interpretation Admission Review v0

Authority：`REFERENCE-ONLY / RESEARCH ADMISSION RECORD / NOT PRODUCTION-ROUTABLE`

## Decision summary

```text
Interpretation source architecture        RESEARCH-ADOPTED
Contextual composition                    ADMIT — RESEARCH
Default source policy                     ADMIT — RESEARCH CANDIDATE
Runtime-facing contracts v0               ADMIT — RESEARCH
Fixture validation v0                     ADMIT — RESEARCH

Full claim registry                       PARTIAL — STAR + PALACE FIRST LAYERS COMPLETE
Batch 1: 6 stars / 12 claims              ADMITTED — RESEARCH
Batch 2: 8 stars / 16 claims              ADMITTED — RESEARCH
14-major-star first-layer coverage        CLOSED — RESEARCH
12-palace first-layer coverage            CLOSED — RESEARCH
Production runtime                        NOT ADMITTED
Production routing                        NOT ADMITTED
Scientific validity                       NOT CLAIMED
```

## Reuse decision

Astrology research already demonstrates a compatible pattern: typed claim registry → source/tradition admission → deterministic retrieval → conflict/provenance preservation → L5 synthesis envelope → maturity/admission review.

Zi Wei adopts that pattern as `ADAPTED`; it does not copy Astrology domain semantics or implementation. Zi Wei retains its own stars, palaces, Four Transformations, Sanfang-Sizheng, Body-Palace overlay and profile components.

## Default source policy

```text
ziwei.interpretation.tw_v1
historical semantic baseline = Nanyang / Quanshu
Zhongzhou = REFERENCE-ONLY
Nihai Tianji = REFERENCE-ONLY
modern claim admission = explicit only
conflict = preserve / no implicit average
case inference = non-generalizable by default
production = false
```

This is a source-policy preset, not a claim that one school is objectively correct.

## Reference-only sources

`Renhuai123/nihai-tianji-corpus@c90006168195c0650328b7199669eb6a2d0cac93` is useful structured practitioner evidence and conflict detection. Corpus data/docs are CC BY-NC-SA 4.0, tools are MIT, and original course rights are separately retained. Disposition: `REFERENCE-ONLY`.

`DestinyLinker/MingLi-Bench@b7433280fd86d7a7c27debbc47d0303c218f0bfd` is `EVALUATION-ONLY`; benchmark answers do not become doctrine authority.

## What is not admitted

The bounded fourteen-star and twelve-palace prototypes were sufficient to test schema/composition behavior. They are not a canonical machine-readable claim registry. Do not infer `prototype discussed → claim admitted`, `source found → project default`, or `benchmark answer → doctrine truth`.

## Material conflict identities

- `CG-TIANJI-RELIEF-001`
- `CG-TIANFU-RELIEF-001`
- `CG-TIANXIANG-AUTHORITY-001`
- `CG-FUDE-SCOPE-001`

These preserve disagreement and block implicit synthesis. They do not resolve truth between traditions.

## Runtime-facing research contracts

Conceptually admitted: Zi Wei Fact Packet v0, Claim Retrieval v0, Interpretation Frame/Synthesis Output v0, explicit fact state, provenance trace, specificity within one authority chain, conflict gate, no model-memory fallback, and pre-render safety gate.

## Production gate

A production phase must be a separate explicit decision. It still needs a frozen calculation runtime, machine-readable schemas, source-normalized claim registry, executable retrieval/composition, dependency validation, behavioral regression, user-facing uncertainty/safety contract and explicit production admission before any METHOD_ROUTING integration.

## Research maturity conclusion

Interpretation Research v0 is architecture-complete enough to stop broad exploratory expansion. Reopen only when a material source-policy premise changes, fixtures expose a new architecture failure class, project objectives change, or production admission reveals a missing contract requirement.

## Batch 1 follow-up

The first source-normalized machine-readable claim batch is admitted separately in `INTERPRETATION_CLAIM_BATCH1_ADMISSION.md`. This narrows the earlier `Full claim registry = DEFER` state to `PARTIAL`; it does not admit the remaining stars, twelve-palace corpus, retrieval runtime or production interpretation.


## Batch 2 follow-up

`INTERPRETATION_CLAIM_BATCH2_ADMISSION.md` admits the remaining eight major stars as 16 source-normalized machine-readable claims. Across Batch 1 + Batch 2, all fourteen major stars now have a first-layer `historical core + representative conditional` pair. This closes major-star first-layer coverage only; the twelve-palace registry, complete combination families, executable retrieval/composition and production interpretation remain deferred.


## Twelve-palace follow-up

`INTERPRETATION_CLAIM_PALACES_V0_ADMISSION.md` admits 24 source-normalized palace claims under schema `0.2.0-research`. The validator remains backward-compatible with the existing v0.1 major-star registries. `CG-FUDE-SCOPE-001` and `CG-NUPU-SCOPE-001` preserve historical-vs-modern scope differences. Major-star + palace first-layer coverage is now 52 claims total; combination families and production remain deferred.
