"""Deterministic, fixed-fact semantic contract regressions for three MCP methods.

This is a TEST-ONLY structured interpretation-outline oracle, not an LLM
interpretation evaluator or a production interpretation engine. It checks
observable responsibility/provenance invariants. Canonical rules remain the
exact-commit owner documents bundled by the selective release.
"""
from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

MCP = Path(__file__).resolve().parents[2] / "integrations" / "chatgpt-mcp"
sys.path.insert(0, str(MCP))
from policy_adapter import get_policy_owner, selected_policy  # noqa: E402


def review_outline(contract: dict, facts: dict, outline: dict) -> list[str]:
    """Reject structural or epistemic violations; do not generate an interpretation."""
    errors = []
    def fail(code: str):
        if code not in errors:
            errors.append(code)

    method = contract.get("method")
    if method not in ("tarot", "meihua", "liuyao"):
        return ["UNSUPPORTED_METHOD"]
    if outline.get("method") != method or facts.get("method") != method:
        fail("METHOD_CHANGED")
    if not contract.get("question_id") or facts.get("question_id") != contract.get("question_id") \
            or outline.get("question_id") != contract.get("question_id"):
        fail("QUESTION_IDENTITY_CHANGED")
    if facts.get("draw_id") != outline.get("draw_id") or not facts.get("draw_id"):
        fail("CAST_FACT_REPLACED")
    if facts.get("provenance") not in ("canonical_runtime", "user_supplied"):
        fail("UNVERIFIED_CAST_SOURCE")
    if outline.get("objective_probability_pct") is not None:
        fail("OBJECTIVE_PROBABILITY_FROM_SYMBOLS")
    if outline.get("guaranteed_outcome", False):
        fail("GUARANTEED_OUTCOME_FROM_SYMBOLS")

    if method == "tarot":
        if outline.get("position_responsibilities") != contract.get("position_responsibilities"):
            fail("TAROT_POSITION_RESPONSIBILITY_CHANGED")
        if outline.get("card_ids_by_position") != facts.get("card_ids_by_position"):
            fail("TAROT_CARDS_REASSIGNED")
        if outline.get("comparison_axis") != contract.get("comparison_axis"):
            fail("TAROT_LIKELIHOOD_QUALITY_CONFLATED")
        reversed_ids = set(facts.get("reversed_card_ids", []))
        reversal_modes = outline.get("reversal_primary_modes", {})
        if not isinstance(reversal_modes, dict) or set(reversal_modes) != reversed_ids \
                or any(not isinstance(x, str) or x not in
                       {"blocked", "internalized", "excessive", "delayed", "shadow"}
                       for x in reversal_modes.values()):
            fail("TAROT_REVERSAL_MODE_UNBOUNDED")
        if outline.get("claims_private_mind_as_fact", False):
            fail("TAROT_PRIVATE_MIND_AS_FACT")

    elif method == "meihua":
        steps = ["upper_lower_moving", "primary_mutual_changed",
                 "body_use_mapping", "body_use_relation", "primary_state",
                 "mutual_process", "changed_trajectory", "moving_line_trigger"]
        if outline.get("evidence_sequence") != steps:
            fail("MEIHUA_EVIDENCE_ORDER_CHANGED")
        if outline.get("body_use_mapping") != contract.get("body_use_mapping") \
                or outline.get("favorable_direction") != contract.get("favorable_direction"):
            fail("MEIHUA_BODY_USE_PERSPECTIVE_CHANGED")
        if outline.get("primary_hexagram") != facts.get("primary_hexagram") \
                or outline.get("mutual_hexagram") != facts.get("mutual_hexagram") \
                or outline.get("changed_hexagram") != facts.get("changed_hexagram") \
                or outline.get("moving_line") != facts.get("moving_line"):
            fail("MEIHUA_STRUCTURED_FACT_CHANGED")
        if outline.get("changed_hexagram_role") != "trajectory":
            fail("MEIHUA_CHANGED_HEXAGRAM_AS_COMPLETION")
        if outline.get("timing_precision") not in ("none", "relative_checkpoint"):
            fail("MEIHUA_FALSE_EXACT_TIMING")
        if outline.get("interprets_good_as_certain_yes", False):
            fail("MEIHUA_GOOD_EQUALS_CERTAIN_YES")

    else:  # liuyao
        if not contract.get("horizon") or not contract.get("completion_rule"):
            fail("LIUYAO_MISSING_COMPLETION_CONTRACT")
        if outline.get("completion_rule") != contract.get("completion_rule") \
                or outline.get("horizon") != contract.get("horizon"):
            fail("LIUYAO_COMPLETION_CONTRACT_CHANGED")
        if outline.get("primary_target") != contract.get("primary_target"):
            fail("LIUYAO_YONGSHEN_RESELECTED")
        lines = facts.get("raw_lines")
        if not isinstance(lines, list) or len(lines) != 6 \
                or any(type(v) is not int or v not in (6, 7, 8, 9) for v in lines) \
                or facts.get("line_order") != "bottom-to-top":
            fail("LIUYAO_INVALID_RAW_FACT")
        if outline.get("raw_lines") != lines or outline.get("line_order") != "bottom-to-top":
            fail("LIUYAO_RAW_FACT_CHANGED")
        if facts.get("structured_verified") is not True \
                and outline.get("analysis_level") == "full_najia":
            fail("LIUYAO_UNVERIFIED_STRUCTURAL_FACTS")
        if facts.get("calendar_verified") is not True \
                and (outline.get("uses_calendar_evidence", False)
                     or outline.get("timing_precision") in ("calendar_window", "exact_date")):
            fail("LIUYAO_UNVERIFIED_CALENDAR_EVIDENCE")
        if outline.get("timing_precision") == "exact_date" \
                and not outline.get("timing_evidence_verified", False):
            fail("LIUYAO_FALSE_EXACT_TIMING")
        if outline.get("layers") != ["outcome", "obstacle", "timing"]:
            fail("LIUYAO_LAYERS_CONFLATED")
    return errors


