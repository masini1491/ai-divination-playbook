from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "references" / "astrology" / "astrology_exp1_sampled_ephemeris_feasibility.json"
REPORT = ROOT / "references" / "astrology" / "ASTROLOGY_EXP1_SAMPLED_EPHEMERIS_FEASIBILITY.md"


class AstrologyExp1SampledEphemerisFeasibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads(RESULT.read_text(encoding="utf-8"))
        cls.report = REPORT.read_text(encoding="utf-8")

    def test_result_is_reference_only_and_not_admitted(self) -> None:
        self.assertEqual("REFERENCE_ONLY_RESEARCH_EVIDENCE", self.data["authority"])
        self.assertEqual("NOT_GRANTED", self.data["production_admission"])
        self.assertEqual("NO_PASSING_VARIANT", self.data["experiment"]["result"])
        self.assertFalse(self.data["experiment"]["temporary_pr_merged"])
        self.assertIsNone(self.data["selected_coarsest_passing_spacing_days"])

    def test_frozen_thresholds_and_three_variants_are_preserved(self) -> None:
        self.assertEqual(
            {
                "longitude_p95_arcsec_max": 10.0,
                "longitude_max_arcsec_max": 30.0,
                "speed_max_deg_per_day": 0.001,
                "binary_payload_bytes_max": 1048576,
                "single_query_raw_payload_bytes_max": 64,
            },
            self.data["thresholds_frozen_before_first_execution"],
        )
        self.assertEqual({"10", "20", "40"}, set(self.data["variants"]))
        self.assertTrue(all(not row["feasibility_pass"] for row in self.data["variants"].values()))

    def test_closest_10_day_candidate_is_rejected_on_speed_without_posthoc_widening(self) -> None:
        row = self.data["variants"]["10"]
        gates = self.data["thresholds_frozen_before_first_execution"]
        self.assertLessEqual(row["binary_float64_payload_bytes"], gates["binary_payload_bytes_max"])
        self.assertLessEqual(row["single_query_raw_payload_bytes"], gates["single_query_raw_payload_bytes_max"])
        self.assertLessEqual(row["longitude_p95_arcsec"], gates["longitude_p95_arcsec_max"])
        self.assertLessEqual(row["longitude_max_arcsec"], gates["longitude_max_arcsec_max"])
        self.assertGreater(row["speed_max_deg_per_day"], gates["speed_max_deg_per_day"])
        self.assertEqual(["speed_max_deg_per_day"], row["failed_gates"])

    def test_network_and_production_boundaries_are_explicit(self) -> None:
        self.assertFalse(self.data["source_authority"]["ordinary_runtime_network_required"])
        self.assertEqual("NONE", self.data["conclusion"]["production_consequence"])
        self.assertIn("No threshold was widened after the result", self.report)
        self.assertIn("ordinary ChatGPT Astrology runtime", self.report)
        self.assertIn("no new network dependency", self.report)


if __name__ == "__main__":
    unittest.main()
