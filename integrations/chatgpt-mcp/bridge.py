"""Fact-only MCP adapter over hash-verified ai-divination-playbook Python engines.

No fetching, user data persistence, RNG reimplementation, or interpretation.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

MANIFEST = json.loads((Path(__file__).parent / 'source_manifest.json').read_text(encoding='utf-8'))
INTEGRITY = json.loads((Path(__file__).parent / 'source_integrity.json').read_text(encoding='utf-8'))
SOURCE_COMMIT: str = MANIFEST['commit']
if INTEGRITY.get('source_commit') != SOURCE_COMMIT or INTEGRITY.get('repository') != MANIFEST.get('repository'):
    raise RuntimeError('SOURCE_MANIFEST_IDENTITY_MISMATCH')
if set(INTEGRITY.get('files', {})) != set(MANIFEST.get('blob_shas', {})):
    raise RuntimeError('SOURCE_MANIFEST_FILE_SET_MISMATCH')
for _rel, _digest in INTEGRITY['files'].items():
    if _digest.get('git_blob_sha1') != MANIFEST['blob_shas'][_rel]:
        raise RuntimeError('SOURCE_MANIFEST_BLOB_MISMATCH')


def _git_blob_sha(content: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest()


def check_source(root: Path) -> None:
    """Verify the five exact original blob identities before importing code."""
    root = root.resolve()
    for rel, expected in MANIFEST['blob_shas'].items():
        path = root / rel
        if not path.is_file() or not path.resolve().is_relative_to(root):
            raise RuntimeError(f'MISSING_SOURCE: {rel}')
        data = path.read_bytes()
        actual = _git_blob_sha(data)
        if actual != expected:
            raise RuntimeError(f'SOURCE_MISMATCH: {rel} expected {expected}, actual {actual}')
        identity = INTEGRITY['files'][rel]
        if len(data) != identity['size'] or hashlib.sha256(data).hexdigest() != identity['sha256']:
            raise RuntimeError(f'SOURCE_SHA256_MISMATCH: {rel}')


def _load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'MODULE_LOAD_FAILED: {path.name}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _valid_execution(payload: Any, expected_method: str) -> None:
    """Reject incompletely attributed, internally inconsistent stochastic envelopes."""
    if not isinstance(payload, dict):
        raise RuntimeError('STOCHASTIC_EXECUTION_FACT_INVALID: payload not an object')
    fields = ('source', 'algorithm_version', 'schema_version', 'runtime_source_commit',
              'generated_at_utc', 'generated_at_taipei', 'timezone', 'results')
    missing = [f for f in fields if payload.get(f) is None or payload.get(f) == '']
    if missing:
        raise RuntimeError(f'STOCHASTIC_EXECUTION_FACT_INVALID: missing {missing}')
    if (payload['source'] != 'divination-casting-randomizer-python'
        or payload['timezone'] != 'Asia/Taipei'
        or payload['runtime_source_commit'] != SOURCE_COMMIT):
        raise RuntimeError('STOCHASTIC_EXECUTION_FACT_INVALID: provenance mismatch')
    # Consumer version gate; canonical RNG implementation remains owned by core.py.
    if payload['algorithm_version'] != '2' or payload['schema_version'] != '4':
        raise RuntimeError('STOCHASTIC_EXECUTION_FACT_INVALID: algorithm/schema version mismatch')
    try:
        utc = datetime.fromisoformat(payload['generated_at_utc'])
        tw = datetime.fromisoformat(payload['generated_at_taipei'])
        if (utc.utcoffset() is None or tw.utcoffset() is None
            or utc.utcoffset().total_seconds() != 0
            or tw.utcoffset().total_seconds() != 8 * 3600
            or utc.astimezone(timezone.utc) != tw.astimezone(timezone.utc)):
            raise ValueError('timestamp must refer to one actual instant')
    except (ValueError, TypeError, AttributeError) as exc:
        raise RuntimeError('STOCHASTIC_EXECUTION_FACT_INVALID: timestamp mismatch') from exc
    results = payload['results']
    if (not isinstance(results, list) or len(results) != 1
        or not isinstance(results[0], dict)
        or results[0].get('method') != expected_method):
        raise RuntimeError('STOCHASTIC_EXECUTION_FACT_INVALID: result mismatch')


class DivinationBridge:
    def __init__(self, repo_root: str | Path):
        root = Path(repo_root).resolve()
        check_source(root)
        self.repo_root = root
        self.core = _load('divination_pinned_core', root / 'runtime/casting/core.py')
        self.meihua = _load('divination_pinned_meihua', root / 'tools/meihua_engine.py')
        self.liuyao = _load('divination_pinned_liuyao', root / 'tools/liuyao_runtime.py')
        invariants = self.core.runtime_invariants()
        if (getattr(self.core, 'ALGORITHM_VERSION', None) != '2'
            or getattr(self.core, 'SCHEMA_VERSION', None) != '4'
            or getattr(self.core, 'SOURCE', None) != 'divination-casting-randomizer-python'):
            raise RuntimeError('CANONICAL_RUNTIME_VERSION_MISMATCH')
        if (invariants.get('execution_entrypoint') != 'execute_stochastic'
            or invariants.get('tarot_deck_size') != 78
            or invariants.get('liuyao_line_count') != 6
            or set(invariants.get('supported_methods', [])) != {'tarot', 'plum', 'liuyao'}):
            raise RuntimeError('CANONICAL_RUNTIME_INVARIANT_MISMATCH')

    def revalidate_source(self) -> None:
        """Fail closed if any pinned repository bytes changed after startup."""
        check_source(self.repo_root)

    def _execute(self, command: str, **kwargs: Any) -> dict[str, Any]:
        result = self.core.execute_stochastic(command, source_commit=SOURCE_COMMIT, **kwargs)
        _valid_execution(result, command)
        return result

    def draw_tarot(self, count: int = 3) -> dict[str, Any]:
        if type(count) is not int or not 1 <= count <= 24:
            raise ValueError('count must be integer between 1 and 24')
        payload = self._execute('tarot', count=count)
        tarot = payload['results'][0].get('tarot')
        if (not isinstance(tarot, dict) or tarot.get('count') != count
            or not isinstance(tarot.get('cards'), list) or len(tarot['cards']) != count):
            raise RuntimeError('STOCHASTIC_EXECUTION_FACT_INVALID: Tarot count mismatch')
        names = []
        for index, card in enumerate(tarot['cards'], 1):
            if (not isinstance(card, dict) or card.get('index') != index
                or not isinstance(card.get('full_name'), str)
                or card.get('orientation') not in ('正', '逆')):
                raise RuntimeError('STOCHASTIC_EXECUTION_FACT_INVALID: Tarot card')
            names.append(card['full_name'])
        if len(set(names)) != count:
            raise RuntimeError('STOCHASTIC_EXECUTION_FACT_INVALID: Tarot duplicate')
        return payload

    def cast_meihua(self) -> dict[str, Any]:
        payload = self._execute('plum')
        cast = payload['results'][0].get('plum')
        if not isinstance(cast, dict):
            raise RuntimeError('STOCHASTIC_EXECUTION_FACT_INVALID: Meihua raw cast missing')
        if any(not isinstance(cast.get(k), str) or len(cast[k]) != 3 or not cast[k].isascii() or not cast[k].isdigit() for k in ('a', 'b')):
            raise RuntimeError('STOCHASTIC_EXECUTION_FACT_INVALID: Meihua A/B')
        structured = self.meihua.derive(
            a=cast['a'], b=cast['b'], upper_trigram=cast['upper_trigram'],
            lower_trigram=cast['lower_trigram'], hexagram=cast['hexagram'],
            moving_line=cast['moving_line'])
        return {'execution': payload, 'structured_method_fact': structured}

    def cast_liuyao(self) -> dict[str, Any]:
        payload = self._execute('liuyao')
        cast = payload['results'][0].get('liuyao')
        if (not isinstance(cast, dict)
            or cast.get('line_order') != 'bottom-to-top'
            or cast.get('cast_method') != 'three-coins'):
            raise RuntimeError('STOCHASTIC_EXECUTION_FACT_INVALID: Liuyao casting contract')
        lines = cast.get('lines')
        if not isinstance(lines, list) or len(lines) != 6:
            raise RuntimeError('STOCHASTIC_EXECUTION_FACT_INVALID: six Liuyao lines required')
        for pos, line in enumerate(lines, 1):
            if not isinstance(line, dict) or line.get('position') != pos:
                raise RuntimeError('STOCHASTIC_EXECUTION_FACT_INVALID: Liuyao line position')
            values = line.get('coin_values')
            if (not isinstance(values, list) or len(values) != 3
                or any(type(v) is not int or v not in (2, 3) for v in values)
                or sum(values) != line.get('value')):
                raise RuntimeError('STOCHASTIC_EXECUTION_FACT_INVALID: Liuyao coins')
            # Reuse the canonical normalizer; never duplicate coin interpretation.
            canonical = self.core.resolve_liuyao_coin_values(values)
            if any(line.get(key) != canonical[key] for key in
                   ('value', 'coin_faces', 'yin_yang', 'changing', 'line_type')):
                raise RuntimeError('STOCHASTIC_EXECUTION_FACT_INVALID: Liuyao line metadata')
        structured = self.liuyao.build_liuyao_fact(
            [line['value'] for line in lines], timestamp=payload['generated_at_taipei'])
        return {'execution': payload, 'structured_method_fact': structured}

    def derive_meihua(self, a: str, b: str, *, upper_trigram: str | None = None,
                      lower_trigram: str | None = None, hexagram: str | None = None,
                      moving_line: int | None = None) -> dict[str, Any]:
        return {'fact_source': 'user_supplied', 'structured_method_fact': self.meihua.derive(
            a=a, b=b, upper_trigram=upper_trigram, lower_trigram=lower_trigram,
            hexagram=hexagram, moving_line=moving_line)}

    def derive_liuyao(self, raw_lines: list[int], cast_timestamp: str) -> dict[str, Any]:
        if (not isinstance(raw_lines, list) or len(raw_lines) != 6
            or any(type(v) is not int or v not in (6, 7, 8, 9) for v in raw_lines)):
            raise ValueError('exactly six bottom-to-top integer raw lines in 6,7,8,9 are required')
        dt = datetime.fromisoformat(cast_timestamp)
        if dt.tzinfo is None or dt.utcoffset() is None:
            raise ValueError('offset required')
        return {'fact_source': 'user_supplied', 'structured_method_fact': self.liuyao.build_liuyao_fact(
            raw_lines, timestamp=cast_timestamp)}