def fixed_cases():
    """Fixed hypothetical method facts; no random draw, no personal details."""
    tarot = (
        {"method": "tarot", "question_id": "comparison-001",
         "position_responsibilities": ["option-A", "option-B"],
         "comparison_axis": "event_likelihood"},
        {"method": "tarot", "question_id": "comparison-001", "draw_id": "fixture-T1",
         "provenance": "user_supplied", "card_ids_by_position": ["card-06", "card-13"],
         "reversed_card_ids": ["card-13"]},
        {"method": "tarot", "question_id": "comparison-001", "draw_id": "fixture-T1",
         "position_responsibilities": ["option-A", "option-B"],
         "comparison_axis": "event_likelihood", "card_ids_by_position": ["card-06", "card-13"],
         "reversal_primary_modes": {"card-13": "blocked"},
         "claims_private_mind_as_fact": False},
    )
    meihua = (
        {"method": "meihua", "question_id": "evolution-001",
         "body_use_mapping": {"body": "subject", "use": "external_party"},
         "favorable_direction": "cooperation_advances"},
        {"method": "meihua", "question_id": "evolution-001", "draw_id": "fixture-M1",
         "provenance": "user_supplied", "primary_hexagram": "fixed-primary",
         "mutual_hexagram": "fixed-mutual", "changed_hexagram": "fixed-changed",
         "moving_line": 3},
        {"method": "meihua", "question_id": "evolution-001", "draw_id": "fixture-M1",
         "evidence_sequence": ["upper_lower_moving", "primary_mutual_changed",
                               "body_use_mapping", "body_use_relation", "primary_state",
                               "mutual_process", "changed_trajectory", "moving_line_trigger"],
         "body_use_mapping": {"body": "subject", "use": "external_party"},
         "favorable_direction": "cooperation_advances",
         "primary_hexagram": "fixed-primary", "mutual_hexagram": "fixed-mutual",
         "changed_hexagram": "fixed-changed", "moving_line": 3,
         "changed_hexagram_role": "trajectory", "timing_precision": "relative_checkpoint"},
    )
    liuyao = (
        {"method": "liuyao", "question_id": "completion-001",
         "horizon": "2026-11-15", "completion_rule": "formal_written_approval_received",
         "primary_target": "formal_approval"},
        {"method": "liuyao", "question_id": "completion-001", "draw_id": "fixture-L1",
         "provenance": "user_supplied", "raw_lines": [7, 8, 9, 7, 8, 6],
         "line_order": "bottom-to-top", "structured_verified": True,
         "calendar_verified": False},
        {"method": "liuyao", "question_id": "completion-001", "draw_id": "fixture-L1",
         "horizon": "2026-11-15", "completion_rule": "formal_written_approval_received",
         "primary_target": "formal_approval", "raw_lines": [7, 8, 9, 7, 8, 6],
         "line_order": "bottom-to-top", "analysis_level": "full_najia",
         "uses_calendar_evidence": False, "timing_precision": "none",
         "layers": ["outcome", "obstacle", "timing"]},
    )
    return {"tarot": tarot, "meihua": meihua, "liuyao": liuyao}


