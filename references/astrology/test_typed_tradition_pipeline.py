#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from typed_tradition_pipeline import run_typed_pipeline, validate_typed_resolution


class TypedTraditionPipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        here = Path(__file__).resolve().parent
        cls.taxonomy = json.loads((here / "tradition_taxonomy_example.json").read_text(encoding="utf-8"))
        cls.registry = json.loads((here / "saturn_moon_aspect_claim_family_registry.json").read_text(encoding="utf-8"))
        cls.registry_ids = {cls.registry["record_id"]}

    def resolution(self):
        return {
            "schema_name": "astrology_query_resolution",
            "schema_version": "0.1.0-research",
            "record_status": "REFERENCE-ONLY",
            "production_routable": False,
            "resolution_status": "resolved",
            "query_id": "typed-psych-opposition",
            "user_question": "In psychological astrology, what does a natal Moon-Saturn opposition mean?",
            "question_risk_class": "normal_symbolic",
            "target_registry_record_id": self.registry["record_id"],
            "tradition_resolution_status": "inferred_from_named_school",
            "requested_tradition_contexts": ["school:modern:psychological_astrology"],
            "requested_synthesis_mode": "synthesis:single_tradition",
            "route": {
                "query_id": "typed-psych-opposition",
                "claim_types": ["aspect_meaning"],
                "tradition_tags_any": [],
                "tradition_context_refs_any": ["school:modern:psychological_astrology"],
                "synthesis_mode": "synthesis:single_tradition",
                "applies_to_all": ["natal", "Moon-Saturn opposition"],
                "requires_l2_facts": True,
                "l2_fact_refs": ["fact:moon-saturn-opposition"],
                "requires_l3_policy": True,
                "l3_policy_refs": ["policy:major-aspect-orb-v1"],
                "allow_reference_only_qualified": False,
                "include_registry_guardrails": True,
            },
            "routing_assumptions": [
                {"field": "claim_types", "basis": "user_text", "evidence_spans": ["what does"], "evidence_refs": []},
                {"field": "tradition_context_refs_any", "basis": "user_text", "evidence_spans": ["psychological astrology"], "evidence_refs": []},
                {"field": "synthesis_mode", "basis": "research_policy", "evidence_spans": [], "evidence_refs": []},
                {"field": "applies_to_all", "basis": "user_text", "evidence_spans": ["natal Moon-Saturn opposition"], "evidence_refs": []},
                {"field": "l2_fact_refs", "basis": "upstream_context", "evidence_spans": [], "evidence_refs": ["fact:moon-saturn-opposition"]},
                {"field": "l3_policy_refs", "basis": "upstream_context", "evidence_spans": [], "evidence_refs": ["policy:major-aspect-orb-v1"]},
            ],
            "unresolved_slots": [],
        }

    def test_single_school_pipeline_reaches_l5(self):
        result = run_typed_pipeline(self.registry, self.resolution(), self.taxonomy, self.registry_ids)
        self.assertEqual(result["pipeline_status"], "complete")
        self.assertEqual(result["synthesis"]["synthesis_status"], "ready_for_l5")
        self.assertEqual(result["retrieval"]["selected_claim_ids"], ["claim:greene-moon-saturn-parent-image"])

    def test_typed_provenance_survives_retrieval_and_l5(self):
        result = run_typed_pipeline(self.registry, self.resolution(), self.taxonomy, self.registry_ids)
        expected = ["school:modern:psychological_astrology"]
        self.assertEqual(result["retrieval"]["tradition_provenance"]["requested_tradition_contexts"], expected)
        self.assertEqual(result["synthesis"]["tradition_provenance"]["requested_tradition_contexts"], expected)
        self.assertEqual(result["synthesis"]["route_snapshot"]["tradition_context_refs_any"], expected)
        self.assertEqual(result["synthesis"]["synthesis_units"][0]["tradition_context_refs"], expected)

    def test_mixed_legacy_and_typed_selector_fails(self):
        resolution = self.resolution()
        resolution["route"]["tradition_tags_any"] = ["psychological_astrology"]
        errors = validate_typed_resolution(resolution, self.taxonomy, self.registry_ids)
        self.assertIn("TRADITION_SELECTOR_MIXED", {error["code"] for error in errors})

    def test_unknown_or_non_doctrine_context_fails(self):
        resolution = self.resolution()
        resolution["requested_tradition_contexts"] = ["meta:history_of_astrology"]
        resolution["route"]["tradition_context_refs_any"] = ["meta:history_of_astrology"]
        errors = validate_typed_resolution(resolution, self.taxonomy, self.registry_ids)
        self.assertIn("TRADITION_CONTEXT_INVALID", {error["code"] for error in errors})

    def test_route_and_resolution_contexts_must_match(self):
        resolution = self.resolution()
        resolution["requested_tradition_contexts"] = ["lineage:hellenistic:ptolemaic"]
        errors = validate_typed_resolution(resolution, self.taxonomy, self.registry_ids)
        self.assertIn("TRADITION_CONTEXT_ROUTE_MISMATCH", {error["code"] for error in errors})

    def test_single_mode_rejects_multiple_contexts(self):
        resolution = self.resolution()
        refs = ["lineage:hellenistic:ptolemaic", "school:modern:psychological_astrology"]
        resolution["tradition_resolution_status"] = "explicit"
        resolution["requested_tradition_contexts"] = refs
        resolution["route"]["tradition_context_refs_any"] = refs
        errors = validate_typed_resolution(resolution, self.taxonomy, self.registry_ids)
        self.assertIn("SINGLE_TRADITION_CARDINALITY_INVALID", {error["code"] for error in errors})

    def comparison_resolution(self):
        resolution = self.resolution()
        refs = ["lineage:hellenistic:ptolemaic", "school:modern:psychological_astrology"]
        resolution["query_id"] = "typed-parallel-comparison"
        resolution["user_question"] = "Compare Ptolemaic and psychological astrology Moon-Saturn meanings."
        resolution["tradition_resolution_status"] = "explicit"
        resolution["requested_tradition_contexts"] = refs
        resolution["requested_synthesis_mode"] = "synthesis:parallel_comparison"
        resolution["route"]["query_id"] = resolution["query_id"]
        resolution["route"]["claim_types"] = ["historical_doctrine", "aspect_meaning"]
        resolution["route"]["tradition_context_refs_any"] = refs
        resolution["route"]["synthesis_mode"] = "synthesis:parallel_comparison"
        resolution["route"]["applies_to_all"] = []
        resolution["route"]["requires_l2_facts"] = False
        resolution["route"]["l2_fact_refs"] = []
        resolution["route"]["requires_l3_policy"] = False
        resolution["route"]["l3_policy_refs"] = []
        resolution["routing_assumptions"] = [
            {"field": "claim_types", "basis": "research_fixture", "evidence_spans": [], "evidence_refs": []},
            {"field": "tradition_context_refs_any", "basis": "user_text", "evidence_spans": ["Ptolemaic", "psychological astrology"], "evidence_refs": []},
            {"field": "synthesis_mode", "basis": "user_text", "evidence_spans": ["Compare"], "evidence_refs": []},
        ]
        return resolution

    def test_parallel_comparison_requires_both_contexts_covered(self):
        result = run_typed_pipeline(self.registry, self.comparison_resolution(), self.taxonomy, self.registry_ids)
        self.assertEqual(result["pipeline_status"], "complete")
        provenance = result["retrieval"]["tradition_provenance"]
        self.assertEqual(provenance["missing_tradition_contexts"], [])
        self.assertEqual(set(provenance["covered_tradition_contexts"]), set(self.comparison_resolution()["requested_tradition_contexts"]))
        self.assertTrue(any("visibly separate" in item for item in result["synthesis"]["required_disclosures"]))

    def test_parallel_comparison_blocks_partial_coverage(self):
        registry = copy.deepcopy(self.registry)
        registry["claims"] = [
            claim for claim in registry["claims"]
            if "psychological_astrology" not in claim.get("tradition_tags", [])
        ]
        result = run_typed_pipeline(registry, self.comparison_resolution(), self.taxonomy, self.registry_ids)
        self.assertEqual(result["pipeline_status"], "blocked")
        self.assertEqual(result["retrieval"]["retrieval_status"], "tradition_coverage_incomplete")
        self.assertEqual(result["synthesis"]["synthesis_status"], "blocked_tradition_coverage_incomplete")
        self.assertIn("school:modern:psychological_astrology", result["retrieval"]["tradition_provenance"]["missing_tradition_contexts"])

    def test_no_cross_tradition_substitution_on_partial_coverage(self):
        registry = copy.deepcopy(self.registry)
        registry["claims"] = [
            claim for claim in registry["claims"]
            if "psychological_astrology" not in claim.get("tradition_tags", [])
        ]
        result = run_typed_pipeline(registry, self.comparison_resolution(), self.taxonomy, self.registry_ids)
        self.assertTrue(any("do not silently substitute" in item.lower() for item in result["synthesis"]["required_disclosures"]))

    def test_explicit_blend_remains_explicit_in_l5_provenance(self):
        resolution = self.comparison_resolution()
        resolution["requested_synthesis_mode"] = "synthesis:explicit_blend"
        resolution["route"]["synthesis_mode"] = "synthesis:explicit_blend"
        result = run_typed_pipeline(self.registry, resolution, self.taxonomy, self.registry_ids)
        self.assertEqual(result["pipeline_status"], "complete")
        self.assertEqual(result["synthesis"]["tradition_provenance"]["requested_synthesis_mode"], "synthesis:explicit_blend")
        self.assertTrue(any("explicitly requested a blend" in item for item in result["synthesis"]["required_disclosures"]))


if __name__ == "__main__":
    unittest.main()
