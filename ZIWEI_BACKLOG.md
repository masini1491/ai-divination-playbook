# Zi Wei Backlog

Authority: **COORDINATION-ONLY / NOT PRODUCTION AUTHORITY / NOT RESEARCH EVIDENCE / NOT ROUTING AUTHORITY**

Purpose: preserve the current Zi Wei maintenance, evaluation and deferred research queue so fresh ChatGPT sessions do not have to reconstruct active work from historical research documents, PR history or conversation handoffs. This file records coordination state only. Canonical technical truth remains in `ZIWEI.md`, admission manifests, production tools, materialization contracts and `references/ziwei/**`.

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
P1 = near-term evaluation, architecture or feature admission
P2 = later / trigger-based expansion
SHARED = cross-method work not owned only by Zi Wei
```

## Current baseline

Last reviewed against:

```text
ai-divination-playbook main
7f307858d6f2a688b6e2cba5dcbbc9641d5cf19a
Add Astrology repository architecture backlog item
```

This SHA is review evidence only, not a pin. Every maintenance, evaluation or implementation task must resolve current `main` again before mutation.

## Recommended execution order

Active near-term Zi Wei work:

1. **ZW-P1-070 — Natal synthesis v1 end-to-end reading evaluation**
2. **ZW-P1-080 — Zi Wei root-surface / domain-path normalization**

Standing guard:

- **ZW-P0-003 — Keep Zi Wei production stack / transport / admission synchronized** remains OPEN and is enforced alongside every affected production change.

Deferred / trigger-based work:

- **ZW-P2-026 — Sparse star×palace contextual research v4/v8** — resume only for a recurring real-reading semantic gap or an explicitly authorized bounded research question; targeted V5/V6 rechecks reopened `七殺×福德宮`, `天梁×父母宮`, and `巨門×兄弟宮`; V7 kept `太陰×子女宮` `HIGH_RISK_BOUNDED / resolved`; V8 advanced `七殺×福德宮` and `巨門×兄弟宮` to research `ADMISSION-CANDIDATE`; the two candidates are now separately production-admitted, while `天梁×父母宮` remains deferred as `DEFER-BORDERLINE`.

The 168-cell matrix remains a routing/control plane and long-term research horizon. It is not a near-term product KPI or release blocker.

## Backlog retention rule

This file is an active / deferred coordination surface, not a completed-work archive.

- `OPEN`, `IN_PROGRESS`, current critical-path `BLOCKED`, standing guards and `DEFERRED` trigger-based work may keep their minimum-sufficient task contracts here.
- `DONE` task bodies are removed after canonical closure; detailed PR / workflow / artifact / candidate-commit history remains in Git history and canonical owners/evidence.
- A completed item stays here only as a compact anti-rediscovery pointer when forgetting it would materially cause the work to be reopened or a deliberate boundary to be lost.
- A completed heading may remain as a compact routing anchor when another current surface points to its fragment identifier.
- Do not create a parallel backlog-history document merely to preserve removed closure prose.

## P0 — correctness and reconciliation

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
  - typed request/result schemas under `schemas/ziwei/**`
- guard:
  - every future Zi Wei production scope change must update every materially affected runtime / schema / admission / deterministic transport / materialization / index / coordination owner in the same bounded work unit;
  - derived transport artifacts never become source authority;
  - completed capabilities must not be rediscovered as open because a current-state surface was left stale;
  - affected behavioral / structural validation and canonical read-back close with the production change.
- rule:
  - this is a standing reconciliation guard, not a request to change current production behavior by itself.

## P1 — active input / natal synthesis work

### ZW-P1-070 — Natal synthesis v1 end-to-end reading evaluation

- type: EVALUATION / INTERPRETATION DELIVERY / PRODUCT SPECIFICITY
- status: OPEN
- priority: P1
- owner: Zi Wei production evaluation
- blocked_by:
  - ZW-P1-060 — DONE
- input_lane_note:
  - explicit-IANA-timezone readings can proceed directly;
  - supported Taiwan birthplace-only readings can now use the admitted `ziwei-birthplace-timezone-tw-v1` pre-adapter to resolve `Asia/Taipei` before the existing Gregorian calendar path;
  - unsupported/non-Taiwan birthplace text still fails closed and requires an explicit IANA timezone.
- current_authority:
  - `natal_synthesis_v1` is already production-admitted as a selection-only layer over the default admitted natal claim set;
  - it creates no new doctrine and does not change optional-module defaults;
  - the matrix is reading-gap-driven rather than a bulk-completion program.
- goal:
  - run a small bounded set of end-to-end production natal readings using current default synthesis behavior;
  - evaluate whether output is more specific, less repetitive and more chart-structured without doctrine overreach;
  - inspect whether any remaining genericness is caused by focus selection / ordering or by a recurring missing star×palace semantic distinction.
- evaluation_dimensions:
  - specificity / chart distinctiveness;
  - generic filler / repetition;
  - traceability to admitted evidence;
  - cross-signal coherence / useful tension;
  - doctrine overreach / unsupported semantic inflation.
- decision_gate:
  - **A — sufficiently distinctive:** keep matrix low priority and continue output / synthesis refinement only when a concrete UX issue appears;
  - **B — genericness is retrieval / ordering:** adjust synthesis selection / ranking; do not open new matrix research;
  - **C — the same star×palace gap recurs across readings:** open only those recurring cells as bounded research candidates under `ZW-P2-026`.
- boundaries:
  - no synthetic user-perceived-accuracy score;
  - no optimization that promotes semantics merely because a reading feels resonant;
  - no new doctrine, calculation-engine change or optional-module default change from this evaluation alone;
  - the 14 unreviewed 疾厄宮 identities remain a separate health-safe research path.
- completion_gate:
  - a small bounded reading sample is reviewed against the dimensions above;
  - the dominant outcome is classified as A / B / C with concrete evidence;
  - any follow-up is persisted only as the minimum bounded coordination delta required by that outcome.

## P2 — deferred / trigger-based research

### ZW-P2-026 — Sparse star×palace contextual research v4/v8

- type: RESEARCH / INTERPRETATION
- status: DEFERRED
- priority: P2
- owner: Zi Wei interpretation evidence
- canonical_research:
  - `references/ziwei/STAR_PALACE_CONTEXTUAL_RESEARCH_V4.md`
  - `references/ziwei/STAR_PALACE_CONTEXTUAL_RESEARCH_V5.md`
  - `references/ziwei/STAR_PALACE_CONTEXTUAL_RESEARCH_V6.md`
  - `references/ziwei/STAR_PALACE_CONTEXTUAL_RESEARCH_V7.md`
  - `references/ziwei/STAR_PALACE_CONTEXTUAL_RESEARCH_V8.md`
  - `references/ziwei/STAR_PALACE_COVERAGE_ARCHITECTURE_V1.md`
  - `indexes/ziwei/star_palace_coverage_v1.json`
- current_state:
  - all ordinary non-health palace rows are reviewed;
  - current coverage = 168 total / 154 reviewed / 119 resolved / 14 unreviewed;
  - the 14 unreviewed identities are the 疾厄宮 row;
  - `紫微×官祿宮` / `天府×財帛宮` / `太陽×父母宮` / `天同×兄弟宮` remain resolved bounded-L5 after targeted recheck;
  - `太陰×子女宮` remains `HIGH_RISK_BOUNDED / resolved` after the separate V7 high-risk review;
  - `七殺×福德宮` and `巨門×兄弟宮` are now production-admitted dedicated-L4 contextual claims;
  - `天梁×父母宮` remains the only V5–V8 reading-gap candidate still `DEFERRED_EVIDENCE / DEFER-BORDERLINE`;
  - production dedicated-L4 expansion is sparse and remains separately admitted from research classification.
- trigger:
  - a recurring real-reading semantic gap identifies a specific unresolved / insufficient star×palace cell; or
  - the user explicitly authorizes a bounded research question.
- continuation_policy:
  - do not resume bulk matrix sweeping;
  - compare any candidate against existing star-core + palace-domain bounded composition first;
  - keep research classification separate from production admission;
  - do not reopen neighboring cells merely because one recurring gap is found.
- health_boundary:
  - 疾厄宮 remains a separate health-safe path with explicit medical / injury / mortality safety gates;
  - no concrete disease, injury, mortality or diagnostic prediction may be promoted from matrix research;
  - health-row completion does not block natal synthesis evaluation.
- long_term_horizon:
  - `resolved_cells = 168` remains a research horizon, not a near-term KPI or release blocker.

## Completed routing anchors

These headings remain only because other current repository surfaces point to their fragment identifiers.

### ZW-P2-030 — Non-Asia/Taipei civil-time input normalization

- type: COMPLETED CONSUMER POINTER
- status: DONE
- canonical_contract: `CIVIL_TIME_NORMALIZATION.md`
- shared coordination owner: `ASTROLOGY_BACKLOG.md#AST-SHARED-003`
- shared implementation pointer: `ASTROLOGY_BACKLOG.md#AST-P1-190`
- current boundary:
  - Zi Wei consumes the admitted shared IANA civil-time normalizer and preserves validated local Gregorian fields for Gregorian→lunar conversion;
  - bounded Taiwan birthplace→timezone pre-resolution is separately admitted under `ZW-P1-080`; broader/global place guessing remains outside admission;
  - true-solar-time remains a separate explicit policy.

### ZW-SHARED-001 — Astrology × Zi Wei reconciliation contract

- type: SHARED POINTER ONLY
- status: DONE
- canonical technical contract: `CROSS_VALIDATION.md` §7
- admitted pair: `Astrology natal × Zi Wei natal_baseline`
- boundary:
  - preserve method-specific evidence lineage;
  - no house↔palace / planet↔star one-to-one mapping, voting, score averaging, objective-probability promotion or forced convergence;
  - Astrology transit × Zi Wei natal remains outside the admitted reconciliation pair.
- external pointer:
  - `ASTROLOGY_BACKLOG.md#AST-SHARED-002` points here; mutable technical authority remains in `CROSS_VALIDATION.md`.

## Completed anti-rediscovery index

The items below are **DONE**. They are retained only as compact identity pointers; do not reopen them unless a new regression, explicit scope expansion or canonical-owner change creates a new judgment node.

- **ZW-P0-001 — Reconcile stale Zi Wei research/current-state documents** — DONE.
- **ZW-P0-002 — Harden conditional applicability / activation semantics** — DONE.
- **ZW-P1-004 — Minguo year-notation input adapter** — DONE.
- **ZW-P1-003 — Calendar deterministic-data architecture evaluation** — DONE.
- **ZW-P1-001 — Unified Zi Wei runtime and typed request/result interface** — DONE.
- **ZW-P1-002 — Normalize Zi Wei production / research execution boundary** — DONE.
- **ZW-P1-010 — M0 auxiliary stars: 左輔／右弼／文昌／文曲** — DONE.
- **ZW-P1-020 — Four Transformations production admission** — DONE.
- **ZW-P1-025 — Natal palace occupancy and empty-palace applicability facts** — DONE.
- **ZW-P1-026 — Exact-main Zi Wei deterministic handoff artifact** — DONE.
- **ZW-P1-030 — Dynamic calculation runtime** — DONE.
- **ZW-P1-040 — Dynamic interpretation claim corpus** — DONE.
- **ZW-P1-050 — Full 14×12 star×palace coverage routing architecture** — DONE.
- **ZW-P1-060 — Evidence-bounded natal synthesis v1** — DONE.
- **ZW-P1-080 — Taiwan birthplace → IANA timezone pre-adapter** — DONE; Taiwan-only `Asia/Taipei`, now supports top-level-region prefixes plus exact allowlisted locality-only aliases such as `頭份市 → 苗栗縣`; no fuzzy geocoding, coordinates or longitude inference; canonical Minguo adapter remains bundled.
- **ZW-P2-010 — M1 high-impact auxiliary stars** — DONE.
- **ZW-P2-020 — Sparse star×palace contextual claims** — DONE.
- **ZW-P2-021 — Sparse star×palace contextual research v3** — DONE.
- **ZW-P2-022 — Admit 破軍×遷移宮 sparse contextual claim** — DONE.
- **ZW-P2-023 — Admit 武曲×田宅宮 sparse contextual claim** — DONE.
- **ZW-P2-024 — Admit 天機×田宅宮 sparse contextual claim** — DONE.
- **ZW-P2-025 — Admit 破軍×夫妻宮 sparse contextual claim** — DONE.
- **ZW-P2-027 — Admit 廉貞×財帛宮 sparse contextual claim** — DONE.
- **ZW-P2-028 — Admit 武曲×命宮 sparse contextual claim** — DONE.
- **ZW-P2-050 — Body-Palace overlay interpretation admission** — DONE.
- **ZW-P2-060 — Sparse same-palace major-star combination claims** — DONE.
- **ZW-P2-040 — True-solar-time policy** — DONE.
- **ZW-P2-030 — Non-Asia/Taipei civil-time input normalization** — DONE; compact routing anchor retained above.
- **ZW-SHARED-001 — Astrology × Zi Wei reconciliation contract** — DONE; compact shared pointer retained above.

Detailed PR / workflow / artifact / candidate-commit history is intentionally omitted from this active coordination surface and remains recoverable from Git history plus the canonical owners/evidence referenced by those revisions.

## Intentionally not backlog blockers

The following are current policy choices or already-closed capabilities and must not be repeatedly rediscovered as blockers:

- Scope-A natal provider — production admitted;
- Gregorian→lunar with admitted explicit-IANA civil-time support — production admitted;
- optional brightness / M0 / M1 / Sihua profiles remain explicit/profile-bound rather than universal defaults;
- ChatGPT deterministic materialization transport — production available;
- explicit Zi Wei routing — admitted;
- ordinary unspecified-user auto-routing — intentionally disabled, not an open defect;
- full 14×12 dedicated star×palace dictionary — intentionally rejected;
- exhaustive 14×14 same-palace major-star pair dictionary — intentionally rejected; only sparse source-explicit pair overrides are admitted/researched;
- the star×palace matrix is a coverage/routing control plane, not a semantic authority or completion KPI;
- Five-Element Bureau user-facing semantics — current Scope-A treats 五行局 as a deterministic chart-construction / placement fact, not an independent interpretation factor; calculation identity must not be promoted into personality or fate doctrine without a separate future evidence/admission decision;
- scientific/objective predictive-validity claim — not a project goal.

## Fresh-session continuation order

Unless the user explicitly asks for a different bounded Zi Wei task, a fresh development/research chat should:

```text
1. resolve current main
2. read ZIWEI_BACKLOG.md
3. reconcile changed status against canonical owners
4. enforce ZW-P0-003 alongside any affected production change
5. continue ZW-P1-070 small end-to-end natal synthesis evaluation using explicit IANA timezone or the admitted Taiwan birthplace pre-adapter
6. keep ZW-P2-026 deferred unless its recurring-gap / explicit-research trigger appears
```

Do not infer from this ordering that a backlog entry authorizes production mutation. Research, evaluation, semantic admission, calculation admission, routing and production mutation remain separate gates.

## Update rule

When a backlog item changes:

1. resolve current repository `main`;
2. update only the affected coordination item;
3. link the canonical owner / admission / evidence that proves the new state;
4. mark `DONE` only after required validation, merge/promotion and canonical read-back;
5. after closure, remove completed task bodies unless a compact anti-rediscovery pointer or externally referenced routing anchor is still needed;
6. do not use this backlog as authority to bypass a production/research admission gate;
7. do not silently add new work because an implementation happens to expose extra capability.
