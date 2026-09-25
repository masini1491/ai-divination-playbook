from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

import astronomy


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "references" / "astrology" / "astrology_exp4_special_points_geometry.json"
REPORT = ROOT / "references" / "astrology" / "ASTROLOGY_EXP4_SPECIAL_POINTS_GEOMETRY.md"
MODULE = ROOT / "references" / "astrology" / "special_points_geometry_research.py"


def load_research_module():
    spec = importlib.util.spec_from_file_location("special_points_geometry_research", MODULE)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load special-point research module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AstrologyExp4SpecialPointsGeometryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads(RESULT.read_text(encoding="utf-8"))
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.module = load_research_module()

    def test_identities_are_distinct_and_reference_only(self) -> None:
        candidates = self.data["candidates"]
        self.assertEqual("vertex_prime_vertical_ecliptic_v0", candidates["vertex"]["fact_id"])
        self.assertEqual(
            "equatorial_ascendant_ra_plus_90_v0",
            candidates["equatorial_ascendant"]["fact_id"],
        )
        self.assertNotEqual(candidates["vertex"]["fact_id"], candidates["equatorial_ascendant"]["fact_id"])
        self.assertEqual("NOT_GRANTED", self.data["production_admission"])
        self.assertEqual("NOT_GRANTED", self.data["semantic_interpretation_admission"])

    def test_frozen_research_gates_pass(self) -> None:
        metrics = self.data["metrics"]
        gates = self.data["thresholds_frozen_before_first_execution"]
        self.assertLessEqual(metrics["synthetic_geometry_plane_abs_max"], gates["geometry_plane_abs_max"])
        self.assertLessEqual(metrics["synthetic_equasc_ra_residual_max_deg"], gates["equasc_ra_residual_max_deg"])
        self.assertLessEqual(metrics["same_input_swiss_max_deg"], gates["same_input_swiss_max_deg"])
        self.assertLessEqual(metrics["project_input_swiss_max_deg"], gates["project_input_swiss_max_deg"])
        self.assertTrue(self.data["pass"]["overall_research_geometry"])

    def test_synthetic_geometry_replays(self) -> None:
        for row in self.data["fixtures"]["synthetic"]:
            residuals = self.module.geometry_residuals(**row)
            self.assertLessEqual(residuals["vertex_prime_vertical_plane_abs"], 1.0e-12)
            self.assertLessEqual(residuals["vertex_ecliptic_plane_abs"], 1.0e-12)
            self.assertLessEqual(residuals["equasc_ra_target_residual_deg"], 1.0e-10)

    def test_greenwich_project_result_replays(self) -> None:
        t = astronomy.Time.Make(2026, 3, 20, 12, 0, 0.0)
        actual = self.module.special_points_from_project_inputs(
            time=t,
            longitude_east_deg=0.0,
            latitude_deg=51.4779,
        )
        expected = self.data["representative_results"]["greenwich"]
        self.assertAlmostEqual(expected["project_armc_deg"], actual["armc_deg"], places=11)
        self.assertAlmostEqual(expected["project_obliquity_deg"], actual["obliquity_deg"], places=11)
        self.assertAlmostEqual(expected["project_vertex_deg"], actual["vertex_deg"], places=11)
        self.assertAlmostEqual(
            expected["project_equatorial_ascendant_deg"],
            actual["equatorial_ascendant_deg"],
            places=11,
        )

    def test_vertex_fails_closed_at_geographic_poles(self) -> None:
        for latitude in (-90.0, 90.0):
            with self.assertRaises(self.module.ResearchGeometryError):
                self.module.vertex_deg(
                    armc_deg=0.0,
                    obliquity_deg=23.4,
                    latitude_deg=latitude,
                )

    def test_east_point_is_compatibility_only(self) -> None:
        alias = self.data["east_point_alias"]
        self.assertFalse(alias["canonical_math_identity"])
        self.assertEqual("NOT_GRANTED", alias["production_alias_admission"])
        self.assertIn("named East Point compatibility evidence", self.report)
        self.assertIn("production alias admission", self.report)

    def test_three_layer_admission_boundary_is_explicit(self) -> None:
        self.assertIn("research geometry PASS", self.report)
        self.assertIn("production calculation admission", self.report)
        self.assertIn("semantic interpretation admission", self.report)


if __name__ == "__main__":
    unittest.main()
