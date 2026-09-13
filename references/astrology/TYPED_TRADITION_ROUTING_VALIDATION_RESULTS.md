# Typed Tradition Routing Validation Results

Status: **REFERENCE-ONLY / RESEARCH VALIDATION / NOT PRODUCTION-ROUTABLE**

Branch baseline: `masini1491/ai-divination-playbook@c5f4f1e4de4322f3642447cdba8e7030f8b4057c`

## 1. Goal

Connect the research tradition taxonomy to executable routing behavior without prematurely rewriting all existing claim registries or promoting broad legacy tags into doctrine selectors.

The bounded adapter is:

```text
tradition_taxonomy_example.json
→ typed_tradition_routing.py
→ canonical tradition context resolution
→ legacy-claim typed-context projection
→ bounded claim filtering
```

This is a migration bridge, not production routing.

## 2. Contract exercised

The adapter enforces these research decisions:

```text
named doctrine/school → canonical typed context
broad classical/modern → fail closed as ambiguous
unspecified tradition → no silent default
multiple traditions → parallel comparison by default
explicit blend → requires explicit blend request
historical/meta/implementation context → cannot satisfy doctrine selector
legacy flat tags → only canonical doctrine/school mappings may project upward
retrieval miss → no cross-tradition substitution
```

## 3. Compatibility strategy

Existing registries currently retain `tradition_tags[]`. They are not bulk-rewritten in this round.

For migration compatibility:

1. if a claim already has `tradition_context_refs[]`, those refs are authoritative for typed routing;
2. otherwise the adapter may project legacy `tradition_tags[]` through `legacy_tag_mappings`;
3. only mappings with `mapping_status = canonical` are considered;
4. only `doctrinal_lineage` and `interpretive_school` contexts can satisfy a tradition selector;
5. ambiguous or contextual tags such as `classical`, `modern`, `early_modern`, `history_of_astrology`, and `retrieval_first` cannot become doctrine selectors merely because they occur on a claim.

This prevents compatibility support from becoming silent semantic promotion.

## 4. Regression fixture

`test_typed_tradition_routing.py` defines 15 deterministic cases covering:

- taxonomy fixture structural validity;
- named psychological school resolution;
- named Ptolemaic lineage resolution;
- broad `classical` ambiguity;
- broad `modern` ambiguity;
- unspecified tradition/no silent default;
- meta context rejection as doctrine selector;
- multi-tradition default to `parallel_comparison`;
- explicit blend rejected without explicit request marker;
- explicit blend accepted with explicit request marker;
- legacy claim mapping to typed school context;
- ambiguous legacy tags not promoted;
- explicit typed claim refs taking precedence over legacy tags;
- no cross-tradition substitution on miss;
- filtering selects only the requested school.

## 5. Validation boundary

The repository's current GitHub Actions workflow runs root `tests/` plus the structural checker. The dedicated Astrology research regression file lives under `references/astrology/`, so PR CI does **not** by itself prove these 15 reference tests executed.

Accordingly, this record does not claim a CI execution PASS for the dedicated reference regression unless a future runtime run explicitly executes:

```text
python -m unittest references/astrology/test_typed_tradition_routing.py -v
```

The artifact is nevertheless deterministic and executable; this round's repository mutation remains bounded to `references/astrology/**` rather than expanding CI/test ownership merely to obtain a green badge.

## 6. What is now closed

The taxonomy is no longer documentation-only. There is now executable research behavior for:

```text
flat source-local tags
→ typed tradition contexts
→ fail-closed query selection
→ synthesis-mode selection
→ claim filtering
```

The critical semantic guard is that historical context, meta perspective, synthesis mode, and implementation mode remain distinct from doctrine/school selection.

## 7. Remaining gap

The next migration step is bounded integration into the existing query-resolution / retrieval pipeline:

```text
AstrologyQueryResolution
→ tradition_resolution_status
→ requested_tradition_contexts[]
→ requested_synthesis_mode
→ deterministic selector
→ L5 envelope preserves typed route snapshot
```

Only after that behavior is stable should current claim-family registries be migrated from discovery-only `tradition_tags[]` toward explicit `tradition_context_refs[]`.

Production admission remains a later, separate decision.

**Current state: REFERENCE-ONLY / RESEARCH / NOT PRODUCTION-ROUTABLE.**
