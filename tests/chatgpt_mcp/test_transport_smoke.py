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
        self.assertEqual(set(tools), {'runtime_status', 'auto_divination', 'derive_meihua', 'derive_liuyao', 'get_interpretation_policy'})
        self.assertIn('include_policy_excerpts', tools['auto_divination']['inputSchema']['properties'])
        self.assertIn('owner', tools['get_interpretation_policy']['inputSchema']['properties'])

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
