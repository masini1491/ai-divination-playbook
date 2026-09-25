from __future__ import annotations

import json
import random
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from tools.ziwei_calendar_data_poc import (
    CalendarDataUnavailable,
    GregorianBirth,
    aggregate_hash,
    normalize_from_data,
    shard_relative_path,
    write_month_shard,
)
from tools.ziwei_calendar_provider import GregorianBirthInput, normalize_gregorian_birth

ROOT=Path(__file__).resolve().parents[1]
POC_ROOT=ROOT/"data"/"calendar"/"ziwei_tw_poc_v0"

def _comparable_current(result):
    return {
        "raw_lunar_conversion":result["raw_lunar_conversion"],
        "policy_lunar_conversion":result["policy_lunar_conversion"],
        "normalized_natal_input":{
            "lunar_year":result["normalized_natal_input"]["lunar_year"],
            "lunar_month":result["normalized_natal_input"]["lunar_month"],
            "lunar_day":result["normalized_natal_input"]["lunar_day"],
            "hour_branch":result["normalized_natal_input"]["hour_branch"],
            "leap_month_identity":result["normalized_natal_input"]["leap_month_identity"],
        },
    }

class ZiWeiCalendarDataPocTests(unittest.TestCase):
    def test_committed_fixture_manifest_hashes_and_query_size(self):
        manifest=json.loads((POC_ROOT/"MANIFEST.json").read_text(encoding="utf-8"))
        rels=[Path(x["path"]) for x in manifest["sample_shards"]]
        self.assertEqual(manifest["aggregate_hash"],aggregate_hash(POC_ROOT,rels))
        for item in manifest["sample_shards"]:
            path=POC_ROOT/item["path"]
            self.assertLess(path.stat().st_size,1024)
        self.assertFalse(manifest["production_admitted"])
        self.assertEqual(1,manifest["one_query_contract"]["ordinary_date_max_files"])
        self.assertEqual(2,manifest["one_query_contract"]["rat_hour_cross_month_max_files"])

    def test_committed_fixture_parity_with_current_provider(self):
        cases=[
            GregorianBirth(2000,8,16,5,30),
            GregorianBirth(2000,8,16,23,0),
            GregorianBirth(2023,4,5,12,0),
            GregorianBirth(2023,4,6,12,0),
        ]
        for case in cases:
            with self.subTest(case=case):
                got=normalize_from_data(case,POC_ROOT)
                current=normalize_gregorian_birth(GregorianBirthInput(
                    case.year,case.month,case.day,case.hour,case.minute,case.second,case.timezone
                ))
                self.assertEqual(_comparable_current(current),got)

    def test_missing_date_fails_closed(self):
        with self.assertRaises(CalendarDataUnavailable):
            normalize_from_data(GregorianBirth(2000,8,18,12,0),POC_ROOT)

    def test_generated_month_resolver_parity_every_hour_branch(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            write_month_shard(root,2000,8)
            write_month_shard(root,2000,9)
            for hour in range(24):
                case=GregorianBirth(2000,8,16,hour,17)
                got=normalize_from_data(case,root)
                current=normalize_gregorian_birth(GregorianBirthInput(2000,8,16,hour,17))
                self.assertEqual(_comparable_current(current),got)

    def test_generated_leap_month_boundary_parity(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            write_month_shard(root,2023,4)
            for day in (5,6):
                for hour in (0,12,23):
                    case=GregorianBirth(2023,4,day,hour,0)
                    got=normalize_from_data(case,root)
                    current=normalize_gregorian_birth(GregorianBirthInput(2023,4,day,hour,0))
                    self.assertEqual(_comparable_current(current),got)

    def test_candidate_range_edges_and_deterministic_random_corpus(self):
        # Research-only feasibility range. This does not admit or narrow production input range.
        rng=random.Random(20260925)
        dates=[date(1900,1,1),date(2100,12,31)]
        span=(date(2100,12,30)-date(1900,1,2)).days
        dates.extend(date(1900,1,2)+timedelta(days=rng.randrange(span+1)) for _ in range(128))
        by_month=sorted({(d.year,d.month) for d in dates} | {
            ((d+timedelta(days=1)).year,(d+timedelta(days=1)).month) for d in dates
        })
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            for year,month in by_month:
                write_month_shard(root,year,month)
            for d in dates:
                for hour in (0,1,22,23):
                    case=GregorianBirth(d.year,d.month,d.day,hour,0)
                    got=normalize_from_data(case,root)
                    current=normalize_gregorian_birth(GregorianBirthInput(d.year,d.month,d.day,hour,0))
                    self.assertEqual(_comparable_current(current),got)

if __name__=="__main__":
    unittest.main()
