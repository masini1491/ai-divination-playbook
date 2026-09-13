#!/usr/bin/env python3
from __future__ import annotations

import json
import unittest
from pathlib import Path

from retrieve_interpretation_claims import retrieve_claims
from validate_interpretation_claim_registry import validate_registry


class FourthTenthHouseAxisRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        here = Path(__file__).resolve().parent
        cls.taxonomy = json.loads((here / "tradition_taxonomy_example.json").read_text(encoding="utf-8"))
        cls.registry = json.loads((here / "fourth_tenth_house_axis_claim_family_registry.json").read_text(encoding="utf-8"))

    def test_registry_validates_under_v02_taxonomy_contract(self):
        self.assertEqual(validate_registry(self.registry, self.taxonomy), [])

    def test_hellenistic_fourth_house_typed_route_selects_only_valens(self):
        route = {
            "query_id": "axis-hellenistic-fourth",
            "claim_types": ["historical_doctrine"],
            "tradition_tags_any": [],
            "tradition_context_refs_any": ["lineage:hellenistic"],
            "synthesis_mode": "synthesis:single_tradition",
            "applies_to_all": ["natal", "fourth house", "IC", "home"],
            "requires_l2_facts": True,
            "l2_fact_refs": ["fact:ic", "fact:house-4"],
            "requires_l3_policy": False,
            "l3_policy_refs": [],
            "allow_reference_only_qualified": False,
            "include_registry_guardrails": False,
        }
        result = retrieve_claims(self.registry, route, self.taxonomy)
        self.assertEqual(result["retrieval_status"], "citation_ready")
        self.assertEqual(result["selected_claim_ids"], ["claim:valens-fourth-place-home-possessions-activity"])

    def test_hellenistic_tenth_house_typed_route_selects_only_valens(self):
        route = {
            "query_id": "axis-hellenistic-tenth",
            "claim_types": ["historical_doctrine"],
            "tradition_tags_any": [],
            "tradition_context_refs_any": ["lineage:hellenistic"],
            "synthesis_mode": "synthesis:single_tradition",
            "applies_to_all": ["natal", "tenth house", "MC", "occupation"],
            "requires_l2_facts": True,
            "l2_fact_refs": ["fact:mc", "fact:house-10"],
            "requires_l3_policy": False,
            "l3_policy_refs": [],
            "allow_reference_only_qualified": False,
            "include_registry_guardrails": False,
        }
        result = retrieve_claims(self.registry, route, self.taxonomy)
        self.assertEqual(result["retrieval_status"], "citation_ready")
        self.assertEqual(result["selected_claim_ids"], ["claim:valens-tenth-place-occupation-rank-success"])

    def test_early_modern_lilly_discovery_keeps_empty_doctrine_context(self):
        route = {
            "query_id": "axis-lilly-tenth",
            "claim_types": ["historical_doctrine"],
            "tradition_tags_any": ["early_modern"],
            "applies_to_all": ["tenth house", "MC", "profession"],
            "requires_l2_facts": True,
            "l2_fact_refs": ["fact:mc", "fact:house-10"],
            "requires_l3_policy": False,
            "l3_policy_refs": [],
            "allow_reference_only_qualified": False,
            "include_registry_guardrails": False,
        }
        result = retrieve_claims(self.registry, route, self.taxonomy)
        self.assertEqual(result["retrieval_status"], "citation_ready")
        self.assertEqual(result["selected_claim_ids"], ["claim:lilly-tenth-house-authority-honour-profession"])
        self.assertEqual(result["claims"][0]["tradition_context_refs"], [])

    def test_reference_only_calling_claim_is_excluded_without_opt_in(self):
        route = {
            "query_id": "axis-modern-tenth-default",
            "claim_types": ["house_meaning"],
            "tradition_tags_any": ["psychological_language"],
            "applies_to_all": ["tenth house", "calling"],
            "requires_l2_facts": True,
            "l2_fact_refs": ["fact:mc", "fact:house-10"],
            "requires_l3_policy": False,
            "l3_policy_refs": [],
            "allow_reference_only_qualified": False,
            "include_registry_guardrails": False,
        }
        result = retrieve_claims(self.registry, route, self.taxonomy)
        self.assertEqual(result["retrieval_status"], "no_match")
        self.assertIn(
            {"claim_id": "claim:reference-tenth-house-calling-public-identity", "reason": "source_admission_insufficient"},
            result["excluded"],
        )

    def test_reference_only_calling_claim_can_be_qualified_opt_in(self):
        route = {
            "query_id": "axis-modern-tenth-opt-in",
            "claim_types": ["house_meaning"],
            "tradition_tags_any": ["psychological_language"],
            "applies_to_all": ["tenth house", "calling"],
            "requires_l2_facts": True,
            "l2_fact_refs": ["fact:mc", "fact:house-10"],
            "requires_l3_policy": False,
            "l3_policy_refs": [],
            "allow_reference_only_qualified": True,
            "include_registry_guardrails": False,
        }
        result = retrieve_claims(self.registry, route, self.taxonomy)
        self.assertEqual(result["retrieval_status"], "citation_ready")
        self.assertEqual(result["selected_claim_ids"], ["claim:reference-tenth-house-calling-public-identity"])
        self.assertEqual(result["claims"][0]["source_admission_mode"], "qualified_reference_only")

    def test_house_axis_route_fails_closed_when_required_l2_refs_are_missing(self):
        route = {
            "query_id": "axis-fourth-missing-l2",
            "claim_types": ["historical_doctrine"],
            "tradition_tags_any": [],
            "tradition_context_refs_any": ["lineage:hellenistic"],
            "synthesis_mode": "synthesis:single_tradition",
            "applies_to_all": ["natal", "fourth house", "IC", "home"],
            "requires_l2_facts": True,
            "l2_fact_refs": [],
            "requires_l3_policy": False,
            "l3_policy_refs": [],
            "allow_reference_only_qualified": False,
            "include_registry_guardrails": False,
        }
        result = retrieve_claims(self.registry, route, self.taxonomy)
        self.assertEqual(result["retrieval_status"], "precondition_failed")
        self.assertIn("l2_fact_refs_required", result["precondition_failures"])
        self.assertEqual(result["selected_claim_ids"], [])

    def test_parent_signification_is_preserved_as_coexist_conflict_not_universal_policy(self):
        conflicts = {row["conflict_group_id"]: row for row in self.registry["conflict_groups"]}
        parent = conflicts["conflict:fourth-tenth-parent-signification"]
        self.assertEqual(parent["resolution_status"], "coexist")
        claims = {claim["claim_id"]: claim for claim in self.registry["claims"]}
        self.assertIn("father", claims["claim:lilly-fourth-house-land-father-endings"]["applies_to"])
        self.assertIn("mother", claims["claim:lilly-tenth-house-authority-honour-profession"]["applies_to"])
        self.assertFalse(any(claim["claim_type"] == "policy_configuration" and "parent" in claim["normalized_statement"].lower() for claim in self.registry["claims"]))

    def test_modern_reference_claims_are_not_silently_typed_as_psychological_school(self):
        claims = {claim["claim_id"]: claim for claim in self.registry["claims"]}
        self.assertEqual(claims["claim:reference-fourth-house-belonging-emotional-foundation"]["tradition_context_refs"], [])
        self.assertEqual(claims["claim:reference-tenth-house-calling-public-identity"]["tradition_context_refs"], [])


if __name__ == "__main__":
    unittest.main()
