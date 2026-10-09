#!/usr/bin/env python3
"""REFERENCE-ONLY PySwissEph vs admitted Astronomy Engine transit parity probe.

Research-only. This script never changes provider routing/admission and does not
claim scientific accuracy. It compares the current admitted transit search
kernel under two longitude/speed backends:

- project Astronomy Engine backend (`tools.astrology_provider._longitude_and_speed`)
- host-native PySwissEph API, requesting SWIEPH|SPEED and recording retflag

Run inside a checkout/materialized runtime that provides the project tools and
astronomy-engine==2.1.19. PySwissEph must already be present in the host; this
script does not install or vendor it.
"""
from __future__ import annotations

import datetime as dt
import json
import math
import sys
from typing import Callable

import swisseph as swe

from tools import astrology_provider as ap
from tools import astrology_transit_provider as tp

UTC = dt.timezone.utc
SWE_IDS = {
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
REQUESTED_FLAGS = swe.FLG_SWIEPH | swe.FLG_SPEED


def backend_name(retflag: int) -> str:
    if retflag & swe.FLG_JPLEPH:
        return "JPLEPH"
    if retflag & swe.FLG_SWIEPH:
        return "SWIEPH"
    if retflag & swe.FLG_MOSEPH:
        return "MOSEPH"
    return f"UNKNOWN({retflag})"


def julian_day(when: dt.datetime) -> float:
    when = when.astimezone(UTC)
    hour = when.hour + when.minute / 60 + when.second / 3600 + when.microsecond / 3_600_000_000
    return swe.julday(when.year, when.month, when.day, hour, swe.GREG_CAL)


def swiss_state(body: str, when: dt.datetime) -> tuple[float, float, int]:
    values, retflag = swe.calc_ut(julian_day(when), SWE_IDS[body], REQUESTED_FLAGS)
    return float(values[0]) % 360.0, float(values[3]), int(retflag)


def swiss_backend(body: str, when: dt.datetime) -> tuple[float, float]:
    lon, speed, _ = swiss_state(body, when)
    return lon, speed


def circular_diff(a: float, b: float) -> float:
    return abs((a - b + 180.0) % 360.0 - 180.0)


def parse_utc(value: str) -> dt.datetime:
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, math.ceil(fraction * len(ordered)) - 1))
    return ordered[index]


def with_backend(fn: Callable, backend: Callable, *args, **kwargs):
    original = tp._longitude_and_speed
    tp._longitude_and_speed = backend
    try:
        return fn(*args, **kwargs)
    finally:
        tp._longitude_and_speed = original


def minimal_natal(longitude_deg: float = 110.0) -> dict:
    return {
        "schema_name": "astrology_fact_bundle",
        "schema_version": "1.0.0",
        "method": "Astrology",
        "reading_mode": "natal",
        "fact_source": "user_supplied_structured_export",
        "calculation_verification": "user_asserted",
        "subject_ref": "subject:synthetic-transit-target",
        "birth_time_certainty": "exact",
        "configuration": {"zodiac_system": "tropical", "center": "geocentric", "house_system": None},
        "facts": {
            "objects": [{
                "fact_id": "fact:object:mercury",
                "object_type": "planet",
                "object_id": "Mercury",
                "longitude_deg": longitude_deg,
            }],
            "houses": [], "aspects": [], "events": [],
        },
    }


def whole_sign_natal() -> dict:
    signs = ("Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces")
    houses = [{
        "fact_id": f"fact:house:{house}",
        "house_number": house,
        "cusp_longitude_deg": float((house - 1) * 30),
        "sign_index": house - 1,
        "sign": signs[house - 1],
        "sign_degree": 0.0,
    } for house in range(1, 13)]
    return {
        "schema_name": "astrology_fact_bundle",
        "schema_version": "1.0.0",
        "method": "Astrology",
        "reading_mode": "natal",
        "fact_source": "user_supplied_structured_export",
        "calculation_verification": "user_asserted",
        "subject_ref": "subject:house-search-fixture",
        "birth_time_certainty": "exact",
        "configuration": {"zodiac_system": "tropical", "center": "geocentric", "house_system": "Whole Sign"},
        "facts": {"objects": [], "houses": houses, "aspects": [], "events": []},
    }


