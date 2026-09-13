from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools.astrology_orchestrator import run_request
from tools.astrology_reading_pipeline import run_pipeline

ROOT = Path(__file__).resolve().parents[1]
READING = ROOT / "tests" / "fixtures" / "astrology_reading_request_transit_v1.json"
REGISTRY_ID = "transit-interpretation-research-v1"
CLAIM_ID = "claim:project-transit-facts-before-interpretation"
QUESTION_ID = "fixture-transit-user-facing-v1"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_requests() -> tuple[dict, dict, dict, dict]:
    reading = load(READING)
    witness_run = run_request(reading)
    events = [
        event
        for event in witness_run["fact_bundles"]["transit"]["facts"]["events"]
        if event.get("event_kind") == "transit_to_natal"
    ]
    if not events:
        raise AssertionError("transit fixture must produce at least one transit_to_natal event")
    event = events[0]
    fact_ref = {"bundle": "transit", "fact_id": event["fact_id"]}
    claim_ref = {"registry_record_id": REGISTRY_ID, "claim_id": CLAIM_ID}

    interpretation = {
        "schema_name": "astrology_interpretation_request",
        "schema_version": "1.0.0",
        "question_id": QUESTION_ID,
        "question": "What exact transit timing fact is present in this synthetic fixture, and what current production boundary applies?",
        "focus": ["deterministic transit timing", "production interpretation boundary"],
        "exclusions": ["guaranteed external event outcomes"],
        "fact_refs": [dict(fact_ref)],
        "claim_requests": [
            {
                "registry_record_id": REGISTRY_ID,
                "claim_id": CLAIM_ID,
                "fact_refs": [dict(fact_ref)],
            }
        ],
        "unsupported_factors": [
            {
                "factor": "pair-specific transit event meaning",
                "reason": "No independently admitted pair-specific transit meaning is selected; deterministic timing geometry does not imply a guaranteed external event outcome.",
            }
        ],
    }

    exact_time = event["exact_time_utc"]
    output = {
        "schema_name": "astrology_output_draft",
        "schema_version": "1.0.0",
        "question_id": QUESTION_ID,
        "conclusion": {
            "text": "This synthetic transit reading contains an admitted exact Sun-to-natal-Sun conjunction timing fact; production use keeps that geometry separate from guaranteed real-world outcomes.",
            "fact_refs": [dict(fact_ref)],
            "claim_refs": [dict(claim_ref)],
        },
        "evidence": [
            {
                "text": f"The deterministic transit provider placed the selected exact contact at {exact_time} and the runtime gate admitted that event fact.",
                "fact_refs": [dict(fact_ref)],
                "claim_refs": [dict(claim_ref)],
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
    return reading, interpretation, output, event


class AstrologyTransitUserPipelineTests(unittest.TestCase):
    def test_transit_request_reaches_bounded_user_facing_output(self):
        reading, interpretation, output, event = build_requests()
        result = run_pipeline(reading, interpretation, output, repo_root=ROOT)

        self.assertEqual("ready_for_user", result["status"])
        self.assertTrue(result["output_allowed"])
        self.assertEqual("transit", result["stages"]["reading_run"]["normalized_request"]["reading_mode"])
        self.assertIn("transit", result["stages"]["reading_run"]["fact_bundles"])

        handoff = result["stages"]["interpretation_handoff"]
        self.assertEqual("events", handoff["selected_facts"][0]["collection"])
        self.assertEqual(event["fact_id"], handoff["selected_facts"][0]["fact"]["fact_id"])
        self.assertEqual(CLAIM_ID, handoff["selected_claims"][0]["claim_id"])
        self.assertEqual(
            "pair-specific transit event meaning",
            handoff["unsupported_factors"][0]["factor"],
        )

        final_output = result["stages"]["user_facing_output"]
        self.assertIn(
            {"bundle": "transit", "fact_id": event["fact_id"]},
            final_output["used_fact_refs"],
        )
        self.assertIn(
            {"registry_record_id": REGISTRY_ID, "claim_id": CLAIM_ID},
            final_output["used_claim_refs"],
        )
        self.assertIn("Unsupported / unavailable factors:", result["rendered_text"])
        self.assertIn("Required disclosures:", result["rendered_text"])
        self.assertIn(event["exact_time_utc"], result["rendered_text"])

    def test_transit_pipeline_cli_runs_with_deterministically_selected_event(self):
        reading, interpretation, output, _ = build_requests()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reading_path = root / "reading.json"
            interpretation_path = root / "interpretation.json"
            output_path = root / "output.json"
            for path, payload in (
                (reading_path, reading),
                (interpretation_path, interpretation),
                (output_path, output),
            ):
                path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "tools.astrology_reading_pipeline",
                    str(reading_path),
                    str(interpretation_path),
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
        self.assertEqual("transit", result["stages"]["reading_run"]["normalized_request"]["reading_mode"])
        self.assertIn("pair-specific transit event meaning", result["rendered_text"])

    def test_transit_reference_only_meaning_stays_fail_closed(self):
        reading, interpretation, output, _ = build_requests()
        interpretation["claim_requests"][0]["claim_id"] = "claim:reference-natal-promise-before-timing"
        output["conclusion"]["claim_refs"][0]["claim_id"] = "claim:reference-natal-promise-before-timing"
        output["evidence"][0]["claim_refs"][0]["claim_id"] = "claim:reference-natal-promise-before-timing"

        with self.assertRaisesRegex(ValueError, "forbidden by production source policy"):
            run_pipeline(reading, interpretation, output, repo_root=ROOT)


if __name__ == "__main__":
    unittest.main()
