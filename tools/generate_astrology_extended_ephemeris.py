#!/usr/bin/env python3
"""Build-time generator contract for Astrology extended ephemeris v1.

Network use is intentionally confined to controlled build/research execution.
Ordinary production runtime must consume the committed verified dataset and
must never call Horizons. The exact production artifact was admitted by
AST-P2-040 evidence; regeneration is a maintenance operation and source drift
must be reviewed rather than silently replacing admitted bytes.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

DATASET_ID="astrology-extended-ephemeris-c1-v1"
REPRESENTATION_ID="c1-cheb-d7-w60"
SOURCE_CONTRACT={
  "provider":"NASA/JPL Horizons","center":"500@399","ephem_type":"OBSERVER",
  "quantities":[31],"apparent":"AIRLESS","time_type":"UT","extra_precision":True,
  "source_grid_days":5,
}
ADMITTED_DATASET_SHA256="460b310131149b012b615dde15fcf892b85142fd2490fa1c5f35613697b93cc3"
MANIFEST=Path(__file__).resolve().parents[1]/"data"/"astrology"/"extended_ephemeris"/"v1"/"MANIFEST.json"

def verify_admitted_manifest(path:Path=MANIFEST)->list[str]:
    errors=[]
    try: data=json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc: return [f"manifest load failed: {exc}"]
    if data.get("dataset_id")!=DATASET_ID: errors.append("dataset_id mismatch")
    if data.get("production_admission")!="PRODUCTION_ADMITTED": errors.append("production admission mismatch")
    if data.get("dataset",{}).get("sha256")!=ADMITTED_DATASET_SHA256: errors.append("dataset digest mismatch")
    if data.get("representation",{}).get("id")!=REPRESENTATION_ID: errors.append("representation mismatch")
    for key,value in SOURCE_CONTRACT.items():
        if data.get("source",{}).get(key)!=value: errors.append(f"source {key} mismatch")
    if data.get("runtime",{}).get("network_required") is not False: errors.append("runtime network must be false")
    if data.get("transport",{}).get("storage_encoding")!="base64": errors.append("storage encoding mismatch")
    return errors

def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--verify-admitted",action="store_true")
    args=p.parse_args()
    if not args.verify_admitted:
        raise SystemExit("controlled Horizons regeneration is intentionally not an ordinary CI operation; use the frozen AST-P2-040 build contract/probe workflow")
    errors=verify_admitted_manifest()
    if errors: raise SystemExit("; ".join(errors))
    print("Astrology extended ephemeris admitted manifest verified")
    return 0
if __name__=="__main__": raise SystemExit(main())
