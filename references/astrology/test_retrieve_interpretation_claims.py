#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from retrieve_interpretation_claims import retrieve_claims


def synthetic_registry():
    return {
        "schema_name": "interpretation_claim_registry",
        "schema_version": "0.1.0-research",
        "record_status": "REFERENCE-ONLY",
        "record_kind": "interpretation_claim_family_registry",
        "record_id": "synthetic-retrieval-registry",
        "production_routable": False,
        "sources": [
            {
                "source_id": "source:primary",
                "title": "Primary",
                "source_role": "PRIMARY_TEXT",
                "admission_status": ["CLAIM_ELIGIBLE"],
                "locator": "Book III",
                "independence_status": "independent_evidence",
            },
            {
                "source_id": "source:practitioner",
                "title": "Practitioner",
                "source_role": "PRACTITIONER_REFERENCE",
                "admission_status": ["CLAIM_ELIGIBLE"],
                "locator": "Article section",
                "independence_status": "independent_evidence",
            },
            {
                "source_id": "source:reference",
                "title": "Reference implementation",
                "source_role": "REFERENCE_IMPLEMENTATION",
                "admission_status": ["REFERENCE_ONLY"],
                "locator": "references/example.md",
                "immutable_revision": "a" * 40,
                "independence_status": "shared_upstream",
            },
        ],
        "claims": [
            {
                "claim_id": "claim:historical",
                "layer": "L4",
                "claim_type": "historical_doctrine",
                "normalized_statement": "Historical bounded doctrine.",
                "source_refs": ["source:primary"],
                "tradition_tags": ["classical"],
                "applies_to": ["maternal inquiry"],
                "confidence_status": "qualified",
                "support_status": "tradition_bounded",
                "conflict_group_ids": ["conflict:scope"],
            },
            {
                "claim_id": "claim:modern-opposition",
                "layer": "L4",
                "claim_type": "aspect_meaning",
                "normalized_statement": "Modern psychological opposition framing.",
                "source_refs": ["source:practitioner"],
                "tradition_tags": ["modern", "psychological_astrology"],
                "applies_to": ["natal", "Moon-Saturn opposition"],
                "confidence_status": "qualified",
                "support_status": "tradition_bounded",
                "conflict_group_ids": ["conflict:scope"],
            },
            {
                "claim_id": "claim:reference-opposition",
                "layer": "L4",
                "claim_type": "aspect_meaning",
                "normalized_statement": "Reference implementation opposition framing.",
                "source_refs": ["source:reference"],
                "tradition_tags": ["modern", "blended"],
                "applies_to": ["Moon-Saturn opposition"],
                "confidence_status": "qualified",
                "support_status": "tradition_bounded",
                "conflict_group_ids": ["conflict:geometry"],
            },
        ],
        "conflict_groups": [
            {
                "conflict_group_id": "conflict:scope",
                "conflict_class": ["scope_difference"],
                "claim_refs": ["claim:historical", "claim:modern-opposition"],
                "resolution_status": "scope_separated",
                "resolution_note": "Keep historical and modern scopes separate.",
            },
            {
                "conflict_group_id": "conflict:geometry",
                "conflict_class": ["scope_difference"],
                "claim_refs": ["claim:reference-opposition"],
                "resolution_status": "scope_separated",
                "resolution_note": "Geometry and metaphor remain separate.",
            },
        ],
        "non_admitted_claims": ["Configuration proves trauma."],
        "privacy": {"contains_real_birth_data": False},
    }


def modern_opposition_query():
    return {
        "query_id": "synthetic-modern-opposition",
        "claim_types": ["aspect_meaning"],
        "tradition_tags_any": ["modern", "psychological_astrology"],
        "applies_to_all": ["natal", "Moon-Saturn opposition"],
        "requires_l2_facts": True,
        "l2_fact_refs": ["fact:moon-saturn-opposition"],
        "requires_l3_policy": True,
        "l3_policy_refs": ["policy:major-aspect-orb-v1"],
        "allow_reference_only_qualified": False,
        "include_registry_guardrails": True,
    }


