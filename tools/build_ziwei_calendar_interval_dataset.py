#!/usr/bin/env python3
"""Build a deterministic research Zi Wei interval calendar dataset.

This builder is range-parameterized so a future product-supported range can be
materialized without changing the storage contract. Generated data remains
research-only until a separate production admission explicitly adopts it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from tools.ziwei_calendar_interval_poc import (
    SCHEMA_NAME as SHARD_SCHEMA_NAME,
    SCHEMA_VERSION as SHARD_SCHEMA_VERSION,
    STATUS as SHARD_STATUS,
    aggregate_hash,
    shard_relative_path,
    write_year_shard,
)

MANIFEST_SCHEMA_NAME="ziwei_calendar_interval_dataset_manifest"
MANIFEST_SCHEMA_VERSION="0.1.0-poc"
MANIFEST_STATUS="RESEARCH_POC_NOT_PRODUCTION"
DEPENDENCY_PACKAGE="lunar_python"
DEPENDENCY_VERSION="1.4.8"
DEPENDENCY_REPOSITORY="6tail/lunar-python"
DEPENDENCY_REVISION="000c8a3d74eed098d6256a28fdd51b869324c559"
DEPENDENCY_LICENSE="MIT"
AGGREGATE_HASH_ALGORITHM="sha256(path + NUL + bytes + NUL, lexicographic path order)"

def _canonical_bytes(payload:dict[str,Any])->bytes:
    return (json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)+"\n").encode("utf-8")

def _sha256(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def build_dataset(root:Path,start_year:int,end_year:int)->dict[str,Any]:
    if not isinstance(start_year,int) or not isinstance(end_year,int):
        raise ValueError("year bounds must be integers")
    if not 2 <= start_year <= end_year <= 9997:
        # Keep one civil year of head/tail room for interval generation and the
        # 23:00 policy-tail shard. Wider boundaries require separate evidence.
        raise ValueError("research range must satisfy 2 <= start_year <= end_year <= 9997")

    root.mkdir(parents=True,exist_ok=True)
    rels=[]
    shards=[]
    interval_total=0
    total_bytes=0
    # Include end_year+1 so 31 Dec 23:00 can resolve policy-next-day.
    for year in range(start_year,end_year+2):
        path=write_year_shard(root,year)
        rel=path.relative_to(root)
        payload=json.loads(path.read_text(encoding="utf-8"))
        count=len(payload["intervals"])
        size=path.stat().st_size
        interval_total+=count
        total_bytes+=size
        rels.append(rel)
        shards.append({
            "year":year,
            "path":rel.as_posix(),
            "sha256":_sha256(path),
            "bytes":size,
            "interval_count":count,
            "support_role":"policy_tail" if year==end_year+1 else "requested_range",
        })

    manifest={
        "schema_name":MANIFEST_SCHEMA_NAME,
        "schema_version":MANIFEST_SCHEMA_VERSION,
        "status":MANIFEST_STATUS,
        "production_admitted":False,
        "dataset_id":f"ziwei_tw_interval_{start_year}_{end_year}_research_v0",
        "requested_gregorian_range":{"start_year":start_year,"end_year":end_year},
        "materialized_year_range":{"start_year":start_year,"end_year":end_year+1},
        "dependency":{
            "package":DEPENDENCY_PACKAGE,
            "version":DEPENDENCY_VERSION,
            "repository":DEPENDENCY_REPOSITORY,
            "revision":DEPENDENCY_REVISION,
            "license":DEPENDENCY_LICENSE,
        },
        "shard_contract":{
            "schema_name":SHARD_SCHEMA_NAME,
            "schema_version":SHARD_SCHEMA_VERSION,
            "status":SHARD_STATUS,
            "shard_key":"Gregorian year",
            "record":"lunar-month interval",
        },
        "one_query_contract":{
            "ordinary_date_max_files":1,
            "rat_hour_cross_year_max_files":2,
        },
        "shards":shards,
        "summary":{
            "shard_count":len(shards),
            "interval_count":interval_total,
            "total_shard_bytes":total_bytes,
        },
        "aggregate_hash_algorithm":AGGREGATE_HASH_ALGORITHM,
        "aggregate_hash":aggregate_hash(root,rels),
    }
    (root/"MANIFEST.json").write_bytes(_canonical_bytes(manifest))
    return manifest

def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    p.add_argument("--start-year",type=int,required=True)
    p.add_argument("--end-year",type=int,required=True)
    args=p.parse_args()
    manifest=build_dataset(Path(args.output),args.start_year,args.end_year)
    print(json.dumps({
        "status":"PASS",
        "output":str(Path(args.output)),
        "dataset_id":manifest["dataset_id"],
        "shard_count":manifest["summary"]["shard_count"],
        "interval_count":manifest["summary"]["interval_count"],
        "total_shard_bytes":manifest["summary"]["total_shard_bytes"],
        "aggregate_hash":manifest["aggregate_hash"],
    },ensure_ascii=False,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
