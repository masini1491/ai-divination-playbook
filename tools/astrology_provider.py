#!/usr/bin/env python3
"""Astrology Production v1 deterministic natal fact provider.

This provider converts raw birth data into ``astrology_fact_bundle@1.0.0``
using the MIT-licensed Astronomy Engine for geocentric tropical longitudes and
project-owned house/aspect derivation.

The provider intentionally does not geocode place names. Callers must supply
explicit latitude, longitude, and an IANA timezone identifier.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
from itertools import combinations
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import astronomy

from tools.astrology_runtime import MAJOR_ASPECT_ORBS, gate_bundle

PROVIDER_ID = "astronomy-engine-natal-v1"
PROVIDER_VERSION = "1.0.0"
ASTRONOMY_ENGINE_PACKAGE_VERSION = "2.1.19"
ASTRONOMY_ENGINE_SOURCE_REVISION = "865d3da7d8112bbc7911238052c6af4aaf877181"
TRI_HOROSCOPE_REFERENCE_REVISION = "11318426c52c222eea108583ca45420c864825ca"

BODY_NAMES = (
    "Sun",
    "Moon",
    "Mercury",
    "Venus",
    "Mars",
    "Jupiter",
    "Saturn",
    "Uranus",
    "Neptune",
    "Pluto",
    "NorthNode",
)
SIGNS = (
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
)
SUPPORTED_HOUSE_SYSTEMS = {"Whole Sign", "Placidus"}
D2R = math.pi / 180.0
R2D = 180.0 / math.pi
PLACIDUS_MAX_ABS_LATITUDE = 66.0


class ProviderInputError(ValueError):
    """Input cannot be deterministically admitted by the provider."""


def _normalize_degrees(value: float) -> float:
    return value % 360.0


def _signed_delta_degrees(a: float, b: float) -> float:
    """Shortest signed angular delta b-a in [-180, 180)."""
    return ((b - a + 180.0) % 360.0) - 180.0


def _parse_local_datetime(value: str) -> dt.datetime:
    try:
        parsed = dt.datetime.fromisoformat(value)
    except ValueError as exc:
        raise ProviderInputError("local_datetime must be ISO-8601 local wall time") from exc
    if parsed.tzinfo is not None:
        raise ProviderInputError("local_datetime must be naive; timezone_name owns timezone resolution")
    return parsed


def _resolve_local_time(local_value: str, timezone_name: str) -> tuple[dt.datetime, dt.datetime, int]:
    local = _parse_local_datetime(local_value)
    try:
        zone = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError as exc:
        raise ProviderInputError(f"unknown IANA timezone: {timezone_name}") from exc

    candidates: list[tuple[int, dt.datetime]] = []
    for fold in (0, 1):
        aware = local.replace(tzinfo=zone, fold=fold)
        utc = aware.astimezone(dt.timezone.utc)
        roundtrip = utc.astimezone(zone).replace(tzinfo=None)
        if roundtrip == local:
            candidates.append((fold, utc))

    distinct = {(fold, utc) for fold, utc in candidates}
    if not distinct:
        raise ProviderInputError("local_datetime is nonexistent in timezone due to DST transition")

    utc_values = {utc for _, utc in candidates}
    if len(utc_values) > 1:
        raise ProviderInputError("local_datetime is ambiguous in timezone due to DST transition")

    fold = candidates[0][0]
    utc = candidates[0][1]
    aware_local = utc.astimezone(zone)
    return aware_local, utc, fold


def _astronomy_time(when_utc: dt.datetime) -> astronomy.Time:
    return astronomy.Time.Make(
        when_utc.year,
        when_utc.month,
        when_utc.day,
        when_utc.hour,
        when_utc.minute,
        when_utc.second + when_utc.microsecond / 1_000_000.0,
    )


def _mean_obliquity_deg(t: astronomy.Time) -> float:
    # Meeus 22.2 mean obliquity, matching the independently reviewed
    # tri-horoscope Placidus implementation used by our research fixture.
    T = t.tt / 36525.0
    return 23.43929111 - (46.8150 * T + 0.00059 * T * T - 0.001813 * T**3) / 3600.0


def _local_sidereal_hours(t: astronomy.Time, longitude_east_deg: float) -> float:
    return (astronomy.SiderealTime(t) + longitude_east_deg / 15.0) % 24.0


def _ecliptic_longitude(body: str, t: astronomy.Time) -> float:
    if body == "NorthNode":
        T = t.tt / 36525.0
        return _normalize_degrees(
            125.0445479
            - 1934.1362891 * T
            + 0.0020754 * T * T
            + T**3 / 467441.0
            - T**4 / 60616000.0
        )
    if body == "Moon":
        return _normalize_degrees(astronomy.EclipticGeoMoon(t).lon)
    enum_body = getattr(astronomy.Body, body)
    vector = astronomy.GeoVector(enum_body, t, True)
    return _normalize_degrees(astronomy.Ecliptic(vector).elon)


def _longitude_and_speed(body: str, when_utc: dt.datetime) -> tuple[float, float]:
    t0 = _astronomy_time(when_utc)
    lon = _ecliptic_longitude(body, t0)
    half_window = dt.timedelta(hours=1)
    lon_before = _ecliptic_longitude(body, _astronomy_time(when_utc - half_window))
    lon_after = _ecliptic_longitude(body, _astronomy_time(when_utc + half_window))
    delta = _signed_delta_degrees(lon_before, lon_after)
    speed_deg_per_day = delta / 2.0 * 24.0
    return lon, speed_deg_per_day


def _motion_state(speed_deg_per_day: float) -> str:
    if abs(speed_deg_per_day) < 0.01:
        return "stationary"
    return "retrograde" if speed_deg_per_day < 0 else "direct"


def _mc_asc(ramc_deg: float, eps_deg: float, latitude_deg: float) -> tuple[float, float]:
    r = ramc_deg * D2R
    e = eps_deg * D2R
    p = latitude_deg * D2R
    mc = math.atan2(math.sin(r), math.cos(r) * math.cos(e)) * R2D % 360.0
    asc = math.atan2(
        math.cos(r),
        -(math.sin(r) * math.cos(e) + math.tan(p) * math.sin(e)),
    ) * R2D % 360.0
    return mc, asc


def _longitude_from_ra(ra_deg: float, eps_deg: float) -> float:
    r = ra_deg * D2R
    e = eps_deg * D2R
    return math.atan2(math.sin(r), math.cos(r) * math.cos(e)) * R2D % 360.0


def _placidus_cusps(ramc_deg: float, eps_deg: float, latitude_deg: float) -> list[float | None]:
    if abs(latitude_deg) > PLACIDUS_MAX_ABS_LATITUDE:
        raise ProviderInputError(
            f"Placidus is not admitted above |latitude|>{PLACIDUS_MAX_ABS_LATITUDE}° in production v1"
        )

    def solve(frac: float, night: bool) -> float:
        base = ramc_deg + (180.0 if night else 0.0)
        ra = (base + (-1.0 if night else 1.0) * frac * 90.0) % 360.0
        for _ in range(300):
            lam = _longitude_from_ra(ra, eps_deg)
            dec = math.asin(math.sin(eps_deg * D2R) * math.sin(lam * D2R)) * R2D
            x = math.tan(latitude_deg * D2R) * math.tan(dec * D2R)
            if not -1.0 <= x <= 1.0:
                raise ProviderInputError("Placidus geometry is undefined for this latitude/time")
            ad = math.asin(x) * R2D
            arc = (90.0 - ad) if night else (90.0 + ad)
            new_ra = (base + (-1.0 if night else 1.0) * frac * arc) % 360.0
            if abs(_signed_delta_degrees(ra, new_ra)) < 1e-11:
                ra = new_ra
                break
            ra = new_ra
        else:
            raise ProviderInputError("Placidus iteration did not converge")
        return _longitude_from_ra(ra, eps_deg)

    mc, asc = _mc_asc(ramc_deg, eps_deg, latitude_deg)
    cusps: list[float | None] = [None] * 13
    cusps[1] = asc
    cusps[10] = mc
    cusps[11] = solve(1.0 / 3.0, False)
    cusps[12] = solve(2.0 / 3.0, False)
    cusps[2] = solve(2.0 / 3.0, True)
    cusps[3] = solve(1.0 / 3.0, True)
    for house in (1, 2, 3, 10, 11, 12):
        opposite = (house + 5) % 12 + 1
        assert cusps[house] is not None
        cusps[opposite] = (float(cusps[house]) + 180.0) % 360.0
    return cusps


def _whole_sign_cusps(asc_deg: float) -> list[float | None]:
    first_start = math.floor(asc_deg / 30.0) * 30.0
    cusps: list[float | None] = [None] * 13
    for house in range(1, 13):
        cusps[house] = (first_start + (house - 1) * 30.0) % 360.0
    return cusps


def _house_of(longitude_deg: float, cusps: list[float | None]) -> int:
    for house in range(1, 13):
        a = cusps[house]
        b = cusps[house % 12 + 1]
        assert a is not None and b is not None
        span = (float(b) - float(a)) % 360.0
        if (longitude_deg - float(a)) % 360.0 < span:
            return house
    raise RuntimeError("house assignment failed")


def _sign_fields(longitude_deg: float) -> dict[str, Any]:
    index = int(longitude_deg // 30.0)
    return {
        "sign_index": index,
        "sign": SIGNS[index],
        "sign_degree": longitude_deg % 30.0,
    }


def _aspect_name_and_orb(left_deg: float, right_deg: float) -> tuple[str, float] | None:
    separation = abs(_signed_delta_degrees(left_deg, right_deg))
    targets = {
        "conjunction": 0.0,
        "sextile": 60.0,
        "square": 90.0,
        "trine": 120.0,
        "opposition": 180.0,
    }
    candidates = [(name, abs(separation - target)) for name, target in targets.items()]
    name, orb = min(candidates, key=lambda item: item[1])
    if orb <= MAJOR_ASPECT_ORBS[name]:
        return name, orb
    return None


def build_natal_bundle(
    *,
    local_datetime: str,
    timezone_name: str,
    latitude: float,
    longitude: float,
    house_system: str,
    subject_ref: str,
    birth_time_certainty: str = "exact",
) -> dict[str, Any]:
    if not -90.0 <= latitude <= 90.0:
        raise ProviderInputError("latitude must be within [-90, 90]")
    if not -180.0 <= longitude <= 180.0:
        raise ProviderInputError("longitude must be within [-180, 180]")
    if house_system not in SUPPORTED_HOUSE_SYSTEMS:
        raise ProviderInputError(f"unsupported house system: {house_system}")
    if birth_time_certainty not in {"exact", "approximate"}:
        raise ProviderInputError(
            "raw-birth-data provider requires exact or approximate birth time; unknown/rectified use another admitted path"
        )
    if not subject_ref or not subject_ref.strip():
        raise ProviderInputError("subject_ref is required")

    local, utc, fold = _resolve_local_time(local_datetime, timezone_name)
    t = _astronomy_time(utc)
    eps = _mean_obliquity_deg(t)
    lst_hours = _local_sidereal_hours(t, longitude)
    ramc = lst_hours * 15.0
    mc_deg, asc_deg = _mc_asc(ramc, eps, latitude)

    if house_system == "Placidus":
        cusps = _placidus_cusps(ramc, eps, latitude)
    else:
        cusps = _whole_sign_cusps(asc_deg)

    body_data: dict[str, tuple[float, float]] = {
        body: _longitude_and_speed(body, utc) for body in BODY_NAMES
    }

    objects: list[dict[str, Any]] = []
    for body in BODY_NAMES:
        lon, speed = body_data[body]
        row = {
            "fact_id": f"fact:object:{body.lower()}",
            "object_type": "point" if body == "NorthNode" else "planet",
            "object_id": body,
            "longitude_deg": lon,
            "speed_deg_per_day": speed,
            "motion": _motion_state(speed),
            "house_number": _house_of(lon, cusps),
            **_sign_fields(lon),
        }
        objects.append(row)

    objects.extend(
        [
            {
                "fact_id": "fact:angle:ascendant",
                "object_type": "angle",
                "object_id": "Ascendant",
                "longitude_deg": asc_deg,
                **_sign_fields(asc_deg),
            },
            {
                "fact_id": "fact:angle:midheaven",
                "object_type": "angle",
                "object_id": "Midheaven",
                "longitude_deg": mc_deg,
                **_sign_fields(mc_deg),
            },
        ]
    )

    houses = [
        {
            "fact_id": f"fact:house:{house}",
            "house_number": house,
            "cusp_longitude_deg": float(cusps[house]),
            **_sign_fields(float(cusps[house])),
        }
        for house in range(1, 13)
    ]

    aspects: list[dict[str, Any]] = []
    aspect_bodies = [body for body in BODY_NAMES]
    for left, right in combinations(aspect_bodies, 2):
        left_lon = body_data[left][0]
        right_lon = body_data[right][0]
        result = _aspect_name_and_orb(left_lon, right_lon)
        if result is None:
            continue
        name, orb = result
        aspects.append(
            {
                "fact_id": f"fact:aspect:{left.lower()}:{name}:{right.lower()}",
                "aspect": name,
                "orb_deg": orb,
                "left_ref": f"fact:object:{left.lower()}",
                "right_ref": f"fact:object:{right.lower()}",
                "scope": "natal",
            }
        )

    bundle = {
        "schema_name": "astrology_fact_bundle",
        "schema_version": "1.0.0",
        "method": "Astrology",
        "reading_mode": "natal",
        "fact_source": "approved_provider",
        "calculation_verification": "verified_provider",
        "subject_ref": subject_ref,
        "birth_time_certainty": birth_time_certainty,
        "configuration": {
            "zodiac_system": "tropical",
            "center": "geocentric",
            "house_system": house_system,
        },
        "provider": {
            "provider_id": PROVIDER_ID,
            "provider_version": PROVIDER_VERSION,
            "astronomy_engine_package": f"astronomy-engine=={ASTRONOMY_ENGINE_PACKAGE_VERSION}",
            "astronomy_engine_source_revision": ASTRONOMY_ENGINE_SOURCE_REVISION,
            "house_algorithm_reference_revision": TRI_HOROSCOPE_REFERENCE_REVISION,
            "local_datetime": local_datetime,
            "timezone_name": timezone_name,
            "resolved_local_iso": local.isoformat(),
            "resolved_utc_iso": utc.isoformat(),
            "fold": fold,
            "latitude": latitude,
            "longitude": longitude,
            "mean_obliquity_deg": eps,
            "local_sidereal_hours": lst_hours,
            "ramc_deg": ramc,
        },
        "facts": {
            "objects": objects,
            "houses": houses,
            "aspects": aspects,
            "events": [],
        },
    }

    gate = gate_bundle(bundle)
    if not gate["interpretation_allowed"]:
        raise RuntimeError(f"provider generated a bundle rejected by runtime gate: {gate['errors']}")
    return bundle


def main() -> int:
    parser = argparse.ArgumentParser(description="Build an Astrology Production v1 natal fact bundle.")
    parser.add_argument("--local-datetime", required=True, help="ISO local wall time, e.g. 1990-06-15T10:00:00")
    parser.add_argument("--timezone", required=True, dest="timezone_name", help="IANA timezone, e.g. Australia/Sydney")
    parser.add_argument("--latitude", required=True, type=float)
    parser.add_argument("--longitude", required=True, type=float)
    parser.add_argument("--house-system", required=True, choices=sorted(SUPPORTED_HOUSE_SYSTEMS))
    parser.add_argument("--subject-ref", required=True)
    parser.add_argument("--birth-time-certainty", default="exact", choices=["exact", "approximate"])
    args = parser.parse_args()
    try:
        bundle = build_natal_bundle(**vars(args))
    except ProviderInputError as exc:
        print(json.dumps({"status": "input_error", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2
    print(json.dumps(bundle, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
