#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from retrieve_interpretation_claims import retrieve_claims
from validate_interpretation_claim_registry import validate_registry


class RegistryRetrievalPreconditionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        here = Path(__file__).resolve().parent
        cls.taxonomy = json.loads((here / "tradition_taxonomy_example.json").read_text(encoding="utf-8"))
        cls.registry = json.loads((here / "remaining_house_axes_claim_family_registry.json").read_text(encoding="utf-8"))

    def test_preconditions_object_must_be_object(self):
        data = copy.deepcopy(self.registry)
        data["retrieval_preconditions"] = []
        codes = {row["code"] for row in validate_registry(data, self.taxonomy)}
        self.assertIn("RETRIEVAL_PRECONDITIONS_OBJECT_REQUIRED", codes)

    def test_precondition_flags_must_be_boolean(self):
        data = copy.deepcopy(self.registry)
        data["retrieval_preconditions"]["requires_l2_facts"] = "yes"
        codes = {row["code"] for row in validate_registry(data, self.taxonomy)}
        self.assertIn("RETRIEVAL_PRECONDITION_BOOLEAN_REQUIRED", codes)

    def test_registry_and_query_preconditions_are_or_composed(self):
        route = {
            "query_id": "metadata-or-composition",
            "claim_types": ["historical_doctrine"],
            "tradition_context_refs_any": ["lineage:hellenistic"],
            "synthesis_mode": "synthesis:single_tradition",
            "applies_to_all": ["natal", "second house", "resources"],
            "requires_l3_policy": True,
            "l2_fact_refs": [],
            "l3_policy_refs": [],
            "allow_reference_only_qualified": False,
            "include_registry_guardrails": False,
        }
        result = retrieve_claims(self.registry, route, self.taxonomy)
        self.assertEqual(result["retrieval_status"], "precondition_failed")
        self.assertEqual(set(result["precondition_failures"]), {"l2_fact_refs_required", "l3_policy_refs_required"})
        provenance = result["precondition_provenance"]
        self.assertTrue(provenance["registry_requires_l2_facts"])
        self.assertTrue(provenance["query_requires_l3_policy"])
        self.assertTrue(provenance["effective_requires_l2_facts"])
        self.assertTrue(provenance["effective_requires_l3_policy"])

    def test_registry_without_metadata_preserves_legacy_behavior(self):
        data = copy.deepcopy(self.registry)
        data.pop("retrieval_preconditions")
        route = {
            "query_id": "metadata-absent-legacy",
            "claim_types": ["historical_doctrine"],
            "tradition_context_refs_any": ["lineage:hellenistic"],
            "synthesis_mode": "synthesis:single_tradition",
            "applies_to_all": ["natal", "second house", "resources"],
            "l2_fact_refs": [],
            "l3_policy_refs": [],
            "allow_reference_only_qualified": False,
            "include_registry_guardrails": False,
        }
        result = retrieve_claims(data, route, self.taxonomy)
        self.assertEqual(result["retrieval_status"], "citation_ready")
        self.assertFalse(result["precondition_provenance"]["effective_requires_l2_facts"])


if __name__ == "__main__":
    unittest.main()
