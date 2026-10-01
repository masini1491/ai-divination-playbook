import json
import unittest
from copy import deepcopy
from pathlib import Path

from references.astrology.validate_exact_claim_admission_policy import validate

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "references" / "astrology" / "EXACT_CLAIM_ADMISSION_POLICY_V1.json"
MANIFEST = ROOT / "admissions/astrology/ASTROLOGY_PRODUCTION_ADMISSION_V1.json"
PLANET_SIGN = ROOT / "references" / "astrology" / "planet_sign_composable_semantics_claim_family_registry.json"
HIGH_VALUE = ROOT / "references" / "astrology" / "high_value_planet_aspects_claim_family_registry.json"
SATURN_MOON = ROOT / "references" / "astrology" / "saturn_moon_aspect_claim_family_registry.json"

class AstrologySparseExactClaimPolicyTests(unittest.TestCase):
    def test_canonical_policy_passes_standalone_validator(self):
        policy = self.load(POLICY)
        self.assertEqual([], validate(policy))

    def test_validator_fails_closed_for_illegal_policy_mutation(self):
        policy = deepcopy(self.load(POLICY))
        policy["production_routable"] = True
        policy["anti_cartesian_rules"]["planet_sign_matrix_completion"] = True
        errors = validate(policy)
        self.assertIn("production_routable", errors)
        self.assertIn("anti_cartesian_rules.planet_sign_matrix_completion", errors)

    def load(self, path):
        return json.loads(path.read_text(encoding="utf-8"))

    def test_four_states_are_explicit_and_complete(self):
        policy = self.load(POLICY)
        self.assertEqual(
            {
                "composition_adequate",
                "research_candidate",
                "exact_claim_admitted",
                "unsupported",
            },
            set(policy["states"]),
        )

    def test_policy_rejects_cartesian_and_feedback_driven_expansion(self):
        anti = self.load(POLICY)["anti_cartesian_rules"]
        self.assertTrue(anti)
        self.assertTrue(all(value is False for value in anti.values()))

    def test_planet_sign_case_matches_current_bounded_composition(self):
        policy = self.load(POLICY)
        case = next(x for x in policy["representative_cases"] if x["case_id"] == "planet-sign-bounded-composition")
        manifest = self.load(MANIFEST)
        registry = self.load(PLANET_SIGN)
        fallback = manifest["natal_semantic_policy"]["semantic_composition_fallback"]["planet_sign"]
        self.assertEqual("composition_adequate", case["expected_state"])
        self.assertEqual(registry["record_id"], fallback["baseline_registry_record_id"])
        self.assertEqual(["planet_function", "sign_style"], fallback["required_claim_types"])
        self.assertEqual(
            "use_bounded_composition_when_all_required_primitives_pass",
            fallback["exact_pair_missing_behavior"],
        )

    def test_qualified_aspect_case_is_research_candidate_not_production(self):
        policy = self.load(POLICY)
        case = next(x for x in policy["representative_cases"] if x["case_id"] == "qualified-high-value-aspect")
        manifest = self.load(MANIFEST)
        registry = self.load(HIGH_VALUE)
        self.assertEqual("research_candidate", case["expected_state"])
        self.assertFalse(registry["production_routable"])
        self.assertIn(registry["record_id"], manifest["qualified_only_registries"])
        self.assertNotIn(registry["record_id"], manifest["admitted_research_registries"])

    def test_moon_saturn_case_is_exact_claim_admitted(self):
        policy = self.load(POLICY)
        case = next(x for x in policy["representative_cases"] if x["case_id"] == "admitted-moon-saturn-opposition")
        manifest = self.load(MANIFEST)
        registry = self.load(SATURN_MOON)
        self.assertEqual("exact_claim_admitted", case["expected_state"])
        self.assertIn(registry["record_id"], manifest["admitted_research_registries"])
        claims = {x["claim_id"]: x for x in registry["claims"]}
        self.assertIn("claim:greene-moon-saturn-parent-image", claims)
        self.assertIn("Moon-Saturn opposition", claims["claim:greene-moon-saturn-parent-image"]["applies_to"])

    def test_generic_aspect_case_remains_unsupported(self):
        policy = self.load(POLICY)
        case = next(x for x in policy["representative_cases"] if x["case_id"] == "generic-unadmitted-aspect-semantic")
        aspect = self.load(MANIFEST)["natal_semantic_policy"]["semantic_composition_fallback"]["natal_aspect"]
        self.assertEqual("unsupported", case["expected_state"])
        self.assertFalse(aspect["general_pair_relationship_semantic_admitted"])
        self.assertFalse(aspect["general_aspect_operator_semantic_admitted"])
        self.assertFalse(aspect["bounded_composition_currently_available"])

    def test_research_policy_has_no_production_routing_authority(self):
        policy = self.load(POLICY)
        self.assertEqual("REFERENCE_ONLY_RESEARCH_POLICY", policy["authority"])
        self.assertFalse(policy["production_routable"])
        self.assertEqual("explicit_production_admission", policy["promotion_boundary"][-1])

if __name__ == "__main__":
    unittest.main()
