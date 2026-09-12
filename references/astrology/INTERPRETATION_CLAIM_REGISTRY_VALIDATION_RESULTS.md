# Astrology Interpretation Claim Registry Validation Results

Status: **REFERENCE-ONLY / RESEARCH VALIDATION / NOT PRODUCTION-ROUTABLE**

Schema under validation:

```text
schema_name    = interpretation_claim_registry
schema_version = 0.1.0-research
```

Baseline repository main when this normalization round began:

`8d6681c83db1238288067329843b382a797cc8ae`

Runtime used for validation:

- Python `3.13.5`
- standard library only
- no network dependency in validator execution
- no external schema package

## 1. Why this round was run

The previous validator established a low-false-positive integrity gate, but its repo-file compatibility test was skipped in the isolated runtime because the actual registry JSON files were not present beside the tests.

This round closes that evidence gap and makes a schema-normalization decision.

The two current registries were first read from current GitHub `main` and executed against the existing validator before mutation:

```text
domicile_claim_family_registry.json          PASS / 0 errors
saturn_moon_aspect_claim_family_registry.json PASS / 0 errors
```

That result matters: schema normalization is not being used to hide invalid evidence. Both registries were already structurally valid under the compatibility contract.

## 2. Schema-drift observation

The two valid registries nevertheless represented two research generations.

Examples:

```text
legacy                         newer
------                         -----
admission_state                admission_status
statement                      normalized_statement
confidence                     confidence_status
conflict_group_refs            conflict_group_ids
author                         author_or_org
revision                       immutable_revision
compact scalar storage labels  canonical storage arrays
```

The divergence was large enough that keeping every future registry alias-tolerant would increase maintenance cost and make the machine-readable contract progressively weaker.

Decision:

```text
freeze 0.1.0-research canonical schema now
+
retain legacy compatibility for old/unversioned regression fixtures
+
apply stricter checks to versioned registries
```

## 3. Canonical schema artifact

The research contract is documented in:

`INTERPRETATION_CLAIM_REGISTRY_SCHEMA_DRAFT.md`

Versioned records now declare:

```text
schema_name = interpretation_claim_registry
schema_version = 0.1.0-research
record_status = REFERENCE-ONLY
record_kind = interpretation_claim_family_registry
production_routable = false
privacy.contains_real_birth_data = false
```

## 4. Migrated current registries

Both current concrete registries are now versioned:

- `domicile_claim_family_registry.json`
- `saturn_moon_aspect_claim_family_registry.json`

The domicile registry required the substantive shape migration because it was the older compact style.

The migration preserved the existing evidence decisions while normalizing field names and making provenance/guard fields explicit.

No migration step was allowed to:

- promote `REFERENCE_ONLY` to claim authority;
- raise confidence;
- invent source independence;
- resolve the southern-hemisphere doctrine conflict;
- claim predictive or clinical validity;
- create production routing.

The Saturn-Moon registry was already close to the canonical shape and mainly required explicit schema identity.

## 5. Versioned strict checks

The validator still accepts bounded legacy aliases for **unversioned** regression fixtures.

Once either schema identity field is present, the record is treated as versioned and the validator additionally requires:

1. exact `schema_name` and `schema_version`;
2. explicit `production_routable = false`;
3. explicit `privacy.contains_real_birth_data = false`;
4. explicit `conflict_groups[]`;
5. canonical `admission_status[]` rather than `admission_state`;
6. canonical array-valued `storage_mode[]`;
7. `author_or_org` rather than legacy `author` when the field is supplied;
8. `immutable_revision` rather than legacy `revision` when the field is supplied;
9. explicit source `independence_status`;
10. `normalized_statement` rather than `statement`;
11. `confidence_status` rather than `confidence`;
12. explicit canonical `support_status`;
13. `conflict_group_ids[]` rather than `conflict_group_refs`.

The existing integrity checks remain in force:

- unique source / claim / conflict IDs;
- source role / admission / storage enums;
- no `PRODUCTION_ADMITTED` in the research validator;
- no unverified-web claim/policy promotion;
- upstream refs must resolve and cannot self-reference;
- claim source/conflict refs must resolve;
- conflict claim refs must resolve;
- `REFERENCE_ONLY` sources cannot self-promote an unqualified supported claim;
- `multi_source_supported` requires at least two distinct source refs and at least two evidence roots;
- explicit real-birth-data fixtures fail closed;
- research results cannot grant production authority or scientific predictive validity.

## 6. Executed direct registry validation

The current registry payloads were executed directly through the validator in the isolated Python runtime after normalization.

Observed result:

```text
domicile_claim_family_registry.json           PASS / 0 errors
saturn_moon_aspect_claim_family_registry.json PASS / 0 errors
```

This closes the previous round's actual-registry runtime gap.

## 7. Executed unittest result

The validator, test module, and both current registry JSON files were placed together in the same isolated filesystem directory.

Command shape:

```text
python -m unittest -v test_interpretation_claim_registry_validator.py
```

Observed result:

```text
Ran 38 tests
OK
```

Breakdown:

```text
38 passed
0 failed
0 errors
0 skipped
```

The formerly skipped current-registry compatibility test executed and passed.

The suite now covers:

- both legacy research styles remaining readable when unversioned;
- valid canonical/versioned fixture;
- invalid schema name/version;
- missing explicit production/privacy guards;
- legacy aliases forbidden in versioned records;
- canonical source arrays;
- canonical claim statement/confidence/support/conflict fields;
- production/scientific promotion guards;
- duplicate IDs;
- unknown/self upstream refs;
- invalid source role/admission/storage values;
- unverified-web promotion;
- invalid claim layer;
- unresolved source/conflict refs;
- insufficient multi-source count;
- fake multi-source independence through shared upstream;
- `REFERENCE_ONLY` authority promotion;
- direct current-registry compatibility.

## 8. Evidence boundary

This validation supports the claim that the current machine-readable registry structures satisfy the declared research contract.

It does **not** validate:

- astrological truth;
- predictive accuracy;
- clinical or psychological validity;
- historical claims beyond their recorded source provenance;
- legal reuse beyond recorded source/licensing metadata;
- whether declared source lineage is factually complete;
- whether an orb, sect rule, tradition taxonomy, or weighting policy should be adopted;
- production readiness.

The machine gate protects evidence bookkeeping and promotion boundaries, not astrology's empirical validity.

## 9. Research conclusion

The registry line has moved from compatibility-only validation to a versioned research contract:

```text
source-admission architecture
→ concrete claim families
→ executable integrity validator
→ actual-registry execution
→ canonical 0.1.0-research schema
→ migrated current registries
→ strict versioned validation
```

The key design choice is:

```text
legacy artifacts stay readable
but
new versioned artifacts cannot keep inventing aliases
```

This keeps research provenance intact while preventing schema drift from becoming permanent architecture.

## 10. Next gap

The next highest-value work is no longer another schema rename. It is behavioral use of the registry:

```text
retrieval behavior regression
→ citation/output provenance contract
→ conflict-selection regression
→ explicit tradition taxonomy
→ additional claim families as needed for coverage
→ explicit production admission only after those gates
```

**Current state: REFERENCE-ONLY / RESEARCH / NOT PRODUCTION-ROUTABLE.**
