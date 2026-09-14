# Astrology Extended Chart Facts Research Architecture｜擴充星盤事實研究架構

Status: **REFERENCE-ONLY / RESEARCH / NOT PRODUCTION-ADMITTED**

Reviewed Playbook baseline: `masini1491/ai-divination-playbook@2b12a367049adb2f2bdaf48331c6b12d6c5eaf4c`

本檔延伸既有 [`EVIDENCE_ARCHITECTURE.md`](EVIDENCE_ARCHITECTURE.md)，研究目前 Astrology Production v1 尚未涵蓋、但常見於完整西洋本命盤輸出的 extended chart facts。

本研究只建立 evidence/source architecture、identity boundary、compatibility target 與 future admission gate；**不修改** production provider、runtime schema、selector、routing、orb policy 或 interpretation authority。

## 1. Research objective

目前 Production v1 已能處理 bounded natal / transit core：

```text
Sun .. Pluto
North Node
Ascendant / MC
Whole Sign / Placidus houses
house placement
retrograde / speed
major aspects
```

完整 consumer chart 常額外輸出：

```text
South Node
Descendant / IC
Chiron
Ceres / Pallas / Juno / Vesta
Black Moon Lilith
Part of Fortune
Vertex
East Point / Equatorial Ascendant
extended angle / point aspects
stellium / T-square / Grand Cross / Grand Trine / other patterns
house-ruler → ruler sign / house projection
```

研究目標不是照抄任何單一網站，而是把這些欄位拆成可追溯、可版本化、可 fail-closed 的 fact / policy families。

## 2. Authority boundary

Canonical layer separation remains:

```text
L0 input / provenance
→ L1 astronomical or ephemeris-defined fact
→ L2 deterministic chart derivation / geometry
→ L3 explicit astrology policy / classification projection
→ L4 sourced interpretation claim
→ L5 synthesis
```

Extended facts 不得因「某個 astrology package 有輸出」就跳過 layer boundary。

尤其禁止：

```text
external package output
→ copy field semantics
→ silently declare production fact
```

以及：

```text
can calculate point
→ therefore its symbolic interpretation is admitted
```

## 3. Candidate fact families

### 3.1 Axial derived points

Candidate deterministic derivations：

```text
South Node = selected North Node definition + 180°
Descendant = Ascendant + 180°
Imum Coeli = MC + 180°
```

Required provenance：

- North Node identity must preserve `mean` vs `true` when material；
- angle derivation must preserve chart time/location/configuration identity；
- normalized longitude must be explicit in `[0, 360)`。

These are strong candidates for L2 derived facts because they do not require interpretive doctrine once the source fact identity is fixed.

### 3.2 Ephemeris-required bodies / points

Candidate extended object set：

```text
Chiron
Ceres
Pallas
Juno
Vesta
```

These require an admitted astronomical/ephemeris calculation path. They must not be approximated from language-model memory or copied from an unrelated chart calculator without provenance.

Candidate object identity fields：

```text
object_id
object_type
calculation_authority
longitude_deg
latitude_deg when available
speed_deg_per_day when available
motion
sign placement
house placement when houses are admitted
availability
```

### 3.3 Black Moon Lilith identity

`Lilith` is not a sufficient deterministic identifier.

At minimum preserve distinct definitions such as:

```text
Mean Black Moon Lilith
True / Osculating Black Moon Lilith
```

Research rule：

> A consumer export labelled only `Lilith` is ambiguous until its calculation definition is identified or independently matched against a pinned oracle.

No future production fact should collapse mean and true definitions into one unqualified `Lilith` object.

### 3.4 Part of Fortune / Lots

Part of Fortune is a deterministic derived point only after an explicit formula policy is fixed.

Common day/night formula family observed in reviewed implementations：

```text
diurnal:   Asc + Moon - Sun
nocturnal: Asc + Sun - Moon
```

Research requirements：

- preserve `lot_policy_id` / formula identity；
- preserve day/night determination inputs；
- normalize resulting longitude；
- do not generalize one project's additional Lots into project-wide authority；
- interpretation of Fortune remains L3/L4, not part of this L2 formula admission.

### 3.5 Vertex

Vertex is location/time sensitive and must not be inferred from sign-only data.

Candidate fact requirements：

```text
explicit birth/event time
coordinates
calculation definition / provider
longitude
availability
```

Cross-engine validation is required before any production admission.

### 3.6 East Point / Equatorial Ascendant

Consumer astrology terminology is not sufficiently stable to treat `East Point` as a universal machine identifier.

