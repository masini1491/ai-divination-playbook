#!/usr/bin/env python3
"""Deterministic E7 house-rulership projection for admitted Astrology natal bundles."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from tools.astrology_runtime import gate_bundle

SCHEMA_NAME = "astrology_rulership_projection"
SCHEMA_VERSION = "1.0.0"

RULERSHIP_POLICIES: dict[str, dict[str, str]] = {
    "rulership-traditional-v1": {
        "Aries": "Mars",
        "Taurus": "Venus",
        "Gemini": "Mercury",
        "Cancer": "Moon",
        "Leo": "Sun",
        "Virgo": "Mercury",
        "Libra": "Venus",
        "Scorpio": "Mars",
        "Sagittarius": "Jupiter",
        "Capricorn": "Saturn",
        "Aquarius": "Saturn",
        "Pisces": "Jupiter",
    },
    "rulership-modern-v1": {
        "Aries": "Mars",
        "Taurus": "Venus",
        "Gemini": "Mercury",
        "Cancer": "Moon",
        "Leo": "Sun",
        "Virgo": "Mercury",
        "Libra": "Venus",
        "Scorpio": "Pluto",
        "Sagittarius": "Jupiter",
        "Capricorn": "Saturn",
        "Aquarius": "Uranus",
        "Pisces": "Neptune",
    },
}


class RulershipProjectionError(ValueError):
    pass


def _facts_by_id(rows: list[dict[str, Any]], key: str) -> dict[Any, dict[str, Any]]:
    out: dict[Any, dict[str, Any]] = {}
    for row in rows:
        value = row.get(key)
        if value is not None:
            out[value] = row
    return out


def build_rulership_projection(bundle: dict[str, Any], policy_id: str) -> dict[str, Any]:
    policy = RULERSHIP_POLICIES.get(policy_id)
    if policy is None:
        raise RulershipProjectionError(
            "explicit admitted rulership policy required: "
            + ", ".join(sorted(RULERSHIP_POLICIES))
        )

    gate = gate_bundle(bundle)
    if gate.get("status") != "admitted":
        raise RulershipProjectionError("rulership projection requires an admitted Astrology fact bundle")
    if bundle.get("reading_mode") != "natal":
        raise RulershipProjectionError("rulership projection is admitted for natal bundles only")

    facts = bundle.get("facts", {})
    houses = facts.get("houses", [])
    objects = facts.get("objects", [])
    if not isinstance(houses, list) or len(houses) != 12:
        raise RulershipProjectionError("rulership projection requires all 12 admitted house facts")
    if not isinstance(objects, list):
        raise RulershipProjectionError("rulership projection requires admitted object facts")

    houses_by_number = _facts_by_id(houses, "house_number")
    objects_by_id = _facts_by_id(objects, "object_id")
    if set(houses_by_number) != set(range(1, 13)):
        raise RulershipProjectionError("rulership projection requires unique house numbers 1 through 12")

    projections: list[dict[str, Any]] = []
    for house_number in range(1, 13):
        house = houses_by_number[house_number]
        sign = house.get("sign")
        if sign not in policy:
            raise RulershipProjectionError(
                f"house {house_number} lacks an admitted zodiac sign for rulership projection"
            )
        ruler = policy[sign]
        ruler_fact = objects_by_id.get(ruler)
        if ruler_fact is None:
            raise RulershipProjectionError(
                f"admitted ruler object fact missing for {ruler}"
            )
        row = {
            "projection_id": f"projection:rulership:{policy_id}:house:{house_number}",
            "projection_kind": "rulership",
            "policy_id": policy_id,
            "house_number": house_number,
            "house_fact_ref": house["fact_id"],
            "sign_on_house": sign,
            "ruler_object_id": ruler,
            "ruler_fact_ref": ruler_fact["fact_id"],
        }
        if isinstance(ruler_fact.get("sign"), str):
            row["ruler_sign"] = ruler_fact["sign"]
        if isinstance(ruler_fact.get("house_number"), int):
            row["ruler_house_number"] = ruler_fact["house_number"]
        projections.append(row)

    return {
        "schema_name": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "status": "projected",
        "authority": "deterministic_policy_projection_only",
        "method": "Astrology",
        "reading_mode": "natal",
        "subject_ref": bundle["subject_ref"],
        "house_system": bundle.get("configuration", {}).get("house_system"),
        "policy_id": policy_id,
        "explicit_policy_required": True,
        "semantic_interpretation_authority": False,
        "projections": projections,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--policy-id", required=True, choices=sorted(RULERSHIP_POLICIES))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    bundle = json.loads(args.input.read_text(encoding="utf-8"))
    result = build_rulership_projection(bundle, args.policy_id)
    encoded = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
