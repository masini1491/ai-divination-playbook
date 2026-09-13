#!/usr/bin/env python3
from __future__ import annotations

import json
import unittest
from pathlib import Path

from retrieve_interpretation_claims import retrieve_claims
from validate_interpretation_claim_registry import validate_registry


class TransitInterpretationRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        here = Path(__file__).resolve().parent
        cls.taxonomy = json.loads((here / "tradition_taxonomy_example.json").read_text(encoding="utf-8"))
        cls.registry = json.loads((here / "transit_interpretation_claim_family_registry.json").read_text(encoding="utf-8"))

    def test_registry_validates_under_v02_taxonomy_contract(self):
        self.assertEqual(validate_registry(self.registry, self.taxonomy), [])

    def test_registry_requires_l2_and_l3_preconditions(self):
        self.assertEqual(
            self.registry["retrieval_preconditions"],
            {"requires_l2_facts": True, "requires_l3_policy": True},
        )

    def test_missing_transit_facts_and_policy_fail_closed(self):
        route = {
            "query_id": "transit-auto-precondition",
            "claim_types": ["transit_policy"],
            "tradition_tags_any": ["research_policy"],
            "applies_to_all": ["transit", "station", "ingress", "transit-to-natal", "exact passage"],
            "l2_fact_refs": [],
            "l3_policy_refs": [],
            "allow_reference_only_qualified": False,
            "include_registry_guardrails": False,
        }
        result = retrieve_claims(self.registry, route, self.taxonomy)
        self.assertEqual(result["retrieval_status"], "precondition_failed")
        self.assertEqual(set(result["precondition_failures"]), {"l2_fact_refs_required", "l3_policy_refs_required"})

    def test_project_transit_policy_is_claim_eligible(self):
        route = {
            "query_id": "transit-project-policy",
            "claim_types": ["transit_policy"],
            "tradition_tags_any": ["research_policy"],
            "applies_to_all": ["transit", "station", "ingress", "transit-to-natal", "exact passage"],
            "l2_fact_refs": ["fact:transit-event"],
            "l3_policy_refs": ["policy:transit-timing"],
            "allow_reference_only_qualified": False,
            "include_registry_guardrails": False,
        }
        result = retrieve_claims(self.registry, route, self.taxonomy)
        self.assertEqual(result["retrieval_status"], "citation_ready")
        self.assertEqual(result["selected_claim_ids"], ["claim:project-transit-facts-before-interpretation"])
        self.assertEqual(result["claims"][0]["source_admission_mode"], "claim_eligible")

    def test_station_reference_meaning_requires_explicit_opt_in(self):
        route = {
            "query_id": "transit-station-reference",
            "claim_types": ["transit_meaning"],
            "tradition_tags_any": ["transit_interpretation"],
            "applies_to_all": ["transit", "station", "timing window"],
            "l2_fact_refs": ["fact:station"],
            "l3_policy_refs": ["policy:station-window"],
            "allow_reference_only_qualified": False,
            "include_registry_guardrails": False,
        }
        result = retrieve_claims(self.registry, route, self.taxonomy)
        self.assertEqual(result["retrieval_status"], "no_match")
        route["allow_reference_only_qualified"] = True
        result = retrieve_claims(self.registry, route, self.taxonomy)
        self.assertEqual(result["retrieval_status"], "citation_ready")
        self.assertEqual(result["selected_claim_ids"], ["claim:reference-station-emphasis-window"])
        self.assertEqual(result["claims"][0]["source_admission_mode"], "qualified_reference_only")

    def test_event_certainty_guardrail_names_high_stakes_examples(self):
        claim = next(c for c in self.registry["claims"] if c["claim_id"] == "claim:reference-transit-event-certainty-forbidden")
        text = claim["normalized_statement"].lower()
        for token in ("pregnancy", "death", "illness", "legal", "investments", "job loss", "relationship endings"):
            self.assertIn(token, text)

    def test_unknown_time_angle_policy_remains_fail_closed(self):
        claim = next(c for c in self.registry["claims"] if c["claim_id"] == "claim:project-unknown-time-transit-angle-fail-closed")
        self.assertIn("Ascendant", claim["normalized_statement"])
        self.assertIn("MC", claim["normalized_statement"])
        self.assertIn("fail closed", claim["normalized_statement"])


if __name__ == "__main__":
    unittest.main()
