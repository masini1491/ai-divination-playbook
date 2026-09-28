# Zi Wei Backlog

Authority: **COORDINATION-ONLY / NOT PRODUCTION AUTHORITY / NOT RESEARCH EVIDENCE / NOT ROUTING AUTHORITY**

Purpose: preserve the current Zi Wei maintenance and expansion queue so fresh ChatGPT sessions do not have to reconstruct open work from historical research documents. This file records work status only. Canonical technical truth remains in `ZIWEI.md`, admission manifests, production tools, and `references/ziwei/**`.

## Status vocabulary

```text
OPEN        = identified and not yet started
BLOCKED     = cannot proceed until blocked_by is closed
IN_PROGRESS = actively being implemented in a bounded task
DONE        = completion gate satisfied and canonical read-back verified
DEFERRED    = intentionally not current work
```

Priority vocabulary:

```text
P0 = correctness / stale-state reconciliation before feature expansion
P1 = near-term architecture or feature admission
P2 = later expansion
SHARED = cross-method work not owned only by Zi Wei
```

## Current baseline

Last reviewed against:

```text
ai-divination-playbook main
d3daa1aaf65891ba72f8e2b81589abe77ed692b5
```

This SHA is review evidence only, not a pin. Every maintenance task must resolve current `main` again before mutation.

## Recommended implementation order

This order is a coordination priority, not production authority. It is optimized for functional importance: correctness/applicability first, then deterministic host transport, then staged dynamic capability, then natal semantic resolution, then broader input/profile expansion.

Standing guard (enforced alongside affected changes, not a one-shot feature):

- **ZW-P0-003 — Keep Zi Wei production stack / transport / admission synchronized**

Execution order:

1. **ZW-P1-025 — Natal palace occupancy and empty-palace applicability facts**
2. **ZW-P1-026 — Exact-main Zi Wei deterministic handoff artifact**
3. **ZW-P1-030 — Dynamic calculation runtime**
4. **ZW-P1-040 — Dynamic interpretation claim corpus**
5. **ZW-P2-060 — Sparse same-palace major-star combination claims**
6. **ZW-P2-050 — Body-Palace overlay interpretation admission**
7. **ZW-P2-020 — Sparse star×palace contextual claims**
8. **ZW-P2-010 — M1 high-impact auxiliary stars**
9. **ZW-P2-030 — Non-Asia/Taipei civil-time input normalization**
10. **ZW-P2-040 — True-solar-time policy**

Ordering rationale:

- correctness / exact applicability outranks semantic enrichment;
- exact-main handoff is a bounded host-transport improvement that should land before the larger dynamic-runtime surface grows;
- dynamic calculation and interpretation are admitted **layer by layer** (decadal → yearly → monthly → daily → hourly) rather than as one monolithic waterfall;
- same-palace and star×palace contextual claims should reuse the canonical occupancy/applicability facts from `ZW-P1-025`, not derive a parallel geometry path;
- same-palace pair semantics and Body-Palace overlay deepen ordinary natal reading without replacing existing L5 composition;
- sparse source-explicit contextual expansion outranks broad auxiliary/input policy expansion for current natal reading quality;
- non-Asia/Taipei and true-solar support remain later profile/input expansion for the current product audience.

## P0 — correctness and reconciliation

### ZW-P0-001 — Reconcile stale Zi Wei research/current-state documents

- type: MAINTENANCE / RECONCILIATION
- status: DONE
- priority: P0
- owner: Zi Wei maintenance
- blocked_by: none
- canonical_evidence:
  - `ZIWEI.md`
  - `ZIWEI_PRODUCTION_ADMISSION_V1.json`
  - `ZIWEI_CALENDAR_ADMISSION_V1.json`
  - `ZIWEI_BRIGHTNESS_ADMISSION_V1.json`
  - `ZIWEI_MATERIALIZATION.md`
  - `PLAYBOOK_INDEX.json`
- stale_targets:
  - `references/ziwei/README.md`
  - `references/ziwei/CALCULATION_ENGINE_RESEARCH.md`
  - `references/ziwei/PRODUCTION_READINESS_GAP_ANALYSIS_V0.md`
  - `references/ziwei/PRODUCTION_SCOPE_A_NATAL_FIRST_V0.md`
  - `references/ziwei/PRODUCTION_NATAL_PROVIDER_ADMISSION_V0.md`
  - `references/ziwei/INTERPRETATION_ADMISSION_REVIEW_V0.md`
  - `references/ziwei/PRODUCTION_SCHEMA_CANDIDATES_V0.md` where a supersession note is needed
- problem:
  - several historical research documents still say G8 / production routing is blocked even though explicit Zi Wei production routing exists;
  - some documents still describe natal provider / brightness state as if later Gregorian, brightness and materialization admissions did not exist;
  - these stale statements can mislead fresh gap reviews.
- completion_gate:
  - preserve historical research decisions;
  - add current-state or superseded annotations instead of rewriting history;
  - distinguish `explicit Zi Wei routing admitted` from `ordinary unspecified auto-routing intentionally false`;
  - document current optional brightness profile `ziwei.brightness.iztro_v1`;
  - document Gregorian adapter and deterministic materialization current state;
  - structural/behavioral validation passes.
- completion_evidence:
  - current-state annotations added without rewriting historical research decisions;
  - explicit production routing vs ordinary unspecified auto-routing is now distinguished;
  - Gregorian adapter, optional brightness profile and deterministic materialization current state are documented.

### ZW-P0-002 — Harden conditional applicability / activation semantics

- type: BUG / CORRECTNESS
- status: DONE
- priority: P0
- owner: Zi Wei interpretation/runtime maintenance
- blocked_by: none
- canonical_evidence:
  - `references/ziwei/INTERPRETATION_CLAIM_REGISTRY_SCHEMA_V0.md`
  - `references/ziwei/EXECUTABLE_RETRIEVAL_COMPOSITION_V0.md`
  - `references/ziwei/interpretation_retrieval_v0.py`
  - `references/ziwei/ziwei_interpretation_claim_registry_batch1.json`
  - `references/ziwei/ziwei_interpretation_claim_registry_batch2.json`
  - `references/ziwei/ziwei_executable_behavioral_fixtures_v0.json`
- problem:
  - current retrieval eligibility is defined by `requires[]` / `forbids[]`;
  - some `star_conditional` statements describe favorable-support or auxiliary conditions while those conditions appear only in `modifiers[]`;
  - current fixtures can select such a conditional rule while separately recording blocked dependencies;
  - `modifiers[]` is not globally equivalent to `requires[]`, so a blanket modifier→require conversion is not valid.
- completion_gate:
  - define an explicit machine-readable distinction between a relevant conditional rule and a condition demonstrated in the current chart;
  - preserve legitimate context-only modifier metadata;
  - fail closed when a claim requires an unavailable deterministic condition;
  - reconcile existing 52-claim fixtures and production selection behavior;
  - add regression coverage for satisfied / unsatisfied / not-computed conditional activation;
  - no model-memory substitution.
- completion_evidence:
  - merged by PR #163 at `fd5e22f275bdad6aa23076179e68115cce1c177e`;
  - conditional activation states are explicit: `not_required / satisfied / unsatisfied / not_computed`;
  - production selection fails closed for undemonstrated fact-gated conditions;
  - 52-claim admitted corpus count is unchanged.

### ZW-P0-003 — Keep Zi Wei production stack / transport / admission synchronized

- type: MAINTENANCE / REGRESSION
- status: OPEN
- priority: P0
- owner: Zi Wei production maintenance
- blocked_by: none
- canonical_evidence:
  - `ZIWEI.md`
  - `ZIWEI_PRODUCTION_ADMISSION_V1.json`
  - `ZIWEI_CALENDAR_ADMISSION_V1.json`
  - `ZIWEI_MATERIALIZATION.md`
  - `PLAYBOOK_INDEX.json`
  - `tools/ziwei_runtime.py`
  - `schemas/ziwei/ZIWEI_READING_REQUEST_V1.schema.json`
  - `schemas/ziwei/ZIWEI_READING_RESULT_V1.schema.json`
- problem:
  - Zi Wei production capabilities span runtime, typed schemas, admission manifests, deterministic bundle/materialization, machine index, backlog/current-state owners and behavioral/structural validation;
  - prior feature admissions required follow-up closure/reconciliation work when one of those surfaces lagged behind the merged implementation;
  - upcoming dynamic-scope work materially increases the risk of schema/admission/transport/current-state drift.
- completion_gate:
  - any future Zi Wei production scope change updates every materially affected owner in the same bounded change;
  - runtime/schema/admission/bundle/materialization/index/backlog identities remain mutually consistent;
  - no derived transport artifact is promoted to source authority;
  - no completed production capability is repeatedly rediscovered as open because a coordination/current-state surface was left stale;
  - affected behavioral/structural validation and canonical read-back close in the same work unit.
- rule:
  - this is a standing reconciliation guard, not a request to change current production behavior immediately.
## P1 — product architecture

### ZW-P1-004 — Minguo year-notation input adapter

- type: INPUT NORMALIZATION / PRODUCTION ADAPTER EXTENSION
- status: DONE
- priority: P1
- owner: Zi Wei maintenance
- scope:
  - explicit 民國 year notation only;
  - deterministic conversion `CE year = 民國 year + 1911`;
  - preserve existing Gregorian timezone/calendar/Zi Wei policy semantics;
  - no natural-language freeform date parser beyond explicit Minguo year notation;
  - no pre-Republic year notation.
- closure:
  - `tools/ziwei_year_notation.py` preserves source/converted facts and returns the existing typed `GregorianBirthInput`;
  - `民國1年 → 1912`, `民國76年 → 1987`, `民國115年 → 2026` regression-covered;
  - invalid / zero / negative Minguo years and invalid converted Gregorian dates fail closed;
  - ordinary CE deterministic bundle remains unchanged; explicit Minguo input performs a same-commit tiny pre-runtime helper read only.
- admission owner: `ZIWEI_CALENDAR_ADMISSION_V1.json`

### ZW-P1-003 — Calendar deterministic-data architecture evaluation

- type: ARCHITECTURE / CALENDAR DATA POC
- status: DONE
- priority: P1
- owner: Zi Wei maintenance
- blocked_by: none
- evidence owner: `references/ziwei/ZIWEI_CALENDAR_DATA_POC.md`
- current decision:
  - option B (build-time pinned upstream → repo-local deterministic calendar data → project-owned resolver) is production-admitted; option A is retained only as the independent build/parity reference oracle;
  - POC uses bounded Gregorian month shards and does not vendor `third_party/lunar-python/**`;
  - full 1900-01-01..2100-12-31 machine parity is complete: 73,414 days / 204,716 comparisons / 0 mismatches in the strongest run;
  - daily-shard candidate-window footprint measured 8,525,044 bytes total;
  - compact Gregorian-year / lunar-month-interval POC completed with 73,414 ordinary-date checks / 4,824 full-hour New-Year cases / 202 year-edge 23:00 cases / 0 mismatches;
  - interval encoding uses 2,692 interval records in 202 year shards and measured 471,865 bytes total (about 94.46% smaller / 18.07x smaller than daily shards), while preserving ordinary 1-file and 23:00 cross-year at-most-2-file lookup;
  - interval encoding is the admitted production storage architecture; the independent upstream reference path is not a production runtime;
  - product-supported Gregorian production range is 1900-01-01..2100-12-31; 2101 exists only as the 2100-12-31 23:00 policy-tail shard and does not extend admitted user input;
  - exact candidate dataset is materialized at `data/calendar/ziwei_tw_interval/v1/**` with 202 Gregorian-year shards (1900..2101 including the 2101 policy tail), 2,692 intervals and 471,865 shard bytes;
  - candidate dataset aggregate SHA-256 is `4913a39e770afcd21eedc387523c572b8c4fc6469889c28f6ea75613f8984d79`; pinned installed-source inventory SHA-256 is `bf49ea69241171a8e5b5a85ca07748c88b00f5ce392f25c21617e398c9c9a712`;
  - range-parameterized builder/validator verifies the existing pinned 34-file upstream Git-blob inventory before generation, writes manifest/provenance/attribution metadata, closes exact shard inventory + per-shard/aggregate hashes and clean deterministic rebuild;
  - dependency-free query-bounded resolver is production-bound through `tools/ziwei_calendar_provider.py`: ordinary dates require one year shard; 2100-12-31 23:00 requires the 2100 + 2101 policy-tail pair; manifest/shard hash and supported-range failures are fail closed;
  - `ZIWEI_CALENDAR_ADMISSION_V1.json` allowlists the exact dataset identity + aggregate hash and classifies pinned `lunar_python==1.4.8` as build/parity source only;
  - ChatGPT transport bundle v2 carries 18 repo-local runtime/retrieval artifacts + exact calendar manifest, no lunar_python runtime files; year shards are same-commit query-bounded acquisitions;
  - independent parity remains available through `tools/ziwei_calendar_upstream_reference.py`, so post-admission dataset validation does not collapse into data-vs-data self-comparison;
  - admission bridge run `36125250303` PASSed bundle-v2 rebuild/check, admission-focused regression, bounded-diff cleanup and no-runtime-dependency assertions; PR #201 full `validate` + `casting-runtime` PASS on head `bea22c3b24a5a351480a02bcb75cce646bcb27f9`.
- scope boundary:
  - does not modify `ZW-P1-020` Four Transformations semantics;
  - does not create repository-layer architecture policy outside `REPOSITORY_ARCHITECTURE.md`.

### ZW-P1-001 — Unified Zi Wei runtime and typed request/result interface

- type: ARCHITECTURE
- status: DONE
- priority: P1
- owner: Zi Wei production runtime
- blocked_by:
  - ZW-P0-002
  - ZW-P1-002
- pre_change_state:
  - four combinatorial public entrypoints owned composition;
  - no canonical `tools/ziwei_runtime.py`;
  - no versioned Zi Wei reading request/result schema.
- implementation_state:
  - `tools/ziwei_runtime.py` owns typed production composition through `run_ziwei()`;
  - `schemas/ziwei/ZIWEI_READING_REQUEST_V1.schema.json` and `ZIWEI_READING_RESULT_V1.schema.json` define the v1 interface;
  - legacy `run_scope_a_*` entrypoints are compatibility adapters;
  - `brightness_v1` is selected through `optional_modules`, not a new canonical entrypoint;
- target:
  - one request owner for birth input, temporal scope, requested subjects, optional modules and profile selections;
  - one result owner for normalized input, deterministic facts, selected claims, omissions, conflicts, provenance and authority state;
  - avoid combinatorial `with_x_and_y` pipeline proliferation.
- completion_gate:
  - versioned request/result schema;
  - deterministic runtime entrypoint;
  - Scope-A + Gregorian + optional brightness behavior preserved;
  - fail-closed unsupported scopes/modules;
  - transport/materialization path updated if runtime source set changes;
  - CI passes; product smoke is required only where the repository workflow actually runs it.
- completion_evidence:
  - merged by PR #166 at `babd0bd814e00d804fd2d29f400bd3a89e320538`;
  - `tools/ziwei_runtime.py` owns the canonical typed `run_ziwei()` composition path;
  - request/result schemas are versioned under `schemas/ziwei/`;
  - four legacy entrypoints remain compatibility adapters with prior public result surfaces;
  - Gregorian and `brightness_v1` composition converge through the same runtime;
  - unsupported temporal scope/module/profile fails closed;
  - deterministic bundle was regenerated with runtime + schemas;
  - Validate Playbook run #616: unit tests, structural checker and casting-runtime succeeded; PR `production-smoke` was skipped by workflow and is not reported as PASS.

### ZW-P1-002 — Normalize Zi Wei production / research execution boundary

- type: ARCHITECTURE / BEHAVIOR-PRESERVING
- status: DONE
- priority: P1
- owner: Zi Wei production runtime / research-boundary maintenance
- blocked_by:
  - ZW-P0-002
  - ZW-P0-001
- pre_change_state:
  - `tools/ziwei_scope_a_pipeline.py` production-loads `references/ziwei/interpretation_retrieval_v0.py`;
  - the same production pipeline loads `references/ziwei/validate_uncertainty_safety_delivery_v0.py` as executable delivery logic;
  - the deterministic ChatGPT bundle includes those two research-path Python executables plus the three admitted research registries;
  - the three claim registries remain historically `production_routable=false` and are explicitly allowlisted by production admission;
  - root admission manifests and flat `tools/ziwei_*.py` layout remain consistent with current repository conventions, including Astrology.
- target:
  - production runtime no longer imports executable Python from `references/ziwei/**`;
  - move only the production-executed retrieval/delivery implementation to coherent production tooling owners;
  - keep research evidence, admission history and the currently admitted research registries in `references/ziwei/**` unless a separate production-data divergence trigger appears;
  - preserve the existing production allowlist/history policy for the 52 claims;
  - update materialization bundle sources, manifest pointers and targeted tests without semantic claim changes.
