#!/usr/bin/env python3
"""Build the derived ChatGPT transport bundle for Astrology deterministic core."""
from __future__ import annotations
import argparse, base64, hashlib, importlib.metadata, importlib.util, json, zlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/"runtime"/"astrology"/"CHATGPT_DETERMINISTIC_CORE_BUNDLE.json"
SOURCE_REPOSITORY="masini1491/ai-divination-playbook"
SCHEMA_VERSION=1
AUTHORITY="derived-transport-cache-only"
CONTRACT="chunked-model-mediated-astrology-deterministic-core-bundle-v1"
CHUNK_SIZE=444
CHUNK_RETRY_LIMIT=2
DEPENDENCY_PACKAGE="astronomy-engine"
DEPENDENCY_IMPORT="astronomy"
DEPENDENCY_VERSION="2.1.19"
DEPENDENCY_REPOSITORY="cosinekitty/astronomy"
DEPENDENCY_REVISION="865d3da7d8112bbc7911238052c6af4aaf877181"
DEPENDENCY_LICENSE="MIT"
DEPENDENCY_LICENSE_BLOB="cb43597eccade848b55b474a63c6649106631f02"

PROJECT_PATHS=(
 "tools/astrology_runtime.py",
 "tools/astrology_provider.py",
 "tools/astrology_transit_provider.py",
 "tools/astrology_orchestrator.py",
)
DEPENDENCY_BLOBS={
 "astronomy/__init__.py":"a51b00b1a7b0e9b9c9a419f9ed34433a7c2c1a2e",
 "astronomy/astronomy.py":"1a48fdf620540df22fcf421d0df0c2c016999e52",
}

def sha256(data:bytes)->str: return hashlib.sha256(data).hexdigest()
def git_blob_sha(data:bytes)->str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii")+data).hexdigest()

def dependency_root()->Path:
    if importlib.metadata.version(DEPENDENCY_PACKAGE) != DEPENDENCY_VERSION:
        raise RuntimeError(f"{DEPENDENCY_PACKAGE} version mismatch")
    spec=importlib.util.find_spec(DEPENDENCY_IMPORT)
    if spec is None or not spec.submodule_search_locations:
        raise RuntimeError(f"{DEPENDENCY_IMPORT} is not installed")
    return Path(next(iter(spec.submodule_search_locations))).parent

def dependency_license_bytes()->bytes:
    dist=importlib.metadata.distribution(DEPENDENCY_PACKAGE)
    candidates=[p for p in (dist.files or ()) if Path(str(p)).name.upper()=="LICENSE"]
    if len(candidates)!=1:
        raise RuntimeError(f"expected exactly one installed dependency LICENSE, found {len(candidates)}")
    data=Path(dist.locate_file(candidates[0])).read_bytes()
    if git_blob_sha(data)!=DEPENDENCY_LICENSE_BLOB:
        raise RuntimeError(f"installed dependency LICENSE byte mismatch: {git_blob_sha(data)}")
    return data

def _entry(path:str,data:bytes,origin:str,offset:int,expected_blob:str|None=None)->dict[str,object]:
    actual=git_blob_sha(data)
    if expected_blob is not None and actual!=expected_blob:
        raise RuntimeError(f"pinned byte mismatch: {path}: {actual} != {expected_blob}")
    return {"path":path,"origin":origin,"byte_size":len(data),"offset":offset,
            "sha256":sha256(data),"git_blob_sha":actual}

def build_bundle()->dict[str,object]:
    manifest=[]; parts=[]; offset=0
    for path in PROJECT_PATHS:
        data=(ROOT/path).read_bytes()
        manifest.append(_entry(path,data,"playbook",offset))
        parts.append(data); offset+=len(data)

    dep_root=dependency_root()
    for path,expected_blob in DEPENDENCY_BLOBS.items():
        data=(dep_root/path).read_bytes()
        manifest.append(_entry(path,data,"dependency",offset,expected_blob))
        parts.append(data); offset+=len(data)

    license_bytes=dependency_license_bytes()
    license_path="third_party/astronomy-engine/LICENSE"
    manifest.append(_entry(license_path,license_bytes,"dependency-license",offset,DEPENDENCY_LICENSE_BLOB))
    parts.append(license_bytes); offset+=len(license_bytes)

    archive=b"".join(parts)
    compressed=zlib.compress(archive,9)
    encoded=base64.b64encode(compressed).decode("ascii")
    chunks=[encoded[i:i+CHUNK_SIZE] for i in range(0,len(encoded),CHUNK_SIZE)]
    return {
      "schema_version":SCHEMA_VERSION,"authority":AUTHORITY,"contract":CONTRACT,
      "source_repository":SOURCE_REPOSITORY,
      "source_revision_policy":"same-resolved-playbook-commit",
      "source_files":manifest,
      "dependency":{
        "package":DEPENDENCY_PACKAGE,"import_name":DEPENDENCY_IMPORT,"version":DEPENDENCY_VERSION,
        "repository":DEPENDENCY_REPOSITORY,"revision":DEPENDENCY_REVISION,"license":DEPENDENCY_LICENSE,
        "license_bundle_path":license_path,"runtime_file_count":len(DEPENDENCY_BLOBS),
        "byte_identity":"installed-package-source-must-match-pinned-upstream-git-blobs"
      },
      "scope":{
        "natal_core":True,"transit_core":True,"explicit_coordinates_plus_iana_timezone":True,
        "place_resolver_included":False,"geonamescache_included":False
      },
      "archive":{
        "layout":"raw-concat-by-source_files-order","decoded_size":len(archive),"sha256":sha256(archive),
        "compression":"zlib","encoding":"base64","compressed_size":len(compressed),"encoded_size":len(encoded),
        "chunk_size":CHUNK_SIZE,"chunk_count":len(chunks),"reassembly":"index-ascending-concat",
        "chunk_retry_limit":CHUNK_RETRY_LIMIT,"retry_source":"fresh-read-same-commit-bundle-failed-chunk-only"
      },
      "execution_contract":{
        "must_attempt_after_verified_local_cache_miss":True,
        "verify_each_chunk_before_reassembly":True,"verify_archive_before_unpack":True,
        "verify_each_file_before_write_or_import":True,
        "dependency_install_required_after_materialization":False,
        "place_resolver_required_for_explicit_coordinates":False,
        "interpretation_authority":False,"new_claim_authority":False
      },
      "cache_contract":{
        "cache_dir":"/mnt/data/divination-astrology-runtime",
        "marker":"core_bundle_verification.json",
        "required_marker_fields":["verified","repository","playbook_commit","bundle_contract","archive_sha256","dependency","files"],
        "reuse_only_when_all_source_file_identities_match":True
      },
      "chunks":[{"index":i,"encoded_length":len(c),"sha256":sha256(c.encode("ascii")),"payload":c}
                for i,c in enumerate(chunks)]
    }

