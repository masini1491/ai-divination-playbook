from __future__ import annotations

import json
import unittest
from pathlib import Path

from tools.astrology_provider import _resolve_local_time
from tools.civil_time_normalizer import (
    CivilTimeNormalizationError,
    NORMALIZER_ID,
    NORMALIZER_VERSION,
    normalize_civil_time,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "civil_time_normalization_v1.json"
ADMISSION = ROOT / "CIVIL_TIME_NORMALIZER_ADMISSION_V1.json"


class CivilTimeNormalizerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_unique_fixture_cases(self) -> None:
        for case in self.fixture["unique_cases"]:
            with self.subTest(case=case["id"]):
                result = normalize_civil_time(case["local_datetime"], case["timezone_name"])
                expected = case["expected"]
                self.assertEqual(expected["validated_local_iso"], result.validated_local_datetime.isoformat())
                self.assertEqual(expected["resolved_utc_iso"], result.resolved_utc_instant.isoformat())
                self.assertEqual(expected["resolved_utc_offset_seconds"], result.resolved_utc_offset_seconds)
                self.assertEqual(expected["fold"], result.fold)
                self.assertEqual(expected["resolution_status"], result.resolution_status)
                self.assertEqual(case["timezone_name"], result.timezone_name)
                self.assertEqual(NORMALIZER_ID, result.normalizer_id)
                self.assertEqual(NORMALIZER_VERSION, result.normalizer_version)

    def test_fail_closed_fixture_cases(self) -> None:
        for case in self.fixture["error_cases"]:
            with self.subTest(case=case["id"]):
                with self.assertRaisesRegex(CivilTimeNormalizationError, case["error_contains"]):
                    normalize_civil_time(case["local_datetime"], case["timezone_name"])

    def test_local_calendar_identity_is_not_rebased_to_utc(self) -> None:
        case = next(row for row in self.fixture["unique_cases"] if row["id"] == "tokyo_local_date_preserved_across_utc_boundary")
        result = normalize_civil_time(case["local_datetime"], case["timezone_name"])
        self.assertEqual("2000-01-01", result.validated_local_datetime.date().isoformat())
        self.assertEqual("1999-12-31", result.resolved_utc_instant.date().isoformat())
        self.assertNotEqual(result.validated_local_datetime.date(), result.resolved_utc_instant.date())

    def test_astrology_compatibility_wrapper_preserves_tuple_contract(self) -> None:
        shared = normalize_civil_time("1990-06-15T10:00:00", "Australia/Sydney")
        local, utc, fold = _resolve_local_time("1990-06-15T10:00:00", "Australia/Sydney")
        self.assertEqual(shared.validated_local_datetime, local)
        self.assertEqual(shared.resolved_utc_instant, utc)
        self.assertEqual(shared.fold, fold)

    def test_provenance_exposes_local_and_utc_as_distinct_facts(self) -> None:
        result = normalize_civil_time("2000-06-01T12:00:00", "Asia/Taipei")
        provenance = result.provenance()
        self.assertEqual("civil-time-zoneinfo-v1", provenance["normalizer_id"])
        self.assertEqual("1.0.0", provenance["normalizer_version"])
        self.assertEqual("Asia/Taipei", provenance["timezone_name"])
        self.assertEqual("2000-06-01T12:00:00+08:00", provenance["validated_local_iso"])
        self.assertEqual("2000-06-01T04:00:00+00:00", provenance["resolved_utc_iso"])
        self.assertEqual(28800, provenance["resolved_utc_offset_seconds"])
        self.assertEqual("python-zoneinfo", provenance["timezone_rule_source"])

    def test_admission_keeps_ziwei_consumer_closed(self) -> None:
        manifest = json.loads(ADMISSION.read_text(encoding="utf-8"))
        self.assertEqual("PRODUCTION_ADMITTED_SHARED_INPUT_ADAPTER", manifest["status"])
        self.assertEqual("PRODUCTION_ADMITTED", manifest["consumers"]["Astrology"]["status"])
        self.assertEqual("PRODUCTION_ADMITTED", manifest["consumers"]["ZiWei"]["status"])
        self.assertFalse(manifest["scope"]["true_solar_time"])
        self.assertFalse(manifest["scope"]["birthplace_timezone_resolution"])


if __name__ == "__main__":
    unittest.main()
