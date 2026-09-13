from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_ROOT = ROOT / "schemas" / "astrology"


class AstrologyOrchestrationContractTests(unittest.TestCase):
    def test_request_schema_is_closed_world_and_bounded_to_natal_transit(self):
        data = json.loads((SCHEMA_ROOT / "ASTROLOGY_READING_REQUEST_V1.schema.json").read_text(encoding="utf-8"))
        self.assertEqual("ASTROLOGY_READING_REQUEST_V1.schema.json", data["$id"])
        self.assertFalse(data["additionalProperties"])
        self.assertEqual(["natal", "transit"], data["properties"]["reading_mode"]["enum"])
        self.assertEqual(
            ["Whole Sign", "Placidus"],
            data["properties"]["birth"]["properties"]["house_system"]["enum"],
        )
        self.assertNotIn("synastry", json.dumps(data))
        self.assertNotIn("solar_return", json.dumps(data))

    def test_interpretation_request_schema_is_closed_world_evidence_selection(self):
        data = json.loads((SCHEMA_ROOT / "ASTROLOGY_INTERPRETATION_REQUEST_V1.schema.json").read_text(encoding="utf-8"))
        self.assertEqual("ASTROLOGY_INTERPRETATION_REQUEST_V1.schema.json", data["$id"])
        self.assertFalse(data["additionalProperties"])
        self.assertIn("fact_refs", data["required"])
        self.assertIn("claim_requests", data["required"])
        self.assertNotIn("final_interpretation", data["properties"])
        self.assertNotIn("synastry", json.dumps(data))
        self.assertNotIn("solar_return", json.dumps(data))

    def test_output_draft_schema_is_closed_world_and_requires_pre_send_gate(self):
        data = json.loads((SCHEMA_ROOT / "ASTROLOGY_OUTPUT_DRAFT_V1.schema.json").read_text(encoding="utf-8"))
        self.assertEqual("ASTROLOGY_OUTPUT_DRAFT_V1.schema.json", data["$id"])
        self.assertFalse(data["additionalProperties"])
        self.assertIn("conclusion", data["required"])
        self.assertIn("evidence", data["required"])
        self.assertIn("pre_send_attestations", data["required"])
        properties = data["properties"]["pre_send_attestations"]["properties"]
        self.assertEqual({True}, {row["const"] for row in properties.values()})
        self.assertNotIn("synastry", json.dumps(data))
        self.assertNotIn("solar_return", json.dumps(data))

    def test_production_manifest_admits_composition_only_orchestrator(self):
        data = json.loads((ROOT / "ASTROLOGY_PRODUCTION_ADMISSION_V1.json").read_text(encoding="utf-8"))
        orchestration = data["orchestration"]
        self.assertEqual("astrology-production-orchestrator-v1", orchestration["orchestrator_id"])
        self.assertEqual("tools/astrology_orchestrator.py", orchestration["runtime_owner"])
        self.assertEqual("schemas/astrology/ASTROLOGY_READING_REQUEST_V1.schema.json", orchestration["request_schema"])
        self.assertEqual("composition_only", orchestration["authority"])
        self.assertTrue(orchestration["runtime_gate_required_for_every_generated_bundle"])
        self.assertEqual("READING_RECORD.md", orchestration["reading_record_bridge"])
        self.assertEqual("external_only", orchestration["reading_record_storage"])
        self.assertFalse(data["ordinary_auto_routing"])
        self.assertIn("synastry", data["unsupported_scopes"])
        self.assertIn("solar_return", data["unsupported_scopes"])

    def test_production_manifest_admits_evidence_packaging_handoff_only(self):
        data = json.loads((ROOT / "ASTROLOGY_PRODUCTION_ADMISSION_V1.json").read_text(encoding="utf-8"))
        handoff = data["orchestration"]["interpretation_handoff"]
        self.assertEqual("astrology-interpretation-handoff-v1", handoff["adapter_id"])
        self.assertEqual("tools/astrology_interpretation_handoff.py", handoff["runtime_owner"])
        self.assertEqual("schemas/astrology/ASTROLOGY_INTERPRETATION_REQUEST_V1.schema.json", handoff["request_schema"])
        self.assertEqual("evidence_packaging_only", handoff["authority"])
        self.assertTrue(handoff["requires_admitted_reading_run"])
        self.assertTrue(handoff["requires_registry_production_admission"])
        self.assertTrue(handoff["requires_source_production_admission"])
        self.assertTrue(handoff["preserve_registered_conflicts"])
        self.assertFalse(handoff["final_prose_authority"])
        self.assertEqual("ASTROLOGY.md", handoff["final_method_owner"])
        self.assertEqual("CHATGPT_OUTPUT.md", handoff["final_output_owner"])

    def test_production_manifest_admits_output_guard_without_semantic_authority(self):
        data = json.loads((ROOT / "ASTROLOGY_PRODUCTION_ADMISSION_V1.json").read_text(encoding="utf-8"))
        output = data["orchestration"]["output_delivery"]
        self.assertEqual("astrology-output-guard-v1", output["adapter_id"])
        self.assertEqual("tools/astrology_output_guard.py", output["runtime_owner"])
        self.assertEqual("schemas/astrology/ASTROLOGY_OUTPUT_DRAFT_V1.schema.json", output["draft_schema"])
        self.assertEqual("provenance_and_pre_send_validation_only", output["authority"])
        self.assertTrue(output["requires_admitted_interpretation_handoff"])
        self.assertTrue(output["requires_all_fact_refs_selected_in_handoff"])
        self.assertTrue(output["requires_all_claim_refs_selected_in_handoff"])
        self.assertTrue(output["requires_pre_send_attestations"])
        self.assertFalse(output["semantic_interpretation_authority"])
        self.assertFalse(output["final_text_authority"])

    def test_production_manifest_admits_composition_only_end_to_end_pipeline(self):
        data = json.loads((ROOT / "ASTROLOGY_PRODUCTION_ADMISSION_V1.json").read_text(encoding="utf-8"))
        pipeline = data["orchestration"]["end_to_end_pipeline"]
        self.assertEqual("astrology-production-reading-pipeline-v1", pipeline["pipeline_id"])
        self.assertEqual("tools/astrology_reading_pipeline.py", pipeline["runtime_owner"])
        self.assertEqual("composition_only", pipeline["authority"])
        self.assertEqual("external_only", pipeline["reading_record_storage"])
        self.assertFalse(pipeline["semantic_selection_authority"])
        self.assertFalse(pipeline["final_text_authority"])

    def test_machine_index_exposes_complete_pipeline_without_changing_activation(self):
        data = json.loads((ROOT / "PLAYBOOK_INDEX.json").read_text(encoding="utf-8"))
        rows = {row["id"]: row for row in data["capabilities"]}
        row = rows["method.astrology"]
        self.assertEqual("explicit-request-only", row["activation"])
        self.assertEqual("schemas/astrology/ASTROLOGY_READING_REQUEST_V1.schema.json", row["request_schema"])
        self.assertEqual("tools/astrology_orchestrator.py", row["orchestrator"])
        self.assertEqual("schemas/astrology/ASTROLOGY_INTERPRETATION_REQUEST_V1.schema.json", row["interpretation_request_schema"])
        self.assertEqual("tools/astrology_interpretation_handoff.py", row["interpretation_handoff"])
        self.assertEqual("schemas/astrology/ASTROLOGY_OUTPUT_DRAFT_V1.schema.json", row["output_draft_schema"])
        self.assertEqual("tools/astrology_output_guard.py", row["output_guard"])
        self.assertEqual("tools/astrology_reading_pipeline.py", row["end_to_end_pipeline"])
        self.assertEqual("tools/astrology_runtime.py", row["runtime"])

    def test_orchestrator_is_composition_not_interpretation_or_storage_owner(self):
        text = (ROOT / "tools" / "astrology_orchestrator.py").read_text(encoding="utf-8")
        self.assertIn('"authority": "composition_only"', text)
        self.assertIn('"storage_policy": "external_only"', text)
        self.assertIn('"complete_reading_record": False', text)
        self.assertIn("gate_bundle", text)
        self.assertNotIn("synastry", text)
        self.assertNotIn("solar_return", text)

    def test_interpretation_handoff_is_not_semantic_or_final_prose_authority(self):
        text = (ROOT / "tools" / "astrology_interpretation_handoff.py").read_text(encoding="utf-8")
        self.assertIn('"authority": "evidence_packaging_only"', text)
        self.assertIn('"final_prose_authority": False', text)
        self.assertIn('"method_owner": "ASTROLOGY.md"', text)
        self.assertIn('"output_owner": "CHATGPT_OUTPUT.md"', text)
        self.assertIn("admitted_research_registries", text)
        self.assertIn("forbidden_source_admission", text)
        self.assertNotIn("synastry", text)
        self.assertNotIn("solar_return", text)

    def test_output_guard_and_pipeline_do_not_gain_semantic_authority(self):
        guard = (ROOT / "tools" / "astrology_output_guard.py").read_text(encoding="utf-8")
        pipeline = (ROOT / "tools" / "astrology_reading_pipeline.py").read_text(encoding="utf-8")
        self.assertIn('"authority": "provenance_and_pre_send_validation_only"', guard)
        self.assertIn('"semantic_interpretation_authored": False', guard)
        self.assertIn('"final_text_authored": False', guard)
        self.assertIn('"authority": "composition_only"', pipeline)
        self.assertIn('"semantic_selection_authored": False', pipeline)
        self.assertIn('"final_text_authored": False', pipeline)
        self.assertNotIn("synastry", guard)
        self.assertNotIn("solar_return", guard)
        self.assertNotIn("synastry", pipeline)
        self.assertNotIn("solar_return", pipeline)


if __name__ == "__main__":
    unittest.main()
