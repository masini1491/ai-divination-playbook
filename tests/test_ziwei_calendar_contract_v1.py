from __future__ import annotations
import json
import unittest
from pathlib import Path

from tools.ziwei_calendar_provider import GregorianBirthInput, normalize_gregorian_birth
from tools.ziwei_true_solar_time import PROFILE_ID as TRUE_SOLAR_PROFILE_ID
from tools.ziwei_gregorian_pipeline import (
    run_scope_a_gregorian,
    run_scope_a_gregorian_with_brightness,
)

ROOT=Path(__file__).resolve().parents[1]

class ZiWeiCalendarContractV1Tests(unittest.TestCase):
    def test_manifest_admits_exact_dataset_and_build_source_boundary(self):
        m=json.loads((ROOT/"ZIWEI_CALENDAR_ADMISSION_V1.json").read_text(encoding="utf-8"))
        self.assertEqual("PRODUCTION_ADMITTED_INPUT_ADAPTER",m["status"])
        self.assertEqual("ziwei-calendar-interval-data",m["calculation"]["provider_id"])
        self.assertEqual("2.2.0",m["calculation"]["provider_version"])
        self.assertEqual("repo_local_interval_data",m["calculation"]["runtime_dependency"])
        self.assertEqual(
            "ziwei_tw_interval_1900_2100_candidate_v1",
            m["calculation"]["dataset"]["id"],
        )
        self.assertEqual(
            "4913a39e770afcd21eedc387523c572b8c4fc6469889c28f6ea75613f8984d79",
            m["calculation"]["dataset"]["aggregate_sha256"],
        )
        self.assertEqual({"start":"1900-01-01","end":"2100-12-31"},m["scope"]["supported_gregorian_range"])
        self.assertEqual("lunar_python",m["calculation"]["build_source"]["package"])
        self.assertFalse(m["calculation"]["build_source"]["runtime_dependency"])
        self.assertEqual("explicit_IANA",m["scope"]["timezone"])
        self.assertEqual("civil-time-zoneinfo-v1",m["scope"]["civil_time_normalization"]["adapter_id"])
        self.assertEqual("ziwei.calendar.civil_v2",m["calculation"]["profile_id"])
        self.assertEqual("explicit_profile_only",m["scope"]["true_solar_time"])
        self.assertEqual(TRUE_SOLAR_PROFILE_ID,m["scope"]["optional_clock_profiles"]["true_solar_time"]["profile_id"])
        self.assertEqual("next_day_at_23",m["policy"]["rat_hour_policy"])
        self.assertEqual("split_after_day_15",m["policy"]["leap_month_policy"])

    def test_documented_solar_fixture_converts_to_expected_lunar_date(self):
        r=normalize_gregorian_birth(GregorianBirthInput(2000,8,16,5,30))
        self.assertEqual("ziwei-calendar-interval-data",r["provider"]["id"])
        self.assertEqual(2000,r["raw_lunar_conversion"]["year"])
        self.assertEqual(7,r["raw_lunar_conversion"]["month"])
        self.assertEqual(17,r["raw_lunar_conversion"]["day"])
        self.assertFalse(r["raw_lunar_conversion"]["is_leap_month"])
        self.assertEqual("卯",r["normalized_natal_input"]["hour_branch"])
        self.assertEqual(["years/2000.json"],r["dataset"]["required_shards"])
        self.assertFalse(r["build_source"]["runtime_dependency"])
        self.assertNotIn("dependency",r)

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

    def test_timezone_dst_range_and_invalid_date_fail_closed(self):
        with self.assertRaisesRegex(ValueError,"unknown IANA timezone"):
            normalize_gregorian_birth(GregorianBirthInput(2000,8,16,5,30,timezone="Mars/Olympus"))
        with self.assertRaisesRegex(ValueError,"unknown IANA timezone"):
            normalize_gregorian_birth(GregorianBirthInput(2000,8,16,5,30,timezone="+08:00"))
        with self.assertRaisesRegex(ValueError,"nonexistent"):
            normalize_gregorian_birth(GregorianBirthInput(2024,3,10,2,30,timezone="America/New_York"))
        with self.assertRaisesRegex(ValueError,"ambiguous"):
            normalize_gregorian_birth(GregorianBirthInput(2024,11,3,1,30,timezone="America/New_York"))
        with self.assertRaises(ValueError):
            normalize_gregorian_birth(GregorianBirthInput(2023,2,30,12,0))
        with self.assertRaisesRegex(ValueError,"outside selected candidate range"):
            normalize_gregorian_birth(GregorianBirthInput(1899,12,31,12,0))
        with self.assertRaisesRegex(ValueError,"outside selected candidate range"):
            normalize_gregorian_birth(GregorianBirthInput(2101,1,1,0,0))

    def test_non_taipei_uses_validated_local_calendar_fields_not_utc_date(self):
        tokyo=normalize_gregorian_birth(GregorianBirthInput(2000,1,1,0,30,timezone="Asia/Tokyo"))
        taipei=normalize_gregorian_birth(GregorianBirthInput(2000,1,1,0,30,timezone="Asia/Taipei"))
        self.assertEqual(
            taipei["raw_lunar_conversion"],
            tokyo["raw_lunar_conversion"],
        )
        self.assertEqual(
            taipei["normalized_natal_input"]["lunar_day"],
            tokyo["normalized_natal_input"]["lunar_day"],
        )
        self.assertEqual("2000-01-01",tokyo["civil_time_normalization"]["validated_local_iso"][:10])
        self.assertEqual("1999-12-31",tokyo["civil_time_normalization"]["resolved_utc_iso"][:10])
        self.assertEqual("Asia/Tokyo",tokyo["calendar_profile"]["timezone"])
        self.assertTrue(tokyo["boundaries"]["local_calendar_identity_preserved"])
        self.assertFalse(tokyo["boundaries"]["utc_rebase_for_lunar_conversion"])

    def test_sydney_explicit_iana_timezone_is_admitted(self):
        r=normalize_gregorian_birth(GregorianBirthInput(1990,6,15,10,0,timezone="Australia/Sydney"))
        self.assertEqual("Australia/Sydney",r["civil_time_normalization"]["timezone_name"])
        self.assertEqual(36000,r["civil_time_normalization"]["resolved_utc_offset_seconds"])
        self.assertEqual("civil-time-zoneinfo-v1",r["civil_time_normalization"]["normalizer_id"])

    def test_admitted_end_edge_uses_policy_tail_only_when_needed(self):
        ordinary=normalize_gregorian_birth(GregorianBirthInput(2100,12,31,22,59))
        late=normalize_gregorian_birth(GregorianBirthInput(2100,12,31,23,0))
        self.assertEqual(["years/2100.json"],ordinary["dataset"]["required_shards"])
        self.assertEqual(["years/2100.json","years/2101.json"],late["dataset"]["required_shards"])

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

    def test_explicit_true_solar_profile_changes_lookup_fields_and_preserves_civil_provenance(self):
        civil=normalize_gregorian_birth(
            GregorianBirthInput(2000,1,1,0,30,timezone="Asia/Shanghai")
        )
        solar=normalize_gregorian_birth(
            GregorianBirthInput(
                2000,1,1,0,30,timezone="Asia/Shanghai",
                true_solar_time_profile=TRUE_SOLAR_PROFILE_ID,
                longitude_deg=87.6168,
            )
        )
        self.assertEqual(["years/2000.json"],civil["dataset"]["required_shards"])
        self.assertEqual(["years/1999.json"],solar["dataset"]["required_shards"])
        self.assertEqual(
            "1999-12-31T22:17:47",
            solar["true_solar_time_normalization"]["apparent_solar_local_iso"],
        )
        self.assertEqual(
            "2000-01-01",
            solar["civil_time_normalization"]["validated_local_iso"][:10],
        )
        self.assertEqual("true_solar_time",solar["calendar_profile"]["clock_mode"])
        self.assertEqual(TRUE_SOLAR_PROFILE_ID,solar["calendar_profile"]["true_solar_time"])
        self.assertTrue(solar["boundaries"]["true_solar_time_applied"])
        self.assertTrue(solar["boundaries"]["apparent_solar_fields_used_for_lunar_conversion"])
        self.assertFalse(solar["boundaries"]["local_calendar_identity_preserved"])
        self.assertNotEqual(civil["raw_lunar_conversion"],solar["raw_lunar_conversion"])

    def test_true_solar_profile_requires_explicit_matching_longitude(self):
        with self.assertRaisesRegex(ValueError,"supplied together"):
            normalize_gregorian_birth(
                GregorianBirthInput(
                    2000,1,1,12,0,
                    true_solar_time_profile=TRUE_SOLAR_PROFILE_ID,
                )
            )
        with self.assertRaisesRegex(ValueError,"supplied together"):
            normalize_gregorian_birth(
                GregorianBirthInput(2000,1,1,12,0,longitude_deg=121.5)
            )
        with self.assertRaisesRegex(ValueError,"unsupported"):
            normalize_gregorian_birth(
                GregorianBirthInput(
                    2000,1,1,12,0,
                    true_solar_time_profile="unknown",
                    longitude_deg=121.5,
                )
            )

if __name__=="__main__":
    unittest.main()
