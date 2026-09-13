from __future__ import annotations

import unittest

from tools.astrology_runtime import gate_bundle, validate_bundle


def natal_bundle() -> dict:
    return {
        "schema_name": "astrology_fact_bundle",
        "schema_version": "1.0.0",
        "method": "Astrology",
        "reading_mode": "natal",
        "fact_source": "user_supplied_structured_export",
        "calculation_verification": "user_asserted",
        "subject_ref": "subject:synthetic-a",
        "birth_time_certainty": "exact",
        "configuration": {
            "zodiac_system": "tropical",
            "center": "geocentric",
            "house_system": "Whole Sign",
        },
        "facts": {
            "objects": [
                {"fact_id": "fact:sun", "object_type": "planet", "object_id": "Sun"},
                {"fact_id": "fact:saturn", "object_type": "planet", "object_id": "Saturn"},
            ],
            "houses": [{"fact_id": "fact:house-1", "house_number": 1}],
            "aspects": [
                {
                    "fact_id": "fact:sun-square-saturn",
                    "aspect": "square",
                    "orb_deg": 2.0,
                    "left_ref": "fact:sun",
                    "right_ref": "fact:saturn",
                    "scope": "natal",
                }
            ],
            "events": [],
        },
    }


class AstrologyRuntimeTests(unittest.TestCase):
    def test_valid_user_supplied_natal_bundle_is_admitted(self):
        result = gate_bundle(natal_bundle())
        self.assertTrue(result["interpretation_allowed"])
        self.assertEqual("admitted", result["status"])

    def test_model_calculated_source_is_forbidden(self):
        data = natal_bundle()
        data["fact_source"] = "model_calculated"
        codes = {e["code"] for e in validate_bundle(data)}
        self.assertIn("FACT_SOURCE_FORBIDDEN", codes)

    def test_source_verification_pair_must_match(self):
        data = natal_bundle()
        data["calculation_verification"] = "verified_provider"
        codes = {e["code"] for e in validate_bundle(data)}
        self.assertIn("FACT_SOURCE_VERIFICATION_MISMATCH", codes)

    def test_approved_provider_requires_verified_provider_status(self):
        data = natal_bundle()
        data["fact_source"] = "approved_provider"
        data["calculation_verification"] = "user_asserted"
        codes = {e["code"] for e in validate_bundle(data)}
        self.assertIn("FACT_SOURCE_VERIFICATION_MISMATCH", codes)

    def test_unknown_birth_time_forbids_houses(self):
        data = natal_bundle()
        data["birth_time_certainty"] = "unknown"
        codes = {e["code"] for e in validate_bundle(data)}
        self.assertIn("UNKNOWN_TIME_HOUSES_FORBIDDEN", codes)

    def test_unknown_birth_time_forbids_angles(self):
        data = natal_bundle()
        data["birth_time_certainty"] = "unknown"
        data["facts"]["houses"] = []
        data["configuration"]["house_system"] = None
        data["facts"]["objects"].append({"fact_id": "fact:asc", "object_type": "angle", "object_id": "Ascendant"})
        codes = {e["code"] for e in validate_bundle(data)}
        self.assertIn("UNKNOWN_TIME_ANGLE_FORBIDDEN", codes)

    def test_house_facts_require_explicit_house_system(self):
        data = natal_bundle()
        data["configuration"]["house_system"] = None
        codes = {e["code"] for e in validate_bundle(data)}
        self.assertIn("HOUSE_SYSTEM_REQUIRED", codes)

    def test_unadmitted_house_system_is_rejected(self):
        data = natal_bundle()
        data["configuration"]["house_system"] = "Koch"
        codes = {e["code"] for e in validate_bundle(data)}
        self.assertIn("HOUSE_SYSTEM_UNSUPPORTED", codes)

    def test_minor_aspect_is_rejected(self):
        data = natal_bundle()
        data["facts"]["aspects"][0]["aspect"] = "quincunx"
        codes = {e["code"] for e in validate_bundle(data)}
        self.assertIn("ASPECT_UNSUPPORTED", codes)

    def test_major_aspect_over_orb_is_rejected(self):
        data = natal_bundle()
        data["facts"]["aspects"][0]["orb_deg"] = 7.5
        codes = {e["code"] for e in validate_bundle(data)}
        self.assertIn("ASPECT_ORB_EXCEEDS_POLICY", codes)

    def test_aspect_refs_must_resolve(self):
        data = natal_bundle()
        data["facts"]["aspects"][0]["right_ref"] = "fact:missing"
        codes = {e["code"] for e in validate_bundle(data)}
        self.assertIn("ASPECT_REF_UNKNOWN", codes)

    def test_transit_mode_requires_transit_fact(self):
        data = natal_bundle()
        data["reading_mode"] = "transit"
        data["facts"]["aspects"] = []
        codes = {e["code"] for e in validate_bundle(data)}
        self.assertIn("TRANSIT_FACT_REQUIRED", codes)

    def test_transit_event_is_admitted_in_transit_mode(self):
        data = natal_bundle()
        data["reading_mode"] = "transit"
        data["facts"]["events"] = [{"fact_id": "fact:station", "event_kind": "station"}]
        self.assertEqual([], validate_bundle(data))

    def test_timing_event_is_rejected_in_natal_mode(self):
        data = natal_bundle()
        data["facts"]["events"] = [{"fact_id": "fact:station", "event_kind": "station"}]
        codes = {e["code"] for e in validate_bundle(data)}
        self.assertIn("EVENTS_REQUIRE_TRANSIT_MODE", codes)

    def test_unsupported_reading_mode_is_rejected(self):
        data = natal_bundle()
        data["reading_mode"] = "synastry"
        codes = {e["code"] for e in validate_bundle(data)}
        self.assertIn("READING_MODE_UNSUPPORTED", codes)


if __name__ == "__main__":
    unittest.main()
