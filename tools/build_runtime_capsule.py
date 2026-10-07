#!/usr/bin/env python3
"""Build or verify derived Free ChatGPT stochastic-core transport artifacts."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import shutil
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "runtime" / "casting" / "core.py"
OUTPUT_V2 = ROOT / "runtime" / "casting" / "CHATGPT_RUNTIME_CAPSULE.json"
OUTPUT_V3_DIR = ROOT / "runtime" / "casting" / "capsule-v3"
OUTPUT_V3_MANIFEST = OUTPUT_V3_DIR / "MANIFEST.json"

MAX_PAYLOAD_CHARS = 5000
MAX_DECODED_BYTES = 8192
CHUNK_CHARS = 512
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

def _git_blob_sha1(data: bytes) -> str:
    """Return the Git blob object id for exact file bytes.

    This is repository object identity, not a cryptographic security digest.
    """
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()

def _encode_core() -> tuple[bytes, str]:
    data = CORE.read_bytes()
    payload = base64.b64encode(zlib.compress(data, level=9)).decode("ascii")
    if len(data) > MAX_DECODED_BYTES:
        raise ValueError(f"core.py exceeds {MAX_DECODED_BYTES} decoded-byte admission bound")
    if len(payload) > MAX_PAYLOAD_CHARS:
        raise ValueError(f"capsule payload exceeds {MAX_PAYLOAD_CHARS}-character admission bound")
    return data, payload

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
    if any(chunk["encoded_length"] > MAX_CHUNK_CHARS for chunk in chunks):
        raise ValueError(f"capsule chunk exceeds {MAX_CHUNK_CHARS}-character admission bound")
    return chunks

def _core_identity(data: bytes) -> dict[str, object]:
    namespace: dict[str, object] = {}
    exec(compile(data, str(CORE), "exec"), namespace)
    return {
        "decoded_size": len(data),
        "decoded_sha256": hashlib.sha256(data).hexdigest(),
        "core_version": namespace["CORE_VERSION"],
        "algorithm_version": namespace["ALGORITHM_VERSION"],
        "supported_methods": list(namespace["SUPPORTED_METHODS"]),
        "runtime_invariants": namespace["runtime_invariants"](),
    }

def build_capsule() -> dict:
    """Legacy v2 single-file compatibility artifact."""
    data, payload = _encode_core()
    chunks = _chunk_payload(payload)
    identity = _core_identity(data)
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
        **identity,
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

def build_capsule_v3() -> tuple[dict, list[str]]:
    """Streaming v3 manifest plus individually retrievable chunk files."""
    data, payload = _encode_core()
    chunks = _chunk_payload(payload)
    identity = _core_identity(data)
    chunk_files = [f"chunk-{chunk['index']:02d}.txt" for chunk in chunks]
    manifest_chunks = []
    payloads = []
    for chunk, filename in zip(chunks, chunk_files, strict=True):
        raw_file = (str(chunk["payload"]) + "\n").encode("ascii")
        manifest_chunks.append(
            {
                "index": chunk["index"],
                "path": f"runtime/casting/capsule-v3/{filename}",
                "git_blob_sha1": _git_blob_sha1(raw_file),
                "raw_file_size": len(raw_file),
                "encoded_length": chunk["encoded_length"],
                "encoded_sha256": chunk["encoded_sha256"],
            }
        )
        payloads.append(raw_file.decode("ascii"))
    manifest = {
        "schema_version": 3,
        "authority": "derived-transport-cache-only",
        "transport_contract": "streaming-model-mediated-opaque-handoff-v3",
        "priority": "preferred-free-chatgpt-cold-start-transport",
        "fallback_transport": "runtime/casting/CHATGPT_RUNTIME_CAPSULE.json",
        "automatic_object_bridge_required": False,
        "must_attempt_when_python_available": True,
        "same_turn_attempt_required": True,
        "streaming_fetch": "one-chunk-file-at-a-time",
        "verify_before_next_fetch": True,
        "chunk_source_identity": "git-blob-sha1",
        "source_identity_before_payload_handoff": True,
        "chunk_retry_required_on_mismatch": True,
        "chunk_retry_limit": CHUNK_RETRY_LIMIT,
        "chunk_retry_source": "fresh-same-commit-single-chunk-file-read",
        "chunk_file_terminator": "LF",
        "verified_payload_extraction": "exclude-at-most-one-terminal-lf",
        "verified_payload_reuse_required": True,
        "chunk_reassembly": "index-ascending-concat-of-retained-verified-payloads",
        "source_repository": "masini1491/ai-divination-playbook",
        "source_path": "runtime/casting/core.py",
        "payload_encoding": "base64+zlib",
        "chunk_encoding": "ascii",
        "chunk_size": CHUNK_CHARS,
        "chunk_count": len(chunks),
        "encoded_size": len(payload),
        **identity,
        "cache_contract": {
            "marker_filename": CACHE_MARKER_FILENAME,
            "cache_locator_version": CACHE_LOCATOR_VERSION,
            "marker_write_required_before_execution": True,
            "marker_readback_required_before_execution": True,
            "post_write_probe_required_before_execution": True,
            "required_marker_fields": CACHE_REQUIRED_MARKER_FIELDS,
        },
        "chunks": manifest_chunks,
    }
    return manifest, payloads

def render_json(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n"

def _expected_v3_files() -> dict[Path, str]:
    manifest, payloads = build_capsule_v3()
    expected = {OUTPUT_V3_MANIFEST: render_json(manifest)}
    for entry, payload in zip(manifest["chunks"], payloads, strict=True):
        expected[ROOT / entry["path"]] = payload
    return expected

def _write_v3() -> None:
    expected = _expected_v3_files()
    if OUTPUT_V3_DIR.exists():
        shutil.rmtree(OUTPUT_V3_DIR)
    OUTPUT_V3_DIR.mkdir(parents=True)
    for path, content in expected.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

def _check_v3() -> None:
    expected = _expected_v3_files()
    actual_files = {p for p in OUTPUT_V3_DIR.glob("*") if p.is_file()}
    if actual_files != set(expected):
        missing = sorted(str(p.relative_to(ROOT)) for p in set(expected) - actual_files)
        extra = sorted(str(p.relative_to(ROOT)) for p in actual_files - set(expected))
        raise SystemExit(f"capsule-v3 file set mismatch; missing={missing}; extra={extra}")
    for path, content in expected.items():
        if path.read_text(encoding="utf-8") != content:
            raise SystemExit(f"stale {path.relative_to(ROOT)}")

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    expected_v2 = render_json(build_capsule())
    if args.check:
        if not OUTPUT_V2.is_file():
            raise SystemExit(f"missing {OUTPUT_V2.relative_to(ROOT)}")
        if OUTPUT_V2.read_text(encoding="utf-8") != expected_v2:
            raise SystemExit(
                "CHATGPT_RUNTIME_CAPSULE.json is stale; run "
                "python tools/build_runtime_capsule.py and commit the result"
            )
        _check_v3()
        print("ChatGPT runtime capsule v2/v3: PASS")
        return 0

    OUTPUT_V2.write_text(expected_v2, encoding="utf-8")
    _write_v3()
    print(f"wrote {OUTPUT_V2.relative_to(ROOT)} and {OUTPUT_V3_DIR.relative_to(ROOT)}/")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
