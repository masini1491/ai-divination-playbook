#!/usr/bin/env python3
"""Validate and optionally deterministically rebuild a Zi Wei interval dataset."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from tools.build_ziwei_calendar_interval_dataset import (
    AGGREGATE_HASH_ALGORITHM,
    DEPENDENCY_PACKAGE,
    DEPENDENCY_REPOSITORY,
    DEPENDENCY_REVISION,
    DEPENDENCY_VERSION,
    MANIFEST_SCHEMA_NAME,
    MANIFEST_SCHEMA_VERSION,
    MANIFEST_STATUS,
    build_dataset,
)
from tools.ziwei_calendar_interval_poc import (
    SCHEMA_NAME as SHARD_SCHEMA_NAME,
    SCHEMA_VERSION as SHARD_SCHEMA_VERSION,
    STATUS as SHARD_STATUS,
    aggregate_hash,
)

class DatasetValidationError(ValueError):
    pass

def sha256(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def validate_dataset(root:Path,rebuild:bool=False)->dict:
    manifest_path=root/"MANIFEST.json"
    if not manifest_path.is_file():
        raise DatasetValidationError("MANIFEST.json missing")
    m=json.loads(manifest_path.read_text(encoding="utf-8"))
    if m.get("schema_name")!=MANIFEST_SCHEMA_NAME or m.get("schema_version")!=MANIFEST_SCHEMA_VERSION:
        raise DatasetValidationError("manifest schema mismatch")
    if m.get("status")!=MANIFEST_STATUS or m.get("production_admitted") is not False:
        raise DatasetValidationError("manifest admission/status mismatch")
    dep=m.get("dependency",{})
    expected=(DEPENDENCY_PACKAGE,DEPENDENCY_VERSION,DEPENDENCY_REPOSITORY,DEPENDENCY_REVISION)
    actual=(dep.get("package"),dep.get("version"),dep.get("repository"),dep.get("revision"))
    if actual!=expected:
        raise DatasetValidationError("dependency provenance mismatch")
    sc=m.get("shard_contract",{})
    if (sc.get("schema_name"),sc.get("schema_version"),sc.get("status")) != (
        SHARD_SCHEMA_NAME,SHARD_SCHEMA_VERSION,SHARD_STATUS
    ):
        raise DatasetValidationError("shard contract mismatch")
    if m.get("aggregate_hash_algorithm")!=AGGREGATE_HASH_ALGORITHM:
        raise DatasetValidationError("aggregate hash algorithm mismatch")

    requested=m.get("requested_gregorian_range",{})
    start=int(requested["start_year"]); end=int(requested["end_year"])
    expected_years=list(range(start,end+2))
    shards=m.get("shards",[])
    if [int(x["year"]) for x in shards] != expected_years:
        raise DatasetValidationError("shard year inventory mismatch")
    rels=[]
    interval_total=0
    total_bytes=0
    for item in shards:
        rel=Path(item["path"])
        path=root/rel
        if not path.is_file():
            raise DatasetValidationError(f"shard missing: {rel}")
        if sha256(path)!=item.get("sha256"):
            raise DatasetValidationError(f"shard sha256 mismatch: {rel}")
        if path.stat().st_size!=int(item["bytes"]):
            raise DatasetValidationError(f"shard byte size mismatch: {rel}")
        payload=json.loads(path.read_text(encoding="utf-8"))
        if payload.get("gregorian_year")!=int(item["year"]):
            raise DatasetValidationError(f"shard year mismatch: {rel}")
        if payload.get("schema_name")!=SHARD_SCHEMA_NAME or payload.get("schema_version")!=SHARD_SCHEMA_VERSION or payload.get("status")!=SHARD_STATUS:
            raise DatasetValidationError(f"shard payload contract mismatch: {rel}")
        count=len(payload.get("intervals",[]))
        if count!=int(item["interval_count"]):
            raise DatasetValidationError(f"interval count mismatch: {rel}")
        interval_total+=count
        total_bytes+=path.stat().st_size
        rels.append(rel)

    summary=m.get("summary",{})
    if int(summary.get("shard_count",-1))!=len(shards) or int(summary.get("interval_count",-1))!=interval_total or int(summary.get("total_shard_bytes",-1))!=total_bytes:
        raise DatasetValidationError("manifest summary mismatch")
    got_aggregate=aggregate_hash(root,rels)
    if got_aggregate!=m.get("aggregate_hash"):
        raise DatasetValidationError("aggregate hash mismatch")

    rebuilt_match=None
    if rebuild:
        with tempfile.TemporaryDirectory() as td:
            rebuilt_root=Path(td)
            rebuilt=build_dataset(rebuilt_root,start,end)
            rebuilt_match=(
                rebuilt["aggregate_hash"]==m["aggregate_hash"]
                and rebuilt["summary"]==m["summary"]
                and (rebuilt_root/"MANIFEST.json").read_bytes()==manifest_path.read_bytes()
            )
            if not rebuilt_match:
                raise DatasetValidationError("deterministic rebuild mismatch")

    return {
        "status":"PASS",
        "dataset_id":m["dataset_id"],
        "requested_gregorian_range":m["requested_gregorian_range"],
        "shard_count":len(shards),
        "interval_count":interval_total,
        "total_shard_bytes":total_bytes,
        "aggregate_hash":got_aggregate,
        "deterministic_rebuild_match":rebuilt_match,
    }

def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--root",required=True)
    p.add_argument("--rebuild",action="store_true")
    args=p.parse_args()
    print(json.dumps(validate_dataset(Path(args.root),args.rebuild),ensure_ascii=False,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
