"""Bounded anonymous transport for stateless divination fact tools.

Deliberately does not authenticate ChatGPT users or read user profiles.
Rate limiting here is process-local defensive friction, NOT a distributed quota.
"""
from __future__ import annotations
import asyncio
import json
import os
import time
from collections import defaultdict, deque
from starlette.responses import JSONResponse

MAX_BODY = 16384
WINDOW_SECONDS = 60
MAX_REQUESTS = 120
_TOOL_NAMES = {
    'runtime_status', 'draw_tarot', 'cast_meihua', 'cast_liuyao',
    'derive_meihua', 'derive_liuyao', 'auto_divination', 'get_interpretation_policy', 'batch_divination',
}


_ADVERTISED_TOOLS = {'runtime_status', 'auto_divination', 'derive_meihua', 'derive_liuyao', 'get_interpretation_policy', 'batch_divination'}

def decorate_tools_list(body: bytes) -> bytes:
    """Only annotate the confirmed tools/list success response, not errors."""
    payload = json.loads(body)
    if not isinstance(payload, dict) or payload.get('jsonrpc') != '2.0':
        raise ValueError('invalid JSON-RPC envelope')
    if 'error' in payload:
        return body
    result = payload.get('result')
    if not isinstance(result, dict) or not isinstance(result.get('tools'), list):
        raise ValueError('missing tools inventory')
    tools = result['tools']
    names = [t.get('name') for t in tools if isinstance(t, dict)]
    if len(names) != len(_TOOL_NAMES) or set(names) != _TOOL_NAMES:
        raise ValueError('tools inventory mismatch')
    for tool in tools:
        # Stateless computation only: no writes, no network search or arbitrary destination.
        annotations = dict(tool.get('annotations') or {})
        annotations.update({'readOnlyHint': True, 'destructiveHint': False,
                            'openWorldHint': False})
        tool['annotations'] = annotations
        tool['securitySchemes'] = [{'type': 'noauth'}]
        meta = tool.setdefault('_meta', {})
        if not isinstance(meta, dict):
            raise ValueError('tool metadata invalid')
        meta['securitySchemes'] = [{'type': 'noauth'}]
    # New ChatGPT tool scans see only the automatic tool as an entry for new
    # stochastic readings; old raw tools remain callable for backward clients.
    result['tools'] = [t for t in tools if t['name'] in _ADVERTISED_TOOLS]
    return json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode()


class PublicGuard:
    def __init__(self, app):
        self.app = app
        self._buckets = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http':
            return await self.app(scope, receive, send)
        path = scope.get('path', '')
        if not (path == '/mcp' or path.startswith('/mcp/')):
            return await self.app(scope, receive, send)

        async def reject(status, code):
            resp = JSONResponse({'error': code}, status_code=status)
            await resp(scope, receive, send)

        method = scope.get('method', '')
        if method not in ('GET', 'POST', 'DELETE'):
            return await reject(405, 'method_not_allowed')
        headers = {k.lower(): v for k, v in scope.get('headers', [])}
        if b'origin' in headers:
            return await reject(403, 'origin_not_allowed')
        if method == 'POST':
            try:
                raw = headers.get(b'content-length')
                if raw is not None:
                    n = int(raw)
                    if n < 0:
                        raise ValueError
                    if n > MAX_BODY:
                        return await reject(413, 'payload_too_large')
            except ValueError:
                return await reject(400, 'invalid_content_length')

        # Source address is the trusted ASGI connection peer. Vercel may place
        # users behind shared proxies; do not trust arbitrary X-Forwarded-For.
        client = scope.get('client') or ('unknown', 0)
        key = str(client[0])
        now = time.monotonic()
        async with self._lock:
            bucket = self._buckets[key]
            while bucket and bucket[0] <= now - WINDOW_SECONDS:
                bucket.popleft()
            if len(bucket) >= MAX_REQUESTS:
                return await reject(429, 'rate_limited')
            bucket.append(now)
            if len(self._buckets) > 4096:
                for k in list(self._buckets)[:2048]:
                    if not self._buckets[k] or self._buckets[k][-1] <= now - WINDOW_SECONDS:
                        del self._buckets[k]

        if method != 'POST':
            return await self.app(scope, receive, send)

        messages = []
        total = 0
        while True:
            message = await receive()
            if message['type'] == 'http.disconnect':
                return
            total += len(message.get('body', b''))
            if total > MAX_BODY:
                return await reject(413, 'payload_too_large')
            messages.append(message)
            if not message.get('more_body'):
                break

        # Inspect only the JSON-RPC method name. Never record user params.
        try:
            raw_data = b''.join(x.get('body', b'') for x in messages)
            request = json.loads(raw_data)
            is_list = (isinstance(request, dict) and request.get('method') == 'tools/list')
        except (ValueError, UnicodeDecodeError):
            is_list = False

        cursor = iter(messages)
        async def replay():
            try: return next(cursor)
            except StopIteration: return {'type':'http.request', 'body':b'', 'more_body':False}
        if not is_list:
            return await self.app(scope, replay, send)

        response_start = None
        response_body = []
        async def capture(message):
            nonlocal response_start
            if message['type'] == 'http.response.start':
                response_start = message
            elif message['type'] == 'http.response.body':
                response_body.append(message.get('body', b''))
                if not message.get('more_body', False):
                    body = b''.join(response_body)
                    code = (response_start or {}).get('status', 200)
                    if code == 200:
                        try: body = decorate_tools_list(body)
                        except (ValueError, TypeError):
                            return await reject(503, 'tool_catalog_unavailable')
                    h = [(k,v) for (k,v) in (response_start or {}).get('headers', []) if k.lower() not in (b'content-length', b'transfer-encoding')]
                    h.append((b'content-length', str(len(body)).encode('ascii')))
                    await send({'type':'http.response.start', 'status':code, 'headers':h})
                    await send({'type':'http.response.body', 'body':body, 'more_body':False})
            else:
                await send(message)
        return await self.app(scope, replay, capture)
