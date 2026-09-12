#!/usr/bin/env python3
"""
REFERENCE-ONLY research probe.

Compare a tri-horoscope-style Western tropical/Placidus fixture against
pyswisseph output for the same fixed-offset civil time and coordinates.

This is not a production astrology engine and does not establish accuracy.
It reports the effective Swiss Ephemeris backend returned at runtime so that
silent SWIEPH -> MOSEPH fallback cannot be mistaken for .se1-backed SWIEPH.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path

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


def jd_from_input(date_s: str, time_s: str, offset_hours: float):
    local = dt.datetime.fromisoformat(f"{date_s}T{time_s}:00").replace(
        tzinfo=dt.timezone(dt.timedelta(hours=offset_hours))
    )
    utc = local.astimezone(dt.timezone.utc)
    hour = utc.hour + utc.minute / 60 + utc.second / 3600 + utc.microsecond / 3.6e9
    return swe.julday(utc.year, utc.month, utc.day, hour), utc


def circular_diff_deg(a: float, b: float) -> float:
    return abs((a - b + 180.0) % 360.0 - 180.0)


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
    ap.add_argument("fixture", type=Path)
    args = ap.parse_args()

    fixture = json.loads(args.fixture.read_text(encoding="utf-8"))
    inp = fixture["input"]
    western = fixture["western_tropical_placidus"]

    jd, utc = jd_from_input(
        inp["date"], inp["time"], float(inp["utcOffsetHours"])
    )
    lat = float(inp["latitude"])
    lon = float(inp["longitude"])

    requested_flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    body_rows = {}
    effective_backends = set()
    computed_lons = {}

    for name, body_id in BODIES.items():
        calc, retflag = swe.calc_ut(jd, body_id, requested_flags)
        actual_lon = calc[0] % 360.0
        expected_lon = float(western["lons"][name]) % 360.0
        diff_arcsec = circular_diff_deg(actual_lon, expected_lon) * 3600.0
        computed_lons[name] = actual_lon
        effective_backends.add(backend_name(retflag))
        body_rows[name] = {
            "fixture_lon_deg": expected_lon,
            "pyswisseph_lon_deg": actual_lon,
            "difference_arcsec": diff_arcsec,
            "speed_deg_per_day": calc[3],
            "effective_backend": backend_name(retflag),
            "sign_agrees": int(actual_lon // 30) == int(expected_lon // 30),
        }

    cusps, ascmc = swe.houses_ex(jd, lat, lon, b"P")
    expected_cusps = tuple(float(x) for x in western["cusps"][1:])
    cusp_rows = []
    for idx, (actual, expected) in enumerate(zip(cusps, expected_cusps), start=1):
        cusp_rows.append(
            {
                "house": idx,
                "fixture_deg": expected,
                "pyswisseph_deg": actual,
                "difference_arcsec": circular_diff_deg(actual, expected) * 3600.0,
            }
        )

    house_mismatches = []
    expected_houses = western.get("houses", {})
    for name, actual_lon in computed_lons.items():
        if name not in expected_houses:
            continue
        actual_house = house_of(actual_lon, cusps)
        expected_house = int(expected_houses[name])
        if actual_house != expected_house:
            house_mismatches.append(
                {
                    "body": name,
                    "fixture_house": expected_house,
                    "pyswisseph_house": actual_house,
                }
            )

    body_diffs = [v["difference_arcsec"] for v in body_rows.values()]
    cusp_diffs = [v["difference_arcsec"] for v in cusp_rows]
    result = {
        "status": "REFERENCE-ONLY",
        "fixture": str(args.fixture),
        "runtime": {
            "pyswisseph_version": swe.version,
            "requested_backend": "SWIEPH",
            "effective_backends": sorted(effective_backends),
            "utc": utc.isoformat(),
            "house_system": "Placidus",
            "zodiac": "tropical",
            "center": "geocentric",
        },
        "summary": {
            "body_count": len(body_rows),
            "planetary_longitude_max_difference_arcsec": max(body_diffs),
            "planetary_longitude_mean_difference_arcsec": sum(body_diffs) / len(body_diffs),
            "sign_disagreements": sum(1 for v in body_rows.values() if not v["sign_agrees"]),
            "asc_difference_arcsec": circular_diff_deg(
                ascmc[0], float(western["ascDeg"])
            ) * 3600.0,
            "mc_difference_arcsec": circular_diff_deg(
                ascmc[1], float(western["mcDeg"])
            ) * 3600.0,
            "cusp_max_difference_arcsec": max(cusp_diffs),
            "cusp_mean_difference_arcsec": sum(cusp_diffs) / len(cusp_diffs),
            "house_placement_mismatch_count": len(house_mismatches),
        },
        "bodies": body_rows,
        "cusps": cusp_rows,
        "house_mismatches": house_mismatches,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
