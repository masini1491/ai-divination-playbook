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
    ('CHATGPT_OUTPUT.md', None),
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
    specs = (*COMMON, (METHOD_OWNERS[method], None))
    excerpts = []
    for name, max_chars in specs:
        owner = pack['owners'][name]
        text = owner['content']
        excerpt = text if max_chars is None else text[:max_chars]
        excerpts.append({'owner': name, 'sha256': owner['sha256'],
                         'excerpt': excerpt, 'is_excerpt': len(text) > len(excerpt),
                         'total_chars': len(text)})
    return {'source_commit': pack['source_commit'], 'profile_id': pack['profile_id'],
            'method': method, 'excerpts': excerpts,
            'required_full_owners': [METHOD_OWNERS[method], 'CHATGPT_OUTPUT.md'],
            'conditional_owners': [name for name in pack['owners'] if name not in (METHOD_OWNERS[method], 'CHATGPT_OUTPUT.md')],
            'note': 'Full method owner and ChatGPT output contract; other excerpts may be partial. Fetch relevant full conditional owners before interpretations that depend on omitted sections.'}


def get_policy_owner(method: str, owner: str, offset: int = 0, max_chars: int = 12000) -> dict:
    """Get exact canonical owner text in bounded, verifiable contiguous chunks.

    No arbitrary file read: method and owner must be in the pinned allowlist.
    Caller must concatenate sequential chunks before claiming full coverage.
    """
    if method not in METHOD_OWNERS:
        raise ValueError('unsupported method')
    if owner not in _bundle()['owners']:
        raise ValueError('owner not allowlisted')
    if type(offset) is not int or offset < 0:
        raise ValueError('offset must be nonnegative integer')
    if type(max_chars) is not int or max_chars < 1 or max_chars > 16000:
        raise ValueError('max_chars must be integer 1..16000')
    pack = _bundle()
    entry = pack['owners'][owner]
    content = entry['content']
    if offset > len(content):
        raise ValueError('offset beyond owner')
    end = min(offset + max_chars, len(content))
    return {'source_commit': pack['source_commit'], 'profile_id': pack['profile_id'],
            'method': method, 'owner': owner, 'sha256': entry['sha256'],
            'offset': offset, 'next_offset': end if end < len(content) else None,
            'total_chars': len(content), 'complete': offset == 0 and end == len(content),
            'text': content[offset:end]}


def selected_policy_reference(method: str | None) -> dict:
    """Compact, hash-pinned policy identity without owner text excerpts."""
    if method not in METHOD_OWNERS:
        raise ValueError('unsupported method for policy reference')
    return {**policy_identity(), 'method': method, 'excerpts': [],
            'required_full_owners': [METHOD_OWNERS[method], 'CHATGPT_OUTPUT.md'],
            'note': 'Compact reference only; no policy excerpts. Obtain canonical policy before interpretation.'}
