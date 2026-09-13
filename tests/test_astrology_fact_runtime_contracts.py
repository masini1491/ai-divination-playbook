from __future__ import annotations

import json
import unittest
from pathlib import Path

from tools.astrology_provider import build_natal_bundle
from tools.astrology_runtime import gate_bundle

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_ROOT = ROOT / "schemas" / "astrology"
FACT_SCHEMA = SCHEMA_ROOT / "ASTROLOGY_FACT_BUNDLE_V1.schema.json"
GATE_SCHEMA = SCHEMA_ROOT / "ASTROLOGY_RUNTIME_GATE_RESULT_V1.schema.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def natal_bundle() -> dict:
    return build_natal_bundle(
        local_datetime="1990-06-15T10:00:00",
        timezone_name="Asia/Tokyo",
        latitude=35.6762,
        longitude=139.6503,
        house_system="Whole Sign",
        subject_ref="contract-fixture",
        birth_time_certainty="exact",
    )


class AstrologyFactRuntimeContractTests(unittest.TestCase):
    def test_fact_bundle_schema_matches_runtime_minimum_contract(self):
        schema = load(FACT_SCHEMA)
        self.assertEqual("ASTROLOGY_FACT_BUNDLE_V1.schema.json", schema["$id"])
        self.assertEqual("astrology_fact_bundle", schema["properties"]["schema_name"]["const"])
        self.assertEqual("1.0.0", schema["properties"]["schema_version"]["const"])
        self.assertEqual(
            {
                "schema_name",
                "schema_version",
                "method",
                "reading_mode",
                "fact_source",
                "calculation_verification",
                "subject_ref",
                "birth_time_certainty",
                "configuration",
                "facts",
            },
            set(schema["required"]),
        )
        self.assertTrue(schema["additionalProperties"])
        self.assertNotIn("model_calculated", schema["properties"]["fact_source"]["enum"])
        self.assertNotIn("memory_inferred", schema["properties"]["fact_source"]["enum"])

    def test_provider_bundle_satisfies_declared_identity_and_required_shape(self):
        schema = load(FACT_SCHEMA)
        bundle = natal_bundle()
        self.assertTrue(set(schema["required"]).issubset(bundle))
        self.assertEqual(schema["properties"]["schema_name"]["const"], bundle["schema_name"])
        self.assertEqual(schema["properties"]["schema_version"]["const"], bundle["schema_version"])
        self.assertEqual(schema["properties"]["method"]["const"], bundle["method"])
        self.assertEqual({"objects", "houses", "aspects", "events"}, set(bundle["facts"]))

    def test_runtime_gate_result_contract_covers_admitted_and_rejected(self):
        schema = load(GATE_SCHEMA)
        admitted = gate_bundle(natal_bundle())
        self.assertEqual(set(schema["required"]).issubset(admitted), True)
        self.assertEqual("admitted", admitted["status"])
        self.assertTrue(admitted["interpretation_allowed"])
        self.assertEqual([], admitted["errors"])

        rejected_bundle = natal_bundle()
        rejected_bundle["fact_source"] = "model_calculated"
        rejected = gate_bundle(rejected_bundle)
        self.assertEqual("rejected", rejected["status"])
        self.assertFalse(rejected["interpretation_allowed"])
        self.assertTrue(rejected["errors"])
        self.assertEqual("FACT_SOURCE_FORBIDDEN", rejected["errors"][0]["code"])

    def test_manifest_and_index_publish_fact_and_gate_contracts(self):
        manifest = load(ROOT / "ASTROLOGY_PRODUCTION_ADMISSION_V1.json")
        index = load(ROOT / "PLAYBOOK_INDEX.json")
        method = {row["id"]: row for row in index["capabilities"]}["method.astrology"]

        self.assertEqual("astrology_fact_bundle@1.0.0", manifest["fact_bundle_schema"])
        self.assertEqual(
            "schemas/astrology/ASTROLOGY_FACT_BUNDLE_V1.schema.json",
            manifest["fact_bundle_schema_path"],
        )
        self.assertEqual(manifest["fact_bundle_schema_path"], method["fact_bundle_schema"])
        self.assertEqual("astrology_runtime_gate_result@1.0.0", manifest["runtime_gate_result_schema"])
        self.assertEqual(
            "schemas/astrology/ASTROLOGY_RUNTIME_GATE_RESULT_V1.schema.json",
            manifest["runtime_gate_result_schema_path"],
        )
        self.assertEqual(manifest["runtime_gate_result_schema_path"], method["runtime_gate_result_schema"])


if __name__ == "__main__":
    unittest.main()
