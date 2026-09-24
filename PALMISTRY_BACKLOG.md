# Palmistry Backlog

Authority: **COORDINATION-ONLY / NOT PRODUCTION AUTHORITY / NOT RESEARCH EVIDENCE / NOT ROUTING AUTHORITY**

Purpose: preserve the current Palmistry maintenance, empirical-research and continuation queue so fresh ChatGPT sessions do not have to reconstruct open work from historical Palmistry research files, recent device-repeatability work, local/private execution artifacts or conversation handoffs. This file records work status only. Canonical technical truth remains in `PALMISTRY.md`, `RESEARCH_ROUTING.md`, `references/palmistry/**`, frozen result identities and the specific plan / lock / closure documents for each node.

## Status vocabulary

```text
OPEN        = identified and not yet started
BLOCKED     = cannot proceed until a stated dependency is satisfied
IN_PROGRESS = actively being executed in one bounded task
DONE        = completion gate satisfied and canonical read-back verified
DEFERRED    = intentionally not current work
```

Priority vocabulary:

```text
P0 = correctness / stale-state reconciliation before further research
P1 = current highest-value empirical continuation
P2 = later validation / expansion
SHARED = cross-method or cross-runtime work not owned only by Palmistry
```

## Current baseline

Last reviewed against:

```text
ai-divination-playbook main
808516dcf67f086ec89ca534acebb2760108ede9
Add Astrology coordination backlog (#158)
```

This SHA is review evidence only, not a pin. Every maintenance or implementation task must resolve current `main` again before mutation.

Current method status remains:

```text
Palmistry = REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE
```

## Recent bounded closures / completed work that must not be rediscovered as open

The following work is already closed or completed within its stated boundary:

- observation uncertainty composition V2 — boundedly closed;
- MediaPipe `1.0.1` vs `1.0.0` tracked 2D runtime compatibility — boundedly closed;
- capture / mirroring / EXIF / anatomical-side deterministic contract — boundedly closed;
- detector-to-detector MediaPipe vs RTMPose comparison — boundedly completed with detector provenance retained;
- principal-line segmentation bounded evidence node — closed for the admitted source/model question;
- first line-detail necessity / sensitivity study — boundedly completed; natural-field calibration remains open;
- first-upload two-device repeated-reposition pilot — complete for pilot scope;
- formal B2 `S1` source subset — locked from earliest-five captures/device;
- formal B2 `S2` / `S3` source collections — not yet supplied.

Closed work above must not be reopened merely because a fresh session has not seen the historical chat.

## P0 — current-state reconciliation

### PALM-P0-001 — Reconcile stale Palmistry overview / roadmap statements

- type: MAINTENANCE / RECONCILIATION
- status: OPEN
- priority: P0
- owner: Palmistry research coordination
- blocked_by: none
- canonical_evidence:
  - `references/palmistry/README.md`
  - `references/palmistry/SYNTHESIS.md`
  - `references/palmistry/PALMISTRY_EVIDENCE_GAP_REPRIORITIZATION_20260913.md`
  - `references/palmistry/DETECTOR_AGREEMENT_RESULTS.md`
  - `references/palmistry/MEDIAPIPE_RUNTIME_COMPATIBILITY_NODE_CLOSURE.md`
  - `references/palmistry/CAPTURE_MIRRORING_ANATOMICAL_SIDE_NODE_CLOSURE.md`
  - `references/palmistry/DEVICE_CAPTURE_FIRST_UPLOAD_PILOT_RESULTS.md`
  - `references/palmistry/DEVICE_CAPTURE_REPEATABILITY_FORMAL_COLLECTION_EXTENSION_LOCK.md`
- problem:
  - `references/palmistry/README.md` still contains historical statements that detector agreement is only predeclared / not executed;
  - older device-repeatability text still emphasizes third-party dataset-permission acquisition even though a private/user-supplied two-device pilot and a formal S1 extension lock now exist;
  - fresh sessions can therefore misread already-completed detector/runtime/capture work or overlook the actual current dependency: new S2/S3 captures.
- completion_gate:
  - preserve historical source dossiers and earlier roadmap decisions;
  - update current-state summaries or add supersession notes rather than rewriting historical execution evidence;
  - make the present B2 state explicit: pilot complete, S1 locked, S2/S3 pending;
  - mark detector agreement as completed bounded evidence rather than pending;
  - structural validation passes;
  - no production promotion.

### PALM-P0-002 — Keep B2 source-selection / freeze discipline synchronized

