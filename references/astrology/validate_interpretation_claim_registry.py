#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import Any

SOURCE_ROLES={"PRIMARY_TEXT","SCHOLARLY_SECONDARY","PRACTITIONER_REFERENCE","REFERENCE_IMPLEMENTATION","UNVERIFIED_WEB_SOURCE","PROJECT_SYNTHESIS"}
ADMISSION={"REJECTED","REFERENCE_ONLY","CLAIM_ELIGIBLE","POLICY_PROVENANCE_ELIGIBLE","CORPUS_STORAGE_ELIGIBLE","PRODUCTION_ADMITTED"}
STORAGE={"metadata_only","metadata_plus_locator","normalized_paraphrase","short_excerpt_with_citation","licensed_module_copy","public_domain_text_copy","project_authored_synthesis","metadata_locator_normalized_paraphrase","metadata_revision_normalized_paraphrase"}
INDEPENDENCE={"independent_evidence","likely_derivative","explicit_derivative","shared_upstream","unknown","primary_witness","secondary_analysis_of_multiple_primary_sources","derivative_practitioner_synthesis"}
LAYERS={"L3","L4"}
CONFIDENCE={"supported","qualified","provisional","conflicted","unsupported"}
SUPPORT={"single_source_supported","multi_source_supported","tradition_bounded","qualified","conflicted","historical_only","architecture_only","unsupported"}

def add(e,c,p,m): e.append({"code":c,"path":p,"message":m})
def aset(v):
    if isinstance(v,str): return {v}
    if isinstance(v,list) and all(isinstance(x,str) for x in v): return set(v)
    return set()
def arr(v,p,e,nonempty=False):
    if not isinstance(v,list): add(e,"ARRAY_REQUIRED",p,"must be an array"); return []
    if nonempty and not v: add(e,"NONEMPTY_ARRAY_REQUIRED",p,"must not be empty")
    return v

