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
c7f7735c54043c3b25e04b196a88136ff4d019cb
Add Zi Wei coordination backlog (#157)
```

This SHA is review evidence only, not a pin. Every maintenance or implementation task must resolve current `main` again before mutation.

Recent Astrology closure sequence reviewed:

```text
#142  Add Astrology core materialization transport
#143  Record Astrology materialization product PASS
#144  Close Astrology place resolver cold-start transport
#145  Admit Astrology E1 derived axes
#146  Admit Astrology E4 Fortune and deterministic sect
#147  Close Astrology derived fact interpretation bypass
#148  Reconcile Astrology extended-chart roadmap
#149  Admit Astrology E7 named rulership projections
#150  Admit Astrology E5 aspect policy identity
#151  Admit Astrology E6 major-aspect pattern topology
#152  Admit bounded Descendant and IC interpretation claims
#154  Harden Astrology E5 E6 runtime boundaries
#155  Reconcile Astrology E8 and natal projection routing
#156  Research ChatGPT-only extended ephemeris alternatives
```

The closed work above must not be repeatedly rediscovered as open work unless a new regression or explicit scope expansion appears.

## P0 — correctness and reconciliation

### AST-P0-001 — Reconcile E8 extended-object readiness after ChatGPT-only feasibility research

- type: MAINTENANCE / RECONCILIATION
- status: OPEN
- priority: P0
- owner: Astrology extended-chart research coordination
- blocked_by: none
- canonical_evidence:
  - `references/astrology/extended_chart_e8_admission_readiness.json`
  - `references/astrology/EXTENDED_CHART_E8_PRODUCTION_ADMISSION_READINESS.md`
  - `references/astrology/CHATGPT_ONLY_EXTENDED_EPHEMERIS_FEASIBILITY.md`
- problem:
  - PR #156 correctly broadened D1 from a Swiss-centered three-way choice into capability lanes;
  - the candidate rows for Chiron / Ceres / Pallas / Juno / Vesta / Lilith / Vertex / Equatorial Ascendant still retain the older `BLOCKED_ON_PROVIDER_OR_LICENSE` research class;
  - that historical class is useful evidence, but fresh gap reviews can read it as if local analytical / bundled-ephemeris feasibility had not been established.
- completion_gate:
  - preserve historical E8 evidence rather than rewriting it as if the later research existed at the time;
  - add explicit current-state/supersession metadata or a new readiness layer;
  - distinguish `provider/license blocked under original E8 implementation surface` from `local analytical / bundled ephemeris research now eligible`;
  - do not grant production admission;
  - regression / structural validation passes.

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

## P1 — place-resolution transport

### AST-P1-005 — Query-bounded place-resolver shard transport admission

- type: RESEARCH / MATERIALIZATION / PROVIDER TRANSPORT
- status: OPEN
- priority: P1
- owner: Astrology place-resolution materialization
- blocked_by: none
- canonical_evidence:
  - `ASTROLOGY_MATERIALIZATION.md`
  - `ASTROLOGY_PLACE_RESOLVER_ADMISSION_V1.json`
  - `reports/astrology/ASTROLOGY_PLACE_RESOLVER_MATERIALIZATION_FEASIBILITY.md`
  - `tools/astrology_place_shard_benchmark.py`
  - `tools/astrology_place_split_shard_benchmark.py`
- current_state:
  - original A-MAT-2 whole-package/model-mediated cold-start transport remains not admitted;
  - PR #172 exact-byte research POC satisfies the query-bounded-shard feasibility re-open trigger;
  - all four admitted `geonamescache==3.0.2` dataset identities matched the prior A-MAT-2 hashes;
  - fixture parity passed for 樹林區/TW, Tokyo/JP and ambiguous Springfield cases across all tested profiles and widths;
  - PR #173 split-store POC preserved fixture parity across all four profiles and selected alias-3hex + candidate-3hex as the current format candidate;
  - split 3+3 reduces aggregate generated storage from 314,579,927 bytes to 189,935,792 bytes (~39.6% reduction);
  - `cities500` split 3+3 unique lookup measured 18,494 bytes for 樹林區/TW and 23,702 bytes for Tokyo/JP; Springfield ambiguity preview measured 63,069 bytes;
  - split 3+3 theoretical file surface is 8,192 shard paths/profile; candidate 2-hex was too costly for ambiguity retrieval and candidate 4-hex created an excessive file surface.
- remaining_gate:
  - freeze external repository / manifest / attribution / exact-revision contract around the selected alias-3hex + candidate-3hex format candidate;
  - make the generator build alias routing once per profile and keep alias/candidate generation deterministic;
  - define exact GitHub Connect retrieval + integrity verification + connector-side filtering + cache behavior;
  - expand semantic parity to a deterministic corpus beyond the bounded POC fixtures;
  - validate end-to-end cold-start payload/latency and full semantic parity;
  - only then consider changing `ASTROLOGY_MATERIALIZATION.md` current production behavior or `ASTROLOGY_PLACE_RESOLVER_ADMISSION_V1.json`.
- completion_gate:
  - deterministic generated-data provenance from the four exact admitted source datasets;
  - bounded worst-case retrieval supported by measured evidence;
  - exact-name/alternate-name, country filtering, ambiguity and not-found semantics preserve current resolver behavior;
  - license / attribution obligations are explicit;
  - production admission remains a separate reviewed change.

## P1 — extended astronomical facts

### AST-P1-010 — EXP-1 five-body compact ephemeris feasibility

- type: RESEARCH / PROVIDER FEASIBILITY
- status: OPEN
- priority: P1
- owner: Astrology extended ephemeris research
- blocked_by:
  - AST-P0-001
- subjects:
  - Chiron
  - Ceres
  - Pallas
  - Juno
  - Vesta
- canonical_research:
  - `references/astrology/CHATGPT_ONLY_EXTENDED_EPHEMERIS_FEASIBILITY.md`
  - `references/astrology/EXTENDED_CHART_E2_EPHEMERIS_OBJECTS_RESEARCH.md`
- target:
  - compare bounded local representations without making a live third-party API a production runtime dependency.
- candidate representations:
  1. bounded SPK excerpt;
  2. piecewise Chebyshev coefficients;
  3. sampled vectors/longitude + interpolation;
  4. multi-epoch osculating elements.
- measurement contract:
  - artifact bytes;
  - materialization/token cost;
  - bounded coverage;
  - maximum and p95 longitude residual;
  - speed residual where relevant;
  - worst fixture date/object;
  - prospectively declared thresholds before validation.
- completion_gate:
  - at least one representation is evaluated under the same bounded fixture set;
  - no silent Keplerian downgrade;
  - Chiron receives separate perturbation-sensitive treatment;
  - build/research network use is separated from ordinary ChatGPT runtime;
  - feasibility result does not itself grant production admission.

### AST-P1-020 — EXP-2 Mean Black Moon Lilith local analytical parity

- type: RESEARCH / DERIVED FACT
- status: OPEN
- priority: P1
- owner: Astrology Lilith research
- blocked_by:
  - AST-P0-001
- canonical_research:
  - `references/astrology/CHATGPT_ONLY_EXTENDED_EPHEMERIS_FEASIBILITY.md`
  - `references/astrology/EXTENDED_CHART_E3_LILITH_RESEARCH.md`
- target:
  - independently implement and validate one explicitly named Mean Lilith definition;
  - pin authoritative formula source, frame/equinox policy and longitude normalization.
- completion_gate:
  - no bare `Lilith` alias;
  - prospective bounded fixtures across the admitted date window;
  - comparison against at least two independent reference paths where practical;
  - residual policy documented before result review;
  - production admission remains separate.

### AST-P1-030 — EXP-3 Osculating / True Lilith local state-vector parity

- type: RESEARCH / DERIVED FACT
- status: OPEN
- priority: P1
- owner: Astrology Lilith research
- blocked_by:
  - AST-P1-020
- target:
  - test whether admitted Moon state vectors can support a project-owned instantaneous lunar-apogee derivation;
  - keep osculating/true identity separate from Mean and Interpolated Lilith.
- completion_gate:
  - explicit mathematical definition;
  - exact input/state-vector authority documented;
  - model sensitivity reported;
  - no claim of Swiss-exact compatibility unless independently demonstrated;
  - fail closed when required state vectors are unavailable.

### AST-P1-040 — EXP-4 Vertex / Equatorial Ascendant formula admission study

- type: RESEARCH / DERIVED GEOMETRY
- status: OPEN
- priority: P1
- owner: Astrology extended-point research
- blocked_by:
  - AST-P0-001
- subjects:
  - Vertex
  - Equatorial Ascendant
  - East Point naming/alias policy
- canonical_research:
  - `references/astrology/CHATGPT_ONLY_EXTENDED_EPHEMERIS_FEASIBILITY.md`
  - `references/astrology/EXTENDED_CHART_E4_SPECIAL_POINTS_RESEARCH.md`
- target:
  - establish project-owned spherical-astronomy derivations from admitted date/time/location inputs;
  - independently validate geographic and latitude edge cases.
- completion_gate:
  - formulas and frame conventions pinned;
  - synthetic + real-location fixtures;
  - Vertex and Equatorial Ascendant identities remain distinct;
  - `East Point` alias only admitted after compatibility/source identity is resolved;
  - no new ephemeris dependency solely for these derived points unless formula study fails.

## P1 — interpretation and policy expansion

### AST-P1-100 — Source-backed South Node / Part of Fortune interpretation admission

- type: FEATURE / INTERPRETATION
- status: OPEN
- priority: P1
- owner: Astrology natal interpretation evidence
- blocked_by: none
- current_state:
  - Mean South Node deterministic fact is admitted;
  - Part of Fortune + deterministic sect are admitted;
  - both remain fact-only under current derived-fact interpretation boundary.
- target:
  - admit only source-backed bounded semantic claims where the source and applicability are explicit.
- completion_gate:
  - exact claim bindings;
  - source/tradition scope preserved;
  - typed selector/handoff exact allowlist;
  - no generic model-memory meaning;
  - facts remain usable even when no semantic claim is admitted.

### AST-P1-110 — Extended aspect participant policies

- type: FEATURE / POLICY
- status: OPEN
- priority: P1
- owner: Astrology aspect policy
- blocked_by:
  - relevant extended deterministic facts must be admitted first
- current_state:
  - `aspect-participants-core-bodies-v1` is admitted;
  - current major-aspect/orb identity is admitted;
  - extended points/angles are not silently included.
- target:
  - add versioned participant policies only for admitted calculable facts;
  - keep current core policy unchanged.
- completion_gate:
  - explicit policy IDs;
  - no auto-include when a provider learns a new object;
  - separate semantic admission from geometric participation.

### AST-P1-120 — Yod / Stellium / Grand Quintile policy expansion

- type: FEATURE / PATTERN POLICY
- status: OPEN
- priority: P1
- owner: Astrology pattern topology
- blocked_by:
  - AST-P1-110 for any extended participants
- current_state:
  - T-Square / Grand Trine / Grand Cross / Kite / Mystic Rectangle / Cradle / Grand Sextile admitted under current major-aspect topology;
  - Yod requires quincunx;
  - Stellium definition remains unadmitted;
  - Grand Quintile requires quintile/biquintile policy;
  - exact 唐綺陽 compatibility remains unverified.
- completion_gate:
  - named aspect/orb/participant/pattern policies;
  - Stellium minimum-count/span/sign-boundary definition explicitly selected;
  - no exact consumer-compatibility claim without independent evidence;
  - current admitted topology behavior preserved.

### AST-P1-130 — Transit house search / temporal house context

- type: FEATURE / TRANSIT
- status: OPEN
- priority: P1
- owner: Astrology transit calculation + interpretation
- blocked_by: none
- source:
  - E8 `recommended_order` retains `TRANSIT_HOUSE_SEARCH`.
- current_state:
  - exact transit-to-natal major aspects, stations and ingresses are admitted;
  - no canonical production transit-house search owner is recorded.
- completion_gate:
  - exact request scope and time-window behavior;
  - deterministic house fact authority;
  - unknown/approximate natal-time fail-closed behavior;
  - separate calculation and semantic admission;
  - bounded search/runtime cost.

## P2 — deferred compatibility / provider expansion

### AST-P2-010 — Interpolated Black Moon Lilith

- type: RESEARCH / COMPATIBILITY
- status: DEFERRED
- priority: P2
- owner: Astrology Lilith research
- blocked_by:
  - AST-P1-020
  - AST-P1-030
- rule:
  - treat as a separate definition/product;
  - never alias to Mean or Osculating Lilith.

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

### AST-P2-040 — Broader extended ephemeris objects

- type: FEATURE / PROVIDER
- status: DEFERRED
- priority: P2
- owner: Astrology extended ephemeris
- blocked_by:
  - AST-P1-010
- rule:
  - do not expand object count before the five-body transport/precision architecture is proven;
  - no opportunistic auto-admission from an upstream catalog.

## SHARED / parallel

### AST-SHARED-001 — Casting/Vercel deployment isolation completion

- type: SHARED / CI / DEPLOYMENT
- status: IN_PROGRESS
- priority: SHARED
- owner: casting runtime / repository CI
- blocked_by: none
- current_external_work:
  - PR #153 `Fix casting deployment provenance gate`
  - head at backlog review: `5a52038e394c9e1d16c6d162e5d8ecf315a6d20e`
- relation_to_astrology:
  - this is not an Astrology feature blocker;
  - repository-wide validation/deployment coupling can still affect unrelated Astrology merges.
- target:
  - Vercel deployment only reacts to `runtime/casting/**`;
  - general repository validation must not depend on the live Vercel endpoint for unrelated Astrology/Zi Wei/docs changes.
- completion_gate:
  - merge/read-back of the final deployment-isolation design;
  - path-bounded Vercel build behavior;
  - online casting production smoke is path-bounded rather than a general main-push dependency;
  - unrelated Astrology main changes no longer inherit live Vercel availability as a gate.

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
4. prefer P0 correctness/reconciliation
5. then continue:
   AST-P1-010 compact ephemeris feasibility
   AST-P1-020 Mean Lilith
   AST-P1-030 Osculating Lilith
   AST-P1-040 Vertex / Equatorial Ascendant
6. run interpretation/policy expansion in parallel only when its factual dependencies are satisfied
```

Do not infer from this ordering that every item is automatically authorized for production mutation. Research, calculation admission, semantic admission and routing remain separate gates.

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
