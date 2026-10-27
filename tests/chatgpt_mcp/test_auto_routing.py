"""Pure routing and tool-catalog regression tests; no MCP SDK or live cloud needed."""
import json
import sys
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[2] / 'integrations' / 'chatgpt-mcp'
sys.path.insert(0, str(BASE))
from auto_routing import route_plan, route_from_summary, execute_auto_route, ROUTER_VERSION  # noqa: E402
from public_guard import decorate_tools_list  # noqa: E402


class FakeBridge:
    def __init__(self):
        self.calls = []

    def draw_tarot(self, count):
        self.calls.append(("draw_tarot", count))
        return {"cards": [{"id": i} for i in range(count)]}

    def cast_meihua(self):
        self.calls.append(("cast_meihua",))
        return {"primary": "fake_meihua"}

    def cast_liuyao(self):
        self.calls.append(("cast_liuyao",))
        return {"lines": [7, 8, 7, 8, 7, 8]}


class RouterTests(unittest.TestCase):
    def test_psychology_routes_tarot(self):
        p = route_plan('psychology_comparison')
        self.assertEqual((p['status'], p['selected_method'], p['selected_tool']),
                         ('ready', 'tarot', 'draw_tarot'))

    def test_process_routes_meihua(self):
        p = route_plan('process_evolution')
        self.assertEqual(p['selected_method'], 'meihua')

    def test_bounded_outcome_routes_liuyao(self):
        p = route_plan('outcome_completion', has_completion_rule=True, has_horizon=True)
        self.assertEqual(p['selected_tool'], 'cast_liuyao')

    def test_calendar_deadline_without_event_rule_must_clarify(self):
        p = route_plan('outcome_completion', has_horizon=True)
        self.assertEqual((p['status'], p['reason_code']), ('needs_clarification', 'completion_contract_incomplete'))

    def test_event_without_horizon_must_clarify(self):
        p = route_plan('outcome_completion', has_completion_rule=True)
        self.assertEqual(p['status'], 'needs_clarification')

    def test_outcome_without_both_must_clarify(self):
        p = route_plan('outcome_completion')
        self.assertIn('期限', p['question'])

    def test_explicit_tarot_overrides_outcome(self):
        p = route_plan('outcome_completion', method_override='tarot')
        self.assertEqual((p['selected_method'], p['selection_reason']), ('tarot', 'user_method_override'))

    def test_explicit_meihua_overrides_psychology(self):
        self.assertEqual(route_plan('psychology_comparison', method_override='meihua')['selected_method'], 'meihua')

    def test_explicit_liuyao_requires_bounded_contract(self):
        self.assertEqual(route_plan('psychology_comparison', method_override='liuyao')['status'], 'needs_clarification')

    def test_explicit_liuyao_with_contract(self):
        p=route_plan('psychology_comparison', method_override='liuyao',has_completion_rule=True,has_horizon=True)
        self.assertEqual(p['selected_method'], 'liuyao')

    def test_unclear_function_does_not_cast(self):
        p = route_plan('unclear')
        fake = FakeBridge()
        result = execute_auto_route(p, lambda: fake)
        self.assertEqual(result['status'], 'needs_clarification')
        self.assertEqual(fake.calls, [])

    def test_explicit_method_clears_unspecified_function(self):
        self.assertEqual(route_plan('unclear', method_override='tarot')['selected_method'], 'tarot')

    def test_existing_facts_preserved(self):
        fake = FakeBridge()
        p = route_plan('outcome_completion', existing_cast=True, has_completion_rule=True, has_horizon=True)
        self.assertEqual(execute_auto_route(p, lambda: fake)['status'], 'existing_cast_preserved')
        self.assertEqual(fake.calls, [])

    def test_existing_fact_precedes_overrides(self):
        p=route_plan('unclear',method_override='astrology',existing_cast=True)
        self.assertEqual(p['reason_code'],'do_not_redraw')

    def test_astrology_fails_closed(self):
        self.assertEqual(route_plan('psychology_comparison',method_override='astrology')['status'], 'unsupported_method')

    def test_ziwei_fails_closed(self):
        self.assertEqual(route_plan('process_evolution',method_override='ziwei')['status'], 'unsupported_method')

    def test_invalid_method(self):
        self.assertEqual(route_plan('psychology_comparison',method_override='unknown')['status'], 'invalid_input')

    def test_invalid_function(self):
        self.assertEqual(route_plan('other')['reason_code'], 'invalid_judgment_function')

    def test_non_bool_contract_rejected(self):
        self.assertEqual(route_plan('outcome_completion',has_horizon='true')['status'], 'invalid_input')

    def test_count_bounds_rejected(self):
        for n in (0,25,-1,True,3.5):
            with self.subTest(n=n):
                self.assertEqual(route_plan('psychology_comparison',tarot_count=n)['status'], 'invalid_input')

    def test_count_three_default(self):
        self.assertEqual(route_plan('psychology_comparison')['tarot_count'], 3)

    def test_execution_once_tarot(self):
        fake=FakeBridge()
        result=execute_auto_route(route_plan('psychology_comparison',tarot_count=5),lambda:fake)
        self.assertEqual(result['status'],'cast_completed')
        self.assertEqual(fake.calls,[('draw_tarot',5)])
        self.assertEqual(len(result['cast_result']['cards']), 5)

    def test_execution_once_meihua(self):
        fake=FakeBridge()
        result=execute_auto_route(route_plan('process_evolution'),lambda:fake)
        self.assertEqual(result['status'],'cast_completed')
        self.assertEqual(fake.calls,[('cast_meihua',)])

    def test_execution_once_liuyao(self):
        fake=FakeBridge()
        p=route_plan('outcome_completion',has_horizon=True,has_completion_rule=True)
        self.assertEqual(execute_auto_route(p,lambda:fake)['status'],'cast_completed')
        self.assertEqual(fake.calls,[('cast_liuyao',)])

    def test_engine_failure_propagates_no_fake_cast(self):
        class Boom:
            def draw_tarot(self,count): raise RuntimeError('simulated engine down')
        with self.assertRaisesRegex(RuntimeError, 'simulated engine down'):
            execute_auto_route(route_plan('psychology_comparison'),lambda:Boom())

    def test_no_private_question_parameter(self):
        import inspect
        signature=inspect.signature(route_plan)
        self.assertNotIn('question',signature.parameters)
        self.assertNotIn('user_name',signature.parameters)
        self.assertEqual(ROUTER_VERSION,'auto-routing-v2')


