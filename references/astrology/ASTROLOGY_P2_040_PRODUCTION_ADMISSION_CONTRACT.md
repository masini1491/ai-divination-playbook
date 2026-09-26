# AST-P2-040 — Extended Ephemeris Production Admission Contract

Status: **PROSPECTIVE / FROZEN BEFORE PRODUCTION PROBE / NOT YET PRODUCTION-ADMITTED**

## Candidate lane

This review does not mutate the existing `astronomy-engine-natal-v1` identity. It evaluates a separate composable calculation provider:

```text
provider_id       astrology-extended-ephemeris-c1-v1
representation    c1-cheb-d7-w60
objects           Chiron / Ceres / Pallas / Juno / Vesta
activation        explicit request only
reading mode      known-time natal only
authority         deterministic calculation facts only
```

The existing core natal provider remains responsible for Sun through Pluto, Mean North Node, houses, angles, sect and current default natal aspects.

## Build / runtime architecture

```text
NASA/JPL Horizons (build-time only)
→ 5-day apparent geocentric tropical longitude grid
→ project-owned sequential C1 Chebyshev generator
→ immutable coefficient dataset under data/astrology/extended_ephemeris/v1
→ manifest + dataset digest + per-shard SHA-256 / Git blob identity
→ GitHub Connect exact admitted revision
→ query-bounded one-shard retrieval
→ project-owned local evaluator
→ extended object fact rows
→ Astrology runtime Fact Gate
```

Ordinary runtime must not call Horizons.

### Frozen representation

- degree: 7
- segment width: 60 days
- 8 float64 coefficients per object/segment
- 3,199 segments
- object order: Chiron, Ceres, Pallas, Juno, Vesta
- coverage source padding through 2350-10-06 UTC
- admitted output window ends at 2350-10-01 UTC
- 96 segments per shard
- 34 shards
- maximum full shard payload: 30,720 raw bytes / 40,960 base64 characters
- one requested object's segment coefficients: 64 raw bytes
- all five objects at one instant: 320 raw coefficient bytes

Runtime evaluates one segment only; no blending.

## Prospective production validation

The following 24 UTC instants were frozen before first production-admission probe. They were not part of E2, AST-P1-010, AST-P2-041 or AST-P2-042 fixture sets.

- `P2-040-V01` — `1836-03-12T03:17:00Z`
- `P2-040-V02` — `1858-02-02T09:43:00Z`
- `P2-040-V03` — `1879-12-27T15:29:00Z`
- `P2-040-V04` — `1901-11-19T21:11:00Z`
- `P2-040-V05` — `1923-10-12T03:17:00Z`
- `P2-040-V06` — `1945-09-04T09:43:00Z`
- `P2-040-V07` — `1967-07-28T15:29:00Z`
- `P2-040-V08` — `1989-06-19T21:11:00Z`
- `P2-040-V09` — `2011-05-12T03:17:00Z`
- `P2-040-V10` — `2033-04-04T09:43:00Z`
- `P2-040-V11` — `2055-02-25T15:29:00Z`
- `P2-040-V12` — `2077-01-17T21:11:00Z`
- `P2-040-V13` — `2098-12-11T03:17:00Z`
- `P2-040-V14` — `2120-11-03T09:43:00Z`
- `P2-040-V15` — `2142-09-26T15:29:00Z`
- `P2-040-V16` — `2164-08-19T21:11:00Z`
- `P2-040-V17` — `2186-07-12T03:17:00Z`
- `P2-040-V18` — `2208-06-04T09:43:00Z`
- `P2-040-V19` — `2230-04-27T15:29:00Z`
- `P2-040-V20` — `2252-03-20T21:11:00Z`
- `P2-040-V21` — `2274-02-10T03:17:00Z`
- `P2-040-V22` — `2296-01-03T09:43:00Z`
- `P2-040-V23` — `2317-11-27T15:29:00Z`
- `P2-040-V24` — `2339-10-20T21:11:00Z`

All five objects are checked at every instant: 120 object-time rows.

Frozen thresholds:

```text
longitude p95     <= 10 arcsec
longitude max     <= 30 arcsec
speed max         <= 0.001 deg/day
```

Truth longitude is direct Horizons observer longitude; truth speed is the established t-1h / t+1h central difference. Thresholds may not be widened after observing these fixtures.

## Data / materialization gates

Production admission also requires:

1. deterministic generator and explicit Horizons query/source contract;
2. immutable manifest with coverage, object order, representation identity, dataset digest and per-shard identities;
3. query-bounded retrieval of only the date-required shard from the exact admitted data revision;
4. shard SHA-256 verification before coefficient decode/evaluation;
5. fail closed on missing shard, digest mismatch, unsupported object, malformed coefficients or out-of-coverage date;
6. local execution without live Horizons;
7. provider/runtime integration preserving existing aspect participant and semantic boundaries.

## Admission boundary

A PASS may admit only **calculation facts**:

```text
longitude
speed
motion
sign
known-time house placement
```

It does not admit:

- Chiron/Ceres/Pallas/Juno/Vesta symbolic meanings;
- extended-object aspect participation by default;
- extended-object transit search;
- unknown-time extended-object facts;
- Swiss compatibility;
- scientific predictive-validity claims.

Any interpretation remains `unsupported_factor` unless a separate source-backed semantic claim family is admitted.
