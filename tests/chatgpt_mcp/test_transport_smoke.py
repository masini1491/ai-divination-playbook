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
                if 'selected_method' in candidate:
                    return candidate
                if isinstance(candidate.get('result'), dict) and 'selected_method' in candidate['result']:
                    return candidate['result']
        self.fail('Missing structured cast result in MCP response')

    def test_catalog_exposes_compact_option(self):
        result = self.rpc('tools/list')
        tools = {t['name']: t for t in result['tools']}
        self.assertEqual(set(tools), {'runtime_status', 'auto_divination', 'derive_meihua', 'derive_liuyao'})
        self.assertIn('include_policy_excerpts', tools['auto_divination']['inputSchema']['properties'])

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

    def test_existing_cast_does_not_invoke_bridge(self):
        fake = FakeBridge()
        with patch.object(service, 'ENGINE', fake):
            result = self.extract_cast(self.rpc('tools/call', {
                'name': 'auto_divination',
                'arguments': {'question_summary': '某項合作後續如何發展', 'existing_cast': True,
                              'include_policy_excerpts': False}}, 4))
        self.assertEqual(result['status'], 'existing_cast_preserved')
        self.assertEqual(fake.calls, [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