class InterpretationSemanticParityTests(unittest.TestCase):
    def test_fixed_structured_outlines_pass(self):
        for method, (contract, fact, outline) in fixed_cases().items():
            with self.subTest(method=method):
                self.assertEqual(review_outline(contract, fact, outline), [])

    def test_negative_mutations_are_caught(self):
        bad = {
            "tarot": [
                ("TAROT_POSITION_RESPONSIBILITY_CHANGED",
                 {"position_responsibilities": ["option-B", "option-A"]}),
                ("TAROT_LIKELIHOOD_QUALITY_CONFLATED", {"comparison_axis": "conditional_quality"}),
                ("TAROT_CARDS_REASSIGNED", {"card_ids_by_position": ["card-13", "card-06"]}),
                ("TAROT_REVERSAL_MODE_UNBOUNDED", {"reversal_primary_modes": {"card-13": ["blocked", "delayed"]}}),
                ("TAROT_PRIVATE_MIND_AS_FACT", {"claims_private_mind_as_fact": True}),
            ],
            "meihua": [
                ("MEIHUA_BODY_USE_PERSPECTIVE_CHANGED", {"body_use_mapping": {"body": "external_party", "use": "subject"}}),
                ("MEIHUA_EVIDENCE_ORDER_CHANGED", {"evidence_sequence": ["changed_trajectory", "primary_state"]}),
                ("MEIHUA_CHANGED_HEXAGRAM_AS_COMPLETION", {"changed_hexagram_role": "guaranteed_completion"}),
                ("MEIHUA_STRUCTURED_FACT_CHANGED", {"moving_line": 6}),
                ("MEIHUA_FALSE_EXACT_TIMING", {"timing_precision": "exact_date"}),
                ("MEIHUA_GOOD_EQUALS_CERTAIN_YES", {"interprets_good_as_certain_yes": True}),
            ],
            "liuyao": [
                ("LIUYAO_YONGSHEN_RESELECTED", {"primary_target": "alternate_target_after_cast"}),
                ("LIUYAO_COMPLETION_CONTRACT_CHANGED", {"completion_rule": "verbal_interest"}),
                ("LIUYAO_RAW_FACT_CHANGED", {"raw_lines": [6, 8, 9, 7, 8, 6]}),
                ("LIUYAO_UNVERIFIED_CALENDAR_EVIDENCE", {"uses_calendar_evidence": True}),
                ("LIUYAO_UNVERIFIED_CALENDAR_EVIDENCE", {"timing_precision": "exact_date"}),
                ("LIUYAO_LAYERS_CONFLATED", {"layers": ["outcome_and_timing"]}),
            ],
        }
        for method, cases in bad.items():
            contract, fact, good = fixed_cases()[method]
            for code, changes in cases:
                with self.subTest(method=method, violation=code):
                    outline = {**copy.deepcopy(good), **changes}
                    self.assertIn(code, review_outline(contract, fact, outline))

    def test_shared_provenance_and_unsupported_probability_fail(self):
        for method, (contract, fact, good) in fixed_cases().items():
            for code, changes in (
                ("QUESTION_IDENTITY_CHANGED", {"question_id": "other-question"}),
                ("CAST_FACT_REPLACED", {"draw_id": "new-cast"}),
                ("OBJECTIVE_PROBABILITY_FROM_SYMBOLS", {"objective_probability_pct": 92}),
                ("GUARANTEED_OUTCOME_FROM_SYMBOLS", {"guaranteed_outcome": True}),
            ):
                with self.subTest(method=method, violation=code):
                    self.assertIn(code, review_outline(contract, fact, {**good, **changes}))

    def test_semantic_contract_is_supported_by_exact_owner_sections(self):
        """Owner anchor drift blocks claims of maintained semantic parity."""
        anchors = {
            "TAROT.md": [
                "這兩種不能混用", "牌位契約", "逆位不要一次疊五種意思",
                "已有牌面時不要重抽",
            ],
            "MEIHUA.md": [
                "主／互／變／體用／動爻的證據角色", "解卦順序",
                "不自動等同 Liuyao-style completion outcome",
                "不作為客觀機率或百分比模型",
            ],
            "LIUYAO.md": [
                "先定用神責任", "Raw Cast ≠ 完整六爻盤",
                "Outcome / Obstacle / Timing 要分層", "calendar facts 已驗證",
            ],
            "CHATGPT_OUTPUT.md": [
                "原題範圍是輸出硬邊界", "先回答原題", "Completion Evidence Guard",
            ],
        }
        for method, owner in (("tarot", "TAROT.md"), ("meihua", "MEIHUA.md"), ("liuyao", "LIUYAO.md")):
            policy = selected_policy(method)
            excerpts = {x["owner"]: x for x in policy["excerpts"]}
            for name in (owner, "CHATGPT_OUTPUT.md"):
                page = get_policy_owner(method, name, offset=0, max_chars=16000)
                self.assertTrue(page["complete"])
                self.assertFalse(excerpts[name]["is_excerpt"])
                self.assertEqual(excerpts[name]["excerpt"], page["text"])
                for phrase in anchors[name]:
                    with self.subTest(method=method, owner=name, phrase=phrase):
                        self.assertIn(phrase, page["text"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