class RetrievalBehaviorUnitTests(unittest.TestCase):
    def test_exact_modern_natal_opposition_selects_only_applicable_claim(self):
        result = retrieve_claims(synthetic_registry(), modern_opposition_query())
        self.assertEqual(result["retrieval_status"], "citation_ready")
        self.assertEqual(result["selected_claim_ids"], ["claim:modern-opposition"])

    def test_missing_l2_fact_fails_closed(self):
        query = modern_opposition_query()
        query["l2_fact_refs"] = []
        result = retrieve_claims(synthetic_registry(), query)
        self.assertEqual(result["retrieval_status"], "precondition_failed")
        self.assertIn("l2_fact_refs_required", result["precondition_failures"])
        self.assertEqual(result["selected_claim_ids"], [])

    def test_missing_l3_policy_fails_closed(self):
        query = modern_opposition_query()
        query["l3_policy_refs"] = []
        result = retrieve_claims(synthetic_registry(), query)
        self.assertEqual(result["retrieval_status"], "precondition_failed")
        self.assertIn("l3_policy_refs_required", result["precondition_failures"])

    def test_unknown_tradition_does_not_fallback(self):
        query = modern_opposition_query()
        query["tradition_tags_any"] = ["unknown_tradition"]
        result = retrieve_claims(synthetic_registry(), query)
        self.assertEqual(result["retrieval_status"], "no_match")
        self.assertEqual(result["claims"], [])

    def test_reference_only_is_excluded_by_default(self):
        query = modern_opposition_query()
        query["applies_to_all"] = ["Moon-Saturn opposition"]
        result = retrieve_claims(synthetic_registry(), query)
        self.assertEqual(result["selected_claim_ids"], ["claim:modern-opposition"])
        self.assertIn(
            {"claim_id": "claim:reference-opposition", "reason": "source_admission_insufficient"},
            result["excluded"],
        )

    def test_reference_only_can_be_explicitly_included_only_as_qualified(self):
        query = modern_opposition_query()
        query["applies_to_all"] = ["Moon-Saturn opposition"]
        query["allow_reference_only_qualified"] = True
        result = retrieve_claims(synthetic_registry(), query)
        self.assertEqual(
            result["selected_claim_ids"],
            ["claim:modern-opposition", "claim:reference-opposition"],
        )
        modes = {claim["claim_id"]: claim["source_admission_mode"] for claim in result["claims"]}
        self.assertEqual(modes["claim:reference-opposition"], "qualified_reference_only")

    def test_reference_only_unqualified_claim_is_still_excluded(self):
        registry = synthetic_registry()
        registry["claims"][2]["confidence_status"] = "supported"
        registry["claims"][2]["support_status"] = "single_source_supported"
        query = modern_opposition_query()
        query["applies_to_all"] = ["Moon-Saturn opposition"]
        query["allow_reference_only_qualified"] = True
        result = retrieve_claims(registry, query)
        self.assertNotIn("claim:reference-opposition", result["selected_claim_ids"])

    def test_conflict_is_preserved_not_averaged(self):
        result = retrieve_claims(synthetic_registry(), modern_opposition_query())
        self.assertEqual(len(result["conflicts"]), 1)
        conflict = result["conflicts"][0]
        self.assertEqual(conflict["conflict_group_id"], "conflict:scope")
        self.assertEqual(conflict["selected_claim_refs"], ["claim:modern-opposition"])
        self.assertEqual(conflict["external_claim_refs"], ["claim:historical"])
        self.assertEqual(conflict["resolution_status"], "scope_separated")

    def test_guardrails_are_carried_when_requested(self):
        result = retrieve_claims(synthetic_registry(), modern_opposition_query())
        self.assertEqual(result["guardrails"], ["Configuration proves trauma."])

    def test_guardrails_can_be_omitted_from_bundle(self):
        query = modern_opposition_query()
        query["include_registry_guardrails"] = False
        result = retrieve_claims(synthetic_registry(), query)
        self.assertEqual(result["guardrails"], [])

    def test_every_selected_claim_carries_source_provenance(self):
        result = retrieve_claims(synthetic_registry(), modern_opposition_query())
        claim = result["claims"][0]
        self.assertTrue(claim["citation_ready"])
        self.assertEqual(claim["source_provenance"][0]["source_id"], "source:practitioner")
        self.assertEqual(claim["source_provenance"][0]["locator"], "Article section")

    def test_missing_source_locator_marks_provenance_incomplete(self):
        registry = synthetic_registry()
        registry["sources"][1].pop("locator")
        result = retrieve_claims(registry, modern_opposition_query())
        self.assertEqual(result["retrieval_status"], "provenance_incomplete")
        self.assertFalse(result["claims"][0]["citation_ready"])

    def test_synthesis_provenance_keeps_l2_l3_l4_and_conflict_refs(self):
        result = retrieve_claims(synthetic_registry(), modern_opposition_query())
        provenance = result["synthesis_provenance"]
        self.assertEqual(provenance["l2_fact_refs"], ["fact:moon-saturn-opposition"])
        self.assertEqual(provenance["l3_policy_refs"], ["policy:major-aspect-orb-v1"])
        self.assertEqual(provenance["claim_refs"], ["claim:modern-opposition"])
        self.assertEqual(provenance["conflict_group_refs"], ["conflict:scope"])

    def test_production_registry_is_rejected(self):
        registry = synthetic_registry()
        registry["production_routable"] = True
        result = retrieve_claims(registry, modern_opposition_query())
        self.assertEqual(result["retrieval_status"], "registry_not_research_safe")

    def test_real_birth_data_registry_is_rejected(self):
        registry = synthetic_registry()
        registry["privacy"]["contains_real_birth_data"] = True
        result = retrieve_claims(registry, modern_opposition_query())
        self.assertEqual(result["retrieval_status"], "registry_not_research_safe")


class ActualRegistryRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        here = Path(__file__).resolve().parent
        cls.domicile = json.loads((here / "domicile_claim_family_registry.json").read_text(encoding="utf-8"))
        cls.saturn = json.loads((here / "saturn_moon_aspect_claim_family_registry.json").read_text(encoding="utf-8"))

    def test_domicile_historical_configuration_query(self):
        query = {
            "query_id": "actual-domicile-configuration",
            "claim_types": ["policy_configuration"],
            "tradition_tags_any": ["ptolemaic", "classical"],
            "applies_to_all": ["domicile configuration"],
            "requires_l2_facts": True,
            "l2_fact_refs": ["fact:venus-libra-placement"],
            "requires_l3_policy": True,
            "l3_policy_refs": ["policy:classical-domicile-candidate"],
            "allow_reference_only_qualified": False,
            "include_registry_guardrails": False,
        }
        result = retrieve_claims(self.domicile, query)
        self.assertEqual(result["retrieval_status"], "citation_ready")
        self.assertEqual(result["selected_claim_ids"], ["claim:domicile-configuration"])
        self.assertTrue(result["claims"][0]["citation_ready"])

    def test_domicile_southern_hemisphere_conflict_query(self):
        query = {
            "query_id": "actual-domicile-southern-conflict",
            "claim_types": ["historical_conflict"],
            "tradition_tags_any": ["history_of_astrology", "early_modern"],
            "applies_to_all": ["southern-hemisphere dignity applicability"],
            "requires_l2_facts": False,
            "l2_fact_refs": [],
            "requires_l3_policy": False,
            "l3_policy_refs": [],
            "allow_reference_only_qualified": False,
            "include_registry_guardrails": False,
        }
        result = retrieve_claims(self.domicile, query)
        self.assertEqual(result["selected_claim_ids"], ["claim:southern-hemisphere-reversal-debate"])
        self.assertEqual(result["conflicts"][0]["conflict_group_id"], "conflict:southern-hemisphere-dignity-applicability")
        self.assertIn("claim:domicile-configuration", result["conflicts"][0]["external_claim_refs"])

    def test_saturn_modern_natal_opposition_query(self):
        query = {
            "query_id": "actual-saturn-modern-natal-opposition",
            "claim_types": ["aspect_meaning"],
            "tradition_tags_any": ["modern", "psychological_astrology"],
            "applies_to_all": ["natal", "Moon-Saturn opposition"],
            "requires_l2_facts": True,
            "l2_fact_refs": ["fact:moon-saturn-opposition"],
            "requires_l3_policy": True,
            "l3_policy_refs": ["policy:major-aspect-orb-v1"],
            "allow_reference_only_qualified": False,
            "include_registry_guardrails": True,
        }
        result = retrieve_claims(self.saturn, query)
        self.assertEqual(result["retrieval_status"], "citation_ready")
        self.assertEqual(result["selected_claim_ids"], ["claim:greene-moon-saturn-parent-image"])
        self.assertIn("conflict:parent-symbol-vs-biography", result["synthesis_provenance"]["conflict_group_refs"])
        self.assertGreaterEqual(len(result["guardrails"]), 1)

    def test_saturn_reference_implementation_requires_explicit_opt_in(self):
        query = {
            "query_id": "actual-saturn-reference-opposition",
            "claim_types": ["aspect_meaning"],
            "tradition_tags_any": ["modern", "blended"],
            "applies_to_all": ["Moon-Saturn opposition"],
            "requires_l2_facts": True,
            "l2_fact_refs": ["fact:moon-saturn-opposition"],
            "requires_l3_policy": True,
            "l3_policy_refs": ["policy:major-aspect-orb-v1"],
            "allow_reference_only_qualified": False,
            "include_registry_guardrails": False,
        }
        default_result = retrieve_claims(self.saturn, query)
        self.assertNotIn("claim:reference-opposition-polarity", default_result["selected_claim_ids"])
        query["allow_reference_only_qualified"] = True
        opt_in_result = retrieve_claims(self.saturn, query)
        self.assertIn("claim:reference-opposition-polarity", opt_in_result["selected_claim_ids"])
        selected = {claim["claim_id"]: claim for claim in opt_in_result["claims"]}
        self.assertEqual(selected["claim:reference-opposition-polarity"]["source_admission_mode"], "mixed_claim_eligible_and_reference_only")

    def test_saturn_unknown_tradition_returns_no_match(self):
        query = {
            "query_id": "actual-saturn-unknown-tradition",
            "claim_types": ["aspect_meaning"],
            "tradition_tags_any": ["unrepresented_tradition"],
            "applies_to_all": ["Moon-Saturn opposition"],
            "requires_l2_facts": True,
            "l2_fact_refs": ["fact:moon-saturn-opposition"],
            "requires_l3_policy": True,
            "l3_policy_refs": ["policy:major-aspect-orb-v1"],
            "allow_reference_only_qualified": True,
            "include_registry_guardrails": True,
        }
        result = retrieve_claims(self.saturn, query)
        self.assertEqual(result["retrieval_status"], "no_match")
        self.assertEqual(result["selected_claim_ids"], [])


if __name__ == "__main__":
    unittest.main()
