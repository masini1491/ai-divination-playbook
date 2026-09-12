#!/usr/bin/env python3
from __future__ import annotations
import copy
import json
import unittest
from pathlib import Path

from validate_interpretation_claim_registry import validate_registry

def domicile_fixture():
    return {
        "record_status":"REFERENCE-ONLY","record_kind":"interpretation_claim_family_registry","record_id":"fixture-domicile",
        "sources":[
            {"source_id":"source:a","source_role":"PRIMARY_TEXT","admission_state":"CLAIM_ELIGIBLE","storage_mode":"metadata_locator_normalized_paraphrase","independence_status":"primary_witness"},
            {"source_id":"source:b","source_role":["PRACTITIONER_REFERENCE","REFERENCE_IMPLEMENTATION"],"admission_state":"REFERENCE_ONLY","storage_mode":"metadata_revision_normalized_paraphrase","independence_status":"derivative_practitioner_synthesis","upstream_source_refs":["source:a"]}
        ],
        "claims":[
            {"claim_id":"claim:a","claim_type":"policy_configuration","layer":"L3","statement":"configuration","source_refs":["source:a"],"confidence":"supported"},
            {"claim_id":"claim:b","claim_type":"condition_meaning","layer":"L4","statement":"meaning","source_refs":["source:b"],"confidence":"qualified"}
        ],
        "conflict_groups":[],
        "research_result":{"production_authority_granted":False,"scientific_predictive_validity_claimed":False}
    }

def saturn_fixture():
    return {
        "record_status":"REFERENCE-ONLY","record_kind":"interpretation_claim_family_registry","record_id":"fixture-saturn","production_routable":False,
        "sources":[
            {"source_id":"source:a","source_role":"PRIMARY_TEXT","admission_status":["CLAIM_ELIGIBLE"],"storage_mode":["metadata_plus_locator","normalized_paraphrase"],"independence_status":"independent_evidence"},
            {"source_id":"source:b","source_role":"SCHOLARLY_SECONDARY","admission_status":["CLAIM_ELIGIBLE"],"storage_mode":["metadata_plus_locator","normalized_paraphrase"],"independence_status":"independent_evidence"},
            {"source_id":"source:c","source_role":"REFERENCE_IMPLEMENTATION","admission_status":["REFERENCE_ONLY"],"storage_mode":["metadata_plus_locator","normalized_paraphrase"],"independence_status":"shared_upstream","upstream_source_refs":["source:a"]}
        ],
        "claims":[
            {"claim_id":"claim:a","layer":"L4","claim_type":"historical_doctrine","normalized_statement":"history","source_refs":["source:a","source:b"],"confidence_status":"supported","support_status":"multi_source_supported","conflict_group_ids":["conflict:a"]},
            {"claim_id":"claim:c","layer":"L4","claim_type":"aspect_meaning","normalized_statement":"meaning","source_refs":["source:c"],"confidence_status":"qualified","support_status":"tradition_bounded","conflict_group_ids":["conflict:a"]}
        ],
        "conflict_groups":[{"conflict_group_id":"conflict:a","claim_refs":["claim:a","claim:c"]}],
        "privacy":{"contains_real_birth_data":False}
    }

def codes(data): return {x["code"] for x in validate_registry(data)}

