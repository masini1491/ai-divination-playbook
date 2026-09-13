#!/usr/bin/env python3
from __future__ import annotations

import json
import unittest
from pathlib import Path

from retrieve_interpretation_claims import retrieve_claims
from validate_interpretation_claim_registry import validate_registry


class RemainingHouseAxesRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        here = Path(__file__).resolve().parent
        cls.taxonomy = json.loads((here / "tradition_taxonomy_example.json").read_text(encoding="utf-8"))
        cls.registry = json.loads((here / "remaining_house_axes_claim_family_registry.json").read_text(encoding="utf-8"))

    def test_registry_validates_under_v02_taxonomy_contract(self):
        self.assertEqual(validate_registry(self.registry, self.taxonomy), [])

    def test_registry_metadata_requires_l2_facts(self):
        self.assertEqual(
            self.registry["retrieval_preconditions"],
            {"requires_l2_facts": True, "requires_l3_policy": False},
        )

    def test_metadata_driven_l2_precondition_fails_closed_without_query_flag(self):
        route = {
            "query_id": "remaining-house-auto-precondition",
            "claim_types": ["historical_doctrine"],
            "tradition_context_refs_any": ["lineage:hellenistic"],
            "synthesis_mode": "synthesis:single_tradition",
            "applies_to_all": ["natal", "second house", "resources"],
            "l2_fact_refs": [],
            "l3_policy_refs": [],
            "allow_reference_only_qualified": False,
            "include_registry_guardrails": False,
        }
        result = retrieve_claims(self.registry, route, self.taxonomy)
        self.assertEqual(result["retrieval_status"], "precondition_failed")
        self.assertEqual(result["precondition_failures"], ["l2_fact_refs_required"])
        self.assertTrue(result["precondition_provenance"]["registry_requires_l2_facts"])
        self.assertFalse(result["precondition_provenance"]["query_requires_l2_facts"])

    def test_hellenistic_second_house_selects_only_valens(self):
        route = {
            "query_id": "remaining-house-second",
            "claim_types": ["historical_doctrine"],
            "tradition_context_refs_any": ["lineage:hellenistic"],
            "synthesis_mode": "synthesis:single_tradition",
            "applies_to_all": ["natal", "second house", "resources"],
            "l2_fact_refs": ["fact:house-2"],
            "l3_policy_refs": [],
            "allow_reference_only_qualified": False,
            "include_registry_guardrails": False,
        }
        result = retrieve_claims(self.registry, route, self.taxonomy)
        self.assertEqual(result["retrieval_status"], "citation_ready")
        self.assertEqual(result["selected_claim_ids"], ["claim:valens-second-place-resource-exchange"])

    def test_hellenistic_ninth_house_selects_only_valens(self):
        route = {
            "query_id": "remaining-house-ninth",
            "claim_types": ["historical_doctrine"],
            "tradition_context_refs_any": ["lineage:hellenistic"],
            "synthesis_mode": "synthesis:single_tradition",
            "applies_to_all": ["natal", "ninth house", "religion", "travel", "divination"],
            "l2_fact_refs": ["fact:house-9"],
            "l3_policy_refs": [],
            "allow_reference_only_qualified": False,
            "include_registry_guardrails": False,
        }
        result = retrieve_claims(self.registry, route, self.taxonomy)
        self.assertEqual(result["retrieval_status"], "citation_ready")
        self.assertEqual(result["selected_claim_ids"], ["claim:valens-ninth-place-god-travel-oracles"])

    def test_all_remaining_house_numbers_have_historical_claim(self):
        expected = {"second house", "third house", "fifth house", "sixth house", "eighth house", "ninth house", "eleventh house", "twelfth house"}
        observed = set()
        for claim in self.registry["claims"]:
            if claim["claim_type"] != "historical_doctrine":
                continue
            observed.update(expected.intersection(claim.get("applies_to", [])))
        self.assertEqual(observed, expected)

    def test_modern_reference_claim_is_reference_only_and_untyped(self):
        claim = next(c for c in self.registry["claims"] if c["claim_id"] == "claim:reference-remaining-houses-modern-psychological-language")
        self.assertEqual(claim["tradition_context_refs"], [])
        source = next(s for s in self.registry["sources"] if s["source_id"] == "source:wvanderen-remaining-house-modules")
        self.assertEqual(source["admission_status"], ["REFERENCE_ONLY"])

    def test_difficult_house_guardrails_are_explicit(self):
        joined = " ".join(self.registry["non_admitted_claims"]).lower()
        self.assertIn("medical", joined)
        self.assertIn("death", joined)
        self.assertIn("financial", joined)


if __name__ == "__main__":
    unittest.main()
