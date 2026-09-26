"""TEMPORARY AST-P2-042 research probe. MUST NOT MERGE.

Executes the prospectively frozen single-segment-query continuity/overlap
Chebyshev candidate family. NASA/JPL Horizons is research/build authority only.
Durable evidence belongs under references/astrology/** in a separate final PR.
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
VALIDATION_STOP = dt.datetime(2350, 10, 1, tzinfo=dt.timezone.utc)
SOURCE_STEP_DAYS = 5
CHUNK_STEPS = 3000

VARIANTS = (
    {
        "id": "c1-cheb-d5-w45",
        "mechanism": "c1",
        "degree": 5,
        "segment_width_days": 45,
        "fit_padding_days": 0,
    },
    {
        "id": "c1-cheb-d7-w60",
        "mechanism": "c1",
        "degree": 7,
        "segment_width_days": 60,
        "fit_padding_days": 0,
    },
    {
        "id": "overlap-cheb-d5-w45-p10",
        "mechanism": "overlap",
        "degree": 5,
        "segment_width_days": 45,
        "fit_padding_days": 10,
    },
    {
        "id": "overlap-cheb-d7-w60-p15",
        "mechanism": "overlap",
        "degree": 7,
        "segment_width_days": 60,
        "fit_padding_days": 15,
    },
)

FEASIBILITY_THRESHOLDS = {
    "fixture_longitude_p95_arcsec_max": 10.0,
    "fixture_longitude_max_arcsec_max": 30.0,
    "fixture_speed_max_deg_per_day": 0.001,
    "source_grid_longitude_p95_arcsec_max": 10.0,
    "source_grid_longitude_max_arcsec_max": 30.0,
    "binary_payload_bytes_max": 1_048_576,
    "single_query_raw_payload_bytes_max": 64,
    "boundary_longitude_jump_arcsec_max": 30.0,
    "boundary_speed_jump_deg_per_day_max": 0.001,
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
    for attempt in range(5):
        try:
            request = urllib.request.Request(
                url,
                headers={"User-Agent": "ai-divination-playbook-astrology-p2-042-research/1"},
            )
            with urllib.request.urlopen(request, timeout=120) as response:
                return json.load(response)
        except Exception as exc:
            last_error = exc
            if attempt == 4:
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


def max_source_stop() -> dt.datetime:
    span_days = (VALIDATION_STOP - GRID_START).total_seconds() / 86400.0
    padded_days = 0
    for variant in VARIANTS:
        width = variant["segment_width_days"]
        pad = variant["fit_padding_days"]
        segment_span = math.ceil(span_days / width) * width
        padded_days = max(padded_days, segment_span + pad)
    padded_days = math.ceil(padded_days / SOURCE_STEP_DAYS) * SOURCE_STEP_DAYS
    return GRID_START + dt.timedelta(days=padded_days)


SOURCE_STOP = max_source_stop()


def horizons_series(command: str) -> tuple[list[float], dict]:
    total_steps = int((SOURCE_STOP - GRID_START).total_seconds() // (SOURCE_STEP_DAYS * 86400))
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


def cheb_basis(x: float, degree: int) -> list[float]:
    out = [1.0]
    if degree == 0:
        return out
    out.append(x)
    for _ in range(2, degree + 1):
        out.append(2.0 * x * out[-1] - out[-2])
    return out


def cheb_derivative_basis(x: float, degree: int, width_days: float) -> list[float]:
    out = [0.0] * (degree + 1)
    if degree == 0:
        return out
    out[1] = 2.0 / width_days
    if degree >= 2:
        u_prev = 1.0
        u_curr = 2.0 * x
        out[2] = 2.0 * u_curr * (2.0 / width_days)
        for n in range(3, degree + 1):
            u_next = 2.0 * x * u_curr - u_prev
            out[n] = n * u_next * (2.0 / width_days)
            u_prev, u_curr = u_curr, u_next
    return out


def solve_linear(matrix: list[list[float]], vector: list[float]) -> list[float]:
    n = len(vector)
    a = [row[:] + [vector[i]] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda row: abs(a[row][col]))
        if abs(a[pivot][col]) < 1e-13:
            raise AssertionError("singular linear system")
        if pivot != col:
            a[col], a[pivot] = a[pivot], a[col]
        scale = a[col][col]
        for j in range(col, n + 1):
            a[col][j] /= scale
        for row in range(n):
            if row == col:
                continue
            factor = a[row][col]
            if factor == 0.0:
                continue
            for j in range(col, n + 1):
                a[row][j] -= factor * a[col][j]
    return [a[i][n] for i in range(n)]


def normal_equations(
    xs: list[float],
    ys: list[float],
    degree: int,
) -> tuple[list[list[float]], list[float]]:
    ata = [[0.0 for _ in range(degree + 1)] for _ in range(degree + 1)]
    aty = [0.0 for _ in range(degree + 1)]
    for x, y in zip(xs, ys):
        basis = cheb_basis(x, degree)
        for r in range(degree + 1):
            aty[r] += basis[r] * y
            for c in range(degree + 1):
                ata[r][c] += basis[r] * basis[c]
    return ata, aty


def fit_ols(xs: list[float], ys: list[float], degree: int) -> list[float]:
    ata, aty = normal_equations(xs, ys, degree)
    return solve_linear(ata, aty)


def fit_c1(
    xs: list[float],
    ys: list[float],
    degree: int,
    width_days: float,
    target_value: float,
    target_speed: float,
) -> list[float]:
    # Align the local unwrap branch to the previous segment's end.
    shift = round((target_value - ys[0]) / 360.0) * 360.0
    aligned = [value + shift for value in ys]
    ata, aty = normal_equations(xs, aligned, degree)
    c_value = cheb_basis(-1.0, degree)
    c_speed = cheb_derivative_basis(-1.0, degree, width_days)
    constraints = [c_value, c_speed]
    targets = [target_value, target_speed]

    n = degree + 1
    m = len(constraints)
    kkt = [[0.0 for _ in range(n + m)] for _ in range(n + m)]
    rhs = [0.0 for _ in range(n + m)]
    for r in range(n):
        rhs[r] = aty[r]
        for c in range(n):
            kkt[r][c] = ata[r][c]
    for ci, row in enumerate(constraints):
        rhs[n + ci] = targets[ci]
        for j in range(n):
            kkt[j][n + ci] = row[j]
            kkt[n + ci][j] = row[j]
    solved = solve_linear(kkt, rhs)
    return solved[:n]


def eval_raw(coeffs: list[float], x: float, width_days: float) -> tuple[float, float]:
    basis = cheb_basis(x, len(coeffs) - 1)
    dbasis = cheb_derivative_basis(x, len(coeffs) - 1, width_days)
    value = sum(c * b for c, b in zip(coeffs, basis))
    speed = sum(c * b for c, b in zip(coeffs, dbasis))
    return value, speed


def fit_core_ols(values: list[float], degree: int) -> list[float]:
    y = local_unwrap(values)
    count = len(y)
    xs = [-1.0 + 2.0 * i / (count - 1) for i in range(count)]
    return fit_ols(xs, y, degree)


def build_variant(
    source: dict[str, list[float]],
    variant: dict,
) -> dict[str, list[list[float]]]:
    degree = variant["degree"]
    width_days = variant["segment_width_days"]
    pad_days = variant["fit_padding_days"]
    mechanism = variant["mechanism"]
    points_per_segment = width_days // SOURCE_STEP_DAYS
    pad_points = pad_days // SOURCE_STEP_DAYS
    span_days = (VALIDATION_STOP - GRID_START).total_seconds() / 86400.0
    segment_count = math.ceil(span_days / width_days)
    out: dict[str, list[list[float]]] = {}

    for object_id, _ in OBJECTS:
        values = source[object_id]
        segments: list[list[float]] = []
        for segment_index in range(segment_count):
            core_start = segment_index * points_per_segment
            core_stop = core_start + points_per_segment
            if mechanism == "c1":
                segment_values = values[core_start : core_stop + 1]
                if len(segment_values) != points_per_segment + 1:
                    raise AssertionError("incomplete C1 segment")
                local = local_unwrap(segment_values)
                xs = [-1.0 + 2.0 * i / points_per_segment for i in range(points_per_segment + 1)]
                if segment_index == 0:
                    coeffs = fit_ols(xs, local, degree)
                else:
                    target_value, target_speed = eval_raw(
                        segments[-1], 1.0, float(width_days)
                    )
                    coeffs = fit_c1(
                        xs,
                        local,
                        degree,
                        float(width_days),
                        target_value,
                        target_speed,
                    )
            elif mechanism == "overlap":
                start = max(0, core_start - pad_points)
                stop = min(len(values) - 1, core_stop + pad_points)
                segment_values = values[start : stop + 1]
                local = local_unwrap(segment_values)
                # x remains defined by the unpadded core interval.
                xs = [
                    -1.0 + 2.0 * ((idx - core_start) * SOURCE_STEP_DAYS) / width_days
                    for idx in range(start, stop + 1)
                ]
                coeffs = fit_ols(xs, local, degree)
            else:
                raise AssertionError(f"unknown mechanism: {mechanism}")
            segments.append(coeffs)
        out[object_id] = segments
    return out


def evaluate_variant(
    segments_by_object: dict[str, list[list[float]]],
    object_id: str,
    when: dt.datetime,
    width_days: int,
) -> tuple[float, float, int]:
    offset_days = (when - GRID_START).total_seconds() / 86400.0
    if offset_days < 0.0 or when > VALIDATION_STOP:
        raise AssertionError(f"date outside validation window: {when.isoformat()}")
    segment_index = min(
        int(offset_days // width_days),
        len(segments_by_object[object_id]) - 1,
    )
    local_days = offset_days - segment_index * width_days
    x = -1.0 + 2.0 * local_days / width_days
    raw, speed = eval_raw(
        segments_by_object[object_id][segment_index], x, float(width_days)
    )
    return raw % 360.0, speed, segment_index


def artifact_metrics(segments_by_object: dict[str, list[list[float]]]) -> dict:
    binary = bytearray()
    for object_id, _ in OBJECTS:
        for coeffs in segments_by_object[object_id]:
            binary.extend(struct.pack("<" + "d" * len(coeffs), *coeffs))
    return {
        "binary_float64_payload_bytes": len(binary),
        "binary_sha256": hashlib.sha256(bytes(binary)).hexdigest(),
        "base64_float64_ascii_chars": 4 * math.ceil(len(binary) / 3),
    }


def boundary_metrics(
    segments_by_object: dict[str, list[list[float]]],
    width_days: int,
) -> tuple[float, float, dict, dict]:
    worst_lon = {"longitude_arcsec": -1.0}
    worst_speed = {"speed_deg_per_day": -1.0}
    for object_id, _ in OBJECTS:
        segments = segments_by_object[object_id]
        for boundary_index in range(1, len(segments)):
            left_raw, left_speed = eval_raw(
                segments[boundary_index - 1], 1.0, float(width_days)
            )
            right_raw, right_speed = eval_raw(
                segments[boundary_index], -1.0, float(width_days)
            )
            lon_jump = circular_separation_deg(left_raw % 360.0, right_raw % 360.0) * 3600.0
            speed_jump = abs(left_speed - right_speed)
            if lon_jump > worst_lon["longitude_arcsec"]:
                worst_lon = {
                    "object_id": object_id,
                    "boundary_index": boundary_index,
                    "utc": (GRID_START + dt.timedelta(days=boundary_index * width_days)).isoformat(),
                    "longitude_arcsec": lon_jump,
                }
            if speed_jump > worst_speed["speed_deg_per_day"]:
                worst_speed = {
                    "object_id": object_id,
                    "boundary_index": boundary_index,
                    "utc": (GRID_START + dt.timedelta(days=boundary_index * width_days)).isoformat(),
                    "speed_deg_per_day": speed_jump,
                }
    return (
        worst_lon["longitude_arcsec"],
        worst_speed["speed_deg_per_day"],
        worst_lon,
        worst_speed,
    )


def source_grid_metrics(
    source: dict[str, list[float]],
    segments_by_object: dict[str, list[list[float]]],
    width_days: int,
) -> tuple[float, float, dict]:
    residuals = []
    max_index = int((VALIDATION_STOP - GRID_START).total_seconds() // (SOURCE_STEP_DAYS * 86400))
    for object_id, _ in OBJECTS:
        for idx in range(max_index + 1):
            when = GRID_START + dt.timedelta(days=idx * SOURCE_STEP_DAYS)
            pred_lon, _, segment_index = evaluate_variant(
                segments_by_object, object_id, when, width_days
            )
            truth_lon = source[object_id][idx]
            residuals.append(
                {
                    "object_id": object_id,
                    "utc": when.isoformat(),
                    "segment_index": segment_index,
                    "longitude_arcsec": circular_separation_deg(pred_lon, truth_lon) * 3600.0,
                }
            )
    values = [row["longitude_arcsec"] for row in residuals]
    worst = max(residuals, key=lambda row: row["longitude_arcsec"])
    return percentile95(values), max(values), worst


@unittest.skipUnless(os.environ.get("GITHUB_ACTIONS") == "true", "temporary Actions-only research probe")
class AstrologyP2042ContinuityChebyshevProbe(unittest.TestCase):
    def test_continuity_chebyshev_feasibility(self) -> None:
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

        results = {}
        for variant in VARIANTS:
            degree = variant["degree"]
            width = variant["segment_width_days"]
            segments = build_variant(source, variant)

            fixture_residuals = []
            for fixture_id, utc in FIXTURES:
                when = parse_iso(utc)
                for object_id, _ in OBJECTS:
                    pred_lon, pred_speed, segment_index = evaluate_variant(
                        segments, object_id, when, width
                    )
                    truth_lon, truth_speed = truths[(fixture_id, object_id)]
                    fixture_residuals.append(
                        {
                            "fixture_id": fixture_id,
                            "object_id": object_id,
                            "segment_index": segment_index,
                            "longitude_arcsec": circular_separation_deg(pred_lon, truth_lon) * 3600.0,
                            "speed_deg_per_day": abs(pred_speed - truth_speed),
                        }
                    )

            fixture_lons = [row["longitude_arcsec"] for row in fixture_residuals]
            fixture_speeds = [row["speed_deg_per_day"] for row in fixture_residuals]
            worst_fixture_lon = max(fixture_residuals, key=lambda row: row["longitude_arcsec"])
            worst_fixture_speed = max(fixture_residuals, key=lambda row: row["speed_deg_per_day"])

            grid_p95, grid_max, worst_grid = source_grid_metrics(
                source, segments, width
            )
            boundary_lon, boundary_speed, worst_boundary_lon, worst_boundary_speed = boundary_metrics(
                segments, width
            )
            artifact = artifact_metrics(segments)
            raw_query_bytes = (degree + 1) * 8

            metrics = {
                "mechanism": variant["mechanism"],
                "degree": degree,
                "segment_width_days": width,
                "fit_padding_days": variant["fit_padding_days"],
                "segment_count_per_object": len(next(iter(segments.values()))),
                "coefficients_per_segment": degree + 1,
                **artifact,
                "single_query_raw_payload_bytes": raw_query_bytes,
                "fixture_validation_rows": len(fixture_residuals),
                "fixture_longitude_p95_arcsec": percentile95(fixture_lons),
                "fixture_longitude_max_arcsec": max(fixture_lons),
                "fixture_speed_max_deg_per_day": max(fixture_speeds),
                "source_grid_longitude_p95_arcsec": grid_p95,
                "source_grid_longitude_max_arcsec": grid_max,
                "boundary_longitude_jump_arcsec_max": boundary_lon,
                "boundary_speed_jump_deg_per_day_max": boundary_speed,
                "worst_fixture_longitude": worst_fixture_lon,
                "worst_fixture_speed": worst_fixture_speed,
                "worst_source_grid_longitude": worst_grid,
                "worst_boundary_longitude": worst_boundary_lon,
                "worst_boundary_speed": worst_boundary_speed,
            }

            checks = [
                ("fixture_longitude_p95_arcsec", "fixture_longitude_p95_arcsec_max"),
                ("fixture_longitude_max_arcsec", "fixture_longitude_max_arcsec_max"),
                ("fixture_speed_max_deg_per_day", "fixture_speed_max_deg_per_day"),
                ("source_grid_longitude_p95_arcsec", "source_grid_longitude_p95_arcsec_max"),
                ("source_grid_longitude_max_arcsec", "source_grid_longitude_max_arcsec_max"),
                ("binary_float64_payload_bytes", "binary_payload_bytes_max"),
                ("single_query_raw_payload_bytes", "single_query_raw_payload_bytes_max"),
                ("boundary_longitude_jump_arcsec_max", "boundary_longitude_jump_arcsec_max"),
                ("boundary_speed_jump_deg_per_day_max", "boundary_speed_jump_deg_per_day_max"),
            ]
            failed = []
            for metric_key, threshold_key in checks:
                if metrics[metric_key] > FEASIBILITY_THRESHOLDS[threshold_key]:
                    failed.append(metric_key)
            metrics["failed_gates"] = failed
            metrics["feasibility_pass"] = not failed
            results[variant["id"]] = metrics

        passing = [
            variant_id for variant_id, metrics in results.items()
            if metrics["feasibility_pass"]
        ]
        result = {
            "schema_name": "astrology_p2_042_continuity_chebyshev_feasibility",
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
                "family_id": "single-segment-query-continuity-chebyshev-v0",
                "source_grid_days": SOURCE_STEP_DAYS,
                "runtime_network_required": False,
                "runtime_blending": False,
            },
            "coverage": {
                "start": GRID_START.isoformat(),
                "validation_stop": VALIDATION_STOP.isoformat(),
                "source_stop": SOURCE_STOP.isoformat(),
                "validation_fixture_ids": [item[0] for item in FIXTURES],
            },
            "thresholds_frozen_before_first_execution": FEASIBILITY_THRESHOLDS,
            "variants": results,
            "passing_variants": passing,
            "conclusion": "PASSING_VARIANT_EXISTS" if passing else "NO_PASSING_VARIANT",
            "notes": [
                "Thresholds are engineering-feasibility gates only, not production numeric-admission tolerances.",
                "The complete in-window 5-day source grid is a longitude anti-drift validation surface.",
                "All candidates preserve one stored segment per ordinary runtime query.",
                "A feasibility PASS does not grant production provider/calculation admission.",
            ],
        }
        print("ASTROLOGY_P2_042_JSON_BEGIN")
        print(json.dumps(result, indent=2, sort_keys=True))
        print("ASTROLOGY_P2_042_JSON_END")


if __name__ == "__main__":
    unittest.main()
