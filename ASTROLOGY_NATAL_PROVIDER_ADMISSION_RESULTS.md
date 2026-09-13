# Astrology Natal Provider Admission Results

Status: **PRODUCTION PROVIDER ADMISSION EVIDENCE**

## Identity

Repository:

`masini1491/ai-divination-playbook`

Baseline:

`09d2a014190b59a5a758c9a0618b06e72a82aecb`

Branch:

`production/astrology-astronomy-engine-provider-20260913`

Pull request:

`#30 production: add Astronomy Engine natal provider`

Feature head directly validated by the canonical successful run:

`6f379044825fe638a3a981864340dd0b5f3a55e7`

PR merge ref executed by GitHub Actions:

`6d41b347aa99560dcb51407b2cdf600c6a0050d9`

## Provider admitted in this round

```text
provider_id       astronomy-engine-natal-v1
provider_version  1.0.0
scope             natal only
output             astrology_fact_bundle@1.0.0
runtime owner      tools/astrology_provider.py
```

Deterministic path:

```text
raw birth data
→ tools/astrology_provider.py
→ Astrology Fact Bundle 1.0
→ tools/astrology_runtime.py
→ ASTROLOGY.md
```

The provider does not own interpretation and cannot bypass `tools/astrology_runtime.py`.

## Dependency / source evidence

Astronomy dependency:

```text
package             astronomy-engine==2.1.19
source repository   cosinekitty/astronomy
reviewed revision   865d3da7d8112bbc7911238052c6af4aaf877181
license              MIT
```

No Astronomy Engine source file is vendored into this repository.

Astrology-specific house/reference evidence:

```text
repository          kounkt/tri-horoscope
reviewed revision   11318426c52c222eea108583ca45420c864825ca
reference path      src/natal_v0.py
fixture path        tests/E1_south_sydney.json
license              MIT
```

The Playbook owns its provider implementation. The reviewed reference is used for bounded algorithm comparison and fixture parity; its unrelated BaZi/Vedic surfaces are not adopted.

## Production input boundary

Provider input requires:

```text
local_datetime      naive ISO local wall time
timezone_name       IANA timezone
latitude            explicit decimal coordinate
longitude           explicit decimal coordinate
house_system        Whole Sign | Placidus
birth_time_certainty exact | approximate
```

Provider v1 deliberately does not own geocoding.

Fail-closed boundaries include:

- nonexistent DST wall time;
- ambiguous DST wall time;
- fixed offset used as timezone identity;
- unknown birth time / local-noon substitution;
- unsupported house system;
- Placidus beyond the conservative Production-v1 latitude boundary;
- undefined or non-convergent Placidus geometry.

## Cross-implementation fixture evidence

Repository fixture:

`tests/fixtures/astrology_provider_sydney_1990.json`

It retains only the minimum Western deterministic values needed for regression from the reviewed MIT upstream fixture:

- ASC / MC;
- tropical body longitudes;
- selected Placidus cusps;
- house assignments.

Acceptance tolerance:

`0.0167° ≈ 1 arcminute`

The successful CI run demonstrated parity for this bounded fixture. This is **not** universal astronomical certification, does not establish scientific predictive validity, and does not claim every possible location/time/house-system boundary has been independently cross-engine certified.

## Canonical execution evidence

GitHub Actions:

```text
workflow          Validate Playbook #219
run id            34760385651
job id            103732076694
feature head      6f379044825fe638a3a981864340dd0b5f3a55e7
PR merge-ref      6d41b347aa99560dcb51407b2cdf600c6a0050d9
```

Environment reported by the job:

```text
Ubuntu            24.04.5 LTS
CPython           3.12.14
git               2.55.0
runner            2.337.0
```

Dependency install:

```text
astronomy-engine-2.1.19 successfully installed
```

Directly executed production suites:

```text
Astrology production contract     10 / 10 PASS
Astrology natal provider          13 / 13 PASS
Astrology runtime gate            15 / 15 PASS
----------------------------------------------
Astrology production relevant     38 / 38 PASS
```

Whole root suite:

```text
Ran 68 tests
OK
```

Structural validation:

```text
PASS playbook structure
```

No temporary CI bridge was used. These tests live permanently under `tests/`.

## Evidence boundary

The run proves the checked-in deterministic/provider contracts and the bounded upstream fixture parity under the recorded environment. It does not prove:

- scientific or predictive validity of astrology;
- universal sub-arcminute accuracy across every date/location;
- transit event-search capability;
- geocoding capability;
- synastry/composite/return capability;
- unknown-time chart reconstruction;
- manual fresh-agent semantic grading of behavioral scenarios.

## Still not admitted

```text
transit event-search provider
station / ingress search provider
geocoding
unknown-time noon substitution
sidereal production mode
synastry
composite
solar return
rectification
```

Palmistry is outside this change and remains untouched.
