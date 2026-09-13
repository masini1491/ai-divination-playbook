from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUEST_SCHEMA = ROOT / "ASTROLOGY_TYPED_EVIDENCE_SELECTION_REQUEST_V1.schema.json"
SELECTION_SCHEMA = ROOT / "ASTROLOGY_TYPED_EVIDENCE_SELECTION_V1.schema.json"
MANIFEST = ROOT / "ASTROLOGY_PRODUCTION_ADMISSION_V1.json"
INDEX = ROOT / "PLAYBOOK_INDEX.json"
RESEARCH_QUERY_SCHEMA = ROOT / "references" / "astrology" / "astrology_query_resolution.schema.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class AstrologyEvidenceSelectorContractTests(unittest.TestCase):
    def test_request_schema_is_closed_world_typed_contract(self):
        schema = load(REQUEST_SCHEMA)
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(
            "astrology_typed_evidence_selection_request",
            schema["properties"]["schema_name"]["const"],
        )
        self.assertEqual("1.0.0", schema["properties"]["schema_version"]["const"])
        self.assertIn("fact_selectors", schema["required"])
        self.assertIn("claim_selectors", schema["required"])
        self.assertNotIn("fact_refs", schema["properties"])
        self.assertNotIn("claim_id", schema["properties"])

    def test_selection_schema_declares_narrow_authority(self):
        schema = load(SELECTION_SCHEMA)
        self.assertFalse(schema["additionalProperties"])
        selector = schema["properties"]["selector"]["properties"]
        self.assertEqual("deterministic_evidence_selection_only", selector["authority"]["const"])
        self.assertFalse(selector["natural_language_understanding_authority"]["const"])
        self.assertFalse(selector["semantic_meaning_authority"]["const"])
        self.assertFalse(selector["source_admission_authority"]["const"])
        self.assertFalse(selector["final_prose_authority"]["const"])

    def test_manifest_admits_selector_without_promoting_research_query_resolution(self):
        manifest = load(MANIFEST)
        selector = manifest["orchestration"]["typed_evidence_selection"]
        self.assertEqual("astrology-typed-evidence-selector-v1", selector["selector_id"])
        self.assertEqual("deterministic_evidence_selection_only", selector["authority"])
        self.assertTrue(selector["requires_explicit_typed_selectors"])
        self.assertEqual("fail_closed", selector["ambiguity_policy"])
        self.assertFalse(selector["free_text_query_resolution"])
        self.assertFalse(selector["natural_language_understanding_authority"])
        self.assertFalse(selector["semantic_meaning_authority"])
        self.assertFalse(selector["source_admission_authority"])
        self.assertFalse(selector["final_prose_authority"])
        self.assertFalse(selector["research_routing_contract_promoted"])

        research = load(RESEARCH_QUERY_SCHEMA)
        self.assertEqual("REFERENCE-ONLY", research["properties"]["record_status"]["const"])
        self.assertFalse(research["properties"]["production_routable"]["const"])

    def test_index_publishes_all_selector_local_paths(self):
        index = load(INDEX)
        astrology = next(row for row in index["capabilities"] if row["id"] == "method.astrology")
        self.assertEqual(
            "ASTROLOGY_TYPED_EVIDENCE_SELECTION_REQUEST_V1.schema.json",
            astrology["typed_evidence_selection_request_schema"],
        )
        self.assertEqual(
            "ASTROLOGY_TYPED_EVIDENCE_SELECTION_V1.schema.json",
            astrology["typed_evidence_selection_schema"],
        )
        self.assertEqual("tools/astrology_evidence_selector.py", astrology["evidence_selector"])
        for key in (
            "typed_evidence_selection_request_schema",
            "typed_evidence_selection_schema",
            "evidence_selector",
        ):
            self.assertTrue((ROOT / astrology[key]).is_file())

    def test_selector_admission_does_not_expand_astrology_method_scope(self):
        manifest = load(MANIFEST)
        self.assertEqual(["natal", "transit"], manifest["reading_modes"])
        self.assertIn("synastry", manifest["unsupported_scopes"])
        self.assertIn("composite", manifest["unsupported_scopes"])
        self.assertIn("solar_return", manifest["unsupported_scopes"])
        self.assertIn("raw_birth_data_model_calculation", manifest["unsupported_scopes"])


if __name__ == "__main__":
    unittest.main()
