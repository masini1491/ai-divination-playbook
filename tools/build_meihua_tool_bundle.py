#!/usr/bin/env python3
"""Build the derived ChatGPT transport bundle for the deterministic Meihua engine."""
from __future__ import annotations
import argparse, base64, hashlib, json, sys, zlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE="tools/meihua_engine.py"
OUTPUT=ROOT/"runtime"/"meihua"/"CHATGPT_DETERMINISTIC_TOOL_BUNDLE.json"
SCHEMA_VERSION=1
AUTHORITY="derived-transport-cache-only"
CONTRACT="chunked-model-mediated-meihua-tool-bundle-v1"
CHUNK_SIZE=444
CHUNK_RETRY_LIMIT=2

def sha256(data:bytes)->str: return hashlib.sha256(data).hexdigest()
def git_blob_sha(data:bytes)->str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii")+data).hexdigest()

def build_bundle()->dict[str,object]:
    data=(ROOT/SOURCE).read_bytes()
    compressed=zlib.compress(data,9)
    encoded=base64.b64encode(compressed).decode("ascii")
    chunks=[encoded[i:i+CHUNK_SIZE] for i in range(0,len(encoded),CHUNK_SIZE)]
    return {
      "schema_version":SCHEMA_VERSION,"authority":AUTHORITY,"contract":CONTRACT,
      "source_repository":"masini1491/ai-divination-playbook",
      "source_revision_policy":"same-resolved-playbook-commit",
      "source_file":{"path":SOURCE,"byte_size":len(data),"sha256":sha256(data),"git_blob_sha":git_blob_sha(data)},
      "payload":{"compression":"zlib","encoding":"base64","decoded_size":len(data),"decoded_sha256":sha256(data),
                 "compressed_size":len(compressed),"encoded_size":len(encoded),"chunk_size":CHUNK_SIZE,
                 "chunk_count":len(chunks),"reassembly":"index-ascending-concat","chunk_retry_limit":CHUNK_RETRY_LIMIT,
                 "retry_source":"fresh-read-same-commit-bundle-failed-chunk-only"},
      "execution_contract":{"preserve_cast_fact":True,"verify_each_chunk_before_reassembly":True,
                            "verify_final_payload_before_write_or_import":True,"interpretation_authority":False},
      "chunks":[{"index":i,"encoded_length":len(c),"sha256":hashlib.sha256(c.encode("ascii")).hexdigest(),"payload":c}
                for i,c in enumerate(chunks)]
    }

def render(value:dict[str,object])->str: return json.dumps(value,ensure_ascii=False,indent=2)+"\n"

def verify(bundle:dict[str,object])->list[str]:
    errors=[]
    try:
        chunks=sorted(bundle["chunks"],key=lambda x:int(x["index"]))
        if [int(x["index"]) for x in chunks] != list(range(len(chunks))): errors.append("chunk indexes invalid")
        parts=[]
        for item in chunks:
            payload=item["payload"]
            if len(payload)!=int(item["encoded_length"]): errors.append(f"chunk {item['index']} length mismatch")
            if hashlib.sha256(payload.encode("ascii")).hexdigest()!=item["sha256"]: errors.append(f"chunk {item['index']} sha mismatch")
            parts.append(payload)
        encoded="".join(parts); meta=bundle["payload"]
        if len(encoded)!=int(meta["encoded_size"]): errors.append("encoded_size mismatch")
        decoded=zlib.decompress(base64.b64decode(encoded,validate=True))
        if len(decoded)!=int(meta["decoded_size"]): errors.append("decoded_size mismatch")
        if sha256(decoded)!=meta["decoded_sha256"]: errors.append("decoded sha mismatch")
        if decoded!=(ROOT/SOURCE).read_bytes(): errors.append("payload does not reproduce canonical source")
    except Exception as exc: errors.append(f"bundle decode error: {exc}")
    return errors

def main(argv=None)->int:
    p=argparse.ArgumentParser(); p.add_argument("--check",action="store_true"); args=p.parse_args(argv)
    expected=build_bundle(); text=render(expected)
    if args.check:
        if not OUTPUT.is_file():
            print(f"FAIL missing {OUTPUT.relative_to(ROOT)}"); return 1
        actual=json.loads(OUTPUT.read_text(encoding="utf-8")); errors=verify(actual)
        if render(actual)!=text: errors.append("committed bundle is stale")
        if errors:
            for error in errors: print(f"FAIL Meihua bundle: {error}")
            return 1
        print("Meihua deterministic tool bundle: PASS"); return 0
    OUTPUT.parent.mkdir(parents=True,exist_ok=True); OUTPUT.write_text(text,encoding="utf-8")
    errors=verify(expected)
    if errors:
        for error in errors: print(f"FAIL Meihua bundle: {error}")
        return 1
    print(f"wrote {OUTPUT.relative_to(ROOT)}"); return 0

if __name__=="__main__": raise SystemExit(main())
