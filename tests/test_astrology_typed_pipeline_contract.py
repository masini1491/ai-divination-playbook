from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_ROOT = ROOT / "schemas" / "astrology"
SCHEMA = SCHEMA_ROOT / "ASTROLOGY_TYPED_READING_PIPELINE_RUN_V1.schema.json"
LEGACY_SCHEMA = SCHEMA_ROOT / "ASTROLOGY_READING_PIPELINE_RUN_V1.schema.json"
MANIFEST = ROOT / "ASTROLOGY_PRODUCTION_ADMISSION_V1.json"
INDEX = ROOT / "PLAYBOOK_INDEX.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class AstrologyTypedPipelineContractTests(unittest.TestCase):
    def test_typed_pipeline_schema_is_closed_world_and_exposes_selection_stage(self):
        schema = load(SCHEMA)
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(
            "astrology_typed_reading_pipeline_run",
            schema["properties"]["schema_name"]["const"],
        )
        stages = schema["properties"]["stages"]
        self.assertFalse(stages["additionalProperties"])
        self.assertEqual(
            ["reading_run", "evidence_selection", "interpretation_handoff", "user_facing_output"],
            stages["required"],
        )
        pipeline = schema["properties"]["pipeline"]["properties"]
        self.assertEqual("composition_only", pipeline["authority"]["const"])
        self.assertFalse(pipeline["free_text_query_resolution"]["const"])
        self.assertFalse(pipeline["semantic_selection_authored"]["const"])
        self.assertFalse(pipeline["final_text_authored"]["const"])

    def test_legacy_exact_reference_pipeline_contract_is_unchanged(self):
        legacy = load(LEGACY_SCHEMA)
        self.assertEqual("astrology_reading_pipeline_run", legacy["properties"]["schema_name"]["const"])
        self.assertEqual(
            ["reading_run", "interpretation_handoff", "user_facing_output"],
            legacy["properties"]["stages"]["required"],
        )
        self.assertNotIn("evidence_selection", legacy["properties"]["stages"]["properties"])

    def test_manifest_admits_typed_pipeline_without_new_semantic_authority(self):
        manifest = load(MANIFEST)
        typed = manifest["orchestration"]["typed_end_to_end_pipeline"]
        self.assertEqual("astrology-production-typed-reading-pipeline-v1", typed["pipeline_id"])
        self.assertEqual("composition_only", typed["authority"])
        self.assertTrue(typed["legacy_exact_reference_pipeline_preserved"])
        self.assertFalse(typed["free_text_query_resolution"])
        self.assertFalse(typed["semantic_selection_authority"])
        self.assertFalse(typed["final_text_authority"])
        self.assertEqual(
            [
                "astrology_reading_run@1.0.0",
                "astrology_typed_evidence_selection@1.0.0",
                "astrology_interpretation_handoff@1.0.0",
                "astrology_user_facing_output@1.0.0",
            ],
            typed["stages"],
        )

    def test_index_publishes_typed_pipeline_local_paths(self):
        index = load(INDEX)
        astrology = next(row for row in index["capabilities"] if row["id"] == "method.astrology")
        self.assertEqual(
            "schemas/astrology/ASTROLOGY_TYPED_READING_PIPELINE_RUN_V1.schema.json",
            astrology["typed_pipeline_run_schema"],
        )
        self.assertEqual(
            "tools/astrology_typed_reading_pipeline.py",
            astrology["typed_end_to_end_pipeline"],
        )
        self.assertTrue((ROOT / astrology["typed_pipeline_run_schema"]).is_file())
        self.assertTrue((ROOT / astrology["typed_end_to_end_pipeline"]).is_file())


if __name__ == "__main__":
    unittest.main()
