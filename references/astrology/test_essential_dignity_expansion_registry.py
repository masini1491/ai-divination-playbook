#!/usr/bin/env python3
from __future__ import annotations

import json
import unittest
from pathlib import Path

from retrieve_interpretation_claims import retrieve_claims
from validate_interpretation_claim_registry import validate_registry


class EssentialDignityExpansionRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        here = Path(__file__).resolve().parent
        cls.taxonomy = json.loads((here / "tradition_taxonomy_example.json").read_text(encoding="utf-8"))
        cls.registry = json.loads((here / "essential_dignity_expansion_claim_family_registry.json").read_text(encoding="utf-8"))

    def test_registry_validates_under_v02_taxonomy_contract(self):
        self.assertEqual(validate_registry(self.registry, self.taxonomy), [])

    def test_registry_requires_l2_and_l3_metadata(self):
        self.assertEqual(
            self.registry["retrieval_preconditions"],
            {"requires_l2_facts": True, "requires_l3_policy": True},
        )

    def test_missing_dignity_facts_and_policy_fail_closed_without_query_flags(self):
        route = {
            "query_id": "dignity-auto-precondition",
            "claim_types": ["historical_doctrine"],
            "tradition_context_refs_any": ["lineage:hellenistic:ptolemaic"],
            "synthesis_mode": "synthesis:single_tradition",
            "applies_to_all": ["dignity", "exaltation", "fall", "depression"],
            "l2_fact_refs": [],
            "l3_policy_refs": [],
            "allow_reference_only_qualified": False,
            "include_registry_guardrails": False,
        }
        result = retrieve_claims(self.registry, route, self.taxonomy)
        self.assertEqual(result["retrieval_status"], "precondition_failed")
        self.assertEqual(set(result["precondition_failures"]), {"l2_fact_refs_required", "l3_policy_refs_required"})

    def test_ptolemaic_exaltation_claim_is_typed(self):
        route = {
            "query_id": "dignity-ptolemy-exaltation",
            "claim_types": ["historical_doctrine"],
            "tradition_context_refs_any": ["lineage:hellenistic:ptolemaic"],
            "synthesis_mode": "synthesis:single_tradition",
            "applies_to_all": ["dignity", "exaltation", "fall", "depression"],
            "l2_fact_refs": ["fact:planet-sign"],
            "l3_policy_refs": ["policy:ptolemaic-dignity"],
            "allow_reference_only_qualified": False,
            "include_registry_guardrails": False,
        }
        result = retrieve_claims(self.registry, route, self.taxonomy)
        self.assertEqual(result["retrieval_status"], "citation_ready")
        self.assertEqual(result["selected_claim_ids"], ["claim:ptolemy-exaltation-depression-pairs"])

    def test_term_system_plurality_is_not_flattened(self):
        claim = next(c for c in self.registry["claims"] if c["claim_id"] == "claim:ptolemy-multiple-term-systems")
        self.assertIn("method-dependent", claim["normalized_statement"])
        conflict = next(g for g in self.registry["conflict_groups"] if g["conflict_group_id"] == "conflict:term-system-selection")
        self.assertEqual(conflict["resolution_status"], "explicit_policy_required")

    def test_face_decan_terminology_gap_is_explicit(self):
        conflict = next(g for g in self.registry["conflict_groups"] if g["conflict_group_id"] == "conflict:face-decan-terminology")
        self.assertEqual(conflict["resolution_status"], "source_specific")
        self.assertIn("proper-face", conflict["resolution_note"])
        self.assertIn("decan/face", conflict["resolution_note"])

    def test_reference_practitioner_claim_requires_opt_in(self):
        route = {
            "query_id": "dignity-reference-default",
            "claim_types": ["dignity_meaning"],
            "tradition_tags_any": ["classical_practitioner"],
            "applies_to_all": ["dignity", "interpretation", "capacity", "accidental strength"],
            "l2_fact_refs": ["fact:dignity"],
            "l3_policy_refs": ["policy:dignity"],
            "allow_reference_only_qualified": False,
            "include_registry_guardrails": False,
        }
        result = retrieve_claims(self.registry, route, self.taxonomy)
        self.assertEqual(result["retrieval_status"], "no_match")
        route["allow_reference_only_qualified"] = True
        result = retrieve_claims(self.registry, route, self.taxonomy)
        self.assertEqual(result["retrieval_status"], "citation_ready")
        self.assertEqual(result["selected_claim_ids"], ["claim:reference-dignity-capacity-framework"])
        self.assertEqual(result["claims"][0]["source_admission_mode"], "qualified_reference_only")


if __name__ == "__main__":
    unittest.main()
