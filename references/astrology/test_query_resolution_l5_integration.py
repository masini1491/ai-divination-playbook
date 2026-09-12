#!/usr/bin/env python3
from __future__ import annotations

import json
import unittest
from pathlib import Path

from compose_interpretation_synthesis import compose_synthesis
from retrieve_interpretation_claims import retrieve_claims
from validate_astrology_query_resolution import validate_query_resolution


class ActualMoonSaturnPipelineIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        here = Path(__file__).resolve().parent
        cls.registry = json.loads((here / "saturn_moon_aspect_claim_family_registry.json").read_text(encoding="utf-8"))

    def resolution(self):
        return {
            "schema_name": "astrology_query_resolution",
            "schema_version": "0.1.0-research",
            "record_status": "REFERENCE-ONLY",
            "production_routable": False,
            "resolution_status": "resolved",
            "query_id": "actual-saturn-modern-natal-opposition-pipeline",
            "user_question": "In modern psychological astrology, what does a natal Moon-Saturn opposition mean?",
            "question_risk_class": "normal_symbolic",
            "target_registry_record_id": self.registry["record_id"],
            "route": {
                "query_id": "actual-saturn-modern-natal-opposition-pipeline",
                "claim_types": ["aspect_meaning"],
                "tradition_tags_any": ["modern", "psychological_astrology"],
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
                {"field": "tradition_tags_any", "basis": "user_text", "evidence_spans": ["modern psychological astrology"], "evidence_refs": []},
                {"field": "applies_to_all", "basis": "user_text", "evidence_spans": ["natal Moon-Saturn opposition"], "evidence_refs": []},
                {"field": "l2_fact_refs", "basis": "upstream_context", "evidence_spans": [], "evidence_refs": ["fact:moon-saturn-opposition"]},
                {"field": "l3_policy_refs", "basis": "upstream_context", "evidence_spans": [], "evidence_refs": ["policy:major-aspect-orb-v1"]},
            ],
            "unresolved_slots": [],
        }

    def test_resolution_validates_against_actual_registry_id(self):
        resolution = self.resolution()
        self.assertEqual(validate_query_resolution(resolution, {self.registry["record_id"]}), [])

    def test_actual_registry_retrieval_selects_greene_claim(self):
        resolution = self.resolution()
        bundle = retrieve_claims(self.registry, resolution["route"])
        self.assertEqual(bundle["retrieval_status"], "citation_ready")
        self.assertEqual(bundle["selected_claim_ids"], ["claim:greene-moon-saturn-parent-image"])

    def test_actual_registry_composes_ready_for_l5(self):
        resolution = self.resolution()
        bundle = retrieve_claims(self.registry, resolution["route"])
        envelope = compose_synthesis(resolution, bundle)
        self.assertEqual(envelope["synthesis_status"], "ready_for_l5")
        self.assertEqual(envelope["synthesis_units"][0]["claim_id"], "claim:greene-moon-saturn-parent-image")
        self.assertGreaterEqual(len(envelope["citation_units"]), 1)

    def test_actual_registry_preserves_conflict_guardrail_and_route_provenance(self):
        resolution = self.resolution()
        bundle = retrieve_claims(self.registry, resolution["route"])
        envelope = compose_synthesis(resolution, bundle)
        conflict_ids = {item["conflict_group_id"] for item in envelope["conflicts"]}
        self.assertIn("conflict:parent-symbol-vs-biography", conflict_ids)
        self.assertGreaterEqual(len(envelope["guardrails"]), 1)
        self.assertEqual(envelope["route_snapshot"]["l2_fact_refs"], ["fact:moon-saturn-opposition"])
        self.assertEqual(envelope["route_snapshot"]["l3_policy_refs"], ["policy:major-aspect-orb-v1"])


if __name__ == "__main__":
    unittest.main()
