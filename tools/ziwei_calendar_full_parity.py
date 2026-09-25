#!/usr/bin/env python3
"""Full-day parity verifier for Zi Wei calendar data architecture research.

Research-only. Does not change production admission or supported range.
"""
from __future__ import annotations

import argparse
import json
import tempfile
import time
from datetime import date, timedelta
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.ziwei_calendar_data_poc import GregorianBirth, normalize_from_data, write_month_shard
from tools.ziwei_calendar_provider import GregorianBirthInput, normalize_gregorian_birth


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
    if key not in generated:
        path = write_month_shard(root, year, month)
        generated.add(key)
        return path
    return root / "years" / f"{year:04d}" / f"{month:02d}.json"


def compare_case(root: Path, d: date, hour: int) -> tuple[bool, dict | None]:
    birth = GregorianBirth(d.year, d.month, d.day, hour, 0, 0)
    got = normalize_from_data(birth, root)
    current = normalize_gregorian_birth(
        GregorianBirthInput(d.year, d.month, d.day, hour, 0, 0)
    )
    expected = comparable_current(current)
    if got == expected:
        return True, None
    return False, {"date": d.isoformat(), "hour": hour, "expected": expected, "got": got}


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
    days = 0
    comparisons = 0
    mismatch_samples: list[dict] = []
    generated: set[tuple[int, int]] = set()
    shard_sizes: list[int] = []
    leap_identity_counts: dict[str, int] = {}
    hour_branch_counts: dict[str, int] = {}

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        for d in iter_dates(start, end):
            days += 1
            ensure_month(root, generated, d.year, d.month)
            next_day = d + timedelta(days=1)
            ensure_month(root, generated, next_day.year, next_day.month)

            # Every Gregorian day: ordinary civil time and the 23:00 next-day policy.
            for hour in (12, 23):
                ok, detail = compare_case(root, d, hour)
                comparisons += 1
                result = normalize_from_data(GregorianBirth(d.year, d.month, d.day, hour), root)
                leap = result["normalized_natal_input"]["leap_month_identity"]
                branch = result["normalized_natal_input"]["hour_branch"]
                leap_identity_counts[leap] = leap_identity_counts.get(leap, 0) + 1
                hour_branch_counts[branch] = hour_branch_counts.get(branch, 0) + 1
                if not ok and len(mismatch_samples) < args.max_mismatches:
                    mismatch_samples.append(detail)

            # Full 24-hour parity on every Gregorian month boundary day.
            if next_day.month != d.month:
                for hour in range(24):
                    ok, detail = compare_case(root, d, hour)
                    comparisons += 1
                    if not ok and len(mismatch_samples) < args.max_mismatches:
                        mismatch_samples.append(detail)

        for year, month in sorted(generated):
            p = root / "years" / f"{year:04d}" / f"{month:02d}.json"
            shard_sizes.append(p.stat().st_size)

    elapsed = time.monotonic() - t0
    report = {
        "schema_name": "ziwei_calendar_full_parity_report",
        "schema_version": "0.1.0",
        "status": "PASS" if not mismatch_samples else "FAIL",
        "research_only": True,
        "production_admission_changed": False,
        "candidate_window": {"start": start.isoformat(), "end": end.isoformat()},
        "days_checked": days,
        "comparisons": comparisons,
        "generated_month_shards": len(generated),
        "mismatch_count_observed": len(mismatch_samples),
        "mismatch_samples": mismatch_samples,
        "shard_size_bytes": {
            "min": min(shard_sizes) if shard_sizes else 0,
            "max": max(shard_sizes) if shard_sizes else 0,
            "mean": (sum(shard_sizes) / len(shard_sizes)) if shard_sizes else 0,
        },
        "one_query_max_files": 2,
        "elapsed_seconds": elapsed,
        "leap_identity_counts": leap_identity_counts,
        "hour_branch_counts_for_daily_core_cases": hour_branch_counts,
    }
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