- type: MAINTENANCE / REGRESSION
- status: OPEN
- priority: P0
- owner: Palmistry device/capture repeatability
- blocked_by: none
- canonical_evidence:
  - `references/palmistry/DEVICE_CAPTURE_REPEATABILITY_PLAN.md`
  - `references/palmistry/DEVICE_CAPTURE_REPEATABILITY_CAPTURE_PROTOCOL.md`
  - `references/palmistry/DEVICE_CAPTURE_REPEATABILITY_FORMAL_COLLECTION_EXTENSION_LOCK.md`
  - `references/palmistry/DEVICE_CAPTURE_FIRST_UPLOAD_PILOT_RESULT_FREEZE.md`
  - `references/palmistry/DEVICE_CAPTURE_FIRST_UPLOAD_PILOT_RESULTS.md`
- standing rule:
  - existing earliest-five/device remain the formal S1 source subset;
  - first-upload ordinals 06–15 remain pilot extras and must not be relabeled as S2/S3;
  - already-inspected pilot geometry must never be used to re-rank or replace S1 captures;
  - future S2/S3 source bytes must be frozen before new detector inference.
- completion_gate:
  - this is a standing reconciliation guard; mark DONE only if replaced by a newer canonical coordination contract.

## P1 — active empirical continuation

### PALM-P1-010 — Collect formal B2 S2 / S3 source images

- type: EMPIRICAL / USER-SUPPLIED PRIVATE EVIDENCE
- status: BLOCKED
- priority: P1
- owner: Palmistry device/capture repeatability
- blocked_by: new real captures
- current_state:
  - D1 = Google Pixel 5;
  - D2 = Google Pixel 10 Pro;
  - anatomical side = left;
  - S1 = locked existing earliest-five/device;
  - S2 = pending;
  - S3 = pending.
- required_new_data:
  - S2: D1 × 5 + D2 × 5;
  - S3: D1 × 5 + D2 × 5;
  - total new images = 20.
- capture contract:
  - true setup reset between sessions;
  - each still preceded by lowering / relaxing / re-raising / natural reposition;
  - same controlled baseline family;
  - no burst / video-frame substitution;
  - no model-informed photo selection.
- completion_gate:
  - 20 new source images supplied;
  - exactly 5/device/session;
  - same explicit anatomical hand;
  - no inference performed before source freeze.

### PALM-P1-020 — Freeze formal B2 30-entry source set

- type: EMPIRICAL / PROVENANCE
- status: BLOCKED
- priority: P1
- owner: Palmistry device/capture repeatability
- blocked_by:
  - PALM-P1-010
- target:
  - combine locked S1 subset with new S2/S3;
  - freeze 20 new source SHA256 values;
  - verify duplicate-byte accounting;
  - retain only task-relevant EXIF orientation / dimensions;
  - build privacy-minimized 30-entry formal manifest;
  - freeze manifest identity before inference.
- completion_gate:
  - 30 formal entries accounted;
  - source / manifest hashes frozen;
  - privacy boundary preserved;
  - no substantive detector geometry inspected.

### PALM-P1-030 — Formal B2 P1/P2/P3 runner + raw-result freeze

- type: EMPIRICAL / EXECUTION
- status: BLOCKED
- priority: P1
- owner: Palmistry device/capture repeatability
- blocked_by:
  - PALM-P1-020
- required_pair_families:
  - P1 within-device / within-session = 60 pairs;
  - P2 cross-device / within-session = 75 pairs;
  - P3 within-device / cross-session = 150 pairs.
- required discipline:
  - exact runtime/model/geometry provenance;
  - fail closed on unresolved target / transform lineage;
  - raw JSON hash freeze before substantive metric interpretation;
  - no post-hoc production threshold.
- completion_gate:
  - all formal pair families executed and accounted;
  - raw result frozen;
  - warnings / unresolved cases recorded.

### PALM-P1-040 — Formal B2 results + bounded node closure

- type: EMPIRICAL / SYNTHESIS / CLOSURE
- status: BLOCKED
- priority: P1
- owner: Palmistry device/capture repeatability
- blocked_by:
  - PALM-P1-030
- target:
  - compare P2 vs P1 and P2 vs P3 descriptively;
  - preserve per-device / per-session heterogeneity;
  - incorporate B3b real-camera lineage observations where supported;
  - update current roadmap / overview;
  - close only the predeclared two-device controlled baseline question.
- non-claims:
  - no arbitrary-device portability;
  - no biometric identity/authentication;
  - no production cutoff;
  - no production routing.
- completion_gate:
  - results document;
  - bounded node closure;
  - roadmap/current-state reconciliation;
  - canonical read-back.

## P1/P2 — follow-up validation after B2

### PALM-P1-100 — Natural-field line-detail quality calibration

- type: EMPIRICAL / QUALITY CALIBRATION
- status: OPEN
- priority: P1/P2
- owner: Palmistry observation quality
- blocked_by:
  - formal B2 is preferred first unless the user explicitly changes priority
- current_state:
  - synthetic / controlled necessity-sensitivity work is complete;
  - natural low-quality photos, glare, uneven illumination, JPEG/crop/occlusion and held-out admission calibration remain open.
