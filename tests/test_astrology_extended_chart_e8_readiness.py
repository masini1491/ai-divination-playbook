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
            "3346b59055a300aa8998884ccc376017483836af",
            data["production_baseline"],
        )
        self.assertEqual("PRODUCTION_ADMITTED", data["current_state_reconciliation"]["e1_status"])
        self.assertEqual("PRODUCTION_ADMITTED", data["current_state_reconciliation"]["e4_status"])
        derived = data["current_state_reconciliation"]["derived_fact_interpretation_boundary"]
        self.assertEqual("BOUNDED_CLAIMS_ADMITTED_BY_PR_152", derived["descendant"])
        self.assertEqual("BOUNDED_CLAIMS_ADMITTED_BY_PR_152", derived["imum_coeli"])
        self.assertEqual("FACT_ONLY", derived["south_node"])
        self.assertEqual("FACT_ONLY", derived["part_of_fortune"])

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

    def test_post_156_research_overlay_preserves_historical_rows(self):
        overlay = self.data["current_research_overlay"]
        self.assertEqual("REFERENCE_ONLY_RESEARCH_ELIGIBILITY", overlay["authority"])
        self.assertFalse(overlay["supersedes_historical_candidate_readiness"])
        self.assertTrue(overlay["historical_candidate_rows_preserved"])
        self.assertFalse(overlay["production_mutation_authorized"])
        self.assertIsNone(overlay["production_selection"])

        rows = {row["id"]: row for row in self.data["candidates"]}
        for object_id, item in overlay["candidates"].items():
            self.assertEqual(rows[object_id]["readiness"], item["historical_readiness"])
            self.assertEqual("NOT_ADMITTED", item["production_status"])

    def test_post_156_research_overlay_routes_object_families_without_admission(self):
        overlay = self.data["current_research_overlay"]["candidates"]
        for object_id in ("chiron", "ceres", "pallas", "juno", "vesta"):
            self.assertEqual(
                "ELIGIBLE_FOR_BUNDLED_EPHEMERIS_RESEARCH",
                overlay[object_id]["current_research_eligibility"],
            )
            self.assertEqual(["BUNDLED_EPHEMERIS"], overlay[object_id]["eligible_lanes"])

        for object_id in ("black_moon_lilith_variants", "vertex", "equatorial_ascendant"):
            self.assertEqual(
                "ELIGIBLE_FOR_LOCAL_ANALYTICAL_RESEARCH",
                overlay[object_id]["current_research_eligibility"],
            )
            self.assertEqual(["LOCAL_ANALYTICAL"], overlay[object_id]["eligible_lanes"])

        self.assertIn(
            "Interpolated remains a separate compatibility definition",
            overlay["black_moon_lilith_variants"]["definition_boundary"],
        )

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
        d1 = decisions["D1_extended_ephemeris_strategy"]
        self.assertEqual(
            [
                "CURRENT_CORE_ONLY",
                "LOCAL_ANALYTICAL",
                "BUNDLED_EPHEMERIS",
                "EXTERNAL_RUNTIME",
                "SWISS_AGPL",
                "SWISS_PROFESSIONAL",
            ],
            d1["options"],
        )
        self.assertEqual(
            "RESEARCH_REFRAMED_NO_PRODUCTION_SELECTION",
            d1["status"],
        )
        self.assertEqual(
            "chatgpt_only_production_must_not_require_live_third_party_api",
            d1["runtime_constraint"],
        )
        self.assertEqual(
            ["LOCAL_ANALYTICAL", "BUNDLED_EPHEMERIS"],
            d1["next_research_lanes"],
        )
        self.assertEqual(
            "references/astrology/CHATGPT_ONLY_EXTENDED_EPHEMERIS_FEASIBILITY.md",
            d1["research_evidence"],
        )
        self.assertIsNone(d1["production_selection"])
        self.assertEqual(
            ["EXPLICIT_SELECTOR_ONLY", "NAMED_COMPATIBILITY_PROFILE"],
            decisions["D2_policy_activation_style"]["options"],
        )
        self.assertEqual(
            "SELECTED_FOR_CURRENT_STACK_LANE",
            decisions["D2_policy_activation_style"]["status"],
        )
        self.assertEqual(
            "EXPLICIT_SELECTOR_ONLY",
            decisions["D2_policy_activation_style"]["selected"],
        )

    def test_chatgpt_only_ephemeris_research_stays_reference_only(self):
        path = ROOT / "references" / "astrology" / "CHATGPT_ONLY_EXTENDED_EPHEMERIS_FEASIBILITY.md"
        text = path.read_text(encoding="utf-8")
        self.assertIn("REFERENCE-ONLY", text)
        self.assertIn("NO PRODUCTION MUTATION AUTHORIZED", text)
        self.assertIn("TheDaniel166/moira@", text)
        self.assertIn("vedika-io/xalen-ephemeris@", text)
        self.assertIn("skyfielders/python-skyfield@", text)
        self.assertIn("brandon-rhodes/python-jplephem@", text)
        self.assertIn("Live JPL API is NOT suitable as a mandatory ChatGPT-only runtime", text)
        self.assertIn("Production admission remains unchanged by this report.", text)

    def test_current_stack_admissions_are_reconciled_without_rewriting_research_class(self):
        rows = {row["id"]: row for row in self.data["candidates"]}
        for object_id in ("mean_south_node", "descendant", "imum_coeli", "part_of_fortune"):
            self.assertEqual("ADMITTED", rows[object_id]["production_status"])
        for object_id in ("rulership_traditional", "rulership_modern"):
            self.assertEqual("ADMITTED", rows[object_id]["production_status"])
        self.assertEqual(
            "ADMITTED_CURRENT_CORE_SCOPE",
            rows["aspect_participant_policy"]["production_status"],
        )
        self.assertEqual(
            "ADMITTED_CURRENT_MAJOR_ASPECT_SCOPE",
            rows["pattern_topology"]["production_status"],
        )
        current = self.data["current_state_reconciliation"]
        self.assertEqual([], current["remaining_current_stack_order"])
        self.assertTrue(current["current_stack_closure"])
        self.assertEqual(
            "PRODUCTION_ADMITTED_EXPLICIT_SELECTOR_ONLY",
            current["e7_status"],
        )
        self.assertEqual(
            "PRODUCTION_ADMITTED_CURRENT_CORE_SCOPE_RUNTIME_HARDENED",
            current["e5_status"],
        )
        self.assertEqual(
            "PRODUCTION_ADMITTED_CURRENT_MAJOR_ASPECT_SCOPE_RUNTIME_HARDENED",
            current["e6_status"],
        )


if __name__ == "__main__":
    unittest.main()
