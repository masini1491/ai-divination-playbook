#!/usr/bin/env python3
"""Build the derived ChatGPT transport bundle for deterministic Zi Wei Scope-A.

The v2 bundle contains repo-local production runtime/retrieval bytes only.
Gregorian calendar data is materialized query-bounded from exact-commit year
shards; pinned lunar_python remains build/parity evidence and is not bundled.
"""
from __future__ import annotations
import argparse, base64, hashlib, importlib.metadata, importlib.util, json, zlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/"runtime"/"ziwei"/"CHATGPT_DETERMINISTIC_TOOL_BUNDLE.json"
SOURCE_REPOSITORY="masini1491/ai-divination-playbook"
SCHEMA_VERSION=2
AUTHORITY="derived-transport-cache-only"
CONTRACT="chunked-model-mediated-ziwei-deterministic-tool-bundle-v2"
CHUNK_SIZE=444; CHUNK_RETRY_LIMIT=2
DEPENDENCY_PACKAGE="lunar_python"; DEPENDENCY_VERSION="1.4.8"
DEPENDENCY_REPOSITORY="6tail/lunar-python"; DEPENDENCY_REVISION="000c8a3d74eed098d6256a28fdd51b869324c559"
DEPENDENCY_LICENSE="MIT"; DEPENDENCY_LICENSE_BLOB="f02d3b9375ad9cd6eb17cabdc9723b91e257f612"
CALENDAR_DATASET_ID="ziwei_tw_interval_1900_2100_candidate_v1"
CALENDAR_DATASET_ROOT="data/calendar/ziwei_tw_interval/v1"
CALENDAR_DATASET_AGGREGATE_SHA256="4913a39e770afcd21eedc387523c572b8c4fc6469889c28f6ea75613f8984d79"
CALENDAR_SUPPORTED_START="1900-01-01"; CALENDAR_SUPPORTED_END="2100-12-31"

