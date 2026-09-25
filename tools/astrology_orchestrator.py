#!/usr/bin/env python3
"""End-to-end Astrology Production v1 request orchestrator.

This module is composition infrastructure. It does not add astronomical,
geocoding, interpretation, or Reading Record authority. It normalizes one
bounded request, resolves an admitted city/locality when requested, invokes the
existing natal/transit providers, and re-applies the Astrology runtime gate to
every generated Fact Bundle before returning a portable run artifact.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from tools.astrology_provider import (
    BODY_NAMES,
    SUPPORTED_HOUSE_SYSTEMS,
    ProviderInputError,
    build_natal_bundle,
    build_unknown_time_natal_bundle,
)
from tools.astrology_runtime import MAJOR_ASPECT_ORBS, gate_bundle
from tools.astrology_transit_provider import TransitProviderInputError, build_transit_bundle

REQUEST_SCHEMA_NAME = "astrology_reading_request"
REQUEST_SCHEMA_VERSION = "1.0.0"
RUN_SCHEMA_NAME = "astrology_reading_run"
RUN_SCHEMA_VERSION = "1.0.0"
ORCHESTRATOR_ID = "astrology-production-orchestrator-v1"
ORCHESTRATOR_VERSION = "1.0.0"
REQUEST_SCHEMA_PATH = "ASTROLOGY_READING_REQUEST_V1.schema.json"


class OrchestrationInputError(ValueError):
    """A reading request cannot be admitted by the orchestration contract."""

def _load_place_resolver():
    """Load the admitted offline resolver only when place/country input needs it."""
    try:
        from tools.astrology_place_resolver import resolve_country_timezone, resolve_place
    except ModuleNotFoundError as exc:
        if exc.name in {"geonamescache", "tools.astrology_place_resolver"}:
            raise OrchestrationInputError(
                "admitted Astrology place resolver runtime unavailable; "
                "provide explicit coordinates + IANA timezone or materialize the resolver separately"
            ) from exc
        raise
    return resolve_country_timezone, resolve_place



def _object(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise OrchestrationInputError(f"{path} must be an object")
    return value


def _exact_keys(data: dict[str, Any], *, allowed: set[str], required: set[str], path: str) -> None:
    missing = sorted(required - data.keys())
    if missing:
        raise OrchestrationInputError(f"{path} missing required field(s): {', '.join(missing)}")
    extra = sorted(data.keys() - allowed)
    if extra:
        raise OrchestrationInputError(f"{path} contains unsupported field(s): {', '.join(extra)}")


def _non_empty_string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise OrchestrationInputError(f"{path} must be a non-empty string")
    return value.strip()


def _finite_number(value: Any, path: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise OrchestrationInputError(f"{path} must be a number")
    number = float(value)
    if number != number or number in (float("inf"), float("-inf")):
        raise OrchestrationInputError(f"{path} must be finite")
    return number


def _unique_strings(value: Any, path: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise OrchestrationInputError(f"{path} must be a non-empty array")
    output: list[str] = []
    for index, item in enumerate(value):
        text = _non_empty_string(item, f"{path}[{index}]")
        if text in output:
            raise OrchestrationInputError(f"{path} must not contain duplicates: {text}")
        output.append(text)
    return output


def _normalize_location(data: Any) -> dict[str, Any]:
    location = _object(data, "$.birth.location")
    _exact_keys(
        location,
        allowed={"place", "coordinates", "country"},
        required=set(),
        path="$.birth.location",
    )
    if set(location) not in ({"place"}, {"coordinates"}, {"country"}):
        raise OrchestrationInputError("$.birth.location must contain exactly one of place, coordinates, or country")

    if "country" in location:
        country = _object(location["country"], "$.birth.location.country")
        _exact_keys(
            country,
            allowed={"name", "country_code"},
            required=set(),
            path="$.birth.location.country",
        )
        if not country:
            raise OrchestrationInputError("$.birth.location.country requires name or country_code")
        normalized_country: dict[str, Any] = {}
        if country.get("name") is not None:
            normalized_country["name"] = _non_empty_string(country["name"], "$.birth.location.country.name")
        if country.get("country_code") is not None:
            code = _non_empty_string(country["country_code"], "$.birth.location.country.country_code").upper()
            if len(code) != 2 or not code.isalpha():
                raise OrchestrationInputError("$.birth.location.country.country_code must be ISO alpha-2")
            normalized_country["country_code"] = code
        return {"country": normalized_country}

    if "place" in location:
        place = _object(location["place"], "$.birth.location.place")
        _exact_keys(
            place,
            allowed={"name", "country_code"},
            required={"name"},
            path="$.birth.location.place",
        )
        normalized: dict[str, Any] = {
            "place": {
                "name": _non_empty_string(place["name"], "$.birth.location.place.name"),
            }
        }
        country_code = place.get("country_code")
        if country_code is not None:
            code = _non_empty_string(country_code, "$.birth.location.place.country_code").upper()
            if len(code) != 2 or not code.isalpha():
                raise OrchestrationInputError("$.birth.location.place.country_code must be ISO alpha-2")
            normalized["place"]["country_code"] = code
        return normalized

    coordinates = _object(location["coordinates"], "$.birth.location.coordinates")
    _exact_keys(
        coordinates,
        allowed={"latitude", "longitude", "timezone_name"},
        required={"latitude", "longitude", "timezone_name"},
        path="$.birth.location.coordinates",
    )
    latitude = _finite_number(coordinates["latitude"], "$.birth.location.coordinates.latitude")
    longitude = _finite_number(coordinates["longitude"], "$.birth.location.coordinates.longitude")
    if not -90.0 <= latitude <= 90.0:
        raise OrchestrationInputError("$.birth.location.coordinates.latitude must be within [-90, 90]")
    if not -180.0 <= longitude <= 180.0:
        raise OrchestrationInputError("$.birth.location.coordinates.longitude must be within [-180, 180]")
    return {
        "coordinates": {
            "latitude": latitude,
            "longitude": longitude,
            "timezone_name": _non_empty_string(
                coordinates["timezone_name"], "$.birth.location.coordinates.timezone_name"
            ),
        }
    }


def _normalize_transit(data: Any) -> dict[str, Any]:
    transit = _object(data, "$.transit")
    _exact_keys(
        transit,
        allowed={
            "start_utc",
            "end_utc",
            "moving_bodies",
            "natal_targets",
            "aspects",
            "include_transit_to_natal",
            "include_stations",
            "include_ingresses",
            "include_house_ingresses",
        },
        required={"start_utc", "end_utc", "moving_bodies"},
        path="$.transit",
    )
    moving_bodies = _unique_strings(transit["moving_bodies"], "$.transit.moving_bodies")
    for body in moving_bodies:
        if body not in BODY_NAMES or body == "NorthNode":
            raise OrchestrationInputError(f"$.transit.moving_bodies contains unsupported body: {body}")
    include_transit_to_natal = transit.get("include_transit_to_natal", True)
    if not isinstance(include_transit_to_natal, bool):
        raise OrchestrationInputError("$.transit.include_transit_to_natal must be boolean")
    natal_targets = _unique_strings(transit["natal_targets"], "$.transit.natal_targets") if "natal_targets" in transit else []
    for target in natal_targets:
        if target not in BODY_NAMES:
            raise OrchestrationInputError(f"$.transit.natal_targets contains unsupported target: {target}")
    aspects = _unique_strings(transit["aspects"], "$.transit.aspects") if "aspects" in transit else []
    for aspect in aspects:
        if aspect not in MAJOR_ASPECT_ORBS:
            raise OrchestrationInputError(f"$.transit.aspects contains unsupported aspect: {aspect}")
    if include_transit_to_natal and not natal_targets:
        raise OrchestrationInputError("$.transit.natal_targets is required when include_transit_to_natal=true")
    if include_transit_to_natal and not aspects:
        raise OrchestrationInputError("$.transit.aspects is required when include_transit_to_natal=true")

    include_stations = transit.get("include_stations", True)
    include_ingresses = transit.get("include_ingresses", True)
    include_house_ingresses = transit.get("include_house_ingresses", False)
    if not isinstance(include_stations, bool):
        raise OrchestrationInputError("$.transit.include_stations must be boolean")
    if not isinstance(include_ingresses, bool):
        raise OrchestrationInputError("$.transit.include_ingresses must be boolean")
    if not isinstance(include_house_ingresses, bool):
        raise OrchestrationInputError("$.transit.include_house_ingresses must be boolean")
    if not any((include_transit_to_natal, include_stations, include_ingresses, include_house_ingresses)):
        raise OrchestrationInputError("$.transit must enable at least one event family")

    return {
        "start_utc": _non_empty_string(transit["start_utc"], "$.transit.start_utc"),
        "end_utc": _non_empty_string(transit["end_utc"], "$.transit.end_utc"),
        "moving_bodies": moving_bodies,
        "natal_targets": natal_targets,
        "aspects": aspects,
        "include_transit_to_natal": include_transit_to_natal,
        "include_stations": include_stations,
        "include_ingresses": include_ingresses,
        "include_house_ingresses": include_house_ingresses,
    }


def normalize_request(data: Any) -> dict[str, Any]:
    root = _object(data, "$")
    _exact_keys(
        root,
        allowed={"schema_name", "schema_version", "reading_mode", "subject_ref", "birth", "transit"},
        required={"schema_name", "schema_version", "reading_mode", "subject_ref", "birth"},
        path="$",
    )
    if root["schema_name"] != REQUEST_SCHEMA_NAME:
        raise OrchestrationInputError(f"$.schema_name must equal {REQUEST_SCHEMA_NAME}")
    if root["schema_version"] != REQUEST_SCHEMA_VERSION:
        raise OrchestrationInputError(f"$.schema_version must equal {REQUEST_SCHEMA_VERSION}")

    reading_mode = _non_empty_string(root["reading_mode"], "$.reading_mode")
    if reading_mode not in {"natal", "transit"}:
        raise OrchestrationInputError("$.reading_mode must be natal or transit")
    if reading_mode == "natal" and "transit" in root:
        raise OrchestrationInputError("$.transit is only allowed when reading_mode=transit")
    if reading_mode == "transit" and "transit" not in root:
        raise OrchestrationInputError("$.transit is required when reading_mode=transit")

    birth = _object(root["birth"], "$.birth")
    _exact_keys(
        birth,
        allowed={"local_datetime", "local_date", "birth_time_certainty", "house_system", "location"},
        required={"birth_time_certainty", "location"},
        path="$.birth",
    )
    certainty = _non_empty_string(birth["birth_time_certainty"], "$.birth.birth_time_certainty")
    if certainty not in {"exact", "approximate", "unknown"}:
        raise OrchestrationInputError("$.birth.birth_time_certainty must be exact, approximate, or unknown")

    normalized_birth: dict[str, Any] = {
        "birth_time_certainty": certainty,
        "location": _normalize_location(birth["location"]),
    }
    if certainty == "unknown":
        if reading_mode != "natal":
            raise OrchestrationInputError("unknown birth time is admitted only for natal invariant-only readings")
        if "local_date" not in birth:
            raise OrchestrationInputError("$.birth.local_date is required when birth_time_certainty=unknown")
        if "local_datetime" in birth:
            raise OrchestrationInputError("$.birth.local_datetime must not be supplied when birth_time_certainty=unknown")
        if birth.get("house_system") not in (None,):
            raise OrchestrationInputError("$.birth.house_system must be null or omitted when birth_time_certainty=unknown")
        normalized_birth["local_date"] = _non_empty_string(birth["local_date"], "$.birth.local_date")
        normalized_birth["house_system"] = None
    else:
        if "local_datetime" not in birth:
            raise OrchestrationInputError("$.birth.local_datetime is required for exact/approximate birth time")
        if "local_date" in birth:
            raise OrchestrationInputError("$.birth.local_date is only allowed when birth_time_certainty=unknown")
        house_system = _non_empty_string(birth.get("house_system"), "$.birth.house_system")
        if house_system not in SUPPORTED_HOUSE_SYSTEMS:
            raise OrchestrationInputError(
                f"$.birth.house_system must be one of {sorted(SUPPORTED_HOUSE_SYSTEMS)}"
            )
        if "country" in normalized_birth["location"]:
            raise OrchestrationInputError(
                "$.birth.location.country is admitted only for unknown-time invariant-only natal readings"
            )
        normalized_birth["local_datetime"] = _non_empty_string(
            birth["local_datetime"], "$.birth.local_datetime"
        )
        normalized_birth["house_system"] = house_system

    normalized: dict[str, Any] = {
        "schema_name": REQUEST_SCHEMA_NAME,
        "schema_version": REQUEST_SCHEMA_VERSION,
        "reading_mode": reading_mode,
        "subject_ref": _non_empty_string(root["subject_ref"], "$.subject_ref"),
        "birth": normalized_birth,
    }
    if reading_mode == "transit":
        normalized["transit"] = _normalize_transit(root["transit"])
        if normalized["transit"]["include_house_ingresses"] and certainty != "exact":
            raise OrchestrationInputError("transit house ingress search requires birth_time_certainty=exact")
    return normalized


def _resolve_location(normalized: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    location = normalized["birth"]["location"]
    resolve_country_timezone = None
    resolve_place = None
    if "country" in location:
        resolve_country_timezone, resolve_place = _load_place_resolver()
        country = location["country"]
        result = resolve_country_timezone(country.get("name"), country_code=country.get("country_code"))
        resolved = result["resolved"]
        return (
            {"timezone_name": resolved["timezone_name"]},
            {"resolution_mode": "offline_country_timezone_resolver", **result},
        )

    if "place" in location:
        resolve_country_timezone, resolve_place = _load_place_resolver()
        place = location["place"]
        result = resolve_place(place["name"], country_code=place.get("country_code"))
        resolved = result["resolved"]
        return (
            {
                "latitude": resolved["latitude"],
                "longitude": resolved["longitude"],
                "timezone_name": resolved["timezone_name"],
            },
            {
                "resolution_mode": "offline_place_resolver",
                **result,
            },
        )

    coordinates = location["coordinates"]
    return (
        {
            "latitude": coordinates["latitude"],
            "longitude": coordinates["longitude"],
            "timezone_name": coordinates["timezone_name"],
        },
        {
            "resolution_mode": "explicit_coordinates",
            "resolved": dict(coordinates),
        },
    )


def _admit_bundle(bundle: dict[str, Any], stage: str) -> dict[str, Any]:
    gate = gate_bundle(bundle)
    if not gate["interpretation_allowed"]:
        raise RuntimeError(f"{stage} bundle rejected by Astrology runtime gate: {gate['errors']}")
    return gate


def _engine_provenance(
    natal_bundle: dict[str, Any],
    transit_bundle: dict[str, Any] | None,
    input_resolution: dict[str, Any],
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "orchestrator_id": ORCHESTRATOR_ID,
        "orchestrator_version": ORCHESTRATOR_VERSION,
        "request_schema": f"{REQUEST_SCHEMA_NAME}@{REQUEST_SCHEMA_VERSION}",
        "natal_provider_id": natal_bundle.get("provider", {}).get("provider_id"),
        "natal_provider_version": natal_bundle.get("provider", {}).get("provider_version"),
        "runtime_gate": "tools/astrology_runtime.py",
        "location_resolution_mode": input_resolution.get("resolution_mode"),
    }
    if input_resolution.get("resolver"):
        result["place_resolver_id"] = input_resolution["resolver"].get("resolver_id")
        result["place_resolver_version"] = input_resolution["resolver"].get("resolver_version")
    if transit_bundle is not None:
        result["transit_provider_id"] = transit_bundle.get("provider", {}).get("provider_id")
        result["transit_provider_version"] = transit_bundle.get("provider", {}).get("provider_version")
    return result


def run_request(data: Any) -> dict[str, Any]:
    normalized = normalize_request(data)
    resolved, input_resolution = _resolve_location(normalized)
    birth = normalized["birth"]

    if birth["birth_time_certainty"] == "unknown":
        natal_bundle = build_unknown_time_natal_bundle(
            local_date=birth["local_date"],
            timezone_name=resolved["timezone_name"],
            subject_ref=normalized["subject_ref"],
        )
    else:
        natal_bundle = build_natal_bundle(
            local_datetime=birth["local_datetime"],
            timezone_name=resolved["timezone_name"],
            latitude=resolved["latitude"],
            longitude=resolved["longitude"],
            house_system=birth["house_system"],
            subject_ref=normalized["subject_ref"],
            birth_time_certainty=birth["birth_time_certainty"],
        )
    natal_gate = _admit_bundle(natal_bundle, "natal")

    transit_bundle: dict[str, Any] | None = None
    transit_gate: dict[str, Any] | None = None
    if normalized["reading_mode"] == "transit":
        transit = normalized["transit"]
        transit_bundle = build_transit_bundle(
            natal_bundle,
            start_utc=transit["start_utc"],
            end_utc=transit["end_utc"],
            subject_ref=normalized["subject_ref"],
            moving_bodies=transit["moving_bodies"],
            natal_targets=transit["natal_targets"],
            aspects=transit["aspects"],
            include_transit_to_natal=transit["include_transit_to_natal"],
            include_stations=transit["include_stations"],
            include_ingresses=transit["include_ingresses"],
            include_house_ingresses=transit["include_house_ingresses"],
        )
        transit_gate = _admit_bundle(transit_bundle, "transit")

    bundles: dict[str, Any] = {"natal": natal_bundle}
    gates: dict[str, Any] = {"natal": natal_gate}
    if transit_bundle is not None and transit_gate is not None:
        bundles["transit"] = transit_bundle
        gates["transit"] = transit_gate

    return {
        "schema_name": RUN_SCHEMA_NAME,
        "schema_version": RUN_SCHEMA_VERSION,
        "status": "admitted",
        "interpretation_allowed": all(gate["interpretation_allowed"] for gate in gates.values()),
        "orchestrator": {
            "orchestrator_id": ORCHESTRATOR_ID,
            "orchestrator_version": ORCHESTRATOR_VERSION,
            "request_schema_path": REQUEST_SCHEMA_PATH,
            "authority": "composition_only",
        },
        "normalized_request": normalized,
        "input_resolution": input_resolution,
        "fact_bundles": bundles,
        "runtime_gates": gates,
        "reading_record_bridge": {
            "target_owner": "READING_RECORD.md",
            "target_record_schema_version": "2",
            "complete_reading_record": False,
            "storage_policy": "external_only",
            "layer_1_method_input": normalized,
            "layer_2b_structured_method_fact": bundles,
            "engine_provenance": _engine_provenance(
                natal_bundle,
                transit_bundle,
                input_resolution,
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run one normalized Astrology Production v1 natal/transit request end to end."
    )
    parser.add_argument("request", type=Path, help="Path to astrology_reading_request@1.0.0 JSON")
    args = parser.parse_args()
    try:
        data = json.loads(args.request.read_text(encoding="utf-8"))
        result = run_request(data)
    except (
        OSError,
        json.JSONDecodeError,
        OrchestrationInputError,
        ProviderInputError,
        TransitProviderInputError,
        RuntimeError,
    ) as exc:
        result = {
            "schema_name": RUN_SCHEMA_NAME,
            "schema_version": RUN_SCHEMA_VERSION,
            "status": "rejected",
            "interpretation_allowed": False,
            "error": str(exc),
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1
    except Exception as exc:
        # Preserve the admitted resolver's public PlaceResolutionError for direct
        # callers without importing geonamescache on coordinates-only cold start.
        if not (
            exc.__class__.__module__ == "tools.astrology_place_resolver"
            and exc.__class__.__name__ == "PlaceResolutionError"
        ):
            raise
        result = {
            "schema_name": RUN_SCHEMA_NAME,
            "schema_version": RUN_SCHEMA_VERSION,
            "status": "rejected",
            "interpretation_allowed": False,
            "error": str(exc),
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
