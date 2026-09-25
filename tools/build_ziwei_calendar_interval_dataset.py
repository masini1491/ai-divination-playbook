#!/usr/bin/env python3
"""Build a deterministic research/candidate Zi Wei interval calendar dataset.

The builder remains range-parameterized. Only the explicitly selected
1900..2100 range is labeled as the current product-range candidate, and even
that dataset remains non-production until a later admission migrates the
runtime resolver/materialization contract.
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

from tools.build_ziwei_tool_bundle import (
    DEPENDENCY_BLOBS,
    DEPENDENCY_LICENSE,
    DEPENDENCY_PACKAGE,
    DEPENDENCY_REPOSITORY,
    DEPENDENCY_REVISION,
    DEPENDENCY_VERSION,
    dependency_root,
    git_blob_sha,
)
from tools.ziwei_calendar_interval_poc import (
    SCHEMA_NAME as SHARD_SCHEMA_NAME,
    SCHEMA_VERSION as SHARD_SCHEMA_VERSION,
    STATUS as SHARD_STATUS,
    aggregate_hash,
    write_year_shard,
)

MANIFEST_SCHEMA_NAME="ziwei_calendar_interval_dataset_manifest"
MANIFEST_SCHEMA_VERSION="0.2.0-candidate"
POC_STATUS="RESEARCH_POC_NOT_PRODUCTION"
CANDIDATE_STATUS="RESEARCH_CANDIDATE_NOT_PRODUCTION"
SELECTED_START_YEAR=1900
SELECTED_END_YEAR=2100
SELECTED_RANGE_STATUS="SELECTED_CANDIDATE_NOT_PRODUCTION_ADMITTED"
UNSELECTED_RANGE_STATUS="RESEARCH_RANGE_NOT_SELECTED"
PROVENANCE_SCHEMA_NAME="ziwei_calendar_dataset_provenance"
PROVENANCE_SCHEMA_VERSION="1.0.0"
GENERATOR_PATH="tools/build_ziwei_calendar_interval_dataset.py"
SOURCE_INVENTORY_OWNER="tools/build_ziwei_tool_bundle.py"
AGGREGATE_HASH_ALGORITHM="sha256(path + NUL + bytes + NUL, lexicographic path order)"
SOURCE_INVENTORY_HASH_ALGORITHM="sha256(path + NUL + sha256 + NUL, lexicographic path order)"

def _canonical_bytes(payload:dict[str,Any])->bytes:
    return (json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)+"\n").encode("utf-8")

def _sha256_bytes(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()

def _sha256(path:Path)->str:
    return _sha256_bytes(path.read_bytes())

def _generator_sha256()->str:
    return _sha256(ROOT/GENERATOR_PATH)

def selected_range(start_year:int,end_year:int)->bool:
    return start_year==SELECTED_START_YEAR and end_year==SELECTED_END_YEAR

def range_contract(start_year:int,end_year:int)->dict[str,Any]:
    is_selected=selected_range(start_year,end_year)
    return {
        "status":SELECTED_RANGE_STATUS if is_selected else UNSELECTED_RANGE_STATUS,
        "selected":is_selected,
        "start_date":f"{start_year:04d}-01-01",
        "end_date":f"{end_year:04d}-12-31",
        "production_admitted":False,
    }

def dependency_source_identity()->dict[str,Any]:
    """Fail closed unless installed source bytes match the pinned upstream blobs."""
    dep_root=dependency_root()
    inventory=[]
    total_bytes=0
    for path,expected_blob in sorted(DEPENDENCY_BLOBS.items()):
        data=(dep_root/path).read_bytes()
        actual_blob=git_blob_sha(data)
        if actual_blob!=expected_blob:
            raise RuntimeError(
                f"pinned dependency byte mismatch: {path}: {actual_blob} != {expected_blob}"
            )
        item={
            "path":path,
            "bytes":len(data),
            "sha256":_sha256_bytes(data),
            "git_blob_sha":actual_blob,
        }
        inventory.append(item)
        total_bytes+=len(data)
    h=hashlib.sha256()
    for item in inventory:
        h.update(item["path"].encode("utf-8"))
        h.update(b"\0")
        h.update(item["sha256"].encode("ascii"))
        h.update(b"\0")
    return {
        "identity_policy":"installed-source-bytes-must-match-pinned-upstream-git-blobs",
        "inventory_owner":SOURCE_INVENTORY_OWNER,
        "hash_algorithm":SOURCE_INVENTORY_HASH_ALGORITHM,
        "sha256":h.hexdigest(),
        "file_count":len(inventory),
        "total_bytes":total_bytes,
    }

def attribution_text(status:str)->str:
    return f"""# Zi Wei Calendar Interval Dataset Attribution

Status: **{status}**