Candidate canonical research identity：

```text
EquatorialAscendant
aliases: ["East Point"]  # only when source definition is confirmed compatible
```

Research must distinguish this from ordinary Ascendant and from any package-specific similarly named point.

### 3.7 Angles as aspect participants

Current Production v1 calculates Ascendant / MC but its bounded natal aspect universe is narrower than a comprehensive consumer chart.

Future research should separate：

```text
object existence
→ raw pair angular separation
→ aspect candidate geometry
→ policy-admitted aspect
```

Candidate aspect participant classes：

```text
planet
node
asteroid / centaur
lot / calculated point
angle
special point
```

Whether each class participates in a displayed aspect is a policy decision and must be explicit rather than inherited from an external package default.

## 4. Pattern / configuration architecture

A chart pattern is not just another single pair aspect.

Candidate pipeline：

```text
eligible chart objects
→ pairwise angular geometry
→ aspect candidate graph
→ explicit orb / aspect-admission policy
→ policy-qualified aspect graph
→ topology detector
→ pattern projection
```

Candidate research pattern families：

```text
Stellium
Grand Trine
T-Square
Grand Cross
Yod
Cradle
Rectangle
```

Classification boundary：

- raw longitudes / separations = L1/L2；
- graph edges admitted under named orb/aspect policy = L3 policy projection；
- `T-Square`, `Grand Cross`, `Stellium` classification = deterministic **given** that named policy, therefore preserve the policy id in the resulting projection；
- symbolic meaning of a pattern = L4 only when separately sourced/admitted。

### 4.1 Pattern identity requirements

A future `ChartPatternProjection` candidate should preserve：

```text
pattern_id
pattern_type
participant_refs[]
edge_refs[]
policy_id
policy_version
orb_summary
completeness / ambiguity
source_algorithm_reference when used for validation only
```

Do not infer a pattern from labels copied out of a consumer report when the underlying object positions / aspect edges are unavailable.

### 4.2 Consumer labels are compatibility evidence, not canonical taxonomy

A consumer export may use a localized label that does not map one-to-one to the project's eventual pattern taxonomy.

Therefore：

```text
consumer label
→ observed compatibility label
→ topology reconstruction
→ canonical mapping only after evidence
```

Unknown labels remain unresolved rather than guessed.

## 5. House-ruler projection architecture

A table like：

```text
house cusp sign
→ ruler
→ ruler sign
→ ruler house
```

is not pure astronomy because rulership can differ by tradition.

Candidate L3 policy split：

```text
rulership-traditional-v1
rulership-modern-v1
```

Example conflict family：

```text
Scorpio  → Mars | Pluto
Aquarius → Saturn | Uranus
Pisces   → Jupiter | Neptune
```

A future projection must preserve：

```text
house_number
cusp_sign
rulership_policy_id
ruler_object_id
ruler_sign
ruler_house
fact_refs[]
```

No production implementation should silently mix traditional and modern rulers in the same unresolved table.

## 6. Reviewed external reference roles

The following immutable revisions were reviewed for this bounded extended-facts research.

| Source | Reviewed revision | Useful role | Authority here |
|---|---|---|---|
| `cosinekitty/astronomy` | `865d3da7d8112bbc7911238052c6af4aaf877181` | existing permissive astronomy baseline already used by Production v1 | existing production dependency only within current admission; no new extended-fact authority |
| `astrorigin/pyswisseph` | `91ec65631badc7faf4a4b913570c944a4c1b101d` | Swiss Ephemeris Python interface; asteroid / extended ephemeris oracle candidate | REFERENCE-ONLY / validation oracle candidate |
| `g-battaglia/kerykeion` | `b18848eb8e1e0a2b09a096dbb9688c8404dfb06b` | broad object taxonomy: nodes, angles, Chiron, major asteroids, mean/true Lilith, Vertex, Lots | REFERENCE-ONLY architecture / compatibility reference |
| `theriftlab/immanuel-python` | `eba98099b7724598064113ffa1322e78dc4bccf6` | structured extended chart objects and Swiss-Ephemeris mapping | REFERENCE-ONLY architecture / cross-check reference |
| `CruiserOne/Astrolog` | `5bf172ea231c4b6ea3d7e09ca307571354a41e8a` | explicit aspect-configuration / topology implementation including Stellium, Grand Trine, T-Square, Yod, Grand Cross | REFERENCE-ONLY pattern-algorithm reference |
| `flatangle/flatlib` | `856d26b8bd1316ccdafe76399994696f9510de9e` | compact Python chart/object abstraction; Chiron and node modeling | REFERENCE-ONLY API-design reference |

