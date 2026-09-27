# Zi Wei Body-Palace Overlay Research v1

Authority: **REFERENCE-ONLY / RESEARCH EVIDENCE / NOT PRODUCTION AUTHORITY**

This bounded record supports `ZW-P2-050`. It separates the already-admitted
Body-Palace calculation identity from user-facing interpretation semantics.

## Deterministic prerequisite

Current natal calculation already computes a Body-Palace branch under:

```text
policy = overlay_not_thirteenth_palace
```

The missing machine fact is not a new palace calculation. It is only the
deterministic projection of that branch onto the existing twelve-palace layout:

```text
body_palace.branch
+ existing branch → palace layout
→ body_palace.overlay_palace
→ fact_available:body_palace_overlay
→ body_palace_overlay:<existing palace>
```

No thirteenth palace is created.

## Bounded source pass

Reviewed source:

```text
Renhuai123/nihai-tianji-corpus
revision c90006168195c0650328b7199669eb6a2d0cac93
docs/02-十二宫.md
```

The project source registry classifies this as practitioner reference evidence.
The repository declares `docs/` and `data/` CC BY-NC-SA 4.0; original course
rights remain separately retained. This project stores only normalized
paraphrases and locators.

### Methodology — 身宮 as postnatal-development overlay

p09 §5 @00:12:22–00:12:56 explicitly defines 身宮 in terms of 後天 and contrasts
it with natal / earlier baseline context. This supports a bounded methodology
claim that Body Palace is an overlay emphasis for later/postnatal development,
not a new ordinary palace.

### 夫妻宮 overlay

p09 §5 @00:13:10 states that when 身宮 is in 夫妻宮, later development is
strongly influenced by marriage. The admitted normalization retains only the
relationship-context emphasis; it does not guarantee marriage quality or
outcome.

### 財帛宮 overlay

p19 §7 @00:24:23 and p21 §8 @00:30:26 repeatedly associate 身宮 in 財帛宮 with
work / earning / private-enterprise or self-directed business development. The
admitted claim removes deterministic job prescriptions and financial outcome
guarantees.

### 官祿宮 overlay

p09 §5 @00:12:47 and p21 §8 @00:30:38 associate 身宮 in 官祿宮 with formal
career / public-office development. The admitted normalization keeps the
career/institutional emphasis and rejects guaranteed public-office outcomes.

### 遷移宮 overlay

p15 §6 @00:20:09 and p21 §8 @00:30:46–00:31:00 associate 身宮 in 遷移宮 with
outward / away-from-home development. The admitted normalization keeps
external-environment / mobility / expansion emphasis and rejects guaranteed
migration or overseas outcomes.

## Research decision

Admit one methodology claim plus four source-explicit overlay claims:

```text
身宮 methodology
├─ 夫妻宮
├─ 財帛宮
├─ 官祿宮
└─ 遷移宮
```

Other Body-Palace contexts remain without a new semantic claim in this pass.
Missing doctrine is not filled from model memory.

Machine registry:
`references/ziwei/ziwei_interpretation_claim_registry_body_palace_overlay_v1.json`

## Composition rule

A matched Body-Palace overlay claim adds a postnatal-development emphasis to
the existing palace/star evidence. It does not replace the underlying palace
domain, same-palace stars, pair claims, Sanfang-Sizheng context, transformation
facts or brightness modifiers.

`body_palace_overlay` therefore has higher specificity than generic
star-core/palace-domain claims, while remaining independently source-bounded.

## Non-claims

- no thirteenth palace;
- no new Life/Body Palace geometry;
- no exhaustive overlay semantic dictionary;
- no deterministic marriage, employment, relocation or wealth outcome;
- no scientific predictive-validity claim.
