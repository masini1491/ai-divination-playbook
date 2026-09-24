#!/usr/bin/env python3
"""Benchmark query-bounded alias-hash shards for the admitted Astrology place resolver.

Research-only utility. It does not change production admission or resolver routing.
The source datasets must match the exact geonamescache==3.0.2 identities recorded by
A-MAT-2 before any benchmark result is accepted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable

GEONAMESCACHE_VERSION = "3.0.2"
GEONAMESCACHE_SOURCE_REVISION = "df4f6497b321f7981645ab0c5c77d3354c63bd01"

EXPECTED_DATASETS: dict[int, dict[str, Any]] = {
    500: {
        "bytes": 79_527_431,
        "sha256": "1523be8c6f083eeee946e1c27a0916474d0f0de4361a15104fcc70218bc4d55e",
    },
    1000: {
        "bytes": 60_986_259,
        "sha256": "a6dffc566a3196e0995c7925defdafa548bb8a8fa951d6ab2ea78abedeb0dd60",
    },
    5000: {
        "bytes": 29_665_391,
        "sha256": "6f65c327a0f7374cb7ee629ed6e5128d6d3a2a4d92ed98fc7629690f5074ed55",
    },
    15000: {
        "bytes": 16_670_875,
        "sha256": "24e87d89c775305650301618fa434d26e47e1b64ba5e27a5611e0f351908fd11",
    },
}

FIXTURES: tuple[dict[str, str | None], ...] = (
    {"name": "樹林區", "country_code": "TW"},
    {"name": "Tokyo", "country_code": "JP"},
    {"name": "Springfield", "country_code": None},
    {"name": "Springfield", "country_code": "US"},
)

SCHEMA_NAME = "astrology-place-alias-shard-poc-v1"


def normalize_query(value: str) -> str:
    """Mirror current resolver exact-match semantics after caller-side strip()."""
    return value.strip().casefold()


def normalize_alias(value: str) -> str:
    """Mirror geonamescache case-insensitive exact alias comparison."""
    return value.casefold()


def bucket_id(normalized_alias: str, bucket_hex_chars: int) -> str:
    if not 1 <= bucket_hex_chars <= 8:
        raise ValueError("bucket_hex_chars must be between 1 and 8")
    return hashlib.sha256(normalized_alias.encode("utf-8")).hexdigest()[:bucket_hex_chars]


def candidate_payload(row: dict[str, Any]) -> list[Any]:
    """Compact candidate payload retaining every currently admitted resolver output field."""
    return [
        int(row["geonameid"]),
        str(row["name"]),
        str(row["countrycode"]),
        str(row.get("admin1code", "")),
        float(row["latitude"]),
        float(row["longitude"]),
        str(row["timezone"]),
        int(row.get("population", 0)),
    ]


def direct_exact_ids(
    records: dict[str, dict[str, Any]],
    name: str,
    *,
    country_code: str | None = None,
) -> list[int]:
    needle = normalize_query(name)
    country = country_code.upper() if country_code else None
    matches: set[int] = set()
    for row in records.values():
        if country and str(row.get("countrycode", "")).upper() != country:
            continue
        aliases = row.get("alternatenames", [])
        if any(needle == normalize_alias(str(alias)) for alias in aliases):
            matches.add(int(row["geonameid"]))
    return sorted(matches)


def build_shards(
    records: dict[str, dict[str, Any]],
    *,
    profile: int,
    bucket_hex_chars: int,
) -> dict[str, dict[str, Any]]:
    del profile
    buckets: dict[str, dict[str, Any]] = {}
    for row in records.values():
        gid = str(int(row["geonameid"]))
        aliases = {
            normalize_alias(str(alias))
            for alias in row.get("alternatenames", [])
            if str(alias)
        }
        if not aliases:
            continue
        payload = candidate_payload(row)
        for alias in aliases:
            bid = bucket_id(alias, bucket_hex_chars)
            bucket = buckets.setdefault(bid, {"aliases": {}, "candidates": {}})
            bucket["aliases"].setdefault(alias, []).append(int(gid))
            bucket["candidates"][gid] = payload

    for bucket in buckets.values():
        for ids in bucket["aliases"].values():
            ids.sort()
    return buckets


def shard_bytes(profile: int, bid: str, bucket: dict[str, Any]) -> bytes:
    payload = {
        "schema": SCHEMA_NAME,
        "profile": profile,
        "bucket": bid,
        "aliases": bucket["aliases"],
        "candidates": bucket["candidates"],
    }
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def percentile(values: list[int], p: float) -> int:
    if not values:
        return 0
    ordered = sorted(values)
    rank = max(1, math.ceil(p * len(ordered)))
    return ordered[rank - 1]


def resolve_from_shards(
    shards: dict[str, dict[str, Any]],
    *,
    name: str,
    country_code: str | None,
    bucket_hex_chars: int,
) -> tuple[str, list[int]]:
    key = normalize_query(name)
    bid = bucket_id(key, bucket_hex_chars)
    bucket = shards.get(bid, {"aliases": {}, "candidates": {}})
    ids = list(bucket["aliases"].get(key, []))
    if country_code:
        wanted = country_code.upper()
        ids = [
            gid
            for gid in ids
            if str(bucket["candidates"][str(gid)][2]).upper() == wanted
        ]
    return bid, sorted(set(ids))


def benchmark_records(
    records: dict[str, dict[str, Any]],
    *,
    profile: int,
    bucket_hex_chars: int,
    fixtures: Iterable[dict[str, str | None]] = FIXTURES,
) -> dict[str, Any]:
    direct = {
        (str(f["name"]), f["country_code"]): direct_exact_ids(
            records,
            str(f["name"]),
            country_code=f["country_code"],
        )
        for f in fixtures
    }
    shards = build_shards(records, profile=profile, bucket_hex_chars=bucket_hex_chars)

    sizes: list[int] = []
    alias_count = 0
    candidate_refs = 0
    largest: list[tuple[int, str, int, int]] = []
    for bid, bucket in shards.items():
        size = len(shard_bytes(profile, bid, bucket))
        sizes.append(size)
        aliases = len(bucket["aliases"])
        candidates = len(bucket["candidates"])
        alias_count += aliases
        candidate_refs += candidates
        largest.append((size, bid, aliases, candidates))
    largest.sort(reverse=True)

    fixture_results = []
    parity_ok = True
    for fixture in fixtures:
        name = str(fixture["name"])
        country = fixture["country_code"]
        bid, actual = resolve_from_shards(
            shards,
            name=name,
            country_code=country,
            bucket_hex_chars=bucket_hex_chars,
        )
        expected = direct[(name, country)]
        ok = actual == expected
        parity_ok = parity_ok and ok
        bucket = shards.get(bid)
        fixture_results.append(
            {
                "name": name,
                "country_code": country,
                "bucket": bid,
                "shard_bytes": len(shard_bytes(profile, bid, bucket)) if bucket else 0,
                "expected_ids": expected,
                "actual_ids": actual,
                "parity": ok,
            }
        )

    total_bytes = sum(sizes)
    return {
        "profile": profile,
        "bucket_hex_chars": bucket_hex_chars,
        "theoretical_bucket_count": 16**bucket_hex_chars,
        "nonempty_shards": len(sizes),
        "alias_keys": alias_count,
        "candidate_refs_across_shards": candidate_refs,
        "total_serialized_bytes": total_bytes,
        "avg_shard_bytes": round(total_bytes / len(sizes), 2) if sizes else 0,
        "p50_shard_bytes": percentile(sizes, 0.50),
        "p95_shard_bytes": percentile(sizes, 0.95),
        "p99_shard_bytes": percentile(sizes, 0.99),
        "max_shard_bytes": max(sizes, default=0),
        "largest_shards": [
            {
                "bucket": bid,
                "bytes": size,
                "aliases": aliases,
                "candidates": candidates,
            }
            for size, bid, aliases, candidates in largest[:5]
        ],
        "fixtures": fixture_results,
        "fixture_parity": parity_ok,
    }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def locate_data_dir() -> tuple[Path, str]:
    import geonamescache

    version = str(geonamescache.__version__)
    data_dir = Path(geonamescache.__file__).resolve().parent / "data"
    return data_dir, version


def verify_dataset(path: Path, profile: int) -> dict[str, Any]:
    expected = EXPECTED_DATASETS[profile]
    actual_bytes = path.stat().st_size
    actual_sha = sha256_file(path)
    ok = actual_bytes == expected["bytes"] and actual_sha == expected["sha256"]
    return {
        "profile": profile,
        "path": path.name,
        "expected_bytes": expected["bytes"],
        "actual_bytes": actual_bytes,
        "expected_sha256": expected["sha256"],
        "actual_sha256": actual_sha,
        "identity_match": ok,
    }


def load_records(path: Path) -> dict[str, dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"expected object dataset in {path}")
    return payload


def run(profiles: list[int], bucket_hex_chars: list[int]) -> dict[str, Any]:
    data_dir, installed_version = locate_data_dir()
    if installed_version != GEONAMESCACHE_VERSION:
        raise RuntimeError(
            f"geonamescache version mismatch: expected {GEONAMESCACHE_VERSION}, got {installed_version}"
        )

    identities = []
    benchmarks = []
    for profile in profiles:
        path = data_dir / f"cities{profile}.json"
        identity = verify_dataset(path, profile)
        identities.append(identity)
        if not identity["identity_match"]:
            raise RuntimeError(f"dataset identity mismatch for cities{profile}.json")

        records = load_records(path)
        for width in bucket_hex_chars:
            benchmarks.append(
                benchmark_records(
                    records,
                    profile=profile,
                    bucket_hex_chars=width,
                )
            )

    return {
        "schema": "astrology-place-shard-benchmark-v1",
        "status": "PASS" if all(b["fixture_parity"] for b in benchmarks) else "FAIL",
        "scope": "research-only; no production admission change",
        "source": {
            "package": f"geonamescache=={GEONAMESCACHE_VERSION}",
            "source_revision": GEONAMESCACHE_SOURCE_REVISION,
            "dataset_origin": "GeoNames",
            "dataset_license": "CC-BY-4.0",
        },
        "dataset_identity": identities,
        "benchmarks": benchmarks,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--profiles",
        type=int,
        nargs="+",
        default=[500, 1000, 5000, 15000],
        choices=sorted(EXPECTED_DATASETS),
    )
    parser.add_argument(
        "--bucket-hex-chars",
        type=int,
        nargs="+",
        default=[2, 3, 4],
        help="SHA-256 hexadecimal prefix widths to benchmark.",
    )
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = run(args.profiles, args.bucket_hex_chars)
    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