PROJECT_PATHS=(
 "tools/ziwei_runtime.py",
 "schemas/ziwei/ZIWEI_READING_REQUEST_V1.schema.json",
 "schemas/ziwei/ZIWEI_READING_RESULT_V1.schema.json",
 "tools/ziwei_calendar_provider.py",
 "tools/ziwei_gregorian_pipeline.py",
 "tools/ziwei_natal_provider.py",
 "tools/ziwei_scope_a_pipeline.py",
 "tools/ziwei_brightness_provider.py",
 "tools/ziwei_m0_auxiliary_provider.py",
 "tools/ziwei_brightness_pipeline.py",
 "tools/ziwei_claim_retrieval.py",
 "tools/ziwei_delivery.py",
 "references/ziwei/ziwei_interpretation_claim_registry_batch1.json",
 "references/ziwei/ziwei_interpretation_claim_registry_batch2.json",
 "references/ziwei/ziwei_interpretation_claim_registry_palaces_v0.json",
 "references/ziwei/ziwei_interpretation_claim_registry_m0_auxiliary_v1.json",
)
DEPENDENCY_BLOBS={
"lunar_python/__init__.py":"373688d6a5c8b65322df473345adc195a811709b",
"lunar_python/EightChar.py":"c0c8e30b75c38c35158f1f5be05bcb25602c7a3a",
"lunar_python/eightchar/__init__.py":"cc814db9cdef7c7454ac39cfdab925da0c2d5259",
"lunar_python/eightchar/DaYun.py":"277ff719de96a351797a80b338d8b1c15486e99b",
"lunar_python/eightchar/LiuNian.py":"2a88edae1b3a026e441d363e5b63e1e2907fb99f",
"lunar_python/eightchar/LiuYue.py":"3643c3fac3f698aba0b3dbb3756d0247542a9300",
"lunar_python/eightchar/XiaoYun.py":"5fe00a2802289b8911642039bca68a089800ffd6",
"lunar_python/eightchar/Yun.py":"a5c6ffb302a09b9a0e47318c06eda9b9bbcc5067",
"lunar_python/Foto.py":"aa31edebd46858bc7f4ea4e7ef25d9b1f9d66ddf",
"lunar_python/FotoFestival.py":"ab72a416a93c04fa2987faf45a48dad4e0a9218b",
"lunar_python/Fu.py":"165038df9ac640505daa95329461f3a916382df4",
"lunar_python/Holiday.py":"aa361df85a5360aff365b0a15fd07c4105df29b5",
"lunar_python/JieQi.py":"24250e2b6d89eb4f6eb096c255ad01c854498fbb",
"lunar_python/Lunar.py":"7ee9a58c9b8d70cc1318a89140e7b57b9249231c",
"lunar_python/LunarMonth.py":"f409bfa539bbf0534a0cd917dadaa84111af4f56",
"lunar_python/LunarTime.py":"98716ac765c083b45821a0bb16653c05d1fcb770",
"lunar_python/LunarYear.py":"a4f7bf2bd9ff0b44878e91ab62eb9773c088fd64",
"lunar_python/NineStar.py":"f571c07cc27dbb95b6197c75338a11d63ab12a38",
"lunar_python/ShuJiu.py":"6dfff503a6cc5a0738b3f27eda59108a125f968c",
"lunar_python/Solar.py":"81f17823495c2db7aadf3661bb2540423a3f3a74",
"lunar_python/SolarHalfYear.py":"b458ba00db82cfe78fac668b0d570b76300e4e8f",
"lunar_python/SolarMonth.py":"99abd68cf480eef807378ca2ec6798034b539d7d",
"lunar_python/SolarSeason.py":"e7d8a2d352a0bff1529989417527fd2bd8841505",
"lunar_python/SolarWeek.py":"7f24a1832e7ec060e9f7160b8da090950f66ad86",
"lunar_python/SolarYear.py":"aa335c8308c0a6e243a05b1dad2d8d776f7087b1",
"lunar_python/Tao.py":"a08f79d7413bf76aeaf59d76633ebaa13a80f08d",
"lunar_python/TaoFestival.py":"99b03ed72e03291d301b2c859234f1a120e8b7a9",
"lunar_python/util/__init__.py":"a8f0b52b75add0a27bd81e3be588dafcd56b4e2c",
"lunar_python/util/FotoUtil.py":"21d1436e2013c1bfd134df194e12375a61b0cf62",
"lunar_python/util/HolidayUtil.py":"7cb4f41432e9f3a51d8553fea38c962c51b8f696",
"lunar_python/util/LunarUtil.py":"61b0c5c236ece0cbb911a48a6f8147fc3f1fde2d",
"lunar_python/util/ShouXingUtil.py":"fd4eb7450b3d043ff7e446da0251b437cbe58f61",
"lunar_python/util/SolarUtil.py":"5d608b66bb82778619a0d3b66aec19e8c1585c70",
"lunar_python/util/TaoUtil.py":"311c5347bbef2a806575041ab4b39e3551f7b83f",
}

def dependency_license_bytes()->bytes:
    dist=importlib.metadata.distribution(DEPENDENCY_PACKAGE)
    candidates=[p for p in (dist.files or ()) if Path(str(p)).name.upper()=="LICENSE"]
    if len(candidates)!=1: raise RuntimeError(f"expected exactly one installed dependency LICENSE, found {len(candidates)}")
    data=Path(dist.locate_file(candidates[0])).read_bytes()
    if git_blob_sha(data)!=DEPENDENCY_LICENSE_BLOB: raise RuntimeError("installed dependency LICENSE byte mismatch")
    return data

def sha256(data:bytes)->str: return hashlib.sha256(data).hexdigest()
def git_blob_sha(data:bytes)->str: return hashlib.sha1(f"blob {len(data)}\0".encode("ascii")+data).hexdigest()
def dependency_root()->Path:
    spec=importlib.util.find_spec(DEPENDENCY_PACKAGE)
    if spec is None or not spec.submodule_search_locations: raise RuntimeError(f"{DEPENDENCY_PACKAGE} is not installed")
    return Path(next(iter(spec.submodule_search_locations))).parent

def _entry(path:str,data:bytes,origin:str,offset:int)->dict[str,object]:
    return {"path":path,"origin":origin,"byte_size":len(data),"offset":offset,"sha256":sha256(data),"git_blob_sha":git_blob_sha(data)}

