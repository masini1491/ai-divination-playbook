#!/usr/bin/env python3
"""Generate deterministic Astrology place shards from admitted geonamescache bytes.

This is a data generator, not a production resolver or materialization admission.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from typing import Any
from astrology_place_shard_benchmark import EXPECTED_DATASETS, GEONAMESCACHE_VERSION, load_records, locate_data_dir, normalize_alias, verify_dataset

GENERATOR_ID="astrology-place-shard-generator-v1"
ALIAS_SCHEMA="astrology-place-alias-shard-v1"
CANDIDATE_SCHEMA="astrology-place-candidate-shard-v1"
ALIAS_HEX=3
CANDIDATE_HEX=3

def sha_bucket(value:str,width:int)->str:
 return hashlib.sha256(value.encode("utf-8")).hexdigest()[:width]
def alias_bucket_id(value:str)->str: return sha_bucket(value,ALIAS_HEX)
def candidate_bucket_id(gid:int)->str: return sha_bucket(str(int(gid)),CANDIDATE_HEX)
def candidate_payload(row:dict[str,Any])->list[Any]:
 return [int(row["geonameid"]),str(row["name"]),str(row["countrycode"]),str(row.get("admin1code","")),float(row["latitude"]),float(row["longitude"]),str(row["timezone"]),int(row.get("population",0))]
def route_payload(row:dict[str,Any])->list[Any]:
 return [int(row["geonameid"]),str(row["countrycode"]),int(row.get("population",0)),str(row["name"])]
def build_profile(records:dict[str,dict[str,Any]]):
 aliases={}; candidates={}
 for row in records.values():
  gid=int(row["geonameid"]); cbid=candidate_bucket_id(gid)
  candidates.setdefault(cbid,{})[str(gid)]=candidate_payload(row)
  for alias in {normalize_alias(str(a)) for a in row.get("alternatenames",[]) if str(a)}:
   aliases.setdefault(alias_bucket_id(alias),{}).setdefault(alias,[]).append(route_payload(row))
 for shard in aliases.values():
  for routes in shard.values(): routes.sort(key=lambda r:(-int(r[2]),str(r[1]),str(r[3]),int(r[0])))
 return aliases,candidates
def render(kind:str,profile:int,bid:str,payload:dict)->bytes:
 obj={"schema":ALIAS_SCHEMA if kind=="aliases" else CANDIDATE_SCHEMA,"profile":profile,"bucket":bid,kind:payload}
 return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")
def shard_path(root:Path,profile:int,kind:str,bid:str)->Path:
 return root/"profiles"/str(profile)/kind/bid[0]/f"{bid[1:]}.json"
def aggregate_digest(parts):
 h=hashlib.sha256()
 for path,payload in sorted(parts,key=lambda x:x[0]):
  h.update(path.encode()); h.update(b"\0"); h.update(hashlib.sha256(payload).digest())
 return h.hexdigest()
def generate(output:Path,profiles:list[int],write:bool)->dict:
 data_dir,version=locate_data_dir()
 if version!=GEONAMESCACHE_VERSION: raise RuntimeError(f"geonamescache version mismatch: {version}")
 summary=[]
 for profile in profiles:
  identity=verify_dataset(data_dir/f"cities{profile}.json",profile)
  if not identity["identity_match"]: raise RuntimeError(f"source identity mismatch: {profile}")
  aliases,candidates=build_profile(load_records(data_dir/f"cities{profile}.json")); parts=[]
  for kind,shards in (("aliases",aliases),("candidates",candidates)):
   for bid,payload in shards.items():
    blob=render(kind,profile,bid,payload); rel=shard_path(Path("."),profile,kind,bid).as_posix().lstrip("./"); parts.append((rel,blob))
    if write:
     path=shard_path(output,profile,kind,bid); path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(blob)
  summary.append({"profile":profile,"source_identity":identity,"alias_nonempty_shards":len(aliases),"candidate_nonempty_shards":len(candidates),"aggregate_digest":aggregate_digest(parts),"generated_bytes":sum(len(p) for _,p in parts)})
 return {"generator_id":GENERATOR_ID,"format":"alias-3hex+candidate-3hex","profiles":summary}
def main():
 p=argparse.ArgumentParser(); p.add_argument("--output",type=Path,default=Path("data/astrology/place/v1")); p.add_argument("--profiles",type=int,nargs="+",default=sorted(EXPECTED_DATASETS),choices=sorted(EXPECTED_DATASETS)); p.add_argument("--write",action="store_true"); a=p.parse_args()
 print(json.dumps(generate(a.output,a.profiles,a.write),ensure_ascii=False,indent=2,sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())