Detailed field-by-field comparison is in [`EXTENDED_CHART_FACTS_COMPATIBILITY_MATRIX.md`](EXTENDED_CHART_FACTS_COMPATIBILITY_MATRIX.md).

## 7. License / reuse boundary

### 7.1 Swiss Ephemeris family

Reviewed `pyswisseph` identifies AGPL-3.0 and the underlying Swiss Ephemeris dual-license boundary.

Research posture：

```text
allowed here: read behavior / API / output / tests as evidence
allowed here: use as independent validation oracle in a controlled research environment
not granted here: copy implementation into current production runtime
not granted here: add dependency without explicit license/admission review
```

### 7.2 Kerykeion / Immanuel

Reviewed repositories are AGPL-3.0-family codebases.

Use them for：

- object taxonomy ideas；
- field-family comparison；
- independent expected-output generation where legally/configurationally appropriate；
- test-case design concepts。

Do not copy source implementation into a permissive production component without a separate legal/admission decision.

### 7.3 Astrolog

Reviewed Astrolog 8.00 source provides valuable aspect-configuration examples, but its repository contains GPL and Swiss-Ephemeris-related licensing surfaces.

Research posture：independent reimplementation from documented topology requirements + black-box / fixture comparison is preferred over source copying.

### 7.4 Flatlib

Flatlib's own repository license is MIT, but the reviewed runtime requirement includes `pyswisseph`.

Therefore：

> permissive wrapper license does not erase the dependency's separate license boundary.

## 8. Validation strategy

### 8.1 No private golden fixture in public repository

This public Playbook must not store a real person's identifying birth date + exact time + birthplace combination.

Use：

- synthetic fixtures；
- public/historical fixtures whose reuse is justified；
- locally held private compatibility checks whose raw identifying input is not committed。

A user-supplied commercial chart export may be used interactively as compatibility evidence, but its identifying data must not become repository fixture material.

### 8.2 Cross-engine fixture dimensions

Each fixture should explicitly pin：

```text
UTC instant
coordinates
zodiac system
ephemeris / center configuration
house system
node definition
Lilith definition when tested
object set
lot formula policy
aspect set / orb policy when testing patterns
```

### 8.3 Comparison result classes

For each field：

```text
MATCH_WITHIN_TOLERANCE
EXPECTED_DEFINITION_DIFFERENCE
CONFIGURATION_MISMATCH
SOURCE_LABEL_AMBIGUOUS
ENGINE_CAPABILITY_GAP
IMPLEMENTATION_DEFECT_CANDIDATE
UNRESOLVED
```

Do not reduce every difference to a numeric tolerance problem.

## 9. Proposed research sequence

```text
Phase E0 — source / identity freeze
Phase E1 — axial derived facts: South Node / DSC / IC
Phase E2 — extended ephemeris objects: Chiron + Ceres/Pallas/Juno/Vesta
Phase E3 — Lilith definition comparison
Phase E4 — Fortune / Vertex / Equatorial Ascendant derivation comparison
Phase E5 — expanded aspect participant graph
Phase E6 — pattern topology detector research
Phase E7 — traditional vs modern rulership projections
Phase E8 — production-admission review, if separately authorized
```

Each phase should produce evidence before the next phase receives authority.

## 10. Minimum production-admission gates

No extended fact becomes Production v1/v1.x merely because this research file exists.

At minimum require：

1. exact semantic identity for every proposed object；
2. calculation authority identified；
3. license boundary resolved；
4. deterministic fixtures；
5. independent cross-engine or formula validation where feasible；
6. numeric tolerance documented；
7. unknown-time/location sensitivity documented；
8. schema/runtime representation decided；
9. selector and unsupported-factor behavior updated；
10. production regression coverage；
11. explicit manifest / method-owner admission；
12. no interpretation promotion without separate L3/L4 evidence。

## 11. Current conclusion

Current Production v1 core should remain unchanged during this research.

The evidence supports a future bounded extended-chart layer, but the safest architecture is：

```text
existing Astronomy Engine production core
+ project-owned deterministic derivations where formulas are unambiguous
+ independently validated extended ephemeris adapter only where needed
+ explicit aspect-participant policy
+ explicit pattern policy
+ explicit rulership policy
```

rather than replacing the existing production provider wholesale with a feature-rich external astrology package.
