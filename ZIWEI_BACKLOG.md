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
6240c8596447e7befeb5c63ea0e4eb8307b4df61
```

This SHA is review evidence only, not a pin. Every maintenance task must resolve current `main` again before mutation.

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
- status: IN_PROGRESS
- priority: P1
- owner: Zi Wei Four-Transformation admission
- blocked_by:
  - ZW-P1-010
- canonical_research:
  - `references/ziwei/FOUR_TRANSFORMATION_VARIANT_REGISTRY.md`
  - `references/ziwei/FOUR_TRANSFORMATION_INTERPRETATION_RESEARCH_V0.md`
- current_state:
  - `sihua.default_v1` exists as a project research/default-candidate identity;
  - deterministic calculation candidate now exists at `tools/ziwei_sihua_provider.py` with explicit `sihua_profile_id`, profile revision, pinned complete 10-stem base-table provenance and one explicit project override (庚科：太陰 → 天府);
  - the candidate is intentionally NOT production-admitted and is not wired into `tools/ziwei_runtime.py`;
  - production transformed-star interpretation claims are still absent.
- completion_gate:
  - deterministic provider with explicit `sihua_profile_id`;
  - no cross-profile averaging;
  - profile selector / provenance;
  - fixtures and admission manifest;
  - source-explicit transformed-star claims only;
  - generic 祿／權／科／忌 outcome guarantees remain forbidden.

## P1/P2 — temporal / dynamic

### ZW-P1-030 — Dynamic calculation runtime

- type: FEATURE / CALCULATION
- status: OPEN
- priority: P1/P2
- owner: Zi Wei temporal runtime
- blocked_by:
  - ZW-P1-020
- sequence:
  1. decadal / 大限
  2. yearly / 流年
  3. monthly / 流月
  4. daily / 流日
  5. hourly / 流時
- canonical_research:
  - `references/ziwei/TEMPORAL_CONTEXT_INTERPRETATION_RESEARCH_V0.md`
  - `references/ziwei/CALCULATION_ENGINE_RESEARCH.md`
- completion_gate:
  - exact temporal scope and target identity;
  - parent-scope linkage;
  - boundary/profile identity;
  - relevant sihua/auxiliary profile identity where applicable;
  - engine/revision provenance;
  - no natal fallback when requested dynamic layer is unavailable.

### ZW-P1-040 — Dynamic interpretation claim corpus

- type: FEATURE / INTERPRETATION
- status: BLOCKED
- priority: P1/P2
- owner: Zi Wei temporal interpretation
- blocked_by:
  - ZW-P1-030
- rule:
  - natal 52 claims must not be silently reused as flow prediction claims.
- completion_gate:
  - scope-normalized claim schema/corpus;
  - temporal applicability and provenance;
  - conflict/safety handling;
  - admission separate from dynamic calculation availability.

## P2 — later expansion

### ZW-P2-010 — M1 high-impact auxiliary stars

- type: FEATURE / ADMISSION
- status: DEFERRED
- priority: P2
- owner: Zi Wei auxiliary-star research/admission
- blocked_by:
  - ZW-P1-010
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
- completion_gate:
  - source identity;
  - calculation/profile closure;
  - bounded interpretation claims;
  - explicit natal vs temporal identity.

### ZW-P2-020 — Sparse star×palace contextual claims

- type: FEATURE / INTERPRETATION
- status: DEFERRED
- priority: P2
- owner: Zi Wei interpretation evidence
- blocked_by: none
- rule:
  - no exhaustive 14×12 Cartesian dictionary;
  - only sparse source-explicit overrides where evidence justifies them.

### ZW-P2-030 — Non-Asia/Taipei civil-time input normalization

- type: FEATURE / INPUT
- status: DEFERRED
- priority: P2
- owner: Zi Wei calendar/input
- blocked_by: none
- current_state:
  - production calendar adapter supports `Asia/Taipei` civil time only.
- completion_gate:
  - explicit IANA timezone provenance;
  - DST-safe Gregorian→lunar normalization policy;
  - no silent birthplace→timezone guessing.

### ZW-P2-040 — True-solar-time policy

- type: FEATURE / INPUT POLICY
- status: DEFERRED
- priority: P2
- owner: Zi Wei calendar/profile research
- blocked_by:
  - ZW-P2-030
- rule:
  - separate from ordinary civil-time timezone expansion;
  - requires explicit profile/policy identity and evidence;
  - must not silently replace civil time.

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
- Gregorian→lunar for `Asia/Taipei` — production admitted;
- optional brightness profile `ziwei.brightness.iztro_v1` — production admitted when explicitly requested;
- ChatGPT deterministic materialization transport — production available;
- explicit Zi Wei routing — admitted;
- ordinary unspecified-user auto-routing — intentionally disabled, not an open defect;
- project-wide universal brightness default — not required while brightness remains explicit/profile-bound;
- full 14×12 star×palace dictionary — intentionally rejected;
- scientific/objective predictive-validity claim — not a project goal.

## Update rule

When a backlog item changes:

1. resolve current repository `main`;
2. update only the affected item;
3. link the canonical owner/admission/evidence that proves the new state;
4. mark `DONE` only after merge + canonical read-back + required CI/workflow evidence;
5. do not use this backlog as authority to bypass a production/research admission gate;
6. do not silently add new work because an implementation happens to expose extra capability.

