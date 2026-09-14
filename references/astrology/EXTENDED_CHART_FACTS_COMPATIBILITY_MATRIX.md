# Astrology Extended Chart Facts Compatibility Matrix｜擴充星盤事實相容性矩陣

Status: **REFERENCE-ONLY / RESEARCH / NOT PRODUCTION-ADMITTED**

Reviewed Playbook baseline: `masini1491/ai-divination-playbook@2b12a367049adb2f2bdaf48331c6b12d6c5eaf4c`

Architecture owner for this research slice: [`EXTENDED_CHART_FACTS_RESEARCH_ARCHITECTURE.md`](EXTENDED_CHART_FACTS_RESEARCH_ARCHITECTURE.md)

本矩陣用「完整 consumer natal chart 常見欄位」作功能 benchmark，對照目前 Astrology Production v1 與本輪外部 GitHub reference implementations。

矩陣只回答：

```text
能否表示 / 能否計算 / 有何定義歧義 / 可拿哪個來源做研究參考
```

它不授權 production adoption，也不宣告任何外部 astrology interpretation 為 canonical。

## 1. Reviewed revisions

| Source | Revision | Role |
|---|---|---|
| `masini1491/ai-divination-playbook` | `2b12a367049adb2f2bdaf48331c6b12d6c5eaf4c` | current production/research baseline |
| `cosinekitty/astronomy` | `865d3da7d8112bbc7911238052c6af4aaf877181` | admitted underlying astronomy dependency for current natal provider |
| `astrorigin/pyswisseph` | `91ec65631badc7faf4a4b913570c944a4c1b101d` | Swiss Ephemeris Python validation-oracle candidate |
| `g-battaglia/kerykeion` | `b18848eb8e1e0a2b09a096dbb9688c8404dfb06b` | extended object taxonomy / formulas / chart architecture reference |
| `theriftlab/immanuel-python` | `eba98099b7724598064113ffa1322e78dc4bccf6` | structured extended chart object / ephemeris mapping reference |
| `CruiserOne/Astrolog` | `5bf172ea231c4b6ea3d7e09ca307571354a41e8a` | aspect configuration / chart-pattern algorithm reference |
| `flatangle/flatlib` | `856d26b8bd1316ccdafe76399994696f9510de9e` | compact chart object API reference |

## 2. Capability legend

```text
YES              observed direct support or current project support
DERIVABLE        deterministic from already-available parent facts, but not currently emitted as a first-class production fact
REFERENCE        useful external reference implementation / taxonomy
PARTIAL          some required pieces exist, but current production path does not expose the complete feature
POLICY-GATED     calculation/classification depends on an explicit convention/policy identity
AMBIGUOUS        label is insufficient to identify a deterministic definition
NO               not currently supported in the relevant production path
N/A              not the source's intended responsibility
```

## 3. Object / point matrix

| Factor | Current Production v1 | pyswisseph / Swiss family | Kerykeion | Immanuel | Flatlib | Research classification |
|---|---|---|---|---|---|---|
| Sun–Pluto | YES | REFERENCE | YES | YES | YES | Core already admitted |
| North Node | YES, mean-node implementation in current provider | REFERENCE | Mean + True variants | Mean + True variants | YES | Definition provenance must remain explicit |
| South Node | DERIVABLE, not first-class emitted object | REFERENCE | YES, mean + true | YES | YES | E1 strong candidate |
| Ascendant | YES | REFERENCE | YES | YES | YES | Core already admitted |
| MC | YES | REFERENCE | YES | YES | YES | Core already admitted |
| Descendant | DERIVABLE, not first-class emitted object | REFERENCE | YES | YES | depends on chart abstraction | E1 strong candidate |
| IC / Imum Coeli | DERIVABLE, not first-class emitted object | REFERENCE | YES | YES | depends on chart abstraction | E1 strong candidate |
| Chiron | NO | REFERENCE | YES | YES | YES | E2 ephemeris-required |
| Ceres | NO | REFERENCE | YES | YES | not primary target | E2 ephemeris-required |
| Pallas | NO | REFERENCE | YES | YES | not primary target | E2 ephemeris-required |
| Juno | NO | REFERENCE | YES | YES | not primary target | E2 ephemeris-required |
| Vesta | NO | REFERENCE | YES | YES | not primary target | E2 ephemeris-required |
| Mean Black Moon Lilith | NO | REFERENCE | YES | YES | not primary target | E3 explicit identity required |
| True / Osculating Black Moon Lilith | NO | REFERENCE | YES | YES / variant support observed | not primary target | E3 explicit identity required |
| Part of Fortune | NO | formula/oracle reference possible | YES, day/night formula | YES | not primary target | E4 POLICY-GATED L2 derivation |
| Vertex | NO | calculation oracle candidate | YES | YES | not primary target | E4 time/location-sensitive |
| East Point / Equatorial Ascendant | NO | oracle candidate | terminology/coverage must be confirmed per implementation | terminology/coverage must be confirmed | not primary target | E4 AMBIGUOUS until exact identity matched |

