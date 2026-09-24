from __future__ import annotations

import json
import unittest
from pathlib import Path

from tools.astrology_provider import build_natal_bundle, build_unknown_time_natal_bundle
from tools.astrology_rulership_projection import (
    RulershipProjectionError,
    build_rulership_projection,
)

ROOT = Path(__file__).resolve().parents[1]


class AstrologyRulershipProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = build_natal_bundle(
            local_datetime="1990-06-15T12:00:00",
            timezone_name="UTC",
            latitude=51.5074,
            longitude=0.0,
            house_system="Whole Sign",
            subject_ref="subject:synthetic-e7",
        )

    def test_explicit_traditional_and_modern_policies_project_all_houses(self):
        traditional = build_rulership_projection(self.bundle, "rulership-traditional-v1")
        modern = build_rulership_projection(self.bundle, "rulership-modern-v1")
        self.assertEqual(12, len(traditional["projections"]))
        self.assertEqual(12, len(modern["projections"]))
        self.assertTrue(traditional["explicit_policy_required"])
        self.assertFalse(traditional["semantic_interpretation_authority"])

        t = {row["sign_on_house"]: row["ruler_object_id"] for row in traditional["projections"]}
        m = {row["sign_on_house"]: row["ruler_object_id"] for row in modern["projections"]}
        self.assertEqual("Mars", t["Scorpio"])
        self.assertEqual("Saturn", t["Aquarius"])
        self.assertEqual("Jupiter", t["Pisces"])
        self.assertEqual("Pluto", m["Scorpio"])
        self.assertEqual("Uranus", m["Aquarius"])
        self.assertEqual("Neptune", m["Pisces"])

    def test_projection_preserves_house_and_ruler_fact_provenance(self):
        result = build_rulership_projection(self.bundle, "rulership-modern-v1")
        for row in result["projections"]:
            self.assertEqual("rulership", row["projection_kind"])
            self.assertEqual("rulership-modern-v1", row["policy_id"])
            self.assertEqual(f"fact:house:{row['house_number']}", row["house_fact_ref"])
            self.assertTrue(row["ruler_fact_ref"].startswith("fact:object:"))
            self.assertIn("ruler_sign", row)
            self.assertIn("ruler_house_number", row)

    def test_no_silent_default_or_unknown_policy(self):
        with self.assertRaisesRegex(RulershipProjectionError, "explicit admitted rulership policy required"):
            build_rulership_projection(self.bundle, "")
        with self.assertRaisesRegex(RulershipProjectionError, "explicit admitted rulership policy required"):
            build_rulership_projection(self.bundle, "rulership-co-ruler-v1")

    def test_unknown_birth_time_fails_closed_without_houses(self):
        unknown = build_unknown_time_natal_bundle(
            local_date="2006-03-14",
            timezone_name="Asia/Taipei",
            subject_ref="subject:synthetic-e7-unknown",
        )
        with self.assertRaisesRegex(RulershipProjectionError, "all 12 admitted house facts"):
            build_rulership_projection(unknown, "rulership-modern-v1")

    def test_machine_admission_is_explicit_selector_only(self):
        manifest = json.loads((ROOT / "ASTROLOGY_PRODUCTION_ADMISSION_V1.json").read_text(encoding="utf-8"))
        policy = manifest["orchestration"]["policy_projections"]["rulership"]
        self.assertEqual("explicit_selector_only", policy["activation"])
        self.assertEqual(
            ["rulership-traditional-v1", "rulership-modern-v1"],
            policy["admitted_policy_ids"],
        )
        self.assertEqual("forbidden", policy["silent_default"])
        self.assertEqual("forbidden", policy["silent_blending"])
        self.assertFalse(policy["semantic_interpretation_authority"])


if __name__ == "__main__":
    unittest.main()
