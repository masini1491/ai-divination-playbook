# Astrology Calculation Completion Results

Status: **PRODUCTION EXECUTION EVIDENCE**

This record closes the two calculation-side gaps that remained after bounded Astrology Production v1 admission:

1. city/locality input resolution to coordinates + IANA timezone;
2. deterministic transit event search over an admitted natal chart.

It is execution/governance evidence only. It does **not** claim scientific or predictive validity for astrology.

## 1. Repository identity

```text
repository: masini1491/ai-divination-playbook
baseline main: 01a159990d2086f3a47be2e299d2e7f04a0e1758
branch: production/astrology-transit-place-resolver-20260913
PR: #31 production: add Astrology transit provider and offline place resolver
```

Palmistry and `CROSS_VALIDATION.md` are outside this change scope.

## 2. Admitted calculation path

```text
city/locality name (optional)
→ tools/astrology_place_resolver.py
→ coordinates + IANA timezone

birth local wall time + timezone + coordinates
→ tools/astrology_provider.py
→ natal Astrology Fact Bundle 1.0
→ tools/astrology_runtime.py

admitted natal bundle + bounded UTC search contract
→ tools/astrology_transit_provider.py
→ transit Astrology Fact Bundle 1.0
→ tools/astrology_runtime.py
→ ASTROLOGY.md interpretation governance
```

The language model is not the astronomical calculator.

## 3. Place resolver admission

```text
resolver_id: geonamescache-city-v1
package: geonamescache==3.0.2
software upstream: yaph/geonamescache@df4f6497b321f7981645ab0c5c77d3354c63bd01
software license: MIT
dataset origin: GeoNames
dataset license: CC-BY-4.0
network required: NO
```

Boundaries:

- city/locality only;
- exact/alternate-name matching;
- optional ISO alpha-2 country disambiguator;
- ambiguous name fails closed with candidates;
- no largest-population auto-selection;
- no street/postal-code/building geocoding;
- place resolution is input provenance, not astronomical authority.

## 4. Transit provider admission

```text
provider_id: astronomy-engine-transit-v1
provider_version: 1.0.0
astronomy-engine: 2.1.19
upstream: cosinekitty/astronomy@865d3da7d8112bbc7911238052c6af4aaf877181
license: MIT
canonical event time: UTC
max search span: 400 days
normal scan step: 3 h
station scan step: 6 h
root tolerance: 0.5 s
```

Admitted event families:

- exact transit-to-natal major aspects;
- station roots;
- tropical sign ingress / retrograde return / direct re-ingress;
- repeated exact passages with sequence identity;
- tangential exact contacts at stations, which do not necessarily produce an ordinary longitude-error sign change.

Not admitted:

- unbounded event search;
- transit-house search;
- sidereal ingress;
- topocentric transit geometry;
- eclipse/lunation outcome guarantees;
- interpretation inside the provider.

## 5. Cross-engine timing evidence

The production provider is Astronomy Engine based. Historical research probes used Swiss Ephemeris API with observed Moshier fallback in the tested environment. Production regressions therefore use those earlier results as a bounded independent timing/topology comparison, not as a runtime dependency.

### Mercury natal longitude 110° — 2026 three-pass conjunction

Historical research benchmark:

```text
2026-06-16T15:44:17.088Z  direct
2026-07-14T03:53:27.175Z  retrograde
2026-08-01T13:51:40.891Z  direct
```

Production acceptance:

- exactly 3 passages;
- direct → retrograde → direct;
- passage identities 1/2/3 preserved;
- each Astronomy Engine exact root within 600 seconds of the historical research benchmark;
- exact-root angular residual bounded by the production test.

This is a cross-engine bounded regression, not universal ephemeris certification.

### 2026 station topology

Production regressions require:

```text
Mercury stations: 6
transition sequence: D→R, R→D, D→R, R→D, D→R, R→D

Saturn stations: 2
transition sequence: D→R, R→D
```