- non_goals:
  - no broad `references/ziwei/**` directory reorganization;
  - no `admissions/ziwei/` migration at this stage;
  - no `tools/ziwei/` package migration at this stage;
  - no duplicate `data/ziwei/production/` claim snapshot without an independent authority/divergence need;
  - no conditional-applicability semantic fix in the relocation PR.
- completion_gate:
  - production execution has no Python import/load dependency on `references/ziwei/**`;
  - research registries retain historical non-routable metadata and explicit production allowlisting;
  - runtime/materialization source inventory and canonical pointers are synchronized;
  - stale old executable-path references are reconciled;
  - behavior-preserving targeted regression, bundle validation and production contract validation pass;
  - canonical read-back confirms only the intended ownership/path normalization.
- completion_evidence:
  - canonical production executables moved to `tools/ziwei_claim_retrieval.py` and `tools/ziwei_delivery.py`;
  - reference-path Python files remain compatibility shims only;
  - production pipeline no longer dynamic-loads Python from `references/ziwei/**`;
  - deterministic bundle contains no reference-path Python executables;
  - admitted research registries remain in `references/ziwei/**` with historical `production_routable=false` policy unchanged.

## P1 — feature admission

### ZW-P1-010 — M0 auxiliary stars: 左輔／右弼／文昌／文曲

- type: FEATURE / ADMISSION
- status: DONE
- priority: P1
- owner: Zi Wei auxiliary-star admission
- blocked_by:
  - ZW-P0-002
  - ZW-P1-001
- current_evidence:
  - `references/ziwei/MINOR_STAR_ADMISSION_TAXONOMY_V0.md`
  - `references/ziwei/CALCULATION_ENGINE_RESEARCH.md`
  - M0 = FIRST ELIGIBLE AUXILIARY GROUP
  - placement/source foundation = strong
- target:
  - deterministic M0 placement provider/profile;
  - deterministic fixtures;
  - auxiliary fact schema/provenance;
  - bounded M0 auxiliary-role policy claims with source context; independent historical star semantics require a separate future admission if desired;
  - conditional-activation integration with existing major-star claims;
  - optional production admission, not blanket minor-star admission.
- completion_gate:
  - exact placement/profile identity;
  - no automatic promotion of M1/M2/M3;
  - auxiliary-role policy claim corpus admitted separately from calculation facts; no independent historical semantic core is implied;
  - production manifest/pipeline/index updated;
  - ChatGPT transport bundle regenerated and verified if new runtime files are needed.
- completion_evidence:
  - optional module id: `m0_auxiliary_v1`;
  - admitted profile: `ziwei.auxiliary.m0.iztro_v1`;
  - deterministic provider: `tools/ziwei_m0_auxiliary_provider.py`;
  - admitted subjects are exactly 左輔／右弼／文昌／文曲; M1/M2/M3 remain excluded;
  - base Scope-A claim corpus remains 52; M0 adds 4 optional bounded auxiliary-role policy claims for a maximum of 56; these are not an admission of independent historical semantic cores for the four stars;
  - M0 exposes `fact_available:m0_auxiliary_stars`, not the broader `fact_available:auxiliary_stars`; generic `unsupported.auxiliary_stars` remains `not_computed`, while the M0-specific domain records its own computed state;
  - existing conditional activation integration is limited to claims whose complete condition domain is covered by M0;
  - deterministic transport bundle regenerated and verified by the M0 candidate bridge;
  - candidate bridge passed registry validation, M0 targeted tests, full unittest suite, `playbook_check.py`, and bundle build/check.

### ZW-P1-020 — Four Transformations production admission

- type: FEATURE / ADMISSION
- status: DONE
- priority: P1
- owner: Zi Wei Four-Transformation admission
- blocked_by:
  - ZW-P1-010
- canonical_research:
  - `references/ziwei/FOUR_TRANSFORMATION_VARIANT_REGISTRY.md`
  - `references/ziwei/FOUR_TRANSFORMATION_INTERPRETATION_RESEARCH_V0.md`
- current_state:
  - `sihua.default_v1` is the admitted project composite profile identity;
  - deterministic production provider exists at `tools/ziwei_sihua_provider.py` with explicit `sihua_profile_id`, profile revision, pinned complete 10-stem base-table provenance and one explicit project override (庚科：太陰 → 天府);
  - optional `sihua_v1` is production-admitted through `tools/ziwei_runtime.py`, typed request/result schemas and `ZIWEI_SIHUA_ADMISSION_V1.json`;
  - natal provider exposes deterministic `fact_available:star_locations` + exact `star_branch:<star>:<branch>` predicates from its already-computed major-star placements;
  - `references/ziwei/ziwei_interpretation_claim_registry_sihua_v0.json` contributes exactly 3 primary-source, fact-gated conditional claims (貪狼化祿四墓；太陽化忌五支例外；太陰化忌四支例外) only when `sihua_v1` is enabled;
  - base admitted claim count remains 52; combined optional-module maximum becomes 59 (M0 +4, sihua +3);
  - generic 祿／權／科／忌 outcome doctrine, cross-profile averaging and unsourced transformed-star prose remain fail closed;
  - deterministic ChatGPT bundle v2 includes the sihua provider + exact bounded sihua registry.
- completion_gate:
  - deterministic provider with explicit `sihua_profile_id`;
  - no cross-profile averaging;
  - profile selector / provenance;
  - fixtures and admission manifest;
  - source-explicit transformed-star claims only;
  - generic 祿／權／科／忌 outcome guarantees remain forbidden.
- completion_evidence:
  - calculation candidate admitted by PR #205 at `b26ea0400a042652ca63493f36ed9f18c6cfb14e`;
  - canonical closure cleanup merged by PR #206 at `5281d89a6b4caabb7c26d0b6222888e8d73d9f4a`;
  - optional module `sihua_v1` / profile `sihua.default_v1` preserves the pinned complete 10-stem base table plus the explicit 庚科 override;
  - exactly 3 source-explicit, fact-gated transformed-star claims are admitted; base Scope-A remains 52 and combined optional maximum is 59;
  - generic transformation outcome doctrine, cross-profile averaging and unsourced transformed-star prose remain fail closed;
  - deterministic ChatGPT bundle was regenerated from canonical sources and canonical read-back confirms the updated provider blob is embedded;
  - PR #206 Validate Playbook run `36134495166`: `validate` PASS, `casting-runtime` PASS, `production-smoke` skipped and is not reported as PASS.

## P1 — natal applicability correctness

### ZW-P1-025 — Natal palace occupancy and empty-palace applicability facts

- type: FEATURE / DETERMINISTIC FACTS / CLAIM APPLICABILITY
- status: DONE
- priority: P1
- owner: Zi Wei natal provider + interpretation retrieval
- blocked_by: none
- problem:
  - current natal provider computes 14 major-star branches, twelve-palace layout and opposite/Sanfang topology;
  - current retrieval facts expose `palace_present:<palace>`, `star_present:<star>`, `fact_available:star_locations` and `star_branch:<star>:<branch>`;
  - it does not expose per-palace major-star membership / count or an exact `empty_palace:<palace>` predicate;
  - admitted palace methodology already refers to empty-palace / opposite / Sanfang handling, but those claims currently remain `context_only` and cannot distinguish whether the current chart is actually empty in that palace.
- canonical_research:
  - `tools/ziwei_natal_provider.py`
  - `references/ziwei/PRODUCTION_NATAL_PROVIDER_ADMISSION_V0.md`
  - `references/ziwei/ziwei_interpretation_claim_registry_palaces_v0.json`
  - `references/ziwei/INTERPRETATION_RUNTIME_CONTRACTS_V0.md`
- target:
  - deterministic per-palace major-star membership;
  - deterministic major-star count / empty-palace predicate;
  - explicit fact-availability identity sufficient for exact claim applicability;
  - reuse existing palace geometry / opposite / Sanfang topology rather than creating a parallel geometry system.
- completion_gate:
  - exact star→palace and palace→major-star membership is deterministic and regression-covered;
  - empty-palace state is machine-visible and derived only from admitted major-star placements;
  - existing empty-palace conditional methodology can be fact-gated where source/admission warrants it;
  - raw occupancy facts remain separate from interpretation policy;
  - calculation provider does not hard-code "borrow from opposite" doctrine;
  - deterministic bundle / schemas / admission surfaces are updated only if the runtime contract materially requires it;
  - new occupancy/applicability facts are explicitly natal-baseline scoped (or inherit an unambiguous natal-baseline scope) and cannot collide with future dynamic-scope facts;
  - required CI passes and canonical read-back verifies no unrelated semantic widening.
- completion_evidence:
  - feature implementation merged by PR #256 at `1147d6709885e91f0e6ebe64ed30cf3987ad1a47`;
  - natal provider advanced to `ziwei-scope-a-natal-python@0.2.0` and exposes structured natal-baseline `palace_occupancy` plus `fact_available:palace_occupancy`, `star_in_palace:<star>:<palace>`, `major_star_count:<palace>:<count>` and `empty_palace:<palace>` facts;
  - Scope-A production pipeline advanced to `1.2.0` and exposes occupancy facts without widening the closed-world request/result temporal scope;
  - `ZW-PAL-MING-COND-002` and `ZW-PAL-CHILD-COND-002` are exact fact-gated empty-palace conditionals; generic topology methodology remains available through the existing domain claims;
  - base Scope-A corpus remains 52 claims and optional-module maximum remains 59; no new palace claim IDs, palace geometry or borrowing doctrine were admitted;
  - deterministic bundle was regenerated by the canonical generator through the temporary PR bridge; canonical main read-back matches provider blob `b1833688bdd87913e9c27208a1de5c28f379a024`, runtime blob `6a148c249bd158399e63fa9776145a3a018a1314`, and palace-registry blob `0976d41a0935f0722b3fbd43e870f388bad88067`;
  - PR #256 formal Validate Playbook run `36260888498`: `validate` PASS and `casting-runtime` PASS after stale research fixture expectations were reconciled; bundle check, Zi Wei deterministic regression selection, full unit suite and structural checker all passed.
- production_boundary:
  - `empty_palace` is a calculation/applicability fact, not an interpretation conclusion;
  - opposite / Sanfang / borrowing semantics remain source-backed interpretation responsibility;
  - no new palace geometry and no model-memory doctrine.

## P1 — host transport

### ZW-P1-026 — Exact-main Zi Wei deterministic handoff artifact

- type: MAINTENANCE / HOST TRANSPORT
- status: DONE
- priority: P1
- owner: Zi Wei deterministic materialization
- blocked_by: none
- problem:
  - current Zi Wei fast path correctly probes/reuses verified local cache and prefers direct byte/file-aware connector→filesystem handoff;
  - when direct handoff is unavailable, the current fallback moves the exact-commit deterministic bundle through bounded verified opaque transport;
  - the current bundle is compact but still contains 120 model-visible chunks, while the GitHub connector now exposes exact workflow-artifact listing/download primitives;
  - Astrology has validated an exact-main Actions handoff artifact as a temporary connector-backed transport convenience without changing source authority.
- target:
  - publish an exact-main Zi Wei deterministic handoff artifact from successful main-push validation;
  - artifact carries only the deterministic bundle, canonical bundle verifier, `PLAYBOOK_COMMIT` and machine-readable handoff manifest;
  - calendar year shards remain query-bounded same-commit acquisitions and are not packed into the handoff artifact.
- completion_gate:
  - cache reuse remains first;
  - direct byte/file-aware handoff remains preferred when available;
  - exact-main workflow artifact becomes the next fallback before model-visible opaque bundle transport;
  - artifact name / manifest binds exact repository commit and payload file identities;
  - downloaded artifact bytes / digest are verified when exposed by GitHub, then internal manifest/file identities are verified before bundle materialization;
  - artifact expiration/unavailability degrades only this transport path and falls back to the existing verified opaque bundle;
  - artifact is explicitly non-authoritative: it does not replace Git-tracked bundle, production admission or canonical source files;
  - ordinary calendar request remains 1 shard and 31 December 23:00 cross-year edge remains at most 2 shards;
  - regression / CI / canonical read-back confirm no production-semantic widening.
- completion_evidence:
  - implementation merged by PR #258 at `d3025243568f79a8d68ef957907b39fb62eba9b9`;
  - successful main-push Validate Playbook run `36262398945` produced `validate` PASS and `casting-runtime` PASS; unit tests, structural checker, Zi Wei handoff preparation, and Zi Wei artifact upload all passed;
  - exact-main artifact `10912972000` / `ziwei-deterministic-handoff-d3025243568f79a8d68ef957907b39fb62eba9b9` was published at 57,348 bytes with GitHub digest `sha256:341868711cd5866d9b040969934fb9b7ecccf49ce59067b5574b38bd4de42362`;
  - connector download materialized the connector-backed ZIP into the execution filesystem; its SHA-256 exactly matched the GitHub artifact digest;
  - `PLAYBOOK_COMMIT`, `HANDOFF_MANIFEST.json`, repository/commit identity, `calendar_shards_included=false`, and every manifest payload size/SHA-256 verified exactly;
  - artifact-contained canonical bundle verifier returned zero errors; materializer reconstructed 20 files with archive SHA-256 `c2723f57b8345acb3a06f608dcea72885f2049216e9672ea6f6be7806e189ce3` and preserved calendar query bounds 1 ordinary / 2 cross-year shards;
  - isolated `python -S` runtime smoke from the materialized cache returned `PRODUCTION_ADMITTED`, pipeline `1.2.0`, provider `0.2.0`, 39 selected claims and production `palace_occupancy` facts;
  - formal consumer evidence: `evals/product_runs/2026-09-27-ziwei-mat-beh-001-exact-main-artifact-d3025243.json`;
  - machine index now exposes already-admitted `sihua_v1`, optional maximum 59, and exact-main handoff metadata under standing guard `ZW-P0-003`;
  - artifact remains temporary/non-authoritative and absent/expired/invalid artifact state falls back to the existing same-commit bounded opaque bundle path without declaring Zi Wei unavailable.
- production_boundary:
  - host transport only; no Zi Wei calculation, interpretation or calendar semantics change.
## P1/P2 — temporal / dynamic

### ZW-P1-030 — Dynamic calculation runtime

- type: FEATURE / CALCULATION
- status: DONE
- priority: P1/P2
- owner: Zi Wei temporal runtime
- blocked_by: none
- stage_progress:
  - decadal / 大限: DONE — bounded calculation-only provider + V2 dynamic transport + admission merged and canonically read back; interpretation remains separately unadmitted;
  - yearly / 流年: DONE — bounded calculation-only provider + V3 dynamic transport + explicit lunar-year boundary + compatible decadal parent + target-year Si Hua facts merged and canonically read back; interpretation remains separately unadmitted;
  - monthly / 流月: DONE — bounded calculation-only provider + V4 dynamic transport + compatible yearly parent + split-after-day-15 leap policy merged and canonically read back; interpretation remains separately unadmitted;
  - daily / 流日: DONE — bounded calculation-only provider + V5 dynamic transport + compatible monthly parent + explicit normalized-lunar-day identity merged and canonically read back; interpretation remains separately unadmitted;
  - hourly / 流時: DONE — bounded calculation-only provider + V6 dynamic transport + compatible daily parent + explicit normalized-lunar-hour identity + project `next_day_at_23` Rat-hour policy merged and canonically read back; interpretation remains separately unadmitted;
- decadal_stage_evidence:
  - implementation merged by PR #261 at `f31a9c1089da36bbee4da82def4fb1766838e745`;
  - provider `ziwei-decadal-quanji-common-python@1.0.0` / profile `decadal.quanji_common_v1` is production-admitted for calculation only, with `age_basis=traditional_nominal_age`;
  - explicit V2 dynamic request/result contracts admit only `temporal_scope=decadal`; existing V1 natal request/result remain closed to `natal_baseline`;
  - explicit `gender` + `target_lunar_year` are required; no prose/memory gender inference, no natal fallback, and yearly/monthly/daily/hourly remain unsupported;
  - canonical bundle read-back matches main provider/runtime/V2-schema Git blob identities and now carries 130 bounded transport chunks;
  - PR #261 Validate Playbook run `36267237273`: `validate` PASS and `casting-runtime` PASS; load pack, load budget, Zi Wei bundle, unit suite and structural checker all passed;
  - successful main-push run `36267370007`: `validate` PASS and `casting-runtime` PASS; unit suite, structural checker, exact-main Zi Wei handoff preparation and upload all passed;
  - main-push artifact `10914591363` / `ziwei-deterministic-handoff-f31a9c1089da36bbee4da82def4fb1766838e745` was published with digest `sha256:dd355858cf0b2877197d05e3b61aaf818575551e8282cb630057a38ff262928d`;
  - no dynamic interpretation claim family was admitted; natal 52 claims were not promoted into decadal predictions.