class ClaimRegistryValidatorTests(unittest.TestCase):
    def test_domicile_style_fixture_valid(self): self.assertEqual(validate_registry(domicile_fixture()), [])
    def test_saturn_style_fixture_valid(self): self.assertEqual(validate_registry(saturn_fixture()), [])
    def test_record_status_invalid(self):
        d=saturn_fixture(); d["record_status"]="PRODUCTION"; self.assertIn("RECORD_STATUS_INVALID",codes(d))
    def test_record_kind_invalid(self):
        d=saturn_fixture(); d["record_kind"]="x"; self.assertIn("RECORD_KIND_INVALID",codes(d))
    def test_production_routable_forbidden(self):
        d=saturn_fixture(); d["production_routable"]=True; self.assertIn("PRODUCTION_ROUTABLE_FORBIDDEN",codes(d))
    def test_production_authority_forbidden(self):
        d=domicile_fixture(); d["research_result"]["production_authority_granted"]=True; self.assertIn("PRODUCTION_AUTHORITY_FORBIDDEN",codes(d))
    def test_scientific_validity_promotion_forbidden(self):
        d=domicile_fixture(); d["research_result"]["scientific_predictive_validity_claimed"]=True; self.assertIn("SCIENTIFIC_VALIDITY_PROMOTION_FORBIDDEN",codes(d))
    def test_real_birth_data_forbidden(self):
        d=saturn_fixture(); d["privacy"]["contains_real_birth_data"]=True; self.assertIn("REAL_BIRTH_DATA_FORBIDDEN",codes(d))
    def test_duplicate_source_id(self):
        d=saturn_fixture(); d["sources"].append(copy.deepcopy(d["sources"][0])); self.assertIn("SOURCE_ID_DUPLICATE",codes(d))
    def test_unknown_upstream_source(self):
        d=saturn_fixture(); d["sources"][2]["upstream_source_refs"]=["source:nope"]; self.assertIn("UPSTREAM_SOURCE_REF_UNKNOWN",codes(d))
    def test_upstream_self_reference(self):
        d=saturn_fixture(); d["sources"][2]["upstream_source_refs"]=["source:c"]; self.assertIn("UPSTREAM_SOURCE_SELF_REFERENCE",codes(d))
    def test_invalid_source_role(self):
        d=saturn_fixture(); d["sources"][0]["source_role"]="BLOG"; self.assertIn("SOURCE_ROLE_INVALID",codes(d))
    def test_invalid_admission_status(self):
        d=saturn_fixture(); d["sources"][0]["admission_status"]=["FOO"]; self.assertIn("ADMISSION_STATUS_INVALID",codes(d))
    def test_production_admission_forbidden(self):
        d=saturn_fixture(); d["sources"][0]["admission_status"]=["PRODUCTION_ADMITTED"]; self.assertIn("PRODUCTION_ADMISSION_FORBIDDEN",codes(d))
    def test_unverified_web_promotion_forbidden(self):
        d=saturn_fixture(); d["sources"][0]["source_role"]="UNVERIFIED_WEB_SOURCE"; d["sources"][0]["admission_status"]=["CLAIM_ELIGIBLE"]; self.assertIn("UNVERIFIED_WEB_PROMOTION_FORBIDDEN",codes(d))
    def test_invalid_storage_mode(self):
        d=saturn_fixture(); d["sources"][0]["storage_mode"]=["copy_everything"]; self.assertIn("STORAGE_MODE_INVALID",codes(d))
    def test_duplicate_claim_id(self):
        d=saturn_fixture(); d["claims"].append(copy.deepcopy(d["claims"][0])); self.assertIn("CLAIM_ID_DUPLICATE",codes(d))
    def test_invalid_claim_layer(self):
        d=saturn_fixture(); d["claims"][0]["layer"]="L5"; self.assertIn("CLAIM_LAYER_INVALID",codes(d))
    def test_claim_statement_required(self):
        d=saturn_fixture(); d["claims"][0].pop("normalized_statement"); self.assertIn("CLAIM_STATEMENT_REQUIRED",codes(d))
    def test_unknown_claim_source_ref(self):
        d=saturn_fixture(); d["claims"][0]["source_refs"]=["source:nope","source:b"]; self.assertIn("CLAIM_SOURCE_REF_UNKNOWN",codes(d))
    def test_unknown_claim_conflict_ref(self):
        d=saturn_fixture(); d["claims"][0]["conflict_group_ids"]=["conflict:nope"]; self.assertIn("CLAIM_CONFLICT_REF_UNKNOWN",codes(d))
    def test_unknown_conflict_claim_ref(self):
        d=saturn_fixture(); d["conflict_groups"][0]["claim_refs"]=["claim:nope"]; self.assertIn("CONFLICT_CLAIM_REF_UNKNOWN",codes(d))
    def test_multi_source_requires_two_sources(self):
        d=saturn_fixture(); d["claims"][0]["source_refs"]=["source:a"]; self.assertIn("MULTI_SOURCE_COUNT_INSUFFICIENT",codes(d))
    def test_multi_source_requires_independent_roots(self):
        d=saturn_fixture(); d["claims"][0]["source_refs"]=["source:a","source:c"]; self.assertIn("MULTI_SOURCE_INDEPENDENCE_INSUFFICIENT",codes(d))
    def test_reference_only_cannot_self_promote_supported_claim(self):
        d=saturn_fixture(); d["claims"][1]["confidence_status"]="supported"; d["claims"][1]["support_status"]="single_source_supported"; self.assertIn("REFERENCE_ONLY_AUTHORITY_PROMOTION",codes(d))
    def test_reference_only_qualified_claim_allowed(self): self.assertNotIn("REFERENCE_ONLY_AUTHORITY_PROMOTION",codes(saturn_fixture()))

class CurrentRegistryCompatibilityTests(unittest.TestCase):
    def test_current_registry_files_validate_when_present(self):
        here=Path(__file__).resolve().parent
        names=("domicile_claim_family_registry.json","saturn_moon_aspect_claim_family_registry.json")
        missing=[n for n in names if not (here/n).exists()]
        if missing: self.skipTest("current registry files not present in isolated unit-test environment")
        for name in names:
            data=json.loads((here/name).read_text(encoding="utf-8"))
            self.assertEqual(validate_registry(data), [], name)

if __name__=="__main__": unittest.main()
