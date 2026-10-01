# Astrology Backlog

Authority: **COORDINATION-ONLY / NOT PRODUCTION AUTHORITY / NOT RESEARCH EVIDENCE / NOT ROUTING AUTHORITY**

Purpose: preserve the current Astrology maintenance, research and expansion queue so fresh ChatGPT sessions do not have to reconstruct open work from historical E0-E8 research, recent PR history or conversation handoffs. This file records work status only. Canonical technical truth remains in `ASTROLOGY.md`, mode owners, admission manifests, production tools, materialization contracts and `references/astrology/**`.

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
P1 = near-term research, architecture or feature admission
P2 = later expansion
SHARED = cross-method / cross-runtime work not owned only by Astrology
```

## Current baseline

Last reviewed against:

```text
ai-divination-playbook main
eabd5bdf22a4cd74b2f2e6591b9cf1424ca9ccb7
Merge pull request #381 from masini1491/fix/astrology-pyswisseph-backend-semantics
```

This SHA is review evidence only, not a pin. Every maintenance or implementation task must resolve current `main` again before mutation.

## Recommended execution order

Active near-term Astrology repository-architecture work:

1. **AST-P1-260 — Astrology root-surface / domain-path normalization**

Standing guard:

- **AST-P0-002** remains OPEN and is enforced alongside affected interpretation changes.

No active one-shot Astrology P2 provider task remains after AST-P2-030 closure.

Closed anti-rediscovery boundary:

- **AST-P2-030** — ChatGPT exact/approximate known-time natal may use only host-preinstalled `swisseph`; non-ChatGPT, unknown-time, transit, runtime-probe failure, or any route requiring install/vendor falls back to Astronomy Engine. Repo never installs or distributes Swiss.
- **PySwissEph/API vs effective backend semantics** — CLOSED: provider identity does not imply SWIEPH data; retflag-derived `SWIEPH_ONLY` / `MOSEPH_ONLY` / `MIXED_SWIEPH_MOSEPH` provenance is authoritative, and only `SWIEPH_ONLY` may be described as Swiss Ephemeris data.
- **Place-resolver materialization ownership** — CLOSED: named-place/country recovery is provider-independent and owned by `ASTROLOGY_PLACE_RESOLVER_MATERIALIZATION.md`; Swiss PASS never authorizes generic-web coordinate substitution.

Deferred / trigger-based work:

- **AST-P2-020** — Named consumer compatibility profile.

The active P1 sequence does **not** create a Cartesian-completion target for every Planet×Sign or Planet-Pair×Aspect combination.

## Backlog retention rule

This file is an active / deferred coordination surface, not a completed-work archive.

- `OPEN`, `IN_PROGRESS`, current critical-path `BLOCKED`, standing guards and `DEFERRED` trigger-based work may keep their minimum-sufficient task contracts here.
- `DONE` task bodies are removed after canonical closure; detailed execution history remains in Git history and canonical owners/evidence.
- A completed item stays here only as a compact anti-rediscovery pointer when forgetting it would materially cause the work to be reopened or a deliberate boundary to be lost.
- Do not create a parallel backlog-history document merely to preserve removed closure prose.

## P0 — correctness and reconciliation

### AST-P0-002 — Keep current-stack closure and projection routing synchronized

- type: MAINTENANCE / REGRESSION
- status: OPEN
- priority: P0
- owner: Astrology natal production maintenance
- blocked_by: none
- canonical_evidence:
  - `ASTROLOGY_NATAL.md`
  - `ASTROLOGY_PRODUCTION_ADMISSION_V1.json`
  - `references/astrology/extended_chart_e8_admission_readiness.json`
  - `tools/astrology_rulership_projection.py`
  - `tools/astrology_pattern_topology.py`
- problem:
  - E5/E6/E7 are now production-admitted under explicit named policies;
  - future research/admission work can easily make E8 metadata or Natal mode routing stale again.
- completion_gate:
  - any future E5/E6/E7 scope change updates the owning manifest/runtime/mode owner and E8 reconciliation in the same bounded change;
  - no second implicit default for rulership, participant, orb or topology policy;
  - no regression reopens already-closed current-stack gaps.

This item is a standing reconciliation guard. It is not a request to change current behavior immediately.

## P1 — repository information architecture

### AST-P1-260 — Astrology root-surface / domain-path normalization

- type: REPOSITORY ARCHITECTURE / AI RETRIEVAL / PATH MIGRATION
- status: OPEN
- priority: P1
- owner: Astrology repository-architecture maintenance
- blocked_by: none
- shared_precondition:
  - before any path move, close one minimum shared topology contract in `REPOSITORY_ARCHITECTURE.md` for root-retention rules, domain-scoped admission paths and routing/index update responsibility;
  - do **not** duplicate that shared mutable contract in both Astrology and Zi Wei backlogs.
- current_state:
  - Astrology already has domain-scoped `tools/astrology_*`, `schemas/astrology/**`, `runtime/astrology/**`, `data/astrology/**`, `references/astrology/**` and `reports/astrology/**`;
  - root still carries a large Astrology-specific surface, especially admission manifests, provider/materialization support contracts and the provider requirements file;
  - ordinary production routing is currently protected by `CHAT_INIT.md`, `CHATGPT_LOAD_PACK.json` and `PLAYBOOK_INDEX.json`, so this task is a discovery/search-noise and maintenance-cost reduction, not a claim that every reading currently loads all root files.
- scope:
  - keep `ASTROLOGY.md` as the root method entry owner unless measured retrieval evidence proves a better route;
  - keep `ASTROLOGY_BACKLOG.md` at its current allowlisted coordination path unless shared governance is explicitly changed;
  - evaluate and migrate Astrology-specific admission manifests into one domain-scoped admission namespace under the shared topology contract;
  - evaluate moving subordinate Astrology support documents such as materialization / place-deployment contracts only when they have independent retrieval intent and the move lowers net retrieval/search cost;
  - move `requirements-astrology-provider.txt` out of root if the shared dependency-path convention admits a dedicated requirements surface;
  - update every exact path pointer in `PLAYBOOK_INDEX.json`, method owners, tests, generators, workflows and validation surfaces in the same bounded migration;
  - preserve production semantics, provider identity, admission scope, deterministic bundle authority and provenance exactly; this is not an Astrology feature expansion.
- exclusions:
  - no semantic rewrite of Natal / Transit;
  - no provider-policy redesign;
  - no SWIEPH/MOSEPH routing change;
  - no bulk relocation of already well-scoped `tools/**`, `data/**`, `runtime/**`, `references/**` or `schemas/**`;
  - no directory-depth increase unless it yields concrete retrieval, scope-isolation or search-noise benefit.
- sequencing:
  - **shared phase A first:** establish only the minimum common path/topology contract required to prevent Astrology and Zi Wei from choosing incompatible layouts;
  - **method phase next:** perform this Astrology migration independently with exact-path reconciliation and method-specific validation;
  - **shared phase B last:** after Astrology and Zi Wei method migrations, reconcile thin global routing/index, root historical cleanup and cross-method load-budget effects from the actual resulting paths.
- completion_gate:
  - Astrology-specific root clutter is materially reduced without increasing ordinary Astrology routing hops;
  - all moved paths have one current canonical pointer and no stale current-authority aliases;
  - `PLAYBOOK_INDEX.json`, loader/bounded-range metadata and any generated routing metadata are synchronized only where materially affected;
  - Astrology production/materialization regressions and structural checks pass;
  - current ChatGPT load-budget profiles do not regress merely because files were reorganized;
  - canonical read-back confirms the new paths and the old root paths are absent or explicitly retained by contract.

## P2 — deferred compatibility / provider expansion

### AST-P2-020 — Named consumer compatibility profile

- type: PRODUCT POLICY / COMPATIBILITY
- status: DEFERRED
- priority: P2
- owner: Astrology product policy
- blocked_by:
  - relevant component policies must be evidence-backed first
- current_state:
  - D2 uses `EXPLICIT_SELECTOR_ONLY`;
  - no universal compatibility profile is admitted.
- rule:
  - profiles may compose named policies but must not hide their identities;
  - exact 唐綺陽 compatibility remains forbidden until independently established.


## SHARED / pointer-only coordination

### AST-SHARED-002 — Astrology × Zi Wei reconciliation pointer

- type: SHARED POINTER ONLY
- canonical coordination owner: `ZIWEI_BACKLOG.md#ZW-SHARED-001`
- canonical technical contract: `CROSS_VALIDATION.md` §7
- mutable status is **not** tracked here; follow the Zi Wei backlog owner to avoid divergent shared state.

## Completed anti-rediscovery index

The items below are **DONE**. They are retained only as compact identity pointers; do not reopen them unless a new regression, explicit scope expansion, or canonical-owner change creates a new judgment node.

- **AST-P0-001 — Reconcile E8 extended-object readiness after ChatGPT-only feasibility research** — DONE.
- **AST-P1-005 — Query-bounded place-resolver shard transport admission** — DONE.
  - anti-rediscovery contract: generated same-repo shards remain under `data/astrology/place/v1/**`; retrieval uses same-commit GitHub Connect bounded shard retrieval.
- **AST-P1-010 — EXP-1 five-body compact ephemeris feasibility** — DONE.
- **AST-P1-020 — EXP-2 Mean Black Moon Lilith local analytical parity** — DONE.
- **AST-P1-030 — EXP-3 Osculating / True Lilith local state-vector parity** — DONE.
- **AST-P1-040 — EXP-4 Vertex / Equatorial Ascendant formula admission study** — DONE.
- **AST-P1-100 — Source-backed South Node / Part of Fortune interpretation admission** — DONE.
- **AST-P1-110 — Extended aspect participant policies** — DONE.
- **AST-P1-120 — Yod / Stellium / Grand Quintile policy expansion** — DONE.
- **AST-P1-130 — Transit house search / temporal house context** — DONE.
- **AST-P1-140 — Point-in-time transit house context** — DONE.
- **AST-P1-150 — Runtime reuse / host integration binding** — DONE.
- **AST-P1-160 — Taiwan administrative locality input normalization** — DONE.
- **AST-P1-170 — North Node sign semantic claim-family admission** — DONE.
- **AST-P1-180 — Exact-main connector-backed core handoff artifact publishing** — DONE.
- **AST-P1-190 — Shared civil-time normalizer extraction/admission** — DONE.
- **AST-P1-200 — Default house-system interaction profile** — DONE.
- **AST-P1-210 — Natal semantic composition fallback contract** — DONE; canonical precedence is exact admitted claim → admitted bounded composition → `unsupported_factor`; typed `aspect_pair` supports admitted exact natal-aspect claims, while general natal-aspect semantic composition remains closed until its primitives are separately admitted.
- **AST-P1-220 — Disclosed default semantic profile for ordinary natal interpretation** — DONE; omitted/null natal `semantic_profile` normalizes to `composable-symbolic-modern-v1` with `project_default` provenance and disclosure; explicit admitted choice remains `explicit_user_choice`; registry/selector silent defaults remain forbidden and unadmitted profiles fail closed.
- **AST-P1-230 — Evidence-bounded concrete natal synthesis contract** — DONE; broad natal may explicitly use `evidence-bounded-concrete-natal-v1`: 3–5 traceable themes, admitted natal fact + semantic claim refs, independently cited material tensions, unsupported suppression, no semantic/claim-admission authority; detailed rules are conditionally loaded from `ASTROLOGY_NATAL_SYNTHESIS.md`.
- **AST-P1-240 — Sparse emergent exact-claim admission policy** — DONE; `references/astrology/EXACT_CLAIM_ADMISSION_POLICY_V1.*` formalizes `composition_adequate / research_candidate / exact_claim_admitted / unsupported`, rejects Cartesian or feedback-driven expansion, and requires explicit production admission after bounded research.
- **AST-P1-250 — Post-Reading Natal Gap Escalation Gate** — DONE; `ASTROLOGY_NATAL_SYNTHESIS.md` now gates concrete passage-level `too_generic / repetitive / tension_not_integrated / unsupported_leakage` findings: reproducible output gaps may create bounded synthesis/guard fixes, semantic-resolution gaps must pass AST-P1-240, vague accuracy feedback creates no Repo work, and public persistence is synthetic/abstract only.
- **AST-P2-010 — Interpolated Black Moon Lilith** — DONE.
- **AST-P2-041 — Piecewise Chebyshev five-body ephemeris feasibility** — DONE.
- **AST-P2-042 — Continuity-constrained / overlap Chebyshev five-body feasibility** — DONE.
- **AST-P2-040 — Broader extended ephemeris objects** — DONE.
- **AST-SHARED-001 — Casting/Vercel deployment isolation completion** — DONE.
- **AST-SHARED-003 — Shared civil-time normalization contract** — DONE.

Detailed PR / workflow / artifact / candidate-commit history is intentionally omitted from this active coordination surface and remains recoverable from Git history plus the canonical owners/evidence referenced by those revisions.

## Intentionally not backlog blockers

The following are already-closed capabilities or deliberate product boundaries and must not be repeatedly rediscovered as blockers:

- Astrology root production method owner and explicit-request routing — admitted;
- Natal and Transit mode owners — admitted;
- Astronomy Engine natal provider — admitted;
- bounded transit provider/search ≤400 days — admitted;
- unknown-time invariant natal facts — admitted;
- deterministic core ChatGPT materialization — product PASS;
- place resolver query-bounded shard materialization — admitted for default profile 500 under `ASTROLOGY_PLACE_RESOLVER_ADMISSION_V1.json`; whole-package/model-mediated transport remains rejected, and explicit coordinates + IANA timezone remain the fallback when the admitted resolver/materialization path cannot satisfy the request;
- Mean South Node / Descendant / IC / Part of Fortune deterministic facts — admitted;
- bounded Descendant / IC interpretation claims — admitted;
- traditional + modern rulership projections — admitted under explicit selectors;
- current-core aspect participant / major-aspect / orb identities — admitted;
- current major-aspect pattern topology — admitted;
- ordinary unspecified-user auto-routing to Astrology — intentionally disabled;
- exact 唐綺陽 compatibility — not claimed;
- scientific/objective predictive-validity claim — not a project goal.

## Fresh-session continuation order

Unless the user explicitly asks for a different bounded task, a fresh Astrology development/research chat should:

```text
1. resolve current main
2. read ASTROLOGY_BACKLOG.md
3. reconcile any changed item status against canonical owners
4. enforce AST-P0-002 alongside any affected interpretation change
5. no one-shot P1 item is currently active; do not invent evaluation-harness or matrix-completion work
6. keep AST-P2-020 deferred unless its explicit trigger appears; AST-P2-030 is closed and must not be reopened unless a new regression or explicit scope expansion appears
7. concrete post-reading broad-natal gaps follow `ASTROLOGY_NATAL_SYNTHESIS.md` §4.1; semantic-resolution gaps then pass `references/astrology/EXACT_CLAIM_ADMISSION_POLICY_V1.md` before exact-claim research
```

Do not infer from this ordering that every item is automatically authorized for production mutation. Research, calculation admission, semantic admission, UX defaulting and routing remain separate gates.

## Update rule

When a backlog item changes:

1. resolve current repository `main`;
2. update only the affected item;
3. link the canonical owner/admission/evidence that proves the new state;
4. mark `DONE` only after merge + canonical read-back + required CI/workflow evidence;
5. do not use this backlog as authority to bypass a production/research admission gate;
6. do not silently add new work because an implementation happens to expose extra capability;
7. if another backlog owns a shared item, link it rather than creating divergent technical authority.
8. generated loader ranges/index metadata remain derived discoverability hints, never backlog authority.