- yearly_stage_evidence:
  - implementation merged by PR #264 at `6e1f7b50dfe1358572a02361afa922f65e2932b5`;
  - provider `ziwei-yearly-year-branch-python@1.0.0` / profile `yearly.year_branch_common_v1` is production-admitted for calculation only with `year_boundary=lunar_year_explicit_v1`;
  - explicit V3 dynamic request/result contracts admit `decadal|yearly`; V2 remains decadal-only and V1 remains natal-only;
  - same explicit `target_lunar_year` must resolve inside an admitted `decadal.quanji_common_v1` parent; no yearly fallback to natal/decadal facts;
  - target-year Heavenly Stem reuses admitted `sihua.default_v1` for calculation facts only; no yearly interpretation or generic Four-Transformation prediction is granted;
  - canonical bundle read-back matches main provider/runtime/V3-schema Git blob identities and carries 135 bounded transport chunks;
  - PR #264 final Validate Playbook run `36273965471`: `validate` PASS and `casting-runtime` PASS;
  - successful main-push run `36274097883`: `validate` PASS and `casting-runtime` PASS; unit suite, structural checker, exact-main Zi Wei handoff preparation and upload all passed;
  - main-push artifact `10916846230` / `ziwei-deterministic-handoff-6e1f7b50dfe1358572a02361afa922f65e2932b5` was published at 63,319 bytes with digest `sha256:8ba3e01f281b04138101d98ad3d1a11d0a4cee0fecd6655443c932882c6c97e4`;
  - monthly / daily / hourly and all dynamic interpretation remain unadmitted.
- monthly_stage_evidence:
  - implementation merged by PR #271 at `35b5a2e7c87791610d5a465736e17abf97304dd6`;
  - provider `ziwei-monthly-doujun-python@1.0.0` / profile `monthly.doujun_effective_month_split15_v1` is production-admitted for calculation only with compatible yearly parent scope;
  - explicit V4 dynamic request/result contracts admit `decadal|yearly|monthly`; V3 remains yearly-max, V2 remains decadal-only, and V1 remains natal-only;
  - monthly target requires explicit normalized lunar year/month/day, leap-month identity and calendar provenance; leap-month 12 day 16+ cross-year rollover remains fail-closed;
  - no monthly Si Hua, flow-star reconstruction, daily/hourly calculation, or dynamic interpretation was admitted;
  - monthly bridge run `36277520547` completed successfully; focused monthly regressions, Zi Wei bundle regeneration/check, load-pack regeneration/check and load-budget checks passed;
  - generated-cache commit `46e100f6abba938c8cb74e4490c098bd97a40523` regenerated the Zi Wei bundle and removed the temporary monthly bridge; human evidence commit `1daaf23dd2b952932f107d059504ea1c9a73c191` re-triggered formal PR validation;
  - PR #271 final Validate Playbook run `36277678251`: `validate` PASS and `casting-runtime` PASS; unit suite, structural checker, Zi Wei bundle/regression selection and all preceding validation gates passed; PR-context exact-commit artifact prepare/upload were skipped;
  - exact-main canonical read-back confirms monthly provider, monthly admission, root V4 runtime admission, V4 request/result schemas, PLAYBOOK_INDEX routing, and canonical bundle source membership;
  - successful main-push run `36277901629`: `validate` PASS and `casting-runtime` PASS; unit suite, structural checker, exact-main Zi Wei handoff preparation and upload all passed;
  - exact-main artifact `10916659950` / `ziwei-deterministic-handoff-35b5a2e7c87791610d5a465736e17abf97304dd6` was published at 66,442 bytes with digest `sha256:e9e6408c8781360e7d661cbd16316c3ff486d785e786d04a7ec29d08c045d7ab`.
- daily_stage_evidence:
  - implementation merged by PR #274 at `6f773180b5dd669066137868d4c1e675fba9cca9`;
  - provider `ziwei-daily-monthly-parent-python@1.0.0` / profile `daily.monthly_parent_lunar_day_v1` is production-admitted for calculation only with compatible monthly parent scope;
  - pinned primary `RedSC1/js-ephemeris-lite@559d4957bc063a6e03a3c810066be4eccf3ea2be` advances the monthly parent branch by lunar `day - 1`; pinned comparator `SylarLong/iztro@2c7ef9be669df7b19d1799f4dce335fed3794f78` computes `dailyIndex = monthlyIndex + lunarDay - 1`;
  - explicit V5 dynamic request/result contracts admit `decadal|yearly|monthly|daily`; V4 remains monthly-max, V3 yearly-max, V2 decadal-only and V1 natal-only;
  - daily target identity is explicit `normalized_lunar_day` with lunar year/month/day, leap flag and calendar provenance; monthly parent leap policy remains authoritative;
  - physical day pillar, timestamp/day-divide inference, daily Si Hua, flow stars, hourly calculation and dynamic interpretation remain unadmitted;
  - daily bridge run `36278853192` completed successfully: focused regressions, Zi Wei bundle regeneration/check, ChatGPT load-pack regeneration/check and load-budget checks passed;
  - generated-cache bot commit `667d6c8639d2302d701b9eeff0c3931ebe9b5aa0` regenerated the Zi Wei bundle and removed the temporary daily bridge; human evidence commit `916b0ef566b56825aa299537148dd84907349142` re-triggered formal PR validation;
  - PR #274 final Validate Playbook run `36278893558`: `validate` PASS and `casting-runtime` PASS; unit suite, structural checker, Zi Wei bundle/regression selection and all preceding validation gates passed; PR-context exact-commit artifact prepare/upload were skipped;
  - exact-main canonical read-back confirms daily provider, daily admission, root V5 runtime admission, V5 request/result schemas, PLAYBOOK_INDEX routing and regenerated bundle source identity;
  - successful main-push run `36278998543`: `validate` PASS and `casting-runtime` PASS; unit suite, structural checker, exact-main Zi Wei handoff preparation and upload all passed;
  - exact-main artifact `10918216153` / `ziwei-deterministic-handoff-6f773180b5dd669066137868d4c1e675fba9cca9` was published at 68,305 bytes with digest `sha256:187f241fd5c6ff40d8fe221ae76994cc4afa4718a07d462654ab8bd94a4e4c37`.
- hourly_stage_evidence:
  - implementation merged by PR #277 at `ba776c119427f1966317f4f8270af60f73166b50`;
  - provider `ziwei-hourly-daily-parent-python@1.0.0` / profile `hourly.daily_parent_hour_branch_next_day_23_v1` is production-admitted for calculation only with compatible daily parent scope;
  - pinned primary `RedSC1/js-ephemeris-lite@559d4957bc063a6e03a3c810066be4eccf3ea2be` advances the daily parent branch by resolved hour index; pinned comparator `SylarLong/iztro@2c7ef9be669df7b19d1799f4dce335fed3794f78` computes `hourlyIndex = dailyIndex + hour-branch index`;
  - both implementations expose separate late-Rat boundary handling; production v1 therefore binds the already-admitted project calendar policy `rat_hour_policy=next_day_at_23` rather than claiming a unique doctrine;
  - explicit V6 dynamic request/result contracts admit `decadal|yearly|monthly|daily|hourly`; V5 remains daily-max, V4 monthly-max, V3 yearly-max, V2 decadal-only and V1 natal-only;
  - hourly target identity is explicit `normalized_lunar_hour` with lunar year/month/day, leap flag, `hour_branch`, Rat-hour policy identity and calendar provenance;
  - physical hour pillar, alternate Rat-hour policy, hourly Si Hua, flow stars and dynamic interpretation remain unadmitted;
  - hourly bridge run `36279918280` completed successfully: focused hourly regressions, Zi Wei bundle regeneration/check, ChatGPT load-pack regeneration/check and load-budget checks passed;
  - generated-cache bot commit `50c6ea5f045d2aa3743f69e9d1c342b098688ca0` regenerated the Zi Wei bundle and removed the temporary hourly bridge; human evidence commit `71f6ee50a5d075731a78bf0458a7b7a5fd0d7185` re-triggered formal PR validation;
  - PR #277 final Validate Playbook run `36279968429`: `validate` PASS and `casting-runtime` PASS; unit suite, structural checker, Zi Wei bundle/regression selection and all preceding validation gates passed; PR-context exact-commit artifact prepare/upload were skipped;
  - exact-main canonical read-back confirms hourly provider, hourly admission, root V6 runtime admission, V6 request/result schemas, PLAYBOOK_INDEX routing and regenerated bundle source identity;
  - successful main-push run `36280084942`: `validate` PASS and `casting-runtime` PASS; unit suite, structural checker, exact-main Zi Wei handoff preparation and upload all passed;
  - exact-main artifact `10918214713` / `ziwei-deterministic-handoff-ba776c119427f1966317f4f8270af60f73166b50` was published at 69,982 bytes with digest `sha256:8aed0244533a7c22cd124b4ceaf0ce2b3060737dcad50917cd246633e38ea79d`;
  - all five contiguous dynamic calculation layers are now production-admitted for calculation only; dynamic interpretation remains governed separately by `ZW-P1-040`.
- sequence:
  1. decadal / 大限
  2. yearly / 流年
  3. monthly / 流月
  4. daily / 流日
  5. hourly / 流時
- staging_rule:
  - admit calculation one contiguous temporal layer at a time;
  - a child layer cannot be admitted without compatible parent-scope identity;
  - each admitted layer may unlock the corresponding `ZW-P1-040` interpretation stage without waiting for all five calculation layers to finish.
- canonical_research:
  - `references/ziwei/TEMPORAL_CONTEXT_INTERPRETATION_RESEARCH_V0.md`
  - `references/ziwei/CALCULATION_ENGINE_RESEARCH.md`
- completion_gate:
  - exact temporal scope and target identity;
  - parent-scope linkage;
  - boundary/profile identity;
  - relevant sihua/auxiliary profile identity where applicable;
  - engine/revision provenance;
  - explicit typed request/result schema evolution strategy for dynamic scopes;
  - current V1 natal-only closed-world contracts remain compatible and are not silently widened;
  - target timestamp/calendar identity and temporal provenance are machine-visible;
  - no natal fallback when requested dynamic layer is unavailable.

### ZW-P1-040 — Dynamic interpretation claim corpus

- type: FEATURE / INTERPRETATION
- status: DONE
- priority: P1/P2
- owner: Zi Wei temporal interpretation
- blocked_by:
  - corresponding admitted calculation stage in ZW-P1-030
- stage_progress:
  - decadal interpretation: DONE — V7 bounded methodology interpretation merged and canonically read back; exactly 2 source-backed claims are admitted, while natal-claim promotion、generic十年吉凶、具體事件與 high-stakes determinism remain fail-closed;
  - yearly interpretation: DONE — V8 bounded methodology interpretation merged and canonically read back; exactly 3 source-backed / project-bounded claims are admitted, while generic流年吉凶、yearly Si Hua斷語、具體事件與 high-stakes determinism remain fail-closed;
  - monthly interpretation: DONE — V9 bounded methodology interpretation merged and canonically read back; exactly 3 bounded claims are admitted, while generic本月吉凶、monthly Si Hua／flow stars、具體日／時事件與 high-stakes determinism remain fail-closed;
  - daily interpretation: DONE — V10 bounded methodology interpretation merged and canonically read back; exactly 3 practitioner/tradition-bounded claims are admitted, while generic今日吉凶、day pillar、daily Si Hua／flow stars、具體流時事件與 high-stakes determinism remain fail-closed;
  - hourly interpretation: DONE — V11 bounded methodology interpretation merged and canonically read back; exactly 3 profile-bounded claims are admitted, while physical hour pillar、五鼠遁時干、hourly Si Hua／flow stars、generic時辰吉凶、具體事件與 high-stakes determinism remain fail-closed;
- staging_rule:
  - decadal interpretation may start after decadal calculation admission;
  - yearly interpretation may start after yearly calculation admission;
  - monthly / daily / hourly follow the same layer-local gate;
  - the umbrella item remains open until the intended dynamic interpretation scope is closed, but later calculation layers do not block already-eligible earlier interpretation work.
- decadal_interpretation_stage_evidence:
  - implementation merged by PR #280 at `f63974a9667e81831b610c1d34e206b878f0b3a3`;
  - V7 decadal interpretation admits exactly `ZW-D10-METHOD-CONTEXT-001` and `ZW-D10-METHOD-CORROBORATION-002` from `ziwei_interpretation_claim_registry_decadal_v1.json`;
  - production authority is bounded methodology only: computed decadal period/life-palace context + lower-layer corroboration rule; natal-claim promotion, generic吉凶、concrete event prediction and high-stakes determinism are not admitted;
  - default natal registries remain natal-only; the decadal registry is explicitly loaded only by the V7 decadal path;
  - first bridge run `36281361092` found a test-only projection mismatch; test corrected at `94f8669aa51751a3b20dac6f79d21db4842faf8b` without widening runtime semantics;
  - successful bridge run `36281425735`: 31 focused regressions PASS, claim-registry validator PASS, Zi Wei bundle regeneration/check PASS, ChatGPT load-pack regeneration/check PASS, load-budget PASS;
  - generated-cache bot commit `efed994abaf8341afcedf8e61fdca901baddab8e` regenerated the canonical bundle and removed the temporary bridge; human evidence commit `a69508b4f9a5f43369e46527ca867bf2f1d3ff42` re-triggered formal PR validation;
  - PR #280 formal run `36281474844`: `validate` PASS and `casting-runtime` PASS; full unit suite and structural checker passed; PR-context exact-commit artifact prepare/upload were skipped;
  - exact-main canonical read-back confirms V7 runtime, decadal interpretation admission, 2-claim registry, root production admission and PLAYBOOK_INDEX routing at `f63974a9667e81831b610c1d34e206b878f0b3a3`;
  - exact-main run `36281589408`: `validate` PASS and `casting-runtime` PASS; full unit suite, structural checker, exact-main Zi Wei handoff preparation and upload all passed;
  - exact-main artifact `10919032233` / `ziwei-deterministic-handoff-f63974a9667e81831b610c1d34e206b878f0b3a3` was published at 73,286 bytes with digest `sha256:c205d77412bf1baac301ce932fc969a0542f67176ba29987ec2e8d9fb487cdec`.
- yearly_interpretation_stage_evidence:
  - implementation merged by PR #283 at `b938bacce0088f775b6fe43c8ab2a2aa924a2d65`;
  - V8 yearly interpretation admits exactly `ZW-Y1-METHOD-TOPOLOGY-001`, `ZW-Y1-METHOD-PARENT-002` and `ZW-Y1-METHOD-BOUNDARY-003` from `ziwei_interpretation_claim_registry_yearly_v1.json`;
  - production authority is bounded methodology only: same-layer sanfang/opposition context + compatible decadal-parent composition + no-generic-yearly-filler boundary; natal/decadal claim promotion, generic yearly fortune, yearly Si Hua interpretation, concrete-event prediction and high-stakes determinism are not admitted;
  - V8 is additive: V7 yearly interpretation remains NOT_ADMITTED, while V8 preserves the V7 decadal bounded interpretation and adds yearly only;
  - first bridge run `36287574927` proved 35 focused regressions PASS and the 3-claim registry validator PASS; its only failure was the independent `explicit_research_astrology` load-budget ratio at `0.8048`;
  - routing summaries were compacted without changing authority at `7b3b69ca233594b2b3a07a067e4242474f477eb6` and `3cea4cd6d552ef570d53c1f3a8c557083b31067b`;
  - successful yearly bridge run `36287724153`: 35 focused regressions PASS, registry validator PASS, Zi Wei bundle PASS, ChatGPT load-pack PASS, `explicit_research_astrology` ratio `0.7996`, overall load budget PASS;
  - generated-cache bot commit `c0b3ff7d874bb3e72460ffd3b60061805e2c41ee` changed only the canonical Zi Wei bundle, generated load pack and removal of the temporary bridge; human evidence commit `768b0100a4f45cbbc9c8b37ef590a1cc4dba4c8e` re-triggered formal validation;
  - PR #283 formal run `36287781413`: `validate` PASS and `casting-runtime` PASS; full unit suite and structural checker passed; PR-context exact-commit artifact steps were skipped;
  - exact-main canonical read-back confirms V8 runtime, yearly interpretation admission, 3-claim registry, root production admission and PLAYBOOK_INDEX routing at `b938bacce0088f775b6fe43c8ab2a2aa924a2d65`;
  - exact-main run `36287885656`: `validate` PASS and `casting-runtime` PASS; full unit suite, structural checker, exact-main Zi Wei handoff preparation and upload all passed;
  - exact-main artifact `10921401398` / `ziwei-deterministic-handoff-b938bacce0088f775b6fe43c8ab2a2aa924a2d65` was published at 75,416 bytes with digest `sha256:0016740286414c3b0c967668b4a87057895167c5b53821dba9c70a1a4e7b00bb`.
