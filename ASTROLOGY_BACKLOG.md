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
136547a0de8fec12deee623e45f4dcc4d05a04ed
Align loader product manifest with regression matrix
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
- status: DONE
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
- closure:
  - preserved every historical `candidates[].readiness` row, including `BLOCKED_ON_PROVIDER_OR_LICENSE`;
  - added `current_research_overlay` as a separate machine-readable post-PR-156 research-eligibility layer;
  - Chiron/Ceres/Pallas/Juno/Vesta route to `BUNDLED_EPHEMERIS` research;
  - Mean/Osculating Lilith family research and Vertex/Equatorial Ascendant route to `LOCAL_ANALYTICAL` research, while Interpolated Lilith remains a separate compatibility definition;
  - overlay explicitly keeps `production_mutation_authorized = false`, `production_selection = null`, and all affected factors `NOT_ADMITTED`;
  - Markdown readiness review now explains historical-readiness vs current-research-eligibility semantics.
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
  - `REPOSITORY_ARCHITECTURE.md`
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
  - PR #189 transport-contract probe passed exact source identity, deterministic rebuild, 13-query corpus parity, <=100 KB corpus query payload, <=10 ambiguity preview records and zero-byte repeated-query cache gates across all four profiles;
  - durable split 3+3 format/provenance/generator contract is frozen under `data/astrology/place/v1/**`; generated shard corpus and production transport remain not admitted.
- remaining_gate:
  - same-repo deterministic-data format/provenance/generator contract: COMPLETE (data corpus intentionally not committed yet);
  - deterministic corpus parity beyond the original POC fixtures: COMPLETE for the frozen 13-query research corpus;
  - same-commit GitHub Connect bounded shard retrieval + exact-ref/path retrieval + returned Git blob identity: COMPLETE at connector-surface proof scope via temporary non-merge PR #208;
  - bounded alias-first → local country/ambiguity filtering → candidate-on-demand orchestration: COMPLETE at connector-surface proof scope; GitHub Connect does not expose server-side filtering;
  - connector cache-hit/network-byte telemetry: UNAVAILABLE; do not treat repeated identical retrieval as a zero-byte cache proof;
  - real generated-shard bounded corpus payload + semantic route evidence: COMPLETE at profile-500 research scope via temporary non-merge PR #210 / workflow 36139602395 / artifact 10866252034;
  - real committed generated shard → GitHub Connect exact-ref retrieval / byte identity / bounded payload / semantic-chain product validation: COMPLETE via temporary non-merge PR #212; connector wall-clock/network latency telemetry is not exposed and must not be fabricated;
  - research validation is complete; production admission review found a separate unresolved deployment gate: the generated corpus is not yet persisted on a production-retrievable same-revision surface, so `ASTROLOGY_MATERIALIZATION.md` behavior and resolver transport admission remain unchanged.
- completion_gate:
  - deterministic generated-data provenance from the four exact admitted source datasets;
  - bounded worst-case retrieval supported by measured evidence;
  - exact-name/alternate-name, country filtering, ambiguity and not-found semantics preserve current resolver behavior;
  - license / attribution obligations are explicit;
  - production admission remains a separate reviewed change.

## P1 — extended astronomical facts

### AST-P1-010 — EXP-1 five-body compact ephemeris feasibility

- type: RESEARCH / PROVIDER FEASIBILITY
- status: DONE
- priority: P1
- owner: Astrology extended ephemeris research
- blocked_by: none
- subjects:
  - Chiron
  - Ceres
  - Pallas
  - Juno
  - Vesta
- canonical_research:
  - `references/astrology/CHATGPT_ONLY_EXTENDED_EPHEMERIS_FEASIBILITY.md`
  - `references/astrology/EXTENDED_CHART_E2_EPHEMERIS_OBJECTS_RESEARCH.md`
  - `references/astrology/ASTROLOGY_EXP1_SAMPLED_EPHEMERIS_FEASIBILITY.md`
  - `references/astrology/astrology_exp1_sampled_ephemeris_feasibility.json`
- target:
  - compare bounded local representations without making a live third-party API a production runtime dependency.
- candidate representations:
  1. bounded SPK excerpt;
  2. piecewise Chebyshev coefficients;
  3. sampled vectors/longitude + interpolation;
  4. multi-epoch osculating elements.
