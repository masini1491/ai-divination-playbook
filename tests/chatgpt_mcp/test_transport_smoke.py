"""Local JSON-RPC/Streamable HTTP smoke with a fake bridge; never draws real cards.

The TestClient sends requests to the in-process ASGI app. It never contacts
Vercel, user accounts, or the production MCP service.
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2] / 'integrations' / 'chatgpt-mcp'
sys.path.insert(0, str(ROOT))
import app as service  # noqa: E402


class FakeBridge:
    def __init__(self):
        self.calls = []

    def revalidate_source(self):
        return None

    def draw_tarot(self, count):
        self.calls.append(('tarot', count))
        return {'fixture_only': 'tarot', 'cards': [{'id': i} for i in range(count)]}

    def cast_meihua(self):
        self.calls.append(('meihua',))
        return {'fixture_only': 'meihua', 'hexagram': 'fixture'}

    def cast_liuyao(self):
        self.calls.append(('liuyao',))
        return {'fixture_only': 'liuyao', 'lines': [7, 8, 7, 8, 7, 8]}


class MCPTransportSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(service.app, base_url='http://localhost')
        cls.client.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.client.__exit__(None, None, None)

    def rpc(self, method, params=None, rpc_id=1):
        body = {'jsonrpc': '2.0', 'id': rpc_id, 'method': method}
        if params is not None:
            body['params'] = params
        result = self.client.post('/mcp', json=body, headers={
            'Accept': 'application/json, text/event-stream',
            'MCP-Protocol-Version': '2025-06-18',
        })
        self.assertEqual(result.status_code, 200, result.text[:500])
        payload = result.json()
        self.assertNotIn('error', payload)
        return payload['result']

    def extract_cast(self, result):
        """MCP Python SDK can return structured content or JSON text content."""
        candidates = [result.get('structuredContent')]
        candidates.extend(part.get('text') for part in result.get('content', []) if isinstance(part, dict))
        for candidate in candidates:
            if isinstance(candidate, str):
                try:
                    candidate = json.loads(candidate)
                except ValueError:
                    continue
            if isinstance(candidate, dict):
                if 'selected_method' in candidate or candidate.get('status') == 'existing_cast_preserved':
                    return candidate
                if isinstance(candidate.get('result'), dict):
                    nested = candidate['result']
                    if 'selected_method' in nested or nested.get('status') == 'existing_cast_preserved':
                        return nested
        self.fail('Missing structured cast result in MCP response')

    def test_catalog_exposes_compact_option(self):
        result = self.rpc('tools/list')
        tools = {t['name']: t for t in result['tools']}
        self.assertEqual(set(tools), {'runtime_status', 'auto_divination', 'derive_meihua', 'derive_liuyao', 'get_interpretation_policy', 'batch_divination', 'plan_batch_chunks'})
        self.assertIn('include_policy_excerpts', tools['auto_divination']['inputSchema']['properties'])
        self.assertIn('owner', tools['get_interpretation_policy']['inputSchema']['properties'])
        self.assertIn('items', tools['batch_divination']['inputSchema']['properties'])
        self.assertIn('expected_request_sha256',
                      tools['batch_divination']['inputSchema']['properties'])
        self.assertIn('chunk_size', tools['plan_batch_chunks']['inputSchema']['properties'])

    def test_runtime_status_advertises_web_plugin_policy_parity_version(self):
        response = self.rpc('tools/call', {
            'name': 'runtime_status', 'arguments': {}}, 11)
        candidates = [response.get('structuredContent')]
        candidates.extend(item.get('text') for item in response.get('content', [])
                          if isinstance(item, dict))
        status = next((obj for candidate in candidates
                       if (obj := json.loads(candidate) if isinstance(candidate, str) else candidate)
                       and isinstance(obj, dict) and 'interpretation_policy_version' in obj), None)
        self.assertIsNotNone(status)
        self.assertEqual(status['interpretation_policy_version'], 'canonical-owner-parity-v1')
        self.assertEqual(status['mcp_runtime_version'], service.MCP_RUNTIME_VERSION)
        capabilities = status['interpretation_policy_capabilities']
        self.assertEqual(capabilities['policy_read_tool'], 'get_interpretation_policy')
        self.assertTrue(capabilities['complete_method_owner_by_default'])
        self.assertTrue(capabilities['complete_output_contract_by_default'])
        self.assertTrue(capabilities['existing_cast_preserves_facts_and_method_policy'])
        self.assertEqual(capabilities['enabled_methods'], ['tarot', 'meihua', 'liuyao'])

    def test_compact_transport_preserves_fixture_cast_and_source(self):
        fake = FakeBridge()
        args = {'question_summary': '某人對合作關係的看法與動機', 'method_override': 'auto'}
        with patch.object(service, 'ENGINE', fake):
            default = self.extract_cast(self.rpc('tools/call', {'name': 'auto_divination', 'arguments': args}, 2))
            compact = self.extract_cast(self.rpc('tools/call', {'name': 'auto_divination', 'arguments': {
                **args, 'include_policy_excerpts': False}}, 3))
        self.assertEqual(fake.calls, [('tarot', 3), ('tarot', 3)])
        self.assertEqual(default['status'], 'cast_completed')
        self.assertEqual(compact['status'], 'cast_completed')
        self.assertEqual(default['cast_result'], compact['cast_result'])
        self.assertEqual(default['routing_source'], 'server_question_summary')
        self.assertTrue(default['method_policy']['excerpts'])
        self.assertEqual(compact['method_policy']['excerpts'], [])
        self.assertEqual(default['method_policy']['source_commit'], compact['method_policy']['source_commit'])

    def test_existing_cast_keeps_full_rules_without_recasing(self):
        from policy_adapter import _bundle, METHOD_OWNERS
        fake = FakeBridge()
        pack = _bundle()
        with patch.object(service, 'ENGINE', fake):
            for method in ('tarot', 'meihua', 'liuyao'):
                with self.subTest(method=method):
                    response = self.rpc('tools/call', {
                        'name': 'auto_divination',
                        'arguments': {'question_summary': '',
                                      'method_override': method,
                                      'existing_cast': True}})
                    result = self.extract_cast(response)
                    self.assertEqual(result['status'], 'existing_cast_preserved')
                    self.assertNotIn('cast_result', result)
                    self.assertEqual(result['selected_method'], method)
                    policy = result['method_policy']
                    owners = {x['owner']: x for x in policy['excerpts']}
                    self.assertEqual(owners[METHOD_OWNERS[method]]['excerpt'],
                                     pack['owners'][METHOD_OWNERS[method]]['content'])
                    self.assertEqual(owners['CHATGPT_OUTPUT.md']['excerpt'],
                                     pack['owners']['CHATGPT_OUTPUT.md']['content'])
                    self.assertNotIn('LIUYAO.md' if method=='tarot' else
                                     'TAROT.md', owners)
        self.assertEqual(fake.calls, [])

    def test_existing_cast_does_not_invoke_bridge(self):
        fake = FakeBridge()
        with patch.object(service, 'ENGINE', fake):
            result = self.extract_cast(self.rpc('tools/call', {
                'name': 'auto_divination',
                'arguments': {'question_summary': '某項合作後續如何發展', 'existing_cast': True,
                              'include_policy_excerpts': False}}, 4))
        self.assertEqual(result['status'], 'existing_cast_preserved')
        self.assertEqual(fake.calls, [])


    def extract_policy(self, result):
        """Read canonical owner response from MCP structured/text content."""
        candidates = [result.get('structuredContent')]
        candidates.extend(part.get('text') for part in result.get('content', [])
                          if isinstance(part, dict))
        for value in candidates:
            if isinstance(value, str):
                try:
                    value = json.loads(value)
                except ValueError:
                    continue
            if isinstance(value, dict):
                if 'owner' in value and 'text' in value:
                    return value
                if isinstance(value.get('result'), dict):
                    nested = value['result']
                    if 'owner' in nested and 'text' in nested:
                        return nested
        self.fail('Missing canonical interpretation policy in MCP response')

    def test_acknowledged_chunk_plan_is_no_draw_over_mcp_transport(self):
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from test_batch_cast import mixed_twelve
        from test_chunk_plan import _digest
        fake = FakeBridge()
        with patch.object(service, 'ENGINE', fake):
            response=self.rpc('tools/call',{'name':'plan_batch_chunks',
                              'arguments':{'items':mixed_twelve(),'chunk_size':3}},16)
        value=response.get('structuredContent')
        if value is None:
            value=next((x.get('text') for x in response.get('content',[])
                        if isinstance(x,dict) and 'text' in x),None)
        if isinstance(value,str): value=json.loads(value)
        if isinstance(value,dict): value=value.get('result',value)
        self.assertEqual(value['status'],'planned_no_cast')
        self.assertEqual(value['chunk_count'],4)
        self.assertEqual([len(x['items']) for x in value['chunks']],[3,3,3,3])
        self.assertEqual(fake.calls,[])

    def test_hash_gated_chunks_over_mcp_transport(self):
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from test_batch_cast import mixed_twelve, FakeBridge
        spy=FakeBridge()
        with patch.object(service,'ENGINE',spy):
            plan_result=self.rpc('tools/call',{'name':'plan_batch_chunks',
                                   'arguments':{'items':mixed_twelve(),'chunk_size':3}},35)
            plan=plan_result.get('structuredContent')
            if plan is None:
                plan=next(x['text'] for x in plan_result.get('content',[]) if 'text' in x)
            if isinstance(plan,str): plan=json.loads(plan)
            plan=plan.get('result',plan)
            first=plan['chunks'][0]
            result=self.rpc('tools/call',{'name':'batch_divination',
                'arguments':{'items':first['items'],
                             'expected_request_sha256':first['request_sha256']}},36)
            payload=result.get('structuredContent')
            if payload is None:
                payload=next(x['text'] for x in result.get('content',[]) if 'text' in x)
            if isinstance(payload,str): payload=json.loads(payload)
            payload=payload.get('result',payload)
        self.assertEqual(payload['status'],'batch_completed')
        self.assertEqual(payload['completed_count'],3)
        self.assertEqual(payload['request_sha256'],first['request_sha256'])
        self.assertEqual(spy.calls,['tarot','liuyao','meihua'])

    def test_twelve_mixed_interleaved_receipts_over_mcp_transport(self):
        # The exact ChatGPT-facing tools/call interface, not just pure helpers.
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from test_batch_cast import FakeBridge, mixed_twelve
        spy = FakeBridge()
        with patch.object(service, 'ENGINE', spy):
            result = self.rpc('tools/call', {
                'name': 'batch_divination',
                'arguments': {'items': mixed_twelve()}}, 17)
        candidates = [result.get('structuredContent')]
        candidates.extend(part.get('text') for part in result.get('content', [])
                          if isinstance(part, dict))
        payload = None
        for value in candidates:
            if isinstance(value, str):
                try:
                    value = json.loads(value)
                except ValueError:
                    continue
            if isinstance(value, dict):
                value = value.get('result', value)
                if isinstance(value, dict) and value.get('status') == 'batch_completed':
                    payload = value
                    break
        self.assertIsNotNone(payload, result)
        self.assertEqual(payload['completed_count'], 12)
        self.assertEqual(payload['total_count'], 12)
        self.assertEqual(len(payload['receipts']), 12)
        self.assertEqual(len({item['receipt_id'] for item in payload['receipts']}), 12)
        self.assertEqual([r['selected_method'] for r in payload['receipts']],
                         [item['method_override'] for item in mixed_twelve()])
        self.assertNotIn('excerpts', str(payload))
        self.assertEqual(len(spy.calls), 12)

    def test_actual_pinned_bridge_twelve_receipts_through_mcp_transport(self):
        # This is the actual MCP HTTP transport plus actual pinned engines;
        # ONLY randomness is replaced with a deterministic zero fixture.
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from test_batch_cast import mixed_twelve
        with patch.object(service.ENGINE.core, 'randbelow', side_effect=lambda limit: 0):
            result = self.rpc('tools/call', {
                'name': 'batch_divination',
                'arguments': {'items': mixed_twelve()}}, 18)
        payload = self.extract_cast(result) if 'selected_method' in result else None
        if payload is None:
            candidates = [result.get('structuredContent')]
            candidates.extend(part.get('text') for part in result.get('content', [])
                              if isinstance(part, dict))
            for candidate in candidates:
                if isinstance(candidate, str):
                    try:
                        candidate = json.loads(candidate)
                    except ValueError:
                        continue
                if isinstance(candidate, dict):
                    candidate = candidate.get('result', candidate)
                    if isinstance(candidate, dict) and candidate.get('status') == 'batch_completed':
                        payload = candidate
                        break
        self.assertIsNotNone(payload, result)
        self.assertEqual(payload['completed_count'], 12)
        self.assertEqual(len(payload['receipts']), 12)
        from bridge import SOURCE_COMMIT
        self.assertTrue(all(x['source']['runtime_source_commit'] == SOURCE_COMMIT
                            for x in payload['receipts']))
        self.assertTrue(all(x['receipt_sha256']
                            for x in payload['receipts']))
        # Structural receipts are intentionally much smaller than a full
        # twelve-chart result with the repeated interpretation rule text.
        self.assertLess(len(json.dumps(result,ensure_ascii=False).encode('utf-8')),
                        80000)

    def test_ten_interleaved_mcp_calls_preserve_each_original_cast(self):
        """Ten sequential HTTP MCP tool calls, >=10 new casts, mixed tool types.

        Uses exact bundled engines and fixed test-only randomness; no real
        person or live prediction. Keep every receipt before the next call.
        """
        import hashlib
        from test_batch_cast import labeled
        timestamp = "2026-10-28T20:20:31+08:00"
        saved = []
        single_casts = []
        sequence = (
            ("batch_divination", {"items": [labeled("tarot", 0), labeled("liuyao", 1)]}),
            ("auto_divination", {"question_summary": "某項合作後續發展",
                                "method_override": "meihua", "include_policy_excerpts": False}),
            ("derive_liuyao", {"raw_lines": [7, 8, 9, 7, 8, 6], "cast_timestamp": timestamp}),
            ("batch_divination", {"items": [labeled("meihua", 2), labeled("tarot", 3)]}),
            ("auto_divination", {"question_summary": "比較兩個方案",
                                "method_override": "tarot", "include_policy_excerpts": False}),
            ("get_interpretation_policy", {"method": "tarot", "owner": "CHATGPT_OUTPUT.md",
                                           "offset": 0, "max_chars": 16000}),
            ("batch_divination", {"items": [labeled("liuyao", 4), labeled("meihua", 5)]}),
            ("auto_divination", {"question_summary": "一個月內是否正式見面",
                                "method_override": "liuyao", "has_completion_rule": True,
                                "has_horizon": True, "include_policy_excerpts": False}),
            ("derive_meihua", {"a": "175", "b": "196"}),
            ("batch_divination", {"items": [labeled("tarot", 6), labeled("liuyao", 7)]}),
        )
        def unpack(result):
            for candidate in [result.get("structuredContent"), *(
                    x.get("text") for x in result.get("content", []) if isinstance(x, dict))]:
                if isinstance(candidate, str):
                    try: candidate = json.loads(candidate)
                    except ValueError: continue
                if isinstance(candidate, dict):
                    return candidate.get("result", candidate)
            self.fail("Missing MCP tool result")
        with patch.object(service.ENGINE.core, "randbelow", side_effect=lambda n: 0):
            for index, (tool, arguments) in enumerate(sequence, 1):
                result = self.rpc("tools/call", {"name": tool, "arguments": arguments},
                                  100 + index)
                self.assertFalse(result.get("isError"), (tool, result))
                payload = unpack(result)
                if tool == "batch_divination":
                    self.assertEqual(payload["status"], "batch_completed")
                    self.assertEqual(payload["completed_count"], 2)
                    for receipt in payload["receipts"]:
                        self.assertEqual(receipt["batch_id"], payload["batch_id"])
                        self.assertEqual(receipt["receipt_format"] if "receipt_format" in receipt
                                         else payload["receipt_format"],
                                         "compact-original-cast-v2")
                        self.assertNotIn("excerpts", receipt)
                        saved.append(receipt)
                elif tool == "auto_divination":
                    self.assertEqual(payload["status"], "cast_completed")
                    self.assertEqual(payload["method_policy"]["excerpts"], [])
                    single_casts.append(payload)
                elif tool == "get_interpretation_policy":
                    self.assertEqual(payload["owner"], "CHATGPT_OUTPUT.md")
                    self.assertTrue(payload["complete"])
                else:
                    self.assertEqual(payload["fact_source"], "user_supplied")
                # Prior receipts must remain unchanged across every subsequent
                # call and must not be mutated by later deterministic derivation.
                for receipt in saved:
                    self.assertEqual(receipt["receipt_sha256"],
                                     __import__("batch_cast")._stable_hash({
                                         k: v for k, v in receipt.items()
                                         if k != "receipt_sha256"}))
        self.assertEqual(len(sequence), 10)
        self.assertEqual(len(saved), 8)
        self.assertEqual(len(single_casts), 3)
        self.assertEqual(len(saved) + len(single_casts), 11)
        self.assertEqual(len({r["receipt_id"] for r in saved}), 8)
        self.assertEqual(len({r["batch_id"] for r in saved}), 4)
        self.assertEqual([r["selected_method"] for r in saved],
                         ["tarot", "liuyao", "meihua", "tarot",
                          "liuyao", "meihua", "tarot", "liuyao"])
        self.assertEqual([r["selected_method"] for r in single_casts],
                         ["meihua", "tarot", "liuyao"])

    def test_full_canonical_policy_reaches_chatgpt_for_all_three_methods(self):
        from policy_adapter import _bundle, METHOD_OWNERS
        pack = _bundle()
        cases = (
            ('tarot', '某人對合作的想法與動機', {}),
            ('meihua', '某項合作接下來怎麼發展', {}),
            ('liuyao', '某項申請是否於2026年11月15日前取得正式核准',
             {'has_completion_rule': True, 'has_horizon': True}),
        )
        fake = FakeBridge()
        with patch.object(service, 'ENGINE', fake):
            for method, summary, flags in cases:
                with self.subTest(method=method):
                    response = self.rpc('tools/call', {'name': 'auto_divination', 'arguments': {
                        'question_summary': summary, 'method_override': method,
                        **flags}})
                    result = self.extract_cast(response)
                    self.assertEqual(result['status'], 'cast_completed')
                    self.assertEqual(result['selected_method'], method)
                    policy = result['method_policy']
                    self.assertEqual(policy['source_commit'], pack['source_commit'])
                    self.assertEqual(set(policy['required_full_owners']),
                                     {METHOD_OWNERS[method], 'CHATGPT_OUTPUT.md'})
                    excerpts = {x['owner']: x for x in policy['excerpts']}
                    for owner in (METHOD_OWNERS[method], 'CHATGPT_OUTPUT.md'):
                        self.assertEqual(excerpts[owner]['excerpt'], pack['owners'][owner]['content'])
                        self.assertFalse(excerpts[owner]['is_excerpt'])
        self.assertEqual([call[0] for call in fake.calls], ['tarot', 'meihua', 'liuyao'])

    def test_paginated_policy_over_transport_preserves_exact_hash_and_no_cast(self):
        import hashlib
        from policy_adapter import _bundle
        pack = _bundle()
        target = pack['owners']['LIUYAO.md']
        fake = FakeBridge()
        offset = 0
        chunks = []
        with patch.object(service, 'ENGINE', fake):
            for _ in range(12):
                response = self.rpc('tools/call', {
                    'name': 'get_interpretation_policy',
                    'arguments': {'method': 'liuyao', 'owner': 'LIUYAO.md',
                                  'offset': offset, 'max_chars': 1357}})
                self.assertFalse(response.get('isError', False))
                page = self.extract_policy(response)
                self.assertEqual(page['source_commit'], pack['source_commit'])
                self.assertEqual(page['sha256'], target['sha256'])
                self.assertEqual(page['offset'], offset)
                chunks.append(page['text'])
                if page['next_offset'] is None:
                    self.assertEqual(page['total_chars'], offset + len(page['text']))
                    break
                offset = page['next_offset']
            else:
                self.fail('Policy pagination did not terminate')
        self.assertEqual(''.join(chunks), target['content'])
        self.assertEqual(hashlib.sha256(''.join(chunks).encode('utf-8')).hexdigest(),
                         target['sha256'])
        self.assertEqual(fake.calls, [])

    def test_invalid_policy_owner_fails_at_mcp_boundary_without_cast(self):
        fake = FakeBridge()
        with patch.object(service, 'ENGINE', fake):
            for method, owner in (('tarot', 'ASTROLOGY.md'),
                                  ('liuyao', '../../README.md'),
                                  ('ziwei', 'LIUYAO.md'),
                                  ('tarot', 'LIUYAO.md'),
                                  ('meihua', 'TAROT.md'),
                                  ('liuyao', 'MEIHUA.md')):
                with self.subTest(method=method, owner=owner):
                    response = self.rpc('tools/call', {
                        'name': 'get_interpretation_policy',
                        'arguments': {'method': method, 'owner': owner}})
                    self.assertTrue(response.get('isError'), response)
        self.assertEqual(fake.calls, [])

    def test_policy_validation_failure_prevents_rng(self):
        from unittest.mock import patch as mock_patch
        import policy_adapter
        fake = FakeBridge()
        with mock_patch.object(service, 'ENGINE', fake), \
             mock_patch.object(policy_adapter, '_bundle',
                               side_effect=RuntimeError('POLICY_DIGEST_MISMATCH')):
            response = self.rpc('tools/call', {'name': 'auto_divination',
                'arguments': {'question_summary': '某人對合作的想法與動機',
                              'method_override': 'tarot'}})
        self.assertTrue(response.get('isError'), response)
        self.assertEqual(fake.calls, [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
