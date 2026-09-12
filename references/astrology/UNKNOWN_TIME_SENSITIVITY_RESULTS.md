# Unknown Birth-Time Sensitivity Results｜出生時間未知敏感度結果

Status: **REFERENCE-ONLY / RESEARCH RESULT｜僅供參考／研究結果**

Playbook baseline at branch start: `masini1491/ai-divination-playbook@18d75bd0e7466b120094be6f681af04f2445d209`

This result quantifies one previously identified evidence gap in [`EVIDENCE_ARCHITECTURE.md`](EVIDENCE_ARCHITECTURE.md): how much a full-day unknown birth-time window can move chart facts.

It is not a production availability contract.

## 1. Reviewed fixture

Input anchor comes from the fictional public fixture:

```text
kounkt/tri-horoscope
revision: 11318426c52c222eea108583ca45420c864825ca
fixture: tests/E4_time_unknown.json
date: 1985-08-07
UTC offset: +09:00
latitude: 26.2124
longitude: 127.6811
timeUnknown: true
```

The reviewed `tri-horoscope` implementation itself marks angles, cusps, houses, Moon degree, and hour pillar as unreliable when birth time is unknown.

This study independently probes the Western tropical/Placidus geometry across the full civil day.

## 2. Method

Companion executable:

[`unknown_time_sensitivity_probe.py`](unknown_time_sensitivity_probe.py)

Research runtime:

```text
pyswisseph version: 2.10.03
requested backend: SWIEPH
effective backend: MOSEPH
zodiac: tropical
house system: Placidus
sample interval: 15 minutes
sample count: 96
```

For every local-time sample from `00:00` through `23:45`, the probe records:

- Sun through Pluto longitude;
- zodiac signs seen during the day;
- Ascendant / MC / 12 cusp positions;
- the houses each planet would occupy at that sample time.

The longitude span is the minimum circular arc containing the discrete samples.

Important:

```text
96 samples
!= continuous mathematical worst-case bound
```

## 3. Planetary longitude sensitivity

| Body | 15-minute-grid longitude span | Signs seen |
|---|---:|---|
| Sun | 0.9482° | Leo |
| Moon | 11.7336° | Aries, Taurus |
| Mercury | 0.7368° | Leo |
| Venus | 1.1383° | Cancer |
| Mars | 0.6356° | Leo |
| Jupiter | 0.1285° | Aquarius |
| Saturn | 0.0196° | Scorpio |
| Uranus | 0.0131° | Sagittarius |
| Neptune | 0.0175° | Capricorn |
| Pluto | 0.0143° | Scorpio |

The Moon crossed a zodiac-sign boundary inside this one-day uncertainty window.

Therefore the rule:

```text
unknown birth time
→ just use local noon Moon sign as known
```

would be false for this fixture.

For the other nine bodies the sign happened to remain unchanged in this specific date/location case. That does **not** make their exact degree time-independent: inner-planet / Sun movement across the day is still large enough to matter near a sign boundary or a tight aspect threshold.

## 4. Angle and cusp sensitivity

Observed circular spans:

```text
Ascendant: 354.7903°
Midheaven: 355.9019°
12 Placidus cusp spans:
minimum ≈ 354.7903°
maximum ≈ 355.9019°
```

This is effectively full-circle sensitivity at the day scale.

Accordingly, a local-noon placeholder cannot be promoted to a known:

- Ascendant;
- MC / IC / DC;
- house cusp;
- house placement.

## 5. House-placement sensitivity

Across the 96 time samples, every one of the ten tested planets occupied **all 12 houses** at some point in the sampled day:

```text
Sun      → houses 1..12
Moon     → houses 1..12
Mercury  → houses 1..12
Venus    → houses 1..12
Mars     → houses 1..12
Jupiter  → houses 1..12
Saturn   → houses 1..12
Uranus   → houses 1..12
Neptune  → houses 1..12
Pluto    → houses 1..12
```

This is direct sensitivity evidence for the current research principle:

```text
unknown birth time
→ houses / angles unavailable
```

A deterministic noon chart may still be useful as a computation placeholder, but the resulting houses must remain explicitly non-authoritative.

## 6. Research implication

This result strengthens the candidate unknown-time boundary:

### Can remain conditionally usable

- date-level slow-planet sign placement when the full uncertainty interval does not cross a sign boundary;
- planetary longitude only if represented as an uncertainty interval / range or if the required decision is insensitive to that range.

### Must fail closed unless additional evidence narrows birth time

- Ascendant / MC / IC / DC;
- Placidus cusps;
- all house placements;
- angle aspects;
- house-based transits.

### Moon requires special treatment

The Moon should not be treated like a slow planet.

At minimum:

```text
unknown time
→ calculate full allowed-time Moon range
→ if range crosses sign/aspect boundary, mark the corresponding fact ambiguous
```

## 7. Limitations

This result does not establish a universal 24-hour uncertainty policy because:

- the study uses one fictional date/location fixture;
- it samples every 15 minutes rather than continuously;
- it uses a fixed UTC offset rather than timezone/DST resolution;
- the effective ephemeris backend was Moshier fallback;
- no formal probability distribution over birth time is assumed;
- different user-provided uncertainty windows may be much narrower than 24 hours.

The next useful step is a multi-fixture uncertainty sweep covering:

- equatorial / northern / southern latitudes;
- Moon near and far from sign boundaries;
- inner planets near sign boundaries;
- narrow uncertainty windows such as ±15 min, ±1 h, ±3 h;
- aspect-boundary sensitivity.

**Current state: REFERENCE-ONLY / RESEARCH / NOT PRODUCTION-ROUTABLE**
