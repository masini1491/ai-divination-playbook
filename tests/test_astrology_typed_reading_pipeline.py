from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools.astrology_typed_reading_pipeline import (
    AstrologyTypedReadingPipelineError,
    run_typed_pipeline,
)

ROOT = Path(__file__).resolve().parents[1]
READING = ROOT / "tests" / "fixtures" / "astrology_pipeline_reading_request_natal_v1.json"
OUTPUT = ROOT / "tests" / "fixtures" / "astrology_pipeline_output_draft_natal_v1.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def typed_request() -> dict:
    return {
        "schema_name": "astrology_typed_evidence_selection_request",
        "schema_version": "1.0.0",
        "question_id": "fixture-natal-house-question",
        "question": "What symbolic relationship theme is supported by the admitted seventh-house evidence?",
        "focus": ["seventh house"],
        "exclusions": ["specific partner motives", "guaranteed relationship outcomes"],
        "fact_selectors": [
            {
                "selector_id": "house-7",
                "selector_kind": "house",
                "bundle": "natal",
                "cardinality": "exactly_one",
                "house_number": 7,
            }
        ],
        "claim_selectors": [
            {
                "selector_id": "hellenistic-seventh-marriage",
                "registry_record_id": "first-seventh-house-axis-research-v1",
                "claim_type": "historical_doctrine",
                "applies_to_all": ["natal", "seventh house", "marriage"],
                "tradition_context_refs_any": ["lineage:hellenistic"],
                "fact_selector_ids": ["house-7"],
            }
        ],
        "unsupported_factors": [
            {
                "factor": "specific partner motives",
                "reason": "The admitted house evidence does not establish another person's private motives.",
            }
        ],
    }


class AstrologyTypedReadingPipelineTests(unittest.TestCase):
    def test_typed_pipeline_reaches_user_output_with_selection_provenance(self):
        result = run_typed_pipeline(load(READING), typed_request(), load(OUTPUT), repo_root=ROOT)

        self.assertEqual("astrology_typed_reading_pipeline_run", result["schema_name"])
        self.assertEqual("ready_for_user", result["status"])
        self.assertTrue(result["output_allowed"])
        self.assertFalse(result["pipeline"]["free_text_query_resolution"])
        self.assertFalse(result["pipeline"]["semantic_selection_authored"])

        stages = result["stages"]
        self.assertEqual("admitted", stages["reading_run"]["status"])
        self.assertEqual("selected", stages["evidence_selection"]["status"])
        self.assertEqual(
            [{"bundle": "natal", "fact_id": "fact:house:7"}],
            stages["evidence_selection"]["fact_refs"],
        )
        self.assertEqual(
            "claim:valens-seventh-place-marriage",
            stages["evidence_selection"]["claim_requests"][0]["claim_id"],
        )
        self.assertEqual("ready_for_bounded_interpretation", stages["interpretation_handoff"]["status"])
        self.assertEqual("ready_for_user", stages["user_facing_output"]["status"])
        self.assertIn("Unsupported / unavailable factors:", result["rendered_text"])

    def test_typed_pipeline_cli_preserves_legacy_output_guard_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reading_path = root / "reading.json"
            typed_path = root / "typed.json"
            output_path = root / "output.json"
            for path, payload in (
                (reading_path, load(READING)),
                (typed_path, typed_request()),
                (output_path, load(OUTPUT)),
            ):
                path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "tools.astrology_typed_reading_pipeline",
                    str(reading_path),
                    str(typed_path),
                    str(output_path),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(0, completed.returncode, completed.stderr or completed.stdout)
        result = json.loads(completed.stdout)
        self.assertEqual("ready_for_user", result["status"])
        self.assertEqual("selected", result["stages"]["evidence_selection"]["status"])

    def test_output_cannot_reference_claim_not_selected_by_typed_stage(self):
        output = load(OUTPUT)
        output["conclusion"]["claim_refs"][0]["claim_id"] = "claim:lilly-seventh-house-marriage-opponents"

        with self.assertRaisesRegex(
            AstrologyTypedReadingPipelineError,
            "claim ref is not selected by the interpretation handoff",
        ):
            run_typed_pipeline(load(READING), typed_request(), output, repo_root=ROOT)

    def test_fact_claim_mismatch_fails_before_handoff(self):
        typed = typed_request()
        typed["fact_selectors"][0]["house_number"] = 12

        with self.assertRaisesRegex(
            AstrologyTypedReadingPipelineError,
            "fact-applicability binding",
        ):
            run_typed_pipeline(load(READING), typed, load(OUTPUT), repo_root=ROOT)


if __name__ == "__main__":
    unittest.main()
