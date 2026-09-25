#!/usr/bin/env python3
"""Explicit E5 extended-aspect projection for admitted Astrology natal bundles."""
from __future__ import annotations
import argparse, json, math
from itertools import combinations
from pathlib import Path
from typing import Any
from tools.astrology_runtime import MAJOR_ASPECT_ORBS, gate_bundle

SCHEMA_NAME="astrology_aspect_projection"
SCHEMA_VERSION="1.0.0"
ASPECT_POLICY_ID="major-aspects-v1"
ORB_POLICY_ID="major-aspect-orbs-v1"
CORE=("Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Uranus","Neptune","Pluto","NorthNode")
PARTICIPANT_POLICIES={
 "aspect-participants-core-plus-angles-v1":{
   "object_ids":CORE+("Ascendant","Midheaven","Descendant","ImumCoeli"),
   "exact_birth_time_required":True,
 },
 "aspect-participants-core-plus-south-node-v1":{
   "object_ids":CORE+("SouthNode",),
   "exact_birth_time_required":False,
 },
 "aspect-participants-core-plus-fortune-v1":{
   "object_ids":CORE+("PartOfFortune",),
   "exact_birth_time_required":True,
 },
}
class AspectProjectionError(ValueError): pass

def _signed_delta(a:float,b:float)->float:
    return (b-a+180.0)%360.0-180.0

def _aspect(left:float,right:float)->tuple[str,float]|None:
    separation=abs(_signed_delta(left,right))
    targets={"conjunction":0.0,"sextile":60.0,"square":90.0,"trine":120.0,"opposition":180.0}
    name,orb=min(((name,abs(separation-target)) for name,target in targets.items()),key=lambda x:x[1])
    return (name,orb) if orb<=MAJOR_ASPECT_ORBS[name] else None

def build_aspect_projection(
    bundle:dict[str,Any], *, participant_policy_id:str, aspect_policy_id:str, orb_policy_id:str
)->dict[str,Any]:
    policy=PARTICIPANT_POLICIES.get(participant_policy_id)
    if policy is None:
        raise AspectProjectionError("explicit admitted participant policy required: "+", ".join(sorted(PARTICIPANT_POLICIES)))
    if aspect_policy_id!=ASPECT_POLICY_ID:
        raise AspectProjectionError(f"explicit admitted aspect policy required: {ASPECT_POLICY_ID}")
    if orb_policy_id!=ORB_POLICY_ID:
        raise AspectProjectionError(f"explicit admitted orb policy required: {ORB_POLICY_ID}")
    gate=gate_bundle(bundle)
    if gate.get("status")!="admitted" or bundle.get("reading_mode")!="natal":
        raise AspectProjectionError("extended aspect projection requires an admitted natal Astrology fact bundle")
    if policy["exact_birth_time_required"] and bundle.get("birth_time_certainty")!="exact":
        raise AspectProjectionError(f"{participant_policy_id} requires exact birth time")
    rows=bundle.get("facts",{}).get("objects",[])
    by_id={}
    for row in rows if isinstance(rows,list) else []:
        if not isinstance(row,dict): continue
        oid=row.get("object_id"); lon=row.get("longitude_deg"); fid=row.get("fact_id")
        if isinstance(oid,str) and not isinstance(lon,bool) and isinstance(lon,(int,float)) and math.isfinite(float(lon)) and isinstance(fid,str):
            if oid in by_id:
                raise AspectProjectionError(f"duplicate admitted participant object identity: {oid}")
            by_id[oid]=(fid,float(lon)%360.0)
    required=tuple(policy["object_ids"])
    missing=[oid for oid in required if oid not in by_id]
    if missing:
        raise AspectProjectionError("admitted participant fact(s) unavailable: "+", ".join(missing))
    aspects=[]
    for left,right in combinations(required,2):
        hit=_aspect(by_id[left][1],by_id[right][1])
        if hit is None: continue
        name,orb=hit
        aspects.append({
          "fact_id":f"projection:aspect:{participant_policy_id}:{left.lower()}:{name}:{right.lower()}",
          "projection_kind":"aspect_geometry",
          "left_object_id":left,
          "right_object_id":right,
          "left_fact_ref":by_id[left][0],
          "right_fact_ref":by_id[right][0],
          "aspect":name,
          "orb_deg":orb,
          "participant_policy_id":participant_policy_id,
          "aspect_policy_id":ASPECT_POLICY_ID,
          "orb_policy_id":ORB_POLICY_ID,
        })
    return {
      "schema_name":SCHEMA_NAME,
      "schema_version":SCHEMA_VERSION,
      "status":"projected",
      "authority":"deterministic_policy_projection_only",
      "method":"Astrology",
      "reading_mode":"natal",
      "subject_ref":bundle["subject_ref"],
      "birth_time_certainty":bundle.get("birth_time_certainty"),
      "participant_policy_id":participant_policy_id,
      "participant_object_ids":list(required),
      "aspect_policy_id":ASPECT_POLICY_ID,
      "orb_policy_id":ORB_POLICY_ID,
      "explicit_policy_required":True,
      "auto_include_new_objects":False,
      "semantic_interpretation_authority":False,
      "aspects":aspects,
    }

def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("input",type=Path)
    p.add_argument("--participant-policy-id",required=True,choices=sorted(PARTICIPANT_POLICIES))
    p.add_argument("--aspect-policy-id",required=True,choices=[ASPECT_POLICY_ID])
    p.add_argument("--orb-policy-id",required=True,choices=[ORB_POLICY_ID])
    p.add_argument("--output",type=Path)
    a=p.parse_args(); bundle=json.loads(a.input.read_text(encoding="utf-8"))
    result=build_aspect_projection(
        bundle,
        participant_policy_id=a.participant_policy_id,
        aspect_policy_id=a.aspect_policy_id,
        orb_policy_id=a.orb_policy_id,
    )
    encoded=json.dumps(result,ensure_ascii=False,indent=2)+"\n"
    if a.output:a.output.write_text(encoded,encoding="utf-8")
    else:print(encoded,end="")
    return 0
if __name__=="__main__": raise SystemExit(main())
