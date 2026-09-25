#!/usr/bin/env python3
"""Astrology Production v1 deterministic transit event-search provider.

Consumes an admitted natal Astrology Fact Bundle and searches bounded UTC
intervals using Astronomy Engine-backed longitude/speed calculations from the
production natal provider. It emits a transit-mode Astrology Fact Bundle 1.0.

Supported event families:
- transit-to-natal major-aspect exact roots, including tangential station hits;
- stations (longitude-speed zero crossings);
- tropical zodiac ingresses / retrograde returns / direct re-ingresses.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from typing import Any, Callable, Iterable

from tools.astrology_provider import (
    ASTRONOMY_ENGINE_PACKAGE_VERSION,
    ASTRONOMY_ENGINE_SOURCE_REVISION,
    BODY_NAMES,
    _longitude_and_speed,
    _normalize_degrees,
    _house_of,
    _signed_delta_degrees,
)
from tools.astrology_runtime import MAJOR_ASPECT_ORBS, gate_bundle

PROVIDER_ID = "astronomy-engine-transit-v1"
PROVIDER_VERSION = "1.0.0"
MAX_SEARCH_DAYS = 400.0
DEFAULT_STEP_HOURS = 3.0
ROOT_TOLERANCE_SECONDS = 0.5
TANGENTIAL_STATION_ANGLE_TOLERANCE_DEG = 1e-4
UTC = dt.timezone.utc

ASPECT_ANGLES = {
    "conjunction": (0.0,),
    "opposition": (180.0,),
    "trine": (120.0, -120.0),
    "square": (90.0, -90.0),
    "sextile": (60.0, -60.0),
}


class TransitProviderInputError(ValueError):
    """Transit search request cannot be admitted deterministically."""


def _parse_utc(value: str) -> dt.datetime:
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise TransitProviderInputError("UTC timestamp must be ISO-8601") from exc
    if parsed.tzinfo is None:
        raise TransitProviderInputError("UTC timestamp must include timezone")
    return parsed.astimezone(UTC)


def _validate_window(start_utc: str, end_utc: str) -> tuple[dt.datetime, dt.datetime]:
    start = _parse_utc(start_utc)
    end = _parse_utc(end_utc)
    if end <= start:
        raise TransitProviderInputError("end_utc must be later than start_utc")
    if (end - start).total_seconds() > MAX_SEARCH_DAYS * 86400.0:
        raise TransitProviderInputError(f"production v1 transit search is bounded to {MAX_SEARCH_DAYS:g} days")
    return start, end


def _bisect_root(
    func: Callable[[dt.datetime], float],
    left: dt.datetime,
    right: dt.datetime,
    *,
    tolerance_seconds: float = ROOT_TOLERANCE_SECONDS,
) -> dt.datetime:
    f_left = func(left)
    f_right = func(right)
    if abs(f_left) < 1e-12:
        return left
    if abs(f_right) < 1e-12:
        return right
    if f_left * f_right > 0:
        raise TransitProviderInputError("root is not bracketed")
    for _ in range(100):
        middle = left + (right - left) / 2
        f_middle = func(middle)
        if abs(f_middle) < 1e-10 or (right - left).total_seconds() <= tolerance_seconds:
            return middle
        if f_left * f_middle <= 0:
            right = middle
            f_right = f_middle
        else:
            left = middle
            f_left = f_middle
    return left + (right - left) / 2


def _longitude_error(body: str, target_deg: float, when: dt.datetime) -> float:
    longitude, _ = _longitude_and_speed(body, when)
    return _signed_delta_degrees(target_deg, longitude)


def _dedupe_times(times: Iterable[dt.datetime], *, tolerance_seconds: float = 2.0) -> list[dt.datetime]:
    ordered = sorted(times)
    output: list[dt.datetime] = []
    for item in ordered:
        if not output or abs((item - output[-1]).total_seconds()) > tolerance_seconds:
            output.append(item)
    return output


def _find_longitude_crossings(
    body: str,
    target_deg: float,
    start: dt.datetime,
    end: dt.datetime,
    *,
    step_hours: float = DEFAULT_STEP_HOURS,
) -> list[dt.datetime]:
    step = dt.timedelta(hours=step_hours)
    roots: list[dt.datetime] = []
    current = start
    current_error = _longitude_error(body, target_deg, current)
    while current < end:
        nxt = min(current + step, end)
        next_error = _longitude_error(body, target_deg, nxt)
        if current_error == 0 or next_error == 0 or (
            current_error * next_error < 0 and abs(current_error - next_error) < 180.0
        ):
            roots.append(
                _bisect_root(
                    lambda when: _longitude_error(body, target_deg, when),
                    current,
                    nxt,
                )
            )
        current = nxt
        current_error = next_error
    return _dedupe_times(roots)


def _find_station_roots(
    body: str,
    start: dt.datetime,
    end: dt.datetime,
    *,
    step_hours: float = 6.0,
) -> list[dt.datetime]:
    step = dt.timedelta(hours=step_hours)
    roots: list[dt.datetime] = []
    current = start
    current_speed = _longitude_and_speed(body, current)[1]
    while current < end:
        nxt = min(current + step, end)
        next_speed = _longitude_and_speed(body, nxt)[1]
        if current_speed == 0 or next_speed == 0 or current_speed * next_speed < 0:
            roots.append(
                _bisect_root(
                    lambda when: _longitude_and_speed(body, when)[1],
                    current,
                    nxt,
                )
            )
        current = nxt
        current_speed = next_speed
    return _dedupe_times(roots, tolerance_seconds=60.0)


def _motion_direction(speed: float) -> str:
    if abs(speed) < 1e-5:
        return "stationary"
    return "retrograde" if speed < 0 else "direct"


def _iso_utc(when: dt.datetime) -> str:
    return when.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _natal_planet_longitudes(natal_bundle: dict[str, Any]) -> dict[str, float]:
    gate = gate_bundle(natal_bundle)
    if not gate["interpretation_allowed"] or natal_bundle.get("reading_mode") != "natal":
        raise TransitProviderInputError("natal_bundle must be an admitted natal Astrology Fact Bundle")
    output: dict[str, float] = {}
    for row in natal_bundle.get("facts", {}).get("objects", []):
        if not isinstance(row, dict):
            continue
        object_id = row.get("object_id")
        longitude = row.get("longitude_deg")
        if object_id in BODY_NAMES and isinstance(longitude, (int, float)):
            output[str(object_id)] = float(longitude) % 360.0
    if not output:
        raise TransitProviderInputError("natal bundle contains no supported natal planet/point longitudes")
    return output



def _natal_house_cusps(natal_bundle: dict[str, Any]) -> dict[int, float]:
    gate = gate_bundle(natal_bundle)
    if not gate["interpretation_allowed"] or natal_bundle.get("reading_mode") != "natal":
        raise TransitProviderInputError("natal_bundle must be an admitted natal Astrology Fact Bundle")
    certainty = natal_bundle.get("birth_time_certainty")
    if certainty in {"unknown", "approximate"}:
        raise TransitProviderInputError("transit house context requires exact or rectified natal time")
    rows = natal_bundle.get("facts", {}).get("houses", [])
    cusps = {row.get("house_number"): float(row["cusp_longitude_deg"]) % 360.0 for row in rows if isinstance(row, dict) and isinstance(row.get("house_number"), int) and isinstance(row.get("cusp_longitude_deg"), (int, float))}
    if set(cusps) != set(range(1, 13)):
        raise TransitProviderInputError("transit house context requires all 12 admitted natal house cusps")
    return cusps

def transit_house_context(natal_bundle: dict[str, Any], *, at_utc: str, moving_bodies: Iterable[str]) -> list[dict[str, Any]]:
    when = _parse_utc(at_utc)
    cusps = _natal_house_cusps(natal_bundle)
    rows = []
    for body in moving_bodies:
        if body not in BODY_NAMES or body == "NorthNode":
            raise TransitProviderInputError(f"transit house context unsupported for body: {body}")
        longitude, speed = _longitude_and_speed(body, when)
        rows.append({"fact_id": f"fact:event:transit-house-context:{body.lower()}:{int(when.timestamp())}","event_kind":"transit_house_context","moving_body":body,"exact_time_utc":_iso_utc(when),"longitude_deg":longitude,"house_number":_house_of(longitude,cusps),"motion_direction":_motion_direction(speed),"speed_deg_per_day":speed})
    return rows

def search_transit_house_ingresses(natal_bundle: dict[str, Any], *, start_utc: str, end_utc: str, moving_bodies: Iterable[str]) -> list[dict[str, Any]]:
    start,end=_validate_window(start_utc,end_utc)
    cusps=_natal_house_cusps(natal_bundle)
    events=[]
    for body in moving_bodies:
        if body not in BODY_NAMES or body == "NorthNode":
            raise TransitProviderInputError(f"transit house search unsupported for body: {body}")
        for house,cusp in sorted(cusps.items()):
            for root in _find_longitude_crossings(body,cusp,start,end):
                longitude,speed=_longitude_and_speed(body,root)
                direction=_motion_direction(speed)
                if direction=="stationary":
                    continue
                if direction=="direct":
                    from_house=12 if house==1 else house-1; to_house=house
                else:
                    from_house=house; to_house=12 if house==1 else house-1
                events.append({"fact_id":f"fact:event:transit-house-ingress:{body.lower()}:{house}:{int(root.timestamp())}","event_kind":"transit_house_ingress","moving_body":body,"exact_time_utc":_iso_utc(root),"cusp_house_number":house,"cusp_longitude_deg":cusp,"from_house":from_house,"to_house":to_house,"longitude_deg":longitude,"motion_direction":direction,"speed_deg_per_day":speed})
    return sorted(events,key=lambda row:(row["exact_time_utc"],row["fact_id"]))

def search_transit_to_natal(
    natal_bundle: dict[str, Any],
    *,
    start_utc: str,
    end_utc: str,
    moving_bodies: Iterable[str],
    natal_targets: Iterable[str],
    aspects: Iterable[str],
) -> list[dict[str, Any]]:
    start, end = _validate_window(start_utc, end_utc)
    natal = _natal_planet_longitudes(natal_bundle)
    events: list[dict[str, Any]] = []

    for body in moving_bodies:
        if body not in BODY_NAMES or body == "NorthNode":
            raise TransitProviderInputError(f"unsupported moving body: {body}")
        station_roots = [] if body in {"Sun", "Moon"} else _find_station_roots(body, start, end)
        for target_id in natal_targets:
            if target_id not in natal:
                raise TransitProviderInputError(f"natal target unavailable: {target_id}")
            natal_lon = natal[target_id]
            for aspect in aspects:
                if aspect not in ASPECT_ANGLES:
                    raise TransitProviderInputError(f"unsupported aspect: {aspect}")
                roots: list[tuple[dt.datetime, float, str]] = []
                for delta in ASPECT_ANGLES[aspect]:
                    target_lon = _normalize_degrees(natal_lon + delta)
                    for root in _find_longitude_crossings(body, target_lon, start, end):
                        roots.append((root, target_lon, "crossing"))
                    for station in station_roots:
                        if abs(_longitude_error(body, target_lon, station)) <= TANGENTIAL_STATION_ANGLE_TOLERANCE_DEG:
                            roots.append((station, target_lon, "tangential_station"))

                roots.sort(key=lambda item: item[0])
                deduped: list[tuple[dt.datetime, float, str]] = []
                for root, target_lon, root_kind in roots:
                    if deduped and abs((root - deduped[-1][0]).total_seconds()) <= 2.0:
                        if root_kind == "tangential_station":
                            previous = deduped[-1]
                            deduped[-1] = (previous[0], previous[1], root_kind)
                        continue
                    deduped.append((root, target_lon, root_kind))

                for passage_index, (root, target_lon, root_kind) in enumerate(deduped, start=1):
                    transit_lon, speed = _longitude_and_speed(body, root)
                    events.append(
                        {
                            "fact_id": f"fact:event:transit:{body.lower()}:{aspect}:{target_id.lower()}:{passage_index}:{int(root.timestamp())}",
                            "event_kind": "transit_to_natal",
                            "moving_body": body,
                            "natal_target": target_id,
                            "natal_longitude_deg": natal_lon,
                            "aspect": aspect,
                            "aspect_branch_deg": _signed_delta_degrees(natal_lon, target_lon),
                            "exact_time_utc": _iso_utc(root),
                            "transit_longitude_deg": transit_lon,
                            "target_longitude_deg": target_lon,
                            "angular_residual_deg": abs(_signed_delta_degrees(target_lon, transit_lon)),
                            "motion_direction": _motion_direction(speed),
                            "speed_deg_per_day": speed,
                            "root_kind": root_kind,
                            "passage_index": passage_index,
                            "passage_count": len(deduped),
                        }
                    )
    return sorted(events, key=lambda row: (row["exact_time_utc"], row["fact_id"]))


def search_stations(*, start_utc: str, end_utc: str, moving_bodies: Iterable[str]) -> list[dict[str, Any]]:
    start, end = _validate_window(start_utc, end_utc)
    events: list[dict[str, Any]] = []
    for body in moving_bodies:
        if body not in BODY_NAMES or body in {"Sun", "Moon", "NorthNode"}:
            raise TransitProviderInputError(f"station search unsupported for body: {body}")
        roots = _find_station_roots(body, start, end)
        for index, root in enumerate(roots, start=1):
            longitude, speed = _longitude_and_speed(body, root)
            before = _longitude_and_speed(body, root - dt.timedelta(hours=12))[1]
            after = _longitude_and_speed(body, root + dt.timedelta(hours=12))[1]
            if before > 0 and after < 0:
                transition = "direct_to_retrograde"
            elif before < 0 and after > 0:
                transition = "retrograde_to_direct"
            else:
                transition = "unresolved"
            events.append(
                {
                    "fact_id": f"fact:event:station:{body.lower()}:{index}:{int(root.timestamp())}",
                    "event_kind": "station",
                    "moving_body": body,
                    "exact_time_utc": _iso_utc(root),
                    "longitude_deg": longitude,
                    "speed_at_root_deg_per_day": speed,
                    "speed_12h_before_deg_per_day": before,
                    "speed_12h_after_deg_per_day": after,
                    "transition": transition,
                }
            )
    return sorted(events, key=lambda row: (row["exact_time_utc"], row["fact_id"]))


def search_ingresses(*, start_utc: str, end_utc: str, moving_bodies: Iterable[str]) -> list[dict[str, Any]]:
    start, end = _validate_window(start_utc, end_utc)
    sign_names = (
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
    )
    events: list[dict[str, Any]] = []
    for body in moving_bodies:
        if body not in BODY_NAMES or body == "NorthNode":
            raise TransitProviderInputError(f"ingress search unsupported for body: {body}")
        roots: list[tuple[dt.datetime, float]] = []
        for boundary in range(0, 360, 30):
            for root in _find_longitude_crossings(body, float(boundary), start, end):
                roots.append((root, float(boundary)))
        roots.sort(key=lambda item: item[0])
        retrograde_returned_boundaries: set[float] = set()
        for index, (root, boundary) in enumerate(roots, start=1):
            longitude, speed = _longitude_and_speed(body, root)
            before_lon = _longitude_and_speed(body, root - dt.timedelta(minutes=5))[0]
            after_lon = _longitude_and_speed(body, root + dt.timedelta(minutes=5))[0]
            before_sign = int(before_lon // 30.0)
            after_sign = int(after_lon // 30.0)
            if before_sign == after_sign:
                continue
            direction = _motion_direction(speed)
            if direction == "retrograde":
                semantic_kind = "retrograde_return"
                retrograde_returned_boundaries.add(boundary)
            elif boundary in retrograde_returned_boundaries:
                semantic_kind = "direct_reingress"
                retrograde_returned_boundaries.remove(boundary)
            else:
                semantic_kind = "direct_ingress"
            events.append(
                {
                    "fact_id": f"fact:event:ingress:{body.lower()}:{index}:{int(root.timestamp())}",
                    "event_kind": "ingress",
                    "moving_body": body,
                    "exact_time_utc": _iso_utc(root),
                    "boundary_longitude_deg": boundary,
                    "longitude_deg": longitude,
                    "motion_direction": direction,
                    "from_sign": sign_names[before_sign],
                    "to_sign": sign_names[after_sign],
                    "ingress_type": semantic_kind,
                    "speed_deg_per_day": speed,
                }
            )
    return sorted(events, key=lambda row: (row["exact_time_utc"], row["fact_id"]))


def build_transit_bundle(
    natal_bundle: dict[str, Any],
    *,
    start_utc: str,
    end_utc: str,
    subject_ref: str,
    moving_bodies: Iterable[str],
    natal_targets: Iterable[str],
    aspects: Iterable[str],
    include_stations: bool = True,
    include_ingresses: bool = True,
) -> dict[str, Any]:
    start, end = _validate_window(start_utc, end_utc)
    moving = tuple(dict.fromkeys(moving_bodies))
    targets = tuple(dict.fromkeys(natal_targets))
    aspect_names = tuple(dict.fromkeys(aspects))
    if not moving:
        raise TransitProviderInputError("at least one moving body is required")
    if not targets:
        raise TransitProviderInputError("at least one natal target is required")
    if not aspect_names:
        raise TransitProviderInputError("at least one aspect is required")
    if not subject_ref or not subject_ref.strip():
        raise TransitProviderInputError("subject_ref is required")

    events = search_transit_to_natal(
        natal_bundle,
        start_utc=start_utc,
        end_utc=end_utc,
        moving_bodies=moving,
        natal_targets=targets,
        aspects=aspect_names,
    )
    if include_stations:
        station_bodies = [body for body in moving if body not in {"Sun", "Moon", "NorthNode"}]
        if station_bodies:
            events.extend(search_stations(start_utc=start_utc, end_utc=end_utc, moving_bodies=station_bodies))
    if include_ingresses:
        ingress_bodies = [body for body in moving if body != "NorthNode"]
        if ingress_bodies:
            events.extend(search_ingresses(start_utc=start_utc, end_utc=end_utc, moving_bodies=ingress_bodies))
    events.sort(key=lambda row: (row["exact_time_utc"], row["fact_id"]))

    bundle = {
        "schema_name": "astrology_fact_bundle",
        "schema_version": "1.0.0",
        "method": "Astrology",
        "reading_mode": "transit",
        "fact_source": "approved_provider",
        "calculation_verification": "verified_provider",
        "subject_ref": subject_ref,
        "birth_time_certainty": natal_bundle.get("birth_time_certainty"),
        "configuration": {
            "zodiac_system": "tropical",
            "center": "geocentric",
            "house_system": natal_bundle.get("configuration", {}).get("house_system"),
        },
        "provider": {
            "provider_id": PROVIDER_ID,
            "provider_version": PROVIDER_VERSION,
            "astronomy_engine_package": f"astronomy-engine=={ASTRONOMY_ENGINE_PACKAGE_VERSION}",
            "astronomy_engine_source_revision": ASTRONOMY_ENGINE_SOURCE_REVISION,
            "search_start_utc": _iso_utc(start),
            "search_end_utc": _iso_utc(end),
            "root_tolerance_seconds": ROOT_TOLERANCE_SECONDS,
            "tangential_station_angle_tolerance_deg": TANGENTIAL_STATION_ANGLE_TOLERANCE_DEG,
            "default_step_hours": DEFAULT_STEP_HOURS,
            "natal_source_provider": natal_bundle.get("provider", {}).get("provider_id"),
        },
        "facts": {"objects": [], "houses": [], "aspects": [], "events": events},
    }
    gate = gate_bundle(bundle)
    if not gate["interpretation_allowed"]:
        raise RuntimeError(f"provider generated a bundle rejected by production gate: {gate['errors']}")
    return bundle


def main() -> int:
    parser = argparse.ArgumentParser(description="Search deterministic Astrology transit events.")
    parser.add_argument("natal_bundle")
    parser.add_argument("--start-utc", required=True)
    parser.add_argument("--end-utc", required=True)
    parser.add_argument("--subject-ref", required=True)
    parser.add_argument("--moving-body", action="append", required=True)
    parser.add_argument("--natal-target", action="append", required=True)
    parser.add_argument("--aspect", action="append", required=True, choices=sorted(MAJOR_ASPECT_ORBS))
    parser.add_argument("--no-stations", action="store_true")
    parser.add_argument("--no-ingresses", action="store_true")
    args = parser.parse_args()
    try:
        with open(args.natal_bundle, encoding="utf-8") as handle:
            natal_bundle = json.load(handle)
        bundle = build_transit_bundle(
            natal_bundle,
            start_utc=args.start_utc,
            end_utc=args.end_utc,
            subject_ref=args.subject_ref,
            moving_bodies=args.moving_body,
            natal_targets=args.natal_target,
            aspects=args.aspect,
            include_stations=not args.no_stations,
            include_ingresses=not args.no_ingresses,
        )
    except (OSError, json.JSONDecodeError, TransitProviderInputError, RuntimeError) as exc:
        print(json.dumps({"status": "rejected", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(bundle, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
