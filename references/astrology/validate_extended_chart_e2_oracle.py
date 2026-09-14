#!/usr/bin/env python3
"""Validate the Phase E2 research oracle manifest without requiring Swiss binaries."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

HEX40 = re.compile(r"^[0-9a-f]{40}$")
EXPECTED_OBJECTS = {
    "Chiron": ("CHIRON", "2060;"),
    "Ceres": ("CERES", "1;"),
    "Pallas": ("PALLAS", "2;"),
    "Juno": ("JUNO", "3;"),
    "Vesta": ("VESTA", "4;"),
}
EXPECTED_FIXTURES = {
    "E2-F01": "2000-01-01T12:00:00Z",
    "E2-F02": "1980-06-01T00:00:00Z",
    "E2-F03": "2026-09-14T00:00:00Z",
    "E2-F04": "2099-12-31T00:00:00Z",
}


def validate(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if payload.get("authority") != "REFERENCE_ONLY":
        errors.append("authority must remain REFERENCE_ONLY")
    if payload.get("binary_commit_policy") != "DO_NOT_COMMIT_EPHEMERIS_BINARY":
        errors.append("binary_commit_policy must forbid committing ephemeris binaries")

    swiss = payload.get("swiss_oracle", {})
    if swiss.get("ephemeris_path") != "ephe/seas_18.se1":
        errors.append("unexpected Swiss ephemeris path")
    if swiss.get("ephemeris_size_bytes") != 223004:
        errors.append("unexpected seas_18.se1 size")
    if not HEX40.match(str(swiss.get("ephemeris_blob_sha", ""))):
        errors.append("Swiss ephemeris blob SHA must be a 40-char lowercase hex Git SHA")
    if not HEX40.match(str(swiss.get("source_revision", ""))):
        errors.append("Swiss source revision must be a 40-char lowercase hex Git SHA")
    if not HEX40.match(str(swiss.get("python_adapter_revision", ""))):
        errors.append("pyswisseph revision must be a 40-char lowercase hex Git SHA")
    if swiss.get("required_flags") != ["FLG_SWIEPH", "FLG_SPEED"]:
        errors.append("Swiss research flags changed unexpectedly")

    objects = payload.get("objects", [])
    observed: dict[str, tuple[str, str]] = {}
    for item in objects:
        object_id = item.get("object_id")
        if object_id in observed:
            errors.append(f"duplicate object: {object_id}")
            continue
        observed[str(object_id)] = (
            str(item.get("swiss_constant", "")),
            str(item.get("horizons_command", "")),
        )
    if observed != EXPECTED_OBJECTS:
        errors.append(f"object mapping mismatch: {observed!r}")

    independent = payload.get("independent_oracle", {})
    required_horizons = {
        "provider": "NASA/JPL Horizons",
        "ephem_type": "OBSERVER",
        "center": "500@399",
        "quantities": [31],
        "apparent": "AIRLESS",
        "time_type": "UT",
        "extra_precision": True,
        "csv_format": True,
    }
    for key, expected in required_horizons.items():
        if independent.get(key) != expected:
            errors.append(f"Horizons contract mismatch for {key}: {independent.get(key)!r}")

    fixtures = {
        str(item.get("fixture_id")): str(item.get("utc"))
        for item in payload.get("fixtures", [])
    }
    if fixtures != EXPECTED_FIXTURES:
        errors.append(f"fixture set mismatch: {fixtures!r}")

    policy = payload.get("comparison_policy", {})
    if policy.get("tolerance_status") != "NOT_DEFINED_PENDING_RESIDUAL_COLLECTION":
        errors.append("tolerance must remain undefined before residual collection")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "manifest",
        nargs="?",
        default=str(Path(__file__).with_name("extended_chart_e2_oracle_manifest.json")),
    )
    args = parser.parse_args()

    payload = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    errors = validate(payload)
    result = {
        "status": "PASS" if not errors else "FAIL",
        "object_count": len(payload.get("objects", [])),
        "fixture_count": len(payload.get("fixtures", [])),
        "tolerance_status": payload.get("comparison_policy", {}).get("tolerance_status"),
        "errors": errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
