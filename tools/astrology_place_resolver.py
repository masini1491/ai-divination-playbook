#!/usr/bin/env python3
"""Offline place-name resolver for Astrology production inputs.

This module is input-resolution infrastructure, not astronomical authority.
It uses the packaged GeoNames city dataset exposed by ``geonamescache``.
Ambiguous names fail closed unless a country code is supplied and leaves a
single exact match.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import geonamescache

RESOLVER_ID = "geonamescache-city-v1"
RESOLVER_VERSION = "1.1.0"
GEONAMESCACHE_VERSION = geonamescache.__version__
GEONAMESCACHE_SOURCE_REVISION = "df4f6497b321f7981645ab0c5c77d3354c63bd01"
TAIWAN_ADMIN_POLICY_PATH = Path(__file__).resolve().parents[1] / "runtime" / "astrology" / "TW_ADMIN_LOCALITY_V1.json"
TAIWAN_ADMIN_POLICY_ID = "taiwan-admin-locality-v1"


class PlaceResolutionError(ValueError):
    """Place input cannot be resolved uniquely under production policy."""


@dataclass(frozen=True)
class PlaceCandidate:
    geoname_id: int
    name: str
    country_code: str
    admin1_code: str
    latitude: float
    longitude: float
    timezone_name: str
    population: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "geoname_id": self.geoname_id,
            "name": self.name,
            "country_code": self.country_code,
            "admin1_code": self.admin1_code,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timezone_name": self.timezone_name,
            "population": self.population,
        }


def _candidate(row: dict[str, Any]) -> PlaceCandidate:
    return PlaceCandidate(
        geoname_id=int(row["geonameid"]),
        name=str(row["name"]),
        country_code=str(row["countrycode"]),
        admin1_code=str(row.get("admin1code", "")),
        latitude=float(row["latitude"]),
        longitude=float(row["longitude"]),
        timezone_name=str(row["timezone"]),
        population=int(row.get("population", 0)),
    )


@lru_cache(maxsize=1)
def _taiwan_admin_policy() -> dict[str, Any]:
    try:
        data = json.loads(TAIWAN_ADMIN_POLICY_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PlaceResolutionError("Taiwan administrative locality policy unavailable or malformed") from exc
    if (
        data.get("schema_name") != "astrology_taiwan_admin_locality_policy"
        or data.get("policy_id") != TAIWAN_ADMIN_POLICY_ID
        or data.get("status") != "PRODUCTION_ADMITTED_INPUT_NORMALIZATION"
        or data.get("country_code") != "TW"
        or not isinstance(data.get("hierarchy"), dict)
    ):
        raise PlaceResolutionError("Taiwan administrative locality policy identity mismatch")
    return data


def normalize_place_query(name: str, *, country_code: str | None = None) -> dict[str, Any]:
    if not name or not name.strip():
        raise PlaceResolutionError("place name is required")
    raw_name = name.strip()
    supplied_country = country_code.upper() if country_code else None
    canonical = raw_name.replace("台", "臺")
    policy = _taiwan_admin_policy()
    hierarchy: dict[str, list[str]] = policy["hierarchy"]
    admin_area = next((city for city in hierarchy if canonical.startswith(city)), None)

    if admin_area is None:
        return {
            "raw_name": raw_name,
            "normalized_name": raw_name,
            "supplied_country_code": supplied_country,
            "effective_country_code": supplied_country,
            "normalization_policy_id": None,
            "admin_area": None,
            "hierarchy_validated": False,
            "script_normalization_applied": False,
        }

    if supplied_country is not None and supplied_country != "TW":
        raise PlaceResolutionError(
            "Taiwan administrative locality input conflicts with supplied country_code; fail closed"
        )

    remainder = canonical[len(admin_area):]
    if not remainder:
        return {
            "raw_name": raw_name,
            "normalized_name": canonical,
            "supplied_country_code": supplied_country,
            "effective_country_code": "TW",
            "normalization_policy_id": TAIWAN_ADMIN_POLICY_ID,
            "admin_area": admin_area,
            "hierarchy_validated": True,
            "script_normalization_applied": canonical != raw_name,
        }

    if remainder not in hierarchy[admin_area]:
        raise PlaceResolutionError(
            "Taiwan administrative locality hierarchy mismatch or unsupported locality; fail closed"
        )

    return {
        "raw_name": raw_name,
        "normalized_name": remainder,
        "supplied_country_code": supplied_country,
        "effective_country_code": "TW",
        "normalization_policy_id": TAIWAN_ADMIN_POLICY_ID,
        "admin_area": admin_area,
        "hierarchy_validated": True,
        "script_normalization_applied": canonical != raw_name,
    }


def search_place_candidates(
    name: str,
    *,
    country_code: str | None = None,
    min_city_population: int = 500,
) -> list[PlaceCandidate]:
    if not name or not name.strip():
        raise PlaceResolutionError("place name is required")
    if min_city_population not in {500, 1000, 5000, 15000}:
        raise PlaceResolutionError("min_city_population must be one of 500, 1000, 5000, 15000")

    cache = geonamescache.GeonamesCache(min_city_population=min_city_population)
    normalization = normalize_place_query(name, country_code=country_code)
    query = normalization["normalized_name"]
    rows = cache.search_cities(query, case_sensitive=False, contains_search=False)
    country = normalization["effective_country_code"]
    if country:
        rows = [row for row in rows if str(row.get("countrycode", "")).upper() == country]

    # GeoNames alternate names can make the same geoname appear only once in this
    # API, but dedupe by geonameid anyway so ambiguity is about places, not aliases.
    unique: dict[int, PlaceCandidate] = {}
    for row in rows:
        cand = _candidate(row)
        unique[cand.geoname_id] = cand
    return sorted(unique.values(), key=lambda c: (-c.population, c.country_code, c.name, c.geoname_id))


def resolve_place(
    name: str,
    *,
    country_code: str | None = None,
    min_city_population: int = 500,
) -> dict[str, Any]:
    candidates = search_place_candidates(
        name,
        country_code=country_code,
        min_city_population=min_city_population,
    )
    if not candidates:
        raise PlaceResolutionError("place not found in offline GeoNames city dataset")
    if len(candidates) != 1:
        preview = [c.as_dict() for c in candidates[:10]]
        raise PlaceResolutionError(
            "place name is ambiguous; provide country_code or explicit coordinates. "
            f"candidate_count={len(candidates)} candidates={json.dumps(preview, ensure_ascii=False)}"
        )

    candidate = candidates[0]
    normalization = normalize_place_query(name, country_code=country_code)
    return {
        "resolver": {
            "resolver_id": RESOLVER_ID,
            "resolver_version": RESOLVER_VERSION,
            "package": f"geonamescache=={GEONAMESCACHE_VERSION}",
            "source_revision": GEONAMESCACHE_SOURCE_REVISION,
            "dataset_origin": "GeoNames",
            "dataset_license": "CC-BY-4.0",
        },
        "query": {
            "name": name,
            "country_code": country_code,
            "normalization": normalization,
        },
        "resolved": candidate.as_dict(),
    }



def resolve_country_timezone(
    name: str | None = None,
    *,
    country_code: str | None = None,
    min_city_population: int = 500,
) -> dict[str, Any]:
    if not name and not country_code:
        raise PlaceResolutionError("country name or country_code is required")
    if min_city_population not in {500, 1000, 5000, 15000}:
        raise PlaceResolutionError("min_city_population must be one of 500, 1000, 5000, 15000")

    cache = geonamescache.GeonamesCache(min_city_population=min_city_population)
    countries = cache.get_countries()
    normalized_code = country_code.upper() if country_code else None
    normalized_name = name.strip().casefold() if name else None
    matches = []
    for code, row in countries.items():
        if normalized_code and code.upper() != normalized_code:
            continue
        if normalized_name and str(row.get("name", "")).casefold() != normalized_name:
            continue
        matches.append(row)

    if not matches:
        raise PlaceResolutionError("country not found in offline GeoNames country dataset")
    if len(matches) != 1:
        raise PlaceResolutionError("country identity is ambiguous; provide ISO alpha-2 country_code")

    country = matches[0]
    code = str(country.get("iso", normalized_code or "")).upper()
    timezones = sorted({
        str(row.get("timezone", "")).strip()
        for row in cache.get_cities().values()
        if str(row.get("countrycode", "")).upper() == code and str(row.get("timezone", "")).strip()
    })
    if len(timezones) != 1:
        raise PlaceResolutionError(
            "country does not resolve to one unique IANA timezone in the admitted offline dataset; "
            f"country_code={code} timezone_count={len(timezones)} timezones={timezones[:10]}"
        )

    return {
        "resolver": {
            "resolver_id": RESOLVER_ID,
            "resolver_version": RESOLVER_VERSION,
            "package": f"geonamescache=={GEONAMESCACHE_VERSION}",
            "source_revision": GEONAMESCACHE_SOURCE_REVISION,
            "dataset_origin": "GeoNames",
            "dataset_license": "CC-BY-4.0",
        },
        "query": {"name": name, "country_code": country_code},
        "resolved": {
            "name": country.get("name"),
            "country_code": code,
            "timezone_name": timezones[0],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve a city/locality to Astrology production coordinates/timezone.")
    parser.add_argument("name")
    parser.add_argument("--country-code")
    parser.add_argument("--min-city-population", type=int, default=500)
    args = parser.parse_args()
    try:
        result = resolve_place(
            args.name,
            country_code=args.country_code,
            min_city_population=args.min_city_population,
        )
    except PlaceResolutionError as exc:
        print(json.dumps({"status": "rejected", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps({"status": "resolved", **result}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
