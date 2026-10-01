from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_ROOT = ROOT / "schemas" / "astrology"
REQUEST_SCHEMA = SCHEMA_ROOT / "ASTROLOGY_TYPED_EVIDENCE_SELECTION_REQUEST_V1.schema.json"
SELECTION_SCHEMA = SCHEMA_ROOT / "ASTROLOGY_TYPED_EVIDENCE_SELECTION_V1.schema.json"
MANIFEST = ROOT / "admissions/astrology/ASTROLOGY_PRODUCTION_ADMISSION_V1.json"
INDEX = ROOT / "PLAYBOOK_INDEX.json"
RESEARCH_QUERY_CONTRACT = ROOT / "references" / "astrology" / "QUERY_RESOLUTION_ROUTING_CONTRACT_DRAFT.md"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class AstrologyEvidenceSelectorContractTests(unittest.TestCase):
    def test_request_schema_is_closed_world_typed_contract(self):
        schema = load(REQUEST_SCHEMA)
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(
            "astrology_typed_evidence_selection_request",
            schema["properties"]["schema_name"]["const"],
        )
        self.assertEqual("1.0.0", schema["properties"]["schema_version"]["const"])
        self.assertIn("fact_selectors", schema["required"])
        self.assertIn("claim_selectors", schema["required"])
        self.assertNotIn("fact_refs", schema["properties"])
        self.assertNotIn("claim_id", schema["properties"])
        self.assertEqual(
            ["selector_shape", "object_core", "sign_style", "object_sign_pair", "aspect_pair", "north_node_core", "north_node_sign_style"],
            schema["$defs"]["claim_selector"]["properties"]["applicability_scope"]["enum"],
        )

    def test_selection_schema_declares_narrow_authority(self):
        schema = load(SELECTION_SCHEMA)
        self.assertFalse(schema["additionalProperties"])
        selector = schema["properties"]["selector"]["properties"]
        self.assertEqual("deterministic_evidence_selection_only", selector["authority"]["const"])
        self.assertFalse(selector["natural_language_understanding_authority"]["const"])
        self.assertFalse(selector["semantic_meaning_authority"]["const"])
        self.assertFalse(selector["source_admission_authority"]["const"])
        self.assertFalse(selector["final_prose_authority"]["const"])

    def test_manifest_admits_selector_without_promoting_research_query_resolution(self):
        manifest = load(MANIFEST)
        selector = manifest["orchestration"]["typed_evidence_selection"]
        self.assertEqual("astrology-typed-evidence-selector-v1", selector["selector_id"])
        self.assertEqual("deterministic_evidence_selection_only", selector["authority"])
        self.assertTrue(selector["requires_explicit_typed_selectors"])
        self.assertEqual("fail_closed", selector["ambiguity_policy"])
        self.assertFalse(selector["free_text_query_resolution"])
        self.assertFalse(selector["natural_language_understanding_authority"])
        self.assertFalse(selector["semantic_meaning_authority"])
        self.assertFalse(selector["source_admission_authority"])
        self.assertFalse(selector["final_prose_authority"])
        self.assertFalse(selector["research_routing_contract_promoted"])
        self.assertIn("planet-sign-composable-semantics-research-v1", manifest["admitted_research_registries"])
        self.assertIn("north-node-sign-semantics-research-v1", manifest["admitted_research_registries"])
        self.assertEqual(
            "compose_admitted_planet_function_plus_sign_style_claims",
            manifest["natal_semantic_policy"]["planet_sign_interpretation"],
        )
        self.assertEqual(
            "compose_admitted_north_node_function_plus_sign_style_claims",
            manifest["natal_semantic_policy"]["north_node_sign_interpretation"],
        )
        self.assertEqual("mean", manifest["natal_provider"]["north_node_definition"])
        self.assertEqual("mean", manifest["natal_semantic_policy"]["north_node_definition_required"])
        self.assertEqual(
            "composable-symbolic-modern-v1",
            manifest["natal_semantic_policy"]["semantic_profile_required_for_north_node_sign_registry"],
        )
        derived = manifest["natal_semantic_policy"]["derived_fact_interpretation"]
        self.assertEqual(
            ["SouthNode", "Descendant", "ImumCoeli", "PartOfFortune"],
            derived["fact_only_object_ids"],
        )
        self.assertEqual(
            "forbidden_unless_explicitly_admitted",
            derived["claim_binding"],
        )
        self.assertEqual(
            {"Descendant", "ImumCoeli", "PartOfFortune"},
            set(derived["admitted_claim_bindings"]),
        )
        self.assertEqual(
            ["SouthNode"],
            derived["no_admitted_claim_bindings"],
        )

        research = RESEARCH_QUERY_CONTRACT.read_text(encoding="utf-8")
        self.assertIn("REFERENCE-ONLY", research)
        self.assertIn("production_routable = false", research)
        self.assertIn("NOT PRODUCTION-ROUTABLE", research)


    def test_north_node_registry_is_bounded_source_backed_and_non_karmic(self):
        registry = load(ROOT / "references" / "astrology" / "north_node_sign_semantics_claim_family_registry.json")
        self.assertEqual("north-node-sign-semantics-research-v1", registry["record_id"])
        self.assertFalse(registry["production_routable"])
        self.assertEqual("composable-symbolic-modern-v1", registry["selection_policy"]["required_semantic_profile"])
        self.assertEqual({"north_node_function": "north_node_core"}, registry["selection_policy"]["required_applicability_scopes_by_claim_type"])
        source = registry["sources"][0]
        self.assertEqual("82df4c1c285cb470625373a716bab86c343e4b6e", source["immutable_revision"])
        self.assertEqual("MIT", source["license_identifier"])
        self.assertIn("CLAIM_ELIGIBLE", source["admission_status"])
        self.assertIn("generic karmic doctrine", source["excluded_scope"])
        self.assertIn("past-life doctrine", source["excluded_scope"])
        self.assertIn("North Node aspect meanings", source["excluded_scope"])
        self.assertEqual("north_node_function", registry["claims"][0]["claim_type"])
        self.assertEqual(["context:modern_contemporary"], registry["claims"][0]["historical_context_refs"])
        import sys
        reference_dir = ROOT / "references" / "astrology"
        sys.path.insert(0, str(reference_dir))
        try:
            from validate_interpretation_claim_registry import validate_registry
            taxonomy = load(reference_dir / "tradition_taxonomy_example.json")
            self.assertEqual([], validate_registry(registry, taxonomy))
        finally:
            sys.path.pop(0)

    def test_index_publishes_all_selector_local_paths(self):
        index = load(INDEX)
        astrology = next(row for row in index["capabilities"] if row["id"] == "method.astrology")
        self.assertEqual(
            "schemas/astrology/ASTROLOGY_TYPED_EVIDENCE_SELECTION_REQUEST_V1.schema.json",
            astrology["typed_evidence_selection_request_schema"],
        )
        self.assertEqual(
            "schemas/astrology/ASTROLOGY_TYPED_EVIDENCE_SELECTION_V1.schema.json",
            astrology["typed_evidence_selection_schema"],
        )
        self.assertEqual("tools/astrology_evidence_selector.py", astrology["evidence_selector"])
        for key in (
            "typed_evidence_selection_request_schema",
            "typed_evidence_selection_schema",
            "evidence_selector",
        ):
            self.assertTrue((ROOT / astrology[key]).is_file())

    def test_selector_admission_does_not_expand_astrology_method_scope(self):
        manifest = load(MANIFEST)
        self.assertEqual(["natal", "transit"], manifest["reading_modes"])
        self.assertIn("synastry", manifest["unsupported_scopes"])
        self.assertIn("composite", manifest["unsupported_scopes"])
        self.assertIn("solar_return", manifest["unsupported_scopes"])
        self.assertIn("raw_birth_data_model_calculation", manifest["unsupported_scopes"])


    def test_natal_semantic_fallback_policy_is_machine_readable_and_fail_closed(self):
        manifest = load(MANIFEST)
        policy = manifest["natal_semantic_policy"]["semantic_composition_fallback"]
        self.assertEqual("natal-semantic-composition-fallback-v1", policy["policy_id"])
        self.assertEqual(
            ["exact_admitted_emergent_claim", "admitted_bounded_composition", "unsupported_factor"],
            policy["precedence"],
        )
        self.assertEqual("forbidden", policy["deterministic_fact_override"])
        self.assertEqual(
            "planet-sign-composable-semantics-research-v1",
            policy["planet_sign"]["baseline_registry_record_id"],
        )
        self.assertEqual(
            ["planet_function", "sign_style"],
            policy["planet_sign"]["required_claim_types"],
        )
        self.assertEqual(
            "use_bounded_composition_when_all_required_primitives_pass",
            policy["planet_sign"]["exact_pair_missing_behavior"],
        )
        self.assertEqual("aspect_pair", policy["natal_aspect"]["exact_pair_applicability_scope"])
        self.assertFalse(policy["natal_aspect"]["geometry_semantic_authority"])
        self.assertFalse(policy["natal_aspect"]["general_pair_relationship_semantic_admitted"])
        self.assertFalse(policy["natal_aspect"]["general_aspect_operator_semantic_admitted"])
        self.assertFalse(policy["natal_aspect"]["bounded_composition_currently_available"])
        self.assertEqual(
            "preserve_geometry_fact_and_mark_semantic_unsupported_factor",
            policy["natal_aspect"]["missing_exact_claim_behavior"],
        )
        self.assertEqual("forbidden", policy["model_memory_backfill"])

    def test_semantic_profile_project_default_is_orchestrator_owned_not_registry_silent_default(self):
        manifest = load(MANIFEST)
        natal = manifest["natal_semantic_policy"]
        profile = natal["semantic_profile_interaction_profile"]
        self.assertEqual(
            "semantic-profile-default-composable-symbolic-modern-v1",
            profile["policy_id"],
        )
        self.assertEqual("composable-symbolic-modern-v1", profile["default_semantic_profile"])
        self.assertEqual(["omitted", "null"], profile["default_on"])
        self.assertTrue(profile["explicit_user_choice_overrides_default"])
        self.assertEqual("semantic_profile_selection", profile["normalized_selection_field"])
        self.assertEqual("project_default", profile["default_selection_value"])
        self.assertEqual("explicit_user_choice", profile["explicit_selection_value"])
        self.assertEqual("forbidden", profile["registry_or_selector_silent_default"])
        self.assertEqual("fail_closed", profile["unsupported_profile_behavior"])
        self.assertFalse(profile["transit_default_activation"])
        self.assertEqual("forbidden_inside_registry_or_selector", natal["silent_default_semantic_profile"])

        for registry_path in (
            ROOT / "references" / "astrology" / "planet_sign_composable_semantics_claim_family_registry.json",
            ROOT / "references" / "astrology" / "north_node_sign_semantics_claim_family_registry.json",
        ):
            registry = load(registry_path)
            self.assertFalse(registry["selection_policy"]["silent_default_allowed"])

if __name__ == "__main__":
    unittest.main()
