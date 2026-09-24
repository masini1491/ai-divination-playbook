#!/usr/bin/env python3
"""Benchmark split alias-index + candidate-store transport for Astrology place resolution.

Research-only utility. It reuses the exact geonamescache==3.0.2 identity and
normalization contract from astrology_place_shard_benchmark.py. Production
resolver behavior and admission remain unchanged.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable

from astrology_place_shard_benchmark import (
    EXPECTED_DATASETS,
    FIXTURES,
    GEONAMESCACHE_SOURCE_REVISION,
    GEONAMESCACHE_VERSION,
    benchmark_records,
    candidate_payload,
    direct_exact_ids,
    load_records,
    locate_data_dir,
    normalize_alias,
    normalize_query,
    percentile,
    verify_dataset,
)

ALIAS_SCHEMA = "astrology-place-alias-index-shard-poc-v1"
CANDIDATE_SCHEMA = "astrology-place-candidate-store-shard-poc-v1"


def sha_bucket(value: str, hex_chars: int) -> str:
    if not 1 <= hex_chars <= 8:
        raise ValueError("hex_chars must be between 1 and 8")
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:hex_chars]


def alias_bucket_id(normalized_alias: str, alias_hex_chars: int) -> str:
    return sha_bucket(normalized_alias, alias_hex_chars)


def candidate_bucket_id(geoname_id: int, candidate_hex_chars: int) -> str:
    return sha_bucket(str(int(geoname_id)), candidate_hex_chars)


def route_payload(row: dict[str, Any]) -> list[Any]:
    """Minimal metadata needed before candidate-record retrieval.

    Fields: geoname_id, country_code, population, canonical name.
    This preserves current country filtering and resolver sort order.
    """
    return [
        int(row["geonameid"]),
        str(row["countrycode"]),
        int(row.get("population", 0)),
        str(row["name"]),
    ]


def build_split_shards(
    records: dict[str, dict[str, Any]],
    *,
    alias_hex_chars: int,
    candidate_hex_chars: int,
) -> tuple[dict[str, dict[str, list[list[Any]]]], dict[str, dict[str, list[Any]]]]:
    alias_shards: dict[str, dict[str, list[list[Any]]]] = {}
    candidate_shards: dict[str, dict[str, list[Any]]] = {}

    for row in records.values():
        gid = int(row["geonameid"])
        route = route_payload(row)
        full = candidate_payload(row)

        cbid = candidate_bucket_id(gid, candidate_hex_chars)
        candidate_shards.setdefault(cbid, {})[str(gid)] = full

        aliases = {
            normalize_alias(str(alias))
            for alias in row.get("alternatenames", [])
            if str(alias)
        }
        for alias in aliases:
            abid = alias_bucket_id(alias, alias_hex_chars)
            alias_shards.setdefault(abid, {}).setdefault(alias, []).append(route)

    for shard in alias_shards.values():
        for routes in shard.values():
            routes.sort(key=lambda r: (-int(r[2]), str(r[1]), str(r[3]), int(r[0])))

    return alias_shards, candidate_shards


def alias_shard_bytes(
    profile: int,
    bid: str,
    shard: dict[str, list[list[Any]]],
) -> bytes:
    return json.dumps(
        {
            "schema": ALIAS_SCHEMA,
            "profile": profile,
            "bucket": bid,
            "aliases": shard,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def candidate_shard_bytes(
    profile: int,
    bid: str,
    shard: dict[str, list[Any]],
) -> bytes:
    return json.dumps(
        {
            "schema": CANDIDATE_SCHEMA,
            "profile": profile,
            "bucket": bid,
            "candidates": shard,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sorted_routes(
    alias_shards: dict[str, dict[str, list[list[Any]]]],
    *,
    name: str,
    country_code: str | None,
    alias_hex_chars: int,
) -> tuple[str, list[list[Any]]]:
    key = normalize_query(name)
    abid = alias_bucket_id(key, alias_hex_chars)
    routes = list(alias_shards.get(abid, {}).get(key, []))
    if country_code:
        wanted = country_code.upper()
        routes = [route for route in routes if str(route[1]).upper() == wanted]

    dedup: dict[int, list[Any]] = {}
    for route in routes:
        dedup[int(route[0])] = route
    ordered = sorted(
        dedup.values(),
        key=lambda r: (-int(r[2]), str(r[1]), str(r[3]), int(r[0])),
    )
    return abid, ordered


def fetch_candidate_records(
    candidate_shards: dict[str, dict[str, list[Any]]],
    *,
    geoname_ids: list[int],
    candidate_hex_chars: int,
) -> tuple[list[str], dict[int, list[Any]]]:
    bucket_ids = sorted(
        {
            candidate_bucket_id(gid, candidate_hex_chars)
            for gid in geoname_ids
        }
    )
    found: dict[int, list[Any]] = {}
    for bid in bucket_ids:
        shard = candidate_shards.get(bid, {})
        for gid in geoname_ids:
            value = shard.get(str(gid))
            if value is not None:
                found[int(gid)] = value
    return bucket_ids, found


def lookup_measurement(
    alias_shards: dict[str, dict[str, list[list[Any]]]],
    candidate_shards: dict[str, dict[str, list[Any]]],
    *,
    profile: int,
    name: str,
    country_code: str | None,
    alias_hex_chars: int,
    candidate_hex_chars: int,
) -> dict[str, Any]:
    abid, routes = sorted_routes(
        alias_shards,
        name=name,
        country_code=country_code,
        alias_hex_chars=alias_hex_chars,
    )
    alias_shard = alias_shards.get(abid, {})
    alias_bytes = len(alias_shard_bytes(profile, abid, alias_shard)) if alias_shard else 0

    all_ids = [int(route[0]) for route in routes]
    # Preserve current resolver behavior:
    # - unique match needs one full record;
    # - ambiguity preview needs the first ten full records after resolver sort;
    # - no match needs no candidate-store read.
    required_ids = all_ids[:1] if len(all_ids) == 1 else all_ids[:10]
    cbids, found = fetch_candidate_records(
        candidate_shards,
        geoname_ids=required_ids,
        candidate_hex_chars=candidate_hex_chars,
    )
    candidate_bytes = sum(
        len(candidate_shard_bytes(profile, bid, candidate_shards[bid]))
        for bid in cbids
    )
    return {
        "name": name,
        "country_code": country_code,
        "alias_bucket": abid,
        "alias_shard_bytes": alias_bytes,
        "candidate_bucket_count": len(cbids),
        "candidate_buckets": cbids,
        "candidate_shard_bytes": candidate_bytes,
        "total_lookup_bytes": alias_bytes + candidate_bytes,
        "match_count": len(all_ids),
        "resolved_ids": all_ids,
        "materialized_preview_ids": required_ids,
        "materialized_record_count": len(found),
    }


def benchmark_split_records(
    records: dict[str, dict[str, Any]],
    *,
    profile: int,
    alias_hex_chars: int,
    candidate_hex_chars: int,
    fixtures: Iterable[dict[str, str | None]] = FIXTURES,
) -> dict[str, Any]:
    alias_shards, candidate_shards = build_split_shards(
        records,
        alias_hex_chars=alias_hex_chars,
        candidate_hex_chars=candidate_hex_chars,
    )

    alias_sizes = [
        len(alias_shard_bytes(profile, bid, shard))
        for bid, shard in alias_shards.items()
    ]
    candidate_sizes = [
        len(candidate_shard_bytes(profile, bid, shard))
        for bid, shard in candidate_shards.items()
    ]

    fixture_results = []
    fixture_parity = True
    for fixture in fixtures:
        name = str(fixture["name"])
        country = fixture["country_code"]
        expected = direct_exact_ids(records, name, country_code=country)
        measurement = lookup_measurement(
            alias_shards,
            candidate_shards,
            profile=profile,
            name=name,
            country_code=country,
            alias_hex_chars=alias_hex_chars,
            candidate_hex_chars=candidate_hex_chars,
        )
        actual = sorted(set(measurement["resolved_ids"]))
        ok = actual == expected
        fixture_parity = fixture_parity and ok
        fixture_results.append(
            {
                **measurement,
                "expected_ids": expected,
                "parity": ok,
            }
        )

    alias_total = sum(alias_sizes)
    candidate_total = sum(candidate_sizes)
    return {
        "profile": profile,
        "alias_hex_chars": alias_hex_chars,
        "candidate_hex_chars": candidate_hex_chars,
        "alias_nonempty_shards": len(alias_sizes),
        "candidate_nonempty_shards": len(candidate_sizes),
        "theoretical_file_surface": (16**alias_hex_chars) + (16**candidate_hex_chars),
        "alias_total_serialized_bytes": alias_total,
        "candidate_total_serialized_bytes": candidate_total,
        "total_serialized_bytes": alias_total + candidate_total,
        "alias_p95_shard_bytes": percentile(alias_sizes, 0.95),
        "alias_p99_shard_bytes": percentile(alias_sizes, 0.99),
        "alias_max_shard_bytes": max(alias_sizes, default=0),
        "candidate_p95_shard_bytes": percentile(candidate_sizes, 0.95),
        "candidate_p99_shard_bytes": percentile(candidate_sizes, 0.99),
        "candidate_max_shard_bytes": max(candidate_sizes, default=0),
        "fixtures": fixture_results,
        "fixture_parity": fixture_parity,
    }


def run(
    profiles: list[int],
    *,
    alias_hex_chars: int,
    candidate_hex_chars: list[int],
) -> dict[str, Any]:
    data_dir, installed_version = locate_data_dir()
    if installed_version != GEONAMESCACHE_VERSION:
        raise RuntimeError(
            f"geonamescache version mismatch: expected {GEONAMESCACHE_VERSION}, got {installed_version}"
        )

    identities = []
    inline_baseline = []
    split_benchmarks = []
    for profile in profiles:
        path = data_dir / f"cities{profile}.json"
        identity = verify_dataset(path, profile)
        identities.append(identity)
        if not identity["identity_match"]:
            raise RuntimeError(f"dataset identity mismatch for cities{profile}.json")

        records = load_records(path)

        # Current candidate from PR #172: inline alias+candidate, 3 hex.
        inline_baseline.append(
            benchmark_records(
                records,
                profile=profile,
                bucket_hex_chars=alias_hex_chars,
            )
        )

        for cwidth in candidate_hex_chars:
            split_benchmarks.append(
                benchmark_split_records(
                    records,
                    profile=profile,
                    alias_hex_chars=alias_hex_chars,
                    candidate_hex_chars=cwidth,
                )
            )

    return {
        "schema": "astrology-place-split-shard-benchmark-v1",
        "status": "PASS"
        if all(i["fixture_parity"] for i in inline_baseline)
        and all(s["fixture_parity"] for s in split_benchmarks)
        else "FAIL",
        "scope": "research-only; no production admission change",
        "source": {
            "package": f"geonamescache=={GEONAMESCACHE_VERSION}",
            "source_revision": GEONAMESCACHE_SOURCE_REVISION,
            "dataset_origin": "GeoNames",
            "dataset_license": "CC-BY-4.0",
        },
        "dataset_identity": identities,
        "inline_3hex_baseline": inline_baseline,
        "split_benchmarks": split_benchmarks,
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
    parser.add_argument("--alias-hex-chars", type=int, default=3)
    parser.add_argument(
        "--candidate-hex-chars",
        type=int,
        nargs="+",
        default=[2, 3, 4],
    )
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = run(
        args.profiles,
        alias_hex_chars=args.alias_hex_chars,
        candidate_hex_chars=args.candidate_hex_chars,
    )
    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
