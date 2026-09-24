from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools.astrology_output_guard import AstrologyOutputGuardError, build_output

ROOT = Path(__file__).resolve().parents[1]


def admitted_handoff() -> dict:
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
            "question_id": "q1",
            "text": "What relationship theme is supported?",
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
                "fact_refs": [
                    {"bundle": "natal", "fact_id": "fact:house:7"}
                ],
            }
        ],
        "conflicts": [],
        "unsupported_factors": [
            {"factor": "private motives", "reason": "Not established by admitted evidence."}
        ],
        "required_disclosures": ["Historical doctrine is not scientific validation."],
    }


def valid_draft() -> dict:
    fact_ref = {"bundle": "natal", "fact_id": "fact:house:7"}
    claim_ref = {
        "registry_record_id": "first-seventh-house-axis-research-v1",
        "claim_id": "claim:valens-seventh-place-marriage",
    }
    return {
        "schema_name": "astrology_output_draft",
        "schema_version": "1.0.0",
        "question_id": "q1",
        "conclusion": {
            "text": "Partnership is a relevant symbolic topic, without establishing private motives.",
            "fact_refs": [copy.deepcopy(fact_ref)],
            "claim_refs": [copy.deepcopy(claim_ref)],
        },
        "evidence": [
            {
                "text": "The admitted seventh-house fact and bounded historical claim support that topic.",
                "fact_refs": [copy.deepcopy(fact_ref)],
                "claim_refs": [copy.deepcopy(claim_ref)],
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


class AstrologyOutputGuardTests(unittest.TestCase):
    def test_valid_draft_becomes_ready_for_user(self):
        result = build_output(admitted_handoff(), valid_draft())
        self.assertEqual("astrology_user_facing_output", result["schema_name"])
        self.assertEqual("ready_for_user", result["status"])
        self.assertTrue(result["output_allowed"])
        self.assertEqual("provenance_and_pre_send_validation_only", result["adapter"]["authority"])
        self.assertFalse(result["adapter"]["semantic_interpretation_authored"])
        self.assertFalse(result["adapter"]["final_text_authored"])
        self.assertIn("private motives", result["rendered_text"])
        self.assertTrue(result["source_provenance"])

    def test_unknown_fact_ref_is_rejected(self):
        draft = valid_draft()
        draft["conclusion"]["fact_refs"][0]["fact_id"] = "fact:missing"
        with self.assertRaisesRegex(AstrologyOutputGuardError, "outside admitted handoff"):
            build_output(admitted_handoff(), draft)

    def test_unknown_claim_ref_is_rejected(self):
        draft = valid_draft()
        draft["evidence"][0]["claim_refs"][0]["claim_id"] = "claim:not-selected"
        with self.assertRaisesRegex(AstrologyOutputGuardError, "outside admitted handoff"):
            build_output(admitted_handoff(), draft)

    def test_question_identity_must_match(self):
        draft = valid_draft()
        draft["question_id"] = "different-question"
        with self.assertRaisesRegex(AstrologyOutputGuardError, "does not match handoff"):
            build_output(admitted_handoff(), draft)

    def test_false_pre_send_attestation_fails_closed(self):
        draft = valid_draft()
        draft["pre_send_attestations"]["scope_and_exclusions_checked"] = False
        with self.assertRaisesRegex(AstrologyOutputGuardError, "attestations must be true"):
            build_output(admitted_handoff(), draft)

    def test_rejected_handoff_cannot_render(self):
        handoff = admitted_handoff()
        handoff["status"] = "rejected"
        handoff["interpretation_allowed"] = False
        with self.assertRaisesRegex(AstrologyOutputGuardError, "not admitted"):
            build_output(handoff, valid_draft())

    def test_cli_emits_ready_output(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            handoff_path = Path(temp_dir) / "handoff.json"
            draft_path = Path(temp_dir) / "draft.json"
            handoff_path.write_text(json.dumps(admitted_handoff()), encoding="utf-8")
            draft_path.write_text(json.dumps(valid_draft()), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, "-m", "tools.astrology_output_guard", str(handoff_path), str(draft_path)],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(0, completed.returncode, completed.stderr or completed.stdout)
        result = json.loads(completed.stdout)
        self.assertEqual("ready_for_user", result["status"])


    def test_output_unit_rejects_claim_not_bound_to_all_cited_facts(self):
        handoff = admitted_handoff()
        handoff["selected_facts"].append(
            {
                "bundle": "natal",
                "collection": "objects",
                "fact": {
                    "fact_id": "fact:angle:descendant",
                    "object_type": "angle",
                    "object_id": "Descendant",
                    "longitude_deg": 180.0,
                },
            }
        )
        draft = valid_draft()
        draft["evidence"][0]["fact_refs"].append(
            {"bundle": "natal", "fact_id": "fact:angle:descendant"}
        )
        with self.assertRaisesRegex(
            AstrologyOutputGuardError,
            "not applicability-bound to fact: natal / fact:angle:descendant",
        ):
            build_output(handoff, draft)

    def test_output_unit_allows_deterministic_fact_without_claim(self):
        handoff = admitted_handoff()
        handoff["selected_facts"].append(
            {
                "bundle": "natal",
                "collection": "objects",
                "fact": {
                    "fact_id": "fact:angle:descendant",
                    "object_type": "angle",
                    "object_id": "Descendant",
                    "longitude_deg": 180.0,
                },
            }
        )
        draft = valid_draft()
        draft["evidence"].append(
            {
                "text": "The deterministic chart contains a Descendant at 180 degrees.",
                "fact_refs": [{"bundle": "natal", "fact_id": "fact:angle:descendant"}],
                "claim_refs": [],
            }
        )
        result = build_output(handoff, draft)
        self.assertEqual("ready_for_user", result["status"])
        self.assertIn(
            {"bundle": "natal", "fact_id": "fact:angle:descendant"},
            result["used_fact_refs"],
        )


if __name__ == "__main__":
    unittest.main()