- measured_result:
  - temporary non-merge PR #181 / workflow run `36086788978` evaluated `sampled-wrapped-longitude-hermite-v0` with 10/20/40-day spacing;
  - source authority was NASA/JPL Horizons in build/research execution only; candidate runtime network dependency remained false;
  - all three variants were evaluated against the same 12 E2 F/H/V fixture instants × five objects;
  - no variant passed the prospectively frozen feasibility gate;
  - 10-day spacing was closest: 767,760-byte float64 payload, longitude p95 4.340 arcsec, longitude max 25.284 arcsec, but speed max 0.002074545 deg/day exceeded the frozen 0.001 deg/day gate;
  - 20/40-day spacing reduced payload but materially worsened longitude and speed residuals;
  - Chiron remained separately measured from direct Horizons samples; no one-epoch or generic Keplerian downgrade was used;
  - selected passing candidate remains `null`; production admission remains unchanged.
- research_boundary:
  - this negative result rejects only the tested sampled/Hermite candidate under the frozen gate;
  - bounded SPK, piecewise Chebyshev and multi-epoch osculating alternatives remain unevaluated research options;
  - their existence does not create an automatic follow-up or production task.
- completion_gate:
  - at least one representation is evaluated under the same bounded fixture set;
  - no silent Keplerian downgrade;
  - Chiron receives separate perturbation-sensitive treatment;
  - build/research network use is separated from ordinary ChatGPT runtime;
  - feasibility result does not itself grant production admission.

### AST-P1-020 — EXP-2 Mean Black Moon Lilith local analytical parity

- type: RESEARCH / DERIVED FACT
- status: DONE
- priority: P1
- owner: Astrology Lilith research
- blocked_by: none
- canonical_research:
  - `references/astrology/CHATGPT_ONLY_EXTENDED_EPHEMERIS_FEASIBILITY.md`
  - `references/astrology/EXTENDED_CHART_E3_LILITH_RESEARCH.md`
  - `references/astrology/ASTROLOGY_EXP2_MEAN_LILITH_PARITY.md`
  - `references/astrology/astrology_exp2_mean_lilith_iers2003_parity.json`
  - `references/astrology/mean_lilith_iers2003_research.py`
- target:
  - independently implement and validate one explicitly named Mean Lilith definition;
  - pin authoritative formula source, frame/equinox policy and longitude normalization.
- measured_result:
  - explicit fact id `black_moon_lilith_mean_iers2003_v1`;
  - definition pinned to IERS 2003 secular mean lunar apogee `F + Omega - l + 180°`, mean ecliptic / mean equinox of date, TT centuries from J2000, modulo-360 longitude;
  - temporary non-merge PR #183 / workflow run `36088099046` evaluated 17 prospective fixtures over research window `T=-2..+2` Julian centuries (~1800-2200);
  - ERFA same-definition max residual `2.0463630789890885e-10 arcsec` passed the frozen `0.0001 arcsec` gate;
  - independent XALEN/Meeus compatibility max residual `0.7098061008719014 arcsec` passed the frozen `1.0 arcsec` gate;
  - Swiss `SE_MEAN_APOG` was explicitly report-only because it is a different ELP-hybrid definition; observed compatibility residual ranged ~79.044-416.343 arcsec;
  - no bare `Lilith` alias was introduced;
  - research validation window is not a production-admitted date window;
  - production admission remains `NOT_GRANTED`.
- closure:
  - Mean Lilith project-owned analytical research → parity PASS → definition identity resolved → research implementation retained under `references/` → NOT production-admitted.
- completion_gate:
  - no bare `Lilith` alias;
  - prospective bounded fixtures across the prospectively declared research validation window;
  - comparison against at least two independent reference paths where practical;
  - residual policy documented before result review;
  - production admission remains separate.

### AST-P1-030 — EXP-3 Osculating / True Lilith local state-vector parity

- type: RESEARCH / DERIVED FACT
- status: DONE
- priority: P1
- owner: Astrology Lilith research
- blocked_by: none
- canonical_research:
  - `references/astrology/CHATGPT_ONLY_EXTENDED_EPHEMERIS_FEASIBILITY.md`
  - `references/astrology/EXTENDED_CHART_E3_LILITH_RESEARCH.md`
  - `references/astrology/ASTROLOGY_EXP3_OSCULATING_LILITH_STATE_VECTOR.md`
  - `references/astrology/astrology_exp3_osculating_lilith_state_vector.json`
  - `references/astrology/osculating_lilith_state_research.py`
- target:
  - test whether the pinned Astronomy Engine Moon state capability can support a project-owned instantaneous lunar-apogee research derivation;
  - keep osculating/true identity separate from Mean and Interpolated Lilith;
  - do not infer production state-vector admission from dependency capability.
