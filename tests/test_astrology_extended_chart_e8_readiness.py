from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "references" / "astrology" / "extended_chart_e8_admission_readiness.json"


class AstrologyExtendedChartE8ReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads(MATRIX.read_text(encoding="utf-8"))

    def test_readiness_review_cannot_mutate_production_authority(self):
        data = self.data
        self.assertEqual("astrology_extended_chart_e8_admission_readiness", data["schema_name"])
        self.assertEqual("REFERENCE_ONLY", data["authority"])
        self.assertFalse(data["production_mutation_authorized"])
        self.assertEqual(
            "c824e79a92476188b9b4c63d608608e1c01e791d",
            data["production_baseline"],
        )
        self.assertEqual("PRODUCTION_ADMITTED", data["current_state_reconciliation"]["e1_status"])
        self.assertEqual("PRODUCTION_ADMITTED", data["current_state_reconciliation"]["e4_status"])
        self.assertEqual(
            "CLOSED_BY_PR_147",
            data["current_state_reconciliation"]["derived_fact_interpretation_boundary"],
        )

    def test_readiness_classes_are_closed_and_used_consistently(self):
        data = self.data
        allowed = set(data["readiness_classes"])
        self.assertEqual(
            {
                "READY_WITH_CURRENT_STACK",
                "READY_IF_EXPLICIT_POLICY_SELECTED",
                "BLOCKED_ON_PROVIDER_OR_LICENSE",
                "BLOCKED_ON_COMPATIBILITY_DEFINITION",
            },
            allowed,
        )
        candidates = data["candidates"]
        self.assertEqual(len(candidates), len({row["id"] for row in candidates}))
        for row in candidates:
            self.assertIn(row["readiness"], allowed)

    def test_current_stack_lane_contains_only_no_new_provider_candidates(self):
        for row in self.data["candidates"]:
            if row["readiness"] in {
                "READY_WITH_CURRENT_STACK",
                "READY_IF_EXPLICIT_POLICY_SELECTED",
            }:
                self.assertFalse(row["requires_new_external_provider"], row["id"])

    def test_extended_ephemeris_objects_remain_provider_or_license_blocked(self):
        rows = {row["id"]: row for row in self.data["candidates"]}
        for object_id in (
            "chiron",
            "ceres",
            "pallas",
            "juno",
            "vesta",
            "black_moon_lilith_variants",
            "vertex",
            "equatorial_ascendant",
        ):
            self.assertEqual(
                "BLOCKED_ON_PROVIDER_OR_LICENSE", rows[object_id]["readiness"]
            )
            self.assertTrue(rows[object_id]["requires_new_external_provider"])

    def test_compatibility_gaps_are_not_misrepresented_as_calculation_readiness(self):
        rows = {row["id"]: row for row in self.data["candidates"]}
        for object_id in (
            "stellium",
            "tang_qiyang_exact_pattern_compatibility",
            "east_point_alias",
        ):
            self.assertEqual(
                "BLOCKED_ON_COMPATIBILITY_DEFINITION", rows[object_id]["readiness"]
            )

    def test_material_decisions_are_explicit_and_unselected(self):
        decisions = self.data["decisions"]
        self.assertEqual(
            ["MIT_ONLY", "SWISS_AGPL", "SWISS_PROFESSIONAL"],
            decisions["D1_extended_ephemeris_strategy"]["options"],
        )
        self.assertEqual(
            ["EXPLICIT_SELECTOR_ONLY", "NAMED_COMPATIBILITY_PROFILE"],
            decisions["D2_policy_activation_style"]["options"],
        )
        self.assertEqual(
            "USER_DECISION_REQUIRED",
            decisions["D1_extended_ephemeris_strategy"]["status"],
        )
        self.assertNotIn("selected", decisions["D1_extended_ephemeris_strategy"])
        self.assertEqual(
            "SELECTED_FOR_CURRENT_STACK_LANE",
            decisions["D2_policy_activation_style"]["status"],
        )
        self.assertEqual(
            "EXPLICIT_SELECTOR_ONLY",
            decisions["D2_policy_activation_style"]["selected"],
        )

    def test_admitted_e1_e4_candidates_are_marked_without_rewriting_research_class(self):
        rows = {row["id"]: row for row in self.data["candidates"]}
        for object_id in ("mean_south_node", "descendant", "imum_coeli", "part_of_fortune"):
            self.assertEqual("ADMITTED", rows[object_id]["production_status"])
        self.assertEqual(
            [
                "E7_NAMED_RULERSHIP",
                "E5_PARTICIPANT_POLICY_PLUMBING",
                "E6_TOPOLOGY_FOR_ADMITTED_ASPECTS",
            ],
            self.data["current_state_reconciliation"]["remaining_current_stack_order"],
        )


if __name__ == "__main__":
    unittest.main()
