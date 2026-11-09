"""No-randomness policy-first routing regression and MCP execution contracts."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

BASE = Path(__file__).resolve().parents[2] / "integrations" / "chatgpt-mcp"
sys.path.insert(0, str(BASE))

from policy_first_routing import routing_identity, route_from_policy
from auto_routing import execute_auto_route
from chunk_plan import plan_chunks
from batch_cast import validate_batch, BatchClarificationRequired, execute_batch, _stable_hash
from policy_adapter import _bundle
import app as service


def decision(method="tarot", function="psychology_comparison", basis="policy_routing",
             completion=False, horizon=False):
    identity = routing_identity()
    return {"source_commit": identity["source_commit"],
            "policy_sha256": identity["policy_sha256"],
            "selected_method": method, "judgment_function": function,
            "selection_basis": basis, "has_completion_rule": completion,
            "has_horizon": horizon}


class FakeBridge:
    def __init__(self):
        self.calls = []

    def draw_tarot(self, count):
        self.calls.append(("tarot", count))
        return {"test": "tarot"}

    def cast_meihua(self):
        self.calls.append(("meihua",))
        return {"test": "meihua"}

    def cast_liuyao(self):
        self.calls.append(("liuyao",))
        return {"test": "liuyao"}


class PolicyFirstRoutingTests(unittest.TestCase):
    def test_read_full_verified_manual_with_pinned_identity(self):
        pack = _bundle()
        p = service.get_routing_policy()
        owner = pack["owners"]["METHOD_ROUTING.md"]
        self.assertEqual(p["text"], owner["content"])
        self.assertEqual(p["policy_sha256"], owner["sha256"])
        self.assertEqual(p["source_commit"], pack["source_commit"])
        self.assertTrue(p["complete"])
        self.assertGreater(len(p["text"]), 8000)

    def test_policy_first_methods_not_server_keyword_classification(self):
        for method, function, summary in (
            ("tarot", "psychology_comparison", "某項方案主觀適配度的比較"),
            ("meihua", "process_evolution", "某項合作的階段轉折"),
            ("liuyao", "outcome_completion", "某項申請期限內是否核准"),
        ):
            with self.subTest(method=method):
                d = decision(method, function, completion=method == "liuyao",
                             horizon=method == "liuyao")
                p = route_from_policy(summary, d)
                self.assertEqual(p["status"], "ready")
                self.assertEqual(p["selected_method"], method)
                self.assertEqual(p["routing_source"], "client_canonical_policy_read")
                self.assertEqual(len(p["route_request_sha256"]), 64)

    def test_no_text_classification_override_rewriting(self):
        # The server must not silently override a policy-approved method
        # because a phrase also matches its legacy regex classifier.
        p = route_from_policy("某項合作是否應該調整與發展", decision("tarot"))
        self.assertEqual(p["selected_method"], "tarot")
        self.assertEqual(p["selection_reason"], "policy_routing")

    def test_explicit_method_override_and_no_auto_fallback(self):
        p = route_from_policy(
            "用塔羅看某事件是否順利",
            decision("tarot", "outcome_completion", "user_method_override"))
        self.assertEqual((p["status"], p["selected_method"]), ("ready", "tarot"))
        bad = route_from_policy("使用占星判斷",
                                decision("astrology", "unclear", "user_method_override"))
        self.assertEqual(bad["status"], "unsupported_method")

    def test_invalid_or_stale_source_never_draws(self):
        fake = FakeBridge()
        for key, value in (("source_commit", "0" * 40),
                           ("policy_sha256", "0" * 64),
                           ("selected_method", "ziwei"),
                           ("selected_method", ["tarot"])):
            with self.subTest(key=key, value=value):
                d = decision()
                d[key] = value
                p = route_from_policy("某人目前如何看待合作", d)
                self.assertNotEqual(p["status"], "ready")
                self.assertEqual(execute_auto_route(p, lambda: fake), p)
        self.assertEqual(fake.calls, [])

    def test_inconsistent_function_and_bad_flags_never_draw(self):
        fake = FakeBridge()
        bad = [
            decision("tarot", "process_evolution"),
            decision("meihua", "unclear"),
            decision("liuyao", "outcome_completion", completion=False, horizon=True),
            decision("liuyao", "outcome_completion", completion=True, horizon=False),
            {**decision(), "has_horizon": "true"},
            {**decision(), "unexpected": True},
            {**decision(), "selection_basis": "model_guessed"},
        ]
        for d in bad:
            with self.subTest(d=d):
                p = route_from_policy("某項匿名事件的測試", d)
                self.assertIn(p["status"], {"invalid_input", "needs_clarification"})
                execute_auto_route(p, lambda: fake)
        self.assertEqual(fake.calls, [])

    def test_no_private_contact_or_empty_summary(self):
        for summary in ("", "https://example.com", "請聯繫0912345678"):
            p = route_from_policy(summary, decision())
            self.assertEqual(p["status"], "invalid_input")

    def test_single_service_uses_fake_bridge_once(self):
        fake = FakeBridge()
        with patch.object(service, "_bridge", lambda: fake):
            cast = service.policy_divination("某項計畫的適配比較", decision())
            missing = service.policy_divination(
                "某事件核准與否",
                decision("liuyao", "outcome_completion", completion=True))
        self.assertEqual(cast["status"], "cast_completed")
        self.assertEqual(cast["selected_method"], "tarot")
        self.assertEqual(missing["status"], "needs_clarification")
        self.assertEqual(fake.calls, [("tarot", 3)])

    def test_batch_requires_policy_decision_and_has_no_legacy_autoroute(self):
        items = [
            {"label": "T1", "question_summary": "方案適配比較",
             "route_decision": decision()},
            {"label": "M2", "question_summary": "合作關係轉折",
             "route_decision": decision("meihua", "process_evolution")},
        ]
        plans = validate_batch(items, policy_first=True)
        self.assertEqual([x["plan"]["selected_method"] for x in plans], ["tarot", "meihua"])
        self.assertEqual(plan_chunks(items, policy_first=True)["routing_mode"], "policy-first-v1")
        bad = [{**items[0], "method_override": "auto"}]
        with self.assertRaisesRegex(ValueError, "POLICY_FIRST_ROUTE_REQUIRED"):
            validate_batch(bad, policy_first=True)
        with self.assertRaisesRegex(ValueError, "POLICY_FIRST_ROUTE_REQUIRED"):
            validate_batch([{"label": "T1", "question_summary": "比較"}], policy_first=True)
        with self.assertRaisesRegex(ValueError, "POLICY_FIRST_API_REQUIRED"):
            validate_batch(items, policy_first=False)

    def test_chunk_keeps_exact_decision_and_digest_unchanged(self):
        items = [
            {"label": "T1", "question_summary": "方案適配比較",
             "route_decision": decision()},
            {"label": "L2", "question_summary": "期限內是否完成申請",
             "route_decision": decision("liuyao", "outcome_completion", completion=True, horizon=True)},
        ]
        plan = plan_chunks(items, chunk_size=1, policy_first=True)
        self.assertEqual(plan["status"], "planned_no_cast")
        self.assertIn("Call policy_batch_divination", plan["instructions"])
        self.assertNotIn("Call batch_divination", plan["instructions"])
        self.assertEqual(plan["chunk_count"], 2)
        for index, ch in enumerate(plan["chunks"]):
            self.assertEqual(ch["items"][0]["route_decision"], items[index]["route_decision"])
            self.assertNotIn("method_override", ch["items"][0])
            self.assertEqual(ch["request_sha256"], _stable_hash(ch["items"]))
            self.assertEqual(validate_batch(ch["items"], policy_first=True)[0]["plan"]["status"], "ready")
        with self.assertRaisesRegex(ValueError, "CHUNK_REQUEST_DIGEST_MISMATCH"):
            execute_batch(items[:1], lambda: FakeBridge(),
                          expected_request_sha256="0" * 64, policy_first=True)

    def test_bad_second_batch_item_blocks_every_cast(self):
        items = [
            {"label": "T1", "question_summary": "方案適配比較", "route_decision": decision()},
            {"label": "L2", "question_summary": "期限內是否完成",
             "route_decision": decision("liuyao", "outcome_completion", completion=True)},
        ]
        fake = FakeBridge()
        with self.assertRaises(BatchClarificationRequired):
            execute_batch(items, lambda: fake, policy_first=True)
        self.assertEqual(fake.calls, [])

    def test_policy_integrity_fail_closed_before_rng(self):
        fake = FakeBridge()
        with patch("policy_first_routing._bundle", side_effect=RuntimeError("POLICY_DIGEST_MISMATCH")):
            with self.assertRaisesRegex(RuntimeError, "POLICY_DIGEST_MISMATCH"):
                service.policy_divination("匿名比較", decision())
        self.assertEqual(fake.calls, [])


if __name__ == "__main__":
    unittest.main()
