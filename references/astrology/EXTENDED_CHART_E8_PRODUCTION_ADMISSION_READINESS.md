# Astrology Extended Chart Facts Phase E8｜Production Admission Readiness

Status: **REFERENCE-ONLY / ADMISSION REVIEW / NO PRODUCTION MUTATION AUTHORIZED**

Reviewed production baseline: `masini1491/ai-divination-playbook@0672df50233a6a7149dd4434179cc6a05467445d`

Research inputs:

- `EXTENDED_CHART_E1_DERIVED_AXES_RESULTS.md`
- `EXTENDED_CHART_E2_EPHEMERIS_OBJECTS_RESEARCH.md`
- `EXTENDED_CHART_E3_LILITH_RESEARCH.md`
- `EXTENDED_CHART_E4_SPECIAL_POINTS_RESEARCH.md`
- `EXTENDED_CHART_E5_ASPECT_PARTICIPANT_POLICY.md`
- `EXTENDED_CHART_E6_PATTERN_TOPOLOGY_RESEARCH.md`
- `EXTENDED_CHART_E7_RULERSHIP_POLICY.md`
- `extended_chart_e3_e7_policy_manifest.json`

This review does **not** admit any new production factor. Its job is to separate implementation-ready candidates from decisions that require new policy, provider, licensing, or compatibility authority.

> Current research supersession: the original D1 Swiss-centered three-way decision below is historical evidence from this E8 review. After current-stack admission and ChatGPT deterministic materialization work, `CHATGPT_ONLY_EXTENDED_EPHEMERIS_FEASIBILITY.md` broadens D1 into provider-neutral capability lanes: `CURRENT_CORE_ONLY`, `LOCAL_ANALYTICAL`, `BUNDLED_EPHEMERIS`, `EXTERNAL_RUNTIME`, `SWISS_AGPL`, and `SWISS_PROFESSIONAL`. No production selection is made by that later research.


## 1. Current production constraints

Astrology Production v1 currently admits:

```text
provider: astronomy-engine-natal-v1
astronomy-engine==2.1.19 / MIT
zodiac: tropical
center: geocentric
house systems: Whole Sign / Placidus
objects: Sun..Pluto + Mean North Node
angles: Ascendant + Midheaven
aspects: conjunction / opposition / trine / square / sextile
activation: explicit user request only
```

The production Fact Bundle 1.0 schema is intentionally structurally extensible at individual fact-row level, while `tools/astrology_runtime.py` owns cross-field policy. Therefore extended facts are not blocked merely because the schema lacks named properties for them.

The main admission gates are instead:

```text
calculation/provider authority
license boundary
object identity/provenance
runtime validation
participant/aspect/orb policy
selector and interpretation boundaries
production manifest admission
regression evidence
```

## 2. Readiness classes

### READY_WITH_CURRENT_STACK

The research identity is resolved and implementation can remain inside the current MIT Astronomy Engine + project-owned derivation architecture. Production admission would still require code/tests/manifests, but no new external calculation license is inherently required.

### READY_IF_EXPLICIT_POLICY_SELECTED

The deterministic mechanics are resolved, but production must choose or explicitly require a named policy rather than silently selecting one.

### BLOCKED_ON_PROVIDER_OR_LICENSE

The factor requires an extended astronomical calculation authority not present in current `astronomy-engine-natal-v1`, or would require a separately reviewed implementation/provider/license path.

### BLOCKED_ON_COMPATIBILITY_DEFINITION

The generic architecture is understood, but exact consumer-compatible behavior is unknown and must not be guessed.

## 2A. Current research overlay after ChatGPT-only feasibility work

The readiness rows below are intentionally preserved as **historical E8 implementation-surface judgments**. They answer whether the original production surface had an admitted calculation/provider/license path at the time of the E8 review.

PR #156 and `CHATGPT_ONLY_EXTENDED_EPHEMERIS_FEASIBILITY.md` add a separate current research layer:

| Factor / family | Historical E8 readiness | Current research eligibility | Eligible lane | Production consequence |
|---|---|---|---|---|
| Chiron | BLOCKED_ON_PROVIDER_OR_LICENSE | research eligible | BUNDLED_EPHEMERIS | none; still not admitted |
| Ceres / Pallas / Juno / Vesta | BLOCKED_ON_PROVIDER_OR_LICENSE | research eligible | BUNDLED_EPHEMERIS | none; still not admitted |
| Mean / Osculating Black Moon Lilith | BLOCKED_ON_PROVIDER_OR_LICENSE | research eligible after explicit definition split | LOCAL_ANALYTICAL | none; still not admitted |
| Interpolated Black Moon Lilith | historical family row retained | AST-P2-010 characterized: no provider-neutral default identity | explicit named definition/provider only | none; still not admitted |
| Vertex | BLOCKED_ON_PROVIDER_OR_LICENSE | research eligible as project-owned derived geometry | LOCAL_ANALYTICAL | none; still not admitted |
| Equatorial Ascendant | BLOCKED_ON_PROVIDER_OR_LICENSE | research eligible as project-owned derived geometry | LOCAL_ANALYTICAL | none; still not admitted |