- rule:
  - no numeric production cutoff may be derived post-hoc from the existing bounded synthetic degradation study.

### PALM-P2-010 — Hand Landmarker model-artifact portability

- type: RUNTIME / MODEL COMPATIBILITY
- status: DEFERRED
- priority: P2
- owner: Palmistry detector/runtime
- blocked_by:
  - a concrete candidate model artifact/version
- current_state:
  - pinned current model SHA256 remains the active research artifact;
  - runtime package pair `1.0.1` vs `1.0.0` is already boundedly closed.
- rule:
  - do not scan arbitrary future model versions without an actual migration candidate.

### PALM-P2-020 — Longer-interval / broader device confirmation

- type: EMPIRICAL / EXTERNAL DATA
- status: DEFERRED
- priority: P2
- owner: Palmistry portability research
- blocked_by:
  - suitable permission-qualified data or new private captures
- rule:
  - public availability / paper citation / article license does not equal dataset reuse permission;
  - do not bypass existing data-use gates.

## P2 — feature / tradition expansion

### PALM-P2-100 — Chinese source-specific projection geometry

- type: FEATURE / TRADITION
- status: DEFERRED
- priority: P2
- owner: Palmistry tradition research
- rule:
  - Western CV classes do not automatically define Chinese palm-palace / 八卦 geometry.

### PALM-P2-110 — Minor lines / named patterns / mounts

- type: FEATURE / OBSERVATION
- status: DEFERRED
- priority: P2
- owner: Palmistry observation research
- rule:
  - branch / island / star / fate line / mounts require separate observation evidence and explicit tradition semantics.

### PALM-P2-120 — Western ↔ Chinese terminology mapping

- type: FEATURE / TERMINOLOGY
- status: DEFERRED
- priority: P2
- owner: Palmistry source normalization
- rule:
  - `heart/head/life` must not be silently equated with `天／人／地紋`.

## SHARED / parallel

### PALM-SHARED-001 — Cross-method production reconciliation

- type: SHARED / FUTURE
- status: DEFERRED
- priority: SHARED
- owner: cross-validation / production governance
- blocked_by:
  - Palmistry is not production-routable
- rule:
  - do not create Astrology / Zi Wei / Tarot / Meihua / Liuyao × Palmistry voting, score averaging or forced convergence while Palmistry remains research-only.

## Intentionally not backlog blockers

The following are already-closed capabilities or deliberate boundaries and must not be repeatedly rediscovered as blockers:

- Palmistry production routing — intentionally not admitted;
- observation uncertainty composition V2 — boundedly closed;
- MediaPipe `1.0.1` vs `1.0.0` tracked 2D compatibility — boundedly closed;
- MediaPipe vs RTMPose detector agreement — boundedly completed; detector provenance remains required;
- capture/mirroring/EXIF/anatomical-side deterministic contract — boundedly closed;
- principal-line segmentation bounded evidence node — closed for its admitted question;
- first-upload two-device repeated-reposition pilot — complete;
- formal S1 source subset — locked;
- B1/B2/B3 pilot ordinal strata — diagnostic only, not formal sessions;
- detector handedness — metadata only, not anatomical-side authority;
- numeric production threshold — intentionally absent;
- biometric identity/authentication — outside scope;
- scientific/objective predictive-validity claim — not a project goal.

## Fresh-session continuation order

Unless the user explicitly requests a different bounded Palmistry research task, a fresh Palmistry development/research chat should:

```text
1. resolve current main
2. read PALMISTRY_BACKLOG.md
3. reconcile item status against canonical Palmistry owners
4. run PALM-P0-001 / PALM-P0-002 maintenance if current summaries are stale
5. inspect whether S2/S3 user evidence exists
   ├─ absent  → STOP at BLOCKED on new user evidence; do not invent replacement work
   └─ present → PALM-P1-020 source freeze
              → PALM-P1-030 formal runner + raw-result freeze
              → PALM-P1-040 results + bounded closure
6. only after the active B2 dependency is resolved, continue lower-priority calibration / portability / feature nodes unless the user explicitly changes priority
```

A fresh session must not ask the user to repeat already-frozen S1 facts when the canonical lock is available.

## Update rule

When a backlog item changes:

1. resolve current repository `main`;
2. update only the affected item;
3. link the canonical owner / plan / lock / result / closure that proves the new state;
4. mark `DONE` only after merge + canonical read-back + required execution / validation evidence;
5. do not use this backlog as authority to bypass a research or production admission gate;
6. do not silently create thresholds from observed pilot/formal distributions;
7. preserve private-image / EXIF / biometric-safety boundaries;
8. if another backlog owns a shared item, link it rather than creating divergent technical authority;
9. generated index / loader metadata remain derived discoverability hints, never backlog authority.
