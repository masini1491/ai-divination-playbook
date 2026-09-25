"""TEMPORARY AST-P1-010 research probe. MUST NOT MERGE.

Uses NASA/JPL Horizons only in the GitHub Actions research environment to evaluate
a compact sampled-longitude representation. Durable evidence belongs under
references/astrology/** in a separate final PR.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import math
import os
import struct
import time
import unittest
import urllib.parse
import urllib.request

HORIZONS_URL = "https://ssd.jpl.nasa.gov/api/horizons.api"
OBJECTS = [
    ("Chiron", "2060;"),
    ("Ceres", "1;"),
    ("Pallas", "2;"),
    ("Juno", "3;"),
    ("Vesta", "4;"),
]
FIXTURES = [
    ("E2-F01", "2000-01-01T12:00:00Z"),
    ("E2-F02", "1980-06-01T00:00:00Z"),
    ("E2-F03", "2026-09-14T00:00:00Z"),
    ("E2-F04", "2099-12-31T00:00:00Z"),
    ("E2-H01", "1850-03-20T06:00:00Z"),
    ("E2-H02", "1955-11-05T18:00:00Z"),
    ("E2-H03", "2050-07-01T06:00:00Z"),
    ("E2-H04", "2200-02-28T18:00:00Z"),
    ("E2-V01", "1825-08-17T03:00:00Z"),
    ("E2-V02", "1925-02-14T15:00:00Z"),
    ("E2-V03", "2075-10-09T09:00:00Z"),
    ("E2-V04", "2350-05-23T21:00:00Z"),
]
GRID_START = dt.datetime(1825, 4, 1, tzinfo=dt.timezone.utc)
GRID_STOP = dt.datetime(2350, 10, 1, tzinfo=dt.timezone.utc)
SOURCE_STEP_DAYS = 10
VARIANT_STEPS_DAYS = (10, 20, 40)
CHUNK_STEPS = 3000

# Engineering feasibility thresholds frozen in this source before first execution.
# These are NOT production-admission tolerances.
FEASIBILITY_THRESHOLDS = {
    "longitude_p95_arcsec_max": 10.0,
    "longitude_max_arcsec_max": 30.0,
    "speed_max_deg_per_day": 0.001,
    "binary_payload_bytes_max": 1_048_576,
    "single_query_raw_payload_bytes_max": 64,
}


def parse_iso(value: str) -> dt.datetime:
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))


def shortest_signed_delta(a: float, b: float) -> float:
    return ((b - a + 180.0) % 360.0) - 180.0


def circular_separation_deg(a: float, b: float) -> float:
    return abs(shortest_signed_delta(a, b))


def percentile95(values: list[float]) -> float:
    ordered = sorted(values)
    return ordered[max(0, math.ceil(0.95 * len(ordered)) - 1)]


def fetch_json(url: str) -> dict:
    last_error = None
    for attempt in range(4):
        try:
            request = urllib.request.Request(
                url,
                headers={"User-Agent": "ai-divination-playbook-astrology-exp1-research/1"},
            )
            with urllib.request.urlopen(request, timeout=120) as response:
                return json.load(response)
        except Exception as exc:  # research probe: retry transient network/API failures
            last_error = exc
            if attempt == 3:
                raise
            time.sleep(2**attempt)
    raise AssertionError(f"unreachable: {last_error}")


def observer_rows(
    command: str,
    start: dt.datetime,
    stop: dt.datetime,
    step_size: str,
) -> tuple[list[tuple[float, float]], dict]:
    fmt = "%Y-%m-%d %H:%M"
    params = {
        "format": "json",
        "COMMAND": f"'{command}'",
        "OBJ_DATA": "'NO'",
        "MAKE_EPHEM": "'YES'",
        "EPHEM_TYPE": "'OBSERVER'",
        "CENTER": "'500@399'",
        "START_TIME": f"'{start.strftime(fmt)}'",
        "STOP_TIME": f"'{stop.strftime(fmt)}'",
        "STEP_SIZE": f"'{step_size}'",
        "QUANTITIES": "'31'",
        "APPARENT": "'AIRLESS'",
        "TIME_TYPE": "'UT'",
        "EXTRA_PREC": "'YES'",
        "CSV_FORMAT": "'YES'",
    }
    payload = fetch_json(HORIZONS_URL + "?" + urllib.parse.urlencode(params))
    if payload.get("error"):
        raise AssertionError(f"Horizons error for {command}: {payload['error']}")
    result = payload.get("result", "")
    if "$$SOE" not in result or "$$EOE" not in result:
        raise AssertionError(f"Horizons table markers missing for {command}")
    table = result.split("$$SOE", 1)[1].split("$$EOE", 1)[0]
    rows: list[tuple[float, float]] = []
    for raw in table.splitlines():
        if not raw.strip():
            continue
        numeric: list[float] = []
        for token in raw.split(","):
            token = token.strip()
            try:
                numeric.append(float(token))
            except ValueError:
                pass
        if len(numeric) != 2:
            raise AssertionError(
                f"Unexpected Horizons observer row for {command}: {raw!r} -> {numeric!r}"
            )
        rows.append((numeric[0], numeric[1]))
    return rows, payload.get("signature", {})


def horizons_series(command: str) -> tuple[list[float], dict]:
    total_steps = int((GRID_STOP - GRID_START).total_seconds() // (SOURCE_STEP_DAYS * 86400))
    values: list[float] = []
    observed_signature = None
    first = True
    start_index = 0
    while start_index <= total_steps:
        end_index = min(total_steps, start_index + CHUNK_STEPS)
        chunk_start = GRID_START + dt.timedelta(days=SOURCE_STEP_DAYS * start_index)
        chunk_stop = GRID_START + dt.timedelta(days=SOURCE_STEP_DAYS * end_index)
        rows, signature = observer_rows(
            command,
            chunk_start,
            chunk_stop,
            f"{SOURCE_STEP_DAYS} d",
        )
        expected = end_index - start_index + 1
        if len(rows) != expected:
            raise AssertionError(
                f"series row count mismatch for {command}: expected {expected}, got {len(rows)}"
            )
        if observed_signature is None:
            observed_signature = signature
        elif signature != observed_signature:
            raise AssertionError("Horizons signature changed during source collection")
        lons = [row[0] % 360.0 for row in rows]
        values.extend(lons if first else lons[1:])
        first = False
        if end_index == total_steps:
            break
        start_index = end_index
    if len(values) != total_steps + 1:
        raise AssertionError(f"full series length mismatch: {len(values)} != {total_steps + 1}")
    return values, observed_signature or {}


def horizons_truth(command: str, center: dt.datetime) -> tuple[float, float, dict]:
    rows, signature = observer_rows(
        command,
        center - dt.timedelta(hours=1),
        center + dt.timedelta(hours=1),
        "1 h",
    )
    if len(rows) != 3:
        raise AssertionError(f"expected 3 truth rows for {command}, got {len(rows)}")
    lon_minus = rows[0][0] % 360.0
    lon_mid = rows[1][0] % 360.0
    lon_plus = rows[2][0] % 360.0
    speed = shortest_signed_delta(lon_minus, lon_plus) * 12.0
    return lon_mid, speed, signature


def local_unwrap(values: list[float]) -> list[float]:
    out = [values[0]]
    for value in values[1:]:
        out.append(out[-1] + shortest_signed_delta(out[-1] % 360.0, value % 360.0))
    return out


def interpolate(samples: list[float], spacing_days: int, when: dt.datetime) -> tuple[float, float, int]:
    offset_days = (when - GRID_START).total_seconds() / 86400.0
    k = math.floor(offset_days / spacing_days)
    if k < 1 or k + 2 >= len(samples):
        raise AssertionError(f"fixture outside four-point interpolation margin: {when.isoformat()}")
    raw = samples[k - 1 : k + 3]
    y0, y1, y2, y3 = local_unwrap(raw)
    h = float(spacing_days)
    m1 = (y2 - y0) / (2.0 * h)
    m2 = (y3 - y1) / (2.0 * h)
    u = (offset_days - k * h) / h
    h00 = 2 * u**3 - 3 * u**2 + 1
    h10 = u**3 - 2 * u**2 + u
    h01 = -2 * u**3 + 3 * u**2
    h11 = u**3 - u**2
    y = h00 * y1 + h10 * h * m1 + h01 * y2 + h11 * h * m2

    dh00 = 6 * u**2 - 6 * u
    dh10 = 3 * u**2 - 4 * u + 1
    dh01 = -6 * u**2 + 6 * u
    dh11 = 3 * u**2 - 2 * u
    speed = (dh00 * y1 + dh10 * h * m1 + dh01 * y2 + dh11 * h * m2) / h
    return y % 360.0, speed, k


def artifact_metrics(samples_by_object: dict[str, list[float]], spacing_days: int) -> dict:
    binary = b"".join(
        struct.pack("<" + "d" * len(values), *values)
        for object_id, values in OBJECTS
        for values in [samples_by_object[object_id]]
    )
    canonical = json.dumps(
        {
            "schema": "sampled-wrapped-longitude-hermite-v0",
            "start": GRID_START.isoformat(),
            "step_days": spacing_days,
            "object_order": [item[0] for item in OBJECTS],
            "samples": samples_by_object,
        },
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return {
        "binary_float64_payload_bytes": len(binary),
        "binary_sha256": hashlib.sha256(binary).hexdigest(),
        "base64_float64_ascii_chars": 4 * math.ceil(len(binary) / 3),
        "canonical_json_bytes": len(canonical),
        "canonical_json_sha256": hashlib.sha256(canonical).hexdigest(),
        "single_query_raw_payload_bytes": 4 * 8,
    }


@unittest.skipUnless(os.environ.get("GITHUB_ACTIONS") == "true", "temporary Actions-only research probe")
class AstrologyExp1SampledEphemerisProbe(unittest.TestCase):
    def test_sampled_longitude_cubic_hermite_feasibility(self) -> None:
        source: dict[str, list[float]] = {}
        source_signature = None
        for object_id, command in OBJECTS:
            values, signature = horizons_series(command)
            source[object_id] = values
            if source_signature is None:
                source_signature = signature
            self.assertEqual(signature, source_signature)

        truths: dict[tuple[str, str], tuple[float, float]] = {}
        for fixture_id, utc in FIXTURES:
            when = parse_iso(utc)
            for object_id, command in OBJECTS:
                lon, speed, signature = horizons_truth(command, when)
                self.assertEqual(signature, source_signature)
                truths[(fixture_id, object_id)] = (lon, speed)

        variants = {}
        for spacing_days in VARIANT_STEPS_DAYS:
            factor = spacing_days // SOURCE_STEP_DAYS
            samples_by_object = {
                object_id: values[::factor]
                for object_id, values in source.items()
            }
            residuals = []
            max_lookup_json_bytes = 0
            for fixture_id, utc in FIXTURES:
                when = parse_iso(utc)
                for object_id, _ in OBJECTS:
                    pred_lon, pred_speed, k = interpolate(
                        samples_by_object[object_id],
                        spacing_days,
                        when,
                    )
                    truth_lon, truth_speed = truths[(fixture_id, object_id)]
                    lon_arcsec = circular_separation_deg(pred_lon, truth_lon) * 3600.0
                    speed_delta = abs(pred_speed - truth_speed)
                    residuals.append(
                        {
                            "fixture_id": fixture_id,
                            "object_id": object_id,
                            "longitude_arcsec": lon_arcsec,
                            "speed_deg_per_day": speed_delta,
                        }
                    )
                    lookup_payload = json.dumps(
                        {
                            "index": k,
                            "samples": samples_by_object[object_id][k - 1 : k + 3],
                        },
                        separators=(",", ":"),
                    ).encode("utf-8")
                    max_lookup_json_bytes = max(max_lookup_json_bytes, len(lookup_payload))

            self.assertEqual(len(residuals), len(FIXTURES) * len(OBJECTS))
            lon_values = [row["longitude_arcsec"] for row in residuals]
            speed_values = [row["speed_deg_per_day"] for row in residuals]
            worst_lon = max(residuals, key=lambda row: row["longitude_arcsec"])
            worst_speed = max(residuals, key=lambda row: row["speed_deg_per_day"])
            per_object = {}
            for object_id, _ in OBJECTS:
                subset = [row for row in residuals if row["object_id"] == object_id]
                lons = [row["longitude_arcsec"] for row in subset]
                speeds = [row["speed_deg_per_day"] for row in subset]
                per_object[object_id] = {
                    "longitude_p95_arcsec": percentile95(lons),
                    "longitude_max_arcsec": max(lons),
                    "speed_p95_deg_per_day": percentile95(speeds),
                    "speed_max_deg_per_day": max(speeds),
                }

            metrics = artifact_metrics(samples_by_object, spacing_days)
            summary = {
                "spacing_days": spacing_days,
                "sample_count_per_object": {
                    object_id: len(values)
                    for object_id, values in samples_by_object.items()
                },
                **metrics,
                "single_query_json_bytes_max": max_lookup_json_bytes,
                "validation_rows": len(residuals),
                "longitude_p95_arcsec": percentile95(lon_values),
                "longitude_max_arcsec": max(lon_values),
                "speed_p95_deg_per_day": percentile95(speed_values),
                "speed_max_deg_per_day": max(speed_values),
                "worst_longitude": worst_lon,
                "worst_speed": worst_speed,
                "per_object": per_object,
            }
            threshold = FEASIBILITY_THRESHOLDS
            summary["feasibility_pass"] = (
                summary["longitude_p95_arcsec"] <= threshold["longitude_p95_arcsec_max"]
                and summary["longitude_max_arcsec"] <= threshold["longitude_max_arcsec_max"]
                and summary["speed_max_deg_per_day"] <= threshold["speed_max_deg_per_day"]
                and summary["binary_float64_payload_bytes"] <= threshold["binary_payload_bytes_max"]
                and summary["single_query_raw_payload_bytes"] <= threshold["single_query_raw_payload_bytes_max"]
            )
            variants[str(spacing_days)] = summary

        passing = [
            int(step)
            for step, summary in variants.items()
            if summary["feasibility_pass"]
        ]
        result = {
            "schema_name": "astrology_exp1_sampled_ephemeris_feasibility",
            "schema_version": "0.1.0",
            "authority": "REFERENCE_ONLY_RESEARCH",
            "production_admission": "NOT_GRANTED",
            "source_authority": {
                "provider": "NASA/JPL Horizons",
                "api": "Horizons API",
                "observed_signature": source_signature,
                "center": "500@399",
                "ephem_type": "OBSERVER",
                "quantities": [31],
                "apparent": "AIRLESS",
                "time_type": "UT",
            },
            "representation": {
                "id": "sampled-wrapped-longitude-hermite-v0",
                "source_grid_days": SOURCE_STEP_DAYS,
                "variant_spacing_days": list(VARIANT_STEPS_DAYS),
                "lookup_points_per_object": 4,
                "interpolation": "cubic Hermite with centered slopes from four local wrapped-longitude samples",
                "runtime_network_required": False,
            },
            "coverage": {
                "start": GRID_START.isoformat(),
                "stop": GRID_STOP.isoformat(),
                "validation_fixture_ids": [item[0] for item in FIXTURES],
            },
            "thresholds_frozen_before_first_execution": FEASIBILITY_THRESHOLDS,
            "variants": variants,
            "selected_coarsest_passing_spacing_days": max(passing) if passing else None,
            "notes": [
                "Thresholds are engineering-feasibility gates only, not production numeric admission tolerances.",
                "No Swiss or other live provider is required by the candidate runtime representation.",
                "The full artifact is not committed by this temporary probe.",
            ],
        }
        print("ASTROLOGY_EXP1_JSON_BEGIN")
        print(json.dumps(result, indent=2, sort_keys=True))
        print("ASTROLOGY_EXP1_JSON_END")


if __name__ == "__main__":
    unittest.main()
