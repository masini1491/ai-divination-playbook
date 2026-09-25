#!/usr/bin/env python3
"""Range-parameterized parity verifier for Zi Wei calendar data architecture.

Research-only. It validates every Gregorian date in a candidate window against
current production calendar semantics while keeping expensive hour-boundary
checks focused on dates where time can change the normalized result.
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
import time
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.ziwei_calendar_data_poc import (
    GregorianBirth,
    load_day_record,
    normalize_from_data,
    write_month_shard,
)
from tools.ziwei_calendar_upstream_reference import GregorianBirthInput, normalize_gregorian_birth


def comparable_current(result: dict) -> dict:
    return {
        "raw_lunar_conversion": result["raw_lunar_conversion"],
        "policy_lunar_conversion": result["policy_lunar_conversion"],
        "normalized_natal_input": {
            "lunar_year": result["normalized_natal_input"]["lunar_year"],
            "lunar_month": result["normalized_natal_input"]["lunar_month"],
            "lunar_day": result["normalized_natal_input"]["lunar_day"],
            "hour_branch": result["normalized_natal_input"]["hour_branch"],
            "leap_month_identity": result["normalized_natal_input"]["leap_month_identity"],
        },
    }


def iter_dates(start: date, end: date):
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def ensure_month(root: Path, generated: set[tuple[int, int]], year: int, month: int) -> Path:
    key = (year, month)
    path = root / "years" / f"{year:04d}" / f"{month:02d}.json"
    if key not in generated:
        path = write_month_shard(root, year, month)
        generated.add(key)
    return path


def compare_case(root: Path, d: date, hour: int) -> dict | None:
    got = normalize_from_data(GregorianBirth(d.year, d.month, d.day, hour), root)
    current = normalize_gregorian_birth(GregorianBirthInput(d.year, d.month, d.day, hour))
    expected = comparable_current(current)
    if got == expected:
        return None
    return {"date": d.isoformat(), "hour": hour, "expected": expected, "got": got}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default="1900-01-01")
    parser.add_argument("--end", default="2100-12-31")
    parser.add_argument("--max-mismatches", type=int, default=20)
    args = parser.parse_args()

    start = date.fromisoformat(args.start)
    end = date.fromisoformat(args.end)
    if end < start:
        raise SystemExit("end before start")

    t0 = time.monotonic()
    generated: set[tuple[int, int]] = set()
    mismatch_samples: list[dict] = []
    daily_cases = boundary_23_cases = full_hour_cases = 0
    leap_day_15_16_dates = lunar_year_crossovers = 0

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)

        # Generate only months needed by the requested window plus one policy day.
        for d in iter_dates(start, end):
            ensure_month(root, generated, d.year, d.month)
        policy_tail = end + timedelta(days=1)
        ensure_month(root, generated, policy_tail.year, policy_tail.month)

        for d in iter_dates(start, end):
            # Universal property: every Gregorian date resolves identically at an
            # ordinary civil hour. This covers every lunar month/year boundary
            # and every leap-month day present in the candidate window.
            detail = compare_case(root, d, 12)
            daily_cases += 1
            if detail and len(mismatch_samples) < args.max_mismatches:
                mismatch_samples.append(detail)

            raw = load_day_record(root, d)
            next_day = d + timedelta(days=1)
            next_raw = load_day_record(root, next_day)

            is_month_end = next_day.month != d.month
            is_year_end = next_day.year != d.year
            is_leap_critical = raw["signed_lunar_month"] < 0 and raw["lunar_day"] in (15, 16)
            is_lunar_year_cross = next_raw["lunar_year"] != raw["lunar_year"]

            if is_leap_critical:
                leap_day_15_16_dates += 1
            if is_lunar_year_cross:
                lunar_year_crossovers += 1

            # Boundary policy: 23:00 is checked exactly where next-day shifting
            # crosses Gregorian or lunar semantic boundaries, plus range edges.
            if is_month_end or is_year_end or is_leap_critical or is_lunar_year_cross or d in (start, end):
                detail = compare_case(root, d, 23)
                boundary_23_cases += 1
                if detail and len(mismatch_samples) < args.max_mismatches:
                    mismatch_samples.append(detail)

            # Hour mapping is independent of Gregorian->lunar conversion. Sweep
            # all 24 civil hours on each Gregorian year edge and each leap 15/16
            # date so every branch and the 23:00 policy participate repeatedly.
            if d.month == 1 and d.day == 1 or is_leap_critical:
                for hour in range(24):
                    detail = compare_case(root, d, hour)
                    full_hour_cases += 1
                    if detail and len(mismatch_samples) < args.max_mismatches:
                        mismatch_samples.append(detail)

        shard_sizes = [
            (root / "years" / f"{year:04d}" / f"{month:02d}.json").stat().st_size
            for year, month in sorted(generated)
        ]

    report = {
        "schema_name": "ziwei_calendar_full_parity_report",
        "schema_version": "0.2.0",
        "status": "PASS" if not mismatch_samples else "FAIL",
        "research_only": True,
        "production_admission_changed": False,
        "candidate_window": {"start": start.isoformat(), "end": end.isoformat()},
        "coverage": {
            "every_gregorian_date_at_12": daily_cases,
            "boundary_23_cases": boundary_23_cases,
            "full_24_hour_cases": full_hour_cases,
            "leap_month_day_15_16_dates": leap_day_15_16_dates,
            "lunar_year_crossovers": lunar_year_crossovers,
        },
        "generated_month_shards": len(generated),
        "mismatch_count_observed": len(mismatch_samples),
        "mismatch_samples": mismatch_samples,
        "shard_size_bytes": {
            "min": min(shard_sizes) if shard_sizes else 0,
            "max": max(shard_sizes) if shard_sizes else 0,
            "mean": (sum(shard_sizes) / len(shard_sizes)) if shard_sizes else 0,
            "total": sum(shard_sizes),
        },
        "one_query_max_files": 2,
        "elapsed_seconds": time.monotonic() - t0,
    }
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
