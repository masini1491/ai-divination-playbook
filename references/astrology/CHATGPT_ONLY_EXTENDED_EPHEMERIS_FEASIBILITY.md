# Astrology ChatGPT-Only Extended Ephemeris Feasibility

Status: **REFERENCE-ONLY / RESEARCH EVIDENCE / NO PRODUCTION MUTATION AUTHORIZED**

Research baseline: `masini1491/ai-divination-playbook@65aa6b0f47a697c68474d62dacdfa140639bcb4d`

Purpose: determine whether extended Astrology facts can be made available to ordinary ChatGPT sessions without making Swiss Ephemeris or a live third-party API a mandatory runtime dependency.

## 1. Product constraint

The target product path is stricter than a normal Python application:

```text
fresh ChatGPT session
→ GitHub Connect exact-revision materialization
→ bounded local Python execution
→ deterministic Astrology facts
```

A live JPL Horizons HTTP call is useful for research/build-time evidence, but it is **not** a reliable ChatGPT-only production primitive. Therefore:

```text
build-time/research network access
!=
runtime network dependency
```

The preferred design is provider-neutral:

```text
source/oracle
→ validated project-owned or pinned artifact
→ local deterministic evaluator
→ Astrology Fact Bundle
```

## 2. GitHub reference implementations reviewed

The following repositories are design evidence only. Their code is not automatically production-admitted and must not be copied across incompatible license boundaries.

| Repository / pinned head | License | Relevant pattern | Product lesson |
|---|---|---|---|
| `TheDaniel166/moira@6dcc0fdaf35c16d96b544e03a509f2188603bc68` | MIT | JPL Horizons vectors are sampled at build/release time, rewritten into project-authored Type-13 SPK artifacts, then shipped locally with manifest/SHA-256/provenance | Strong evidence that live Horizons can be removed from runtime while preserving JPL trajectory provenance |
| `vedika-io/xalen-ephemeris@cc6edbec1f748ebdc4950ae6198f575c5ada73fa` | Apache-2.0 | analytical Mean/True Lilith; Keplerian asteroid elements; Chiron uses multi-epoch osculating elements because a single epoch drifts badly | Strong evidence for local formulas, but also evidence that naïve one-epoch Chiron propagation is too weak |
| `skyfielders/python-skyfield@d618ee9c0568492e00b9c7681dd334c00b74082f` | MIT | local JPL BSP/SPK evaluation and ephemeris excerpts | Evidence that local binary ephemeris evaluation is a mature architecture |
| `brandon-rhodes/python-jplephem@810ff57244f82bb55624aa201b4a9706419c4800` | MIT | standalone reader/evaluator for NASA SPICE SPK Chebyshev segments | Evidence that a small project-owned reader can evaluate local SPK without Swiss |
| `kefer-astrology/function-wrapper@0886c50a4215886d87c19ae69a7c76529c3f30f2` | AGPL-3.0 | vendors only five MPCORB rows (~KB) and locally propagates Chiron/Ceres/Pallas/Juno/Vesta; Mean/True Lilith computed locally | Architecture evidence only; AGPL code must not be copied into this project |
| `g-battaglia/libephemeris@37ffb0555b7a9f5083b4f1b6dc1a0f10feeb85fa` | AGPL-3.0 | SPK cache/download + strict fail-closed precision + optional compact binary ephemeris | Architecture evidence only; useful model for explicit precision tiers and no silent downgrade |

## 3. Small-body strategies

### A. Tiny orbital-element snapshot

Observed pattern:

```text
MPC/JPL elements snapshot
→ local Kepler propagation
→ geocentric reduction
```

Advantages:

- tiny transport, potentially KB-scale for five bodies;
- easy ChatGPT materialization;
- no live API.

Risks:

- perturbations make accuracy strongly date/body dependent;
- Chiron is especially unsuitable for a single fixed epoch. XALEN explicitly uses multi-epoch elements and still documents degree-class residuals over a bounded modern interval;
- current Playbook previously rejected a universal broad residual threshold for extended bodies.

Conclusion:

```text
GOOD as bounded fallback/research prototype
NOT sufficient for high-confidence production admission without prospective per-body/date validation
```

### B. Build-time JPL sampling → bundled local ephemeris

Moira provides the closest public precedent.

Observed artifact:

```text
JPL Horizons VECTORS
→ 10-day samples
→ project-authored DAF/SPK Type-13 interpolation
→ manifest + coverage + SHA-256 + NOTICE
→ local runtime
```

Its wheel catalog contains 25 named bodies across 1600–2500 in one ~46 MB shard. That is acceptable for a desktop/Python wheel but **too large for direct model-token transport**.

The important lesson is not the exact 46 MB artifact. It is the architecture:

```text
network only during controlled build
→ immutable versioned local artifact
→ runtime never calls Horizons
```

For this Playbook, a feasibility experiment should narrow all three dimensions:

```text
objects: Chiron + Ceres + Pallas + Juno + Vesta only
coverage: bounded consumer/natal window, not 1600–2500 by default
representation: evaluate compact Chebyshev/polynomial coefficients or query-bounded shards
```

A model-mediated transport target must be materially smaller than Moira's general-purpose wheel catalog.

### C. Local SPK with an MIT reader

Skyfield/jplephem demonstrate that local SPK evaluation is technically independent of Swiss.

Potential architecture:

