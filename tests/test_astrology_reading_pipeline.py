from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from tools.astrology_reading_pipeline import AstrologyReadingPipelineError, run_pipeline

ROOT = Path(__file__).resolve().parents[1]
READING = ROOT / "tests" / "fixtures" / "astrology_pipeline_reading_request_natal_v1.json"
INTERPRETATION = ROOT / "tests" / "fixtures" / "astrology_pipeline_interpretation_request_natal_v1.json"
OUTPUT = ROOT / "tests" / "fixtures" / "astrology_pipeline_output_draft_natal_v1.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class AstrologyReadingPipelineTests(unittest.TestCase):
    def test_full_request_to_user_output_pipeline(self):
        result = run_pipeline(load(READING), load(INTERPRETATION), load(OUTPUT), repo_root=ROOT)
        self.assertEqual("astrology_reading_pipeline_run", result["schema_name"])
        self.assertEqual("1.0.0", result["schema_version"])
        self.assertEqual("ready_for_user", result["status"])
        self.assertTrue(result["output_allowed"])
        self.assertEqual("composition_only", result["pipeline"]["authority"])
        self.assertFalse(result["pipeline"]["semantic_selection_authored"])
        self.assertFalse(result["pipeline"]["final_text_authored"])
        self.assertEqual("external_only", result["pipeline"]["reading_record_storage"])

        stages = result["stages"]
        self.assertEqual("admitted", stages["reading_run"]["status"])
        self.assertEqual("ready_for_bounded_interpretation", stages["interpretation_handoff"]["status"])
        self.assertEqual("ready_for_user", stages["user_facing_output"]["status"])
        self.assertEqual("offline_place_resolver", stages["reading_run"]["input_resolution"]["resolution_mode"])
        self.assertEqual("Asia/Tokyo", stages["reading_run"]["input_resolution"]["resolved"]["timezone_name"])
        self.assertEqual(
            "fact:house:7",
            stages["interpretation_handoff"]["selected_facts"][0]["fact"]["fact_id"],
        )
        self.assertEqual(
            "claim:valens-seventh-place-marriage",
            stages["interpretation_handoff"]["selected_claims"][0]["claim_id"],
        )
        self.assertIn("Unsupported / unavailable factors:", result["rendered_text"])
        self.assertIn("Required disclosures:", result["rendered_text"])

    def test_output_draft_cannot_escape_handoff(self):
        output = load(OUTPUT)
        output["conclusion"]["claim_refs"][0]["claim_id"] = "claim:not-selected"
        with self.assertRaisesRegex(AstrologyReadingPipelineError, "outside admitted handoff"):
            run_pipeline(load(READING), load(INTERPRETATION), output, repo_root=ROOT)

    def test_interpretation_request_cannot_use_unadmitted_registry(self):
        interpretation = load(INTERPRETATION)
        interpretation["claim_requests"][0]["registry_record_id"] = "not-admitted"
        with self.assertRaisesRegex(AstrologyReadingPipelineError, "not production-admitted"):
            run_pipeline(load(READING), interpretation, load(OUTPUT), repo_root=ROOT)

    def test_cli_runs_complete_pipeline(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "tools.astrology_reading_pipeline",
                str(READING),
                str(INTERPRETATION),
                str(OUTPUT),
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, completed.returncode, completed.stderr or completed.stdout)
        result = json.loads(completed.stdout)
        self.assertEqual("ready_for_user", result["status"])
        self.assertTrue(result["output_allowed"])
        self.assertIn("rendered_text", result)


    def test_legacy_pipeline_rejects_derived_fact_only_claim_binding(self):
        interpretation = load(INTERPRETATION)
        descendant_ref = {"bundle": "natal", "fact_id": "fact:angle:descendant"}
        interpretation["fact_refs"] = [descendant_ref]
        interpretation["claim_requests"][0]["fact_refs"] = [descendant_ref]
        with self.assertRaisesRegex(
            AstrologyReadingPipelineError,
            "claim binding is not admitted for fact-only object: Descendant",
        ):
            run_pipeline(load(READING), interpretation, load(OUTPUT), repo_root=ROOT)


if __name__ == "__main__":
    unittest.main()
