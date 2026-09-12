# Transit Timing Validation Results｜行運事件時間驗證結果

Status: **REFERENCE-ONLY / RESEARCH RESULT｜僅供參考／研究結果**

Playbook baseline at branch start: `masini1491/ai-divination-playbook@7ef77b03000f03bbb4c3e7589517f9ace31974fe`

本檔延續 Astrology Cold research line，驗證 exact aspect、station、applying / separating 與幾何 window 的 deterministic 表達方式。它**不建立 production engine authority、orb policy、interpretation policy 或 routing admission**。

## 1. Research questions

本輪收窄四個問題：

1. exact aspect time 是否能對外部 pinned benchmark 做可量化 timing check？
2. retrograde / direct station 是否能由 longitude speed 的零點明確表示？
3. applying / separating 是否能由 signed aspect error 與 relative speed deterministic 判定，而不需要語言模型猜測？
4. 若給定一個明確 orb 作**測試參數**，entry / exact / exit 是否應由幾何求根，而不是以 exact time 前後對稱加減固定時數？

## 2. Reviewed external evidence

### 2.1 Astronomy Engine lunar-phase benchmark

Pinned source:

```text
cosinekitty/astronomy@865d3da7d8112bbc7911238052c6af4aaf877181
```

Reviewed files:

```text
generate/moonphase/moonphases.txt
generate/test.py
```

The test suite maps:

```text
quarter code 0 / 1 / 2 / 3
→ target Moon-Sun elongation 0° / 90° / 180° / 270°
```

and sets:

```text
threshold_seconds = 90.0
```

for prediction-time validation against the benchmark corpus.

This corpus is used here as a **shared pinned timing benchmark**. It is not treated as proof that Astronomy Engine and Swiss Ephemeris are identical.

### 2.2 AstroScript exact-aspect search architecture

Pinned source:

```text
Shoresh613/astro-script@18f4a3e291a557b2ef47c7fb5e27b108f1bcf4b7
```

Reviewed files:

```text
src/astroscript/aspect_search.py
tests/test_aspect_search.py
```

Static review shows the search implementation:

- uses timezone-aware UTC normalization;
- obtains longitude + speed from Swiss Ephemeris;
- adaptively limits search steps to at most 6 hours and at most about 2° phase change;
- unwraps angular phase across 0° / 360°;
- bisects crossings to a 1-second time tolerance;
- detects relative-speed sign changes and splits segments around the relative station;
- includes tests for wraparound conjunctions, oppositions, inclusive boundaries, three-pass retrograde crossings and a tangential hit at station;
- includes a real-ephemeris test requiring exactly one Sun-Moon trine during 2026-07-05..06 UTC with separation ≈120°.

These are useful algorithm / failure-mode references only. AstroScript's unresolved license discrepancy remains unchanged; no source code is copied from it.

## 3. Local research runtime

Probe runtime:

```text
pyswisseph: 2.10.03
requested flags: FLG_SWIEPH | FLG_SPEED = 258
effective returned flags: 260 = FLG_MOSEPH | FLG_SPEED
zodiac: tropical
center: geocentric
time basis: UTC
```

As in the previous engine comparison, `.se1` files were not available in this runtime. Therefore all numeric results below are:

> **Swiss Ephemeris API using Moshier fallback**

and must not be described as `.se1` / DE441 Swiss results.

Companion executable:

[`transit_timing_validation_probe.py`](transit_timing_validation_probe.py)

## 4. Lunar exact-event timing benchmark

A bounded slice of 12 benchmark events from January through March 2020 was used. The benchmark timestamps have minute resolution.

For each event the probe solved:

```text
Moon longitude - Sun longitude
= quarter × 90°
```

by direct root finding.

Summary:

```text
count                         = 12
max |calculated - benchmark|  = 24.538 s
mean |calculated - benchmark| = 15.174 s
median                        = 17.480 s
all 12                        < 30 s from the listed minute mark
Astronomy Engine test limit   = 90 s
```

Because the benchmark timestamps themselves are minute-granularity, this result **does not establish a sub-25-second model-to-model difference**. It supports the narrower statement that the Moshier-backed solver lands inside the same benchmark minute neighborhood for all 12 sampled phase events and well inside the benchmark suite's stated 90-second acceptance window.

