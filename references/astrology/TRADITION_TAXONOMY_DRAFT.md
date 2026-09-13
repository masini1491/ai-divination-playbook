# Astrology Tradition Taxonomy Draft

Status: **REFERENCE-ONLY / RESEARCH TAXONOMY / NOT PRODUCTION-ROUTABLE**

Branch baseline: `masini1491/ai-divination-playbook@94fadc8db489b43697f61b03e95309025b84c900`

## 1. Why this taxonomy is needed

The current claim registries intentionally preserve source-local `tradition_tags[]`, but those tags mix different semantic dimensions.

Observed examples include:

```text
hellenistic
ptolemaic
classical
history_of_astrology
early_modern
modern
psychological_astrology
blended
retrieval_first
```

Those labels are useful discovery metadata, but they are not a safe canonical routing taxonomy because they do not all answer the same question.

For example:

- `ptolemaic` names a doctrinal lineage / identifiable authorial framework;
- `early_modern` names a historical context;
- `psychological_astrology` names a modern interpretive school/family;
- `blended` names a synthesis mode;
- `retrieval_first` names an implementation behavior;
- `history_of_astrology` names a scholarly/meta perspective rather than an astrology doctrine.

A flat tag set can therefore create false matches such as treating `early_modern` as a reading tradition or `retrieval_first` as doctrine.

## 2. Design goal

The research taxonomy should support bounded routing without pretending that astrology traditions form one universally agreed hierarchy.

Required properties:

```text
stable IDs
explicit semantic dimension
parent/child relation only when justified
aliases kept separate from IDs
source-local tags preserved for provenance
no automatic equivalence from shared words
no automatic blending
no production adoption
```

The taxonomy is a routing/evidence structure, not a claim that one school is historically correct or scientifically valid.

## 3. Separate semantic dimensions

### 3.1 `doctrinal_lineage`

Use for identifiable historical or textual frameworks whose claims can be scoped to a lineage.

Initial research IDs:

```text
lineage:hellenistic
lineage:hellenistic:ptolemaic
```

`lineage:hellenistic:ptolemaic` may be treated as a child context of Hellenistic astrology for retrieval, but this does not imply that Ptolemy represents all Hellenistic astrology.

### 3.2 `interpretive_school`

Use for later interpretive schools/families with a recognizable methodological or semantic program.

Initial research ID:

```text
school:modern:psychological_astrology
```

This ID may support claims sourced to authors working within psychological astrology. It must not be projected backward onto historical sources without evidence.

### 3.3 `historical_context`

Use for period/geographic contexts that help scope a claim but are not themselves doctrine.

Initial research IDs:

```text
context:classical_antiquity
context:early_modern
context:modern_contemporary
context:southern_hemisphere_reception
```

A historical context may coexist with multiple competing doctrines.

### 3.4 `meta_perspective`

Use for scholarship or source-analysis perspectives rather than astrology interpretation doctrine.

Initial research IDs:

```text
meta:history_of_astrology
meta:historiography
```

These contexts can support claims about what traditions taught, how they changed, or how sources should be interpreted. They do not become natal-reading traditions.

### 3.5 `synthesis_mode`

Use for how multiple admitted traditions are combined at L5.

Initial research IDs:

```text
synthesis:single_tradition
synthesis:parallel_comparison
synthesis:explicit_blend
```

`explicit_blend` means the user/project deliberately requested a blended synthesis. It does **not** authorize silent averaging of incompatible doctrines.

### 3.6 `implementation_mode`

Use for software/retrieval behavior that is not semantic doctrine.

Initial research IDs:

```text
implementation:retrieval_first
```

Implementation mode must never satisfy a query's tradition requirement by itself.

## 4. Canonical context record

Candidate record:

```text
AstrologyTraditionContext
- context_id
- dimension
- label
- parent_id
- aliases[]
- description
- source_refs[]
- admission_status
- notes[]
```

Candidate dimensions:

```text
doctrinal_lineage
interpretive_school
historical_context
meta_perspective
synthesis_mode
implementation_mode
```

`parent_id` is optional and must not be used merely to force every label into a tree.

## 5. Claim-side context

A claim should not rely on an untyped flat tradition tag for canonical routing.

Candidate claim-side fields:

```text
tradition_context_refs[]
historical_context_refs[]
meta_context_refs[]
```

Existing `tradition_tags[]` remain useful as source-local / legacy discovery metadata during research migration.

A future registry migration can therefore preserve:

```text
tradition_tags[]
```

while adding canonical typed refs.

