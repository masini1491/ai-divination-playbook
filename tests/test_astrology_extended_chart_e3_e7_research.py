from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASTROLOGY_REFS = ROOT / "references" / "astrology"
MANIFEST_PATH = ASTROLOGY_REFS / "extended_chart_e3_e7_policy_manifest.json"

SIGNS = {
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
}


class AstrologyExtendedChartE3E7ResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    def test_manifest_remains_reference_only_and_unadmitted(self):
        data = self.data
        self.assertEqual(
            "astrology_extended_chart_e3_e7_policy_manifest", data["schema_name"]
        )
        self.assertEqual("0.2.0", data["schema_version"])
        self.assertEqual("REFERENCE_ONLY", data["authority"])
        self.assertEqual("NOT_GRANTED", data["production_admission"])
        self.assertEqual(
            "40d4938bb3f265d332608312463b550fb8b8aa13",
            data["playbook_baseline"],
        )

    def test_no_research_phase_silently_selects_a_production_default(self):
        data = self.data
        self.assertEqual("NOT_SELECTED", data["e3_lilith"]["production_default"])
        self.assertEqual(
            "NOT_SELECTED",
            data["e4_special_points"]["production_default_alias_policy"],
        )
        self.assertEqual(
            "NOT_SELECTED", data["e5_aspect_participants"]["production_default"]
        )
        self.assertEqual("NOT_SELECTED", data["e6_patterns"]["production_default"])
        self.assertEqual("NOT_SELECTED", data["e7_rulership"]["production_default"])

    def test_lilith_models_are_distinct_and_bare_identity_fails_closed(self):
        e3 = self.data["e3_lilith"]
        models = e3["models"]
        self.assertEqual(3, len(models))
        self.assertEqual(
            {
                "black_moon_lilith_mean": "SE_MEAN_APOG",
                "black_moon_lilith_osculating": "SE_OSCU_APOG",
                "black_moon_lilith_interpolated": "SE_INTP_APOG",
            },
            {row["fact_id"]: row["swiss_constant"] for row in models},
        )
        self.assertEqual("AMBIGUOUS_MODEL", e3["bare_lilith_identity"])
        self.assertEqual(len({row["fact_id"] for row in models}), len(models))
        self.assertEqual(len({row["swiss_constant"] for row in models}), len(models))

    def test_fortune_and_sect_contract_are_explicit_and_fail_closed(self):
        fortune = self.data["e4_special_points"]["fortune"]
        self.assertEqual("fortune-day-night-v1", fortune["policy_id"])
        self.assertEqual(
            "sect-geometric-solar-altitude-v1", fortune["sect_policy_id"]
        )
        self.assertEqual("ASC + Moon - Sun", fortune["diurnal_formula"])
        self.assertEqual("ASC + Sun - Moon", fortune["nocturnal_formula"])
        self.assertEqual("mod_360", fortune["normalize"])
        rule = fortune["sect_rule"]
        self.assertEqual("altitude_deg > 0", rule["diurnal_when"])
        self.assertEqual("altitude_deg < 0", rule["nocturnal_when"])
        self.assertEqual("FAIL_CLOSED_AT_EXACT_ZERO", rule["horizon_boundary"])
        self.assertEqual("FAIL_CLOSED", rule["calculation_failure"])

    def test_swiss_special_point_indices_remain_distinct(self):
        ascmc = self.data["e4_special_points"]["swiss_ascmc"]
        self.assertEqual(
            {
                "ascendant": 0,
                "mc": 1,
                "armc": 2,
                "vertex": 3,
                "equatorial_ascendant": 4,
            },
            ascmc,
        )
        self.assertEqual(len(set(ascmc.values())), len(ascmc))
        alias = self.data["e4_special_points"]["east_point_alias"]
        self.assertEqual("equatorial_ascendant", alias["canonical_candidate"])
        self.assertEqual(
            "COMPATIBILITY_POLICY_REQUIRES_SOURCE_MATCH", alias["status"]
        )

    def test_aspect_participant_classes_do_not_imply_default_admission(self):
        e5 = self.data["e5_aspect_participants"]
        self.assertEqual(
            {
                "planet",
                "lunar_node",
                "angle",
                "asteroid_or_centaur",
                "lunar_apsis",
                "lot",
                "special_point",
            },
            set(e5["classes"]),
        )
        self.assertEqual(3, len(e5["research_policy_ids"]))
        self.assertEqual("NOT_SELECTED", e5["production_default"])

    def test_pattern_templates_form_complete_simple_graphs(self):
        e6 = self.data["e6_patterns"]
        referenced = set(e6["aspect_types_referenced"])
        templates = e6["topology_templates"]
        expected_vertices = {
            "t_square": 3,
            "grand_trine": 3,
            "yod": 3,
            "grand_cross": 4,
            "kite": 4,
            "mystic_rectangle": 4,
            "cradle": 4,
            "grand_sextile": 6,
            "grand_quintile": 5,
        }
        self.assertEqual(set(expected_vertices), set(templates))
        for pattern, template in templates.items():
            vertices = template["vertices"]
            self.assertEqual(expected_vertices[pattern], vertices)
            edge_counts = template["edge_counts"]
            self.assertTrue(set(edge_counts) <= referenced)
            self.assertTrue(all(isinstance(v, int) and v > 0 for v in edge_counts.values()))
            self.assertEqual(vertices * (vertices - 1) // 2, sum(edge_counts.values()))
        self.assertEqual(2, templates["yod"]["edge_counts"]["quincunx"])
        self.assertEqual(3, templates["cradle"]["edge_counts"]["sextile"])
        self.assertEqual(
            {"sextile": 6, "trine": 6, "opposition": 3},
            templates["grand_sextile"]["edge_counts"],
        )
        self.assertEqual(
            {"quintile": 5, "biquintile": 5},
            templates["grand_quintile"]["edge_counts"],
        )
        self.assertEqual("POLICY_GATED", e6["stellium"]["status"])
        self.assertEqual("UNRESOLVED", e6["exact_consumer_orb_policy"])

    def test_rulership_policies_cover_all_signs_and_preserve_known_conflicts(self):
        e7 = self.data["e7_rulership"]
        traditional = e7["policies"]["rulership-traditional-v1"]
        modern = e7["policies"]["rulership-modern-v1"]
        self.assertEqual(SIGNS, set(traditional))
        self.assertEqual(SIGNS, set(modern))
        self.assertEqual("Mars", traditional["Scorpio"])
        self.assertEqual("Pluto", modern["Scorpio"])
        self.assertEqual("Saturn", traditional["Aquarius"])
        self.assertEqual("Uranus", modern["Aquarius"])
        self.assertEqual("Jupiter", traditional["Pisces"])
        self.assertEqual("Neptune", modern["Pisces"])
        self.assertEqual("PROHIBITED", e7["silent_blending"])

    def test_research_docs_keep_production_boundary_explicit(self):
        docs = [
            "EXTENDED_CHART_E3_LILITH_RESEARCH.md",
            "EXTENDED_CHART_E4_SPECIAL_POINTS_RESEARCH.md",
            "EXTENDED_CHART_E5_ASPECT_PARTICIPANT_POLICY.md",
            "EXTENDED_CHART_E6_PATTERN_TOPOLOGY_RESEARCH.md",
            "EXTENDED_CHART_E7_RULERSHIP_POLICY.md",
        ]
        for name in docs:
            text = (ASTROLOGY_REFS / name).read_text(encoding="utf-8")
            self.assertIn("REFERENCE-ONLY", text, name)
            self.assertIn("NOT PRODUCTION-ADMITTED", text, name)


if __name__ == "__main__":
    unittest.main()