- monthly_interpretation_stage_evidence:
  - implementation merged by PR #286 at `e54b1730d61dba875959a271e9410e4b9a7b2efc`;
  - V9 monthly interpretation admits exactly `ZW-M1-METHOD-IDENTITY-001`, `ZW-M1-METHOD-PARENT-002` and `ZW-M1-METHOD-BOUNDARY-003` from `ziwei_interpretation_claim_registry_monthly_v1.json`;
  - production authority is bounded methodology only: Doujun/effective-month month identity + compatible yearly-parent composition + no-generic-monthly-filler boundary; natal/decadal/yearly claim promotion, generic monthly fortune, monthly Si Hua/flow-star reconstruction, concrete daily/hourly prediction and high-stakes determinism are not admitted;
  - V9 is additive: V8 monthly interpretation remains NOT_ADMITTED, while V9 preserves V7/V8 decadal/yearly bounded interpretation and adds monthly only;
  - first monthly bridge run `36291105587`: 47 focused regressions PASS but registry validator correctly rejected `layer=L5`; registry-only contract fix `408c550b823e59cf0284b895598261c3dfae653b` changed all 3 claims to canonical `L4` without changing interpretation semantics;
  - successful monthly bridge run `36291152590`: 47 focused regressions PASS, 3-claim registry validator PASS, Zi Wei bundle PASS, ChatGPT load-pack PASS, `explicit_research_astrology` load ratio `0.8000`, overall load budget PASS;
  - generated-cache bot commit `24ba0e456bb8a3ad38053b1ef88caf25d446d469` changed only the canonical Zi Wei bundle, generated load pack and removal of the temporary bridge; human evidence commit `578c36731d41739350f01f8dac985190b68ba024` re-triggered formal validation;
  - PR #286 formal run `36291201924`: `validate` PASS and `casting-runtime` PASS; full unit suite and structural checker passed; PR-context exact-commit artifact steps were skipped;
  - exact-main canonical read-back confirms V9 runtime, monthly interpretation admission, 3-claim registry, root production admission and PLAYBOOK_INDEX routing at `e54b1730d61dba875959a271e9410e4b9a7b2efc`;
  - exact-main run `36291341656`: `validate` PASS and `casting-runtime` PASS; full unit suite, structural checker, exact-main Zi Wei handoff preparation and upload all passed;
  - exact-main artifact `10921784224` / `ziwei-deterministic-handoff-e54b1730d61dba875959a271e9410e4b9a7b2efc` was published at 77,259 bytes with digest `sha256:8465f024d9b0405eadaf561e75bbd8dcdda20a99818c1c3f8101d58ac3d60ecf`.
- daily_interpretation_stage_evidence:
  - implementation merged by PR #289 at `1900a97ec112551f604601b276f8bc5cb90dfc1d`;
  - V10 daily interpretation admits exactly `ZW-D1-METHOD-IDENTITY-001`, `ZW-D1-METHOD-PARENT-002` and `ZW-D1-METHOD-BOUNDARY-003` from `ziwei_interpretation_claim_registry_daily_v1.json`;
  - production authority is practitioner/tradition-bounded methodology only: explicit lunar-day identity + compatible monthly-parent composition + no-generic-daily-filler boundary; natal/decadal/yearly/monthly claim promotion, day-pillar interpretation, daily Si Hua/flow-star reconstruction, generic daily fortune, concrete hourly prediction and high-stakes determinism are not admitted;
  - evidence class is preserved explicitly: the daily registry uses `PRACTITIONER_REFERENCE` sources and `named_tradition/project_adoption`, not `PRIMARY_TEXT/historical_core`;
  - V10 is additive: V9 daily interpretation remains NOT_ADMITTED, while V10 preserves V7–V9 decadal/yearly/monthly bounded interpretation and adds daily only;
  - first daily bridge run `36292164990` found a test-only V6 hourly fixture omission; fixed at `83a9c7b5c288bd39ccf9addd7b98b8cbe962d185` without changing V10 runtime semantics;
  - second daily bridge run `36292215488`: 49 focused regressions PASS and 3-claim registry validator PASS; generated bundle/load-pack regenerated successfully, but `explicit_research_astrology` load ratio was `0.8002`;
  - bootstrap summary was compacted without changing authority at `b20f6c52c40243e806641fbad75558c793411c6e`;
  - successful daily bridge run `36292265611`: 49 focused regressions PASS, 3-claim registry validator PASS, Zi Wei bundle PASS, ChatGPT load-pack PASS, `explicit_research_astrology` load ratio `0.7997`, overall load budget PASS;
  - generated-cache bot commit `c5f8d42acbfd3afad8641054b8014b03d158581b` changed only the canonical Zi Wei bundle, generated load pack and removal of the temporary bridge; human evidence commit `4d0de204a2001037a54265b9eb6b6d61a8eab0ae` re-triggered formal validation;
  - PR #289 formal run `36292316639`: `validate` PASS and `casting-runtime` PASS; full unit suite and structural checker passed; PR-context exact-commit artifact steps were skipped;
  - exact-main canonical read-back confirms V10 runtime, daily interpretation admission, 3-claim registry, root production admission and PLAYBOOK_INDEX routing at `1900a97ec112551f604601b276f8bc5cb90dfc1d`;
  - exact-main run `36292422893`: `validate` PASS and `casting-runtime` PASS; full unit suite, structural checker, exact-main Zi Wei handoff preparation and upload all passed;
  - exact-main artifact `10922547919` / `ziwei-deterministic-handoff-1900a97ec112551f604601b276f8bc5cb90dfc1d` was published at 79,613 bytes with digest `sha256:68ffa1cc5ad8417a95790a4b19172a55918f39b0cdadf168b50ec3c9774a1a5b`.
- hourly_interpretation_stage_evidence:
  - implementation merged by PR #292 at `7e5fb2b57a3abed0d75e95fc3ddc35c12ac23899`;
  - V11 hourly interpretation admits exactly `ZW-H1-METHOD-IDENTITY-001`, `ZW-H1-METHOD-PARENT-002` and `ZW-H1-METHOD-BOUNDARY-003` from `ziwei_interpretation_claim_registry_hourly_v1.json`;
  - production authority is profile-bounded methodology only: explicit hour-branch identity + compatible daily-parent composition + no-generic-hourly-filler boundary; parent-claim promotion, physical hour-pillar interpretation, 五鼠遁 hour-stem reconstruction, hourly Si Hua/flow stars, generic hourly fortune, concrete event prediction and high-stakes determinism are not admitted;
  - evidence explicitly records method non-uniqueness: iztro documents the daily-palace-as-Zi-hour progression while DestinyNet preserves an alternate fixed-branch approach, so V11 does not claim a unique traditional rule;
  - V11 is additive: V10 hourly interpretation remains NOT_ADMITTED while V11 preserves V7–V10 bounded interpretation and adds hourly only;
  - successful hourly bridge run `36293420833`: 50 focused regressions PASS, 3-claim registry validator PASS, Zi Wei bundle PASS, ChatGPT load-pack PASS, `explicit_research_astrology` load ratio `0.7994`, overall load budget PASS;
  - generated-cache bot commit `dafb35c816d96164170a331c591146b6601403a8` changed only the canonical Zi Wei bundle, generated load pack and removal of the temporary hourly bridge; human evidence commit `f2cbc279df41d4fdc7b3e74931171861a3db21d6` re-triggered formal validation;
  - PR #292 formal run `36293469493`: `validate` PASS and `casting-runtime` PASS; full unit suite and structural checker passed;
  - exact-main canonical read-back confirms V11 runtime, hourly interpretation admission, 3-claim registry, root production admission and PLAYBOOK_INDEX routing at `7e5fb2b57a3abed0d75e95fc3ddc35c12ac23899`;
  - exact-main run `36293572450`: `validate` PASS and `casting-runtime` PASS; full unit suite, structural checker, exact-main Zi Wei handoff preparation and upload all passed;
  - exact-main artifact `10923515424` / `ziwei-deterministic-handoff-7e5fb2b57a3abed0d75e95fc3ddc35c12ac23899` was published at 81,968 bytes with digest `sha256:9ddaf92074360c3d67412f5b646a31a340645591d26d9321d1f343384c5b8a7f`;
  - all five intended temporal interpretation layers are now closed under their own bounded admission contracts: decadal / yearly / monthly / daily / hourly.
- rule:
  - natal 52 claims must not be silently reused as flow prediction claims.
- completion_gate:
  - scope-normalized claim schema/corpus per admitted temporal layer;
  - temporal applicability and provenance;
  - parent/child scope compatibility;
  - conflict/safety handling;
  - admission separate from dynamic calculation availability;
  - no generic flow prediction filler when a layer has calculation facts but no admitted interpretation claim.

### ZW-P1-050 — Full 14×12 star×palace coverage routing architecture

- type: ARCHITECTURE / ROUTING / COVERAGE INDEX
- status: DONE
- priority: P1
- owner: Zi Wei interpretation architecture
- blocked_by:
  - ZW-P2-025 — DONE
- shared_development_playbook_reviewed: `masini1491/ai-development-playbook@9236b42550b7f748cc6c5744075d106e643c6042`
- goal:
  - make all `14 × 12 = 168` major-star × palace identities machine-visible without forcing 168 dedicated L4 doctrines;
  - separate coverage completeness from dedicated production-claim admission;
  - optimize ChatGPT routing so ordinary lookup resolves one compact cell first, then loads only the minimum necessary L4/L5/conditional/high-risk detail.
- target_completion_metrics:
  - `total_cells = 168`;
  - `reviewed_cells` = cells with an explicit research/classification result, including deferred cells;
  - `resolved_cells` = cells with a stable production routing mode;
  - project completion target = `resolved_cells = 168`;
  - `DEDICATED_L4` count remains an independent quality/evidence metric and is not the 168-cell completion target.
- routing_modes:
  - `DEDICATED_L4` — exact source/admission-backed contextual override;
  - `BOUNDED_L5_COMPOSITION` — reviewed and resolved via existing star core + palace domain;
  - `CONDITIONAL_ONLY` — meaning is valid only under explicit admitted conditions/modifiers;
  - `HIGH_RISK_BOUNDED` — reviewed high-stakes domain with stricter safe-rendering policy;
  - `DEFERRED_EVIDENCE` — reviewed but not yet resolved; does not count toward `resolved_cells`;
  - `UNREVIEWED` — identity exists but no completed classification yet.
- architecture_boundary:
  - current 7 dedicated star×palace production claims remain unchanged during the architecture refactor;
  - full 168-cell coverage enumeration does not grant 168 dedicated L4 claims;
  - coverage/index metadata is routing/control-plane data, not semantic source authority;
  - research/provenance remains in canonical research/source owners;
  - generated Hot index must stay compact and must not inline long-form evidence, historical quotations or full doctrine text;
  - no model-memory filler for unresolved cells.
- first_stage_outputs:
  - `references/ziwei/STAR_PALACE_COVERAGE_ARCHITECTURE_V1.md`;
  - `schemas/ziwei/ZIWEI_STAR_PALACE_COVERAGE_V1.schema.json`;
  - project-owned coverage decision input for already researched V1–V3 cells;
  - deterministic generator for exactly 168 unique cell identities;
  - compact generated `indexes/ziwei/star_palace_coverage_v1.json`;
  - routing metadata in `PLAYBOOK_INDEX.json`;
  - structural/regression tests for 168 uniqueness, mode/count invariants, known dedicated L4 mapping and Hot-index size;
  - repository architecture adoption of `indexes/ziwei/**` as routing-only supporting surface.
- backfill_policy:
  - all current 7 production-admitted pairs become `DEDICATED_L4 / resolved`;
  - V1–V3 explicitly rejected redundant cells may become `BOUNDED_L5_COMPOSITION / resolved` when the research record establishes that generic composition is sufficient;
  - V1–V3 deferred/borderline cells remain `DEFERRED_EVIDENCE / reviewed-not-resolved`;
  - V4 preliminary discovery does not become resolved merely because it is listed in backlog.
- first_stage_candidate:
  - exact 168-cell identity grid uses canonical `奴僕宮` and does not create a second `交友宮` identity;
  - production registry is the sole source of `DEDICATED_L4` mappings;
  - V1–V3 backfill: 4 explicit redundant cells → `BOUNDED_L5_COMPOSITION`; 4 inconclusive/borderline cells → `DEFERRED_EVIDENCE`;
  - initial metrics = reviewed 15 / resolved 11 / unreviewed 153 / dedicated 7 / bounded-L5 4 / deferred 4;
  - V4 preliminary candidates remain unreviewed until V4 actually executes.
- closure:
  - architecture candidate merged by PR #334 to exact main `f0ef9b5fa303236ede34c77b1256144698b32765`;
  - canonical 168-cell coverage index is generated at `indexes/ziwei/star_palace_coverage_v1.json` by `tools/build_ziwei_star_palace_coverage.py`;
  - exact-main metrics = total 168 / reviewed 15 / resolved 11 / unreviewed 153 / dedicated L4 7 / bounded L5 4 / deferred 4;
  - Hot routing index remains compact (~26 KB UTF-8) and does not inline long-form doctrine;
  - existing star×palace production semantics remain unchanged at 7 dedicated L4 claims; this stage changes routing/coverage architecture only;
  - PR #334 candidate run `36384551472` PASSed coverage generator check, full unit suite, structural checker and casting-runtime;
  - exact-main run `36384710178` PASSed coverage generator check, full unit suite, structural checker, casting-runtime and exact-main Zi Wei handoff preparation/upload;
  - exact-main Zi Wei artifact `10953549703` / `ziwei-deterministic-handoff-f0ef9b5fa303236ede34c77b1256144698b32765` published with digest `sha256:90f91e4cd1b7fbda1b098c633120ee06480d401489d51cc7e10543535b6605d5`.
- next_authorized_action:
  - resume `ZW-P2-026` V4 research under the admitted 168-cell coverage architecture; update reviewed/resolved metrics in bounded batches.
- completion_gate:
  - schema/index/generator/architecture docs and tests are synchronized;
  - index contains exactly 168 unique canonical star×palace cells;
  - current dedicated L4 claim registry is referenced, not duplicated as source authority;
  - `reviewed_cells + unreviewed_cells = 168`;
  - `resolved_cells <= reviewed_cells <= 168`;
  - Hot index load footprint is measured and kept bounded;
  - existing 7 production interpretations and claim counts do not change during this architecture stage;
  - formal candidate validation + merge + exact-main read-back complete before architecture stage is marked DONE.

## P2 — later expansion

### ZW-P2-010 — M1 high-impact auxiliary stars

- type: FEATURE / ADMISSION
- status: DONE
- priority: P2
- owner: Zi Wei auxiliary-star research/admission
- blocked_by:
  - ZW-P1-010 — CLOSED
- subjects:
  - 天魁
  - 天鉞
  - 祿存
  - 天馬
  - 擎羊
  - 陀羅
  - 火星
  - 鈴星
  - 地空
  - 地劫
- evidence_decision:
  - pinned `SylarLong/iztro@2c7ef9be669df7b19d1799f4dce335fed3794f78` and `airicyu/fortel-ziweidoushu@2620cc895395f9f6994abd4927e739d31015c67d` independently expose equivalent natal placement rules for all 10 M1 stars;
  - reconciled calculation families are year-stem 魁鉞、year-stem 祿存/羊陀、year-branch trine 天馬、year-branch+hour 火鈴、hour-based 空劫;
  - pinned practitioner corpus `Renhuai123/nihai-tianji-corpus@c90006168195c0650328b7199669eb6a2d0cac93` supports their high-impact modifier roles, but its deterministic health/death/legal/promotion/wealth outcomes are explicitly excluded;
  - production semantics are therefore 10 bounded modifier-role policy claims, not independent historical semantic cores.
- canonical_research:
  - `references/ziwei/MINOR_STAR_ADMISSION_TAXONOMY_V0.md`
  - `references/ziwei/CALCULATION_ENGINE_RESEARCH.md`
  - `references/ziwei/M1_AUXILIARY_RESEARCH_V1.md`
  - `references/ziwei/ziwei_interpretation_claim_registry_m1_auxiliary_v1.json`
- implementation:
  - optional module `m1_auxiliary_v1`, profile `ziwei.auxiliary.m1.common_v1`, provider `tools/ziwei_m1_auxiliary_provider.py`;
  - M1 is natal-only and requires `m0_auxiliary_v1`; M1-alone requests fail closed;
  - M1 provider emits `fact_available:m1_auxiliary_stars`, 10 `star_present` facts and exact self/sanfang modifier relations;
  - only M0+M1 union adds generic `fact_available:auxiliary_stars` + `fact_available:star_relations`, preserving M0-alone behavior;
  - 六煞 relations additionally expose bounded generic `modifier_present:<major>:malefic_stars` applicability without event doctrine;
  - base natal claims remain 61; optional maximum is 78 = 61 + M0 4 + M1 10 + Sihua 3;
  - Scope-A pipeline advances to `1.5.0`; natal provider remains `0.3.0`.