def paired_times(a: list[dict], b: list[dict]) -> list[float]:
    if len(a) != len(b):
        return []
    return [abs((parse_utc(x["exact_time_utc"]) - parse_utc(y["exact_time_utc"])).total_seconds()) for x, y in zip(a, b)]


def compact_pair(a: list[dict], b: list[dict], fields: tuple[str, ...]) -> list[dict]:
    deltas = paired_times(a, b)
    rows = []
    for index, (left, right) in enumerate(zip(a, b), start=1):
        row = {
            "index": index,
            "astronomy_engine_time_utc": left.get("exact_time_utc"),
            "pyswisseph_time_utc": right.get("exact_time_utc"),
            "absolute_time_delta_seconds": deltas[index - 1] if deltas else None,
        }
        for field in fields:
            row[f"{field}_astronomy_engine"] = left.get(field)
            row[f"{field}_pyswisseph"] = right.get(field)
        rows.append(row)
    return rows


def pointwise_probe() -> dict:
    dates = [dt.datetime(2026, month, day, 12, 0, tzinfo=UTC) for month in range(1, 13) for day in (1, 15)]
    dates.extend(parse_utc(value) for value in (
        "2026-02-26T06:48:00Z", "2026-03-20T19:33:00Z", "2026-06-16T15:44:00Z",
        "2026-06-29T17:36:00Z", "2026-07-14T03:53:00Z", "2026-07-23T22:58:00Z",
        "2026-08-01T13:52:00Z", "2026-09-10T08:07:00Z", "2026-10-24T07:13:00Z",
        "2026-10-25T09:10:00Z", "2026-11-13T15:54:00Z", "2026-12-04T08:13:00Z",
        "2026-12-10T23:31:00Z",
    ))
    dates = sorted(set(dates))
    rows = []
    for when in dates:
        for body in SWE_IDS:
            ae_lon, ae_speed = ap._longitude_and_speed(body, when)
            sw_lon, sw_speed, retflag = swiss_state(body, when)
            rows.append({
                "time_utc": when.isoformat().replace("+00:00", "Z"),
                "body": body,
                "longitude_difference_deg": circular_diff(ae_lon, sw_lon),
                "speed_difference_deg_per_day": abs(ae_speed - sw_speed),
                "pyswisseph_retflag": retflag,
                "pyswisseph_effective_backend": backend_name(retflag),
            })
    lon = [x["longitude_difference_deg"] for x in rows]
    speed = [x["speed_difference_deg_per_day"] for x in rows]
    return {
        "timestamp_count": len(dates),
        "sample_count": len(rows),
        "summary": {
            "longitude_max_deg": max(lon),
            "longitude_max_arcsec": max(lon) * 3600.0,
            "longitude_p95_deg": percentile(lon, 0.95),
            "longitude_p99_deg": percentile(lon, 0.99),
            "speed_max_deg_per_day": max(speed),
            "speed_p95_deg_per_day": percentile(speed, 0.95),
            "speed_p99_deg_per_day": percentile(speed, 0.99),
            "effective_backends": sorted({x["pyswisseph_effective_backend"] for x in rows}),
            "retflags": sorted({x["pyswisseph_retflag"] for x in rows}),
        },
        "worst_longitude": max(rows, key=lambda x: x["longitude_difference_deg"]),
        "worst_speed": max(rows, key=lambda x: x["speed_difference_deg_per_day"]),
    }


