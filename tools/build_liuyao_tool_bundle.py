#!/usr/bin/env python3
"""Build the derived ChatGPT transport bundle for deterministic Liuyao tools.

Canonical authority remains in the three source Python files. This generator only
packages their exact bytes into a chunked, verifiable transport cache so a
GitHub-Connect cold start can move one bounded payload into local Python without
merging deterministic Liuyao logic into the stochastic casting core.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys
import zlib

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "runtime" / "liuyao" / "CHATGPT_DETERMINISTIC_TOOL_BUNDLE.json"
SOURCE_REPOSITORY = "masini1491/ai-divination-playbook"
SOURCE_PATHS = (
    "tools/liuyao_calendar.py",
    "tools/liuyao_engine.py",
    "tools/liuyao_runtime.py",
)
SCHEMA_VERSION = 1
AUTHORITY = "derived-transport-cache-only"
CONTRACT = "chunked-model-mediated-deterministic-tool-bundle-v1"
CHUNK_SIZE = 444
CHUNK_RETRY_LIMIT = 2


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def build_bundle() -> dict[str, object]:
    manifest: list[dict[str, object]] = []
    parts: list[bytes] = []
    offset = 0
    for relative in SOURCE_PATHS:
        data = (ROOT / relative).read_bytes()
        manifest.append(
            {
                "path": relative,
                "byte_size": len(data),
                "offset": offset,
                "sha256": sha256_bytes(data),
                "git_blob_sha": git_blob_sha(data),
            }
        )
        parts.append(data)
        offset += len(data)

    archive = b"".join(parts)
    compressed = zlib.compress(archive, level=9)
    encoded = base64.b64encode(compressed).decode("ascii")
    chunks = [encoded[i : i + CHUNK_SIZE] for i in range(0, len(encoded), CHUNK_SIZE)]

    return {
        "schema_version": SCHEMA_VERSION,
        "authority": AUTHORITY,
        "contract": CONTRACT,
        "source_repository": SOURCE_REPOSITORY,
        "source_revision_policy": "same-resolved-playbook-commit",
        "source_files": manifest,
        "archive": {
            "layout": "raw-concat-by-source_files-order",
            "decoded_size": len(archive),
            "sha256": sha256_bytes(archive),
            "compression": "zlib",
            "encoding": "base64",
            "compressed_size": len(compressed),
            "encoded_size": len(encoded),
            "chunk_size": CHUNK_SIZE,
            "chunk_count": len(chunks),
            "reassembly": "index-ascending-concat",
            "chunk_retry_limit": CHUNK_RETRY_LIMIT,
            "retry_source": "fresh-read-same-commit-bundle-failed-chunk-only",
        },
        "execution_contract": {
            "must_attempt_after_verified_local_cache_miss": True,
            "preserve_raw_cast": True,
            "preserve_cast_timestamp": True,
            "verify_each_chunk_before_reassembly": True,
            "verify_archive_before_unpack": True,
            "verify_each_file_before_write_or_import": True,
            "interpretation_authority": False,
            "yongshen_selection_authority": False,
        },
        "cache_contract": {
            "cache_dir": "/mnt/data/divination-liuyao-runtime",
            "marker": "bundle_verification.json",
            "required_marker_fields": [
                "verified",
                "repository",
                "playbook_commit",
                "bundle_contract",
                "archive_sha256",
                "files",
            ],
            "reuse_only_when_all_source_file_identities_match": True,
        },
        "chunks": [
            {
                "index": index,
                "encoded_length": len(chunk),
                "sha256": hashlib.sha256(chunk.encode("ascii")).hexdigest(),
                "payload": chunk,
            }
            for index, chunk in enumerate(chunks)
        ],
    }


def render(bundle: dict[str, object]) -> str:
    return json.dumps(bundle, ensure_ascii=False, indent=2) + "\n"


def verify_bundle(bundle: dict[str, object]) -> list[str]:
    errors: list[str] = []
    if bundle.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version mismatch")
    if bundle.get("authority") != AUTHORITY:
        errors.append("authority mismatch")
    if bundle.get("contract") != CONTRACT:
        errors.append("contract mismatch")
    if bundle.get("source_repository") != SOURCE_REPOSITORY:
        errors.append("source_repository mismatch")

    source_files = bundle.get("source_files")
    chunks = bundle.get("chunks")
    archive_meta = bundle.get("archive")
    if not isinstance(source_files, list) or not isinstance(chunks, list) or not isinstance(archive_meta, dict):
        return errors + ["bundle shape invalid"]

    try:
        ordered = sorted(chunks, key=lambda item: int(item["index"]))
        if [int(item["index"]) for item in ordered] != list(range(len(ordered))):
            errors.append("chunk indexes must be contiguous from zero")
        encoded_parts: list[str] = []
        for item in ordered:
            payload = item["payload"]
            if not isinstance(payload, str):
                errors.append("chunk payload must be ASCII text")
                continue
            if len(payload) != int(item["encoded_length"]):
                errors.append(f"chunk {item['index']} encoded_length mismatch")
            if hashlib.sha256(payload.encode("ascii")).hexdigest() != item["sha256"]:
                errors.append(f"chunk {item['index']} sha256 mismatch")
            encoded_parts.append(payload)
        encoded = "".join(encoded_parts)
        if len(encoded) != int(archive_meta["encoded_size"]):
            errors.append("encoded_size mismatch")
        compressed = base64.b64decode(encoded, validate=True)
        if len(compressed) != int(archive_meta["compressed_size"]):
            errors.append("compressed_size mismatch")
        decoded = zlib.decompress(compressed)
        if len(decoded) != int(archive_meta["decoded_size"]):
            errors.append("decoded_size mismatch")
        if sha256_bytes(decoded) != archive_meta["sha256"]:
            errors.append("archive sha256 mismatch")

        cursor = 0
        for entry in source_files:
            size = int(entry["byte_size"])
            if int(entry["offset"]) != cursor:
                errors.append(f"{entry['path']} offset mismatch")
            part = decoded[cursor : cursor + size]
            if len(part) != size:
                errors.append(f"{entry['path']} truncated")
            if sha256_bytes(part) != entry["sha256"]:
                errors.append(f"{entry['path']} sha256 mismatch")
            if git_blob_sha(part) != entry["git_blob_sha"]:
                errors.append(f"{entry['path']} git blob mismatch")
            canonical = (ROOT / str(entry["path"])).read_bytes()
            if part != canonical:
                errors.append(f"{entry['path']} does not reproduce canonical bytes")
            cursor += size
        if cursor != len(decoded):
            errors.append("archive has trailing bytes")
    except (KeyError, TypeError, ValueError, zlib.error, base64.binascii.Error) as exc:
        errors.append(f"bundle decode error: {exc}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the committed bundle is stale or invalid")
    args = parser.parse_args(argv)

    expected = build_bundle()
    expected_text = render(expected)
    if args.check:
        if not OUTPUT.is_file():
            print(f"FAIL missing {OUTPUT.relative_to(ROOT)}")
            return 1
        try:
            actual = json.loads(OUTPUT.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"FAIL {OUTPUT.relative_to(ROOT)}: {exc}")
            return 1
        errors = verify_bundle(actual)
        if render(actual) != expected_text:
            errors.append("committed bundle is stale relative to canonical Liuyao source files")
        if errors:
            for error in errors:
                print(f"FAIL Liuyao bundle: {error}")
            return 1
        print("Liuyao deterministic tool bundle: PASS")
        return 0

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(expected_text, encoding="utf-8")
    errors = verify_bundle(expected)
    if errors:
        for error in errors:
            print(f"FAIL Liuyao bundle: {error}")
        return 1
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
