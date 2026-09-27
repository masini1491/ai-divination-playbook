# Zi Wei Sparse Star × Palace Contextual Research v2

Authority: **REFERENCE-ONLY / RESEARCH EVIDENCE / NOT PRODUCTION AUTHORITY**

This bounded follow-up extends the evidence review behind `ZW-P2-020` without
reopening its current production admission. The production contract remains
exactly two sparse star×palace overrides (`天相×命宮`, `天梁×官祿宮`) until a
separate production-admission change is explicitly authorized, implemented and
validated.

The same rule from `STAR_PALACE_COMBINATION_RESEARCH_V0.md` applies: a
dedicated star×palace L4 candidate must be source-explicit and must add material
information beyond independent star-core + palace-domain composition. Missing
coverage is never permission for model-memory filler or Cartesian expansion.

## Source pass

### Historical semantic baseline candidate

```text
新鋟希夷陳先生紫微斗數全書
Nanyang-Hall witness family tracked by the project source registry
digital witness locator:
https://www.shidianguji.com/zh/book/SDZJ0170/chapter/1jvzoopnqo0t6
```

Relevant bounded sections:

- `諸星問答論 → 問：貪狼所主若何？`
- `諸星問答論 → 問：紫微所主若何？`
- `諸星問答論 → 問：破軍所主若何？`

Only normalized paraphrases are retained here. The historical witness is used as
the existing project historical-semantic baseline candidate, not as scientific
validation or a claim that one transmitted text is the only legitimate school.

### Practitioner comparator

```text
Renhuai123/nihai-tianji-corpus
revision c90006168195c0650328b7199669eb6a2d0cac93
docs/01-主星.md
```

Role remains `PRACTITIONER_REFERENCE / REFERENCE-ONLY`. Case inference and
strong practitioner heuristics do not generalize automatically.

## Candidate review

### 貪狼 × 夫妻宮 — historical bounded admission candidate

The historical witness explicitly assigns a spouse-palace-specific unfavorable
relationship context to `貪狼`. That is materially more specific than:

- generic `貪狼` core = 桃花、欲望、交際、禍福與資源追求等面向;
- generic `夫妻宮` domain = 配偶、婚姻關係與互動狀態.

The same historical star section is highly condition-dependent by dignity,
co-stars and other modifiers, so its categorical source wording must not be
promoted verbatim into deterministic fate.

Normalized candidate:

> 在 historical profile 中，貪狼落夫妻宮可作為婚姻／伴侶互動較需留意穩定性與失衡壓力的 contextual modifier；仍須合看廟旺、吉煞、同會與其他已 admitted 條件，不得翻成必然婚姻失敗、多婚、外遇或固定配偶特徵。

Research classification:

```text
material_distinctness = PASS
source_explicit = PASS
source_role = historical_semantic_baseline_candidate
research_state = ADMISSION-CANDIDATE
production_authority_granted = false
```

A future production pass must still define exact normalized claim identity,
conflict/provenance metadata, applicability and regression coverage.

### Nihai spouse-age heuristic — practitioner-only / deferred

The pinned practitioner corpus states at `p19 §9 @00:29:42` that `貪狼` in
the spouse palace may correlate with an older spouse, while the same passage
explicitly cautions against treating the rule as universally certain.

This bounded pass did not establish independent historical-primary support for
that fixed spouse-age characteristic. Therefore it is not folded into the
historical `貪狼×夫妻宮` candidate.

Research classification:

```text
source_role = PRACTITIONER_REFERENCE
self_caveated = true
independent_historical_support_in_this_pass = not_established
research_state = DEFER / REFERENCE-ONLY
```

If revisited later, it must remain a separate tradition/profile-bounded claim
rather than silently broadening the historical candidate.

### 紫微 × 官祿宮 — reject as non-material restatement

The historical witness directly discusses `紫微` in career / life-palace
contexts and emphasizes the importance of supporting stars. The current project
already preserves:

- `ZW-B1-ZIWEI-CORE-001`: centrality / authority / leadership-oriented core;
- `ZW-B1-ZIWEI-COND-002`: positive authority manifestation depends on
  supporting-star conditions and is weakened by adverse conditions;
- `ZW-PAL-CAREER-DOM-001`: career, office, achievement, position and public
  responsibility domain.

A new `紫微×官祿宮` claim would therefore mainly restate existing L4 evidence
through bounded L5 composition rather than add a materially distinct semantic.

Research classification:

```text
source_explicit = PASS
material_distinctness = FAIL
research_state = REJECT-REDUNDANT
```

No dedicated L4 override is proposed.

### 破軍 × 遷移宮 — borderline / defer

The historical witness explicitly assigns `破軍` in the migration palace an
ineffective / strenuous movement context. The current project already has:

- `破軍` core = 耗、破舊、劇烈變動與重整;
- `遷移宮` domain = 外出、異地、移動與外部環境中的際遇.

The source's low-efficacy nuance may be more specific than generic composition,
but it is close enough to the existing core+domain synthesis that this bounded
pass does not promote it. The categorical historical wording also deserves a
separate modifier/condition review before any production normalization.

The practitioner corpus passage found in this pass groups multiple martial stars
and additional gender/context assumptions together, so it does not establish a
clean isolated `破軍×遷移宮` rule.

Research classification:

```text
source_explicit = PASS
material_distinctness = BORDERLINE
isolated_practitioner_support = not_established
research_state = DEFER-BORDERLINE
```

A future pass should seek independent or condition-specific evidence and prove
that the normalized meaning cannot be safely delivered by existing L5
composition.

## Research decision

This pass changes **research evidence only**:

```text
historical admission candidates = 1
  - 貪狼×夫妻宮

practitioner-only deferred heuristics = 1
  - 貪狼×夫妻宮 → spouse-age characteristic

rejected as non-material = 1
  - 紫微×官祿宮

borderline / deferred = 1
  - 破軍×遷移宮

production claims added = 0
production claim count changed = false
cartesian expansion = false
```

Current production authority therefore remains unchanged:

```text
天相×命宮
天梁×官祿宮
```

## Next admission gate

A later production-admission action for `貪狼×夫妻宮` is allowed only as a
separate bounded change. At minimum it must:

1. normalize the historical wording without deterministic marriage outcomes;
2. keep the Nihai spouse-age heuristic separate and tradition-bounded;
3. define exact `star_in_palace:貪狼:夫妻宮` applicability;
4. preserve generic star-core and palace-domain evidence as context;
5. add retrieval/runtime/production-contract regression coverage;
6. update admission/index/materialization/generated caches only through their
   current authoritative generator / bridge path;
7. complete formal validation, merge and exact-main read-back before any
   production `DONE` claim.

## Privacy

This research record contains no real birth data or private reading context.
