#!/usr/bin/env python3
"""
REFERENCE-ONLY host capability probe for optional PySwissEph / Swiss Ephemeris runtimes.

This tool does not establish production authority. It reports what the current
Python host can actually execute and preserves the effective ephemeris backend
returned by Swiss Ephemeris so SWIEPH -> MOSEPH fallback cannot be hidden.
"""
from __future__ import annotations

import argparse
import importlib
import json
import platform
import sys
from pathlib import Path

CORE_BODIES = (
    ("Sun", "SUN"),
    ("Moon", "MOON"),
    ("Mercury", "MERCURY"),
    ("Venus", "VENUS"),
    ("Mars", "MARS"),
    ("Jupiter", "JUPITER"),
    ("Saturn", "SATURN"),
    ("Uranus", "URANUS"),
    ("Neptune", "NEPTUNE"),
    ("Pluto", "PLUTO"),
)
OPTIONAL_BODIES = (
    ("MeanNode", "MEAN_NODE"),
    ("TrueNode", "TRUE_NODE"),
    ("Chiron", "CHIRON"),
)
STANDARD_FILES = ("sepl_18.se1", "semo_18.se1", "seas_18.se1")


def backend_name(swe, retflag: int) -> str:
    if retflag & swe.FLG_JPLEPH:
        return "JPLEPH"
    if retflag & swe.FLG_SWIEPH:
        return "SWIEPH"
    if retflag & swe.FLG_MOSEPH:
        return "MOSEPH"
    return f"UNKNOWN({retflag})"


def classify(core_rows: dict, houses_ok: bool) -> str:
    if not core_rows:
        return "MODULE_ONLY"
    core_ok = all(row.get("status") == "PASS" for row in core_rows.values())
    if not core_ok or not houses_ok:
        return "PARTIAL_EXECUTION"
    backends = {row.get("effective_backend") for row in core_rows.values()}
    if backends == {"MOSEPH"}:
        return "MOSHIER_NATAL_BASELINE"
    if backends == {"SWIEPH"}:
        return "SWIEPH_NATAL_BASELINE"
    if backends == {"JPLEPH"}:
        return "JPL_NATAL_BASELINE"
    return "MIXED_NATAL_BASELINE"


def inspect_standard_files(ephe_path: str | None) -> dict:
    if not ephe_path:
        return {name: {"exists": None, "path": None} for name in STANDARD_FILES}
    root = Path(ephe_path)
    return {
        name: {"exists": (root / name).is_file(), "path": str(root / name)}
        for name in STANDARD_FILES
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ephe-path", help="optional explicit Swiss Ephemeris data directory")
    ap.add_argument("--lat", type=float, default=25.0330)
    ap.add_argument("--lon", type=float, default=121.5654)
    args = ap.parse_args()

    result = {
        "status": "REFERENCE-ONLY",
        "production_authority": False,
        "python": platform.python_version(),
        "python_executable": sys.executable,
        "probe_fixture": {
            "utc": "2000-01-01T12:00:00Z",
            "latitude_deg": args.lat,
            "longitude_deg": args.lon,
            "house_system": "Placidus",
        },
    }

    try:
        swe = importlib.import_module("swisseph")
    except Exception as exc:
        result.update(
            {
                "module_available": False,
                "classification": "UNAVAILABLE",
                "error": repr(exc),
            }
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    if args.ephe_path:
        swe.set_ephe_path(args.ephe_path)

    jd = swe.julday(2000, 1, 1, 12.0)
    requested_flags = swe.FLG_SWIEPH | swe.FLG_SPEED

    core_rows = {}
    optional_rows = {}
    for target, rows in ((CORE_BODIES, core_rows), (OPTIONAL_BODIES, optional_rows)):
        for name, attr in target:
            body_id = getattr(swe, attr)
            try:
                values, retflag = swe.calc_ut(jd, body_id, requested_flags)
                rows[name] = {
                    "status": "PASS",
                    "longitude_deg": values[0] % 360.0,
                    "speed_deg_per_day": values[3],
                    "retflag": retflag,
                    "effective_backend": backend_name(swe, retflag),
                    "swieph": bool(retflag & swe.FLG_SWIEPH),
                    "moseph": bool(retflag & swe.FLG_MOSEPH),
                    "jpleph": bool(retflag & swe.FLG_JPLEPH),
                }
            except Exception as exc:
                rows[name] = {"status": "FAIL", "error": repr(exc)}

    try:
        cusps, ascmc = swe.houses_ex(jd, args.lat, args.lon, b"P")
        houses = {
            "status": "PASS",
            "asc_deg": ascmc[0] % 360.0,
            "mc_deg": ascmc[1] % 360.0,
            "cusps_deg": [value % 360.0 for value in cusps],
        }
        houses_ok = True
    except Exception as exc:
        houses = {"status": "FAIL", "error": repr(exc)}
        houses_ok = False

    result.update(
        {
            "module_available": True,
            "pyswisseph_version": getattr(swe, "version", None),
            "library_path": (
                swe.get_library_path() if hasattr(swe, "get_library_path") else None
            ),
            "requested_flags": {
                "value": requested_flags,
                "SWIEPH": swe.FLG_SWIEPH,
                "MOSEPH": swe.FLG_MOSEPH,
                "JPLEPH": swe.FLG_JPLEPH,
                "SPEED": swe.FLG_SPEED,
            },
            "explicit_ephe_path": args.ephe_path,
            "standard_ephemeris_files": inspect_standard_files(args.ephe_path),
            "core_bodies": core_rows,
            "optional_bodies": optional_rows,
            "houses": houses,
            "classification": classify(core_rows, houses_ok),
        }
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