This deterministic derived dataset is generated from the project-pinned
`lunar_python=={DEPENDENCY_VERSION}` implementation:

- upstream repository: `{DEPENDENCY_REPOSITORY}`
- pinned revision: `{DEPENDENCY_REVISION}`
- upstream license: {DEPENDENCY_LICENSE}

The dataset stores derived Gregorian→traditional-lunar interval facts only. It
does not vendor the upstream implementation and does not change current
production authority. Exact installed source bytes are verified against the
project's pinned upstream Git-blob allowlist before generation.
"""

def build_dataset(root:Path,start_year:int,end_year:int)->dict[str,Any]:
    if not isinstance(start_year,int) or not isinstance(end_year,int):
        raise ValueError("year bounds must be integers")
    if not 2 <= start_year <= end_year <= 9997:
        raise ValueError("research range must satisfy 2 <= start_year <= end_year <= 9997")

    source_identity=dependency_source_identity()
    is_selected=selected_range(start_year,end_year)
    status=CANDIDATE_STATUS if is_selected else POC_STATUS
    dataset_id=(
        f"ziwei_tw_interval_{start_year}_{end_year}_candidate_v1"
        if is_selected
        else f"ziwei_tw_interval_{start_year}_{end_year}_research_v0"
    )

    root.mkdir(parents=True,exist_ok=True)
    rels=[]
    shards=[]
    interval_total=0
    total_bytes=0
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

    provenance={
        "schema_name":PROVENANCE_SCHEMA_NAME,
        "schema_version":PROVENANCE_SCHEMA_VERSION,
        "status":status,
        "production_authority":False,
        "dataset_id":dataset_id,
        "dataset_kind":"derived_gregorian_year_shards_with_lunar_month_intervals",
        "generator":{"path":GENERATOR_PATH,"sha256":_generator_sha256()},
        "source":{
            "package":DEPENDENCY_PACKAGE,
            "version":DEPENDENCY_VERSION,
            "repository":DEPENDENCY_REPOSITORY,
            "revision":DEPENDENCY_REVISION,
            "license":DEPENDENCY_LICENSE,
            "source_identity":source_identity,
        },
        "selected_product_range":range_contract(start_year,end_year),
        "timezone_scope":"Asia/Taipei civil time",
        "runtime_policy_separation":[
            "next_day_at_23",
            "split_after_day_15",
            "hour_branch_mapping",
        ],
        "license_note":"Upstream implementation is MIT licensed; this tree stores deterministic derived calendar facts, not vendored upstream implementation.",
    }
    provenance_path=root/"provenance.json"
    provenance_path.write_bytes(_canonical_bytes(provenance))
    attribution_path=root/"ATTRIBUTION.md"
    attribution_path.write_text(attribution_text(status),encoding="utf-8")

    metadata_files=[
        {"path":"provenance.json","sha256":_sha256(provenance_path),"bytes":provenance_path.stat().st_size},
        {"path":"ATTRIBUTION.md","sha256":_sha256(attribution_path),"bytes":attribution_path.stat().st_size},
    ]

    manifest={
        "schema_name":MANIFEST_SCHEMA_NAME,
        "schema_version":MANIFEST_SCHEMA_VERSION,
        "status":status,
        "production_admitted":False,
        "dataset_id":dataset_id,
        "selected_product_range":range_contract(start_year,end_year),
        "requested_gregorian_range":{"start_year":start_year,"end_year":end_year},
        "materialized_year_range":{"start_year":start_year,"end_year":end_year+1},
        "generator":{"path":GENERATOR_PATH,"sha256":_generator_sha256()},
        "dependency":{
            "package":DEPENDENCY_PACKAGE,
            "version":DEPENDENCY_VERSION,
            "repository":DEPENDENCY_REPOSITORY,
            "revision":DEPENDENCY_REVISION,
            "license":DEPENDENCY_LICENSE,
            "source_identity":source_identity,
        },
        "shard_contract":{
            "schema_name":SHARD_SCHEMA_NAME,
            "schema_version":SHARD_SCHEMA_VERSION,
            "status":SHARD_STATUS,
            "shard_key":"Gregorian year",
            "record":"lunar-month interval",
        },
        "one_query_contract":{"ordinary_date_max_files":1,"rat_hour_cross_year_max_files":2},
        "metadata_files":metadata_files,
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
        "selected_product_range":manifest["selected_product_range"],
        "source_inventory_sha256":manifest["dependency"]["source_identity"]["sha256"],
        "shard_count":manifest["summary"]["shard_count"],
        "interval_count":manifest["summary"]["interval_count"],
        "total_shard_bytes":manifest["summary"]["total_shard_bytes"],
        "aggregate_hash":manifest["aggregate_hash"],
    },ensure_ascii=False,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