def build_bundle()->dict[str,object]:
    manifest=[]; parts=[]; offset=0
    for path in PROJECT_PATHS:
        data=(ROOT/path).read_bytes(); manifest.append(_entry(path,data,"playbook",offset)); parts.append(data); offset+=len(data)
    archive=b"".join(parts); compressed=zlib.compress(archive,9); encoded=base64.b64encode(compressed).decode("ascii")
    chunks=[encoded[i:i+CHUNK_SIZE] for i in range(0,len(encoded),CHUNK_SIZE)]
    return {
      "schema_version":SCHEMA_VERSION,"authority":AUTHORITY,"contract":CONTRACT,"source_repository":SOURCE_REPOSITORY,
      "source_revision_policy":"same-resolved-playbook-commit","source_files":manifest,
      "calendar_data":{"dataset_id":CALENDAR_DATASET_ID,"root":CALENDAR_DATASET_ROOT,"aggregate_sha256":CALENDAR_DATASET_AGGREGATE_SHA256,
        "supported_range":{"start":CALENDAR_SUPPORTED_START,"end":CALENDAR_SUPPORTED_END},
        "materialization":"query-bounded exact-commit year shard","ordinary_max_files":1,"year_edge_23_max_files":2},
      "build_dependency":{"package":DEPENDENCY_PACKAGE,"version":DEPENDENCY_VERSION,"repository":DEPENDENCY_REPOSITORY,
        "revision":DEPENDENCY_REVISION,"license":DEPENDENCY_LICENSE,"runtime_bundled":False,"runtime_file_count":0,"role":"build_parity_only"},
      "archive":{"layout":"raw-concat-by-source_files-order","decoded_size":len(archive),"sha256":sha256(archive),"compression":"zlib",
        "encoding":"base64","compressed_size":len(compressed),"encoded_size":len(encoded),"chunk_size":CHUNK_SIZE,"chunk_count":len(chunks),
        "reassembly":"index-ascending-concat","chunk_retry_limit":CHUNK_RETRY_LIMIT,"retry_source":"fresh-read-same-commit-bundle-failed-chunk-only"},
      "execution_contract":{"must_attempt_after_verified_local_cache_miss":True,"verify_each_chunk_before_reassembly":True,
        "verify_archive_before_unpack":True,"verify_each_file_before_write_or_import":True,"preserve_calendar_provenance":True,
        "calendar_shard_materialization_required_for_gregorian_input":True,"interpretation_authority":False,"new_claim_authority":False,
        "dependency_install_required_after_materialization":False},
      "cache_contract":{"cache_dir":"/mnt/data/divination-ziwei-runtime","marker":"bundle_verification.json",
        "required_marker_fields":["verified","repository","playbook_commit","bundle_contract","archive_sha256","calendar_data","files"],
        "reuse_only_when_all_source_file_identities_match":True},
      "chunks":[{"index":i,"encoded_length":len(c),"sha256":sha256(c.encode("ascii")),"payload":c} for i,c in enumerate(chunks)]
    }

def render(v:dict[str,object])->str: return json.dumps(v,ensure_ascii=False,indent=2)+"\n"
def decode_archive(bundle:dict[str,object])->bytes:
    chunks=sorted(bundle["chunks"],key=lambda x:int(x["index"]))
    if [int(x["index"]) for x in chunks]!=list(range(len(chunks))): raise ValueError("chunk indexes invalid")
    parts=[]
    for item in chunks:
        p=item["payload"]
        if len(p)!=int(item["encoded_length"]): raise ValueError(f"chunk {item['index']} length mismatch")
        if sha256(p.encode("ascii"))!=item["sha256"]: raise ValueError(f"chunk {item['index']} sha mismatch")
        parts.append(p)
    encoded="".join(parts); meta=bundle["archive"]
    if len(encoded)!=int(meta["encoded_size"]): raise ValueError("encoded_size mismatch")
    compressed=base64.b64decode(encoded,validate=True)
    if len(compressed)!=int(meta["compressed_size"]): raise ValueError("compressed_size mismatch")
    archive=zlib.decompress(compressed)
    if len(archive)!=int(meta["decoded_size"]) or sha256(archive)!=meta["sha256"]: raise ValueError("archive identity mismatch")
    return archive

