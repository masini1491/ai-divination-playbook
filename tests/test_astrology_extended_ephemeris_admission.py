from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.astrology_orchestrator import OrchestrationInputError, normalize_request, run_request
from tools.astrology_runtime import gate_bundle, validate_bundle

ROOT = Path(__file__).resolve().parents[1]
DATA_COMMIT = "0052ba1c0a3b65238b4f9ec3a94a1aff47e341ea"
DATASET_SHA = "580bb2a8ef463dfc6527ea611f27daad3562cb1fa5698391b3e2baeba64987bf"


def extended_provider(object_ids: list[str]) -> dict:
    return {
        "provider_id": "astrology-extended-ephemeris-c1-v1",
        "provider_version": "1.0.0",
        "dataset_id": "astrology-extended-ephemeris-c1-f32-v1",
        "dataset_sha256": DATASET_SHA,
        "representation_id": "c1-cheb-d7-w60-f32-c0mod360-v1",
        "exact_data_commit": DATA_COMMIT,
        "requested_object_ids": object_ids,
        "ordinary_runtime_network_required": False,
        "semantic_interpretation_authority": False,
        "default_aspect_participation": False,
    }


def extended_row(object_id: str = "Chiron") -> dict:
    return {
        "fact_id": f"fact:object:{object_id.lower()}",
        "object_type": "minor_planet",
        "object_id": object_id,
        "longitude_deg": 12.5,
        "speed_deg_per_day": 0.01,
        "motion": "direct",
        "sign_index": 0,
        "sign": "Aries",
        "sign_degree": 12.5,
        "house_number": 1,
        "segment_index": 100,
        "shard_index": 0,
        "dataset_id": "astrology-extended-ephemeris-c1-f32-v1",
        "dataset_sha256": DATASET_SHA,
        "representation_id": "c1-cheb-d7-w60-f32-c0mod360-v1",
        "exact_data_commit": DATA_COMMIT,
    }


def minimal_bundle() -> dict:
    return {
        "schema_name": "astrology_fact_bundle",
        "schema_version": "1.0.0",
        "method": "Astrology",
        "reading_mode": "natal",
        "fact_source": "approved_provider",
        "calculation_verification": "verified_provider",
        "subject_ref": "subject:extended-test",
        "birth_time_certainty": "exact",
        "configuration": {
            "zodiac_system": "tropical",
            "center": "geocentric",
            "house_system": "Whole Sign",
        },
        "provider": {"extended_ephemeris": extended_provider(["Chiron"])},
        "facts": {
            "objects": [extended_row()],
            "houses": [],
            "aspects": [],
            "events": [],
        },
    }


def known_time_request() -> dict:
    return {
        "schema_name": "astrology_reading_request",
        "schema_version": "1.0.0",
        "reading_mode": "natal",
        "subject_ref": "subject:extended-orchestrator",
        "birth": {
            "local_datetime": "1987-05-07T05:17:00",
            "birth_time_certainty": "exact",
            "house_system": "Whole Sign",
            "location": {
                "coordinates": {
                    "latitude": 25.0,
                    "longitude": 121.4,
                    "timezone_name": "Asia/Taipei",
                }
            },
        },
        "extended_objects": ["Chiron", "Ceres"],
    }


