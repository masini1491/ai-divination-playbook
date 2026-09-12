# Astrology Source Registry｜占星來源登錄

Status: **REFERENCE-ONLY / RESEARCH｜僅供參考／研究中**

Reviewed Playbook baseline: `masini1491/ai-divination-playbook@6bd58ea5bb61849c2464f4e485bc4f7917f64862`

本檔記錄第一輪 Astrology external GitHub source 的 immutable reviewed revision、license evidence、可借鑑範圍與 not-adopted boundary。所有來源均只取得 reference authority；不因收錄而取得本 Playbook 的 production policy authority。

## 1. Source table

| Source | Reviewed revision | Role in research | License / legal note | Current status |
|---|---|---|---|---|
| `aloistr/swisseph` | `91339e55d2351f32548d8a8d5bca6aa93b4f6da7` | ephemeris / astronomical calculation reference | dual-license: AGPL or Swiss Ephemeris Professional License | REFERENCE-ONLY |
| `theriftlab/immanuel-python` | `46190726ebe012f43c93d163745682e806975759` | structured chart-data model / serialization reference | AGPL-3.0 | REFERENCE-ONLY |
| `wvanderen/astrology-skill` | `a9339b3c7151313530aa5002572c6612a2cfd59f` | retrieval-first interpretation architecture / no-calculation boundary | root runtime MIT; optional Swiss-Ephemeris-based calculator separately AGPL | REFERENCE-ONLY |
| `Shoresh613/astro-script` | `18f4a3e291a557b2ef47c7fb5e27b108f1bcf4b7` | transit / timing / unknown-time degradation patterns | README claims MIT, but referenced `LICENSE.md` is absent at reviewed revision; treat license as unresolved | REFERENCE-ONLY |
| `kounkt/tri-horoscope` | `11318426c52c222eea108583ca45420c864825ca` | MIT alternative deterministic chart engine; fact/interpretation separation | MIT | REFERENCE-ONLY |
| `cosinekitty/astronomy` | `865d3da7d8112bbc7911238052c6af4aaf877181` | lower-level astronomy engine / independent deterministic astronomy reference | MIT | REFERENCE-ONLY |

## 2. `aloistr/swisseph`

### Observed evidence

Reviewed README states Swiss Ephemeris is a programmer toolbox for astrological software, uses high-precision astronomical data based on NASA JPL, and that as of 14 April 2026 the `.se1` planetary and asteroid data files were rebuilt with JPL DE441.

Reviewed license file explicitly defines a dual-license choice:

- GNU AGPL; or
- Swiss Ephemeris Professional License.

### Useful research contribution

- candidate high-precision ephemeris authority;
- explicit provenance for planetary positions;
- reference for separating astronomical calculation from later interpretation.

### Not adopted

- no Swiss Ephemeris source code is copied into this Playbook;
- no `.se1` data files are vendored here;
- no conclusion is made yet that Swiss Ephemeris should become the production engine;
- AGPL / professional-license consequences remain an explicit architecture constraint.

## 3. `theriftlab/immanuel-python`

### Observed evidence

README describes chart-centric structured data including planets, points, signs, houses, aspects, weightings, natal, solar-return, progressed, composite and cross-chart aspects. It shows serialization of a chart object into JSON-like structured facts including longitude, sign, house, movement and dignities.

Repository license is AGPL-3.0.

### Useful research contribution

- evidence that Astrology facts can be represented as explicit structured data instead of prose;
- concrete candidate field families for a future source-neutral `Structured Astrology Fact`;
- example of natal / return / progression / composite separation.

### Not adopted

- its schema is not yet canonical here;
- its dignity, weighting or interpretation assumptions are not automatically accepted;
- no direct dependency is added.

## 4. `wvanderen/astrology-skill`

### Observed evidence

README explicitly describes a retrieval-first interpretation skill whose preferred input is already-calculated chart data. It enforces a no-calculation boundary: raw birth data may optionally be converted to chart JSON by a separate support script; routing / interpretation consume the calculated output and do not freehand missing chart factors.

