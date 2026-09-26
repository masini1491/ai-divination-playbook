#!/usr/bin/env python3
"""TEMPORARY AST-P2-040 production-admission probe. MUST NOT MERGE.

Builds the frozen c1-cheb-d7-w60 five-body coefficient dataset from
NASA/JPL Horizons, validates 24 newly frozen prospective instants, exercises
fail-closed evaluator paths, and writes a transportable artifact directory.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import time
import urllib.parse
import urllib.request

HORIZONS_URL = "https://ssd.jpl.nasa.gov/api/horizons.api"
GRID_START = dt.datetime(1825, 4, 1, tzinfo=dt.timezone.utc)
ADMITTED_STOP = dt.datetime(2350, 10, 1, tzinfo=dt.timezone.utc)
SOURCE_STOP = dt.datetime(2350, 10, 6, tzinfo=dt.timezone.utc)
STEP_DAYS = 5
WIDTH_DAYS = 60
DEGREE = 7
COEFFS = 8
SEGMENT_COUNT = 3199
SEGMENTS_PER_SHARD = 192
OBJECTS = [
    ("Chiron", "2060;"),
    ("Ceres", "1;"),
    ("Pallas", "2;"),
    ("Juno", "3;"),
    ("Vesta", "4;"),
]
FIXTURES = [
    ("P2-040-Q01","1834-02-11T01:13:00Z"),
    ("P2-040-Q02","1866-12-16T07:37:00Z"),
    ("P2-040-Q03","1899-10-20T13:53:00Z"),
    ("P2-040-Q04","1932-08-24T19:23:00Z"),
    ("P2-040-Q05","1965-06-28T01:13:00Z"),
    ("P2-040-Q06","1998-05-02T07:37:00Z"),
    ("P2-040-Q07","2031-03-06T13:53:00Z"),
    ("P2-040-Q08","2064-01-08T19:23:00Z"),
    ("P2-040-Q09","2096-11-11T01:13:00Z"),
    ("P2-040-Q10","2129-09-16T07:37:00Z"),
    ("P2-040-Q11","2162-07-21T13:53:00Z"),
    ("P2-040-Q12","2195-05-25T19:23:00Z"),
    ("P2-040-Q13","2228-03-29T01:13:00Z"),
    ("P2-040-Q14","2261-01-31T07:37:00Z"),
    ("P2-040-Q15","2293-12-05T13:53:00Z"),
    ("P2-040-Q16","2326-10-09T19:23:00Z"),
]
THRESHOLDS = {
    "longitude_p95_arcsec_max": 10.0,
    "longitude_max_arcsec_max": 30.0,
    "speed_max_deg_per_day": 0.001,
}
OUTPUT = Path(os.environ.get("AST_P2_040_OUTPUT", "tmp/astrology-p2-040-f32-artifact"))


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def parse_iso(value: str) -> dt.datetime:
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))


def shortest_signed_delta(a: float, b: float) -> float:
    return ((b - a + 180.0) % 360.0) - 180.0


def circular_sep(a: float, b: float) -> float:
    return abs(shortest_signed_delta(a, b))


def percentile95(values: list[float]) -> float:
    ordered = sorted(values)
    return ordered[max(0, math.ceil(0.95 * len(ordered)) - 1)]


def fetch_json(url: str) -> dict:
    last = None
    for attempt in range(5):
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "ai-divination-playbook-ast-p2-040-f32-transport-probe/1"},
            )
            with urllib.request.urlopen(req, timeout=120) as response:
                return json.load(response)
        except Exception as exc:
            last = exc
            if attempt == 4:
                raise
            time.sleep(2**attempt)
    raise RuntimeError(last)


def observer_rows(command: str, start: dt.datetime, stop: dt.datetime, step: str):
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
        "STEP_SIZE": f"'{step}'",
        "QUANTITIES": "'31'",
        "APPARENT": "'AIRLESS'",
        "TIME_TYPE": "'UT'",
        "EXTRA_PREC": "'YES'",
        "CSV_FORMAT": "'YES'",
    }
    payload = fetch_json(HORIZONS_URL + "?" + urllib.parse.urlencode(params))
    if payload.get("error"):
        raise RuntimeError(payload["error"])
    text = payload.get("result", "")
    if "$$SOE" not in text or "$$EOE" not in text:
        raise RuntimeError("Horizons table markers missing")
    table = text.split("$$SOE", 1)[1].split("$$EOE", 1)[0]
    rows = []
    for raw in table.splitlines():
        if not raw.strip():
            continue
        nums = []
        for token in raw.split(","):
            try:
                nums.append(float(token.strip()))
            except ValueError:
                pass
        if len(nums) != 2:
            raise RuntimeError(f"unexpected Horizons row: {raw!r} -> {nums!r}")
        rows.append((nums[0] % 360.0, nums[1]))
    return rows, payload.get("signature", {})


def horizons_series(command: str):
    total_steps = int((SOURCE_STOP - GRID_START).total_seconds() // (STEP_DAYS * 86400))
    chunk_steps = 3000
    values = []
    signature = None
    start_index = 0
    first = True
    while start_index <= total_steps:
        end_index = min(total_steps, start_index + chunk_steps)
        a = GRID_START + dt.timedelta(days=start_index * STEP_DAYS)
        b = GRID_START + dt.timedelta(days=end_index * STEP_DAYS)
        rows, sig = observer_rows(command, a, b, f"{STEP_DAYS} d")
        expected = end_index - start_index + 1
        if len(rows) != expected:
            raise RuntimeError(f"source row count mismatch: {len(rows)} != {expected}")
        if signature is None:
            signature = sig
        elif signature != sig:
            raise RuntimeError("Horizons signature changed during build")
        lons = [row[0] for row in rows]
        values.extend(lons if first else lons[1:])
        first = False
        if end_index == total_steps:
            break
        start_index = end_index
    if len(values) != total_steps + 1:
        raise RuntimeError("full source grid length mismatch")
    raw = struct.pack("<" + "d" * len(values), *values)
    return values, signature or {}, sha256(raw)


def horizons_truth(command: str, when: dt.datetime):
    rows, sig = observer_rows(
        command,
        when - dt.timedelta(hours=1),
        when + dt.timedelta(hours=1),
        "1 h",
    )
    if len(rows) != 3:
        raise RuntimeError("truth query must return exactly 3 rows")
    speed = shortest_signed_delta(rows[0][0], rows[2][0]) * 12.0
    return rows[1][0], speed, sig


def local_unwrap(values: list[float]) -> list[float]:
    out = [values[0]]
    for value in values[1:]:
        out.append(out[-1] + shortest_signed_delta(out[-1] % 360.0, value))
    return out


def cheb_basis(x: float) -> list[float]:
    out = [1.0, x]
    for _ in range(2, COEFFS):
        out.append(2.0 * x * out[-1] - out[-2])
    return out


def deriv_basis(x: float) -> list[float]:
    out = [0.0] * COEFFS
    out[1] = 2.0 / WIDTH_DAYS
    u_prev = 1.0
    u_curr = 2.0 * x
    out[2] = 2.0 * u_curr * (2.0 / WIDTH_DAYS)
    for n in range(3, COEFFS):
        u_next = 2.0 * x * u_curr - u_prev
        out[n] = n * u_next * (2.0 / WIDTH_DAYS)
        u_prev, u_curr = u_curr, u_next
    return out


def solve(matrix: list[list[float]], vector: list[float]) -> list[float]:
    n = len(vector)
    a = [row[:] + [vector[i]] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(a[r][col]))
        if abs(a[pivot][col]) < 1e-13:
            raise RuntimeError("singular fit system")
        a[col], a[pivot] = a[pivot], a[col]
        scale = a[col][col]
        for j in range(col, n + 1):
            a[col][j] /= scale
        for row in range(n):
            if row == col:
                continue
            f = a[row][col]
            if f == 0:
                continue
            for j in range(col, n + 1):
                a[row][j] -= f * a[col][j]
    return [a[i][n] for i in range(n)]


def normal_eq(xs: list[float], ys: list[float]):
    ata = [[0.0] * COEFFS for _ in range(COEFFS)]
    aty = [0.0] * COEFFS
    for x, y in zip(xs, ys):
        b = cheb_basis(x)
        for r in range(COEFFS):
            aty[r] += b[r] * y
            for c in range(COEFFS):
                ata[r][c] += b[r] * b[c]
    return ata, aty


def fit_ols(xs: list[float], ys: list[float]):
    ata, aty = normal_eq(xs, ys)
    return solve(ata, aty)


def eval_raw(coeffs: list[float], x: float):
    b = cheb_basis(x)
    db = deriv_basis(x)
    return sum(c*v for c,v in zip(coeffs,b)), sum(c*v for c,v in zip(coeffs,db))


def fit_c1(xs: list[float], ys: list[float], target_value: float, target_speed: float):
    shift = round((target_value - ys[0]) / 360.0) * 360.0
    aligned = [y + shift for y in ys]
    ata, aty = normal_eq(xs, aligned)
    cv = cheb_basis(-1.0)
    cs = deriv_basis(-1.0)
    n = COEFFS
    kkt = [[0.0] * (n + 2) for _ in range(n + 2)]
    rhs = [0.0] * (n + 2)
    for r in range(n):
        rhs[r] = aty[r]
        for c in range(n):
            kkt[r][c] = ata[r][c]
    for ci, row in enumerate((cv, cs)):
        rhs[n + ci] = (target_value, target_speed)[ci]
        for j in range(n):
            kkt[j][n + ci] = row[j]
            kkt[n + ci][j] = row[j]
    return solve(kkt, rhs)[:n]


def build_coefficients(source: dict[str, list[float]]):
    points = WIDTH_DAYS // STEP_DAYS
    result = {}
    for object_id, _ in OBJECTS:
        vals = source[object_id]
        segs = []
        for seg in range(SEGMENT_COUNT):
            a = seg * points
            y = local_unwrap(vals[a:a+points+1])
            if len(y) != points + 1:
                raise RuntimeError("incomplete segment")
            xs = [-1.0 + 2.0*i/points for i in range(points+1)]
            if seg == 0:
                coeff = fit_ols(xs, y)
            else:
                target_value, target_speed = eval_raw(segs[-1], 1.0)
                coeff = fit_c1(xs, y, target_value, target_speed)
            segs.append(coeff)
        result[object_id] = segs
    return result


def write_dataset(coeffs, signature, source_digests):
    root = OUTPUT / "data" / "astrology" / "extended_ephemeris" / "v1"
    shards_dir = root / "shards"
    shards_dir.mkdir(parents=True, exist_ok=True)
    shard_meta = []
    dataset_bytes = bytearray()
    for shard_index, first_segment in enumerate(range(0, SEGMENT_COUNT, SEGMENTS_PER_SHARD)):
        count = min(SEGMENTS_PER_SHARD, SEGMENT_COUNT - first_segment)
        raw = bytearray()
        for seg in range(first_segment, first_segment + count):
            for object_id, _ in OBJECTS:
                projected = list(coeffs[object_id][seg])
                projected[0] = projected[0] % 360.0
                raw.extend(struct.pack("<8f", *projected))
        data = bytes(raw)
        path = shards_dir / f"{shard_index:02d}.bin"
        path.write_bytes(data)
        dataset_bytes.extend(data)
        shard_meta.append({
            "shard_index": shard_index,
            "path": f"shards/{shard_index:02d}.bin",
            "first_segment": first_segment,
            "segment_count": count,
            "byte_size": len(data),
            "sha256": sha256(data),
            "git_blob_sha": git_blob_sha(data),
        })
    manifest = {
        "schema_name": "astrology_extended_ephemeris_dataset",
        "schema_version": "1.0.0",
        "dataset_id": "astrology-extended-ephemeris-c1-f32-v1",
        "authority": "derived-deterministic-data",
        "production_admission": "CANDIDATE_ONLY",
        "source": {
            "provider": "NASA/JPL Horizons",
            "api": "Horizons API",
            "observed_signature": signature,
            "center": "500@399",
            "ephem_type": "OBSERVER",
            "quantities": [31],
            "apparent": "AIRLESS",
            "time_type": "UT",
            "extra_precision": True,
            "source_grid_days": STEP_DAYS,
            "object_source_grid_sha256": source_digests,
        },
        "representation": {
            "id": "c1-cheb-d7-w60-f32-c0mod360-v1",
            "degree": DEGREE,
            "segment_width_days": WIDTH_DAYS,
            "coefficients_per_object_segment": COEFFS,
            "float_encoding": "IEEE-754 float32 little-endian",
            "object_order": [x[0] for x in OBJECTS],
            "coverage_start": GRID_START.isoformat(),
            "coverage_stop_exclusive": SOURCE_STOP.isoformat(),
            "admitted_output_window_end": ADMITTED_STOP.isoformat(),
            "segment_count": SEGMENT_COUNT,
            "segments_per_shard": SEGMENTS_PER_SHARD,
            "record_layout": "segment-major, object-major, 8 float64 coefficients",
        },
        "dataset": {
            "raw_byte_size": len(dataset_bytes),
            "sha256": sha256(bytes(dataset_bytes)),
            "shard_count": len(shard_meta),
            "shards": shard_meta,
        },
        "runtime": {
            "network_required": False,
            "query_bounded_one_shard": True,
            "missing_or_mismatched_shard": "fail_closed",
        },
    }
    (root / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return root, manifest


class DatasetError(ValueError):
    pass


def eval_from_dataset(root: Path, manifest: dict, object_id: str, when: dt.datetime):
    objects = manifest["representation"]["object_order"]
    if object_id not in objects:
        raise DatasetError("unsupported object")
    if when < GRID_START or when > ADMITTED_STOP:
        raise DatasetError("date outside admitted coverage")
    offset_days = (when - GRID_START).total_seconds() / 86400.0
    seg = min(int(offset_days // WIDTH_DAYS), SEGMENT_COUNT - 1)
    shard_index = seg // SEGMENTS_PER_SHARD
    shard = manifest["dataset"]["shards"][shard_index]
    path = root / shard["path"]
    if not path.exists():
        raise DatasetError("required shard missing")
    data = path.read_bytes()
    if len(data) != shard["byte_size"] or sha256(data) != shard["sha256"]:
        raise DatasetError("required shard identity mismatch")
    within = seg - shard["first_segment"]
    object_index = objects.index(object_id)
    record_size = COEFFS * 4
    offset = (within * len(objects) + object_index) * record_size
    rec = data[offset:offset+record_size]
    if len(rec) != record_size:
        raise DatasetError("coefficient record truncated")
    coeff = list(struct.unpack("<8f", rec))
    local_days = offset_days - seg * WIDTH_DAYS
    x = -1.0 + 2.0 * local_days / WIDTH_DAYS
    raw, speed = eval_raw(coeff, x)
    return raw % 360.0, speed, seg, shard_index


def validate(root: Path, manifest: dict, signature: dict):
    rows = []
    for fixture_id, utc in FIXTURES:
        when = parse_iso(utc)
        for object_id, command in OBJECTS:
            pred_lon, pred_speed, seg, shard = eval_from_dataset(root, manifest, object_id, when)
            truth_lon, truth_speed, sig = horizons_truth(command, when)
            if sig != signature:
                raise RuntimeError("Horizons signature changed during validation")
            rows.append({
                "fixture_id": fixture_id,
                "utc": utc,
                "object_id": object_id,
                "segment_index": seg,
                "shard_index": shard,
                "longitude_arcsec": circular_sep(pred_lon, truth_lon) * 3600.0,
                "speed_deg_per_day": abs(pred_speed - truth_speed),
            })
    lons = [x["longitude_arcsec"] for x in rows]
    speeds = [x["speed_deg_per_day"] for x in rows]
    metrics = {
        "validation_rows": len(rows),
        "longitude_p95_arcsec": percentile95(lons),
        "longitude_max_arcsec": max(lons),
        "speed_max_deg_per_day": max(speeds),
        "worst_longitude": max(rows, key=lambda x: x["longitude_arcsec"]),
        "worst_speed": max(rows, key=lambda x: x["speed_deg_per_day"]),
    }
    failed = []
    if metrics["longitude_p95_arcsec"] > THRESHOLDS["longitude_p95_arcsec_max"]:
        failed.append("longitude_p95_arcsec")
    if metrics["longitude_max_arcsec"] > THRESHOLDS["longitude_max_arcsec_max"]:
        failed.append("longitude_max_arcsec")
    if metrics["speed_max_deg_per_day"] > THRESHOLDS["speed_max_deg_per_day"]:
        failed.append("speed_max_deg_per_day")
    metrics["failed_gates"] = failed
    metrics["prospective_validation_pass"] = not failed
    return metrics


def fail_closed_checks(root: Path, manifest: dict):
    when = parse_iso("2000-01-01T12:00:00Z")
    checks = {}
    try:
        eval_from_dataset(root, manifest, "Eris", when)
        checks["unsupported_object"] = False
    except DatasetError:
        checks["unsupported_object"] = True
    try:
        eval_from_dataset(root, manifest, "Chiron", parse_iso("1800-01-01T00:00:00Z"))
        checks["out_of_coverage"] = False
    except DatasetError:
        checks["out_of_coverage"] = True

    _, _, seg, shard_idx = eval_from_dataset(root, manifest, "Chiron", when)
    shard = manifest["dataset"]["shards"][shard_idx]
    path = root / shard["path"]
    original = path.read_bytes()
    path.unlink()
    try:
        eval_from_dataset(root, manifest, "Chiron", when)
        checks["missing_shard"] = False
    except DatasetError:
        checks["missing_shard"] = True
    path.write_bytes(original)

    bad = bytearray(original)
    bad[0] ^= 1
    path.write_bytes(bytes(bad))
    try:
        eval_from_dataset(root, manifest, "Chiron", when)
        checks["digest_mismatch"] = False
    except DatasetError:
        checks["digest_mismatch"] = True
    path.write_bytes(original)
    return checks


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    source = {}
    source_digests = {}
    signature = None
    for object_id, command in OBJECTS:
        values, sig, digest = horizons_series(command)
        source[object_id] = values
        source_digests[object_id] = digest
        if signature is None:
            signature = sig
        elif signature != sig:
            raise RuntimeError("Horizons signature mismatch across objects")

    coeffs = build_coefficients(source)
    root, manifest = write_dataset(coeffs, signature or {}, source_digests)
    metrics = validate(root, manifest, signature or {})
    fail_closed = fail_closed_checks(root, manifest)
    all_fail_closed = all(fail_closed.values())

    result = {
        "schema_name": "astrology_p2_040_f32_transport_probe",
        "schema_version": "1.0.0",
        "authority": "PRODUCTION_ADMISSION_EVIDENCE_CANDIDATE",
        "production_admission": "NOT_GRANTED_BY_PROBE",
        "contract_commit": "da10658332c921ad8c5f455236a899edd9c73287",
        "source_signature": signature,
        "dataset_manifest": manifest,
        "thresholds_frozen_before_execution": THRESHOLDS,
        "prospective_validation": metrics,
        "fail_closed_checks": fail_closed,
        "result": "PASS" if metrics["prospective_validation_pass"] and all_fail_closed else "FAIL",
    }
    (OUTPUT / "AST_P2_040_PROBE_RESULT.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print("ASTROLOGY_P2_040_F32_JSON_BEGIN")
    print(json.dumps(result, indent=2, sort_keys=True))
    print("ASTROLOGY_P2_040_F32_JSON_END")
    if result["result"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
