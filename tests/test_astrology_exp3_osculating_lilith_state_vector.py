from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from unittest.mock import patch
import unittest

import astronomy


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "references" / "astrology" / "astrology_exp3_osculating_lilith_state_vector.json"
REPORT = ROOT / "references" / "astrology" / "ASTROLOGY_EXP3_OSCULATING_LILITH_STATE_VECTOR.md"
MODULE = ROOT / "references" / "astrology" / "osculating_lilith_state_research.py"


def load_research_module():
    spec = importlib.util.spec_from_file_location("osculating_lilith_state_research", MODULE)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Osculating Lilith research module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AstrologyExp3OsculatingLilithStateVectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads(RESULT.read_text(encoding="utf-8"))
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.module = load_research_module()

    def test_identity_is_explicit_and_reference_only(self) -> None:
        candidate = self.data["candidate"]
        self.assertEqual("black_moon_lilith_osculating_lrl_aengine_v0", candidate["fact_id"])
        self.assertFalse(candidate["bare_lilith_alias"])
        self.assertEqual("REFERENCE_ONLY", candidate["implementation_status"])
        self.assertFalse(candidate["production_state_vector_fact_admitted"])
        self.assertEqual("NOT_GRANTED", self.data["production_admission"])
        self.assertEqual("NOT_GRANTED", self.data["semantic_interpretation_admission"])

    def test_frozen_stability_gates_pass(self) -> None:
        metrics = self.data["metrics"]
        gates = self.data["thresholds_frozen_before_first_execution"]
        self.assertLessEqual(metrics["state_vs_fd_0p05_max_deg"], gates["state_vs_fd_0p05_max_deg"])
        self.assertLessEqual(metrics["fd_step_spread_max_deg"], gates["fd_step_spread_max_deg"])
        self.assertTrue(self.data["pass"]["overall_research_stability"])

    def test_model_sensitivity_is_material_and_swiss_is_report_only(self) -> None:
        self.assertGreater(self.data["metrics"]["earth_only_mu_sensitivity_max_deg"], 10.0)
        self.assertEqual("REPORT_ONLY_MODEL_SENSITIVE_COMPATIBILITY", self.data["swiss_gate"])
        self.assertIn("does not establish a universal same-definition identity", self.report)

    def test_research_window_is_not_production_date_admission(self) -> None:
        window = self.data["candidate_validation_window"]
        self.assertEqual(17, window["fixture_count"])
        self.assertEqual(
            "RESEARCH_WINDOW_ONLY_NOT_PRODUCTION_DATE_ADMISSION",
            window["admission_semantics"],
        )

    def test_j2000_replays_saved_candidate(self) -> None:
        time = astronomy.Time.FromTerrestrialTime(0.0)
        candidate, eccentricity = self.module.osculating_lilith_from_state(time)
        row = self.data["notable_rows"]["j2000"]
        self.assertAlmostEqual(row["candidate_deg"], candidate, places=11)
        self.assertAlmostEqual(row["eccentricity_norm"], eccentricity, places=12)

    def test_required_state_input_fails_closed(self) -> None:
        time = astronomy.Time.FromTerrestrialTime(0.0)
        with patch.object(
            self.module.astronomy,
            "GeoMoonState",
            side_effect=RuntimeError("synthetic unavailable"),
        ):
            with self.assertRaisesRegex(self.module.ResearchInputError, "research input unavailable"):
                self.module.osculating_lilith_from_state(time)
        with self.assertRaises(self.module.ResearchInputError):
            self.module.osculating_lilith_from_position_finite_difference(time, dt_days=0.0)

    def test_three_layer_admission_boundary_is_explicit(self) -> None:
        self.assertIn("research stability PASS", self.report)
        self.assertIn("production calculation admission", self.report)
        self.assertIn("semantic interpretation admission", self.report)


if __name__ == "__main__":
    unittest.main()