class AstrologyExtendedEphemerisAdmissionTests(unittest.TestCase):
    def test_admission_manifest_is_exact_commit_pinned_and_fact_only(self):
        data = json.loads((ROOT / "ASTROLOGY_EXTENDED_EPHEMERIS_ADMISSION_V1.json").read_text())
        self.assertEqual("PRODUCTION_ADMITTED", data["status"])
        self.assertEqual(DATA_COMMIT, data["dataset"]["exact_data_commit"])
        self.assertEqual(DATASET_SHA, data["dataset"]["expected_sha256"])
        self.assertEqual(17, data["dataset"]["shard_count"])
        self.assertEqual(40960, data["dataset"]["max_base64_transport_chars"])
        self.assertFalse(data["calculation_policy"]["default_aspect_participation"])
        self.assertFalse(data["calculation_policy"]["semantic_interpretation_authority"])
        self.assertEqual("not_admitted", data["calculation_policy"]["unknown_time"])
        self.assertEqual("not_admitted", data["calculation_policy"]["transit"])

    def test_runtime_admits_exact_extended_fact_provenance(self):
        gate = gate_bundle(minimal_bundle())
        self.assertTrue(gate["interpretation_allowed"], gate["errors"])

    def test_runtime_rejects_spoofed_dataset_identity(self):
        bundle = minimal_bundle()
        bundle["facts"]["objects"][0]["dataset_sha256"] = "0" * 64
        codes = {row["code"] for row in validate_bundle(bundle)}
        self.assertIn("EXTENDED_EPHEMERIS_ROW_IDENTITY_MISMATCH", codes)

    def test_runtime_rejects_provider_identity_mismatch(self):
        bundle = minimal_bundle()
        bundle["provider"]["extended_ephemeris"]["exact_data_commit"] = "0" * 40
        codes = {row["code"] for row in validate_bundle(bundle)}
        self.assertIn("EXTENDED_EPHEMERIS_PROVIDER_IDENTITY_MISMATCH", codes)

    def test_runtime_rejects_extended_provider_without_facts(self):
        bundle = minimal_bundle()
        bundle["facts"]["objects"] = []
        codes = {row["code"] for row in validate_bundle(bundle)}
        self.assertIn("EXTENDED_EPHEMERIS_PROVIDER_WITHOUT_FACTS", codes)

    def test_runtime_rejects_unknown_time_extended_exact_facts(self):
        bundle = minimal_bundle()
        bundle["birth_time_certainty"] = "unknown"
        bundle["configuration"]["house_system"] = None
        codes = {row["code"] for row in validate_bundle(bundle)}
        self.assertIn("EXTENDED_EPHEMERIS_KNOWN_TIME_REQUIRED", codes)

    def test_runtime_rejects_extended_object_as_default_natal_aspect_participant(self):
        bundle = minimal_bundle()
        sun = {
            "fact_id": "fact:object:sun",
            "object_type": "planet",
            "object_id": "Sun",
            "longitude_deg": 12.5,
        }
        bundle["facts"]["objects"].append(sun)
        bundle["facts"]["aspects"].append({
            "fact_id": "fact:aspect:sun:conjunction:chiron",
            "aspect": "conjunction",
            "orb_deg": 0.0,
            "left_ref": "fact:object:sun",
            "right_ref": "fact:object:chiron",
            "scope": "natal",
            "participant_policy_id": "aspect-participants-core-bodies-v1",
            "aspect_policy_id": "major-aspects-v1",
            "orb_policy_id": "major-aspect-orbs-v1",
        })
        bundle["provider"]["aspect_policies"] = {
            "participant_policy_id": "aspect-participants-core-bodies-v1",
            "participant_object_ids": ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto", "NorthNode"],
            "aspect_policy_id": "major-aspects-v1",
            "aspect_types": ["conjunction", "opposition", "trine", "square", "sextile"],
            "orb_policy_id": "major-aspect-orbs-v1",
            "max_orb_degrees": {"conjunction": 8.0, "opposition": 8.0, "trine": 7.0, "square": 7.0, "sextile": 5.0},
            "extended_points_or_angles": "not_admitted",
        }
        codes = {row["code"] for row in validate_bundle(bundle)}
        self.assertIn("NATAL_ASPECT_PARTICIPANT_NOT_ADMITTED", codes)

    def test_request_normalization_accepts_explicit_known_time_natal_extended_objects(self):
        normalized = normalize_request(known_time_request())
        self.assertEqual(["Chiron", "Ceres"], normalized["extended_objects"])

    def test_request_normalization_rejects_transit_extended_objects(self):
        request = known_time_request()
        request["reading_mode"] = "transit"
        request["transit"] = {
            "start_utc": "2026-01-01T00:00:00Z",
            "end_utc": "2026-01-02T00:00:00Z",
            "moving_bodies": ["Sun"],
            "include_transit_to_natal": False,
        }
        with self.assertRaisesRegex(OrchestrationInputError, "only when reading_mode=natal"):
            normalize_request(request)

    def test_request_normalization_rejects_unknown_time_extended_objects(self):
        request = known_time_request()
        request["birth"].pop("local_datetime")
        request["birth"]["local_date"] = "1987-05-07"
        request["birth"]["birth_time_certainty"] = "unknown"
        request["birth"]["house_system"] = None
        with self.assertRaisesRegex(OrchestrationInputError, "requires exact or approximate"):
            normalize_request(request)

    def test_orchestrator_appends_only_explicit_extended_rows_and_reapplies_gate(self):
        request = known_time_request()
        rows = [extended_row("Chiron"), extended_row("Ceres")]
        provider = extended_provider(["Chiron", "Ceres"])
        with patch("tools.astrology_orchestrator.build_extended_object_rows", return_value=(rows, provider)) as mocked:
            result = run_request(request)
        mocked.assert_called_once()
        natal = result["fact_bundles"]["natal"]
        ids = {row.get("object_id") for row in natal["facts"]["objects"]}
        self.assertTrue({"Chiron", "Ceres"}.issubset(ids))
        self.assertEqual(provider, natal["provider"]["extended_ephemeris"])
        self.assertTrue(result["runtime_gates"]["natal"]["interpretation_allowed"])
        provenance = result["reading_record_bridge"]["engine_provenance"]
        self.assertEqual("astrology-extended-ephemeris-c1-v1", provenance["extended_ephemeris_provider_id"])
        self.assertEqual(DATA_COMMIT, provenance["extended_ephemeris_data_commit"])

    def test_default_request_does_not_activate_extended_provider(self):
        request = known_time_request()
        request.pop("extended_objects")
        with patch("tools.astrology_orchestrator.build_extended_object_rows") as mocked:
            result = run_request(request)
        mocked.assert_not_called()
        self.assertNotIn("extended_ephemeris", result["fact_bundles"]["natal"]["provider"])


if __name__ == "__main__":
    unittest.main()