- measured_result:
  - candidate id `black_moon_lilith_osculating_lrl_aengine_v0` uses geocentric EQJ `GeoMoonState()`, Earth-Moon-system μ, LRL eccentricity vector and ECT output longitude;
  - temporary non-merge PR #185 / workflow run `36093918723` evaluated 17 prospective fixtures over research window `T=-0.5..+0.5` Julian centuries (~1950-2050);
  - exact-state vs 0.05-day finite-difference max `0.0736442766763048°` passed the frozen `0.25°` gate;
  - 0.025/0.05/0.1-day finite-difference spread max `0.2771757229215268°` passed the frozen `0.50°` gate;
  - changing Earth-Moon μ to Earth-only μ shifted the derived direction by up to `16.91063143396633°`, establishing material model sensitivity;
  - Swiss `SE_OSCU_APOG` residual ranged `0.011865695005838006°..0.15242307614090578°` and remains report-only; no Swiss-exact or same-definition claim is granted;
  - required Moon state input fails closed in the retained research implementation;
  - production calculation and semantic interpretation admission remain `NOT_GRANTED`.
- closure:
  - Osculating/True Lilith project-owned state-vector research → stability PASS → LRL definition + Earth-Moon μ identity resolved → model sensitivity measured → research implementation retained under `references/` → NOT production-admitted.
- completion_gate:
  - explicit mathematical definition;
  - exact research input/state-vector authority documented without implying production fact admission;
  - model sensitivity reported;
  - no claim of Swiss-exact compatibility unless independently demonstrated;
  - fail closed when required state vectors are unavailable.

### AST-P1-040 — EXP-4 Vertex / Equatorial Ascendant formula admission study

- type: RESEARCH / DERIVED GEOMETRY
- status: DONE
- priority: P1
- owner: Astrology extended-point research
- blocked_by: none
- subjects:
  - Vertex
  - Equatorial Ascendant
  - East Point naming/alias policy
- canonical_research:
  - `references/astrology/CHATGPT_ONLY_EXTENDED_EPHEMERIS_FEASIBILITY.md`
  - `references/astrology/EXTENDED_CHART_E4_SPECIAL_POINTS_RESEARCH.md`
  - `references/astrology/ASTROLOGY_EXP4_SPECIAL_POINTS_GEOMETRY.md`
  - `references/astrology/astrology_exp4_special_points_geometry.json`
  - `references/astrology/special_points_geometry_research.py`
- measured_result:
  - `vertex_prime_vertical_ecliptic_v0` defines Vertex as the western prime-vertical/ecliptic intersection;
  - `equatorial_ascendant_ra_plus_90_v0` defines Equatorial Ascendant as the ecliptic point with RA = ARMC + 90°;
  - temporary non-merge PR #187 / workflow run `36095412306` validated seven synthetic geometry fixtures including ±89° latitude and five public real-location fixtures;
  - synthetic plane residual max `5.551115123125783e-17` passed the frozen `1e-12` gate;
  - Equatorial Ascendant RA-identity residual max `2.842170943040401e-14°` passed the frozen `1e-10°` gate;
  - same-input Swiss max residual `2.842170943040401e-14°` passed the frozen `1e-8°` gate;
  - current project sidereal-time/mean-obliquity input path max Swiss residual `0.0016446705079715684°` passed the frozen `0.05°` gate;
  - Astrolog `EP` → Swiss `SE_EQUASC` provides named East Point compatibility evidence, but canonical mathematical identity and production alias admission remain separate;
  - no new ephemeris dependency is required;
  - production calculation and semantic interpretation admission remain `NOT_GRANTED`.
- closure:
  - Vertex / Equatorial Ascendant project-owned geometry research → formula parity PASS → identities/frame conventions resolved → East Point retained as named compatibility evidence only → research implementation retained under `references/` → NOT production-admitted.
- completion_gate:
  - formulas and frame conventions pinned;
  - synthetic + real-location fixtures;
  - Vertex and Equatorial Ascendant identities remain distinct;
  - `East Point` is not production-admitted merely from compatibility evidence;
  - no new ephemeris dependency solely for these derived points.

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

### AST-SHARED-002 — Astrology × Zi Wei reconciliation pointer

- type: SHARED POINTER ONLY
- canonical coordination owner: `ZIWEI_BACKLOG.md#ZW-SHARED-001`
- canonical technical contract: `CROSS_VALIDATION.md` §7
- mutable status is **not** tracked here; follow the Zi Wei backlog owner to avoid divergent shared state.

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
