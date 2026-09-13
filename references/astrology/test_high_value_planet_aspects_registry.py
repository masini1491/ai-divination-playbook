#!/usr/bin/env python3
from __future__ import annotations

import json
import unittest
from pathlib import Path

from retrieve_interpretation_claims import retrieve_claims
from validate_interpretation_claim_registry import validate_registry


class HighValuePlanetAspectsRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        here = Path(__file__).resolve().parent
        cls.taxonomy = json.loads((here / "tradition_taxonomy_example.json").read_text(encoding="utf-8"))
        cls.registry = json.loads((here / "high_value_planet_aspects_claim_family_registry.json").read_text(encoding="utf-8"))

    def test_registry_validates_under_v02_taxonomy_contract(self):
        self.assertEqual(validate_registry(self.registry, self.taxonomy), [])

    def test_registry_requires_l2_and_l3_preconditions(self):
        self.assertEqual(
            self.registry["retrieval_preconditions"],
            {"requires_l2_facts": True, "requires_l3_policy": True},
        )

    def test_pair_reference_claim_fails_closed_without_facts_or_policy(self):
        route = {
            "query_id": "pair-precondition",
            "claim_types": ["aspect_meaning"],
            "tradition_tags_any": ["pair_specific_interpretation"],
            "applies_to_all": ["Sun", "Saturn", "square", "natal"],
            "l2_fact_refs": [],
            "l3_policy_refs": [],
            "allow_reference_only_qualified": True,
            "include_registry_guardrails": False,
        }
        result = retrieve_claims(self.registry, route, self.taxonomy)
        self.assertEqual(result["retrieval_status"], "precondition_failed")
        self.assertEqual(set(result["precondition_failures"]), {"l2_fact_refs_required", "l3_policy_refs_required"})

    def test_pair_reference_claim_requires_explicit_qualified_opt_in(self):
        route = {
            "query_id": "sun-saturn-reference",
            "claim_types": ["aspect_meaning"],
            "tradition_tags_any": ["pair_specific_interpretation"],
            "applies_to_all": ["Sun", "Saturn", "square", "natal"],
            "l2_fact_refs": ["fact:sun-square-saturn"],
            "l3_policy_refs": ["policy:major-aspect-orb"],
            "allow_reference_only_qualified": False,
            "include_registry_guardrails": False,
        }
        result = retrieve_claims(self.registry, route, self.taxonomy)
        self.assertEqual(result["retrieval_status"], "no_match")
        route["allow_reference_only_qualified"] = True
        result = retrieve_claims(self.registry, route, self.taxonomy)
        self.assertEqual(result["retrieval_status"], "citation_ready")
        self.assertEqual(result["selected_claim_ids"], ["claim:reference-sun-square-saturn"])
        self.assertEqual(result["claims"][0]["source_admission_mode"], "qualified_reference_only")

    def test_all_five_pair_exemplars_are_present(self):
        expected = {
            "claim:reference-sun-square-saturn",
            "claim:reference-venus-square-mars",
            "claim:reference-mars-opposition-saturn",
            "claim:reference-mercury-trine-jupiter",
            "claim:reference-venus-square-saturn",
        }
        observed = {c["claim_id"] for c in self.registry["claims"] if c["claim_type"] == "aspect_meaning"}
        self.assertEqual(observed, expected)

    def test_primary_geometry_claim_is_not_pair_specific(self):
        claim = next(c for c in self.registry["claims"] if c["claim_id"] == "claim:ptolemy-major-aspect-geometry-distinct")
        self.assertEqual(claim["tradition_context_refs"], ["lineage:hellenistic:ptolemaic"])
        self.assertNotIn("Sun", claim["applies_to"])
        self.assertNotIn("Saturn", claim["applies_to"])

    def test_venus_mars_claim_contains_consent_guardrail(self):
        claim = next(c for c in self.registry["claims"] if c["claim_id"] == "claim:reference-venus-square-mars")
        self.assertIn("Consent", " ".join(claim["cautions"]))


if __name__ == "__main__":
    unittest.main()
