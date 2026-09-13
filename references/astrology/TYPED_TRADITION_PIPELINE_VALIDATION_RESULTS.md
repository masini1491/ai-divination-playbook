# Typed Tradition Pipeline Validation Results

Status: **REFERENCE-ONLY / RESEARCH VALIDATION / NOT PRODUCTION-ROUTABLE**

Baseline: `masini1491/ai-divination-playbook@6667c084834508411d2a4b22cf85b03daf656a5e`

## 1. Goal

Connect the research tradition taxonomy to the existing deterministic chain:

```text
AstrologyQueryResolution
→ interpretation claim retrieval
→ L5 synthesis envelope
```

without silently falling back to broad legacy `tradition_tags[]` semantics.

## 2. New integration surface

Added:

```text
typed_tradition_pipeline.py
test_typed_tradition_pipeline.py
```

The integration layer is intentionally separate from the older 0.1.0 research components. It allows typed-routing behavior to be exercised without bulk-rewriting existing claim registries or silently changing legacy regression semantics.

## 3. Typed resolution contract

A typed executable route carries:

```text
tradition_resolution_status
requested_tradition_contexts[]
requested_synthesis_mode
route.tradition_context_refs_any[]
route.synthesis_mode
```

Research invariants:

- typed refs and legacy `tradition_tags_any[]` must not both select tradition in one executable route;
- typed refs must resolve to taxonomy contexts whose dimensions are `doctrinal_lineage` or `interpretive_school`;
- historical, meta, synthesis, and implementation contexts cannot masquerade as doctrine selectors;
- `requested_tradition_contexts[]` must exactly match the executable typed route;
- a resolved typed route requires `tradition_resolution_status = explicit | inferred_from_named_school`;
- `single_tradition` requires exactly one requested context;
- `parallel_comparison` / `explicit_blend` require at least two requested contexts.

## 4. Retrieval provenance

The typed retrieval wrapper filters the registry by canonical tradition context before calling the existing deterministic selector.

For legacy claims that have not yet been migrated, canonical contexts are projected only through the already-reviewed taxonomy mapping rules.

Selected claims carry:

```text
tradition_context_refs[]
```

The retrieval bundle carries:

```text
tradition_provenance:
  tradition_resolution_status
  requested_tradition_contexts[]
  requested_synthesis_mode
  covered_tradition_contexts[]
  missing_tradition_contexts[]
```

A retrieval miss does not authorize cross-tradition substitution.

## 5. Multi-tradition coverage gate

For:

```text
synthesis:parallel_comparison
synthesis:explicit_blend
```

all requested tradition contexts must be represented by selected claims.

If any requested context is missing:

```text
retrieval_status = tradition_coverage_incomplete
synthesis_status = blocked_tradition_coverage_incomplete
```

The L5 envelope then contains no synthesis units and explicitly requires the downstream renderer not to substitute, invent, or collapse the missing perspective.

This is stronger than merely returning the claims that happened to match.

## 6. L5 provenance

When composition succeeds, the synthesis envelope preserves:

```text
tradition_provenance
route_snapshot.tradition_context_refs_any[]
route_snapshot.synthesis_mode
synthesis_units[].tradition_context_refs[]
```

Additional disclosure rules:

- `parallel_comparison` → keep traditions visibly separate; do not average into consensus;
- `explicit_blend` → state that blending was explicitly requested and preserve contributing tradition provenance plus conflicts.

## 7. Regression cases authored

The dedicated test module covers:

1. single named school reaches `ready_for_l5`;
2. typed provenance survives retrieval and synthesis;
3. mixed legacy + typed selector fails;
4. non-doctrine context fails;
5. route/resolution tradition mismatch fails;
6. single-tradition cardinality fails on multiple contexts;
7. complete parallel comparison covers all requested contexts;
8. partial comparison coverage blocks synthesis;
9. missing tradition is not cross-substituted;
10. explicit blend remains explicit in L5 provenance.

## 8. Validation boundary

The repository GitHub Actions workflow currently executes:

```text
python -m unittest discover -s tests -v
python tools/playbook_check.py .
```

It does **not** automatically execute tests under `references/astrology/`.

Therefore this round must not describe a green repository workflow as proof that `test_typed_tradition_pipeline.py` executed in CI.

The dedicated tests are deterministic and stdlib-only, but CI admission for research-folder tests is a separate governance/validation decision outside this mutation scope.

## 9. Migration consequence

The next migration can now add explicit:

```text
tradition_context_refs[]
```

to the current claim-family registries incrementally.

Once migrated, the explicit typed refs take precedence over legacy discovery tags. Broad tags such as `classical` and `modern` remain non-canonical selectors.

## 10. Non-goals

This work does not:

- choose a default astrology tradition;
- declare classical or modern astrology to be single coherent schools;
- bulk-migrate every registry;
- promote research evidence to production;
- establish predictive or clinical validity;
- change root method routing;
- change production user-facing output.

**Current state: REFERENCE-ONLY / RESEARCH / NOT PRODUCTION-ROUTABLE.**
