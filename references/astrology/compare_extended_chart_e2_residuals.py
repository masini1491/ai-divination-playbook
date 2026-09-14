#!/usr/bin/env python3
"""Compare Phase E2 Swiss/Horizons observations under the research oracle contract."""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any


EXPECTED_MANIFEST_SCHEMA = "astrology_extended_chart_e2_oracle_manifest"
EXPECTED_OBSERVATION_SCHEMA = "astrology_extended_chart_e2_residual_observations"
ALLOWED_TOLERANCE_STATUSES = {
    "NOT_DEFINED_PENDING_RESIDUAL_COLLECTION",
    "NO_UNIVERSAL_PROSPECTIVELY_VALIDATED_TOLERANCE_OVER_TESTED_1825_2350_RANGE",
}


def circular_separation_deg(a: float, b: float) -> float:
    delta = abs((b - a) % 360.0)
    return min(delta, 360.0 - delta)


def finite_number(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be numeric")
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{field} must be finite")
    return value


def validate_manifest(manifest: dict[str, Any]) -> None:
    if manifest.get("schema_name") != EXPECTED_MANIFEST_SCHEMA:
        raise ValueError("unexpected manifest schema")
    if manifest.get("authority") != "REFERENCE_ONLY":
        raise ValueError("manifest authority must remain REFERENCE_ONLY")
    tolerance_status = manifest.get("comparison_policy", {}).get("tolerance_status")
    if tolerance_status not in ALLOWED_TOLERANCE_STATUSES:
        raise ValueError(f"unexpected E2 tolerance status: {tolerance_status}")


def validate_provenance(dataset: dict[str, Any], manifest: dict[str, Any]) -> None:
    kind = dataset.get("dataset_kind")
    if kind not in {"synthetic_test", "measured_oracle"}:
        raise ValueError("dataset_kind must be synthetic_test or measured_oracle")
    if kind == "synthetic_test":
        return

    swiss = dataset.get("swiss_provenance")
    horizons = dataset.get("horizons_provenance")
    if not isinstance(swiss, dict) or not isinstance(horizons, dict):
        raise ValueError("measured_oracle requires both provenance objects")

    expected_swiss = manifest["swiss_oracle"]
    if swiss.get("source_revision") != expected_swiss.get("source_revision"):
        raise ValueError("Swiss provenance mismatch: source_revision")
    pairs = (
        ("asteroid_ephemeris_blob_sha", expected_swiss["asteroid_ephemeris"]["blob_sha"]),
        ("asteroid_ephemeris_size_bytes", expected_swiss["asteroid_ephemeris"]["size_bytes"]),
        ("planetary_ephemeris_blob_sha", expected_swiss["planetary_ephemeris"]["blob_sha"]),
        ("planetary_ephemeris_size_bytes", expected_swiss["planetary_ephemeris"]["size_bytes"]),
    )
    for key, expected in pairs:
        if swiss.get(key) != expected:
            raise ValueError(f"Swiss provenance mismatch: {key}")

    expected_horizons = manifest["independent_oracle"]
    for key in ("provider", "ephem_type", "center", "apparent", "time_type"):
        if horizons.get(key) != expected_horizons.get(key):
            raise ValueError(f"Horizons provenance mismatch: {key}")
    if horizons.get("quantities") != expected_horizons.get("quantities"):
        raise ValueError("Horizons provenance mismatch: quantities")


def fixture_rows(manifest: dict[str, Any], dataset: dict[str, Any]) -> list[dict[str, Any]]:
    group = dataset.get("fixture_group", "calibration")
    groups = manifest.get("fixture_groups")
    if isinstance(groups, dict):
        rows = groups.get(group)
        if not isinstance(rows, list):
            raise ValueError(f"unknown fixture_group: {group}")
        return rows
    # Backward compatibility for the original research manifest.
    if group != "calibration":
        raise ValueError("legacy manifest only supports calibration fixtures")
    rows = manifest.get("fixtures")
    if not isinstance(rows, list):
        raise ValueError("manifest has no fixture definitions")
    return rows


def compare(manifest: dict[str, Any], dataset: dict[str, Any]) -> dict[str, Any]:
    validate_manifest(manifest)
    if dataset.get("schema_name") != EXPECTED_OBSERVATION_SCHEMA:
        raise ValueError("unexpected observation schema")
    if dataset.get("authority") != "REFERENCE_ONLY":
        raise ValueError("observation authority must remain REFERENCE_ONLY")
    validate_provenance(dataset, manifest)

    object_ids = [row["object_id"] for row in manifest["objects"]]
    fixtures = fixture_rows(manifest, dataset)
    fixture_times = {row["fixture_id"]: row["utc"] for row in fixtures}
    expected_pairs = {
        (fixture_id, object_id)
        for fixture_id in fixture_times
        for object_id in object_ids
    }

    seen: set[tuple[str, str]] = set()
    rows: list[dict[str, Any]] = []
    per_object: dict[str, list[dict[str, float]]] = defaultdict(list)

    for index, row in enumerate(dataset.get("observations", [])):
        fixture_id = row.get("fixture_id")
        object_id = row.get("object_id")
        key = (fixture_id, object_id)
        if key not in expected_pairs:
            raise ValueError(f"unexpected fixture/object pair at observation {index}: {key}")
        if key in seen:
            raise ValueError(f"duplicate fixture/object pair: {key}")
        seen.add(key)

        expected_utc = fixture_times[fixture_id]
        if row.get("utc") != expected_utc:
            raise ValueError(f"UTC mismatch for {fixture_id}/{object_id}")

        swiss = row.get("swiss", {})
        horizons = row.get("horizons", {})
        swiss_lon = finite_number(swiss.get("longitude_deg"), "swiss.longitude_deg")
        horizons_lon = finite_number(horizons.get("longitude_deg"), "horizons.longitude_deg")
        swiss_speed = finite_number(swiss.get("speed_deg_per_day"), "swiss.speed_deg_per_day")
        horizons_speed = finite_number(horizons.get("speed_deg_per_day"), "horizons.speed_deg_per_day")
        for name, value in (
            ("swiss.longitude_deg", swiss_lon),
            ("horizons.longitude_deg", horizons_lon),
        ):
            if not 0.0 <= value < 360.0:
                raise ValueError(f"{name} must be normalized to [0, 360)")

        if dataset["dataset_kind"] == "measured_oracle":
            expected_flags = manifest["swiss_oracle"].get("expected_returned_flags")
            if expected_flags is not None and swiss.get("returned_flags") != expected_flags:
                raise ValueError(f"Swiss returned_flags mismatch for {fixture_id}/{object_id}")

        lon_delta = circular_separation_deg(swiss_lon, horizons_lon)
        speed_delta = abs(swiss_speed - horizons_speed)
        comparison = {
            "fixture_id": fixture_id,
            "utc": expected_utc,
            "object_id": object_id,
            "longitude_delta_deg": lon_delta,
            "speed_delta_deg_per_day": speed_delta,
        }
        rows.append(comparison)
        per_object[object_id].append(
            {"longitude_delta_deg": lon_delta, "speed_delta_deg_per_day": speed_delta}
        )

    missing = sorted(expected_pairs - seen)
    if missing:
        raise ValueError(f"incomplete observation matrix; missing {len(missing)} pairs")

    summaries: dict[str, Any] = {}
    for object_id in object_ids:
        values = per_object[object_id]
        lon = [v["longitude_delta_deg"] for v in values]
        speed = [v["speed_delta_deg_per_day"] for v in values]
        summaries[object_id] = {
            "samples": len(values),
            "longitude_delta_deg": {"mean": sum(lon) / len(lon), "max": max(lon)},
            "speed_delta_deg_per_day": {"mean": sum(speed) / len(speed), "max": max(speed)},
        }

    return {
        "schema_name": "astrology_extended_chart_e2_residual_report",
        "schema_version": "0.2.0",
        "authority": "REFERENCE_ONLY",
        "dataset_kind": dataset["dataset_kind"],
        "fixture_group": dataset.get("fixture_group", "calibration"),
        "status": "NUMERIC_OBSERVATION" if dataset["dataset_kind"] == "measured_oracle" else "SYNTHETIC_HARNESS_PASS",
        "tolerance_status": manifest["comparison_policy"]["tolerance_status"],
        "sample_count": len(rows),
        "comparisons": rows,
        "per_object": summaries,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        default=str(Path(__file__).with_name("extended_chart_e2_oracle_manifest.json")),
    )
    parser.add_argument("observations")
    args = parser.parse_args()

    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    dataset = json.loads(Path(args.observations).read_text(encoding="utf-8"))
    try:
        result = compare(manifest, dataset)
    except (KeyError, TypeError, ValueError) as exc:
        print(json.dumps({"status": "FAIL_CLOSED", "error": str(exc)}, indent=2))
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
