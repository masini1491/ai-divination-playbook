#!/usr/bin/env python3
"""Build or verify the derived Free ChatGPT stochastic-core transport capsule."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "runtime" / "casting" / "core.py"
OUTPUT = ROOT / "runtime" / "casting" / "CHATGPT_RUNTIME_CAPSULE.json"
MAX_PAYLOAD_CHARS = 5000
MAX_DECODED_BYTES = 8192
CHUNK_CHARS = 444
MAX_CHUNK_CHARS = 512
CHUNK_RETRY_LIMIT = 2
CACHE_LOCATOR_VERSION = 4
CACHE_MARKER_FILENAME = "capsule_verification.json"
CACHE_REQUIRED_MARKER_FIELDS = [
    "verified",
    "cache_locator_version",
    "runtime_source_repository",
    "runtime_source_path",
    "capsule_path",
    "runtime_source_ref",
    "runtime_source_commit",
    "runtime_copy_sha256",
    "core_version",
    "algorithm_version",
    "supported_methods",
    "tarot_deck_size",
]


def _chunk_payload(payload: str) -> list[dict[str, object]]:
    chunks: list[dict[str, object]] = []
    for start in range(0, len(payload), CHUNK_CHARS):
        chunk = payload[start : start + CHUNK_CHARS]
        chunks.append(
            {
                "index": len(chunks),
                "encoded_length": len(chunk),
                "encoded_sha256": hashlib.sha256(chunk.encode("ascii")).hexdigest(),
                "payload": chunk,
            }
        )
    return chunks


def build_capsule() -> dict:
    data = CORE.read_bytes()
    payload = base64.b64encode(zlib.compress(data, level=9)).decode("ascii")
    if len(data) > MAX_DECODED_BYTES:
        raise ValueError(f"core.py exceeds {MAX_DECODED_BYTES} decoded-byte admission bound")
    if len(payload) > MAX_PAYLOAD_CHARS:
        raise ValueError(f"capsule payload exceeds {MAX_PAYLOAD_CHARS}-character admission bound")

    chunks = _chunk_payload(payload)
    if any(chunk["encoded_length"] > MAX_CHUNK_CHARS for chunk in chunks):
        raise ValueError(f"capsule chunk exceeds {MAX_CHUNK_CHARS}-character admission bound")

    namespace: dict[str, object] = {}
    exec(compile(data, str(CORE), "exec"), namespace)
    return {
        "schema_version": 2,
        "authority": "derived-transport-cache-only",
        "transport_contract": "chunked-model-mediated-opaque-handoff-v2",
        "automatic_object_bridge_required": False,
        "must_attempt_when_python_available": True,
        "same_turn_attempt_required": True,
        "missing_automatic_bridge_is_not_gap": True,
        "chunk_retry_required_on_mismatch": True,
        "chunk_reassembly": "index-ascending-concat",
        "chunk_retry_limit": CHUNK_RETRY_LIMIT,
        "chunk_retry_source": "fresh-same-commit-capsule-read",
        "source_repository": "masini1491/ai-divination-playbook",
        "source_path": "runtime/casting/core.py",
        "payload_encoding": "base64+zlib",
        "chunk_encoding": "ascii",
        "chunk_size": CHUNK_CHARS,
        "chunk_count": len(chunks),
        "encoded_size": len(payload),
        "decoded_size": len(data),
        "decoded_sha256": hashlib.sha256(data).hexdigest(),
        "core_version": namespace["CORE_VERSION"],
        "algorithm_version": namespace["ALGORITHM_VERSION"],
        "supported_methods": list(namespace["SUPPORTED_METHODS"]),
        "cache_contract": {
            "marker_filename": CACHE_MARKER_FILENAME,
            "cache_locator_version": CACHE_LOCATOR_VERSION,
            "marker_write_required_before_execution": True,
            "marker_readback_required_before_execution": True,
            "post_write_probe_required_before_execution": True,
            "required_marker_fields": CACHE_REQUIRED_MARKER_FIELDS,
        },
        "chunks": chunks,
        "legacy": {
            "transport_contract": "bounded-model-mediated-opaque-handoff-v1",
        },
    }


def render(capsule: dict) -> str:
    return json.dumps(capsule, ensure_ascii=False, separators=(",", ":")) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = render(build_capsule())

    if args.check:
        if not OUTPUT.is_file():
            raise SystemExit(f"missing {OUTPUT.relative_to(ROOT)}")
        current = OUTPUT.read_text(encoding="utf-8")
        if current != expected:
            raise SystemExit(
                "CHATGPT_RUNTIME_CAPSULE.json is stale; run "
                "python tools/build_runtime_capsule.py and commit the result"
            )
        print("ChatGPT runtime capsule: PASS")
        return 0

    OUTPUT.write_text(expected, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