### Sample rows

| Target | Benchmark UTC | Calculated UTC | Delta |
|---|---|---|---:|
| 90° | 2020-01-03 04:45:00 | 2020-01-03 04:45:24.538 | +24.538 s |
| 180° | 2020-01-10 19:21:00 | 2020-01-10 19:21:19.784 | +19.784 s |
| 270° | 2020-01-17 12:58:00 | 2020-01-17 12:58:22.658 | +22.658 s |
| 0° | 2020-01-24 21:42:00 | 2020-01-24 21:41:58.177 | −1.823 s |
| 180° | 2020-03-09 17:48:00 | 2020-03-09 17:47:39.677 | −20.323 s |
| 0° | 2020-03-24 09:28:00 | 2020-03-24 09:28:13.786 | +13.786 s |

The calculated angular residuals at the solved roots were on the order of `10^-8` degrees in this runtime.

## 5. Exact moving-body aspect case

To mirror AstroScript's real-ephemeris regression case, the probe searched:

```text
Sun ↔ Moon
aspect branch: 120°
window: 2026-07-05 00:00 UTC
     → 2026-07-06 00:00 UTC
```

Result:

```text
exact UTC                  = 2026-07-05 08:01:16.761389
phase at root              = 120.0000000263°
angular residual           = +2.63e-8°
relative speed             = -11.7193478°/day
effective backend flags    = 260 (MOSEPH + SPEED)
```

This independently reproduces the **existence and exact-geometry shape** of the pinned AstroScript regression case: one Sun-Moon trine in the requested UTC day window.

The reviewed AstroScript test does not publish an expected timestamp, so this is **not** a cross-implementation timestamp comparison for that particular 2026 event.

## 6. Applying / separating geometry

Using the same 120° branch, signed error is defined as the shortest signed angular difference from that exact branch.

Observed around the root:

| Offset from exact | Signed error | Distance | Deterministic state |
|---:|---:|---:|---|
| −6 h | +2.921637° | 2.921637° | applying |
| −1 h | +0.488077° | 0.488077° | applying |
| +1 h | −0.488541° | 0.488541° | separating |
| +6 h | −2.938365° | 2.938365° | separating |

This supports a candidate fact-layer rule:

```text
applying / separating
= geometry + direction of relative motion
```

not:

```text
LLM interpretation of whether the aspect "feels incoming" or "already passed"
```

The eventual Structured Astrology Fact should retain enough data to reproduce this decision, e.g.:

```text
signed_error
absolute_orb
relative_speed
branch / target_angle
exact_time when available
applying | exact | separating
```

## 7. Geometry-window experiment

For validation only, an explicit test parameter was set:

```text
orb = 1.0°
```

This is **not an adopted orb policy**.

For the same Sun-Moon trine:

```text
1° entry = 2026-07-05 05:58:17.219361 UTC
exact    = 2026-07-05 08:01:16.761389 UTC
1° exit  = 2026-07-05 10:04:01.937937 UTC
```

Durations:

```text
entry → exact = 7379.542 s
exact → exit  = 7365.177 s
total window  = 14744.719 s ≈ 4 h 05 m 44.7 s
```

The two sides are close but not perfectly symmetric because relative speed changes through the interval.

Research implication:

> If a future tradition policy says an aspect uses `N°` orb, `entry_time` and `exit_time` should be solved from geometry. They should not be generated by adding a fixed clock duration around `exact_time`.

The **choice of N°** remains L3 tradition / policy. The root-finding of where geometry equals N° is L1/L2 deterministic calculation.

## 8. Station root validation

A station candidate is defined here as a zero crossing of geocentric ecliptic longitude speed:

```text
speed < 0 → retrograde
speed = 0 → station root
speed > 0 → direct
```

The probe sampled the year 2026 and refined sign changes by bisection. Two bodies were retained as stress examples:

- Mercury: fast body / short retrograde cycles;
- Saturn: slow body / small speed near station.

### Mercury 2026

