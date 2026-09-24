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
        data["facts"]["aspects"] = []
        data["configuration"]["house_system"] = None
        data["facts"]["objects"].append({"fact_id": "fact:asc", "object_type": "angle", "object_id": "Ascendant"})
        codes = {e["code"] for e in validate_bundle(data)}
        self.assertIn("UNKNOWN_TIME_ANGLE_FORBIDDEN", codes)

    def test_unknown_birth_time_forbids_exact_position_detail(self):
        data = natal_bundle()
        data["birth_time_certainty"] = "unknown"
        data["facts"]["houses"] = []
        data["facts"]["aspects"] = []
        data["configuration"]["house_system"] = None
        data["facts"]["objects"][0]["longitude_deg"] = 353.5
        data["facts"]["objects"][0]["sign_degree"] = 23.5
        codes = {e["code"] for e in validate_bundle(data)}
        self.assertIn("UNKNOWN_TIME_POSITION_DETAIL_FORBIDDEN", codes)

    def test_unknown_birth_time_forbids_natal_aspects(self):
        data = natal_bundle()
        data["birth_time_certainty"] = "unknown"
        data["facts"]["houses"] = []
        data["configuration"]["house_system"] = None
        codes = {e["code"] for e in validate_bundle(data)}
        self.assertIn("UNKNOWN_TIME_ASPECTS_FORBIDDEN", codes)

    def test_unknown_birth_time_is_natal_only_at_runtime_gate(self):
        data = natal_bundle()
        data["birth_time_certainty"] = "unknown"
        data["reading_mode"] = "transit"
        data["facts"]["houses"] = []
        data["facts"]["aspects"] = []
        data["configuration"]["house_system"] = None
        data["facts"]["events"] = [{"fact_id": "fact:station", "event_kind": "station"}]
        codes = {e["code"] for e in validate_bundle(data)}
        self.assertIn("UNKNOWN_TIME_TRANSIT_FORBIDDEN", codes)

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

    def test_natal_aspect_cannot_reference_house_fact(self):
        data = natal_bundle()
        data["facts"]["aspects"][0]["right_ref"] = "fact:house-1"
        codes = {e["code"] for e in validate_bundle(data)}
        self.assertIn("NATAL_ASPECT_ENDPOINT_NOT_OBJECT", codes)

    def test_natal_aspect_rejects_extended_object_outside_e5_participant_policy(self):
        data = natal_bundle()
        data["facts"]["objects"].append(
            {"fact_id": "fact:desc", "object_type": "angle", "object_id": "Descendant"}
        )
        data["facts"]["aspects"][0]["right_ref"] = "fact:desc"
        codes = {e["code"] for e in validate_bundle(data)}
        self.assertIn("NATAL_ASPECT_PARTICIPANT_NOT_ADMITTED", codes)

    def test_user_supplied_natal_aspect_may_omit_policy_ids_for_backward_compatibility(self):
        data = natal_bundle()
        aspect = data["facts"]["aspects"][0]
        self.assertNotIn("participant_policy_id", aspect)
        self.assertNotIn("aspect_policy_id", aspect)
        self.assertNotIn("orb_policy_id", aspect)
        self.assertEqual([], validate_bundle(data))

    def test_user_supplied_wrong_policy_id_is_rejected_when_present(self):
        data = natal_bundle()
        data["facts"]["aspects"][0]["participant_policy_id"] = "aspect-participants-core-plus-angles-v1"
        codes = {e["code"] for e in validate_bundle(data)}
        self.assertIn("NATAL_ASPECT_POLICY_PROVENANCE_INVALID", codes)

    def test_approved_provider_natal_aspect_requires_row_policy_ids_and_provider_policy_block(self):
        data = natal_bundle()
        data["fact_source"] = "approved_provider"
        data["calculation_verification"] = "verified_provider"
        codes = {e["code"] for e in validate_bundle(data)}
        self.assertIn("NATAL_ASPECT_POLICY_PROVENANCE_INVALID", codes)
        self.assertIn("NATAL_ASPECT_PROVIDER_POLICY_REQUIRED", codes)

    def test_approved_provider_policy_block_cannot_spoof_extended_participants(self):
        data = natal_bundle()
        data["fact_source"] = "approved_provider"
        data["calculation_verification"] = "verified_provider"
        data["facts"]["aspects"][0].update(
            {
                "participant_policy_id": "aspect-participants-core-bodies-v1",
                "aspect_policy_id": "major-aspects-v1",
                "orb_policy_id": "major-aspect-orbs-v1",
            }
        )
        data["provider"] = {
            "aspect_policies": {
                "participant_policy_id": "aspect-participants-core-bodies-v1",
                "participant_object_ids": [
                    "Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter",
                    "Saturn", "Uranus", "Neptune", "Pluto", "NorthNode", "Descendant",
                ],
                "aspect_policy_id": "major-aspects-v1",
                "aspect_types": ["conjunction", "opposition", "trine", "square", "sextile"],
                "orb_policy_id": "major-aspect-orbs-v1",
                "max_orb_degrees": {
                    "conjunction": 8,
                    "opposition": 8,
                    "trine": 7,
                    "square": 7,
                    "sextile": 5,
                },
                "extended_points_or_angles": "not_admitted",
            }
        }
        codes = {e["code"] for e in validate_bundle(data)}
        self.assertIn("NATAL_ASPECT_PROVIDER_POLICY_MISMATCH", codes)

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
