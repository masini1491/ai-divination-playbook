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
d8aca589e4d32fb13358129530be38dc006ac6d4
Add evidence-bounded concrete natal synthesis (#359)
```

This SHA is review evidence only, not a pin. Every maintenance or implementation task must resolve current `main` again before mutation.

## Recommended execution order

Active near-term Astrology work:

1. **AST-P1-240 — Sparse emergent exact-claim admission policy**

Standing guard:

- **AST-P0-002** remains OPEN and is enforced alongside affected interpretation changes.

Deferred / trigger-based work:

- **AST-P2-020** — Named consumer compatibility profile.
- **AST-P2-030** — Optional Swiss compatibility/provider lane.

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

## P1 — active natal interpretation work

### AST-P1-240 — Sparse emergent exact-claim admission policy

- type: RESEARCH POLICY / INTERPRETATION / CLAIM ADMISSION
- status: OPEN
- priority: P1
- owner: Astrology semantic research coordination
- blocked_by: none
- prerequisite:
  - AST-P1-210 — DONE.
- target:
  - establish when an exact Planet×Sign or Planet-Pair×Aspect claim is worth separate research/admission because admitted lower-level composition leaves a **material semantic delta**;
  - valid triggers may include a demonstrable production coverage gap, recurrent over-generic composition, materially distinct source-backed semantics, or a case where lower-level primitives cannot safely express the scoped meaning;
  - each exact claim still requires source/profile/context/applicability admission and must preserve the lower-level evidence lineage it refines;
  - discovery of one gap may create one bounded research candidate, but does not automatically create a permanent ranking/queue or neighboring matrix work.
- completion_gate:
  - publish explicit candidate/admission criteria and anti-duplication rules;
  - distinguish `composition adequate`, `research candidate`, `exact claim admitted` and `unsupported` states;
  - add at least representative regression/fixture coverage proving that an exact claim enriches rather than duplicates or overrides valid lower-level semantics;
  - keep research admission separate from production mutation and routing.
- non_goals:
  - no 120-cell Planet×Sign completion target;
  - no full planet-pair × major-aspect Cartesian completion target;
  - no automatic claim generation from model synthesis;
  - no feedback-driven semantic promotion merely because an interpretation is popular or subjectively resonant.

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

### AST-P2-030 — Optional Swiss compatibility/provider lane

- type: PROVIDER / LICENSE
- status: DEFERRED
- priority: P2
- owner: Astrology provider strategy
- blocked_by: none
- options:
  - `SWISS_AGPL`
  - `SWISS_PROFESSIONAL`
- rule:
  - Swiss is an optional compatibility/provider lane, not a mandatory Astrology foundation;
  - license posture and technical admission are separate gates;
  - no production dependency is authorized by the current research.

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
- place-resolver model-mediated cold-start transport — intentionally **not admitted** after feasibility study; explicit coordinates + IANA timezone remain the fallback;
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
5. continue the active P1 natal-interpretation sequence:
   AST-P1-240 sparse emergent exact-claim admission policy
6. keep AST-P2-020 / AST-P2-030 deferred unless their explicit trigger appears
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
