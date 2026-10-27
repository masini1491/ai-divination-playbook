#!/usr/bin/env python3
"""Build only the approved ChatGPT MCP release files from canonical repo HEAD.

Usage: python tools/build_chatgpt_mcp_release.py [--check] [--repo-root DIR]
Generated files stay under integrations/chatgpt-mcp. This program does not
trigger deployments, modify Git refs, or add new methods on its own.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = 'integrations/chatgpt-mcp/release_profile.json'
OUTPUT = 'integrations/chatgpt-mcp'
_ALLOWED_METHODS = ('tarot', 'meihua', 'liuyao')
_ALLOWED_ENGINE_FILES = (
    'runtime/casting/core.py', 'tools/meihua_engine.py',
    'tools/liuyao_engine.py', 'tools/liuyao_calendar.py',
    'tools/liuyao_runtime.py',
)
_ALLOWED_POLICY_FILES = (
    'METHOD_ROUTING.md', 'INPUT_CONTRACT.md', 'QUESTION_DESIGN.md',
    'TAROT.md', 'MEIHUA.md', 'LIUYAO.md', 'READING_LIFECYCLE.md',
    'READING_RECORD.md', 'CROSS_VALIDATION.md', 'CHATGPT_OUTPUT.md',
    'RUNTIME_DRAW.md',
)

def _git(repo: Path, *args: str) -> str:
    return subprocess.check_output(['git', '-C', str(repo), *args], text=True).strip()

def _sha_blob(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()

def _dump(obj: object) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + '\n').encode('utf-8')

def generate(repo: Path) -> dict[str, bytes]:
    profile = json.loads((repo / PROFILE).read_text(encoding='utf-8'))
    if (profile.get('schema_version') != 1
            or tuple(profile.get('enabled_methods', [])) != _ALLOWED_METHODS
            or tuple(profile.get('canonical_engines', [])) != _ALLOWED_ENGINE_FILES
            or tuple(profile.get('canonical_policy_owners', [])) != _ALLOWED_POLICY_FILES):
        raise ValueError('RELEASE_PROFILE_NOT_APPROVED: exact allowlist required')
    if not all(x not in set(profile['canonical_engines'] + profile['canonical_policy_owners'])
               for x in ('PALMISTRY.md', 'ASTROLOGY.md', 'ZIWEI.md')):
        raise ValueError('UNAPPROVED_METHOD_IN_RELEASE')
    source_commit = _git(repo, 'rev-parse', 'HEAD')
    git_root = Path(_git(repo, 'rev-parse', '--show-toplevel')).resolve()
    if git_root != repo.resolve():
        raise ValueError('EXPECTED_GIT_ROOT_MISMATCH')
    if len(source_commit) != 40 or not all(ch in '0123456789abcdef' for ch in source_commit):
        raise ValueError('INVALID_SOURCE_COMMIT')
    mirrored: dict[str, bytes] = {}
    blobs = {}
    integrity = {}
    policy = {}
    for relative in [*_ALLOWED_ENGINE_FILES, *_ALLOWED_POLICY_FILES]:
        path = (repo / relative).resolve()
        if not path.is_relative_to(repo.resolve()) or path.is_symlink() or not path.is_file():
            raise ValueError(f'UNSAFE_SOURCE_FILE: {relative}')
        data = path.read_bytes()
        if not data or len(data) > 350_000:
            raise ValueError(f'INVALID_SOURCE_SIZE: {relative}')
        blob = _sha_blob(data)
        if blob != _git(repo, 'rev-parse', f'HEAD:{relative}'):
            raise ValueError(f'UNCOMMITTED_CANONICAL_SOURCE: {relative}')
        if relative in _ALLOWED_ENGINE_FILES:
            mirrored[f'canonical-repo/{relative}'] = data
            blobs[relative] = blob
            integrity[relative] = {'size': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
                                   'git_blob_sha1': blob}
        else:
            decoded = data.decode('utf-8')
            policy[relative] = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
                                'git_blob_sha1': blob, 'content': decoded}
    mirrored['source_manifest.json'] = _dump({'repository':'masini1491/ai-divination-playbook',
                                                'commit':source_commit, 'blob_shas': blobs})
    mirrored['source_integrity.json'] = _dump({'repository':'masini1491/ai-divination-playbook',
                                                'source_commit':source_commit, 'files': integrity})
    mirrored['policy_pack.json'] = _dump({'schema_version':1,'profile_id':profile['profile_id'],
                                           'source_commit':source_commit,'owners':policy})
    return mirrored

def sync(repo: Path, check: bool) -> int:
    expected = generate(repo)
    root = repo / OUTPUT
    managed = {'source_manifest.json', 'source_integrity.json', 'policy_pack.json'}
    managed |= {f'canonical-repo/{s}' for s in _ALLOWED_ENGINE_FILES}
    # Refuse unexpected files under our generated subdirectory, e.g. palmistry.
    generated_root = root / 'canonical-repo'
    if generated_root.exists():
        for current in generated_root.rglob('*'):
            if current.is_file() and current.relative_to(root).as_posix() not in managed:
                raise ValueError(f'UNAPPROVED_GENERATED_FILE: {current.relative_to(root)}')
    changed = []
    for relative, data in expected.items():
        dest = root / relative
        if not dest.is_file() or dest.read_bytes() != data:
            changed.append(relative)
            if not check:
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(data)
    print(json.dumps({'mode':'check' if check else 'sync', 'source_commit':_git(repo,'rev-parse','HEAD'),
                      'managed_files':len(expected),'changed':changed},ensure_ascii=False))
    return 1 if check and changed else 0

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo-root', type=Path, default=ROOT)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    try:
        return sync(args.repo_root.resolve(), args.check)
    except (ValueError, OSError, subprocess.CalledProcessError, UnicodeDecodeError) as ex:
        print(f'RELEASE_SYNC_REJECTED: {ex}', file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
