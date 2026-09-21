#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from validate_interpretation_claim_registry import validate_registry

SCHEMA_NAME = "interpretation_claim_registry"
SCHEMA_VERSION = "0.2.0-research"
LEGACY_SCHEMA_VERSION = "0.1.0-research"


def legacy_domicile_fixture():
    return {
        "record_status": "REFERENCE-ONLY",
        "record_kind": "interpretation_claim_family_registry",
        "record_id": "fixture-domicile",
        "sources": [
            {"source_id": "source:a", "source_role": "PRIMARY_TEXT", "admission_state": "CLAIM_ELIGIBLE", "storage_mode": "metadata_locator_normalized_paraphrase", "independence_status": "primary_witness"},
            {"source_id": "source:b", "source_role": ["PRACTITIONER_REFERENCE", "REFERENCE_IMPLEMENTATION"], "admission_state": "REFERENCE_ONLY", "storage_mode": "metadata_revision_normalized_paraphrase", "independence_status": "derivative_practitioner_synthesis", "upstream_source_refs": ["source:a"]},
        ],
        "claims": [
            {"claim_id": "claim:a", "claim_type": "policy_configuration", "layer": "L3", "statement": "configuration", "source_refs": ["source:a"], "confidence": "supported"},
            {"claim_id": "claim:b", "claim_type": "condition_meaning", "layer": "L4", "statement": "meaning", "source_refs": ["source:b"], "confidence": "qualified"},
        ],
        "conflict_groups": [],
        "research_result": {"production_authority_granted": False, "scientific_predictive_validity_claimed": False},
    }


def legacy_v01_fixture():
    data = canonical_fixture()
    data["schema_version"] = LEGACY_SCHEMA_VERSION
    for claim in data["claims"]:
        claim.pop("tradition_context_refs", None)
        claim.pop("historical_context_refs", None)
        claim.pop("meta_context_refs", None)
    return data


def canonical_fixture():
    return {
        "schema_name": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "record_status": "REFERENCE-ONLY",
        "record_kind": "interpretation_claim_family_registry",
        "record_id": "fixture-v02",
        "production_routable": False,
        "sources": [
            {"source_id": "source:a", "source_role": "PRIMARY_TEXT", "admission_status": ["CLAIM_ELIGIBLE"], "storage_mode": ["metadata_plus_locator", "normalized_paraphrase"], "independence_status": "independent_evidence"},
            {"source_id": "source:b", "source_role": "SCHOLARLY_SECONDARY", "admission_status": ["CLAIM_ELIGIBLE"], "storage_mode": ["metadata_plus_locator", "normalized_paraphrase"], "independence_status": "independent_evidence"},
            {"source_id": "source:c", "source_role": "REFERENCE_IMPLEMENTATION", "admission_status": ["REFERENCE_ONLY"], "storage_mode": ["metadata_plus_locator", "normalized_paraphrase"], "independence_status": "shared_upstream", "upstream_source_refs": ["source:a"]},
        ],
        "claims": [
            {
                "claim_id": "claim:a",
                "layer": "L4",
                "claim_type": "historical_doctrine",
                "normalized_statement": "history",
                "source_refs": ["source:a", "source:b"],
                "confidence_status": "supported",
                "support_status": "multi_source_supported",
                "conflict_group_ids": ["conflict:a"],
                "tradition_context_refs": ["lineage:hellenistic:ptolemaic"],
            },
            {
                "claim_id": "claim:c",
                "layer": "L4",
                "claim_type": "aspect_meaning",
                "normalized_statement": "meaning",
                "source_refs": ["source:c"],
                "confidence_status": "qualified",
                "support_status": "tradition_bounded",
                "conflict_group_ids": ["conflict:a"],
                "tradition_context_refs": [],
                "historical_context_refs": ["context:early_modern"],
                "meta_context_refs": ["meta:history_of_astrology"],
            },
        ],
        "conflict_groups": [{"conflict_group_id": "conflict:a", "claim_refs": ["claim:a", "claim:c"]}],
        "privacy": {"contains_real_birth_data": False},
    }


class ClaimRegistryValidatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        here = Path(__file__).resolve().parent
        cls.taxonomy = json.loads((here / "tradition_taxonomy_example.json").read_text(encoding="utf-8"))

    def codes(self, data, taxonomy=None):
        return {item["code"] for item in validate_registry(data, self.taxonomy if taxonomy is None else taxonomy)}

    def test_unversioned_legacy_fixture_valid(self):
        self.assertEqual(validate_registry(legacy_domicile_fixture()), [])

    def test_v01_versioned_fixture_remains_compatible_without_taxonomy(self):
        self.assertEqual(validate_registry(legacy_v01_fixture()), [])

    def test_v02_canonical_fixture_valid(self):
        self.assertEqual(validate_registry(canonical_fixture(), self.taxonomy), [])

    def test_v02_requires_taxonomy(self):
        self.assertIn("TAXONOMY_REQUIRED_FOR_REGISTRY_V2", {item["code"] for item in validate_registry(canonical_fixture())})

    def test_record_status_invalid(self):
        data = canonical_fixture(); data["record_status"] = "PRODUCTION"; self.assertIn("RECORD_STATUS_INVALID", self.codes(data))

    def test_schema_version_invalid(self):
        data = canonical_fixture(); data["schema_version"] = "9"; self.assertIn("SCHEMA_VERSION_UNSUPPORTED", self.codes(data))

    def test_versioned_requires_explicit_production_false(self):
        data = canonical_fixture(); data.pop("production_routable"); self.assertIn("PRODUCTION_ROUTABLE_EXPLICIT_FALSE_REQUIRED", self.codes(data))

    def test_real_birth_data_forbidden(self):
        data = canonical_fixture(); data["privacy"]["contains_real_birth_data"] = True; self.assertIn("REAL_BIRTH_DATA_FORBIDDEN", self.codes(data))

    def test_duplicate_source_id(self):
        data = canonical_fixture(); data["sources"].append(copy.deepcopy(data["sources"][0])); self.assertIn("SOURCE_ID_DUPLICATE", self.codes(data))

    def test_unknown_upstream_source(self):
        data = canonical_fixture(); data["sources"][2]["upstream_source_refs"] = ["source:nope"]; self.assertIn("UPSTREAM_SOURCE_REF_UNKNOWN", self.codes(data))

    def test_invalid_source_role(self):
        data = canonical_fixture(); data["sources"][0]["source_role"] = "BLOG"; self.assertIn("SOURCE_ROLE_INVALID", self.codes(data))

    def test_production_admission_forbidden(self):
        data = canonical_fixture(); data["sources"][0]["admission_status"] = ["PRODUCTION_ADMITTED"]; self.assertIn("PRODUCTION_ADMISSION_FORBIDDEN", self.codes(data))

    def test_versioned_rejects_admission_state_alias(self):
        data = canonical_fixture(); data["sources"][0]["admission_state"] = data["sources"][0].pop("admission_status"); self.assertIn("LEGACY_SOURCE_FIELD_FORBIDDEN", self.codes(data))

    def test_duplicate_claim_id(self):
        data = canonical_fixture(); data["claims"].append(copy.deepcopy(data["claims"][0])); self.assertIn("CLAIM_ID_DUPLICATE", self.codes(data))

    def test_invalid_claim_layer(self):
        data = canonical_fixture(); data["claims"][0]["layer"] = "L5"; self.assertIn("CLAIM_LAYER_INVALID", self.codes(data))

    def test_unknown_claim_source_ref(self):
        data = canonical_fixture(); data["claims"][0]["source_refs"] = ["source:nope", "source:b"]; self.assertIn("CLAIM_SOURCE_REF_UNKNOWN", self.codes(data))

    def test_unknown_claim_conflict_ref(self):
        data = canonical_fixture(); data["claims"][0]["conflict_group_ids"] = ["conflict:nope"]; self.assertIn("CLAIM_CONFLICT_REF_UNKNOWN", self.codes(data))

    def test_multi_source_requires_independent_roots(self):
        data = canonical_fixture(); data["claims"][0]["source_refs"] = ["source:a", "source:c"]; self.assertIn("MULTI_SOURCE_INDEPENDENCE_INSUFFICIENT", self.codes(data))

    def test_reference_only_cannot_self_promote_supported_claim(self):
        data = canonical_fixture(); data["claims"][1]["confidence_status"] = "supported"; data["claims"][1]["support_status"] = "single_source_supported"; self.assertIn("REFERENCE_ONLY_AUTHORITY_PROMOTION", self.codes(data))

    def test_v02_requires_explicit_tradition_context_array(self):
        data = canonical_fixture(); data["claims"][0].pop("tradition_context_refs"); self.assertIn("TYPED_CONTEXT_FIELD_REQUIRED", self.codes(data))

    def test_v02_allows_explicit_empty_tradition_context_array(self):
        data = canonical_fixture(); data["claims"][0]["tradition_context_refs"] = []; self.assertNotIn("TYPED_CONTEXT_FIELD_REQUIRED", self.codes(data))

    def test_v02_rejects_unknown_tradition_context_ref(self):
        data = canonical_fixture(); data["claims"][0]["tradition_context_refs"] = ["lineage:nope"]; self.assertIn("TYPED_CONTEXT_REF_UNKNOWN", self.codes(data))

    def test_v02_rejects_meta_ref_in_tradition_array(self):
        data = canonical_fixture(); data["claims"][0]["tradition_context_refs"] = ["meta:history_of_astrology"]; self.assertIn("TYPED_CONTEXT_DIMENSION_INVALID", self.codes(data))

    def test_v02_rejects_duplicate_tradition_ref(self):
        data = canonical_fixture(); data["claims"][0]["tradition_context_refs"] = ["lineage:hellenistic:ptolemaic", "lineage:hellenistic:ptolemaic"]; self.assertIn("TYPED_CONTEXT_REF_DUPLICATE", self.codes(data))

    def test_v02_validates_historical_context_dimension(self):
        data = canonical_fixture(); data["claims"][1]["historical_context_refs"] = ["meta:history_of_astrology"]; self.assertIn("TYPED_CONTEXT_DIMENSION_INVALID", self.codes(data))

    def test_v02_validates_meta_context_dimension(self):
        data = canonical_fixture(); data["claims"][1]["meta_context_refs"] = ["context:early_modern"]; self.assertIn("TYPED_CONTEXT_DIMENSION_INVALID", self.codes(data))


class CurrentRegistryCompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        here = Path(__file__).resolve().parent
        cls.here = here
        cls.taxonomy = json.loads((here / "tradition_taxonomy_example.json").read_text(encoding="utf-8"))

    def test_current_registry_files_are_v02_and_validate(self):
        names = (
            "domicile_claim_family_registry.json",
            "saturn_moon_aspect_claim_family_registry.json",
            "planet_sign_composable_semantics_claim_family_registry.json",
        )
        for name in names:
            data = json.loads((self.here / name).read_text(encoding="utf-8"))
            self.assertEqual(data["schema_version"], SCHEMA_VERSION, name)
            self.assertEqual(validate_registry(data, self.taxonomy), [], name)


if __name__ == "__main__":
    unittest.main()
