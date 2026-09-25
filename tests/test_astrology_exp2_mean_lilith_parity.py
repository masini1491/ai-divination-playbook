from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "references" / "astrology" / "astrology_exp2_mean_lilith_iers2003_parity.json"
REPORT = ROOT / "references" / "astrology" / "ASTROLOGY_EXP2_MEAN_LILITH_PARITY.md"
MODULE = ROOT / "references" / "astrology" / "mean_lilith_iers2003_research.py"


def load_research_module():
    spec = importlib.util.spec_from_file_location("mean_lilith_iers2003_research", MODULE)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Mean Lilith research module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AstrologyExp2MeanLilithParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads(RESULT.read_text(encoding="utf-8"))
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.module = load_research_module()

    def test_identity_is_explicit_and_reference_only(self) -> None:
        candidate = self.data["candidate"]
        self.assertEqual("black_moon_lilith_mean_iers2003_v1", candidate["fact_id"])
        self.assertFalse(candidate["bare_lilith_alias"])
        self.assertEqual("REFERENCE_ONLY", candidate["implementation_status"])
        self.assertEqual("NOT_GRANTED", self.data["production_admission"])
        self.assertEqual("REFERENCE_ONLY_RESEARCH_EVIDENCE", self.data["authority"])

    def test_prospective_parity_gates_pass_without_swiss_redefinition(self) -> None:
        metrics = self.data["metrics"]
        gates = self.data["thresholds_frozen_before_first_execution"]
        self.assertLessEqual(
            metrics["erfa_same_definition_max_arcsec"],
            gates["erfa_same_definition_max_arcsec"],
        )
        self.assertLessEqual(
            metrics["xalen_meeus_compatibility_max_arcsec"],
            gates["xalen_meeus_compatibility_max_arcsec"],
        )
        self.assertTrue(self.data["pass"]["overall_research_parity"])
        self.assertEqual("REPORT_ONLY_DIFFERENT_DEFINITION", self.data["swiss_gate"])
        self.assertGreater(metrics["swiss_compatibility_min_arcsec"], 1.0)

    def test_validation_window_is_not_misrepresented_as_production_admission(self) -> None:
        window = self.data["candidate_validation_window"]
        self.assertEqual(-2.0, window["t_centuries_min"])
        self.assertEqual(2.0, window["t_centuries_max"])
        self.assertEqual(
            "RESEARCH_WINDOW_ONLY_NOT_PRODUCTION_DATE_ADMISSION",
            window["admission_semantics"],
        )
        self.assertIn("research validation window", self.report)
        self.assertIn("not a production-admitted date window", self.report)

    def test_research_implementation_has_stable_j2000_identity(self) -> None:
        self.assertEqual(
            "black_moon_lilith_mean_iers2003_v1",
            self.module.FACT_ID,
        )
        self.assertAlmostEqual(
            self.data["notable_rows"]["xalen_worst"]["candidate_deg"],
            self.module.mean_lilith_iers2003_deg(2.0),
            places=12,
        )

    def test_temporary_probe_was_not_merged(self) -> None:
        self.assertFalse(self.data["experiment"]["temporary_pr_merged"])
        self.assertEqual("RESEARCH_PARITY_PASS", self.data["experiment"]["result"])
        self.assertEqual("NONE", self.data["conclusion"]["production_consequence"])


if __name__ == "__main__":
    unittest.main()