class ToolListTests(unittest.TestCase):
    NAMES=('runtime_status','draw_tarot','cast_meihua','cast_liuyao',
           'derive_meihua','derive_liuyao','auto_divination')

    def payload(self,names=NAMES):
        return json.dumps({'jsonrpc':'2.0','id':2,
                           'result':{'tools':[{'name':name,'inputSchema':{'type':'object'}} for name in names]}}).encode()

    def test_seven_registered_four_advertised(self):
        data=json.loads(decorate_tools_list(self.payload()))
        tools=data['result']['tools']
        self.assertEqual(len(tools),4)
        self.assertEqual({t["name"] for t in tools},{"runtime_status","auto_divination","derive_meihua","derive_liuyao"})
        for tool in tools:
            self.assertEqual(tool['securitySchemes'],[{'type':'noauth'}])
            self.assertEqual(tool['_meta']['securitySchemes'],[{'type':'noauth'}])
            self.assertTrue(tool['annotations']['readOnlyHint'])
            self.assertFalse(tool['annotations']['destructiveHint'])
            self.assertFalse(tool['annotations']['openWorldHint'])

    def test_missing_auto_is_denied(self):
        with self.assertRaisesRegex(ValueError,'inventory mismatch'):
            decorate_tools_list(self.payload(self.NAMES[:-1]))

    def test_extra_unknown_is_denied(self):
        with self.assertRaisesRegex(ValueError,'inventory mismatch'):
            decorate_tools_list(self.payload((*self.NAMES,'exfiltrate')))

    def test_error_passthrough(self):
        raw=json.dumps({'jsonrpc':'2.0','id':2,'error':{'code':-1,'message':'error'}}).encode()
        self.assertEqual(decorate_tools_list(raw),raw)




class CompactEvidenceTests(unittest.TestCase):
    """No random cast: verify real question-summary routing and compact policy references."""

    def test_three_intents_without_cast(self):
        cases = (
            ("某人目前對合作關係的主觀看法與動機", {}, "tarot", "draw_tarot"),
            ("某項長期合作未來半年的發展方向與轉折", {}, "meihua", "cast_meihua"),
            ("某項申請是否於2026年11月15日前收到正式核准通知",
             {"has_completion_rule": True, "has_horizon": True}, "liuyao", "cast_liuyao"),
        )
        for summary, flags, method, tool in cases:
            with self.subTest(method=method):
                plan = route_from_summary(summary, method_override="auto", **flags)
                self.assertEqual(plan["status"], "ready")
                self.assertEqual(plan["selected_method"], method)
                self.assertEqual(plan["selected_tool"], tool)
                self.assertEqual(plan["routing_source"], "server_question_summary")
                self.assertNotIn("cast_result", plan)

    def test_compact_policy_reference_no_owner_text(self):
        from policy_adapter import selected_policy_reference, policy_identity
        reference = selected_policy_reference("meihua")
        identity = policy_identity()
        self.assertEqual(reference["method"], "meihua")
        self.assertEqual(reference["excerpts"], [])
        for key, value in identity.items():
            self.assertEqual(reference[key], value)
        self.assertNotIn("content", str(reference))


    def test_compact_payload_preserves_cast_and_drops_excerpts(self):
        # Isolated service-level formatter; fake cast evidence, no RNG call.
        from response_format import method_policy_output
        from policy_adapter import selected_policy, selected_policy_reference
        cast = {"cards": [{"name": "fixture", "orientation": "upright"}]}
        base = {"selected_method": "tarot", "status": "cast_completed", "cast_result": cast}
        full = method_policy_output(base, include_policy_excerpts=True)
        compact = method_policy_output(base, include_policy_excerpts=False)
        self.assertEqual(full["cast_result"], compact["cast_result"])
        self.assertEqual(compact["cast_result"], cast)
        self.assertEqual(full["method_policy"], selected_policy("tarot"))
        self.assertEqual(compact["method_policy"], selected_policy_reference("tarot"))
        self.assertEqual(compact["method_policy"]["excerpts"], [])
        self.assertTrue(full["method_policy"]["excerpts"])
        self.assertEqual(base, {"selected_method": "tarot", "status": "cast_completed", "cast_result": cast})

    def test_no_cast_response_remains_without_policy(self):
        from response_format import method_policy_output
        original = {"status": "needs_clarification", "reason_code": "question_identity_missing"}
        self.assertEqual(method_policy_output(original, False), original)

    def test_compact_reference_rejects_unsupported_method(self):
        from policy_adapter import selected_policy_reference
        with self.assertRaises(ValueError):
            selected_policy_reference("palmistry")

if __name__ == '__main__':
    unittest.main(verbosity=2)
