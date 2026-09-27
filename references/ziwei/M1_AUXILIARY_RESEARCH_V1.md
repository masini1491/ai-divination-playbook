# Zi Wei M1 High-Impact Auxiliary Research v1

Authority: **REFERENCE-ONLY / RESEARCH EVIDENCE / NOT PRODUCTION AUTHORITY**

This bounded record supports `ZW-P2-010`.

## Scope

M1 contains exactly:

```text
天魁 天鉞 祿存 天馬 擎羊 陀羅 火星 鈴星 地空 地劫
```

It is natal-only in this admission pass. Flow/cycle identities remain owned by
the temporal research line and are not inferred from natal placements.

## Calculation / profile closure

Two pinned implementations independently expose equivalent natal placement
rules for the full M1 set:

- `SylarLong/iztro@2c7ef9be669df7b19d1799f4dce335fed3794f78`
  - `src/star/location.ts`
- `airicyu/fortel-ziweidoushu@2620cc895395f9f6994abd4927e739d31015c67d`
  - `src/model/minorStar.ts`

Reconciled rule families:

- 天魁 / 天鉞: birth-year Heavenly Stem table;
- 祿存: birth-year Heavenly Stem table;
- 擎羊 / 陀羅: one branch ahead / behind 祿存;
- 天馬: birth-year Earthly-Branch trine group;
- 火星 / 鈴星: birth-year branch group chooses 子時 base, then advance by birth-hour branch index;
- 地空 / 地劫: 亥起子時, reverse / forward by birth-hour branch index.

The production candidate profile is therefore named
`ziwei.auxiliary.m1.common_v1`; it does not claim a unique historical lineage.

## Interpretation evidence and safety boundary

The pinned practitioner corpus
`Renhuai123/nihai-tianji-corpus@c90006168195c0650328b7199669eb6a2d0cac93`
contains explicit material for:

- 天魁 / 天鉞 as high-impact support / benefactor / qualification modifiers;
- 祿存 / 天馬 as resource + mobility modifiers, including the named 禄马交驰 pattern;
- 羊陀火鈴空劫 as high-impact adverse / disruptive modifiers.

The corpus also contains deterministic health, death, legal, promotion and
wealth claims. Those stronger outcomes are **not admitted** here. M1 only
admits bounded modifier-role policy claims. No M1 star independently grants a
specific event prediction.

## Completeness contract

Existing first-layer major-star conditionals use broader availability tokens:

```text
fact_available:auxiliary_stars
fact_available:star_relations
```

M0 alone intentionally does not emit those tokens. The M1 candidate therefore
requires `m0_auxiliary_v1` at runtime. Only the admitted **M0 + M1** union may
mark the current bounded auxiliary domain complete enough for those generic
availability facts.

This is not blanket minor-star admission:

- M0 + M1 covers 14 explicitly admitted auxiliary/modifier subjects only;
- M2 long-tail stars remain unadmitted;
- M3 cycle/flow stars remain unadmitted;
- missing contextual doctrine is never filled from model memory.

## Research decision

Candidate admission:

- deterministic M1 natal placements for exactly 10 stars;
- exact self/sanfang relation facts to admitted major stars;
- one bounded modifier-role policy claim per M1 star;
- generic auxiliary completeness only when M0 and M1 are both active;
- no independent historical semantic-core claim;
- no high-stakes deterministic outcome claim.
