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
    CANDIDATE_STATUS,
    DEPENDENCY_LICENSE,
    DEPENDENCY_PACKAGE,
    DEPENDENCY_REPOSITORY,
    DEPENDENCY_REVISION,
    DEPENDENCY_VERSION,
    GENERATOR_PATH,
    MANIFEST_SCHEMA_NAME,
    MANIFEST_SCHEMA_VERSION,
    POC_STATUS,
    PROVENANCE_SCHEMA_NAME,
    PROVENANCE_SCHEMA_VERSION,
    SOURCE_INVENTORY_HASH_ALGORITHM,
    attribution_text,
    build_dataset,
    dependency_source_identity,
    range_contract,
    selected_range,
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

def _generator_sha256()->str:
    return sha256(ROOT/GENERATOR_PATH)

def validate_dataset(root:Path,rebuild:bool=False)->dict:
    manifest_path=root/"MANIFEST.json"
    if not manifest_path.is_file():
        raise DatasetValidationError("MANIFEST.json missing")
    m=json.loads(manifest_path.read_text(encoding="utf-8"))
    if m.get("schema_name")!=MANIFEST_SCHEMA_NAME or m.get("schema_version")!=MANIFEST_SCHEMA_VERSION:
        raise DatasetValidationError("manifest schema mismatch")

    requested=m.get("requested_gregorian_range",{})
    start=int(requested["start_year"]); end=int(requested["end_year"])
    expected_status=CANDIDATE_STATUS if selected_range(start,end) else POC_STATUS
    if m.get("status")!=expected_status or m.get("production_admitted") is not False:
        raise DatasetValidationError("manifest admission/status mismatch")
    expected_range=range_contract(start,end)
    if m.get("selected_product_range")!=expected_range:
        raise DatasetValidationError("selected product range mismatch")

    generator=m.get("generator",{})
    if generator.get("path")!=GENERATOR_PATH or generator.get("sha256")!=_generator_sha256():
        raise DatasetValidationError("generator identity mismatch")

    dep=m.get("dependency",{})
    expected=(DEPENDENCY_PACKAGE,DEPENDENCY_VERSION,DEPENDENCY_REPOSITORY,DEPENDENCY_REVISION,DEPENDENCY_LICENSE)
    actual=(dep.get("package"),dep.get("version"),dep.get("repository"),dep.get("revision"),dep.get("license"))
    if actual!=expected:
        raise DatasetValidationError("dependency provenance mismatch")
    current_source_identity=dependency_source_identity()
    if dep.get("source_identity")!=current_source_identity:
        raise DatasetValidationError("dependency source identity mismatch")
    if current_source_identity.get("hash_algorithm")!=SOURCE_INVENTORY_HASH_ALGORITHM:
        raise DatasetValidationError("dependency source hash algorithm mismatch")

    provenance_path=root/"provenance.json"
    attribution_path=root/"ATTRIBUTION.md"
    if not provenance_path.is_file() or not attribution_path.is_file():
        raise DatasetValidationError("dataset metadata file missing")
    metadata=m.get("metadata_files",[])
    expected_metadata_paths=["provenance.json","ATTRIBUTION.md"]
    if [item.get("path") for item in metadata]!=expected_metadata_paths:
        raise DatasetValidationError("metadata file inventory mismatch")
    for item in metadata:
        path=root/item["path"]
        if sha256(path)!=item.get("sha256") or path.stat().st_size!=int(item.get("bytes",-1)):
            raise DatasetValidationError(f"metadata identity mismatch: {item['path']}")

    provenance=json.loads(provenance_path.read_text(encoding="utf-8"))
    if provenance.get("schema_name")!=PROVENANCE_SCHEMA_NAME or provenance.get("schema_version")!=PROVENANCE_SCHEMA_VERSION:
        raise DatasetValidationError("provenance schema mismatch")
    if provenance.get("status")!=expected_status or provenance.get("production_authority") is not False:
        raise DatasetValidationError("provenance status mismatch")
    if provenance.get("dataset_id")!=m.get("dataset_id"):
        raise DatasetValidationError("provenance dataset identity mismatch")
    if provenance.get("selected_product_range")!=expected_range:
        raise DatasetValidationError("provenance selected range mismatch")
    if provenance.get("source")!={
        "package":DEPENDENCY_PACKAGE,
        "version":DEPENDENCY_VERSION,
        "repository":DEPENDENCY_REPOSITORY,
        "revision":DEPENDENCY_REVISION,
        "license":DEPENDENCY_LICENSE,
        "source_identity":current_source_identity,
    }:
        raise DatasetValidationError("provenance source mismatch")
    if provenance.get("generator")!=m.get("generator"):
        raise DatasetValidationError("provenance generator mismatch")
    if attribution_path.read_text(encoding="utf-8")!=attribution_text(expected_status):
        raise DatasetValidationError("attribution content mismatch")

    sc=m.get("shard_contract",{})
    if (sc.get("schema_name"),sc.get("schema_version"),sc.get("status")) != (
        SHARD_SCHEMA_NAME,SHARD_SCHEMA_VERSION,SHARD_STATUS
    ):
        raise DatasetValidationError("shard contract mismatch")
    if m.get("aggregate_hash_algorithm")!=AGGREGATE_HASH_ALGORITHM:
        raise DatasetValidationError("aggregate hash algorithm mismatch")

    expected_years=list(range(start,end+2))
    shards=m.get("shards",[])
    if [int(x["year"]) for x in shards] != expected_years:
        raise DatasetValidationError("shard year inventory mismatch")
    expected_paths=[item["path"] for item in shards]
    actual_paths=sorted(p.relative_to(root).as_posix() for p in (root/"years").glob("*.json"))
    if actual_paths!=expected_paths:
        raise DatasetValidationError("shard file inventory mismatch")

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
                and (rebuilt_root/"provenance.json").read_bytes()==provenance_path.read_bytes()
                and (rebuilt_root/"ATTRIBUTION.md").read_bytes()==attribution_path.read_bytes()
            )
            if not rebuilt_match:
                raise DatasetValidationError("deterministic rebuild mismatch")

    return {
        "status":"PASS",
        "dataset_id":m["dataset_id"],
        "selected_product_range":m["selected_product_range"],
        "requested_gregorian_range":m["requested_gregorian_range"],
        "source_inventory_sha256":current_source_identity["sha256"],
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