def event_probe() -> dict:
    natal = minimal_natal()
    ae_three = with_backend(tp.search_transit_to_natal, ap._longitude_and_speed, natal,
        start_utc="2026-06-01T00:00:00Z", end_utc="2026-08-10T00:00:00Z",
        moving_bodies=["Mercury"], natal_targets=["Mercury"], aspects=["conjunction"])
    sw_three = with_backend(tp.search_transit_to_natal, swiss_backend, natal,
        start_utc="2026-06-01T00:00:00Z", end_utc="2026-08-10T00:00:00Z",
        moving_bodies=["Mercury"], natal_targets=["Mercury"], aspects=["conjunction"])

    station_pairs = {}
    for body in ("Mercury", "Saturn"):
        left = with_backend(tp.search_stations, ap._longitude_and_speed,
            start_utc="2026-01-01T00:00:00Z", end_utc="2027-01-01T00:00:00Z", moving_bodies=[body])
        right = with_backend(tp.search_stations, swiss_backend,
            start_utc="2026-01-01T00:00:00Z", end_utc="2027-01-01T00:00:00Z", moving_bodies=[body])
        station_pairs[body] = {
            "astronomy_engine_count": len(left), "pyswisseph_count": len(right),
            "rows": compact_pair(left, right, ("transition", "longitude_deg")),
        }

    ae_ing = with_backend(tp.search_ingresses, ap._longitude_and_speed,
        start_utc="2026-08-01T00:00:00Z", end_utc="2026-12-31T23:59:59Z", moving_bodies=["Venus"])
    sw_ing = with_backend(tp.search_ingresses, swiss_backend,
        start_utc="2026-08-01T00:00:00Z", end_utc="2026-12-31T23:59:59Z", moving_bodies=["Venus"])
    ae_210 = [x for x in ae_ing if abs(float(x["boundary_longitude_deg"]) - 210.0) < 1e-9]
    sw_210 = [x for x in sw_ing if abs(float(x["boundary_longitude_deg"]) - 210.0) < 1e-9]

    houses = whole_sign_natal()
    ae_house = with_backend(tp.search_house_ingresses, ap._longitude_and_speed, houses,
        start_utc="2026-03-19T00:00:00Z", end_utc="2026-03-22T00:00:00Z", moving_bodies=["Sun"])
    sw_house = with_backend(tp.search_house_ingresses, swiss_backend, houses,
        start_utc="2026-03-19T00:00:00Z", end_utc="2026-03-22T00:00:00Z", moving_bodies=["Sun"])
    ae_house = [x for x in ae_house if x["to_house"] == 1]
    sw_house = [x for x in sw_house if x["to_house"] == 1]

    ae_context = with_backend(tp.transit_house_context, ap._longitude_and_speed, houses,
        at_utc="2026-03-20T12:00:00Z", moving_bodies=["Sun"])
    sw_context = with_backend(tp.transit_house_context, swiss_backend, houses,
        at_utc="2026-03-20T12:00:00Z", moving_bodies=["Sun"])

    ae_station = with_backend(tp.search_stations, ap._longitude_and_speed,
        start_utc="2026-06-20T00:00:00Z", end_utc="2026-07-05T00:00:00Z", moving_bodies=["Mercury"])[0]
    sw_station = with_backend(tp.search_stations, swiss_backend,
        start_utc="2026-06-20T00:00:00Z", end_utc="2026-07-05T00:00:00Z", moving_bodies=["Mercury"])[0]
    fixed_target = float(ae_station["longitude_deg"])
    tangent_natal = minimal_natal(fixed_target)
    ae_tangent = with_backend(tp.search_transit_to_natal, ap._longitude_and_speed, tangent_natal,
        start_utc="2026-06-20T00:00:00Z", end_utc="2026-07-05T00:00:00Z",
        moving_bodies=["Mercury"], natal_targets=["Mercury"], aspects=["conjunction"])
    sw_tangent = with_backend(tp.search_transit_to_natal, swiss_backend, tangent_natal,
        start_utc="2026-06-20T00:00:00Z", end_utc="2026-07-05T00:00:00Z",
        moving_bodies=["Mercury"], natal_targets=["Mercury"], aspects=["conjunction"])

    return {
        "mercury_three_pass": {
            "astronomy_engine_count": len(ae_three), "pyswisseph_count": len(sw_three),
            "rows": compact_pair(ae_three, sw_three, ("motion_direction", "root_kind", "speed_deg_per_day")),
        },
        "stations_2026": station_pairs,
        "venus_210_boundary": {
            "astronomy_engine_count": len(ae_210), "pyswisseph_count": len(sw_210),
            "rows": compact_pair(ae_210, sw_210, ("motion_direction", "ingress_type", "from_sign", "to_sign")),
        },
        "sun_whole_sign_house_1_ingress": {
            "astronomy_engine_count": len(ae_house), "pyswisseph_count": len(sw_house),
            "rows": compact_pair(ae_house, sw_house, ("from_house", "to_house", "motion_direction")),
        },
        "sun_house_context": {
            "astronomy_engine_house": ae_context[0]["house_number"],
            "pyswisseph_house": sw_context[0]["house_number"],
            "astronomy_engine_longitude_deg": ae_context[0]["longitude_deg"],
            "pyswisseph_longitude_deg": sw_context[0]["longitude_deg"],
            "longitude_difference_deg": circular_diff(ae_context[0]["longitude_deg"], sw_context[0]["longitude_deg"]),
        },
        "tangential_station_fixed_target": {
            "fixed_target_source": "Astronomy Engine Mercury station longitude",
            "fixed_target_longitude_deg": fixed_target,
            "astronomy_engine_station_time_utc": ae_station["exact_time_utc"],
            "pyswisseph_station_time_utc": sw_station["exact_time_utc"],
            "station_longitude_difference_deg": circular_diff(float(ae_station["longitude_deg"]), float(sw_station["longitude_deg"])),
            "station_longitude_difference_arcsec": circular_diff(float(ae_station["longitude_deg"]), float(sw_station["longitude_deg"])) * 3600.0,
            "admitted_tangential_detection_tolerance_deg": tp.TANGENTIAL_STATION_ANGLE_TOLERANCE_DEG,
            "admitted_tangential_detection_tolerance_arcsec": tp.TANGENTIAL_STATION_ANGLE_TOLERANCE_DEG * 3600.0,
            "astronomy_engine_exact_event_count": len(ae_tangent),
            "pyswisseph_exact_event_count": len(sw_tangent),
            "astronomy_engine_root_kinds": [x["root_kind"] for x in ae_tangent],
            "pyswisseph_root_kinds": [x["root_kind"] for x in sw_tangent],
        },
    }