def validate_registry(data: Any):
    e=[]
    if not isinstance(data,dict): add(e,"ROOT_OBJECT_REQUIRED","$","registry must be an object"); return e
    for k in ("record_status","record_kind","record_id","sources","claims"):
        if k not in data: add(e,"REQUIRED_FIELD_MISSING",f"$.{k}","required field is missing")
    if data.get("record_status")!="REFERENCE-ONLY": add(e,"RECORD_STATUS_INVALID","$.record_status","research registry must be REFERENCE-ONLY")
    if data.get("record_kind")!="interpretation_claim_family_registry": add(e,"RECORD_KIND_INVALID","$.record_kind","must equal interpretation_claim_family_registry")
    if data.get("production_routable") is True: add(e,"PRODUCTION_ROUTABLE_FORBIDDEN","$.production_routable","research registry cannot be production-routable")
    rr=data.get("research_result")
    if isinstance(rr,dict):
        if rr.get("production_authority_granted") is True: add(e,"PRODUCTION_AUTHORITY_FORBIDDEN","$.research_result.production_authority_granted","research registry cannot grant production authority")
        if rr.get("scientific_predictive_validity_claimed") is True: add(e,"SCIENTIFIC_VALIDITY_PROMOTION_FORBIDDEN","$.research_result.scientific_predictive_validity_claimed","claim registry cannot promote scientific predictive validity")
    privacy=data.get("privacy")
    if isinstance(privacy,dict) and privacy.get("contains_real_birth_data") is True: add(e,"REAL_BIRTH_DATA_FORBIDDEN","$.privacy.contains_real_birth_data","source-evidence registry fixtures must not contain real birth data")

    sources=arr(data.get("sources"),"$.sources",e,True)
    claims=arr(data.get("claims"),"$.claims",e,True)
    conflicts=arr(data.get("conflict_groups",[]),"$.conflict_groups",e)
    source_by_id={}
    for i,s in enumerate(sources):
        p=f"$.sources[{i}]"
        if not isinstance(s,dict): add(e,"SOURCE_OBJECT_REQUIRED",p,"source entry must be an object"); continue
        sid=s.get("source_id")
        if not isinstance(sid,str) or not sid: add(e,"SOURCE_ID_REQUIRED",p+".source_id","non-empty source_id is required"); continue
        if sid in source_by_id: add(e,"SOURCE_ID_DUPLICATE",p+".source_id","source_id must be unique")
        source_by_id[sid]=s
        roles=aset(s.get("source_role"))
        if not roles: add(e,"SOURCE_ROLE_REQUIRED",p+".source_role","source_role must be string or string array")
        for x in roles-SOURCE_ROLES: add(e,"SOURCE_ROLE_INVALID",p+".source_role",f"unsupported source role: {x}")
        adm=aset(s.get("admission_status",s.get("admission_state")))
        if not adm: add(e,"ADMISSION_STATUS_REQUIRED",p,"admission_state or admission_status is required")
        for x in adm-ADMISSION: add(e,"ADMISSION_STATUS_INVALID",p,f"unsupported admission status: {x}")
        if "PRODUCTION_ADMITTED" in adm: add(e,"PRODUCTION_ADMISSION_FORBIDDEN",p,"research validator forbids PRODUCTION_ADMITTED")
        if "UNVERIFIED_WEB_SOURCE" in roles and adm & {"CLAIM_ELIGIBLE","POLICY_PROVENANCE_ELIGIBLE","PRODUCTION_ADMITTED"}:
            add(e,"UNVERIFIED_WEB_PROMOTION_FORBIDDEN",p,"unverified web source cannot be claim/policy/production admitted")
        storage=aset(s.get("storage_mode"))
        if not storage: add(e,"STORAGE_MODE_REQUIRED",p+".storage_mode","storage_mode must be declared")
        for x in storage-STORAGE: add(e,"STORAGE_MODE_INVALID",p+".storage_mode",f"unsupported storage mode: {x}")
        indep=s.get("independence_status")
        if indep is not None and indep not in INDEPENDENCE: add(e,"INDEPENDENCE_STATUS_INVALID",p+".independence_status",f"unsupported independence status: {indep}")

    for i,s in enumerate(sources):
        if not isinstance(s,dict) or not isinstance(s.get("source_id"),str): continue
        sid=s["source_id"]; refs=s.get("upstream_source_refs",[])
        if refs is None: refs=[]
        if not isinstance(refs,list) or not all(isinstance(x,str) for x in refs):
            add(e,"UPSTREAM_SOURCE_REFS_INVALID",f"$.sources[{i}].upstream_source_refs","must be string array"); continue
        for ref in refs:
            if ref==sid: add(e,"UPSTREAM_SOURCE_SELF_REFERENCE",f"$.sources[{i}].upstream_source_refs","source cannot cite itself as upstream")
            elif ref not in source_by_id: add(e,"UPSTREAM_SOURCE_REF_UNKNOWN",f"$.sources[{i}].upstream_source_refs",f"unknown upstream source: {ref}")

    conflict_by_id={}
    for i,g in enumerate(conflicts):
        p=f"$.conflict_groups[{i}]"
        if not isinstance(g,dict): add(e,"CONFLICT_OBJECT_REQUIRED",p,"conflict group must be an object"); continue
        cid=g.get("conflict_group_id")
        if not isinstance(cid,str) or not cid: add(e,"CONFLICT_ID_REQUIRED",p+".conflict_group_id","non-empty conflict_group_id is required"); continue
        if cid in conflict_by_id: add(e,"CONFLICT_ID_DUPLICATE",p+".conflict_group_id","conflict_group_id must be unique")
        conflict_by_id[cid]=g

    claim_by_id={}
    for i,c in enumerate(claims):
        p=f"$.claims[{i}]"
        if not isinstance(c,dict): add(e,"CLAIM_OBJECT_REQUIRED",p,"claim must be an object"); continue
        cid=c.get("claim_id")
        if not isinstance(cid,str) or not cid: add(e,"CLAIM_ID_REQUIRED",p+".claim_id","non-empty claim_id is required"); continue
        if cid in claim_by_id: add(e,"CLAIM_ID_DUPLICATE",p+".claim_id","claim_id must be unique")
        claim_by_id[cid]=c
        if c.get("layer") not in LAYERS: add(e,"CLAIM_LAYER_INVALID",p+".layer","claim layer must be L3 or L4")
        text=c.get("normalized_statement",c.get("statement"))
        if not isinstance(text,str) or not text.strip(): add(e,"CLAIM_STATEMENT_REQUIRED",p,"statement or normalized_statement is required")
        refs=arr(c.get("source_refs"),p+".source_refs",e,True)
        srefs=[r for r in refs if isinstance(r,str)]
        if len(srefs)!=len(refs): add(e,"CLAIM_SOURCE_REF_TYPE_INVALID",p+".source_refs","source_refs must contain strings only")
        for ref in srefs:
            if ref not in source_by_id: add(e,"CLAIM_SOURCE_REF_UNKNOWN",p+".source_refs",f"unknown source: {ref}")
        conf=c.get("confidence_status",c.get("confidence"))
        if conf is not None and conf not in CONFIDENCE: add(e,"CLAIM_CONFIDENCE_INVALID",p,f"unsupported confidence: {conf}")
        sup=c.get("support_status")
        if sup is not None and sup not in SUPPORT: add(e,"CLAIM_SUPPORT_STATUS_INVALID",p+".support_status",f"unsupported support status: {sup}")
        crefs=c.get("conflict_group_ids",c.get("conflict_group_refs",[]))
        if crefs is None: crefs=[]
        if not isinstance(crefs,list) or not all(isinstance(x,str) for x in crefs): add(e,"CLAIM_CONFLICT_REFS_INVALID",p,"conflict refs must be string array")
        else:
            for ref in crefs:
                if ref not in conflict_by_id: add(e,"CLAIM_CONFLICT_REF_UNKNOWN",p,f"unknown conflict group: {ref}")
        admissions=[]
        for ref in srefs:
            s=source_by_id.get(ref)
            if s: admissions.append(aset(s.get("admission_status",s.get("admission_state"))))
        if srefs and admissions and all("REFERENCE_ONLY" in a and len(a)==1 for a in admissions):
            if conf=="supported" or sup in {"single_source_supported","multi_source_supported"}:
                add(e,"REFERENCE_ONLY_AUTHORITY_PROMOTION",p,"REFERENCE_ONLY sources cannot by themselves support an unqualified supported claim")
        if sup=="multi_source_supported":
            if len(set(srefs))<2: add(e,"MULTI_SOURCE_COUNT_INSUFFICIENT",p+".source_refs","multi_source_supported requires >=2 distinct sources")
            roots=set()
            for ref in set(srefs):
                s=source_by_id.get(ref,{})
                ups=s.get("upstream_source_refs",[])
                if isinstance(ups,list) and ups: roots.update(x for x in ups if isinstance(x,str))
                else: roots.add(ref)
            if len(roots)<2: add(e,"MULTI_SOURCE_INDEPENDENCE_INSUFFICIENT",p+".source_refs","multi_source_supported requires >=2 evidence roots")

    for i,g in enumerate(conflicts):
        if not isinstance(g,dict): continue
        refs=g.get("claim_refs")
        if refs is None: continue
        if not isinstance(refs,list) or not all(isinstance(x,str) for x in refs): add(e,"CONFLICT_CLAIM_REFS_INVALID",f"$.conflict_groups[{i}].claim_refs","claim_refs must be string array"); continue
        for ref in refs:
            if ref not in claim_by_id: add(e,"CONFLICT_CLAIM_REF_UNKNOWN",f"$.conflict_groups[{i}].claim_refs",f"unknown claim: {ref}")
    return e

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("paths",nargs="+",type=Path)
    ap.add_argument("--json",action="store_true",dest="as_json")
    args=ap.parse_args(); out=[]; failed=False
    for path in args.paths:
        try: errors=validate_registry(json.loads(path.read_text(encoding="utf-8")))
        except (OSError,json.JSONDecodeError) as exc: errors=[{"code":"REGISTRY_LOAD_ERROR","path":"$","message":str(exc)}]
        valid=not errors; failed|=not valid; out.append({"path":str(path),"valid":valid,"errors":errors})
    if args.as_json: print(json.dumps(out,ensure_ascii=False,indent=2))
    else:
        for r in out:
            print(f"{r['path']}: {'PASS' if r['valid'] else 'FAIL'}")
            for x in r["errors"]: print(f"  {x['code']} {x['path']}: {x['message']}")
    return 1 if failed else 0

if __name__=="__main__": raise SystemExit(main())