Interpretation rule:

```text
candidates[].readiness
→ historical E8 implementation-surface judgment

current_research_overlay
→ later research eligibility only

research eligibility
≠ calculation admission
≠ semantic admission
≠ production provider selection
```

Therefore a fresh gap review must not read `BLOCKED_ON_PROVIDER_OR_LICENSE` as “research may not proceed.” It means the original E8 production surface lacked an admitted provider/license path. The later overlay permits bounded research into local analytical or bundled-ephemeris alternatives while keeping `production_selection = null`.

AST-P2-010 adds one narrower compatibility finding: `Interpolated Black Moon Lilith` is a **named-definition family**, not a project-default mathematical identity. Swiss `SE_INTP_APOG` and independently defined smooth apsis curves may share the user-facing label while differing numerically between passages. Any future admission must name the target definition/provider explicitly and must not infer Swiss-exact compatibility from the generic word "Interpolated".

## 3. Admission readiness matrix

| Factor / family | Readiness | Current-stack path | Remaining gate |
|---|---|---|---|
| Mean South Node | READY_WITH_CURRENT_STACK | antipode of admitted Mean North Node | production object id/provenance + runtime/provider tests |
| Descendant | READY_WITH_CURRENT_STACK | antipode of admitted Ascendant | production angle row + regressions |
| Imum Coeli | READY_WITH_CURRENT_STACK | antipode of admitted Midheaven | production angle row + regressions |
| Part of Fortune | READY_WITH_CURRENT_STACK | admitted ASC/Sun/Moon + project-owned formula; sect can use current MIT Astronomy Engine horizon capability | implement/validate `sect-geometric-solar-altitude-v1` and formula fixtures |
| Traditional rulership projection | READY_IF_EXPLICIT_POLICY_SELECTED | project-owned table projection | admission of named policy; no silent default |
| Modern rulership projection | READY_IF_EXPLICIT_POLICY_SELECTED | project-owned table projection | admission of named policy; no silent default |
| Aspect participants: current-core equivalent | READY_WITH_CURRENT_STACK | preserve existing body-only behavior under named policy | policy id/provenance plumbing |
| Aspect participants: angles / extended points | READY_IF_EXPLICIT_POLICY_SELECTED | geometry code is project-owned once facts exist | explicit participant policy; only calculable/admitted facts may participate |
| Pattern topology over existing major aspects | READY_IF_EXPLICIT_POLICY_SELECTED | project-owned graph/topology implementation | explicit participant/orb/projection policies |
| Yod | READY_IF_EXPLICIT_POLICY_SELECTED | project-owned topology | requires new quincunx aspect policy/orb; current major-only policy cannot produce Yod |
| Stellium | BLOCKED_ON_COMPATIBILITY_DEFINITION | implementation possible after definition | minimum count/span/sign-boundary/participant policy unresolved |
| Exact 唐綺陽 pattern compatibility | BLOCKED_ON_COMPATIBILITY_DEFINITION | no safe exact emulation yet | exact participant/orb/nested-pattern algorithm unverified |
| Chiron | BLOCKED_ON_PROVIDER_OR_LICENSE | current Astronomy Engine provider lacks admitted calculation path | choose extended ephemeris/provider/license + bounded epoch/tolerance |
| Ceres / Pallas / Juno / Vesta | BLOCKED_ON_PROVIDER_OR_LICENSE | current Astronomy Engine provider lacks admitted calculation path | same as Chiron |
| Mean / Osculating / Interpolated Black Moon Lilith | BLOCKED_ON_PROVIDER_OR_LICENSE | identities resolved, current provider lacks admitted calculation path | choose extended provider/license; do not collapse variants |
| Vertex | BLOCKED_ON_PROVIDER_OR_LICENSE | current provider does not expose admitted Vertex calculation | independently validated project-owned formula or admitted provider |
| Equatorial Ascendant | BLOCKED_ON_PROVIDER_OR_LICENSE | current provider does not expose admitted calculation | independently validated project-owned formula or admitted provider |
| `East Point` display alias | BLOCKED_ON_COMPATIBILITY_DEFINITION | may alias Equatorial Ascendant only after source match | compatibility-source identity / naming policy |

## 4. MIT/current-stack lane

The lowest-risk production extension lane does **not** require Swiss Ephemeris:

```text
E1 derived axes
+ E4 Part of Fortune / deterministic sect
+ explicit named E7 rulership projections
+ E5 policy plumbing for existing or explicitly selected participants
+ E6 project-owned topology only where admitted aspects already exist
```

Astronomy Engine's pinned source exposes a `Horizon(...)` calculation for local horizontal coordinates. This gives the current MIT dependency a plausible calculation path for the Sun geometric altitude needed by `sect-geometric-solar-altitude-v1`; implementation still requires dedicated fixtures and parity evidence before admission.

This lane can improve consumer-chart completeness without changing the astronomical provider family.

## 5. Extended-ephemeris lane