def main() -> int:
    pointwise = pointwise_probe()
    events = event_probe()
    all_event_deltas = []
    for section in (events["mercury_three_pass"], events["venus_210_boundary"], events["sun_whole_sign_house_1_ingress"]):
        all_event_deltas.extend(row["absolute_time_delta_seconds"] for row in section["rows"] if row["absolute_time_delta_seconds"] is not None)
    for section in events["stations_2026"].values():
        all_event_deltas.extend(row["absolute_time_delta_seconds"] for row in section["rows"] if row["absolute_time_delta_seconds"] is not None)

    output = {
        "schema_name": "host_native_pyswisseph_transit_parity_research_result",
        "schema_version": "1.0.0",
        "authority": "reference-only-research-evidence",
        "production_authority": False,
        "runtime": {
            "python": sys.version.split()[0],
            "pyswisseph_version": swe.version,
            "requested_flags": REQUESTED_FLAGS,
            "requested_backend": "SWIEPH|SPEED",
            "observed_effective_backends": pointwise["summary"]["effective_backends"],
            "astronomy_engine_package": f"astronomy-engine=={ap.ASTRONOMY_ENGINE_PACKAGE_VERSION}",
            "astronomy_engine_source_revision": ap.ASTRONOMY_ENGINE_SOURCE_REVISION,
        },
        "comparison_policy": {
            "longitude_reference_ceiling_deg": 0.0167,
            "longitude_reference_ceiling_role": "existing swiss-natal production geometry reference only; not promoted to a transit production tolerance",
            "speed_diagnostic_band_deg_per_day": 0.001,
            "speed_diagnostic_band_role": "research discrepancy screen away from speed-zero roots; stations are judged by zero-crossing topology and event time",
            "event_time_reference_bands_seconds": {"tight": 90.0, "existing_mercury_transit_ceiling": 600.0},
            "event_time_reference_role": "historical/reference bands only; no global transit production tolerance is selected",
        },
        "pointwise": pointwise,
        "event_families": events,
        "event_time_summary": {
            "compared_event_count": len(all_event_deltas),
            "max_absolute_delta_seconds": max(all_event_deltas),
            "within_90_seconds": sum(1 for x in all_event_deltas if x <= 90.0),
            "within_600_seconds": sum(1 for x in all_event_deltas if x <= 600.0),
            "over_600_seconds": sum(1 for x in all_event_deltas if x > 600.0),
        },
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