def verify_bundle(bundle:dict[str,object],*,compare_project:bool=True)->list[str]:
    errors=[]
    try:
        for k,v in {"schema_version":SCHEMA_VERSION,"authority":AUTHORITY,"contract":CONTRACT,"source_repository":SOURCE_REPOSITORY}.items():
            if bundle.get(k)!=v: errors.append(f"{k} mismatch")
        cd=bundle.get("calendar_data",{})
        expected_cd={"dataset_id":CALENDAR_DATASET_ID,"root":CALENDAR_DATASET_ROOT,"aggregate_sha256":CALENDAR_DATASET_AGGREGATE_SHA256}
        for k,v in expected_cd.items():
            if cd.get(k)!=v: errors.append(f"calendar_data {k} mismatch")
        bd=bundle.get("build_dependency",{})
        for k,v in {"package":DEPENDENCY_PACKAGE,"version":DEPENDENCY_VERSION,"repository":DEPENDENCY_REPOSITORY,"revision":DEPENDENCY_REVISION,"license":DEPENDENCY_LICENSE}.items():
            if bd.get(k)!=v: errors.append(f"build_dependency {k} mismatch")
        if bd.get("runtime_bundled") is not False or int(bd.get("runtime_file_count",-1))!=0: errors.append("build dependency runtime bundling mismatch")
        archive=decode_archive(bundle); cursor=0
        for entry in bundle["source_files"]:
            if entry.get("origin")!="playbook": errors.append(f"non-playbook bundle origin: {entry.get('path')}")
            size=int(entry["byte_size"])
            if int(entry["offset"])!=cursor: errors.append(f"{entry['path']} offset mismatch")
            part=archive[cursor:cursor+size]
            if sha256(part)!=entry["sha256"] or git_blob_sha(part)!=entry["git_blob_sha"]: errors.append(f"{entry['path']} identity mismatch")
            if compare_project and part!=(ROOT/entry["path"]).read_bytes(): errors.append(f"{entry['path']} does not reproduce canonical bytes")
            cursor+=size
        if cursor!=len(archive): errors.append("archive has trailing bytes")
    except Exception as exc: errors.append(f"bundle decode error: {exc}")
    return errors

def materialize(bundle:dict[str,object],target:Path,playbook_commit:str)->dict[str,object]:
    errors=verify_bundle(bundle,compare_project=False)
    if errors: raise ValueError("; ".join(errors))
    archive=decode_archive(bundle); target.mkdir(parents=True,exist_ok=True); files=[]; cursor=0
    for entry in bundle["source_files"]:
        size=int(entry["byte_size"]); data=archive[cursor:cursor+size]; cursor+=size
        path=target/entry["path"]; path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(data)
        files.append({"path":entry["path"],"sha256":entry["sha256"],"git_blob_sha":entry["git_blob_sha"]})
    marker={"verified":True,"repository":SOURCE_REPOSITORY,"playbook_commit":playbook_commit,"bundle_contract":CONTRACT,
      "archive_sha256":bundle["archive"]["sha256"],"calendar_data":bundle["calendar_data"],"build_dependency":bundle["build_dependency"],"files":files}
    (target/bundle["cache_contract"]["marker"]).write_text(json.dumps(marker,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return marker

def materialize_repo_data_file(repo_relative_path:str,target:Path)->dict[str,object]:
    source=ROOT/repo_relative_path
    data=source.read_bytes(); path=target/repo_relative_path; path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(data)
    return {"path":repo_relative_path,"sha256":sha256(data),"git_blob_sha":git_blob_sha(data),"bytes":len(data)}

def main(argv=None)->int:
    p=argparse.ArgumentParser(); p.add_argument("--check",action="store_true"); args=p.parse_args(argv)
    expected=build_bundle(); expected_text=render(expected)
    if args.check:
        if not OUTPUT.is_file(): print(f"FAIL missing {OUTPUT.relative_to(ROOT)}"); return 1
        try: actual=json.loads(OUTPUT.read_text(encoding="utf-8"))
        except Exception as exc: print(f"FAIL Zi Wei bundle read: {exc}"); return 1
        errors=verify_bundle(actual)
        if render(actual)!=expected_text: errors.append("committed bundle is stale relative to canonical sources")
        if errors:
            for e in errors: print(f"FAIL Zi Wei bundle: {e}")
            return 1
        print("Zi Wei deterministic tool bundle: PASS"); return 0
    OUTPUT.parent.mkdir(parents=True,exist_ok=True); OUTPUT.write_text(expected_text,encoding="utf-8")
    errors=verify_bundle(expected)
    if errors:
        for e in errors: print(f"FAIL Zi Wei bundle: {e}")
        return 1
    print(f"wrote {OUTPUT.relative_to(ROOT)}"); return 0
if __name__=="__main__": raise SystemExit(main())