E2 live research established that Swiss-family calculations can produce Chiron and the four major asteroids and can be independently cross-checked against JPL Horizons, but the tested broad `5 arcsec / 1e-5 deg/day` global residual hypothesis was prospectively rejected at the far-future fixture. Therefore any production admission must choose a bounded epoch/object validation policy rather than asserting one universal residual threshold.

More importantly, the Swiss family introduces a separate licensing decision:

```text
research oracle use
!=
production dependency authorization
```

The current production dependency is MIT Astronomy Engine. Adding Swiss/pyswisseph is not an implementation detail; it changes provider provenance and license/deployment obligations and therefore requires explicit authority.

The same provider decision affects:

```text
Chiron
Ceres / Pallas / Juno / Vesta
Black Moon Lilith variants
potentially Vertex / Equatorial Ascendant if using Swiss houses output
```

A professional-license path and an AGPL-compatible deployment path are distinct production choices and must not be silently conflated.

## 6. Product-policy lane

Several extended capabilities can avoid a universal default by requiring explicit named selectors.

Recommended fail-closed architecture:

```text
bare Lilith
→ reject / require explicit mean|osculating|interpolated

house-ruler projection
→ require rulership-traditional-v1 or rulership-modern-v1

extended aspect generation
→ require explicit participant_policy_id

pattern generation
→ require participant_policy_id + aspect_policy_id + orb_policy_id + pattern_projection_policy_id
```

This reduces the number of product-default decisions and makes compatibility modes versionable.

However, if the user-facing product wants a one-click consumer-chart profile, then a compatibility profile itself becomes a policy object and needs explicit admission.

## 7. Decisions that cannot be derived from evidence alone

At this point, the remaining material decisions are:

### D1 — Extended ephemeris production strategy

The original E8 review framed D1 as `MIT_ONLY | SWISS_AGPL | SWISS_PROFESSIONAL`. Current ChatGPT-only research has shown that this is too coarse because runtime transport is itself a product constraint.

Current research decision surface:

```text
CURRENT_CORE_ONLY
  keep extended ephemeris unsupported.

LOCAL_ANALYTICAL
  project-owned deterministic formula/orbital model where independently validated.

BUNDLED_EPHEMERIS
  controlled build-time authoritative data
  → immutable compact local artifact
  → no mandatory runtime API.

EXTERNAL_RUNTIME
  JPL/SPICE/other provider only in environments with explicit external runtime capability;
  not sufficient as the ordinary ChatGPT-only path.

SWISS_AGPL
  optional Swiss production dependency under AGPL-compatible obligations.

SWISS_PROFESSIONAL
  optional Swiss production dependency under separately obtained professional license.
```

These are capability lanes and need not be mutually exclusive across object families. No production lane is selected yet. Current next research lanes are `LOCAL_ANALYTICAL` and `BUNDLED_EPHEMERIS`; see `CHATGPT_ONLY_EXTENDED_EPHEMERIS_FEASIBILITY.md`.

This review does not provide legal advice and does not select a production license/provider posture.

### D2 — Production policy activation style

Choose one product behavior:

```text
EXPLICIT_SELECTOR_ONLY
  no new universal defaults;
  callers request Lilith model / rulership / participant / pattern policies explicitly.

NAMED_COMPATIBILITY_PROFILE
  add one or more versioned profiles that select a bundle of explicit policies;
  profile contents must be evidence-backed and cannot claim exact 唐綺陽 compatibility
  until its unknown orb/pattern rules are independently established.
```

These two approaches can coexist, but admitting a default profile still requires an explicit product decision.

## 8. Recommended staged implementation if production expansion is authorized

Independent of D1, the safest order is:

```text
P1  E1 derived axes
P2  E4 Fortune + sect policy
P3  E7 named rulership projection(s)
P4  E5 named participant-policy plumbing while preserving current behavior
P5  E6 topology for aspects already admitted by the selected policy
P6  only after D1: extended provider objects / Lilith / additional special points
P7  only after evidence: consumer compatibility profile / stellium / exact pattern matching
```

Each production step should use a new provider/policy version or admission manifest update with regression tests; research completion alone must never mutate production authority.

## 9. E8 review conclusion

```text
E1 derived axes                     admission-ready candidate / current stack
Fortune + geometric-altitude sect   admission-ready candidate after implementation fixtures
rulership policy families           ready if explicit named policy selected
aspect participant architecture     ready if explicit named policy selected
pattern topology architecture       ready if explicit aspect/orb policy selected
E2 extended bodies                  historical provider/license block; bundled-ephemeris research now eligible
E3 Lilith variants                  historical provider/license block; Mean/Osculating local-analytical research now eligible
Vertex / Equatorial Ascendant       historical provider/formula block; project-owned geometry research now eligible
East Point alias                    compatibility-policy gated
exact 唐綺陽 pattern compatibility  unresolved / do not claim
production mutation                 NOT AUTHORIZED BY THIS REVIEW
```

The research sequence E0-E8 is now sufficient to ask only the material production decisions rather than reopening fact-definition research.
