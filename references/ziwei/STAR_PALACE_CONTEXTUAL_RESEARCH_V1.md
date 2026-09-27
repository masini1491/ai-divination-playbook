# Zi Wei Sparse Star × Palace Contextual Research v1

Authority: **REFERENCE-ONLY / RESEARCH EVIDENCE / NOT PRODUCTION AUTHORITY**

This bounded record supports `ZW-P2-020`. It applies the existing
`STAR_PALACE_COMBINATION_RESEARCH_V0.md` rule: only source-explicit
star-in-palace semantics that add material information beyond independent
star-core + palace-domain composition are eligible.

## Source pass

Reviewed practitioner source:

```text
Renhuai123/nihai-tianji-corpus
revision c90006168195c0650328b7199669eb6a2d0cac93
docs/01-主星.md
```

Only normalized paraphrases and exact locators are retained.

## Admitted candidates

### 天相 × 命宮

Source:
- p11 §2 @00:05:40
- p11 §2 @00:06:09

The practitioner corpus explicitly narrows `命宮坐天相` toward an assistant /
coordinator orientation and away from actively seeking authority. This is
materially more specific than:
- generic 天相 core = 印、官祿、輔佐、秩序、協調;
- generic 命宮 domain = self / core expression.

The current historical registry separately preserves evidence that 天相 can
show authority under favorable supporting-star conditions. Therefore this
contextual claim remains practitioner-bounded and conflict-preserving; it must
not become a universal "位高無權" rule.

### 天梁 × 官祿宮

Source:
- p05 §12 @00:54:50

The practitioner corpus explicitly links 天梁 in 官祿宮 with a career/public-role
context carrying substantial social, entertaining, or coordination load. This
adds a concrete occupational-context modifier that is not present in:
- generic 天梁 core = 蔭庇、保護、長上、規範;
- generic 官祿宮 domain = office, career, achievement, position, public responsibility.

The normalized claim does not guarantee public office and does not preserve
the source's stronger occupation wording as deterministic fate.

## Rejected / deferred candidates from this pass

The following reviewed combinations were **not** promoted:

- `太陽×財帛宮` / `太陽×官祿宮`: source-explicit, but materially duplicates
  already-admitted 太陽 core + 財帛/官祿 domain composition.
- `武曲×財帛宮`: no isolated materially distinct source-explicit rule was
  established in the bounded pass.
- `巨門×夫妻宮`: reviewed passages depended on additional 火鈴 / litigation
  context and did not establish a clean standalone star×palace override.
- `天相×官祿宮`: no isolated source-explicit semantic rule was established.
- case-specific or high-impact deterministic claims involving death, illness,
  guaranteed wealth, guaranteed marriage failure, or fixed occupational
  outcomes remain outside this admission.

## Deterministic applicability

No new chart geometry is introduced. Applicability reuses the already admitted
natal occupancy facts:

```text
fact_available:palace_occupancy
star_in_palace:<star>:<palace>
```

A contextual claim may activate only when the exact canonical
`star_in_palace` fact is present.

## Composition rule

Specificity for an exact admitted star×palace contextual claim is higher than
generic star conditional/core and palace domain evidence, but the base evidence
is retained as context. If no dedicated contextual override matches, runtime
falls back to the existing bounded L5 composition and does not fill missing
doctrine from model memory.

## Research decision

Admit exactly two contextual claims in this pass:

```text
天相 × 命宮
天梁 × 官祿宮
```

No Cartesian 14×12 expansion is created.
