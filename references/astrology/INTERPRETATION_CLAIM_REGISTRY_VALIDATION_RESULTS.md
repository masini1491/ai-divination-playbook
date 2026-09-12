# Astrology Interpretation Claim Registry Validation Results

Status: **REFERENCE-ONLY / RESEARCH VALIDATION / NOT PRODUCTION-ROUTABLE**

Baseline repository main when this validation round began:

`19fde16b2ec43069b1258a845f3d38d26cf05017`

Runtime used for the isolated validation pass:

- Python `3.13.5`
- standard library only
- no network dependency
- no external schema package

## Scope

This validator covers deterministic structural invariants shared by the first two concrete Astrology interpretation claim-family registries:

- `domicile_claim_family_registry.json`
- `saturn_moon_aspect_claim_family_registry.json`

It intentionally tolerates bounded research-era schema differences already present between those registries, including:

- `admission_state` vs `admission_status`
- `statement` vs `normalized_statement`
- `confidence` vs `confidence_status`
- `conflict_group_refs` vs `conflict_group_ids`
- compact legacy storage/independence labels used by the domicile registry

This is a compatibility validator, not a schema-freeze decision.

## Deterministic checks implemented

The validator checks:

1. research envelope remains `REFERENCE-ONLY` and uses `interpretation_claim_family_registry`;
2. research records cannot set `production_routable = true`;
3. research results cannot grant production authority or claim scientific predictive validity;
4. source IDs, claim IDs, and conflict-group IDs are unique;
5. source roles and admission states come from the bounded research taxonomy;
6. `PRODUCTION_ADMITTED` is rejected in this research validator;
7. an `UNVERIFIED_WEB_SOURCE` cannot be promoted to claim/policy/production admission;
8. storage mode and source-independence labels are from the accepted research vocabulary;
9. upstream source references resolve and cannot self-reference;
10. claim layers are limited to `L3` / `L4`;
11. each claim has a statement and at least one source reference;
12. claim source references resolve;
13. claim-to-conflict and conflict-to-claim references resolve;
14. `REFERENCE_ONLY` sources cannot by themselves support an unqualified `supported` claim;
15. `multi_source_supported` requires at least two distinct source refs;
16. `multi_source_supported` also requires at least two independent/upstream evidence roots, so derivative copies do not create fake consensus;
17. source-evidence fixtures reject an explicit `contains_real_birth_data = true` marker.

## Executed test result

Command shape:

```text
python -m unittest -v test_interpretation_claim_registry_validator.py
```

Observed isolated result:

```text
Ran 27 tests
OK (skipped=1)
```

Breakdown:

- 26 tests executed and passed.
- 1 compatibility test was skipped because the isolated test directory did not contain the repository's two actual registry JSON files.

The executed cases include both positive fixture styles and negative mutation tests for:

- invalid research envelope;
- production promotion;
- real-birth-data fixture marker;
- duplicate source/claim IDs;
- unknown/self upstream refs;
- invalid source role/admission/storage values;
- unverified-web promotion;
- invalid claim layer or missing statement;
- unresolved source/conflict refs;
- insufficient multi-source count;
- fake multi-source independence through shared upstream;
- `REFERENCE_ONLY` authority promotion.

## Actual-registry runtime status

The test suite contains a compatibility test that directly reads:

```text
domicile_claim_family_registry.json
saturn_moon_aspect_claim_family_registry.json
```

when they are present beside the test file in a repository checkout or CI workspace.

That direct filesystem check was **not executed in the isolated tool runtime used during this round**, because the GitHub repository itself was not checked out locally. The validator design was instead checked against synthetic fixtures matching both observed registry schema styles, and the current registry contents were bounded-read through the GitHub connector before implementation.

Therefore the evidence claim is:

```text
validator logic and regression cases executed successfully
+
current registry structures were connector-reviewed for compatibility
```

not:

```text
remote GitHub files were executed directly in the isolated runtime
```

A later repo-local or CI run should execute the included actual-file compatibility test without the skip.

## Explicit non-goals

This validator does **not** determine:

- whether an astrology interpretation is true;
- whether a historical source is doctrinally correct;
- whether a practitioner interpretation is psychologically valid;
- whether a source is legally reusable beyond the metadata already recorded;
- whether two sources are genuinely independent beyond declared lineage metadata;
- whether an orb, sect rule, tradition taxonomy, or synthesis weighting should be adopted;
- whether astrology has clinical or predictive validity;
- whether any claim should become production doctrine.

It also does not infer semantic privacy from arbitrary prose. The current privacy check is only for an explicit machine-readable fixture marker.

## Research conclusion

The first two concrete claim-family registries now have enough repeated structure for a low-false-positive executable integrity gate.

The most important machine-enforced boundary is:

```text
source exists
!= claim is supported
!= source is independent
!= source is production-admitted
!= claim is scientifically valid
```

The validator preserves those distinctions while remaining tolerant of bounded research-schema evolution.

## Next gap

Before schema freeze or production use, the next useful work is:

```text
repo-local actual-registry execution
→ schema normalization decision
→ conflict/lineage regression fixtures across more claim families
→ retrieval behavior regression
→ citation/output provenance contract
→ explicit tradition taxonomy
→ explicit production admission
```

**Current state: REFERENCE-ONLY / RESEARCH / NOT PRODUCTION-ROUTABLE.**
