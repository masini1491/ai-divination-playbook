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


def synthesis_handoff() -> dict:
    handoff = admitted_handoff()
    handoff["reading_run_identity"] = {"reading_mode": "natal"}
    extra = [
        ("fact:object:sun", "planet-sign-composable-semantics-research-v1", "claim:planet-function:sun"),
        ("fact:object:moon", "planet-sign-composable-semantics-research-v1", "claim:planet-function:moon"),
    ]
    for fact_id, registry_id, claim_id in extra:
        handoff["selected_facts"].append(
            {
                "bundle": "natal",
                "collection": "objects",
                "fact": {"fact_id": fact_id, "object_type": "planet"},
            }
        )
        handoff["selected_claims"].append(
            {
                "registry_record_id": registry_id,
                "claim_id": claim_id,
                "source_provenance": [],
                "cautions": [],
                "fact_refs": [{"bundle": "natal", "fact_id": fact_id}],
            }
        )
    return handoff


def synthesis_draft() -> dict:
    draft = valid_draft()
    house_fact = {"bundle": "natal", "fact_id": "fact:house:7"}
    house_claim = {
        "registry_record_id": "first-seventh-house-axis-research-v1",
        "claim_id": "claim:valens-seventh-place-marriage",
    }
    sun_fact = {"bundle": "natal", "fact_id": "fact:object:sun"}
    sun_claim = {
        "registry_record_id": "planet-sign-composable-semantics-research-v1",
        "claim_id": "claim:planet-function:sun",
    }
    moon_fact = {"bundle": "natal", "fact_id": "fact:object:moon"}
    moon_claim = {
        "registry_record_id": "planet-sign-composable-semantics-research-v1",
        "claim_id": "claim:planet-function:moon",
    }
    draft["natal_synthesis"] = {
        "profile_id": "evidence-bounded-concrete-natal-v1",
        "themes": [
            {
                "title": "Relational orientation",
                "statement": "Partnership is a material symbolic domain in the selected evidence.",
                "manifestation": "This may show as deliberate attention to how commitments are structured.",
                "fact_refs": [house_fact],
                "claim_refs": [house_claim],
                "limiting_condition": {
                    "text": "The solar evidence can pull attention back toward self-directed priorities.",
                    "fact_refs": [sun_fact],
                    "claim_refs": [sun_claim],
                },
            },
            {
                "title": "Self-directed emphasis",
                "statement": "The admitted solar function contributes a distinct self-directed theme.",
                "manifestation": "This may show as a preference to define a personal direction before adapting to others.",
                "fact_refs": [sun_fact],
                "claim_refs": [sun_claim],
            },
            {
                "title": "Responsive emphasis",
                "statement": "The admitted lunar function contributes a responsive or receptive theme.",
                "manifestation": "This may show as greater sensitivity to context when deciding how to respond.",
                "fact_refs": [moon_fact],
                "claim_refs": [moon_claim],
            },
        ],
    }
    return draft


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

    def test_valid_concrete_natal_synthesis_preserves_traceable_themes(self):
        result = build_output(synthesis_handoff(), synthesis_draft())
        self.assertEqual(
            "evidence-bounded-concrete-natal-v1",
            result["natal_synthesis"]["profile_id"],
        )
        self.assertEqual(3, len(result["natal_synthesis"]["themes"]))
        self.assertIn("Major natal themes:", result["rendered_text"])
        self.assertIn("Limiting condition / tension:", result["rendered_text"])
        self.assertIn(
            {"bundle": "natal", "fact_id": "fact:object:sun"},
            result["used_fact_refs"],
        )
        self.assertIn(
            {
                "registry_record_id": "planet-sign-composable-semantics-research-v1",
                "claim_id": "claim:planet-function:sun",
            },
            result["used_claim_refs"],
        )

    def test_natal_synthesis_requires_three_to_five_themes(self):
        draft = synthesis_draft()
        draft["natal_synthesis"]["themes"] = draft["natal_synthesis"]["themes"][:2]
        with self.assertRaisesRegex(AstrologyOutputGuardError, "3 to 5"):
            build_output(synthesis_handoff(), draft)

    def test_natal_synthesis_theme_cannot_inflate_fact_only_semantics(self):
        draft = synthesis_draft()
        draft["natal_synthesis"]["themes"][0]["claim_refs"] = []
        with self.assertRaisesRegex(AstrologyOutputGuardError, "admitted semantic evidence"):
            build_output(synthesis_handoff(), draft)

    def test_natal_synthesis_is_rejected_for_transit_handoff(self):
        handoff = synthesis_handoff()
        handoff["reading_run_identity"]["reading_mode"] = "transit"
        with self.assertRaisesRegex(AstrologyOutputGuardError, "requires an admitted natal"):
            build_output(handoff, synthesis_draft())

    def test_natal_synthesis_limiting_condition_requires_admitted_refs(self):
        draft = synthesis_draft()
        draft["natal_synthesis"]["themes"][0]["limiting_condition"]["claim_refs"][0]["claim_id"] = "claim:not-selected"
        with self.assertRaisesRegex(AstrologyOutputGuardError, "outside admitted handoff"):
            build_output(synthesis_handoff(), draft)



if __name__ == "__main__":
    unittest.main()
