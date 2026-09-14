#!/usr/bin/env python3
"""Research-only availability probe for E2 Swiss-Ephemeris-backed objects."""
from __future__ import annotations

import json

try:
    import swisseph as swe
except ImportError:
    print(json.dumps({"status": "DEPENDENCY_MISSING", "dependency": "pyswisseph"}, indent=2))
    raise SystemExit(2)

OBJECTS = (
    ("Chiron", swe.CHIRON),
    ("Ceres", swe.CERES),
    ("Pallas", swe.PALLAS),
    ("Juno", swe.JUNO),
    ("Vesta", swe.VESTA),
)


def main() -> int:
    jd = swe.julday(2000, 1, 1, 12.0)
    results = []
    for name, index in OBJECTS:
        try:
            values, flags = swe.calc_ut(jd, index)
            results.append({
                "object_id": name,
                "status": "AVAILABLE",
                "longitude_deg": values[0],
                "latitude_deg": values[1],
                "distance_au": values[2],
                "speed_deg_per_day": values[3],
                "return_flags": flags,
            })
        except Exception as exc:  # Swiss Ephemeris reports missing data as runtime errors.
            results.append({
                "object_id": name,
                "status": "UNAVAILABLE",
                "error_type": type(exc).__name__,
                "error": str(exc),
            })

    available = sum(row["status"] == "AVAILABLE" for row in results)
    payload = {
        "authority": "REFERENCE_ONLY",
        "pyswisseph_version": getattr(swe, "version", None),
        "synthetic_julian_day": jd,
        "available": available,
        "requested": len(results),
        "results": results,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if available == len(results) else 3


if __name__ == "__main__":
    raise SystemExit(main())