- completion_gate:
  - source identity and pinned cross-implementation placement closure;
  - exact natal/profile identity for all 10 subjects;
  - M1→M0 dependency and generic completeness boundary fail closed;
  - bounded interpretation claims only; no high-stakes deterministic event doctrine;
  - explicit natal vs temporal identity; no M3/flow promotion;
  - runtime/schema/admission/index/materialization/bundle/current docs synchronized;
  - focused regressions + full CI + merge + exact-main artifact + canonical read-back before `DONE`.
- closure:
  - implementation merged by PR #318 at `d3daa1aaf65891ba72f8e2b81589abe77ed692b5`;
  - optional module `m1_auxiliary_v1` / profile `ziwei.auxiliary.m1.common_v1` production-admits exactly 天魁、天鉞、祿存、天馬、擎羊、陀羅、火星、鈴星、地空、地劫 for natal baseline;
  - M1 requires `m0_auxiliary_v1`; M1-alone requests fail closed, while M0-alone behavior remains unchanged;
  - only M0+M1 union emits generic `fact_available:auxiliary_stars` and `fact_available:star_relations`; canonical 14-major-star placements are materialized into self/sanfang major-star relation predicates before generic relation availability is asserted;
  - M1 adds exactly 10 bounded modifier-role policy claims; independent historical semantic cores, M2/M3, temporal/flow identities and deterministic health/death/legal/promotion/wealth doctrine remain unadmitted;
  - base natal claim count remains 61; maximum optional count is 78 = 61 + M0 4 + M1 10 + Sihua 3;
  - Scope-A pipeline is `1.5.0`; natal provider remains `0.3.0`;
  - generator bridge run `36329251553` PASSed M1 registry validation, focused M1/M0/production/Sihua/unified-runtime/materialization regressions, canonical Zi Wei bundle regeneration/check, ChatGPT load-pack regeneration/check, load-budget and bundle regression;
  - generator-owned cache commit `720f684e53a684a8196dfb339caa2a512afb563a` removed the temporary bridge after canonical cache regeneration;
  - formal PR #318 run `36329306523` PASSed `validate` + `casting-runtime`, including full unit suite and structural checker;
  - exact-main canonical read-back at `d3daa1aaf65891ba72f8e2b81589abe77ed692b5` confirms 10-star M1 admission, M0 dependency, 10-claim registry, historical-core=false, pipeline `1.5.0`, base 61 / max 78 and bounded generic completeness;
  - exact-main run `36329426662` PASSed `validate` + `casting-runtime`, full unit suite, structural checker and exact-main Zi Wei handoff preparation/upload;
  - exact-main artifact `10935411434` / `ziwei-deterministic-handoff-d3daa1aaf65891ba72f8e2b81589abe77ed692b5` published at 98,167 bytes with digest `sha256:9555861b2f5cfa55077d24d09aa18fd3e51119d7b4280f871a20862e24854a1a`.

### ZW-P2-020 — Sparse star×palace contextual claims

- type: FEATURE / INTERPRETATION
- status: DONE
- priority: P2
- owner: Zi Wei interpretation evidence
- blocked_by:
  - ZW-P1-025 — CLOSED
- evidence_decision:
  - pinned practitioner corpus `Renhuai123/nihai-tianji-corpus@c90006168195c0650328b7199669eb6a2d0cac93` supports exactly two materially distinct source-explicit contextual overrides in this bounded pass: `天相×命宮` and `天梁×官祿宮`;
  - `天相×命宮` remains practitioner/profile-bounded and preserves conflict with the existing historical evidence that 天相 can manifest authority under favorable supporting-star conditions;
  - `天梁×官祿宮` adds a bounded career/public-role social / coordination-load modifier without guaranteeing public office;
  - reviewed `太陽×財帛宮` / `太陽×官祿宮` were rejected as non-material restatements of existing star-core + palace-domain composition; `武曲×財帛宮`、`巨門×夫妻宮`、`天相×官祿宮` lacked a clean isolated materially distinct rule in the pass.
  - post-closure research follow-up `STAR_PALACE_CONTEXTUAL_RESEARCH_V2.md` records `貪狼×夫妻宮` as a historical bounded admission candidate; the Nihai spouse-age heuristic remains practitioner-only / deferred, `紫微×官祿宮` remains rejected as redundant, and `破軍×遷移宮` remains borderline / deferred; this follow-up does not change production admission.
- canonical_research:
  - `references/ziwei/STAR_PALACE_COMBINATION_RESEARCH_V0.md`
  - `references/ziwei/STAR_PALACE_CONTEXTUAL_RESEARCH_V1.md`
  - `references/ziwei/STAR_PALACE_CONTEXTUAL_RESEARCH_V2.md`
  - `references/ziwei/ziwei_interpretation_claim_registry_star_palace_context_v1.json`
- implementation:
  - schema `0.5.0-research` adds explicit `star_palace_context` with `star` / `palace` / `subjects[]` identity;
  - exact applicability reuses canonical `fact_available:palace_occupancy` + `star_in_palace:<star>:<palace>` facts from `ZW-P1-025`; no new geometry provider is introduced;
  - contextual specificity is higher than generic star conditional/core and palace-domain claims only on an exact admitted match; base evidence remains context;
  - production registry adds exactly 2 claims and rejects 14×12 Cartesian expansion;
  - base natal claim count candidate becomes 61 = 52 first-layer + 2 sparse same-palace pair + 5 Body-Palace + 2 sparse star×palace claims; optional M0 + Sihua maximum becomes 68;
  - Scope-A pipeline advances to `1.4.0`; natal calculation provider remains `0.3.0`.
- completion_gate:
  - only source-explicit materially distinct contextual overrides are eligible;
  - exact star×palace applicability facts / provenance are machine-matchable and derive from canonical occupancy;
  - tradition/profile conflicts remain explicit;
  - contextual claims outrank generic composition only inside admitted scope;
  - absence of a contextual claim continues to use existing bounded L5 composition;
  - regression coverage prevents Cartesian expansion or model-memory star×palace doctrine;
  - registry/schema/runtime/admission/index/materialization/bundle/current docs remain synchronized;
  - canonical generator outputs, formal PR CI, merge, exact-main CI/artifact and canonical read-back complete before `DONE`.
- closure:
  - implementation merged by PR #316 at `33c10c7f012633b278cc56d16da694379a032591`;
  - schema `0.5.0-research` preserves explicit `star_palace_context` / `star` / `palace` / `subjects[]` identity without rewriting historical registries;
  - production admission contains exactly 2 practitioner-bounded contextual claims: `天相×命宮` and `天梁×官祿宮`;
  - `天相×命宮` preserves a named conflict with existing historical favorable-support authority evidence rather than universalizing the practitioner `位高無權` heuristic;
  - `天梁×官祿宮` adds only a bounded career/public-role social / coordination-load modifier and does not guarantee public office;
  - reviewed `太陽×財帛宮` / `太陽×官祿宮` remain unadmitted as non-material restatements; `武曲×財帛宮`、`巨門×夫妻宮`、`天相×官祿宮` remain unadmitted because the bounded pass did not establish a clean isolated materially distinct rule;
  - exact applicability reuses canonical `fact_available:palace_occupancy` + `star_in_palace:<star>:<palace>` facts; no new geometry provider or 14×12 Cartesian dictionary was added;
  - contextual specificity is higher than generic star conditional/core and palace-domain claims only on exact admitted match; generic evidence remains bounded context and no-match behavior stays existing L5 composition;
  - base natal claim count is 61 = 52 first-layer + 2 sparse same-palace pair + 5 Body-Palace + 2 sparse star×palace claims; optional M0 + Sihua maximum is 68;
  - Scope-A pipeline advanced to `1.4.0`; natal provider remains `0.3.0`;
  - first generator bridge run `36325407203` proved all 5 new P2-020 tests PASS, then failed only on a test-file formatting SyntaxError caused by a literal `\n`; production source was unchanged;
  - bounded test-only formatting repair commit `e69ed220ba3b3125b3d8181d08ae902be7fb2d13`;
  - second generator bridge run `36325462973` PASSed focused P2-020 / production / Sihua / same-palace / Body-Palace / retrieval / unified-runtime / materialization regressions, Zi Wei bundle regeneration/check, ChatGPT load-pack regeneration/check, load-budget and bundle regression;
  - generator-owned cache commit `533d89ad8369117a43946c1c559337d666e979b3` removed the temporary bridge after canonical derived-cache regeneration;
  - formal PR #316 run `36325507624` PASSed `validate` + `casting-runtime`, including full unit suite and structural checker;
  - exact-main canonical read-back at `33c10c7f012633b278cc56d16da694379a032591` confirms 2-claim admission, exact pair identities, pipeline `1.4.0`, 61/68 claim counts and `cartesian_expansion=false`;
  - exact-main run `36325630892` PASSed `validate` + `casting-runtime`, full unit suite, structural checker and exact-main Zi Wei handoff preparation/upload;
  - exact-main artifact `10933523207` / `ziwei-deterministic-handoff-33c10c7f012633b278cc56d16da694379a032591` published at 94,180 bytes with digest `sha256:7553980c7903d7807ec6bb18296470008c5d8b456dbff281b57556b116c2e6b2`.
- production_boundary:
  - no exhaustive 14×12 Cartesian dictionary;
  - no star×palace doctrine inferred solely from independent star-core + palace-domain meanings;
  - no guaranteed office, wealth, marriage, illness or death outcome.

#### 2026-09-28 bounded extension — 貪狼×夫妻宮

- status: DONE
- shared_development_playbook_reviewed: `masini1491/ai-development-playbook@5713f23f1a306bed7b6346edaaa0226a248949dd`
- research_evidence: `STAR_PALACE_CONTEXTUAL_RESEARCH_V2.md` established `貪狼×夫妻宮` as a materially distinct historical bounded admission candidate; Nihai spouse-age heuristic remains practitioner-only / deferred.
- production_result:
  - added exactly one historical-bounded `貪狼×夫妻宮` claim to existing `sparse_star_palace_context_v1`;
  - exact applicability remains `fact_available:palace_occupancy` + `star_in_palace:貪狼:夫妻宮`;
  - base natal claims = 62; maximum optional claims = 79; star×palace claims = 3;
  - Scope-A pipeline remains `1.5.0`; no new runtime, geometry provider or claim type.
- production_boundary: no deterministic marriage failure, multiple-marriage, affair or fixed-spouse-characteristic prediction; Nihai spouse-age heuristic remains non-production; no Cartesian expansion.
- completion_evidence:
  - generator bridge run `36358158923` PASSed registry validation, focused admission regressions, canonical Zi Wei bundle regeneration/check, ChatGPT load-pack regeneration/check, load-budget check and bundle regression;
  - generator-owned cache commit `767cbbf33dccd4a1b4ab122f30735db616aff0ea` removed the temporary bridge after canonical cache regeneration;
  - formal PR #326 run `36358201777` PASSed `validate` + `casting-runtime`, including full unit suite and structural checker;
  - PR #326 merged to exact main `dfefcc8c49102f2cb2ca96fb221ea5f2aa8cce2f`;
  - exact-main canonical read-back confirms pairs `天相×命宮` / `天梁×官祿宮` / `貪狼×夫妻宮`, counts 62 / 79, pipeline `1.5.0`, declared shared baseline `main` and reviewed shared revision `5713f23f1a306bed7b6346edaaa0226a248949dd`;
  - exact-main run `36358309882` PASSed `validate` + `casting-runtime`, full unit suite, structural checker and exact-main Zi Wei handoff preparation/upload;
  - exact-main artifact `10945090252` / `ziwei-deterministic-handoff-dfefcc8c49102f2cb2ca96fb221ea5f2aa8cce2f` published at 98,677 bytes with digest `sha256:6dad5b327e92622790be8f971ce5da306f4b0bb2f6f70acd8d42c1bff922a2ae`.

### ZW-P2-021 — Sparse star×palace contextual research v3

- type: RESEARCH / INTERPRETATION
- status: DONE
- priority: P2
- owner: Zi Wei interpretation evidence
- blocked_by: none
- trigger:
  - explicit user request to continue the Zi Wei research line after v2 / production closure.
- research_scope:
  - targeted re-review `破軍×遷移宮`;
  - source-first discovery of additional star×palace candidates;
  - material-distinctness comparison against current star-core + palace-domain evidence;
  - research-only; no production admission in this action.
- evidence_decision:
  - `破軍×遷移宮` upgraded from v2 `DEFER-BORDERLINE` to `ADMISSION-CANDIDATE` after direct current-project Nanyang-Hall 遷移宮 evidence established baseline + dignity + malefic-condition semantics;
  - `破軍×夫妻宮` = `ADMISSION-CANDIDATE`, historical + practitioner corroborated, but requires strict relationship-safety normalization;
  - `武曲×田宅宮` = `ADMISSION-CANDIDATE`, historical + practitioner corroborated property acquisition / retention trajectory;
  - `天機×田宅宮` = `ADMISSION-CANDIDATE`, historically explicit directional property pattern;
  - `貪狼×遷移宮` = `DEFER-BORDERLINE`;
  - `紫微×遷移宮` = `REJECT-REDUNDANT`.
- canonical_research:
  - `references/ziwei/STAR_PALACE_CONTEXTUAL_RESEARCH_V3.md`
- production_boundary:
  - current production star×palace admission remains exactly 3 claims;
  - no claim registry / runtime / admission manifest / pipeline / count change;
  - no 14×12 Cartesian expansion;
  - no deterministic marriage, wealth, property, travel-accident or other guaranteed event prediction.
- recommended_next_admission_order:
  1. `破軍×遷移宮`
  2. `武曲×田宅宮`
  3. `天機×田宅宮`
  4. `破軍×夫妻宮`
- completion_evidence:
  - research implementation PR #328 run `36361592025` PASSed `validate` + `casting-runtime`, including full unit suite and structural checker;
  - PR #328 merged to exact main `fff3c5bd9a5724aa35e90890fb99ca0755fab558`;
  - exact-main canonical read-back confirms `STAR_PALACE_CONTEXTUAL_RESEARCH_V3.md` and this backlog item are present while production remains base 62 / maximum optional 79 / star×palace 3 / pipeline `1.5.0`;
  - exact-main run `36361727278` PASSed `validate` + `casting-runtime`, full unit suite, structural checker and exact-main Zi Wei handoff preparation/upload;
  - exact-main artifact `10946220860` / `ziwei-deterministic-handoff-fff3c5bd9a5724aa35e90890fb99ca0755fab558` published at 98,678 bytes with digest `sha256:77a6379187f6a23db5d169f6aea29acc0da2ba2c33672ba3e8cbdfe5df70cfd2`.
- next_authorized_action:
  - STOP — any production admission of the v3 candidates is a separate bounded action.

### ZW-P2-022 — Admit 破軍×遷移宮 sparse contextual claim

- type: FEATURE / INTERPRETATION / PRODUCTION ADMISSION
- status: DONE
- priority: P2
- owner: Zi Wei production maintenance
- blocked_by:
  - ZW-P2-021 — DONE
- shared_development_playbook_reviewed: `masini1491/ai-development-playbook@9236b42550b7f748cc6c5744075d106e643c6042`
- promotion_route:
  - production candidate used PR because current canonical `.github/workflows/validation.yml` provides candidate validation on `pull_request`; this was current evidence need, not historical PR convention;
  - this coordination-only closure uses direct non-force promotion because no independent review / PR-specific check is required, and main-push validation + canonical read-back provide the required closure evidence.
- evidence_decision:
  - `STAR_PALACE_CONTEXTUAL_RESEARCH_V3.md` upgrades `破軍×遷移宮` to `ADMISSION-CANDIDATE` using direct Nanyang-Hall 遷移宮 evidence with baseline + dignity + malefic-condition semantics.
- production_result:
  - added exactly one historical-bounded `破軍×遷移宮` claim to existing `sparse_star_palace_context_v1`;
  - exact applicability = `fact_available:palace_occupancy` + `star_in_palace:破軍:遷移宮`;
  - base natal claims = 63; maximum optional claims = 80; star×palace claims = 4;
  - Scope-A pipeline remains `1.5.0`; no new runtime, geometry provider or claim type;
  - stale `ZIWEI.md` activation-flow star×palace count was repaired from 2 to 4 while affected current-state owners were synchronized.
- production_boundary:
  - no "出外必凶" doctrine;
  - no deterministic travel failure, accident, injury or other guaranteed adverse-event prediction;
  - dignity / brightness remains a modifier only and does not authorize brightness-only doctrine;
  - no 14×12 Cartesian expansion.