## 4. Formula / identity notes

### 4.1 Nodes

Current production provider uses a mean-node model for `NorthNode`.

Future first-class South Node support should therefore not expose a generic node pair without provenance. Prefer：

```text
MeanNorthNode ↔ MeanSouthNode
TrueNorthNode ↔ TrueSouthNode
```

or an equivalent explicit field such as `node_definition = mean | true`.

### 4.2 Lilith

Reviewed Kerykeion distinguishes：

```text
Mean_Lilith
True_Lilith
```

Reviewed Immanuel likewise exposes multiple Lilith identities in its chart constants/settings surface.

Therefore a consumer value labelled only `Lilith` is not sufficient evidence for a production mapping.

Minimum compatibility test：

```text
consumer longitude
vs mean candidate
vs true/osculating candidate
→ identify matching definition within documented tolerance
```

If neither matches, classification remains `UNRESOLVED`.

### 4.3 Part of Fortune

Reviewed Kerykeion documents a day/night formula family：

```text
Day   = Asc + Moon - Sun
Night = Asc + Sun - Moon
```

This is useful compatibility evidence, not yet project policy authority.

Future fixture must prove：

1. day/night classification；
2. source longitudes used；
3. normalized final longitude；
4. agreement with at least one independent oracle/reference；
5. policy identity preserved in the emitted fact。

### 4.4 Vertex

Vertex must be tested across multiple latitudes / longitudes / times, not accepted from one matching chart.

Suggested fixture set：

```text
mid-latitude north
mid-latitude south
equatorial
near-boundary high latitude where provider behavior remains defined
```

### 4.5 East Point

Do not admit `EastPoint` until the source's exact mathematical definition is frozen.

Candidate test procedure：

```text
consumer "East Point" longitude
→ compare against Equatorial Ascendant candidate
→ compare against any alternate documented candidate
→ only alias when repeatable across multiple fixtures
```

## 5. Aspect participation matrix

Current Production v1 has a major-aspect policy, but the natal provider's practical aspect participant universe is narrower than a comprehensive consumer chart.

| Participant class | Object can exist in current Production v1? | Participates in current provider natal aspect generation? | Future research need |
|---|---:|---:|---|
| Sun–Pluto planets | YES | YES | retain |
| North Node | YES | YES | preserve node-definition provenance |
| Ascendant | YES | NO | E5 |
| MC | YES | NO | E5 |
| Descendant | not first-class | NO | E5 after E1 |
| IC | not first-class | NO | E5 after E1 |
| Chiron | NO | NO | E5 after E2 |
| Ceres/Pallas/Juno/Vesta | NO | NO | E5 after E2 |
| Lilith | NO | NO | E5 after E3 |
| Fortune | NO | NO | E5 after E4 |
| Vertex | NO | NO | E5 after E4 |
| Equatorial Ascendant | NO | NO | E5 after E4 |

Future architecture should not solve this by replacing one hard-coded body list with a larger hard-coded body list.

Prefer：

```text
all available chart objects
→ aspect_participant_policy
→ eligible set
→ pair geometry
```

## 6. Pattern / topology matrix

| Pattern | Current Production v1 | Astrolog 8.00 observed reference | Research disposition |
|---|---|---|---|
| Stellium-3 | NO | YES | E6 |
| Stellium-4 | NO | YES | E6 |
| Grand Trine | NO | YES | E6 |
| T-Square | NO | YES | E6 |
| Grand Cross | NO | YES | E6 |
| Yod | NO | YES | E6, requires quincunx policy not in current major-only Production v1 |
| Cradle | NO | YES | later E6 candidate |
| Rectangle | NO | YES | later E6 candidate |
| consumer localized triangle labels | NO | N/A | reconstruct topology before naming/mapping |

### Important separation

Astrolog's existence proves useful implementation precedent, not project authority.

Future project detector should be independently specified from graph constraints, then validated against one or more reference implementations / fixtures.

## 7. Rulership / house-ruler matrix

