"""Read verified, allowlisted method-owner excerpts shipped with the release.

Canonical interpretation and governance always originate in the pinned repo,
not in locally invented interpretations. No runtime network or GitHub fetch.
"""
from __future__ import annotations
import hashlib
import json
from functools import lru_cache
from pathlib import Path

BASE = Path(__file__).resolve().parent
METHOD_OWNERS = {'tarot': 'TAROT.md', 'meihua': 'MEIHUA.md', 'liuyao': 'LIUYAO.md'}
COMMON = (
    ('METHOD_ROUTING.md', 3800),
    ('QUESTION_DESIGN.md', 2500),
    ('READING_LIFECYCLE.md', 1700),
    ('CHATGPT_OUTPUT.md', 1800),
)

@lru_cache(maxsize=1)
def _bundle() -> dict:
    payload = json.loads((BASE / 'policy_pack.json').read_text(encoding='utf-8'))
    if payload.get('profile_id') != 'chatgpt-mcp-tarot-meihua-liuyao-v1':
        raise RuntimeError('POLICY_PROFILE_MISMATCH')
    if not isinstance(payload.get('owners'), dict):
        raise RuntimeError('POLICY_PACK_INVALID')
    for owner, entry in payload['owners'].items():
        text = entry['content']
        data = text.encode('utf-8')
        if entry['sha256'] != hashlib.sha256(data).hexdigest() or entry['bytes'] != len(data):
            raise RuntimeError(f'POLICY_DIGEST_MISMATCH: {owner}')
    return payload

def policy_identity() -> dict:
    pack = _bundle()
    return {'source_commit': pack['source_commit'], 'profile_id': pack['profile_id'],
            'policy_pack_sha256': hashlib.sha256((BASE/'policy_pack.json').read_bytes()).hexdigest(),
            'policy_owner_count': len(pack['owners'])}

def selected_policy(method: str | None) -> dict:
    """Return bounded, exact excerpts; label clearly that text may be truncated."""
    pack = _bundle()
    if method not in METHOD_OWNERS:
        return {'source_commit': pack['source_commit'], 'profile_id': pack['profile_id'],
                'method': method, 'excerpts': []}
    specs = (*COMMON, (METHOD_OWNERS[method], 7000))
    excerpts = []
    for name, max_chars in specs:
        owner = pack['owners'][name]
        text = owner['content']
        excerpts.append({'owner': name, 'sha256': owner['sha256'],
                         'excerpt': text[:max_chars], 'is_excerpt': len(text) > max_chars})
    return {'source_commit': pack['source_commit'], 'profile_id': pack['profile_id'],
            'method': method, 'excerpts': excerpts,
            'note': 'Exact canonical excerpts, not full owner contents. Do not infer omitted sections.'}
