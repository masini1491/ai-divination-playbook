#!/usr/bin/env python3
"""
REFERENCE-ONLY research probe.

Sample a full local civil day at a fixed interval to quantify how unknown birth
time affects planetary longitudes, zodiac-sign availability, angles/cusps, and
house placement under pyswisseph.

The discrete sample is not a continuous mathematical bound. House results are
sensitivity evidence only; they are not facts for an unknown-time natal chart.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from collections import defaultdict

import swisseph as swe

BODIES = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
    "Uranus": swe.URANUS,
    "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO,
}
SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]


def jd_for_local(date_s: str, minutes_from_midnight: int, offset_hours: float):
    day = dt.date.fromisoformat(date_s)
    local = dt.datetime.combine(day, dt.time.min).replace(
        tzinfo=dt.timezone(dt.timedelta(hours=offset_hours))
    ) + dt.timedelta(minutes=minutes_from_midnight)
    utc = local.astimezone(dt.timezone.utc)
    hour = utc.hour + utc.minute / 60 + utc.second / 3600 + utc.microsecond / 3.6e9
    return swe.julday(utc.year, utc.month, utc.day, hour)


def circular_span_deg(values):
    xs = sorted(v % 360.0 for v in values)
    if len(xs) < 2:
        return 0.0
    gaps = [
        (xs[(i + 1) % len(xs)] - xs[i]) % 360.0
        for i in range(len(xs))
    ]
    return 360.0 - max(gaps)


def backend_name(retflag: int) -> str:
    if retflag & swe.FLG_JPLEPH:
        return "JPLEPH"
    if retflag & swe.FLG_SWIEPH:
        return "SWIEPH"
    if retflag & swe.FLG_MOSEPH:
        return "MOSEPH"
    return f"UNKNOWN({retflag})"


def house_of(longitude: float, cusps: tuple[float, ...]) -> int:
    for idx in range(12):
        a = cusps[idx]
        b = cusps[(idx + 1) % 12]
        span = (b - a) % 360.0
        if (longitude - a) % 360.0 < span:
            return idx + 1
    return 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    ap.add_argument("--utc-offset-hours", type=float, required=True)
    ap.add_argument("--latitude", type=float, required=True)
    ap.add_argument("--longitude", type=float, required=True)
    ap.add_argument("--step-minutes", type=int, default=15)
    args = ap.parse_args()

    if args.step_minutes <= 0 or 1440 % args.step_minutes != 0:
        raise SystemExit("--step-minutes must be a positive divisor of 1440")

    requested_flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    body_values = defaultdict(list)
    house_sets = defaultdict(set)
    asc_values = []
    mc_values = []
    cusp_values = [[] for _ in range(12)]
    backends = set()

    for minute in range(0, 1440, args.step_minutes):
        jd = jd_for_local(args.date, minute, args.utc_offset_hours)
        cusps, ascmc = swe.houses_ex(
            jd, args.latitude, args.longitude, b"P"
        )
        asc_values.append(ascmc[0])
        mc_values.append(ascmc[1])
        for idx, cusp in enumerate(cusps):
            cusp_values[idx].append(cusp)

        for name, body_id in BODIES.items():
            calc, retflag = swe.calc_ut(jd, body_id, requested_flags)
            lon = calc[0] % 360.0
            body_values[name].append(lon)
            house_sets[name].add(house_of(lon, cusps))
            backends.add(backend_name(retflag))

    bodies = {}
    for name in BODIES:
        vals = body_values[name]
        sign_indexes = sorted({int(v // 30) % 12 for v in vals})
        bodies[name] = {
            "longitude_span_deg": circular_span_deg(vals),
            "signs_seen": [SIGNS[i] for i in sign_indexes],
            "houses_seen": sorted(house_sets[name]),
        }

    result = {
        "status": "REFERENCE-ONLY",
        "runtime": {
            "pyswisseph_version": swe.version,
            "requested_backend": "SWIEPH",
            "effective_backends": sorted(backends),
            "date": args.date,
            "utc_offset_hours": args.utc_offset_hours,
            "latitude": args.latitude,
            "longitude": args.longitude,
            "step_minutes": args.step_minutes,
            "sample_count": 1440 // args.step_minutes,
            "house_system": "Placidus",
            "zodiac": "tropical",
        },
        "bodies": bodies,
        "angles": {
            "asc_span_deg": circular_span_deg(asc_values),
            "mc_span_deg": circular_span_deg(mc_values),
            "cusp_spans_deg": [circular_span_deg(v) for v in cusp_values],
        },
        "limitations": [
            "Discrete sampling is not a continuous bound.",
            "A fixed UTC offset is used; timezone/DST resolution is outside this probe.",
            "House placements are sensitivity evidence only when birth time is unknown.",
        ],
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
