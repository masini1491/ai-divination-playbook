from __future__ import annotations

import json
import unittest
from pathlib import Path

from tools.astrology_output_guard import build_output

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "ASTROLOGY_USER_FACING_OUTPUT_V1.schema.json"


def _handoff() -> dict:
    return {
        "schema_name": "astrology_interpretation_handoff",
        "schema_version": "1.0.0",
        "status": "ready_for_bounded_interpretation",
        "interpretation_allowed": True,
        "adapter": {
            "adapter_id": "astrology-interpretation-handoff-v1",
            "adapter_version": "1.0.0",
            "authority": "evidence_packaging_only",
            "semantic_selection_validated_not_authored": True,
            "final_prose_authority": False,
        },
        "question": {
            "question_id": "contract-q1",
            "text": "What bounded symbolic topic is supported?",
            "focus": ["seventh house"],
            "exclusions": ["private motives"],
        },
        "selected_facts": [
            {
                "bundle": "natal",
                "collection": "houses",
                "fact": {
                    "fact_id": "fact:house:7",
                    "house_number": 7,
                    "cusp_longitude_deg": 180.0,
                    "sign": "Libra",
                },
            }
        ],
        "selected_claims": [
            {
                "registry_record_id": "first-seventh-house-axis-research-v1",
                "claim_id": "claim:valens-seventh-place-marriage",
                "source_provenance": [
                    {
                        "source_id": "source:valens",
                        "title": "Anthologies",
                        "locator": "book02/37-marriage.tex",
                    }
                ],
                "cautions": ["Do not expand this into private-motive claims."],
            }
        ],
        "conflicts": [],
        "unsupported_factors": [
            {"factor": "private motives", "reason": "Not established by admitted evidence."}
        ],
        "required_disclosures": ["Historical doctrine is not scientific validation."],
    }


def _draft() -> dict:
    fact_ref = {"bundle": "natal", "fact_id": "fact:house:7"}
    claim_ref = {
        "registry_record_id": "first-seventh-house-axis-research-v1",
        "claim_id": "claim:valens-seventh-place-marriage",
    }
    return {
        "schema_name": "astrology_output_draft",
        "schema_version": "1.0.0",
        "question_id": "contract-q1",
        "conclusion": {
            "text": "Partnership is a bounded symbolic topic; private motives remain unsupported.",
            "fact_refs": [fact_ref],
            "claim_refs": [claim_ref],
        },
        "evidence": [
            {
                "text": "The selected seventh-house fact and admitted claim support that bounded topic.",
                "fact_refs": [fact_ref],
                "claim_refs": [claim_ref],
            }
        ],
        "pre_send_attestations": {
            "direct_answer_checked": True,
            "scope_and_exclusions_checked": True,
            "evidence_language_checked": True,
            "conclusion_consistency_checked": True,
            "unresolved_handling_checked": True,
            "eligible_layer_checked": True,
            "structured_fact_provenance_checked": True,
            "unsupported_factor_boundary_checked": True,
            "conflict_and_caution_checked": True,
        },
    }


class AstrologyUserFacingOutputContractTests(unittest.TestCase):
    def test_schema_is_closed_world_success_contract(self):
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual("ASTROLOGY_USER_FACING_OUTPUT_V1.schema.json", schema["$id"])
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual("astrology_user_facing_output", schema["properties"]["schema_name"]["const"])
        self.assertEqual("1.0.0", schema["properties"]["schema_version"]["const"])
        self.assertEqual("ready_for_user", schema["properties"]["status"]["const"])
        self.assertTrue(schema["properties"]["output_allowed"]["const"])
        self.assertNotIn("synastry", json.dumps(schema))
        self.assertNotIn("solar_return", json.dumps(schema))

    def test_runtime_success_envelope_matches_declared_top_level_shape(self):
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        result = build_output(_handoff(), _draft())
        self.assertEqual(set(schema["required"]), set(result))
        self.assertEqual(schema["properties"]["schema_name"]["const"], result["schema_name"])
        self.assertEqual(schema["properties"]["schema_version"]["const"], result["schema_version"])
        self.assertEqual(schema["properties"]["status"]["const"], result["status"])
        self.assertEqual(schema["properties"]["output_allowed"]["const"], result["output_allowed"])
        self.assertEqual(
            schema["properties"]["adapter"]["properties"]["authority"]["const"],
            result["adapter"]["authority"],
        )
        self.assertEqual(
            set(schema["properties"]["owners"]["required"]),
            set(result["owners"]),
        )
        self.assertEqual(
            set(schema["properties"]["question"]["required"]),
            set(result["question"]),
        )

    def test_manifest_and_machine_index_publish_same_schema(self):
        manifest = json.loads((ROOT / "ASTROLOGY_PRODUCTION_ADMISSION_V1.json").read_text(encoding="utf-8"))
        index = json.loads((ROOT / "PLAYBOOK_INDEX.json").read_text(encoding="utf-8"))
        output = manifest["orchestration"]["output_delivery"]
        rows = {row["id"]: row for row in index["capabilities"]}
        method = rows["method.astrology"]
        self.assertEqual("ASTROLOGY_USER_FACING_OUTPUT_V1.schema.json", output["output_schema"])
        self.assertEqual("astrology_user_facing_output@1.0.0", output["output_schema_id"])
        self.assertEqual(output["output_schema"], method["user_facing_output_schema"])
        self.assertFalse(output["semantic_interpretation_authority"])
        self.assertFalse(output["final_text_authority"])


if __name__ == "__main__":
    unittest.main()