| Station UTC | Transition |
|---|---|
| 2026-02-26 06:48:13.637 | direct → retrograde |
| 2026-03-20 19:32:54.291 | retrograde → direct |
| 2026-06-29 17:35:59.357 | direct → retrograde |
| 2026-07-23 22:57:55.371 | retrograde → direct |
| 2026-10-24 07:12:47.872 | direct → retrograde |
| 2026-11-13 15:53:56.937 | retrograde → direct |

For every listed Mercury root, speed 12 hours before and after had opposite signs.

### Saturn 2026

| Station UTC | Transition |
|---|---|
| 2026-07-26 19:56:47.575 | direct → retrograde |
| 2026-12-10 23:31:02.457 | retrograde → direct |

Saturn's ±12-hour speed values are much smaller than Mercury's, so slow-body station search is a useful numerical stress case.

### Station evidence boundary

These station timestamps are **single-engine self-consistency evidence only**. No independent Astronomy-Engine-family station benchmark has yet been established in this research line.

Therefore the current supported statement is:

```text
station representation + root-search method
→ executable and internally fail-checkable
```

not:

```text
these station timestamps are already cross-engine certified production facts
```

## 9. Candidate TransitEvent fact boundary

This evidence supports refining the earlier event sketch into a future candidate fact shape:

```text
TransitEvent
- event_kind: exact_aspect | station | ingress | later...
- exact_time_utc
- moving_body
- target_type / target
- target_angle / condition
- body_longitude(s)
- speed(s)
- relative_speed when applicable
- signed_error / absolute_orb at query time
- applying_state: applying | exact | separating | not_applicable
- geometry_window:
    - orb_value
    - orb_policy_id / source
    - entry_time
    - exit_time
- zodiac / center / coordinate configuration
- engine identity + version
- requested backend
- effective backend
- availability / uncertainty
```

Important separation:

```text
exact geometry + speed + root time
→ deterministic fact

orb size / aspect inclusion / weighting
→ tradition or policy

"what it means"
→ interpretation layer
```

## 10. Failure modes exposed by this round

### 10.1 Requested backend != effective backend

A caller may request `FLG_SWIEPH` while the runtime actually calculates with `FLG_MOSEPH` fallback.

Future engine provenance must record **effective returned flags / backend**, not just requested flags.

### 10.2 Angular wrap

0° / 360° crossings can create false sign changes unless phase is normalized / unwrapped deliberately.

### 10.3 Retrograde multiple passage

A single aspect can become exact multiple times during a retrograde loop. Event identity therefore cannot be only:

```text
body A + aspect + body B
```

It also needs exact-time / passage identity.

### 10.4 Tangential exact hit

An aspect can touch exactness at a relative station without a simple monotonic crossing. A production search algorithm must not assume every root has an ordinary sign-changing crossing.

### 10.5 Orb-window policy leakage

Calculating entry / exit from an orb is deterministic only **after** the orb has been explicitly supplied by an upstream tradition / policy contract.

## 11. What this round supports

Current evidence supports:

1. exact aspect geometry can be represented as deterministic fact;
2. a bounded lunar timing probe agrees with the pinned benchmark suite's minute-level event times well inside its stated 90-second threshold;
3. applying / separating can be determined from signed geometry + relative motion;
4. station roots can be detected from speed sign changes and verified locally before / after the root;
5. orb-window entry / exit should be solved from geometry after an explicit orb policy is provided;
6. effective ephemeris backend must be part of provenance;
7. retrograde loops require multi-passage event identity and search logic.

## 12. Remaining evidence gaps

Still open before production consideration:

```text
.se1-backed SWIEPH timing comparison
independent station-time benchmark
planet-to-planet exact-aspect cross-engine benchmark
transit-to-fixed-natal-point timing validation
ingress timing validation
mean-node vs true-node timing/provenance
sidereal / ayanamsa timing parity
topocentric timing parity where relevant
polar / house-dependent transit failure semantics
DST / timezone-resolution contract for user-facing local windows
production tolerance selection
```

No production tolerance is selected from the current sample.

**Current state: REFERENCE-ONLY / RESEARCH / NOT PRODUCTION-ROUTABLE**