The root license is MIT. `tools/NOTICE.md` separately documents that its optional `pyswisseph` birth-data calculator is AGPL-3.0 because of Swiss Ephemeris dependency.

### Useful research contribution

- strong architectural precedent for:
  - deterministic calculation boundary;
  - structured chart input;
  - retrieval-only interpretation modules;
  - separation of permissive interpretation runtime from copyleft calculator unit.

### Not adopted

- its `SKILL.md` is not a canonical owner for this Playbook;
- its interpretive corpus is not imported wholesale;
- its claim that process separation confines AGPL is treated as that project's architecture statement, not as legal advice for this repository.

## 5. `Shoresh613/astro-script`

### Observed evidence

README documents:

- planetary / house / aspect calculations;
- tropical and sidereal modes;
- exact aspect-period search;
- natal-transit conditions;
- retrograde, zodiac-sign, transit-house, VOC Moon and planetary-hour conditions;
- structured event search;
- an explicit unknown-birth-time behavior: planetary positions may still be represented using a defined fallback, while house-, cusp- and angle-dependent conditions are rejected.

The README says the project is MIT and points to `LICENSE.md`, but `LICENSE.md` is not present at the reviewed revision. Therefore the license claim is **not treated as fully verified**.

### Useful research contribution

- transit-search and timing-window decomposition;
- fail-closed behavior for time-sensitive facts;
- distinction between current transit houses and natal houses;
- explicit condition objects rather than prose-only timing claims.

### Not adopted

- no activity scoring / `0-100` opportunity score is accepted as a validated astrological rule;
- no preset electional rules are promoted;
- license-sensitive reuse is blocked until the license discrepancy is resolved.

## 6. `kounkt/tri-horoscope`

### Observed evidence

README describes a deterministic natal chart computation library that intentionally excludes interpretation and prose. Western output includes tropical positions, Placidus houses, Ascendant, Midheaven, bodies, nodes, house placements and aspects. It also provides explicit behavior for unknown birth time and a fixture-based regression suite.

Repository license is MIT. The project states it uses `astronomy-engine` rather than Swiss Ephemeris.

### Useful research contribution

- permissive-license calculation candidate;
- clean fact-only responsibility boundary;
- test-fixture pattern for boundary conditions such as high latitude and unknown birth time;
- useful comparison target against Swiss-Ephemeris-based implementations.

### Not adopted

- its 1-arc-minute tolerance and fixture claims are not independently validated here yet;
- its specific house / node / aspect implementation is not canonical;
- Vedic and BaZi capabilities are outside the immediate Western Astrology research scope unless separately admitted later.

## 7. `cosinekitty/astronomy`

### Observed evidence

README describes Astronomy Engine as a multi-language deterministic astronomy library for Sun, Moon and planetary positions plus astronomical events. It states a design target of approximately ±1 arcminute and describes validation against NOVAS, JPL Horizons and other sources.

Repository license is MIT.

### Useful research contribution

- independent lower-level astronomy engine candidate;
- useful for separating astronomical coordinates from astrology-specific house / aspect / interpretation logic;
- candidate basis for cross-engine validation.

### Not adopted

- Astronomy Engine alone is not an astrology engine;
- house systems, astrology aspects, zodiac-mode conventions and interpretation remain separate responsibilities;
- its accuracy statements are source claims until reproduced in our own validation context.

## 8. Current source-selection implication

The first-round evidence supports comparing at least two deterministic architecture families:

```text
A. Swiss-Ephemeris family
Swiss Ephemeris
→ chart wrapper / schema
→ Structured Astrology Fact

B. permissive astronomy family
Astronomy Engine
→ astrology-specific derived calculations
→ Structured Astrology Fact
```

No engine has been selected. The next research step should be a bounded comparison on a small set of synthetic / public test inputs, with explicit configuration parity and no private birth data committed to the repository.