### Venus 210° boundary

Production regression requires:

```text
direct_ingress      Libra → Scorpio
retrograde_return   Scorpio → Libra
direct_reingress    Libra → Scorpio
```

### Tangential station contact

A dedicated regression constructs a natal longitude equal to a computed Mercury station longitude and verifies that the exact contact is returned as:

```text
root_kind = tangential_station
```

This explicitly closes the research-identified failure mode where a station can touch an exact target without the ordinary longitude-error function changing sign.

## 6. First executable implementation run — GitHub Actions #223

```text
run: Validate Playbook #223
run id: 34761092899
job id: 103733945903
feature head: c7381bf151c80b627e33e0820ed9cb98bbec0b26
Ubuntu: 24.04.5 LTS
Python: 3.12.14
git: 2.55.0
runner: 2.337.0
```

Dependencies actually installed:

```text
astronomy-engine-2.1.19
geonamescache-3.0.2
typing-extensions-4.16.0
```

Results at that feature head:

```text
place resolver                 5 / 5 PASS
transit provider               7 / 7 PASS
existing production contract  10 / 10 PASS
natal provider                13 / 13 PASS
runtime gate                  15 / 15 PASS
-------------------------------------------
Astrology production relevant 50 / 50 PASS
whole root suite              80 / 80 PASS
playbook structure            PASS
```

#223 predates the later governance/admission-document updates and the added station-tangent/re-ingress hardening. It is retained as the first executable core evidence, not final merge-state evidence.

## 7. Hardening run — GitHub Actions #234

```text
run: Validate Playbook #234
run id: 34761558790
job id: 103735186901
head: be12bca8886984fd1b39d5e9832cd63ee447f5e2
```

Material calculation regressions all passed, including:

- place resolver 5/5;
- updated production admission contract 12/12;
- natal provider 13/13;
- runtime gate 15/15;
- transit provider 8/8, including station-tangent and direct-reingress semantics.

The run ended `FAIL` only because the current research README already linked to this completion record before this file existed. `test_repository_root_passes` correctly reported the two missing-link references; structural checker was skipped after the unit-test failure.

Therefore #234 is **not** success evidence and must not be represented as such. It is useful failure-boundary evidence showing that the calculation tests passed while a repository-link integrity requirement remained open.

## 8. Complete integration run — GitHub Actions #235

After adding this completion record and thereby closing the README link-integrity gap:

```text
run: Validate Playbook #235
run id: 34761616256
job id: 103735341769
head: 9a3c8c612f0e26279839707f3a5435f6488cd3a0
PR merge-ref: 4aebff6472ccb9057f7197b006b92e071da52be4
Ubuntu: 24.04.5 LTS
Python: 3.12.14
git: 2.55.0
runner: 2.337.0
```

Dependencies actually installed:

```text
astronomy-engine-2.1.19
geonamescache-3.0.2
typing-extensions-4.16.0
```

Results:

```text
place resolver                  5 / 5 PASS
production admission contract  12 / 12 PASS
natal provider                 13 / 13 PASS
runtime gate                   15 / 15 PASS
transit provider                8 / 8 PASS
--------------------------------------------
Astrology production relevant  53 / 53 PASS
whole root suite               83 / 83 PASS
playbook structure             PASS
```

#235 is the canonical complete-integration execution evidence for the implemented calculation path at that head. A subsequent final-head CI is still required if this evidence-record update changes the branch head before merge.

## 9. Evidence limits

These tests establish:

- deterministic execution of the admitted implementation;
- bounded parity/topology against reviewed historical fixtures/results;
- fail-closed input/search boundaries;
- compatibility with the existing Astrology Fact Bundle runtime gate;
- explicit software/data provenance.

They do not establish:

- universal astronomical accuracy for every epoch/location;
- scientific validity of astrological interpretation;
- deterministic real-world event outcomes;
- production support for scopes explicitly excluded by the admission manifests.