| Capability | Current Production v1 | Research status |
|---|---|---|
| house cusp sign | YES | L2 available |
| planet sign | YES | L2 available |
| planet house | YES | L2 available |
| traditional sign ruler lookup | research evidence exists, not a universal raw fact | POLICY-GATED L3 |
| modern outer-planet ruler lookup | not project-wide default | POLICY-GATED L3 |
| house → ruler → ruler sign | not a first-class production projection | E7 |
| house → ruler → ruler house | not a first-class production projection | E7 |
| simultaneous traditional + modern views | not current production feature | preferred comparison architecture |

Recommended future representation：

```text
RulershipProjection
- policy_id
- policy_version
- house_number
- cusp_sign
- ruler_object_id
- ruler_sign_fact_ref
- ruler_house_fact_ref
```

No one unlabeled `house_ruler` field should hide which rulership system was used.

## 8. Source suitability matrix

| Source | Numerical oracle value | Architecture value | Pattern value | Direct-copy suitability | Main caveat |
|---|---:|---:|---:|---:|---|
| Astronomy Engine | HIGH for current admitted core | HIGH | LOW | existing bounded production dependency | extended astrology objects not all covered |
| pyswisseph / Swiss Ephemeris | VERY HIGH | MEDIUM | LOW | LOW without separate licensing decision | AGPL / Professional License boundary |
| Kerykeion | HIGH as consumer-style cross-check | VERY HIGH | MEDIUM | LOW | AGPL-3.0; package conventions are not project policy |
| Immanuel | HIGH as Swiss-family cross-check | VERY HIGH | evolving / reference | LOW | AGPL-3.0; interpretation/weighting assumptions must not leak |
| Astrolog 8.00 | HIGH for legacy-style chart behavior checks | MEDIUM | VERY HIGH | LOW | GPL/Swiss licensing surfaces; old/new conventions need explicit mapping |
| Flatlib | MEDIUM | HIGH for simple Python API ideas | LOW | MEDIUM for wrapper ideas only | MIT wrapper still depends on pyswisseph |

## 9. Proposed compatibility fixture schema

A future research fixture should look conceptually like：

```json
{
  "fixture_id": "synthetic-extended-chart-001",
  "input": {
    "utc": "...",
    "latitude": 0.0,
    "longitude": 0.0
  },
  "configuration": {
    "zodiac_system": "tropical",
    "center": "geocentric",
    "house_system": "Placidus",
    "node_definition": "mean",
    "lilith_definition": "mean",
    "lot_policy_id": "candidate-fortune-day-night-v1"
  },
  "expected": {
    "objects": [],
    "angles": [],
    "lots": [],
    "patterns": []
  },
  "oracles": []
}
```

This is a research shape only; it is not a production schema proposal yet.

## 10. Tolerance strategy

Do not define one global tolerance for every fact.

Separate at least：

```text
planet / asteroid longitude tolerance
node longitude tolerance by definition
angle tolerance
Vertex / Equatorial Ascendant tolerance
house cusp tolerance
formula-derived-point exact arithmetic tolerance
pattern boundary tolerance inherited from explicit orb policy
```

A result just outside tolerance must first be checked for definition/config mismatch before being classified as calculation defect.

## 11. Privacy-safe consumer compatibility workflow

When comparing against a real person's exported chart：

```text
real chart remains outside public repository
→ extract only non-identifying compatibility observations
→ synthetic/public regression reproduces the rule where possible
→ commit rule/evidence, not private birth data
```

Acceptable committed statement example：

```text
"A private Placidus compatibility check matched the day/night Fortune formula; no identifying input retained."
```

Not acceptable：

```text
full birth date + exact time + birthplace + complete chart fixture
```

## 12. Gap priority

### P0 — deterministic object coverage

```text
South Node
Descendant
IC
Chiron
Ceres / Pallas / Juno / Vesta
Lilith identity
Fortune
Vertex
Equatorial Ascendant identity
```

### P0 — aspect universe architecture

```text
angles / nodes / asteroids / points as explicit policy-controlled participants
```

### P1 — topology / pattern engine

```text
Stellium
Grand Trine
T-Square
Grand Cross
then Yod / Cradle / Rectangle if scope warrants
```

### P1 — rulership projections

```text
traditional view
modern view
no silent blending
```

### P2 — interpretation evidence

Only after L1/L2/L3 identities are stable should the project expand L4 interpretation claims for Chiron, asteroids, Lilith, Vertex, Lots or patterns.

## 13. Exit criteria for research phase

This compatibility research is ready for a separate production-admission review only when：

```text
all P0 object identities are explicit
+ licenses are documented
+ independent fixtures exist
+ tolerance policy exists
+ aspect participant policy is explicit
+ pattern definitions are machine-testable
+ rulership policy split is explicit
+ private consumer data is not required for regressions
```

Until then：

**REFERENCE-ONLY / NOT PRODUCTION-ADMITTED**