```text
pinned small-body SPK or project-authored excerpt
+ MIT reader/evaluator
→ local geocentric vector
→ project-owned tropical longitude reduction
```

This is attractive for a normal application but ChatGPT cold-start still needs a byte-preserving way to materialize the binary artifact. A 10–50 MB kernel cannot be assumed safe for model-mediated JSON/token transport.

Therefore this lane is:

```text
TECHNICALLY VALID
CHATGPT-ONLY TRANSPORT NOT YET PROVEN
```

## 4. Lilith strategies

GitHub evidence materially changes the earlier assumption that every Lilith variant requires Swiss.

### Mean Lilith

Independent projects implement Mean Lilith analytically:

- Moira: IERS 2003 analytical mean lunar apogee;
- XALEN: analytical mean apogee;
- Kefer: mean-perigee polynomial + 180 degrees.

This makes a project-owned analytical implementation plausible.

Production still requires:

```text
explicit definition
→ authoritative formula source
→ frame/equinox policy
→ prospective fixtures
→ independent parity/oracle comparison
```

### Osculating / True Lilith

XALEN and Kefer both derive an instantaneous lunar apogee from Moon state vectors. This suggests a local implementation can reuse the admitted Astronomy Engine lunar state path or another independently admitted Moon state provider.

However osculating apogee is model-sensitive. Exact Swiss compatibility must not be claimed merely because a local osculating solution exists.

### Interpolated Lilith

Remains a separate compatibility definition. Do not collapse it into mean or osculating Lilith.

## 5. Vertex / Equatorial Ascendant

These remain better treated as project-owned spherical-astronomy derivations than as a reason to add a new ephemeris family.

Research lane:

```text
admitted date/time/location
+ sidereal time / obliquity / coordinate geometry
→ project-owned derived point
→ independent parity fixtures
```

No Swiss dependency should be presumed until formula/prospective validation is attempted.

## 6. License and provenance boundary

The reference implementations demonstrate architectures, not automatic license permission.

Rules for this project:

1. MIT / Apache reference code may still require attribution and independent review before reuse.
2. AGPL projects are **architecture evidence only** unless the project deliberately adopts a compatible license posture.
3. JPL/NAIF data provenance and kernel redistribution requirements remain separate from the evaluator library's software license.
4. A project-authored artifact generated from public trajectory samples must retain source, coverage, sampling/interpolation policy, checksums and non-endorsement/provenance notice.
5. No production license conclusion is made by this research document.

## 7. Revised D1 decision surface

The earlier three-way `MIT_ONLY | SWISS_AGPL | SWISS_PROFESSIONAL` decision is too coarse for a ChatGPT-only product.

Research options should instead be:

```text
CURRENT_CORE_ONLY
  no extended ephemeris production.

LOCAL_ANALYTICAL
  project-owned deterministic formulas / orbital models where evidence supports them.

BUNDLED_EPHEMERIS
  build-time authoritative data → compact immutable local artifact → no runtime API.

EXTERNAL_RUNTIME
  JPL/SPICE/other provider available only in environments with explicit external runtime capability.

SWISS_AGPL
  optional Swiss production dependency under AGPL-compatible obligations.

SWISS_PROFESSIONAL
  optional Swiss production dependency under separately obtained professional license.
```

These are capability lanes, not necessarily mutually exclusive. A likely architecture is object-specific:

```text
Mean Lilith
→ LOCAL_ANALYTICAL candidate

Osculating Lilith
→ LOCAL_ANALYTICAL candidate after lunar-state validation

Vertex / Equatorial Ascendant
→ LOCAL_ANALYTICAL / derived-geometry candidate

Chiron + Ceres/Pallas/Juno/Vesta
→ BUNDLED_EPHEMERIS feasibility first
→ bounded orbital-element fallback may be researched but not silently substituted

Swiss
→ optional compatibility/provider lane, not a mandatory foundation
```

## 8. Recommended experiments

### EXP-1 — Five-body compact ephemeris feasibility

Use JPL Horizons only as build/research authority.

Measure several representations over an explicitly bounded epoch:

```text
raw SPK excerpt
piecewise Chebyshev coefficients
sampled longitude/vector table + interpolation
multi-epoch osculating elements
```

For each object report:

```text
artifact bytes
maximum/p95 longitude residual
speed residual where relevant
coverage
worst fixture date
materialization/token cost
```

Do not set a tolerance after looking at results; prospectively declare candidate thresholds before each validation round.

### EXP-2 — Mean Lilith local analytical parity

Compare an independently implemented formula against multiple reference engines across a bounded modern window. Preserve exact definition and frame policy.

### EXP-3 — Osculating Lilith local state-vector parity

Use admitted Moon state vectors to derive instantaneous apogee. Validate separately from Mean Lilith; never alias the two.

### EXP-4 — Vertex / Equatorial Ascendant formula admission study

Implement only after pinning definition and reference formulas; compare synthetic and real geographic fixtures including latitude edge cases.

## 9. Current conclusion

```text
Swiss is NOT proven necessary for extended Astrology.

Live JPL API is NOT suitable as a mandatory ChatGPT-only runtime.

Best next research lane:
build-time authoritative data / local analytical formulas
→ compact, immutable, deterministic materialization
→ fail closed when the required artifact/definition is unavailable.

Production admission remains unchanged by this report.
```
