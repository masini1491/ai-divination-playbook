from __future__ import annotations

import random
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from tools.ziwei_calendar_interval_poc import (
    CalendarIntervalUnavailable,
    GregorianBirth,
    normalize_from_interval_data,
    write_year_shard,
)
from tools.ziwei_calendar_provider import GregorianBirthInput, normalize_gregorian_birth

def comparable_current(result):
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

class ZiWeiCalendarIntervalPocTests(unittest.TestCase):
    def parity(self,root,case):
        got=normalize_from_interval_data(case,root)
        current=normalize_gregorian_birth(GregorianBirthInput(
            case.year,case.month,case.day,case.hour,case.minute,case.second,case.timezone
        ))
        self.assertEqual(comparable_current(current),got)

    def test_known_cases_and_cross_year_rat_hour(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            for y in (1999,2000,2001,2023,2024):
                write_year_shard(root,y)
            for case in (
                GregorianBirth(2000,8,16,5,30),
                GregorianBirth(2000,8,16,23,0),
                GregorianBirth(2023,4,5,12,0),
                GregorianBirth(2023,4,6,23,0),
                GregorianBirth(2000,12,31,23,0),
            ):
                with self.subTest(case=case):
                    self.parity(root,case)

    def test_all_hours(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); write_year_shard(root,2000); write_year_shard(root,2001)
            for hour in range(24):
                self.parity(root,GregorianBirth(2000,8,16,hour,17))

    def test_missing_year_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(CalendarIntervalUnavailable):
                normalize_from_interval_data(GregorianBirth(2000,8,16,12),Path(td))

    def test_deterministic_rebuild_same_year_bytes(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            pa=write_year_shard(Path(a),2000)
            pb=write_year_shard(Path(b),2000)
            self.assertEqual(pa.read_bytes(),pb.read_bytes())

    def test_candidate_edges_and_random_corpus(self):
        rng=random.Random(20260925)
        dates=[date(1900,1,1),date(2100,12,31)]
        span=(date(2100,12,30)-date(1900,1,2)).days
        dates.extend(date(1900,1,2)+timedelta(days=rng.randrange(span+1)) for _ in range(256))
        years={d.year for d in dates}
        years |= {(d+timedelta(days=1)).year for d in dates}
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            for year in sorted(years):
                write_year_shard(root,year)
            for d in dates:
                for hour in (0,12,23):
                    self.parity(root,GregorianBirth(d.year,d.month,d.day,hour))

if __name__=="__main__":
    unittest.main()
