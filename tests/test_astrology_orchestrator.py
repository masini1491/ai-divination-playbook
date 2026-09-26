from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from tools.astrology_orchestrator import OrchestrationInputError, normalize_request, run_request
from tools.astrology_place_resolver import PlaceResolutionError

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "astrology_reading_request_transit_v1.json"


class AstrologyOrchestratorTests(unittest.TestCase):
    def test_module_cli_runs_end_to_end_fixture(self):
        completed = subprocess.run(
            [sys.executable, "-m", "tools.astrology_orchestrator", str(FIXTURE)],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, completed.returncode, completed.stderr or completed.stdout)
        result = json.loads(completed.stdout)
        self.assertEqual("admitted", result["status"])
        self.assertTrue(result["interpretation_allowed"])
        self.assertEqual(
            "astrology-production-orchestrator-v1",
            result["orchestrator"]["orchestrator_id"],
        )
        self.assertIn("natal", result["fact_bundles"])
        self.assertIn("transit", result["fact_bundles"])

    def test_end_to_end_place_natal_transit_runtime_pipeline(self):
        request = json.loads(FIXTURE.read_text(encoding="utf-8"))
        result = run_request(request)

        self.assertEqual("astrology_reading_run", result["schema_name"])
        self.assertEqual("1.0.0", result["schema_version"])
        self.assertEqual("admitted", result["status"])
        self.assertTrue(result["interpretation_allowed"])
        self.assertEqual("JP", result["normalized_request"]["birth"]["location"]["place"]["country_code"])
        self.assertEqual("offline_place_resolver", result["input_resolution"]["resolution_mode"])
        self.assertEqual("Asia/Tokyo", result["input_resolution"]["resolved"]["timezone_name"])

        natal = result["fact_bundles"]["natal"]
        transit = result["fact_bundles"]["transit"]
        self.assertEqual("natal", natal["reading_mode"])
        self.assertEqual("transit", transit["reading_mode"])
        self.assertTrue(result["runtime_gates"]["natal"]["interpretation_allowed"])
        self.assertTrue(result["runtime_gates"]["transit"]["interpretation_allowed"])

        events = transit["facts"]["events"]
        self.assertGreaterEqual(len(events), 1)
        self.assertTrue(any(event["event_kind"] == "transit_to_natal" for event in events))

        bridge = result["reading_record_bridge"]
        self.assertEqual("READING_RECORD.md", bridge["target_owner"])
        self.assertEqual("2", bridge["target_record_schema_version"])
        self.assertFalse(bridge["complete_reading_record"])
        self.assertEqual("external_only", bridge["storage_policy"])
        self.assertEqual(
            "astrology-production-orchestrator-v1",
            bridge["engine_provenance"]["orchestrator_id"],
        )

    def test_explicit_coordinates_bypass_place_resolver(self):
        request = {
            "schema_name": "astrology_reading_request",
            "schema_version": "1.0.0",
            "reading_mode": "natal",
            "subject_ref": "fixture-explicit-location",
            "birth": {
                "local_datetime": "1990-06-15T10:00:00",
                "birth_time_certainty": "exact",
                "house_system": "Whole Sign",
                "location": {
                    "coordinates": {
                        "latitude": 35.6895,
                        "longitude": 139.6917,
                        "timezone_name": "Asia/Tokyo",
                    }
                },
            },
        }
        result = run_request(request)
        self.assertEqual("admitted", result["status"])
        self.assertEqual("explicit_coordinates", result["input_resolution"]["resolution_mode"])
        self.assertNotIn("resolver", result["input_resolution"])
        self.assertNotIn("transit", result["fact_bundles"])

    def test_full_taiwan_admin_locality_runs_through_existing_place_resolver(self):
        request = {
            "schema_name": "astrology_reading_request",
            "schema_version": "1.0.0",
            "reading_mode": "natal",
            "subject_ref": "fixture-taiwan-admin-locality",
            "birth": {
                "local_datetime": "1987-05-07T05:17:00",
                "birth_time_certainty": "exact",
                "house_system": "Whole Sign",
                "location": {"place": {"name": "新北市樹林區"}},
            },
        }
        result = run_request(request)
        self.assertEqual("admitted", result["status"])
        resolution = result["input_resolution"]
        self.assertEqual("offline_place_resolver", resolution["resolution_mode"])
        self.assertEqual(1668875, resolution["resolved"]["geoname_id"])
        self.assertEqual("Asia/Taipei", resolution["resolved"]["timezone_name"])
        self.assertEqual(
            "taiwan-admin-locality-v1",
            resolution["query"]["normalization"]["normalization_policy_id"],
        )

    def test_unknown_time_country_only_natal_emits_invariant_signs(self):
        request = {
            "schema_name": "astrology_reading_request",
            "schema_version": "1.0.0",
            "reading_mode": "natal",
            "subject_ref": "fixture-date-only-taiwan",
            "birth": {
                "local_date": "2006-03-14",
                "birth_time_certainty": "unknown",
                "house_system": None,
                "location": {"country": {"name": "Taiwan", "country_code": "TW"}},
            },
        }
        result = run_request(request)
        self.assertEqual("admitted", result["status"])
        self.assertEqual("offline_country_timezone_resolver", result["input_resolution"]["resolution_mode"])
        natal = result["fact_bundles"]["natal"]
        self.assertEqual("unknown", natal["birth_time_certainty"])
        self.assertIsNone(natal["configuration"]["house_system"])
        self.assertEqual([], natal["facts"]["houses"])
        self.assertEqual([], natal["facts"]["aspects"])
        objects = {row["object_id"]: row for row in natal["facts"]["objects"]}
        self.assertEqual("Pisces", objects["Sun"]["sign"])

    def test_unknown_time_is_not_admitted_for_transit(self):
        request = {
            "schema_name": "astrology_reading_request",
            "schema_version": "1.0.0",
            "reading_mode": "transit",
            "subject_ref": "fixture-date-only-transit",
            "birth": {
                "local_date": "2006-03-14",
                "birth_time_certainty": "unknown",
                "house_system": None,
                "location": {"country": {"country_code": "TW"}},
            },
            "transit": {
                "start_utc": "2026-06-01T00:00:00Z",
                "end_utc": "2026-07-01T00:00:00Z",
                "moving_bodies": ["Sun"],
                "natal_targets": ["Sun"],
                "aspects": ["conjunction"],
            },
        }
        with self.assertRaisesRegex(OrchestrationInputError, "only for natal"):
            normalize_request(request)

    def test_ambiguous_place_fails_closed(self):
        request = {
            "schema_name": "astrology_reading_request",
            "schema_version": "1.0.0",
            "reading_mode": "natal",
            "subject_ref": "fixture-ambiguous-place",
            "birth": {
                "local_datetime": "1990-06-15T10:00:00",
                "birth_time_certainty": "exact",
                "house_system": "Whole Sign",
                "location": {"place": {"name": "Springfield"}},
            },
        }
        with self.assertRaisesRegex(PlaceResolutionError, "ambiguous"):
            run_request(request)

    def test_location_mode_is_exclusive(self):
        request = {
            "schema_name": "astrology_reading_request",
            "schema_version": "1.0.0",
            "reading_mode": "natal",
            "subject_ref": "fixture-invalid-location",
            "birth": {
                "local_datetime": "1990-06-15T10:00:00",
                "birth_time_certainty": "exact",
                "house_system": "Whole Sign",
                "location": {
                    "place": {"name": "Tokyo", "country_code": "JP"},
                    "coordinates": {
                        "latitude": 35.6895,
                        "longitude": 139.6917,
                        "timezone_name": "Asia/Tokyo",
                    },
                },
            },
        }
        with self.assertRaisesRegex(OrchestrationInputError, "exactly one"):
            normalize_request(request)

    def test_transit_block_required_only_for_transit_mode(self):
        base = {
            "schema_name": "astrology_reading_request",
            "schema_version": "1.0.0",
            "subject_ref": "fixture-mode",
            "birth": {
                "local_datetime": "1990-06-15T10:00:00",
                "birth_time_certainty": "exact",
                "house_system": "Whole Sign",
                "location": {"place": {"name": "Tokyo", "country_code": "JP"}},
            },
        }
        transit_missing = {**base, "reading_mode": "transit"}
        with self.assertRaisesRegex(OrchestrationInputError, "required"):
            normalize_request(transit_missing)

        natal_with_transit = {
            **base,
            "reading_mode": "natal",
            "transit": {
                "start_utc": "2026-06-01T00:00:00Z",
                "end_utc": "2026-07-01T00:00:00Z",
                "moving_bodies": ["Sun"],
                "natal_targets": ["Sun"],
                "aspects": ["conjunction"],
            },
        }
        with self.assertRaisesRegex(OrchestrationInputError, "only allowed"):
            normalize_request(natal_with_transit)


if __name__ == "__main__":
    unittest.main()
