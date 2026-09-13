from __future__ import annotations

import json
import unittest
from pathlib import Path

from tools.astrology_reading_pipeline import run_pipeline

ROOT = Path(__file__).resolve().parents[1]
READING = ROOT / "tests" / "fixtures" / "astrology_pipeline_reading_request_natal_v1.json"
INTERPRETATION = ROOT / "tests" / "fixtures" / "astrology_pipeline_interpretation_request_natal_v1.json"
OUTPUT = ROOT / "tests" / "fixtures" / "astrology_pipeline_output_draft_natal_v1.json"

SCHEMAS = {
    "reading_run": ROOT / "ASTROLOGY_READING_RUN_V1.schema.json",
    "interpretation_handoff": ROOT / "ASTROLOGY_INTERPRETATION_HANDOFF_V1.schema.json",
    "pipeline_run": ROOT / "ASTROLOGY_READING_PIPELINE_RUN_V1.schema.json",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class AstrologyRuntimeArtifactContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pipeline = run_pipeline(load(READING), load(INTERPRETATION), load(OUTPUT), repo_root=ROOT)

    def test_success_artifact_schemas_are_closed_world(self):
        expected = {
            "reading_run": ("ASTROLOGY_READING_RUN_V1.schema.json", "astrology_reading_run"),
            "interpretation_handoff": (
                "ASTROLOGY_INTERPRETATION_HANDOFF_V1.schema.json",
                "astrology_interpretation_handoff",
            ),
            "pipeline_run": (
                "ASTROLOGY_READING_PIPELINE_RUN_V1.schema.json",
                "astrology_reading_pipeline_run",
            ),
        }
        for key, path in SCHEMAS.items():
            with self.subTest(key=key):
                schema = load(path)
                expected_id, expected_name = expected[key]
                self.assertEqual(expected_id, schema["$id"])
                self.assertFalse(schema["additionalProperties"])
                self.assertEqual(expected_name, schema["properties"]["schema_name"]["const"])
                self.assertEqual("1.0.0", schema["properties"]["schema_version"]["const"])
                text = json.dumps(schema)
                self.assertNotIn("synastry", text)
                self.assertNotIn("solar_return", text)

    def test_runtime_top_level_shapes_match_declared_contracts(self):
        artifacts = {
            "reading_run": self.pipeline["stages"]["reading_run"],
            "interpretation_handoff": self.pipeline["stages"]["interpretation_handoff"],
            "pipeline_run": self.pipeline,
        }
        for key, artifact in artifacts.items():
            with self.subTest(key=key):
                schema = load(SCHEMAS[key])
                self.assertEqual(set(schema["required"]), set(artifact))
                self.assertEqual(schema["properties"]["schema_name"]["const"], artifact["schema_name"])
                self.assertEqual(schema["properties"]["schema_version"]["const"], artifact["schema_version"])

    def test_authority_constants_match_runtime(self):
        reading_schema = load(SCHEMAS["reading_run"])
        handoff_schema = load(SCHEMAS["interpretation_handoff"])
        pipeline_schema = load(SCHEMAS["pipeline_run"])
        reading = self.pipeline["stages"]["reading_run"]
        handoff = self.pipeline["stages"]["interpretation_handoff"]

        self.assertEqual(
            reading_schema["properties"]["orchestrator"]["properties"]["authority"]["const"],
            reading["orchestrator"]["authority"],
        )
        self.assertEqual(
            handoff_schema["properties"]["adapter"]["properties"]["authority"]["const"],
            handoff["adapter"]["authority"],
        )
        self.assertFalse(handoff["adapter"]["final_prose_authority"])
        self.assertEqual(
            pipeline_schema["properties"]["pipeline"]["properties"]["authority"]["const"],
            self.pipeline["pipeline"]["authority"],
        )
        self.assertFalse(self.pipeline["pipeline"]["semantic_selection_authored"])
        self.assertFalse(self.pipeline["pipeline"]["final_text_authored"])

    def test_manifest_and_index_publish_all_runtime_artifact_schemas(self):
        manifest = load(ROOT / "ASTROLOGY_PRODUCTION_ADMISSION_V1.json")
        index = load(ROOT / "PLAYBOOK_INDEX.json")
        row = {item["id"]: item for item in index["capabilities"]}["method.astrology"]
        orchestration = manifest["orchestration"]

        self.assertEqual("ASTROLOGY_READING_RUN_V1.schema.json", orchestration["run_schema"])
        self.assertEqual(orchestration["run_schema"], row["reading_run_schema"])
        self.assertEqual(
            "ASTROLOGY_INTERPRETATION_HANDOFF_V1.schema.json",
            orchestration["interpretation_handoff"]["handoff_schema"],
        )
        self.assertEqual(
            orchestration["interpretation_handoff"]["handoff_schema"],
            row["interpretation_handoff_schema"],
        )
        self.assertEqual(
            "ASTROLOGY_READING_PIPELINE_RUN_V1.schema.json",
            orchestration["end_to_end_pipeline"]["run_schema"],
        )
        self.assertEqual(orchestration["end_to_end_pipeline"]["run_schema"], row["pipeline_run_schema"])


if __name__ == "__main__":
    unittest.main()
