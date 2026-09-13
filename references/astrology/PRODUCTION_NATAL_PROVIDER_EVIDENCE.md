# Astrology Production Natal Provider Evidence

Status: **PRODUCTION-PROVIDER EVIDENCE / NOT INTERPRETATION AUTHORITY**

Baseline before provider admission:

`masini1491/ai-divination-playbook@09d2a014190b59a5a758c9a0618b06e72a82aecb`

## Decision

Astrology Production v1 admits a bounded natal calculation provider:

```text
provider_id: astronomy-engine-natal-v1
runtime owner: tools/astrology_provider.py
output: astrology_fact_bundle@1.0.0
scope: natal only
```

It does not change ordinary method routing and does not admit a transit event-search engine.

## Why Astronomy Engine

Reviewed source:

```text
cosinekitty/astronomy
revision: 865d3da7d8112bbc7911238052c6af4aaf877181
Python package: astronomy-engine 2.1.19
license: MIT
```

The upstream repository supplies deterministic Sun/Moon/planet astronomy under a permissive MIT license. Production pins the Python package version and records the reviewed source revision in provider provenance.

This avoids silently binding the Playbook to Swiss Ephemeris / `pyswisseph`, whose dual-license and ephemeris-asset boundaries remain materially different.

No Astronomy Engine source file is vendored into this repository. It remains an external pinned dependency installed through `requirements-astrology-provider.txt`.

## Astrology-specific derived calculations

Astronomy Engine does not own astrology house systems. The project provider therefore owns:

- tropical sign projection;
- mean obliquity used by the house calculation;
- local sidereal-time → RAMC;
- Ascendant / Midheaven geometry;
- Whole Sign house cusps and placements;
- bounded Placidus cusp iteration and placements;
- major-aspect geometry under the existing production orb policy;
- finite-difference apparent motion state;
- mean North Node calculation;
- Fact Bundle construction / provenance.

## Placidus reference

Reviewed permissive reference:

```text
kounkt/tri-horoscope
revision: 11318426c52c222eea108583ca45420c864825ca
path: src/natal_v0.py
license: MIT
```

The provider uses a bounded adaptation of the reviewed ASC/MC and Placidus iteration approach. It does not import the project wholesale and does not adopt its BaZi/Vedic surfaces.

Production additionally tightens the reference behavior:

- no silent `asin` clamping when geometry is outside the admitted domain;
- fail closed if Placidus iteration cannot converge;
- conservative `|latitude| > 66°` rejection for Production v1;
- IANA timezone required instead of fixed-offset-only identity;
- ambiguous/nonexistent DST wall times fail closed;
- unknown birth time is not replaced by noon.

## Cross-implementation fixture

Regression fixture:

`tests/fixtures/astrology_provider_sydney_1990.json`

Source provenance:

```text
kounkt/tri-horoscope@11318426c52c222eea108583ca45420c864825ca
path: tests/E1_south_sydney.json
license: MIT
```

Only the minimum Western deterministic values needed for regression are retained:

- input date/time/coordinates;
- ASC / MC;
- selected/all natal body longitudes;
- key Placidus cusps;
- house placements.

The BaZi portion is not copied.

Acceptance tolerance for numeric parity:

```text
0.0167° ≈ 1 arcminute
```

The fixture proves parity with the reviewed reference implementation at that bounded input; it does not establish universal astronomical accuracy by itself.

## Time input contract

Production provider requires:

```text
local_datetime: naive ISO local wall time
timezone_name: IANA timezone
latitude / longitude: explicit decimal coordinates
birth_time_certainty: exact | approximate
```

The provider intentionally does not geocode city names. Location-name resolution is a separate capability and must not become a hidden network/default dependency inside deterministic calculation.

## Unknown time

The direct raw-birth-data provider does not accept `birth_time_certainty=unknown`.

Reason: research already demonstrated that houses / angles are time-sensitive and that local-noon substitution must not masquerade as an exact chart. Unknown-time users may still supply a structured fact set with the appropriate uncertainty boundary through the existing Fact Bundle path.

## Provider / runtime separation

```text
raw birth data
→ tools/astrology_provider.py      # calculation
→ Astrology Fact Bundle 1.0
→ tools/astrology_runtime.py       # admission validation
→ ASTROLOGY.md                     # interpretation
```

Provider output never bypasses the runtime gate.

## Not admitted in this round

- geocoding;
- transit event search / station search / ingress search;
- synastry / composite / solar return;
- rectification;
- sidereal zodiac;
- topocentric planet positions;
- unknown-time noon substitution;
- Placidus beyond the Production v1 latitude boundary;
- any scientific or predictive-validity claim.