def render(v:dict[str,object])->str: return json.dumps(v,ensure_ascii=False,indent=2)+"\n"

def decode_archive(bundle:dict[str,object])->bytes:
    chunks=sorted(bundle["chunks"],key=lambda x:int(x["index"]))
    if [int(x["index"]) for x in chunks] != list(range(len(chunks))):
        raise ValueError("chunk indexes invalid")
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
    if len(archive)!=int(meta["decoded_size"]): raise ValueError("decoded_size mismatch")
    if sha256(archive)!=meta["sha256"]: raise ValueError("archive sha mismatch")
    return archive

def verify_bundle(bundle:dict[str,object], *, compare_project:bool=True)->list[str]:
    errors=[]
    try:
        if bundle.get("schema_version")!=SCHEMA_VERSION: errors.append("schema_version mismatch")
        if bundle.get("authority")!=AUTHORITY: errors.append("authority mismatch")
        if bundle.get("contract")!=CONTRACT: errors.append("contract mismatch")
        if bundle.get("source_repository")!=SOURCE_REPOSITORY: errors.append("source_repository mismatch")
        dep=bundle.get("dependency",{})
        for k,v in {"package":DEPENDENCY_PACKAGE,"version":DEPENDENCY_VERSION,"repository":DEPENDENCY_REPOSITORY,
                    "revision":DEPENDENCY_REVISION,"license":DEPENDENCY_LICENSE}.items():
            if dep.get(k)!=v: errors.append(f"dependency {k} mismatch")
        scope=bundle.get("scope",{})
        if scope.get("place_resolver_included") is not False: errors.append("place resolver must remain excluded")
        archive=decode_archive(bundle); cursor=0
        for entry in bundle["source_files"]:
            size=int(entry["byte_size"])
            if int(entry["offset"])!=cursor: errors.append(f"{entry['path']} offset mismatch")
            part=archive[cursor:cursor+size]
            if sha256(part)!=entry["sha256"]: errors.append(f"{entry['path']} sha mismatch")
            if git_blob_sha(part)!=entry["git_blob_sha"]: errors.append(f"{entry['path']} git blob mismatch")
            if compare_project and entry["origin"]=="playbook" and part!=(ROOT/entry["path"]).read_bytes():
                errors.append(f"{entry['path']} does not reproduce canonical bytes")
            if entry["origin"]=="dependency":
                expected=DEPENDENCY_BLOBS.get(entry["path"])
                if expected!=entry["git_blob_sha"]: errors.append(f"{entry['path']} pinned upstream blob mismatch")
            if entry["origin"]=="dependency-license" and git_blob_sha(part)!=DEPENDENCY_LICENSE_BLOB:
                errors.append("dependency license bytes mismatch")
            cursor+=size
        if cursor!=len(archive): errors.append("archive has trailing bytes")
    except Exception as exc:
        errors.append(f"bundle decode error: {exc}")
    return errors

def materialize(bundle:dict[str,object], target:Path, playbook_commit:str)->dict[str,object]:
    errors=verify_bundle(bundle,compare_project=False)
    if errors: raise ValueError("; ".join(errors))
    archive=decode_archive(bundle); target.mkdir(parents=True,exist_ok=True)
    files=[]; cursor=0
    for entry in bundle["source_files"]:
        size=int(entry["byte_size"]); data=archive[cursor:cursor+size]; cursor+=size
        path=target/entry["path"]; path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(data)
        files.append({"path":entry["path"],"sha256":entry["sha256"],"git_blob_sha":entry["git_blob_sha"]})
    marker={"verified":True,"repository":SOURCE_REPOSITORY,"playbook_commit":playbook_commit,
            "bundle_contract":CONTRACT,"archive_sha256":bundle["archive"]["sha256"],
            "dependency":bundle["dependency"],"scope":bundle["scope"],"files":files}
    marker_path=target/"core_bundle_verification.json"
    marker_path.write_text(json.dumps(marker,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    reread=json.loads(marker_path.read_text(encoding="utf-8"))
    if reread!=marker: raise RuntimeError("marker read-back mismatch")
    return marker

def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    args=p.parse_args()
    built=build_bundle(); rendered=render(built)
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8")!=rendered:
            raise SystemExit("Astrology deterministic core bundle is stale; rebuild it")
        errors=verify_bundle(built)
        if errors: raise SystemExit("; ".join(errors))
        print("Astrology deterministic core bundle verified")
        return 0
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(rendered,encoding="utf-8")
    print(OUTPUT)
    return 0

if __name__=="__main__": raise SystemExit(main())
