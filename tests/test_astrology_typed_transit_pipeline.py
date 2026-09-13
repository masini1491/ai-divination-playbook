from __future__ import annotations

import json
import unittest
from pathlib import Path

from tools.astrology_orchestrator import run_request
from tools.astrology_typed_reading_pipeline import run_typed_pipeline

ROOT = Path(__file__).resolve().parents[1]
READING = ROOT / "tests" / "fixtures" / "astrology_reading_request_transit_v1.json"
REGISTRY_ID = "transit-interpretation-research-v1"
CLAIM_ID = "claim:project-transit-facts-before-interpretation"
QUESTION_ID = "fixture-typed-transit-user-facing-v1"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_requests() -> tuple[dict, dict, dict, dict]:
    reading = load(READING)
    witness_run = run_request(reading)
    event = next(
        (
            row
            for row in witness_run["fact_bundles"]["transit"]["facts"]["events"]
            if row.get("event_kind") == "transit_to_natal"
        ),
        None,
    )
    if event is None:
        raise AssertionError("transit fixture must produce at least one transit_to_natal event")

    fact_ref = {"bundle": "transit", "fact_id": event["fact_id"]}
    claim_ref = {"registry_record_id": REGISTRY_ID, "claim_id": CLAIM_ID}
    typed = {
        "schema_name": "astrology_typed_evidence_selection_request",
        "schema_version": "1.0.0",
        "question_id": QUESTION_ID,
        "question": "What exact transit timing fact is present, and what production boundary applies?",
        "focus": ["deterministic transit timing", "production interpretation boundary"],
        "exclusions": ["guaranteed external event outcomes"],
        "fact_selectors": [
            {
                "selector_id": "exact-transit-contact",
                "selector_kind": "event",
                "bundle": "transit",
                "cardinality": "exactly_one",
                "event_kind": "transit_to_natal",
                "moving_body": event["moving_body"],
                "natal_target": event["natal_target"],
                "aspect": event["aspect"],
                "passage_index": event["passage_index"],
            }
        ],
        "claim_selectors": [
            {
                "selector_id": "transit-policy",
                "registry_record_id": REGISTRY_ID,
                "claim_type": "transit_policy",
                "applies_to_all": ["transit", "transit-to-natal", "exact passage"],
                "fact_selector_ids": ["exact-transit-contact"],
            }
        ],
        "unsupported_factors": [
            {
                "factor": "pair-specific transit event meaning",
                "reason": "No independently admitted pair-specific transit meaning is selected; exact timing geometry does not imply a guaranteed external event outcome.",
            }
        ],
    }

    output = {
        "schema_name": "astrology_output_draft",
        "schema_version": "1.0.0",
        "question_id": QUESTION_ID,
        "conclusion": {
            "text": "This synthetic transit reading contains an admitted exact transit-to-natal timing fact; production use keeps that geometry separate from guaranteed real-world outcomes.",
            "fact_refs": [dict(fact_ref)],
            "claim_refs": [dict(claim_ref)],
        },
        "evidence": [
            {
                "text": f"The deterministic transit provider placed the selected exact contact at {event['exact_time_utc']} and the typed selector resolved it without using a caller-supplied fact id.",
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
    return reading, typed, output, event


class AstrologyTypedTransitPipelineTests(unittest.TestCase):
    def test_transit_typed_pipeline_resolves_event_and_claim_end_to_end(self):
        reading, typed, output, event = build_requests()
        result = run_typed_pipeline(reading, typed, output, repo_root=ROOT)

        self.assertEqual("ready_for_user", result["status"])
        self.assertTrue(result["output_allowed"])
        self.assertEqual("transit", result["stages"]["reading_run"]["normalized_request"]["reading_mode"])

        selection = result["stages"]["evidence_selection"]
        self.assertEqual("selected", selection["status"])
        self.assertEqual([{"bundle": "transit", "fact_id": event["fact_id"]}], selection["fact_refs"])
        self.assertEqual(CLAIM_ID, selection["claim_requests"][0]["claim_id"])
        self.assertEqual(
            [{"bundle": "transit", "fact_id": event["fact_id"]}],
            selection["selection_provenance"]["fact_selectors"][0]["matched_fact_refs"],
        )

        handoff = result["stages"]["interpretation_handoff"]
        self.assertEqual("events", handoff["selected_facts"][0]["collection"])
        self.assertEqual(event["fact_id"], handoff["selected_facts"][0]["fact"]["fact_id"])
        self.assertEqual(CLAIM_ID, handoff["selected_claims"][0]["claim_id"])

        final_output = result["stages"]["user_facing_output"]
        self.assertIn({"bundle": "transit", "fact_id": event["fact_id"]}, final_output["used_fact_refs"])
        self.assertIn({"registry_record_id": REGISTRY_ID, "claim_id": CLAIM_ID}, final_output["used_claim_refs"])
        self.assertIn(event["exact_time_utc"], result["rendered_text"])
        self.assertIn("Unsupported / unavailable factors:", result["rendered_text"])

    def test_transit_typed_pipeline_cannot_select_reference_only_pair_meaning(self):
        reading, typed, output, _ = build_requests()
        typed["claim_selectors"][0] = {
            "selector_id": "reference-only-meaning",
            "registry_record_id": REGISTRY_ID,
            "claim_type": "transit_meaning",
            "applies_to_all": ["transit", "natal promise", "activation"],
            "fact_selector_ids": ["exact-transit-contact"],
        }

        with self.assertRaisesRegex(ValueError, "fact-applicability binding"):
            run_typed_pipeline(reading, typed, output, repo_root=ROOT)


if __name__ == "__main__":
    unittest.main()