- completion_evidence:
  - generator bridge run `36362822915` PASSed registry validation, focused admission regressions, canonical Zi Wei bundle regeneration/check, ChatGPT load-pack regeneration/check, load-budget check and bundle regression;
  - generator-owned cache commit `9ab80ccd776c7a50d3f7560b3876f8577c6b8b8b` removed the temporary bridge after regeneration;
  - formal PR #330 run `36362895240` PASSed `validate` + `casting-runtime`, including full unit suite and structural checker;
  - PR #330 merged to exact main `8f6031f83548ebca11396fa2144bae706909109b`;
  - exact-main canonical read-back confirms 4 pairs `天相×命宮` / `天梁×官祿宮` / `貪狼×夫妻宮` / `破軍×遷移宮`, counts 63 / 80, pipeline `1.5.0`, declared shared baseline `main`, and reviewed shared revision `9236b42550b7f748cc6c5744075d106e643c6042`;
  - exact-main run `36363026681` PASSed `validate` + `casting-runtime`, full unit suite, structural checker and exact-main Zi Wei handoff preparation/upload;
  - exact-main artifact `10946208245` / `ziwei-deterministic-handoff-8f6031f83548ebca11396fa2144bae706909109b` published at 99,154 bytes with digest `sha256:c267f152ead7c6b888deffbbf8e387c219e6b8f7267e05def615eb464b45b306`.
- next_authorized_action:
  - STOP — next research-approved production candidate is `武曲×田宅宮`; it requires a separate bounded production-admission action.


### ZW-P2-023 — Admit 武曲×田宅宮 sparse contextual claim

- type: FEATURE / INTERPRETATION / PRODUCTION ADMISSION
- status: DONE
- priority: P2
- owner: Zi Wei production maintenance
- blocked_by:
  - ZW-P2-021 — DONE
  - ZW-P2-022 — DONE
- shared_development_playbook_reviewed: `masini1491/ai-development-playbook@9236b42550b7f748cc6c5744075d106e643c6042`
- promotion_route:
  - production candidate used PR because current canonical `.github/workflows/validation.yml` provides candidate validation on `pull_request`; this was current evidence need, not historical PR convention;
  - this coordination-only closure uses direct non-force promotion because no independent review / PR-specific check is required, and main-push validation + canonical read-back provide the required closure evidence.
- evidence_decision:
  - `STAR_PALACE_CONTEXTUAL_RESEARCH_V3.md` marks `武曲×田宅宮` as `ADMISSION-CANDIDATE` with direct Nanyang-Hall 田宅宮 evidence and practitioner corroboration;
  - production semantics use the historical primary-text source identity; practitioner evidence remains corroborative.
- production_result:
  - added exactly one historical-bounded `武曲×田宅宮` claim to existing `sparse_star_palace_context_v1`;
  - exact applicability = `fact_available:palace_occupancy` + `star_in_palace:武曲:田宅宮`;
  - base natal claims = 64; maximum optional claims = 81; star×palace claims = 5;
  - Scope-A pipeline remains `1.5.0`; no new runtime, geometry provider or claim type.
- production_boundary:
  - no guaranteed inheritance, property purchase, property retention or fixed-wealth outcome;
  - dignity / brightness remains a modifier only and does not authorize brightness-only doctrine;
  - no 14×12 Cartesian expansion.
- completion_evidence:
  - generator bridge run `36364867700` PASSed registry validation, focused admission regressions, canonical Zi Wei bundle regeneration/check, ChatGPT load-pack regeneration/check, load-budget check and bundle regression;
  - generator-owned cache commit `49daf3b391c03b356c4759e21778b1cbf6b56d77` removed the temporary bridge after regeneration;
  - formal PR #331 run `36364912183` PASSed `validate` + `casting-runtime`, including full unit suite and structural checker;
  - PR #331 merged to exact main `a2d7c3ced79641234d6bbc9e557cf863456aee2b`;
  - exact-main canonical read-back confirms 5 pairs `天相×命宮` / `天梁×官祿宮` / `貪狼×夫妻宮` / `破軍×遷移宮` / `武曲×田宅宮`, counts 64 / 81, pipeline `1.5.0`;
  - exact-main run `36365057416` PASSed `validate` + `casting-runtime`, full unit suite, structural checker and exact-main Zi Wei handoff preparation/upload;
  - exact-main artifact `10947006911` / `ziwei-deterministic-handoff-a2d7c3ced79641234d6bbc9e557cf863456aee2b` published at 99,484 bytes with digest `sha256:e8cb7574e54d38733a8dc78213517142f38a55f021221b9502703e58380a4cb2`.
- next_authorized_action:
  - STOP — next research-approved production candidate is `天機×田宅宮`; it requires a separate bounded production-admission action.


### ZW-P2-024 — Admit 天機×田宅宮 sparse contextual claim

- type: FEATURE / INTERPRETATION / PRODUCTION ADMISSION
- status: DONE
- priority: P2
- owner: Zi Wei production maintenance
- blocked_by:
  - ZW-P2-021 — DONE
  - ZW-P2-023 — DONE
- shared_development_playbook_reviewed: `masini1491/ai-development-playbook@9236b42550b7f748cc6c5744075d106e643c6042`
- promotion_route:
  - production candidate used PR because current canonical `.github/workflows/validation.yml` provides candidate validation on `pull_request`; this was current evidence need, not historical PR convention;
  - this coordination-only closure uses direct non-force promotion because no independent review / PR-specific check is required, and main-push validation + canonical read-back provide the required closure evidence.
- evidence_decision:
  - `STAR_PALACE_CONTEXTUAL_RESEARCH_V3.md` marks `天機×田宅宮` as `ADMISSION-CANDIDATE` with direct Nanyang-Hall 田宅宮 evidence;
  - independent practitioner support was not required or established in v3; production semantics remain historical-primary-text bounded.
- production_result:
  - added exactly one historical-bounded `天機×田宅宮` claim to existing `sparse_star_palace_context_v1`;
  - exact applicability = `fact_available:palace_occupancy` + `star_in_palace:天機:田宅宮`;
  - base natal claims = 65; maximum optional claims = 82; star×palace claims = 6;
  - Scope-A pipeline remains `1.5.0`; no new runtime, geometry provider or claim type.
- production_boundary:
  - no guaranteed ancestral-property loss;
  - no guaranteed new-property acquisition or fixed property outcome;
  - dignity / brightness remains a modifier only and does not authorize brightness-only doctrine;
  - no 14×12 Cartesian expansion.
- completion_evidence:
  - generator bridge run `36366453109` PASSed registry validation, focused admission regressions, canonical Zi Wei bundle regeneration/check, ChatGPT load-pack regeneration/check, load-budget check and bundle regression;
  - generator-owned cache commit `6b57ddcd7532c29e1e3387b3b21baa042180277e` removed the temporary bridge after regeneration;
  - formal PR #332 run `36366513636` PASSed `validate` + `casting-runtime`, including full unit suite and structural checker;
  - PR #332 merged to exact main `42f64d19d2320c3e82a5da3b0e4997fb4a9d02bd`;
  - exact-main canonical read-back confirms 6 pairs `天相×命宮` / `天梁×官祿宮` / `貪狼×夫妻宮` / `破軍×遷移宮` / `武曲×田宅宮` / `天機×田宅宮`, counts 65 / 82, pipeline `1.5.0`;
  - exact-main run `36366655289` PASSed `validate` + `casting-runtime`, full unit suite, structural checker and exact-main Zi Wei handoff preparation/upload;
  - exact-main artifact `10946983921` / `ziwei-deterministic-handoff-42f64d19d2320c3e82a5da3b0e4997fb4a9d02bd` published at 99,779 bytes with digest `sha256:73282e396774d6e6924624115522e4602219e631202d91adc7c0c97cc8139245`.
- next_authorized_action:
  - STOP — next research-approved production candidate is `破軍×夫妻宮`; it requires a separate bounded production-admission action.


### ZW-P2-025 — Admit 破軍×夫妻宮 sparse contextual claim

- type: FEATURE / INTERPRETATION / PRODUCTION ADMISSION
- status: DONE
- priority: P2
- owner: Zi Wei production maintenance
- blocked_by:
  - ZW-P2-021 — DONE
  - ZW-P2-024 — DONE
- shared_development_playbook_reviewed: `masini1491/ai-development-playbook@9236b42550b7f748cc6c5744075d106e643c6042`
- promotion_route:
  - production candidate used PR because current canonical `.github/workflows/validation.yml` provides candidate validation on `pull_request`; this was current evidence need, not historical PR convention;
  - this coordination-only closure uses direct non-force promotion because no independent review / PR-specific check is required, and main-push validation + canonical read-back provide the required closure evidence.
- evidence_decision:
  - `STAR_PALACE_CONTEXTUAL_RESEARCH_V3.md` marks `破軍×夫妻宮` as `ADMISSION-CANDIDATE` with historical + practitioner corroboration and explicit relationship-safety hardening requirement;
  - production authority uses the historical primary-text source identity; practitioner evidence remains corroborative / conflict-detection evidence only.
- production_result:
  - added exactly one historical-bounded `破軍×夫妻宮` claim to existing `sparse_star_palace_context_v1`;
  - exact applicability = `fact_available:palace_occupancy` + `star_in_palace:破軍:夫妻宮`;
  - base natal claims = 66; maximum optional claims = 83; star×palace claims = 7;
  - Scope-A pipeline remains `1.5.0`; no new runtime, geometry provider or claim type.
- production_boundary:
  - no deterministic divorce, separation, spouse harm, fixed marriage count or other guaranteed relationship event;
  - practitioner categorical wording remains non-production;
  - dignity / brightness remains a modifier only and does not authorize brightness-only doctrine;
  - no 14×12 Cartesian expansion.
- completion_evidence:
  - generator bridge run `36378833597` PASSed registry validation, focused admission regressions, canonical Zi Wei bundle regeneration/check, ChatGPT load-pack regeneration/check, load-budget check and bundle regression;
  - generator-owned cache commit `43a58918fe9e4378374eaf81220671bc97b46199` removed the temporary bridge after regeneration;
  - formal PR #333 run `36378887523` PASSed `validate` + `casting-runtime`, including full unit suite and structural checker;
  - PR #333 merged to exact main `944fecf8e0837924db64b3408cfe5ce8caf5040d`;
  - exact-main canonical read-back confirms 7 pairs `天相×命宮` / `天梁×官祿宮` / `貪狼×夫妻宮` / `破軍×遷移宮` / `武曲×田宅宮` / `天機×田宅宮` / `破軍×夫妻宮`, counts 66 / 83, pipeline `1.5.0`;
  - exact-main run `36379027662` PASSed `validate` + `casting-runtime`, full unit suite, structural checker and exact-main Zi Wei handoff preparation/upload;
  - exact-main artifact `10951843929` / `ziwei-deterministic-handoff-944fecf8e0837924db64b3408cfe5ce8caf5040d` published at 100,115 bytes with digest `sha256:0533227732b6510acfa7cb48bb23e1c648e73d020759883fbd1662720fb197c8`.
- next_authorized_action:
  - STOP — all four v3 admission candidates are now production-admitted; further star×palace expansion requires a new research stage or separate explicitly authorized research action.


### ZW-P2-026 — Sparse star×palace contextual research v4

- type: RESEARCH / INTERPRETATION
- status: IN_PROGRESS
- priority: P2
- owner: Zi Wei interpretation evidence
- blocked_by:
  - ZW-P2-025 — DONE
  - ZW-P1-050 — DONE
- shared_development_playbook_reviewed: `masini1491/ai-development-playbook@9236b42550b7f748cc6c5744075d106e643c6042`
- trigger:
  - all four v3 admission candidates are production-admitted;
  - further sparse star×palace expansion requires a new source-first research stage rather than continuing the old candidate list.
- research_goal:
  - continue V4 source-first candidate discovery after the 168-cell coverage/routing architecture is admitted;
  - require material semantic distinctness beyond existing star-core + palace-domain L5 composition;
  - preserve historical / practitioner source roles and reject source-explicit but redundant pairs;
  - remain research-only until a later separate production-admission action is explicitly authorized.
- first_batch_priority:
  1. `天機×福德宮` — strongest preliminary candidate; test whether the historical "先勞後逸" directional pattern remains materially distinct after full source reconciliation and safe normalization;
  2. `紫微×奴僕宮` — candidate; test support-network effectiveness + favorable/adverse condition reversal while preserving historical 奴僕 scope versus modern 交友 expansion;
  3. `天同×財帛宮` — candidate with wealth-safety hardening; test whether historical self-made / later-forming resource trajectory adds material information without becoming guaranteed wealth prediction.
- control_and_defer_set:
  - `天機×財帛宮` — preliminary `BORDERLINE`; current evidence may remain representable as 天機 thought/planning + 財帛 resource-acquisition L5 composition;
  - `巨門×奴僕宮` — preliminary `BORDERLINE / LIKELY-REDUNDANT`; dispute / communication semantics may already be covered by 巨門 core + 奴僕 support-relationship domain;
  - `破軍×福德宮` — `DEFER`; current historical + practitioner material risks collapsing into generic 破軍 disruption + 福德 unrest, and practitioner marriage projection must not become production doctrine;
  - `太陽×父母宮` / `太陰×父母宮` / `天梁×父母宮` — `REJECT-REDUNDANT controls` unless new condition-specific evidence materially exceeds existing parent-symbol / parent-domain claims.
- health_domain_boundary:
  - source-explicit 疾厄宮 star×palace material exists but is excluded from this ordinary V4 batch;
  - any 疾厄宮 expansion requires a separate health-safe bounded research stage with explicit high-stakes health / injury / death safety gates;
  - no concrete disease, injury, mortality or diagnostic prediction may be admitted from this V4 item.
- production_boundary:
  - current production remains exactly 7 sparse star×palace claims;
  - no registry / admission manifest / runtime / pipeline / claim-count change in this research item;
  - no 14×12 dedicated-L4 Cartesian expansion; the architecture may enumerate all 168 identities as routing/coverage cells;
  - no guaranteed relationship, wealth, property, health, injury, death or other concrete event prediction.
- expected_outputs:
  - `references/ziwei/STAR_PALACE_CONTEXTUAL_RESEARCH_V4.md`;
  - update the canonical 168-cell coverage classification/routing state produced by ZW-P1-050;
  - bounded candidate / borderline / reject classifications with explicit source-role and material-distinctness rationale;
  - recommended later production-review order only for candidates that pass the V4 gate.
- batch_1_result:
  - research owner: `references/ziwei/STAR_PALACE_CONTEXTUAL_RESEARCH_V4.md`;
  - admission candidates / reviewed unresolved: `天機×福德宮`、`紫微×奴僕宮`、`天同×財帛宮`;
  - resolved bounded-L5 controls: `天機×財帛宮`、`巨門×奴僕宮`、`破軍×福德宮`、`太陽×父母宮`、`太陰×父母宮`、`天梁×父母宮`;
  - coverage delta = +9 reviewed / +6 resolved;
  - coverage state = reviewed 24 / resolved 17 / unreviewed 144 / dedicated L4 7 / bounded L5 10 / deferred 7;
  - production claim count/runtime/pipeline remain unchanged.
- batch_2_result:
  - full `福德宮` row is now 14/14 reviewed;
  - new admission candidates / reviewed unresolved: `紫微×福德宮`、`太陽×福德宮`、`武曲×福德宮`、`廉貞×福德宮`、`天府×福德宮`、`貪狼×福德宮`、`天相×福德宮`;
  - new resolved bounded-L5 cells: `天同×福德宮`、`太陰×福德宮`、`巨門×福德宮`、`天梁×福德宮`、`七殺×福德宮`;
  - coverage delta = +12 reviewed / +5 resolved;
  - coverage state = reviewed 36 / resolved 22 / unreviewed 132 / dedicated L4 7 / bounded L5 15 / deferred 14;
  - production claim count/runtime/pipeline remain unchanged.
- batch_3_result:
  - full `官祿宮` row is now 14/14 reviewed and 10/14 resolved;
  - new admission candidates / reviewed unresolved: `天機×官祿宮`、`廉貞×官祿宮`、`巨門×官祿宮`;
  - new resolved bounded-L5 cells: `武曲×官祿宮`、`天同×官祿宮`、`天府×官祿宮`、`太陰×官祿宮`、`貪狼×官祿宮`、`七殺×官祿宮`、`破軍×官祿宮`;
  - coverage delta = +10 reviewed / +7 resolved;
  - coverage state = reviewed 46 / resolved 29 / unreviewed 122 / dedicated L4 7 / bounded L5 22 / deferred 17;
  - production claim count/runtime/pipeline remain unchanged.