## 6. Query-side selection

A query should resolve tradition intent explicitly before claim retrieval.

Candidate structure:

```text
requested_tradition_contexts[]
requested_synthesis_mode
tradition_resolution_status
```

Candidate resolution statuses:

```text
explicit
inferred_from_named_school
unspecified
ambiguous
unsupported
```

Rules:

1. A named school such as psychological astrology can resolve to a canonical school ID.
2. Generic words such as `classical` should remain ambiguous unless the project has a bounded mapping for the specific query.
3. `unspecified` must not silently select a preferred project doctrine.
4. When multiple traditions are requested, default to `parallel_comparison` unless explicit blending is requested and allowed.
5. A retrieval miss does not authorize substitution from another tradition.

## 7. Initial mapping of current repository tags

Research mapping:

| Existing tag | Canonical treatment | Notes |
|---|---|---|
| `hellenistic` | `lineage:hellenistic` | broad lineage/context |
| `ptolemaic` | `lineage:hellenistic:ptolemaic` | identifiable lineage/framework |
| `classical` | legacy/discovery alias only for now | too broad for canonical routing without further decision |
| `history_of_astrology` | `meta:history_of_astrology` | scholarship/meta, not doctrine |
| `early_modern` | `context:early_modern` | historical context |
| `modern` | legacy/discovery alias only for now | too broad to identify a school |
| `psychological_astrology` | `school:modern:psychological_astrology` | modern interpretive school/family |
| `blended` | `synthesis:explicit_blend` only when explicitly selected | not a doctrine source by itself |
| `retrieval_first` | `implementation:retrieval_first` | implementation behavior only |

The intentionally conservative choice is to **not** canonize broad `classical` or `modern` tags as single production traditions yet.

## 8. Routing consequences

### 8.1 Historical claims

A Ptolemaic historical claim may carry:

```text
tradition_context_refs:
- lineage:hellenistic:ptolemaic
historical_context_refs:
- context:classical_antiquity
```

This does not make the claim representative of every Hellenistic author.

### 8.2 Modern psychological claims

A Greene-style claim may carry:

```text
tradition_context_refs:
- school:modern:psychological_astrology
historical_context_refs:
- context:modern_contemporary
```

It must not be retrieved as if it were classical doctrine merely because both discuss Moon-Saturn symbolism.

### 8.3 Scholarly historical claims

A history-of-astrology source may carry:

```text
meta_context_refs:
- meta:history_of_astrology
historical_context_refs:
- context:early_modern
```

That source can support a claim about historical disagreement without becoming an interpretive school for natal synthesis.

### 8.4 Blended outputs

If a user explicitly requests blended interpretation:

```text
requested_synthesis_mode = synthesis:explicit_blend
```

L5 must still preserve source/tradition provenance and conflict boundaries. Blending is an output policy, not evidence that incompatible doctrines agree.

## 9. Conflict interaction

Tradition taxonomy does not replace conflict groups.

Two claims can share the same broad lineage and still conflict. Two claims can come from different traditions and still be compatible within a bounded scope.

Therefore:

```text
taxonomy = applicability / routing context
conflict_group = recorded disagreement / non-collapsibility
```

Neither field should infer the other automatically.

## 10. Admission boundary

This taxonomy remains research-only.

It does **not**:

- adopt Ptolemaic doctrine for production;
- adopt psychological astrology for production;
- declare `classical` a single coherent school;
- declare `modern` a single coherent school;
- choose a default user-facing tradition;
- choose weights between traditions;
- establish scientific predictive validity;
- change production routing.

## 11. Migration strategy

Recommended sequence:

```text
1. freeze taxonomy IDs and dimensions
2. add typed context refs to current claim-family fixtures
3. validate unknown refs / wrong-dimension refs / parent cycles
4. add query-resolution regression for explicit / unspecified / ambiguous tradition intent
5. add parallel-comparison vs explicit-blend regression
6. define a production admission gate only after the above behavior is stable
```

Do not bulk-rewrite all historical `tradition_tags[]` before validator behavior exists.

## 12. Current decision

The minimum useful taxonomy is multi-dimensional rather than a single flat tree:

```text
doctrinal lineage
+ interpretive school
+ historical context
+ meta perspective
+ synthesis mode
+ implementation mode
```

The main safety decision is:

```text
source-local tags may remain broad
but canonical routing refs must say what kind of context they represent
```

**Current state: REFERENCE-ONLY / RESEARCH / NOT PRODUCTION-ROUTABLE.**
