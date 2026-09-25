from __future__ import annotations

import json
import unittest
from pathlib import Path

from tools.astrology_provider import build_natal_bundle
from tools.astrology_special_pattern_projection import (
    ASPECT_POLICY_ID,
    ORB_POLICY_ID,
    PARTICIPANT_POLICIES,
    PATTERN_POLICY_ID,
    PROJECTION_POLICY_ID,
    STELLIUM_POLICY_ID,
    SpecialPatternProjectionError,
    _aspect,
    build_special_pattern_projection,
)

ROOT = Path(__file__).resolve().parents[1]
CORE = "aspect-participants-core-bodies-v1"


def base_bundle(certainty: str = "exact") -> dict:
    return build_natal_bundle(
        local_datetime="1990-06-15T12:00:00",
        timezone_name="UTC",
        latitude=51.5074,
        longitude=0.0,
        house_system="Whole Sign",
        subject_ref="subject:synthetic-p1-120",
        birth_time_certainty=certainty,
    )


def set_longitudes(bundle: dict, mapping: dict[str, float]) -> None:
    for row in bundle["facts"]["objects"]:
        object_id = row.get("object_id")
        if object_id in mapping:
            row["longitude_deg"] = mapping[object_id]


def project(bundle: dict, participant_policy_id: str = CORE) -> dict:
    return build_special_pattern_projection(
        bundle,
        participant_policy_id=participant_policy_id,
        aspect_policy_id=ASPECT_POLICY_ID,
        orb_policy_id=ORB_POLICY_ID,
        pattern_policy_id=PATTERN_POLICY_ID,
        stellium_policy_id=STELLIUM_POLICY_ID,
        pattern_projection_policy_id=PROJECTION_POLICY_ID,
    )


class AstrologySpecialPatternProjectionTests(unittest.TestCase):
    def test_yod_is_detected_from_explicit_sextile_and_quincunx_policy(self):
        bundle = base_bundle()
        set_longitudes(bundle, {
            "Sun": 0.0, "Moon": 60.0, "Mars": 210.0,
            "Mercury": 95.0, "Venus": 125.0, "Jupiter": 245.0,
            "Saturn": 275.0, "Uranus": 305.0, "Neptune": 335.0,
            "Pluto": 35.0, "NorthNode": 170.0,
        })
        rows = [row for row in project(bundle)["patterns"] if row["pattern_type"] == "Yod"]
        self.assertTrue(rows)
        target = next(row for row in rows if {"Sun", "Moon", "Mars"}.issubset(row["participant_object_ids"]))
        self.assertEqual(3, len(target["supporting_aspect_ids"]))

    def test_grand_quintile_is_detected_from_five_quintiles_and_five_biquintiles(self):
        bundle = base_bundle()
        set_longitudes(bundle, {
            "Sun": 0.0, "Moon": 72.0, "Mercury": 144.0, "Venus": 216.0, "Mars": 288.0,
            "Jupiter": 25.0, "Saturn": 115.0, "Uranus": 205.0, "Neptune": 250.0,
            "Pluto": 330.0, "NorthNode": 175.0,
        })
        rows = [row for row in project(bundle)["patterns"] if row["pattern_type"] == "Grand Quintile"]
        self.assertTrue(rows)
        target = next(row for row in rows if {"Sun", "Moon", "Mercury", "Venus", "Mars"}.issubset(row["participant_object_ids"]))
        self.assertEqual(10, len(target["supporting_aspect_ids"]))

    def test_stellium_requires_three_planets_same_sign_and_span_at_most_ten_degrees(self):
        bundle = base_bundle()
        set_longitudes(bundle, {
            "Sun": 5.0, "Moon": 8.0, "Mercury": 12.0,
            "Venus": 50.0, "Mars": 80.0, "Jupiter": 110.0, "Saturn": 140.0,
            "Uranus": 170.0, "Neptune": 200.0, "Pluto": 230.0, "NorthNode": 260.0,
        })
        rows = [row for row in project(bundle)["patterns"] if row["pattern_type"] == "Stellium"]
        self.assertEqual([["Mercury", "Moon", "Sun"]], [row["participant_object_ids"] for row in rows])

    def test_stellium_does_not_cross_sign_boundary_even_when_span_is_small(self):
        bundle = base_bundle()
        set_longitudes(bundle, {
            "Sun": 28.0, "Moon": 29.0, "Mercury": 31.0,
            "Venus": 50.0, "Mars": 80.0, "Jupiter": 110.0, "Saturn": 140.0,
            "Uranus": 170.0, "Neptune": 200.0, "Pluto": 230.0, "NorthNode": 260.0,
        })
        rows = [row for row in project(bundle)["patterns"] if row["pattern_type"] == "Stellium"]
        self.assertFalse(any({"Sun", "Moon", "Mercury"}.issubset(row["participant_object_ids"]) for row in rows))

    def test_minor_orb_policy_is_bounded(self):
        self.assertEqual(("quincunx", 3.0), _aspect(0.0, 153.0))
        self.assertIsNone(_aspect(0.0, 153.01))
        self.assertEqual(("quintile", 2.0), _aspect(0.0, 74.0))
        self.assertIsNone(_aspect(0.0, 74.01))

    def test_extended_exact_time_policy_remains_fail_closed(self):
        bundle = base_bundle("approximate")
        with self.assertRaisesRegex(SpecialPatternProjectionError, "requires exact birth time"):
            project(bundle, "aspect-participants-core-plus-angles-v1")

    def test_policy_ids_are_explicit_and_semantics_remain_closed(self):
        bundle = base_bundle()
        with self.assertRaisesRegex(SpecialPatternProjectionError, "aspect policy"):
            build_special_pattern_projection(
                bundle, participant_policy_id=CORE, aspect_policy_id="pattern-aspects-v999",
                orb_policy_id=ORB_POLICY_ID, pattern_policy_id=PATTERN_POLICY_ID,
                stellium_policy_id=STELLIUM_POLICY_ID, pattern_projection_policy_id=PROJECTION_POLICY_ID,
            )
        result = project(bundle)
        self.assertFalse(result["semantic_interpretation_authority"])
        self.assertFalse(result["exact_consumer_compatibility_claimed"])

    def test_machine_admission_pins_every_special_policy(self):
        manifest = json.loads((ROOT / "ASTROLOGY_PRODUCTION_ADMISSION_V1.json").read_text(encoding="utf-8"))
        policy = manifest["orchestration"]["policy_projections"]["special_patterns"]
        self.assertEqual(ASPECT_POLICY_ID, policy["aspect_policy_id"])
        self.assertEqual(ORB_POLICY_ID, policy["orb_policy_id"])
        self.assertEqual(PATTERN_POLICY_ID, policy["pattern_policy_id"])
        self.assertEqual(STELLIUM_POLICY_ID, policy["stellium_policy"]["policy_id"])
        self.assertEqual(3, policy["stellium_policy"]["minimum_count"])
        self.assertEqual(10.0, policy["stellium_policy"]["maximum_span_deg"])
        self.assertEqual("same_zodiac_sign_required", policy["stellium_policy"]["sign_boundary_policy"])
        self.assertEqual(set(PARTICIPANT_POLICIES), set(policy["admitted_participant_policy_ids"]))
        self.assertFalse(policy["semantic_interpretation_authority"])
        self.assertFalse(policy["exact_consumer_compatibility_claimed"])


if __name__ == "__main__":
    unittest.main()