- batch_4_natal_priority_result:
  - requested priority set: `武曲×命宮`、`紫微×官祿宮`、`太陽×父母宮`、`天梁×父母宮`、`廉貞×財帛宮`、`天府×財帛宮`、`天同×兄弟宮`、`巨門×兄弟宮`、`太陰×子女宮`、`七殺×福德宮`;
  - previously reviewed controls remain resolved bounded-L5: `紫微×官祿宮`、`太陽×父母宮`、`天梁×父母宮`、`七殺×福德宮`;
  - new admission candidates / reviewed unresolved: `廉貞×財帛宮`、`武曲×命宮`;
  - new resolved bounded-L5 cells: `天府×財帛宮`、`天同×兄弟宮`、`巨門×兄弟宮`;
  - new high-risk bounded cell: `太陰×子女宮` — source-explicit child sex/count/health/outcome doctrine remains non-production;
  - coverage delta = +6 reviewed / +4 resolved;
  - coverage state = reviewed 52 / resolved 33 / unreviewed 116 / dedicated L4 7 / bounded L5 25 / high-risk 1 / deferred 19;
  - recommended separate production-admission order: `廉貞×財帛宮` then `武曲×命宮`;
  - production claim count/runtime/pipeline remain unchanged in this research batch.
- batch_5_result:
  - full `財帛宮` row is now 14/14 reviewed and 8/14 resolved;
  - new admission candidates / reviewed unresolved: `貪狼×財帛宮`、`巨門×財帛宮`、`天梁×財帛宮`、`破軍×財帛宮`;
  - new resolved bounded-L5 cells: `紫微×財帛宮`、`太陰×財帛宮`、`天相×財帛宮`、`七殺×財帛宮`;
  - coverage delta = +8 reviewed / +4 resolved;
  - coverage state = reviewed 60 / resolved 39 / unreviewed 108 / dedicated L4 9 / bounded L5 29 / high-risk 1 / deferred 21;
  - production claim count/runtime/pipeline remain unchanged.
- batch_6_result:
  - full `父母宮` row is now 14/14 reviewed and 14/14 resolved;
  - all 11 newly reviewed cells route `HIGH_RISK_BOUNDED` because their pair-specific historical distinctions are dominated by parental survival/loss, injury, estrangement, adoption/re-parenting or lineage outcomes;
  - coverage delta = +11 reviewed / +11 resolved;
  - coverage state = reviewed 71 / resolved 50 / unreviewed 97 / dedicated L4 9 / bounded L5 29 / high-risk 12 / deferred 21;
  - no new admission candidate; production claim count/runtime/pipeline remain unchanged.
- batch_7_result:
  - full `夫妻宮` row is now 14/14 reviewed and 14/14 resolved;
  - new resolved bounded-L5 cells: `紫微×夫妻宮`、`天同×夫妻宮`、`天府×夫妻宮`、`太陰×夫妻宮`、`天相×夫妻宮`、`天梁×夫妻宮`;
  - new high-risk bounded cells: `天機×夫妻宮`、`太陽×夫妻宮`、`武曲×夫妻宮`、`廉貞×夫妻宮`、`七殺×夫妻宮`;
  - coverage delta = +11 reviewed / +11 resolved;
  - coverage state = reviewed 82 / resolved 61 / unreviewed 86 / dedicated L4 9 / bounded L5 35 / high-risk 17 / deferred 21;
  - no new admission candidate; production claim count/runtime/pipeline remain unchanged.
- batch_8_result:
  - full `遷移宮` row is now 14/14 reviewed and 8/14 resolved;
  - new admission candidates / reviewed unresolved: `天機×遷移宮`、`太陽×遷移宮`、`武曲×遷移宮`、`廉貞×遷移宮`、`七殺×遷移宮`;
  - new resolved bounded-L5 cells: `天同×遷移宮`、`天府×遷移宮`、`太陰×遷移宮`、`巨門×遷移宮`、`天相×遷移宮`、`天梁×遷移宮`;
  - coverage delta = +11 reviewed / +6 resolved;
  - coverage state = reviewed 93 / resolved 67 / unreviewed 75 / dedicated L4 9 / bounded L5 41 / high-risk 17 / deferred 26;
  - production claim count/runtime/pipeline remain unchanged.
- batch_9_result:
  - full `田宅宮` row is now 14/14 reviewed and 8/14 resolved;
  - new admission candidates / reviewed unresolved: `紫微×田宅宮`、`太陽×田宅宮`、`天同×田宅宮`、`貪狼×田宅宮`、`破軍×田宅宮`;
  - new resolved bounded-L5 cells: `天府×田宅宮`、`太陰×田宅宮`、`巨門×田宅宮`、`天相×田宅宮`、`天梁×田宅宮`;
  - new high-risk bounded cell: `廉貞×田宅宮`;
  - new evidence-gap deferred cell: `七殺×田宅宮` — no clean standalone primary-text paragraph established;
  - coverage delta = +12 reviewed / +6 resolved;
  - coverage state = reviewed 105 / resolved 73 / unreviewed 63 / dedicated L4 9 / bounded L5 46 / high-risk 18 / deferred 32;
  - production claim count/runtime/pipeline remain unchanged.
- batch_10_result:
  - full `命宮` row is now 14/14 reviewed and 14/14 resolved;
  - all 12 newly reviewed cells route `BOUNDED_L5_COMPOSITION`; no new admission candidate;
  - `天相×命宮` and `武曲×命宮` remain the only dedicated 命宮 overrides and were not generalized;
  - coverage delta = +12 reviewed / +12 resolved;
  - coverage state = reviewed 117 / resolved 85 / unreviewed 51 / dedicated L4 9 / bounded L5 58 / high-risk 18 / deferred 32;
  - production claim count/runtime/pipeline remain unchanged.
- batch_11_result:
  - full `兄弟宮` row is now 14/14 reviewed and 14/14 resolved;
  - new resolved bounded-L5 cells: `紫微×兄弟宮`、`天機×兄弟宮`、`太陽×兄弟宮`、`武曲×兄弟宮`、`廉貞×兄弟宮`、`天府×兄弟宮`、`太陰×兄弟宮`、`天相×兄弟宮`;
  - new high-risk bounded cells: `貪狼×兄弟宮`、`天梁×兄弟宮`、`七殺×兄弟宮`、`破軍×兄弟宮`;
  - exact sibling count / half-sibling / loss / guaranteed estrangement doctrine remains non-production;
  - coverage delta = +12 reviewed / +12 resolved;
  - coverage state = reviewed 129 / resolved 97 / unreviewed 39 / dedicated L4 9 / bounded L5 66 / high-risk 22 / deferred 32;
  - no new admission candidate; production claim count/runtime/pipeline remain unchanged.
- batch_12_result:
  - full `奴僕宮` row is now 14/14 reviewed and 13/14 resolved;
  - all 12 newly reviewed cells route `BOUNDED_L5_COMPOSITION`;
  - historical 奴僕 scope is not silently expanded into modern 交友 / peers / partnerships;
  - `紫微×奴僕宮` remains the only unresolved cell in this row;
  - coverage delta = +12 reviewed / +12 resolved;
  - coverage state = reviewed 141 / resolved 109 / unreviewed 27 / dedicated L4 9 / bounded L5 78 / high-risk 22 / deferred 32;
  - no new admission candidate; production claim count/runtime/pipeline remain unchanged.
- next_batch:
  - continue with the remaining ordinary `子女宮` row;
  - keep all V4 admission candidates research-only until separate bounded production-admission authorization;
  - keep 疾厄宮 on its separate health-safe path.
- completion_gate:
  - current historical primary-text locators and pinned practitioner evidence reconciled;
  - admitted / rejected / deferred V1-V3 pairs excluded from duplicate rediscovery;
  - each proposed candidate compared against existing star-core + palace-domain claims;
  - high-risk domains separated before user-facing doctrine;
  - research owner + research README + backlog synchronized;
  - production admission remains a separate bounded action after research closure.

### ZW-P2-027 — Admit 廉貞×財帛宮 sparse contextual claim

- type: FEATURE / INTERPRETATION / PRODUCTION ADMISSION
- status: IN_PROGRESS
- priority: P2
- owner: Zi Wei production maintenance
- blocked_by:
  - ZW-P2-026 natal-priority research classification
- shared_development_playbook_reviewed: `masini1491/ai-development-playbook@9236b42550b7f748cc6c5744075d106e643c6042`
- evidence_decision:
  - `STAR_PALACE_CONTEXTUAL_RESEARCH_V4.md` marks `廉貞×財帛宮` as `ADMISSION-CANDIDATE`;
  - historical 財帛宮 evidence adds a materially distinct active-acquisition / initial-friction-to-later-improvement trajectory beyond generic 廉貞 core + 財帛 domain.
- intended_production_delta:
  - add exactly one historical-bounded `廉貞×財帛宮` claim to `sparse_star_palace_context_v1`;
  - exact applicability = `fact_available:palace_occupancy` + `star_in_palace:廉貞:財帛宮`;
  - base natal claims 66 → 67; maximum optional claims 83 → 84; star×palace claims 7 → 8;
  - coverage resolved 33 → 34; dedicated L4 7 → 8; deferred 19 → 18;
  - Scope-A pipeline remains `1.5.0`; no new runtime, geometry provider or claim type.
- production_boundary:
  - no guaranteed wealth, return, fixed income, business success or guaranteed loss;
  - dignity / brightness remains modifier-only;
  - no 14×12 Cartesian expansion;
  - no borrowing doctrine from any different star×palace occupancy.
- candidate_bridge:
  - canonical Zi Wei bundle regeneration completed through the temporary PR bridge; the bridge is absent from the final candidate tree before formal validation.
- completion_gate:
  - registry / module admission / root admission / coverage decision+index / docs / tests synchronized;
  - canonical generator refreshes derived Zi Wei bundle;
  - formal PR validation + merge + canonical read-back complete; exact-main validation/artifact recorded only when established.

### ZW-P2-028 — Admit 武曲×命宮 sparse contextual claim

- type: FEATURE / INTERPRETATION / PRODUCTION ADMISSION
- status: IN_PROGRESS
- priority: P2
- owner: Zi Wei production maintenance
- blocked_by:
  - ZW-P2-026 natal-priority research classification
  - ZW-P2-027 canonical production state
- shared_development_playbook_reviewed: `masini1491/ai-development-playbook@9236b42550b7f748cc6c5744075d106e643c6042`
- evidence_decision:
  - V4 marks `武曲×命宮` as an admission candidate;
  - production-level recheck found direct historical `武曲守命` evidence tying core-self manifestation to condition-sensitive supporting/malefic context;
  - production authority is historical-bounded and does not depend on body-shape or fixed-occupation practitioner heuristics.
- intended_production_delta:
  - add exactly one `武曲×命宮` historical-bounded contextual claim;
  - exact applicability = `fact_available:palace_occupancy` + `star_in_palace:武曲:命宮`;
  - base natal claims 67 → 68; maximum optional claims 84 → 85; star×palace claims 8 → 9;
  - coverage resolved 34 → 35; dedicated L4 8 → 9; deferred 18 → 17;
  - Scope-A pipeline remains `1.5.0`; no runtime or geometry widening.
- production_boundary:
  - no fixed occupation, wealth, body type, gender role, office rank or social status;
  - dignity/supporting-star language is modifier-only;
  - no doctrine borrowed from `武曲×田宅宮` or any other occupancy;
  - no 14×12 Cartesian expansion.
- completion_gate:
  - registry / module admission / root admission / coverage / docs / tests synchronized;
  - canonical generator refreshes the derived Zi Wei bundle;
  - formal PR validation + merge + canonical read-back complete; exact-main validation/artifact recorded only when established.

### ZW-P2-050 — Body-Palace overlay interpretation admission

- type: FEATURE / INTERPRETATION / NATAL OVERLAY
- status: DONE
- priority: P2
- owner: Zi Wei interpretation evidence
- blocked_by: none
- evidence_decision:
  - pinned practitioner corpus `Renhuai123/nihai-tianji-corpus@c90006168195c0650328b7199669eb6a2d0cac93` explicitly defines 身宮 as a postnatal / 後天 development overlay and provides bounded semantics for 身宮 overlaying `夫妻宮`、`財帛宮`、`官祿宮`、`遷移宮`;
  - this pass admits one methodology claim plus those four exact overlay claims only;
  - other Body-Palace contexts remain without new semantic doctrine rather than being filled from model memory.
- canonical_research:
  - `references/ziwei/INTERPRETATION_ARCHITECTURE_V0.md`
  - `references/ziwei/INTERPRETATION_RUNTIME_CONTRACTS_V0.md`
  - `references/ziwei/SOURCE_RECONCILIATION_V1.md`
  - `references/ziwei/CALCULATION_ENGINE_RESEARCH.md`
  - `references/ziwei/BODY_PALACE_OVERLAY_RESEARCH_V1.md`
  - `references/ziwei/ziwei_interpretation_claim_registry_body_palace_overlay_v1.json`
- implementation:
  - natal provider advances to `ziwei-scope-a-natal-python@0.3.0` and deterministically projects `body_palace.branch` onto the existing twelve-palace layout as `body_palace.overlay_palace`;
  - retrieval facts add `fact_available:body_palace_overlay` + one `body_palace_overlay:<existing palace>` token; no second geometry path or thirteenth palace is introduced;
  - claim schema `0.4.0-research` adds explicit `body_palace_overlay` / `overlay_palace` / `subjects[]` identity;
  - production registry adds exactly 5 claims: 1 methodology + 4 exact overlays;
  - `body_palace_overlay` specificity outranks generic star/palace claims only when the exact admitted overlay fact matches; base claims remain bounded context;
  - base natal claim count candidate becomes 59 = 52 first-layer + 2 sparse same-palace pair + 5 Body-Palace claims; optional M0 + Sihua maximum becomes 66;
  - Scope-A pipeline advances to `1.3.0`; downstream decadal parent identity tracks natal provider `0.3.0`.
- completion_gate:
  - source-explicit Body-Palace domain / methodology evidence;
  - exact overlay-to-existing-palace applicability;
  - any required machine fact / profile identity is explicit and regression-covered;
  - bounded synthesis with palace/star evidence preserves provenance and conflict identity;
  - interpretation admission is separate from already-admitted Body-Palace calculation;
  - registry/schema/provider/runtime/admission/index/materialization/bundle/current docs remain synchronized;
  - generator outputs, formal PR CI, merge, exact-main CI/artifact and canonical read-back complete before `DONE`.
- closure:
  - implementation merged by PR #314 at `b172a8deb1bbcdbf99319c57ecc788b015a9008e`;
  - natal provider advanced to `ziwei-scope-a-natal-python@0.3.0` and emits `body_palace.overlay_palace`, `fact_available:body_palace_overlay` and one exact `body_palace_overlay:<existing palace>` token while preserving `overlay_not_thirteenth_palace`;
  - claim schema `0.4.0-research` adds explicit `body_palace_overlay` / `overlay_palace` / `subjects[]` identity without rewriting historical registry versions;
  - production admission contains exactly 5 practitioner-bounded claims: 1 身宮 postnatal-development methodology claim + exact overlays for `夫妻宮`、`財帛宮`、`官祿宮`、`遷移宮`; all other Body-Palace contexts remain without new doctrine;
  - base natal claim count is 59 = 52 first-layer + 2 sparse same-palace pair + 5 Body-Palace claims; optional M0 + Sihua maximum is 66;
  - Scope-A pipeline advanced to `1.3.0`; downstream decadal parent contract tracks natal provider `0.3.0`;
  - generator bridge run `36321582292` PASSed focused Body-Palace/provider/production/Sihua/unified-runtime/decadal/materialization regressions, Zi Wei bundle regeneration/check, ChatGPT load-pack regeneration/check, load-budget and bundle regression;
  - generator-owned cache commit `49e4352326efc718ea465a21b9f24ba37bbc6994` removed the temporary bridge after canonical derived-cache regeneration;
  - formal PR #314 run `36321624618` PASSed `validate` + `casting-runtime`, including full unit suite and structural checker;
  - exact-main canonical read-back at `b172a8deb1bbcdbf99319c57ecc788b015a9008e` confirms provider `0.3.0`, pipeline `1.3.0`, 5-claim Body-Palace admission, four admitted overlay contexts, 59/66 claim counts and `thirteenth_palace=false`;
  - exact-main run `36321729365` PASSed `validate` + `casting-runtime`, full unit suite, structural checker and exact-main Zi Wei handoff preparation/upload;
  - exact-main artifact `10932523663` / `ziwei-deterministic-handoff-b172a8deb1bbcdbf99319c57ecc788b015a9008e` published at 92,752 bytes with digest `sha256:ea5ee1a3333acc9261a4c5315b8c0a4f56e50029043b1d5930be359e6aec737b`.
