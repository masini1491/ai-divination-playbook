#!/usr/bin/env python3
"""Validate Phase E1 opposite-axis derivations using synthetic fixtures only."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def normalize_degrees(value: float) -> float:
    return value % 360.0


def opposite_longitude(value: float) -> float:
    return normalize_degrees(value + 180.0)


def circular_separation(a: float, b: float) -> float:
    delta = abs((b - a) % 360.0)
    return min(delta, 360.0 - delta)


def close(a: float, b: float, tolerance: float) -> bool:
    return circular_separation(a, b) <= tolerance


def validate_case(case: dict[str, Any], tolerance: float) -> list[str]:
    errors: list[str] = []
    fixture_id = case["fixture_id"]
    inputs = case["inputs"]
    expected = case["expected"]

    derived = {
        "south_node_deg": opposite_longitude(float(inputs["north_node_deg"])),
        "descendant_deg": opposite_longitude(float(inputs["ascendant_deg"])),
        "imum_coeli_deg": opposite_longitude(float(inputs["midheaven_deg"])),
    }

    for key, actual in derived.items():
        wanted = float(expected[key])
        if not close(actual, wanted, tolerance):
            errors.append(f"{fixture_id}: {key}: actual={actual} expected={wanted}")

    pairs = (
        ("north_node_deg", "south_node_deg"),
        ("ascendant_deg", "descendant_deg"),
        ("midheaven_deg", "imum_coeli_deg"),
    )
    for source_key, opposite_key in pairs:
        source = float(inputs[source_key])
        target = derived[opposite_key]
        if abs(circular_separation(source, target) - 180.0) > tolerance:
            errors.append(
                f"{fixture_id}: {source_key}<->{opposite_key} is not antipodal: "
                f"separation={circular_separation(source, target)}"
            )
        recovered = opposite_longitude(target)
        if not close(recovered, normalize_degrees(source), tolerance):
            errors.append(
                f"{fixture_id}: opposite(opposite({source_key})) did not recover source"
            )

    if case.get("node_definition") != "mean":
        errors.append(f"{fixture_id}: E1 fixture must preserve mean-node identity")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "fixture",
        nargs="?",
        default=str(Path(__file__).with_name("extended_chart_e1_fixtures.json")),
    )
    args = parser.parse_args()

    payload = json.loads(Path(args.fixture).read_text(encoding="utf-8"))
    if payload.get("authority") != "REFERENCE_ONLY":
        raise SystemExit("fixture authority must remain REFERENCE_ONLY")

    tolerance = float(payload["rules"]["tolerance_deg"])
    errors: list[str] = []
    for case in payload["cases"]:
        errors.extend(validate_case(case, tolerance))

    result = {
        "status": "PASS" if not errors else "FAIL",
        "cases": len(payload["cases"]),
        "assertion_families": [
            "expected-longitude",
            "antipodal-separation",
            "opposite-involution",
            "mean-node-provenance",
        ],
        "errors": errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
