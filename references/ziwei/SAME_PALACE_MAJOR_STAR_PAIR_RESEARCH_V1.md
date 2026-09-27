# Zi Wei Same-Palace Major-Star Pair Research v1

Authority: **REFERENCE-ONLY / RESEARCH EVIDENCE / NOT PRODUCTION AUTHORITY**

This record is the bounded evidence review for `ZW-P2-060`. It does not
create a 14×14 pair dictionary and does not infer pair doctrine by combining
two independent star-core meanings.

## Research question

Can the current production occupancy facts support a small family of
source-explicit same-palace major-star claims without adding a second chart
geometry path?

## Deterministic prerequisite

Current `tools/ziwei_natal_provider.py` already emits:

```text
fact_available:palace_occupancy
star_in_palace:<star>:<palace>
major_star_count:<palace>:<count>
```

Therefore same-palace applicability is already machine-verifiable. A pair claim
requires both star-in-palace facts naming the same palace. No new placement
algorithm or inferred geometry is needed.

## Bounded source pass

Reviewed practitioner source:

```text
Renhuai123/nihai-tianji-corpus
revision c90006168195c0650328b7199669eb6a2d0cac93
docs/02-十二宫.md
```

The project source registry classifies this corpus as practitioner reference
evidence. Its `docs/` and `data/` are declared CC BY-NC-SA 4.0 by the
reviewed repository; original course rights remain separately retained. This
project stores only normalized paraphrases plus locators.

### Eligible: 武曲 × 天相 / 兄弟宮

Locator: p15 §12 @00:44:42–00:45:22.

The source explicitly identifies the siblings palace as 武曲 + 天相 and treats
that configuration as a positive / supportive sibling signal. The admissible
normalization is limited to that palace context. Later case details involving
化權、化祿 or business roles are not generalized into the pair claim.

### Eligible: 武曲 × 天相 / 官祿宮

Locator: p25 §9 @00:38:08.

The source explicitly discusses 武曲 and 天相 in 官祿宮 and contrasts public
service with private-enterprise development. This is retained only as a
practitioner-bounded career-direction heuristic. It is not a deterministic
career outcome or suitability judgment.

## Reviewed but not eligible in this pass

### 廉貞 × 天府

The pinned corpus explicitly names a 夫妻宮 containing 廉貞天府, but the
bounded passage does not isolate a pair-specific semantic rule. Co-occurrence
alone is not enough.

### 天同 × 巨門

The pinned corpus identifies 天同巨門 inside a multi-star 夫妻宮 case that also
contains 天鉞、曲昌 and other context. The bounded pass did not isolate a
pair-specific semantic rule, so no pair claim is created.

### 太陽 × 天梁

The current bounded practitioner pass did not locate an explicit pair-specific
semantic rule. Reference implementations can demonstrate co-occupancy, but
implementation placement evidence is not interpretation authority.

## Research decision

Admit only a sparse claim family candidate:

```text
武曲 × 天相
├─ 兄弟宮: bounded supportive-sibling tendency
└─ 官祿宮: bounded private-enterprise career-direction heuristic
```

Everything else remains absent rather than filled from model memory.

Machine registry:
`ziwei_interpretation_claim_registry_same_palace_pairs_v1.json`

## Composition rule

A matched pair-specific claim has higher retrieval specificity than generic
star-core / palace-domain composition, but does not delete those base claims.
The synthesis layer should present the pair-specific source-explicit statement
first and use generic claims only as bounded context.

No pair claim match means the existing first-layer composition remains
unchanged.

## Non-claims

- no exhaustive 14×14 matrix;
- no reverse-engineered pair meaning from two star-core meanings;
- no promotion of mere co-occupancy examples;
- no universal named-school identity;
- no scientific or predictive-validity claim;
- no deterministic employment, wealth, family, health or relationship outcome.
