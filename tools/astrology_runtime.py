#!/usr/bin/env python3
"""Deterministic production gate for Astrology Fact Bundle 1.0.

This module does not calculate astronomy. It validates supplied deterministic or
user-supplied structured chart facts against the bounded Astrology v1 admission
policy before interpretation is allowed.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

SCHEMA_NAME = "astrology_fact_bundle"
SCHEMA_VERSION = "1.0.0"
METHOD = "Astrology"
READING_MODES = {"natal", "transit"}
FACT_SOURCES = {"approved_provider", "user_supplied_structured_export", "existing_verified_record"}
CALCULATION_VERIFICATION = {"verified_provider", "user_asserted", "verified_existing_record"}
FACT_SOURCE_VERIFICATION = {
    "approved_provider": "verified_provider",
    "user_supplied_structured_export": "user_asserted",
    "existing_verified_record": "verified_existing_record",
}
BIRTH_TIME_CERTAINTY = {"exact", "approximate", "unknown", "rectified"}
ZODIAC_SYSTEMS = {"tropical"}
CENTERS = {"geocentric"}
HOUSE_SYSTEMS = {"Whole Sign", "Placidus"}
MAJOR_ASPECT_ORBS = {
    "conjunction": 8.0,
    "opposition": 8.0,
    "trine": 7.0,
    "square": 7.0,
    "sextile": 5.0,
}
FORBIDDEN_FACT_SOURCES = {"model_calculated", "memory_inferred"}


def _error(errors: list[dict[str, str]], code: str, path: str, message: str) -> None:
    errors.append({"code": code, "path": path, "message": message})


def _finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_bundle(data: Any) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    if not isinstance(data, dict):
        return [{"code": "ROOT_OBJECT_REQUIRED", "path": "$", "message": "bundle must be an object"}]

    required = (
        "schema_name",
        "schema_version",
        "method",
        "reading_mode",
        "fact_source",
        "calculation_verification",
        "subject_ref",
        "birth_time_certainty",
        "configuration",
        "facts",
    )
    for key in required:
        if key not in data:
            _error(errors, "REQUIRED_FIELD_MISSING", f"$.{key}", "required field is missing")

    if data.get("schema_name") != SCHEMA_NAME:
        _error(errors, "SCHEMA_NAME_INVALID", "$.schema_name", f"must equal {SCHEMA_NAME}")
    if data.get("schema_version") != SCHEMA_VERSION:
        _error(errors, "SCHEMA_VERSION_UNSUPPORTED", "$.schema_version", f"must equal {SCHEMA_VERSION}")
    if data.get("method") != METHOD:
        _error(errors, "METHOD_INVALID", "$.method", f"must equal {METHOD}")
    if data.get("reading_mode") not in READING_MODES:
        _error(errors, "READING_MODE_UNSUPPORTED", "$.reading_mode", f"must be one of {sorted(READING_MODES)}")

    fact_source = data.get("fact_source")
    if fact_source in FORBIDDEN_FACT_SOURCES:
        _error(errors, "FACT_SOURCE_FORBIDDEN", "$.fact_source", "LLM/model or memory-derived chart calculation is forbidden")
    elif fact_source not in FACT_SOURCES:
        _error(errors, "FACT_SOURCE_UNSUPPORTED", "$.fact_source", f"must be one of {sorted(FACT_SOURCES)}")

    verification = data.get("calculation_verification")
    if verification not in CALCULATION_VERIFICATION:
        _error(errors, "CALCULATION_VERIFICATION_INVALID", "$.calculation_verification", f"must be one of {sorted(CALCULATION_VERIFICATION)}")
    elif fact_source in FACT_SOURCE_VERIFICATION and verification != FACT_SOURCE_VERIFICATION[fact_source]:
        _error(
            errors,
            "FACT_SOURCE_VERIFICATION_MISMATCH",
            "$.calculation_verification",
            f"{fact_source} requires {FACT_SOURCE_VERIFICATION[fact_source]}",
        )

    if not _string(data.get("subject_ref")):
        _error(errors, "SUBJECT_REF_REQUIRED", "$.subject_ref", "non-empty subject_ref is required")

    certainty = data.get("birth_time_certainty")
    if certainty not in BIRTH_TIME_CERTAINTY:
        _error(errors, "BIRTH_TIME_CERTAINTY_INVALID", "$.birth_time_certainty", f"must be one of {sorted(BIRTH_TIME_CERTAINTY)}")

    config = data.get("configuration")
    if not isinstance(config, dict):
        _error(errors, "CONFIGURATION_OBJECT_REQUIRED", "$.configuration", "configuration must be an object")
        config = {}
    if config.get("zodiac_system") not in ZODIAC_SYSTEMS:
        _error(errors, "ZODIAC_SYSTEM_UNSUPPORTED", "$.configuration.zodiac_system", "production v1 admits tropical zodiac only")
    if config.get("center") not in CENTERS:
        _error(errors, "CENTER_UNSUPPORTED", "$.configuration.center", "production v1 admits geocentric center only")

    house_system = config.get("house_system")
    if house_system is not None and house_system not in HOUSE_SYSTEMS:
        _error(errors, "HOUSE_SYSTEM_UNSUPPORTED", "$.configuration.house_system", f"must be null or one of {sorted(HOUSE_SYSTEMS)}")

    facts = data.get("facts")
    if not isinstance(facts, dict):
        _error(errors, "FACTS_OBJECT_REQUIRED", "$.facts", "facts must be an object")
        facts = {}

    for key in ("objects", "houses", "aspects", "events"):
        if key not in facts:
            _error(errors, "FACT_COLLECTION_REQUIRED", f"$.facts.{key}", "fact collection is required")
        elif not isinstance(facts[key], list):
            _error(errors, "FACT_COLLECTION_ARRAY_REQUIRED", f"$.facts.{key}", "fact collection must be an array")

    objects = facts.get("objects", []) if isinstance(facts.get("objects"), list) else []
    houses = facts.get("houses", []) if isinstance(facts.get("houses"), list) else []
    aspects = facts.get("aspects", []) if isinstance(facts.get("aspects"), list) else []
    events = facts.get("events", []) if isinstance(facts.get("events"), list) else []

    if certainty == "unknown":
        if data.get("reading_mode") != "natal":
            _error(errors, "UNKNOWN_TIME_TRANSIT_FORBIDDEN", "$.reading_mode", "unknown birth time is admitted only for natal invariant-sign facts")
        if houses:
            _error(errors, "UNKNOWN_TIME_HOUSES_FORBIDDEN", "$.facts.houses", "unknown birth time cannot supply production house facts")
        if aspects:
            _error(errors, "UNKNOWN_TIME_ASPECTS_FORBIDDEN", "$.facts.aspects", "unknown birth time cannot supply production natal aspect facts")
        forbidden_object_fields = {
            "longitude_deg", "sign_degree", "speed_deg_per_day", "motion", "house_number", "cusp_longitude_deg"
        }
        for i, row in enumerate(objects):
            if not isinstance(row, dict):
                continue
            if row.get("object_type") in {"angle", "cusp"}:
                _error(errors, "UNKNOWN_TIME_ANGLE_FORBIDDEN", f"$.facts.objects[{i}]", "unknown birth time cannot supply angle/cusp facts")
            for field in sorted(forbidden_object_fields & row.keys()):
                _error(
                    errors,
                    "UNKNOWN_TIME_POSITION_DETAIL_FORBIDDEN",
                    f"$.facts.objects[{i}].{field}",
                    "unknown birth time invariant-only facts cannot supply exact/time-sensitive position detail",
                )

    if houses and house_system is None:
        _error(errors, "HOUSE_SYSTEM_REQUIRED", "$.configuration.house_system", "house facts require an explicit admitted house system")

    seen_ids: set[str] = set()
    object_or_house_ids: set[str] = set()
    for collection_name, collection in (("objects", objects), ("houses", houses), ("aspects", aspects), ("events", events)):
        for i, row in enumerate(collection):
            path = f"$.facts.{collection_name}[{i}]"
            if not isinstance(row, dict):
                _error(errors, "FACT_OBJECT_REQUIRED", path, "fact row must be an object")
                continue
            fact_id = row.get("fact_id")
            if not _string(fact_id):
                _error(errors, "FACT_ID_REQUIRED", path + ".fact_id", "non-empty fact_id is required")
            elif fact_id in seen_ids:
                _error(errors, "FACT_ID_DUPLICATE", path + ".fact_id", "fact_id must be unique")
            else:
                seen_ids.add(fact_id)
                if collection_name in {"objects", "houses"}:
                    object_or_house_ids.add(fact_id)

    for i, aspect in enumerate(aspects):
        if not isinstance(aspect, dict):
            continue
        path = f"$.facts.aspects[{i}]"
        name = aspect.get("aspect")
        if name not in MAJOR_ASPECT_ORBS:
            _error(errors, "ASPECT_UNSUPPORTED", path + ".aspect", "production v1 admits major aspects only")
        else:
            orb = aspect.get("orb_deg")
            if not _finite_number(orb) or float(orb) < 0:
                _error(errors, "ASPECT_ORB_INVALID", path + ".orb_deg", "orb_deg must be a finite non-negative number")
            elif float(orb) > MAJOR_ASPECT_ORBS[name]:
                _error(errors, "ASPECT_ORB_EXCEEDS_POLICY", path + ".orb_deg", f"{name} exceeds production v1 max orb {MAJOR_ASPECT_ORBS[name]}")
        for ref_key in ("left_ref", "right_ref"):
            ref = aspect.get(ref_key)
            if not _string(ref):
                _error(errors, "ASPECT_REF_REQUIRED", path + f".{ref_key}", f"{ref_key} is required")
            elif ref not in object_or_house_ids:
                _error(errors, "ASPECT_REF_UNKNOWN", path + f".{ref_key}", f"unknown fact ref: {ref}")

    for i, event in enumerate(events):
        if not isinstance(event, dict):
            continue
        path = f"$.facts.events[{i}]"
        kind = event.get("event_kind")
        if kind not in {"transit_to_natal", "station", "ingress"}:
            _error(errors, "EVENT_KIND_UNSUPPORTED", path + ".event_kind", "production v1 admits transit_to_natal, station and ingress events only")
        if data.get("reading_mode") != "transit":
            _error(errors, "EVENTS_REQUIRE_TRANSIT_MODE", path, "timing events require reading_mode=transit")

    if data.get("reading_mode") == "transit" and not events and not any(
        isinstance(row, dict) and row.get("scope") == "transit_to_natal" for row in aspects
    ):
        _error(errors, "TRANSIT_FACT_REQUIRED", "$.facts", "transit mode requires at least one supplied transit event or transit-to-natal aspect")

    return errors


def gate_bundle(data: Any) -> dict[str, Any]:
    errors = validate_bundle(data)
    result = {
        "schema_name": "astrology_runtime_gate_result",
        "schema_version": "1.0.0",
        "method": "Astrology",
        "method_version": "astrology-v1",
        "status": "admitted" if not errors else "rejected",
        "interpretation_allowed": not errors,
        "errors": errors,
    }
    if isinstance(data, dict):
        result["reading_mode"] = data.get("reading_mode")
        result["subject_ref"] = data.get("subject_ref")
        result["fact_source"] = data.get("fact_source")
        result["calculation_verification"] = data.get("calculation_verification")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an Astrology Production v1 fact bundle.")
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    try:
        data = json.loads(args.bundle.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        result = {"status": "load_error", "interpretation_allowed": False, "errors": [{"code": "BUNDLE_LOAD_ERROR", "path": "$", "message": str(exc)}]}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2

    result = gate_bundle(data)
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Astrology v1: {result['status']}")
        for err in result["errors"]:
            print(f"  {err['code']} {err['path']}: {err['message']}")
    return 0 if result["interpretation_allowed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