- production_boundary:
  - Body Palace remains an overlay, never a thirteenth ordinary palace;
  - calculation identity alone does not create user-facing doctrine;
  - no model-memory fallback when source-explicit semantic evidence is unavailable;
  - no deterministic marriage, employment, relocation or wealth outcome.

### ZW-P2-060 — Sparse same-palace major-star combination claims

- type: FEATURE / INTERPRETATION / SPARSE OVERRIDES
- status: DONE
- priority: P2
- owner: Zi Wei interpretation evidence
- blocked_by:
  - ZW-P1-025 — CLOSED
- evidence_decision:
  - pinned practitioner corpus `Renhuai123/nihai-tianji-corpus@c90006168195c0650328b7199669eb6a2d0cac93` supports exactly two bounded `武曲×天相` claims in the current pass: `兄弟宮` and `官祿宮`;
  - reviewed `廉貞×天府` and `天同×巨門` passages establish co-occupancy/case context but not isolated pair-specific semantics; `太陽×天梁` did not yield a source-explicit semantic rule in the bounded pass;
  - therefore missing candidates remain unadmitted rather than filled from model memory.
- canonical_research:
  - `references/ziwei/INTERPRETATION_ARCHITECTURE_V0.md`
  - `references/ziwei/INTERPRETATION_RUNTIME_CONTRACTS_V0.md`
  - `references/ziwei/SAME_PALACE_MAJOR_STAR_PAIR_RESEARCH_V1.md`
  - `references/ziwei/ziwei_interpretation_claim_registry_same_palace_pairs_v1.json`
- implementation:
  - schema `0.3.0-research` adds explicit `same_palace_pair` identity with `pair_members[]` / `subjects[]`;
  - exact applicability reuses `fact_available:palace_occupancy` + two canonical `star_in_palace:<star>:<same palace>` facts;
  - `tools/ziwei_claim_retrieval.py` gives pair claims higher specificity than generic star/palace claims and keeps generic claims as bounded context;
  - default natal runtime loads the separately admitted 2-claim pair registry; no new geometry provider or optional selector is introduced;
  - base natal claim count becomes 54 = 52 first-layer + 2 sparse pair claims; optional M0 + Sihua maximum becomes 61.
- completion_gate:
  - only source-explicit sparse pair claims are eligible;
  - exact same-palace pair applicability facts / provenance are machine-matchable and derive from the canonical occupancy facts admitted by `ZW-P1-025`;
  - tradition/profile/conflict identity is preserved;
  - pair-specific claims outrank generic composition only inside their admitted scope;
  - absence of a pair-specific claim continues to use existing bounded L5 composition;
  - regression coverage prevents Cartesian expansion or model-memory pair doctrine;
  - registry/schema/runtime/admission/index/materialization/bundle/current docs remain synchronized;
  - canonical generator outputs, formal PR CI, merge, exact-main CI/artifact and canonical read-back complete before `DONE`.
- closure:
  - implementation merged by PR #312 at `652775c4655cc4dd0cc5ffbec529c11a68f0bee8`;
  - schema `0.3.0-research` preserves explicit `same_palace_pair` / `pair_members[]` / `subjects[]` identity without rewriting historical v0.1/v0.2 registries;
  - production admission contains exactly 2 practitioner-bounded `武曲×天相` claims: `兄弟宮` and `官祿宮`; `廉貞×天府`、`天同×巨門`、`太陽×天梁` remain non-admitted because the bounded source pass did not establish isolated pair semantics;
  - exact applicability reuses canonical `fact_available:palace_occupancy` + two `star_in_palace:<star>:<same palace>` facts; no new geometry provider was added;
  - pair specificity is higher than generic star/palace claims only on an exact admitted match; generic claims remain bounded context and no-match behavior stays unchanged;
  - base natal claim count is 54 = 52 first-layer + 2 sparse pair claims; optional M0 + Sihua maximum is 61;
  - generator bridge run `36315270893` PASSed focused pair/provider/runtime regressions, canonical Zi Wei bundle regeneration/check, ChatGPT load-pack regeneration/check, load-budget and bundle regression; generator-owned cache commit `2cf963df59b50e8000aebc26cfd0bdd1b004b0e7` removed the temporary workflow;
  - first PR #312 run `36315314512` correctly FAILED one stale existing test expectation (`59` vs new `61`) while all P2-060 tests passed; bounded test-only repair commit `043fb6002bdd7e8a7d57d449577b67a342682f7c` updated the current contract assertion;
  - second formal PR #312 run `36315461096` PASSed `validate` + `casting-runtime`, including full unit suite and structural checker;
  - exact-main canonical read-back at `652775c4655cc4dd0cc5ffbec529c11a68f0bee8` confirms pair admission, two claim IDs, 54/61 claim counts and explicit non-admission of the other reviewed pairs;
  - exact-main run `36315575849` PASSed `validate` + `casting-runtime`, full unit suite, structural checker and exact-main Zi Wei handoff preparation/upload;
  - exact-main artifact `10930736486` / `ziwei-deterministic-handoff-652775c4655cc4dd0cc5ffbec529c11a68f0bee8` published at 90,932 bytes with digest `sha256:0866dc48255096d9c359520070029bb244240dc1ac5587115eec7ed8d61b3e3c`.
- production_boundary:
  - no exhaustive 14×14 Cartesian dictionary;
  - this item is distinct from `ZW-P2-020` star×palace contextual claims;
  - no pair-specific historical claim may be invented from two independently admitted star-core meanings.

### ZW-P2-030 — Non-Asia/Taipei civil-time input normalization

- type: FEATURE / INPUT
- status: DONE
- priority: P2
- owner: Zi Wei calendar/input
- blocked_by: none
- shared_prerequisite:
  - `ASTROLOGY_BACKLOG.md#AST-P1-190` is DONE;
  - shared adapter `civil-time-zoneinfo-v1@1.0.0` is production-admitted for Astrology consumption;
  - Zi Wei is production-admitted as a consumer of `civil-time-zoneinfo-v1@1.0.0`.
- shared_contract:
  - `CIVIL_TIME_NORMALIZATION.md`
  - contract coordination closed by `ASTROLOGY_BACKLOG.md#AST-SHARED-003`; Zi Wei does not duplicate its mutable status.
- current_state:
  - canonical calendar profile `ziwei.calendar.civil_v2` accepts explicit IANA civil time through the shared normalizer;
  - existing Gregorian interval dataset remains date-keyed and is reused from validated local Gregorian fields; no per-timezone lunar dataset is introduced.
- Zi_Wei_responsibility:
  - consume the shared validated local civil datetime + timezone provenance;
  - feed validated **local Gregorian** year/month/day/hour/minute/second into the admitted Gregorian→lunar layer;
  - keep resolved UTC instant as provenance/identity evidence rather than rebasing the lunar conversion to UTC calendar fields;
  - validate overseas calendar-data/runtime coverage and Zi Wei-specific parity separately;
  - preserve `next_day_at_23`, `split_after_day_15` and other Zi Wei policies as method-owned layers after civil-time validation.
- closure:
  - implementation merged by PR #305 at `e859a3539bd8988d892d2456e89d4d70304d4e98`;
  - `tools/ziwei_calendar_provider.py` consumes shared `civil-time-zoneinfo-v1@1.0.0` before Gregorian→lunar lookup;
  - `ziwei.calendar.civil_v2` accepts explicit IANA timezone identity and preserves validated local Gregorian calendar fields; resolved UTC is provenance-only and never rebases lunar conversion;
  - existing `data/calendar/ziwei_tw_interval/v1/**` dataset is reused without per-timezone duplication; `next_day_at_23` and `split_after_day_15` remain Zi Wei-owned policies;
  - regression coverage includes Tokyo local-date-vs-UTC-boundary preservation, Sydney explicit-IANA input, New York DST gap/fold fail-closed, invalid/fixed-offset timezone rejection, transport round-trip, Minguo timezone preservation, and existing Asia/Taipei parity;
  - successful bridge run `36304792495`: 28 focused Zi Wei regressions PASS, regenerated Zi Wei bundle PASS, post-regeneration bundle tests 5 PASS, ChatGPT load-pack PASS, `explicit_research_astrology` ratio `0.7994`, overall load budget PASS;
  - generated-cache bot commit `a3e7c581e8f9c960e9b5c0ad38901b9d6494df34` changed only the canonical Zi Wei bundle and temporary bridge removal;
  - formal PR run `36305049795`: `validate` PASS, `casting-runtime` PASS, full unit suite PASS, structural checker PASS;
  - exact-main canonical read-back confirms shared Zi Wei consumer admission, `ZIWEI_CALENDAR_ADMISSION_V1` v2.1, provider v2.1/profile `ziwei.calendar.civil_v2`, machine routing, Minguo compatibility and backlog candidate state at `e859a3539bd8988d892d2456e89d4d70304d4e98`;
  - exact-main run `36305181663`: `validate` PASS, `casting-runtime` PASS, full unit suite PASS, structural checker PASS, Astrology and Zi Wei exact-main handoff preparation/upload PASS;
  - Zi Wei exact-main artifact `10926499513` / `ziwei-deterministic-handoff-e859a3539bd8988d892d2456e89d4d70304d4e98` published at 84,700 bytes with digest `sha256:9c24b88760458f000bcf84215bfe48e378ba24dacd45a9490776f20b291260ad`;
  - Astrology exact-main artifact `10926932471` / `astrology-core-handoff-e859a3539bd8988d892d2456e89d4d70304d4e98` published at 177,049 bytes with digest `sha256:d40a39007601e3106917cda1397d8863e6d7b2aa9873c0dee19dcc7b58479813`;
  - automatic birthplace→timezone resolution remains outside Zi Wei admission; true-solar-time remains owned by `ZW-P2-040`.
- completion_gate:
  - shared normalizer consumption is explicit and regression-covered;
  - non-`Asia/Taipei` IANA timezone provenance is preserved;
  - DST-safe local civil-time validation is inherited from the shared contract;
  - overseas Gregorian→lunar production parity / dataset-runtime coverage is independently validated;
  - no silent birthplace→timezone guessing;
  - current `Asia/Taipei` behavior remains regression-equivalent.
- non_goals:
  - do not duplicate generic timezone/DST normalization;
  - do not silently replace civil time with true solar time;
  - `ZW-P2-040` remains the separate true-solar-time policy item.

### ZW-P2-040 — True-solar-time policy

- type: FEATURE / INPUT POLICY
- status: DONE
- priority: P2
- owner: Zi Wei calendar/profile research
- blocked_by: none
- admitted_profile:
  - profile: `ziwei.true_solar.noaa_fractional_year_v1`;
  - clock identity: local apparent solar time;
  - civil time remains the default;
  - activation requires explicit profile + explicit longitude;
  - shared `civil-time-zoneinfo-v1` validation runs first;
  - correction uses east-positive longitude + resolved civil UTC offset + NOAA fractional-year equation of time;
  - corrected local Gregorian fields feed the existing Gregorian→lunar dataset before `next_day_at_23` / `split_after_day_15`;
  - birthplace→longitude and birthplace→timezone remain unadmitted.
- canonical_research:
  - `references/ziwei/TRUE_SOLAR_TIME_POLICY_V1.md`;
  - `references/ziwei/SOURCE_REGISTRY.md`.
- implementation:
  - `tools/ziwei_true_solar_time.py`;
  - `ZIWEI_TRUE_SOLAR_TIME_ADMISSION_V1.json`;
  - `ZIWEI_CALENDAR_ADMISSION_V1.json` v2.2 / provider v2.2.0;
  - Gregorian / Minguo / natal + dynamic V2–V11 JSON transport preservation.
- rule:
  - separate from ordinary civil-time timezone expansion;
  - requires explicit profile/policy identity and evidence;
  - must not silently replace civil time.
- completion_gate:
  - explicit profile + longitude contract is fail-closed and regression-covered;
  - civil-time default remains regression-equivalent;
  - solar correction may cross Gregorian date/hour and that corrected local identity is what feeds Gregorian→lunar lookup;
  - resolved UTC remains civil provenance only;
  - no birthplace/coordinate guessing;
  - runtime/schema/admission/index/materialization/bundle surfaces stay synchronized;
  - generated Zi Wei bundle and load pack are regenerated only by canonical generators;
  - implementation merge + exact-main CI/artifact + canonical read-back complete before status becomes DONE.
- closure:
  - implementation merged by PR #310 at `eb52537c358d532eff2aeae2eb7712b36a18b2a7`;
  - civil time remains the default; true solar activates only with exact profile `ziwei.true_solar.noaa_fractional_year_v1` plus explicit longitude;
  - the profile computes local apparent solar time from east-positive longitude + the civil normalizer's resolved UTC offset + NOAA fractional-year equation of time, then feeds corrected local Gregorian fields into the existing Gregorian→lunar dataset before Zi Wei `next_day_at_23` / `split_after_day_15`;
  - automatic birthplace→longitude and birthplace→timezone resolution remain unadmitted; latitude is not required by this clock correction;
  - natal + V2–V11 Gregorian JSON transports accept only the paired profile/longitude extension; legacy civil requests retain their prior field contract and behavior;
  - explicit Minguo year notation preserves timezone, true-solar profile and longitude through CE conversion;
  - generator bridge run `36311904574`: Zi Wei bundle regeneration/check PASS, ChatGPT load-pack regeneration/check PASS, load-budget PASS and focused true-solar/calendar/runtime/Minguo/bundle regressions PASS; generated-cache bot commit `8f80ffb3a15b903b2debac33a416a3f8efc1eead` removed the temporary bridge after generator-owned cache updates;
  - PR #310 formal run `36311949652`: `validate` PASS and `casting-runtime` PASS; full unit suite and structural checker PASS;
  - exact-main canonical read-back at `eb52537c358d532eff2aeae2eb7712b36a18b2a7` confirms calendar admission v2.2/provider v2.2.0, optional true-solar admission, root owner and machine index synchronization;
  - exact-main run `36312043721`: `validate` PASS and `casting-runtime` PASS; full unit suite, structural checker and exact-main Zi Wei handoff preparation/upload PASS;
  - exact-main artifact `10928709886` / `ziwei-deterministic-handoff-eb52537c358d532eff2aeae2eb7712b36a18b2a7` published at 88,476 bytes with digest `sha256:b55ca0c986347feecadc07444b2bbe324ca67052fde3d0b87a5e2953f1d452c7`.

## SHARED / parallel

### ZW-SHARED-001 — Astrology × Zi Wei reconciliation contract

- type: SHARED / RECONCILIATION
- status: DONE
- priority: SHARED
- owner: cross-validation / reconciliation
- blocked_by: none
- closure:
  - canonical contract: `CROSS_VALIDATION.md` §7;
  - admitted pair is bounded to `Astrology natal × Zi Wei natal_baseline`;
  - reconciliation states: `AGREEMENT / COMPLEMENT / TENSION / UNRESOLVED / NOT_COMPARABLE`;
  - method-specific evidence lineage is preserved; no house↔palace / planet↔star one-to-one mapping is implied;
  - Astrology transit × Zi Wei natal remains outside formal cross-validation;
  - no voting, score averaging, objective-probability promotion or forced convergence;
  - routing / bootstrap / machine index synchronized;
  - behavioral regression: `TAROT-BEH-026`.
- astrology_backlog: pointer-only at `AST-SHARED-002`; mutable shared status remains owned here.

## Intentionally not backlog blockers

The following are current policy choices or already-closed capabilities and must not be repeatedly rediscovered as blockers:

- Scope-A natal provider — production admitted;
- Gregorian→lunar via `ziwei.calendar.civil_v2` + explicit IANA civil time — production admitted;
- optional brightness profile `ziwei.brightness.iztro_v1` — production admitted when explicitly requested;
- ChatGPT deterministic materialization transport — production available;
- explicit Zi Wei routing — admitted;
- ordinary unspecified-user auto-routing — intentionally disabled, not an open defect;
- project-wide universal brightness default — not required while brightness remains explicit/profile-bound;
- full 14×12 star×palace dictionary — intentionally rejected;
- exhaustive 14×14 same-palace major-star pair dictionary — intentionally rejected; only sparse source-explicit pair overrides may be considered under `ZW-P2-060`;
- Five-Element Bureau user-facing semantics — current Scope-A treats 五行局 as a deterministic chart-construction / placement fact, not an independent interpretation factor; calculation identity must not be promoted into 金四局／木三局／水二局／土五局／火六局 personality or fate doctrine without a separate future evidence/admission decision;
- scientific/objective predictive-validity claim — not a project goal.

## Update rule

When a backlog item changes:

1. resolve current repository `main`;
2. update only the affected item;
3. link the canonical owner/admission/evidence that proves the new state;
4. mark `DONE` only after merge + canonical read-back + required CI/workflow evidence;
5. do not use this backlog as authority to bypass a production/research admission gate;
6. do not silently add new work because an implementation happens to expose extra capability.

