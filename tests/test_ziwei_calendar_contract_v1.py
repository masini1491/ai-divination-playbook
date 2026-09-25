from __future__ import annotations
import json
import unittest
from pathlib import Path

from tools.ziwei_calendar_provider import GregorianBirthInput, normalize_gregorian_birth
from tools.ziwei_gregorian_pipeline import (
    run_scope_a_gregorian,
    run_scope_a_gregorian_with_brightness,
)

ROOT=Path(__file__).resolve().parents[1]

class ZiWeiCalendarContractV1Tests(unittest.TestCase):
    def test_manifest_pins_dependency_and_boundary(self):
        m=json.loads((ROOT/"ZIWEI_CALENDAR_ADMISSION_V1.json").read_text(encoding="utf-8"))
        self.assertEqual("PRODUCTION_ADMITTED_INPUT_ADAPTER",m["status"])
        self.assertEqual("ziwei-calendar-interval-data",m["calculation"]["provider_id"])
        self.assertEqual("2.0.0",m["calculation"]["provider_version"])
        self.assertEqual("ziwei_tw_interval_1900_2100_candidate_v1",m["calculation"]["dataset_id"])
        self.assertEqual("4913a39e770afcd21eedc387523c572b8c4fc6469889c28f6ea75613f8984d79",m["calculation"]["dataset_aggregate_sha256"])
        self.assertTrue(m["calculation"]["dataset_production_use_admitted"])
        self.assertFalse(m["calculation"]["build_parity_dependency"]["runtime_required"])
        self.assertEqual({"start":"1900-01-01","end":"2100-12-31"},m["scope"]["supported_gregorian_range"])
        self.assertEqual("Asia/Taipei",m["scope"]["timezone"])
        self.assertEqual("next_day_at_23",m["policy"]["rat_hour_policy"])
        self.assertEqual("split_after_day_15",m["policy"]["leap_month_policy"])

    def test_documented_solar_fixture_converts_to_expected_lunar_date(self):
        r=normalize_gregorian_birth(GregorianBirthInput(2000,8,16,5,30))
        self.assertEqual(2000,r["raw_lunar_conversion"]["year"])
        self.assertEqual(7,r["raw_lunar_conversion"]["month"])
        self.assertEqual(17,r["raw_lunar_conversion"]["day"])
        self.assertFalse(r["raw_lunar_conversion"]["is_leap_month"])
        self.assertEqual("卯",r["normalized_natal_input"]["hour_branch"])

    def test_late_rat_hour_advances_policy_date_but_preserves_raw_conversion(self):
        early=normalize_gregorian_birth(GregorianBirthInput(2000,8,16,22,59))
        late=normalize_gregorian_birth(GregorianBirthInput(2000,8,16,23,0))
        self.assertEqual(17,early["normalized_natal_input"]["lunar_day"])
        self.assertEqual(17,late["raw_lunar_conversion"]["day"])
        self.assertEqual(18,late["normalized_natal_input"]["lunar_day"])
        self.assertEqual("子",late["normalized_natal_input"]["hour_branch"])
        self.assertTrue(late["policy_lunar_conversion"]["rat_hour_date_shift_applied"])

    def test_leap_month_policy_is_explicit(self):
        first=normalize_gregorian_birth(GregorianBirthInput(2023,4,5,12,0))
        second=normalize_gregorian_birth(GregorianBirthInput(2023,4,6,12,0))
        self.assertTrue(first["raw_lunar_conversion"]["is_leap_month"])
        self.assertEqual(2,first["raw_lunar_conversion"]["month"])
        self.assertEqual(15,first["raw_lunar_conversion"]["day"])
        self.assertEqual(2,first["normalized_natal_input"]["lunar_month"])
        self.assertEqual(3,second["normalized_natal_input"]["lunar_month"])
        self.assertIn("day_1_15_as_same_month",first["normalized_natal_input"]["leap_month_identity"])
        self.assertIn("day_16_plus_as_next_month",second["normalized_natal_input"]["leap_month_identity"])

    def test_timezone_and_invalid_date_fail_closed(self):
        with self.assertRaises(ValueError):
            normalize_gregorian_birth(GregorianBirthInput(2000,8,16,5,30,timezone="UTC"))
        with self.assertRaises(ValueError):
            normalize_gregorian_birth(GregorianBirthInput(2023,2,30,12,0))

    def test_supported_range_and_policy_tail_fail_closed(self):
        with self.assertRaisesRegex(ValueError,"outside admitted range"):
            normalize_gregorian_birth(GregorianBirthInput(1899,12,31,12,0))
        with self.assertRaisesRegex(ValueError,"outside admitted range"):
            normalize_gregorian_birth(GregorianBirthInput(2101,1,1,0,0))
        tail=normalize_gregorian_birth(GregorianBirthInput(2100,12,31,23,0))
        self.assertEqual(
            ["data/calendar/ziwei_tw_interval/v1/years/2100.json","data/calendar/ziwei_tw_interval/v1/years/2101.json"],
            tail["dataset"]["required_shards"],
        )
        self.assertFalse(tail["dependency"]["runtime_required"])

    def test_gregorian_pipeline_reaches_scope_a(self):
        r=run_scope_a_gregorian(
            GregorianBirthInput(2000,8,16,5,30),
            request_id="gregorian-scope-a",
            requested_subjects=("紫微",),
        )
        self.assertEqual("PRODUCTION_ADMITTED",r["status"])
        self.assertTrue(r["authority"]["gregorian_input_adapter_admitted"])
        self.assertEqual("gregorian",r["input_adapter"]["calendar"]["input"]["calendar"])
        self.assertEqual({"紫微"},set(r["interpretation"]["subject_claims"]))

    def test_gregorian_pipeline_composes_with_optional_brightness(self):
        r=run_scope_a_gregorian_with_brightness(
            GregorianBirthInput(2000,8,16,5,30),
            request_id="gregorian-brightness",
            requested_subjects=("太陽",),
        )
        self.assertTrue(r["authority"]["gregorian_input_adapter_admitted"])
        self.assertTrue(r["authority"]["brightness_profile_admitted"])
        self.assertEqual("computed_by_optional_profile",r["calculation"]["unsupported"]["brightness"])

if __name__=="__main__":
    unittest.main()
