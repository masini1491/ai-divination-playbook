#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import unittest

from compose_interpretation_synthesis import compose_synthesis
from validate_astrology_query_resolution import validate_query_resolution


def resolved_resolution():
    return {
        "schema_name": "astrology_query_resolution",
        "schema_version": "0.1.0-research",
        "record_status": "REFERENCE-ONLY",
        "production_routable": False,
        "resolution_status": "resolved",
        "query_id": "q1",
        "user_question": "In modern psychological astrology, what does a natal Moon-Saturn opposition mean?",
        "question_risk_class": "normal_symbolic",
        "target_registry_record_id": "saturn-moon-major-aspects-research-v1",
        "route": {
            "query_id": "q1",
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


def bundle_fixture():
    return {
        "schema_name": "interpretation_retrieval_provenance_bundle",
        "schema_version": "0.1.0-research",
        "record_status": "REFERENCE-ONLY",
        "production_routable": False,
        "query_id": "q1",
        "registry_record_id": "saturn-moon-major-aspects-research-v1",
        "registry_schema_name": "interpretation_claim_registry",
        "registry_schema_version": "0.1.0-research",
        "retrieval_status": "citation_ready",
        "selected_claim_ids": ["claim:modern"],
        "claims": [
            {
                "claim_id": "claim:modern",
                "layer": "L4",
                "claim_type": "aspect_meaning",
                "normalized_statement": "Within a modern psychological frame, the opposition is interpreted symbolically.",
                "tradition_tags": ["modern", "psychological_astrology"],
                "applies_to": ["natal", "Moon-Saturn opposition"],
                "scope": "modern psychological practitioner interpretation",
                "confidence_status": "qualified",
                "support_status": "tradition_bounded",
                "cautions": ["Do not infer literal biography."],
                "source_refs": ["source:practitioner"],
                "source_locator_refs": ["section"],
                "source_admission_mode": "claim_eligible",
                "citation_ready": True,
                "source_provenance": [
                    {
                        "source_id": "source:practitioner",
                        "title": "Practitioner article",
                        "author_or_org": "Example Author",
                        "source_role": "PRACTITIONER_REFERENCE",
                        "admission_status": ["CLAIM_ELIGIBLE"],
                        "locator": "section",
                        "edition": None,
                        "immutable_revision": None,
                        "publication_or_release_date": "2020-01-01",
                        "license_status": "verified_proprietary_or_restricted",
                        "copyright_status": "copyrighted",
                    }
                ],
                "conflict_group_ids": ["conflict:scope"],
            }
        ],
        "conflicts": [
            {
                "conflict_group_id": "conflict:scope",
                "conflict_class": ["scope_difference"],
                "resolution_status": "scope_separated",
                "resolution_note": "Keep symbolic scope separate from literal biography.",
                "selected_claim_refs": ["claim:modern"],
                "external_claim_refs": ["claim:historical"],
            }
        ],
        "guardrails": ["This does not prove trauma."],
        "excluded": [],
        "synthesis_provenance": {
            "l2_fact_refs": ["fact:moon-saturn-opposition"],
            "l3_policy_refs": ["policy:major-aspect-orb-v1"],
            "claim_refs": ["claim:modern"],
            "conflict_group_refs": ["conflict:scope"],
        },
    }


def codes(data, registries=None):
    return {error["code"] for error in validate_query_resolution(data, registries)}


class QueryResolutionValidatorTests(unittest.TestCase):
    def test_valid_resolution(self):
        self.assertEqual(validate_query_resolution(resolved_resolution(), {"saturn-moon-major-aspects-research-v1"}), [])

    def test_schema_name_invalid(self):
        data = resolved_resolution(); data["schema_name"] = "x"
        self.assertIn("SCHEMA_NAME_INVALID", codes(data))

    def test_production_guard(self):
        data = resolved_resolution(); data["production_routable"] = True
        self.assertIn("PRODUCTION_ROUTABLE_FORBIDDEN", codes(data))

    def test_private_motive_cannot_resolve(self):
        data = resolved_resolution(); data["question_risk_class"] = "private_motive_inference"
        self.assertIn("RISK_CLASS_CANNOT_RESOLVE", codes(data))

    def test_clinical_request_cannot_resolve(self):
        data = resolved_resolution(); data["question_risk_class"] = "clinical_or_diagnostic"
        self.assertIn("RISK_CLASS_CANNOT_RESOLVE", codes(data))

    def test_high_stakes_request_cannot_resolve(self):
        data = resolved_resolution(); data["question_risk_class"] = "high_stakes_external_outcome"
        self.assertIn("RISK_CLASS_CANNOT_RESOLVE", codes(data))

    def test_unknown_registry_rejected(self):
        self.assertIn("TARGET_REGISTRY_UNKNOWN", codes(resolved_resolution(), {"other"}))

    def test_route_query_id_must_match(self):
        data = resolved_resolution(); data["route"]["query_id"] = "x"
        self.assertIn("ROUTE_QUERY_ID_MISMATCH", codes(data))

    def test_missing_l2_fact_refs_rejected(self):
        data = resolved_resolution(); data["route"]["l2_fact_refs"] = []
        self.assertIn("ROUTE_L2_REFS_REQUIRED", codes(data))

    def test_missing_l3_policy_refs_rejected(self):
        data = resolved_resolution(); data["route"]["l3_policy_refs"] = []
        self.assertIn("ROUTE_L3_REFS_REQUIRED", codes(data))

    def test_reference_only_opt_in_requires_justification(self):
        data = resolved_resolution(); data["route"]["allow_reference_only_qualified"] = True
        self.assertIn("REFERENCE_ONLY_JUSTIFICATION_REQUIRED", codes(data))

    def test_user_text_span_must_exist_in_question(self):
        data = resolved_resolution(); data["routing_assumptions"][0]["evidence_spans"] = ["not in question"]
        self.assertIn("EVIDENCE_SPAN_NOT_IN_QUESTION", codes(data))

    def test_semantic_route_field_requires_provenance(self):
        data = resolved_resolution()
        data["routing_assumptions"] = [item for item in data["routing_assumptions"] if item["field"] != "tradition_tags_any"]
        self.assertIn("ROUTE_FIELD_UNGROUNDED", codes(data))

    def test_needs_clarification_requires_unresolved_slot(self):
        data = resolved_resolution()
        data["resolution_status"] = "needs_clarification"
        data["route"] = None
        data["unresolved_slots"] = []
        data["clarification_question"] = "Which tradition?"
        self.assertIn("UNRESOLVED_SLOTS_REQUIRED", codes(data))

    def test_needs_clarification_allows_material_slot(self):
        data = resolved_resolution()
        data["resolution_status"] = "needs_clarification"
        data["route"] = None
        data["unresolved_slots"] = ["tradition"]
        data["clarification_question"] = "Which tradition?"
        self.assertNotIn("UNRESOLVED_SLOTS_REQUIRED", codes(data))
        self.assertNotIn("ROUTE_FORBIDDEN_WHEN_UNRESOLVED", codes(data))

    def test_unsupported_requires_reason(self):
        data = resolved_resolution()
        data["resolution_status"] = "unsupported"
        data["route"] = None
        data["question_risk_class"] = "clinical_or_diagnostic"
        data["unresolved_slots"] = []
        data.pop("unsupported_reason", None)
        self.assertIn("UNSUPPORTED_REASON_REQUIRED", codes(data))

    def test_unsupported_high_risk_does_not_trigger_resolved_gate(self):
        data = resolved_resolution()
        data["resolution_status"] = "unsupported"
        data["route"] = None
        data["question_risk_class"] = "private_motive_inference"
        data["unsupported_reason"] = "private-state inference is outside this routing contract"
        data["unresolved_slots"] = []
        self.assertNotIn("RISK_CLASS_CANNOT_RESOLVE", codes(data))


class SynthesisEnvelopeTests(unittest.TestCase):
    def test_ready_for_l5(self):
        self.assertEqual(compose_synthesis(resolved_resolution(), bundle_fixture())["synthesis_status"], "ready_for_l5")

    def test_unresolved_resolution_blocks(self):
        resolution = resolved_resolution(); resolution["resolution_status"] = "needs_clarification"; resolution["route"] = None
        self.assertEqual(compose_synthesis(resolution, bundle_fixture())["synthesis_status"], "blocked_resolution_not_resolved")

    def test_query_id_mismatch_blocks(self):
        bundle = bundle_fixture(); bundle["query_id"] = "x"
        self.assertEqual(compose_synthesis(resolved_resolution(), bundle)["synthesis_status"], "blocked_query_mismatch")

    def test_registry_mismatch_blocks(self):
        bundle = bundle_fixture(); bundle["registry_record_id"] = "x"
        self.assertEqual(compose_synthesis(resolved_resolution(), bundle)["synthesis_status"], "blocked_registry_mismatch")

    def test_l2_provenance_mismatch_blocks(self):
        bundle = bundle_fixture(); bundle["synthesis_provenance"]["l2_fact_refs"] = []
        self.assertEqual(compose_synthesis(resolved_resolution(), bundle)["synthesis_status"], "blocked_provenance_mismatch")

    def test_claim_provenance_mismatch_blocks(self):
        bundle = bundle_fixture(); bundle["synthesis_provenance"]["claim_refs"] = []
        self.assertEqual(compose_synthesis(resolved_resolution(), bundle)["synthesis_status"], "blocked_provenance_mismatch")

    def test_no_match_yields_no_supported_claims(self):
        bundle = bundle_fixture()
        bundle["retrieval_status"] = "no_match"
        bundle["selected_claim_ids"] = []
        bundle["claims"] = []
        bundle["conflicts"] = []
        bundle["synthesis_provenance"]["claim_refs"] = []
        bundle["synthesis_provenance"]["conflict_group_refs"] = []
        result = compose_synthesis(resolved_resolution(), bundle)
        self.assertEqual(result["synthesis_status"], "no_supported_claims")
        self.assertEqual(result["synthesis_units"], [])

    def test_provenance_incomplete_blocks(self):
        bundle = bundle_fixture(); bundle["retrieval_status"] = "provenance_incomplete"
        self.assertEqual(compose_synthesis(resolved_resolution(), bundle)["synthesis_status"], "blocked_provenance_incomplete")

    def test_cautions_preserved(self):
        result = compose_synthesis(resolved_resolution(), bundle_fixture())
        self.assertEqual(result["synthesis_units"][0]["cautions"], ["Do not infer literal biography."])

    def test_conflict_external_claim_preserved(self):
        result = compose_synthesis(resolved_resolution(), bundle_fixture())
        self.assertEqual(result["conflicts"][0]["external_claim_refs"], ["claim:historical"])
        self.assertTrue(any("conflicts" in disclosure for disclosure in result["required_disclosures"]))

    def test_guardrails_preserved(self):
        self.assertEqual(compose_synthesis(resolved_resolution(), bundle_fixture())["guardrails"], ["This does not prove trauma."])

    def test_citation_locator_preserved(self):
        self.assertEqual(compose_synthesis(resolved_resolution(), bundle_fixture())["citation_units"][0]["locator"], "section")

    def test_statement_hash_is_stable(self):
        result = compose_synthesis(resolved_resolution(), bundle_fixture())
        statement = bundle_fixture()["claims"][0]["normalized_statement"]
        self.assertEqual(result["synthesis_units"][0]["statement_sha256"], hashlib.sha256(statement.encode("utf-8")).hexdigest())

    def test_reference_only_presence_requires_disclosure(self):
        bundle = bundle_fixture(); bundle["claims"][0]["source_admission_mode"] = "qualified_reference_only"
        result = compose_synthesis(resolved_resolution(), bundle)
        self.assertTrue(any("REFERENCE_ONLY provenance" in disclosure for disclosure in result["required_disclosures"]))

    def test_missing_locator_blocks(self):
        bundle = bundle_fixture(); bundle["claims"][0]["source_provenance"][0]["locator"] = ""
        self.assertEqual(compose_synthesis(resolved_resolution(), bundle)["synthesis_status"], "blocked_provenance_incomplete")

    def test_duplicate_citation_is_deduplicated(self):
        bundle = bundle_fixture()
        second = copy.deepcopy(bundle["claims"][0])
        second["claim_id"] = "claim:modern2"
        bundle["claims"].append(second)
        bundle["selected_claim_ids"].append("claim:modern2")
        bundle["synthesis_provenance"]["claim_refs"].append("claim:modern2")
        result = compose_synthesis(resolved_resolution(), bundle)
        self.assertEqual(result["synthesis_status"], "ready_for_l5")
        self.assertEqual(len(result["citation_units"]), 1)


if __name__ == "__main__":
    unittest.main()
