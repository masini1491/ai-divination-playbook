from __future__ import annotations

from datetime import date
import json
import random
import shutil
import tempfile
from pathlib import Path
import unittest

from tools.ziwei_calendar_data_provider import (
    DATASET_ROOT,
    CalendarDataUnavailable,
    CandidateGregorianBirth,
    load_manifest,
    normalize_candidate_birth,
    required_shard_paths,
    required_shard_years,
)
from tools.ziwei_calendar_provider import GregorianBirthInput, normalize_gregorian_birth

ROOT=Path(__file__).resolve().parents[1]

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

class ZiWeiCalendarDataProviderCandidateTests(unittest.TestCase):
    def assertParity(self,birth:CandidateGregorianBirth):
        got=normalize_candidate_birth(birth)
        current=normalize_gregorian_birth(GregorianBirthInput(
            birth.year,birth.month,birth.day,birth.hour,birth.minute,birth.second,birth.timezone
        ))
        self.assertEqual(comparable_current(current),{
            "raw_lunar_conversion":got["raw_lunar_conversion"],
            "policy_lunar_conversion":got["policy_lunar_conversion"],
            "normalized_natal_input":got["normalized_natal_input"],
        })

    def test_manifest_contract_and_dependency_free_source(self):
        m=load_manifest()
        self.assertEqual("ziwei_tw_interval_1900_2100_candidate_v1",m["dataset_id"])
        self.assertFalse(m["production_admitted"])
        source=(ROOT/"tools"/"ziwei_calendar_data_provider.py").read_text(encoding="utf-8")
        self.assertNotIn("from lunar_python",source)
        self.assertNotIn("import lunar_python",source)

    def test_required_shards_are_query_bounded(self):
        ordinary=CandidateGregorianBirth(2000,8,16,5,30)
        self.assertEqual((2000,),required_shard_years(ordinary))
        self.assertEqual(("years/2000.json",),required_shard_paths(ordinary))
        edge=CandidateGregorianBirth(2100,12,31,23,0)
        self.assertEqual((2100,2101),required_shard_years(edge))
        self.assertEqual(("years/2100.json","years/2101.json"),required_shard_paths(edge))

    def test_selected_range_is_fail_closed(self):
        with self.assertRaisesRegex(CalendarDataUnavailable,"outside selected candidate range"):
            required_shard_years(CandidateGregorianBirth(1899,12,31,12))
        with self.assertRaisesRegex(CalendarDataUnavailable,"outside selected candidate range"):
            required_shard_years(CandidateGregorianBirth(2101,1,1,0))

    def test_documented_and_policy_edge_fixtures_match_current_provider(self):
        for birth in (
            CandidateGregorianBirth(1900,1,1,0,0),
            CandidateGregorianBirth(2000,8,16,5,30),
            CandidateGregorianBirth(2000,8,16,23,0),
            CandidateGregorianBirth(2023,4,5,12,0),
            CandidateGregorianBirth(2023,4,6,12,0),
            CandidateGregorianBirth(2099,12,31,23,0),
            CandidateGregorianBirth(2100,12,31,22,59),
            CandidateGregorianBirth(2100,12,31,23,0),
        ):
            with self.subTest(birth=birth):
                self.assertParity(birth)

    def test_fixed_random_corpus_matches_current_provider(self):
        rng=random.Random(20260925)
        start=date(1900,1,1); end=date(2100,12,31)
        span=(end-start).days
        for _ in range(200):
            d=date.fromordinal(start.toordinal()+rng.randint(0,span))
            hour=rng.randint(0,23)
            birth=CandidateGregorianBirth(d.year,d.month,d.day,hour,rng.randint(0,59),rng.randint(0,59))
            with self.subTest(date=d.isoformat(),hour=hour):
                self.assertParity(birth)

    def test_missing_and_tampered_shards_fail_closed(self):
        manifest=load_manifest()
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            shutil.copy2(DATASET_ROOT/"MANIFEST.json",root/"MANIFEST.json")
            item=next(x for x in manifest["shards"] if x["year"]==2000)
            src=DATASET_ROOT/item["path"]; dst=root/item["path"]
            dst.parent.mkdir(parents=True,exist_ok=True)
            with self.assertRaisesRegex(CalendarDataUnavailable,"shard unavailable"):
                normalize_candidate_birth(CandidateGregorianBirth(2000,8,16,5,30),root)
            shutil.copy2(src,dst)
            dst.write_text(dst.read_text(encoding="utf-8")+"\n",encoding="utf-8")
            with self.assertRaisesRegex(CalendarDataUnavailable,"byte-size mismatch|sha256 mismatch"):
                normalize_candidate_birth(CandidateGregorianBirth(2000,8,16,5,30),root)

    def test_manifest_tamper_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            root.mkdir(parents=True,exist_ok=True)
            m=load_manifest().copy()
            m["dataset_id"]="wrong"
            (root/"MANIFEST.json").write_text(json.dumps(m),encoding="utf-8")
            with self.assertRaisesRegex(CalendarDataUnavailable,"identity/status mismatch"):
                normalize_candidate_birth(CandidateGregorianBirth(2000,8,16,5,30),root)

if __name__=="__main__":
    unittest.main()
