#!/usr/bin/env python3
"""Research-only validator for Structured Astrology Fact 0.1.0-research."""
from __future__ import annotations
import argparse, json, math
from datetime import datetime
from pathlib import Path
from typing import Any

SCHEMA="structured_astrology_fact"; VERSION="0.1.0-research"
ENUM={
"record_kind":{"chart_snapshot","event_collection","combined"},
"availability":{"available","bounded","ambiguous","unavailable","placeholder"},
"degree":{"exact","bounded","ambiguous","unavailable"},
"time":{"exact","bounded","ambiguous","unavailable"},
"layer":{"L1","L2"},
"object_type":{"luminary","planet","node","angle","cusp","asteroid","fixed_star","other"},
"motion":{"direct","retrograde","stationary","indeterminate"},
"event":{"exact_aspect","transit_to_natal","station","ingress"},
"applying":{"applying","exact","separating","indeterminate"},
"ingress":{"direct_ingress","retrograde_return_to_previous_sign","direct_reingress","other"},
"station":{"direct_to_retrograde","retrograde_to_direct","unresolved"},
"resolution":{"unique","ambiguous","nonexistent","unknown","not_applicable"},
"zodiac":{"tropical","sidereal"},
}
FORBIDDEN={"interpretation","interpretation_text","prediction","prediction_outcome","dignity","dignities","score","weighting","weightings","house_topic_meaning","transit_score"}

def add(e,c,p,m): e.append({"code":c,"path":p,"message":m})
def obj(v,p,e):
    if not isinstance(v,dict): add(e,"TYPE_OBJECT_REQUIRED",p,"must be an object"); return None
    return v
def req(o,ks,p,e):
    for k in ks:
        if k not in o: add(e,"REQUIRED_FIELD_MISSING",f"{p}.{k}","required field is missing")
def enum(v,k,p,e,code="ENUM_INVALID"):
    if v not in ENUM[k]: add(e,code,p,f"must be one of {sorted(ENUM[k])}")
def num(v): return isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(float(v))
def utc(v,p,e):
    if not isinstance(v,str) or not v.endswith("Z"): add(e,"UTC_Z_REQUIRED",p,"must be ISO-8601 UTC using Z"); return None
    try: return datetime.fromisoformat(v[:-1]+"+00:00")
    except ValueError: add(e,"UTC_PARSE_ERROR",p,"invalid UTC timestamp"); return None
def window(v,p,e):
    o=obj(v,p,e)
    if not o:return (None,None)
    req(o,["start","end"],p,e); a=utc(o.get("start"),p+".start",e) if "start" in o else None; b=utc(o.get("end"),p+".end",e) if "end" in o else None
    if a and b and a>=b:add(e,"WINDOW_ORDER_INVALID",p,"start must be earlier than end")
    return a,b
def avail(v,p,e):
    o=obj(v,p,e)
    if not o:return None
    req(o,["status"],p,e); s=o.get("status"); enum(s,"availability",p+".status",e,"AVAILABILITY_STATUS_INVALID") if s is not None else None
    return s
def degree(v,p,e):
    o=obj(v,p,e)
    if not o:return None
    req(o,["status"],p,e); s=o.get("status"); enum(s,"degree",p+".status",e,"DEGREE_STATUS_INVALID") if s is not None else None
    chk=lambda x,q: add(e,"DEGREE_RANGE_INVALID",q,"degree must be finite in [0,360)") if not(num(x) and 0<=float(x)<360) else None
    if s=="exact":
        if "exact_deg" not in o:add(e,"DEGREE_EXACT_REQUIRED",p+".exact_deg","exact status requires exact_deg")
        else:chk(o["exact_deg"],p+".exact_deg")
        if o.get("ranges_deg") or o.get("candidate_deg"):add(e,"DEGREE_EXACT_MIXED_REPRESENTATION",p,"exact value cannot carry ranges/candidates")
    elif s=="bounded":
        r=o.get("ranges_deg")
        if not isinstance(r,list) or not r:add(e,"DEGREE_BOUNDED_RANGES_REQUIRED",p+".ranges_deg","bounded status requires ranges")
        else:
            for i,x in enumerate(r):
                q=f"{p}.ranges_deg[{i}]"
                if not isinstance(x,dict) or "start_deg" not in x or "end_deg" not in x:add(e,"DEGREE_RANGE_OBJECT_INVALID",q,"range requires start_deg/end_deg")
                else:chk(x["start_deg"],q+".start_deg"); chk(x["end_deg"],q+".end_deg")
    elif s=="ambiguous":
        c=o.get("candidate_deg")
        if not isinstance(c,list) or len(c)<2:add(e,"DEGREE_AMBIGUOUS_CANDIDATES_REQUIRED",p+".candidate_deg","ambiguous status requires >=2 candidates")
        else:
            for i,x in enumerate(c):chk(x,f"{p}.candidate_deg[{i}]")
    elif s=="unavailable" and any(o.get(k) not in (None,[]) for k in ("exact_deg","ranges_deg","candidate_deg")):add(e,"DEGREE_UNAVAILABLE_VALUE_FORBIDDEN",p,"unavailable degree cannot carry a value")
    return s
def temporal(v,p,e):
    o=obj(v,p,e)
    if not o:return (None,None,None)
    req(o,["status"],p,e); s=o.get("status"); enum(s,"time",p+".status",e,"TEMPORAL_STATUS_INVALID") if s is not None else None
    a=b=None
    if s=="exact": a=utc(o.get("exact_utc"),p+".exact_utc",e) if "exact_utc" in o else None; b=a; add(e,"TEMPORAL_EXACT_REQUIRED",p+".exact_utc","exact status requires exact_utc") if "exact_utc" not in o else None
    elif s=="bounded":
        if "start_utc" not in o or "end_utc" not in o:add(e,"TEMPORAL_BOUNDS_REQUIRED",p,"bounded status requires start_utc/end_utc")
        else:a=utc(o["start_utc"],p+".start_utc",e); b=utc(o["end_utc"],p+".end_utc",e); add(e,"TEMPORAL_BOUNDS_ORDER_INVALID",p,"start_utc must be <= end_utc") if a and b and a>b else None
    elif s=="ambiguous":
        c=o.get("candidate_utc")
        if not isinstance(c,list) or len(c)<2:add(e,"TEMPORAL_AMBIGUOUS_CANDIDATES_REQUIRED",p+".candidate_utc","ambiguous status requires >=2 candidates")
        else:
            ds=[utc(x,f"{p}.candidate_utc[{i}]",e) for i,x in enumerate(c)]; ds=[x for x in ds if x]; a=min(ds) if ds else None; b=max(ds) if ds else None
            if len(c)!=len(set(c)):add(e,"TEMPORAL_AMBIGUOUS_CANDIDATES_NOT_DISTINCT",p+".candidate_utc","candidates must be distinct")
    elif s=="unavailable" and any(o.get(k) not in (None,[]) for k in ("exact_utc","start_utc","end_utc","candidate_utc")):add(e,"TEMPORAL_UNAVAILABLE_VALUE_FORBIDDEN",p,"unavailable time cannot carry a value")
    return s,a,b
def scan(v,p,e):
    if isinstance(v,dict):
        for k,x in v.items():
            q=f"{p}.{k}" if p else k
            if k in FORBIDDEN:add(e,"L3_L4_FIELD_FORBIDDEN",q,"field belongs outside L1/L2 fact core")
            scan(x,q,e)
    elif isinstance(v,list):
        for i,x in enumerate(v):scan(x,f"{p}[{i}]",e)
def meta(o,p,e):
    req(o,["fact_id","evidence_layer","availability"],p,e)
    if "evidence_layer" in o:enum(o["evidence_layer"],"layer",p+".evidence_layer",e,"EVIDENCE_LAYER_INVALID")
    if "availability" in o:avail(o["availability"],p+".availability",e)

def validate_record(r:Any):
    e=[]; root=obj(r,"$",e)
    if not root:return e
    req(root,["schema_name","schema_version","record_status","record_kind","record_id","subject_ref","provenance","configuration","facts"],"$",e)
    if root.get("schema_name")!=SCHEMA:add(e,"SCHEMA_NAME_INVALID","$.schema_name",f"must equal {SCHEMA}")
    if root.get("schema_version")!=VERSION:add(e,"SCHEMA_VERSION_UNSUPPORTED","$.schema_version",f"must equal {VERSION}")
    if root.get("record_status")!="REFERENCE-ONLY":add(e,"RECORD_STATUS_INVALID","$.record_status","research validator accepts REFERENCE-ONLY only")
    if "record_kind" in root:enum(root["record_kind"],"record_kind","$.record_kind",e,"RECORD_KIND_INVALID")
    p=obj(root.get("provenance"),"$.provenance",e) if "provenance" in root else None
    if p:
        req(p,["time","engine"],"$.provenance",e); t=obj(p.get("time"),"$.provenance.time",e) if "time" in p else None
        if t:
            req(t,["input_kind","resolution_status"],"$.provenance.time",e); s=t.get("resolution_status"); enum(s,"resolution","$.provenance.time.resolution_status",e,"TIME_RESOLUTION_INVALID") if s is not None else None
            if t.get("resolved_utc") is not None:utc(t["resolved_utc"],"$.provenance.time.resolved_utc",e)
            if "search_window_utc" in t:window(t["search_window_utc"],"$.provenance.time.search_window_utc",e)
            if t.get("input_kind")=="local_wall_time" and not t.get("iana_timezone"):add(e,"TIME_IANA_ZONE_REQUIRED","$.provenance.time.iana_timezone","local wall time requires IANA timezone")
            if s=="unique" and t.get("input_kind")=="local_wall_time" and not t.get("resolved_utc"):add(e,"TIME_UNIQUE_RESOLVED_UTC_REQUIRED","$.provenance.time.resolved_utc","unique local time requires resolved_utc")
            if s=="ambiguous":
                c=t.get("candidate_utc");
                if not isinstance(c,list) or len(c)<2:add(e,"TIME_AMBIGUOUS_CANDIDATES_REQUIRED","$.provenance.time.candidate_utc","ambiguous local time requires >=2 candidates")
                elif any(utc(x,f"$.provenance.time.candidate_utc[{i}]",e) is None for i,x in enumerate(c)):pass
                if t.get("resolved_utc") is not None:add(e,"TIME_AMBIGUOUS_RESOLUTION_FORBIDDEN","$.provenance.time.resolved_utc","ambiguous local time cannot choose one instant")
            if s=="nonexistent" and t.get("resolved_utc") is not None:add(e,"TIME_NONEXISTENT_RESOLUTION_FORBIDDEN","$.provenance.time.resolved_utc","nonexistent local time cannot resolve")
        g=obj(p.get("engine"),"$.provenance.engine",e) if "engine" in p else None
        if g:
            req(g,["engine_name","engine_version","requested_backend","effective_backend"],"$.provenance.engine",e)
            if not g.get("effective_backend"):add(e,"ENGINE_EFFECTIVE_BACKEND_REQUIRED","$.provenance.engine.effective_backend","effective backend must be recorded")
    c=obj(root.get("configuration"),"$.configuration",e) if "configuration" in root else None
    if c:
        req(c,["zodiac_system","center"],"$.configuration",e); z=c.get("zodiac_system"); enum(z,"zodiac","$.configuration.zodiac_system",e,"ZODIAC_SYSTEM_INVALID") if z is not None else None
        if z=="sidereal" and not c.get("ayanamsa"):add(e,"SIDEREAL_AYANAMSA_REQUIRED","$.configuration.ayanamsa","sidereal requires explicit ayanamsa")
    f=obj(root.get("facts"),"$.facts",e) if "facts" in root else None
    if not f:return e
    for k in ("targets","objects","houses","aspects","events"):
        if k not in f:add(e,"FACT_COLLECTION_REQUIRED",f"$.facts.{k}","required collection missing")
        elif not isinstance(f[k],list):add(e,"FACT_COLLECTION_ARRAY_REQUIRED",f"$.facts.{k}","must be an array")
    scan(f,"$.facts",e); ids=set(); targets=set(); event_ids=set(); passages=set(); tp=p.get("time",{}) if isinstance(p,dict) else {}
    for coll in ("targets","objects","houses","aspects"):
        for i,x in enumerate(f.get(coll,[]) if isinstance(f.get(coll),list) else []):
            q=f"$.facts.{coll}[{i}]"; o=obj(x,q,e)
            if not o:continue
            meta(o,q,e); fid=o.get("fact_id")
            if isinstance(fid,str):
                if fid in ids:add(e,"FACT_ID_DUPLICATE",q+".fact_id","fact_id must be unique")
                ids.add(fid); targets.add(fid) if coll=="targets" else None
            if coll=="targets": req(o,["target_type","longitude"],q,e); degree(o.get("longitude"),q+".longitude",e) if "longitude" in o else None
            elif coll=="objects":
                req(o,["object_id","object_type","longitude"],q,e); enum(o.get("object_type"),"object_type",q+".object_type",e,"OBJECT_TYPE_INVALID") if "object_type" in o else None; degree(o.get("longitude"),q+".longitude",e) if "longitude" in o else None
                if tp.get("birth_time_certainty")=="unknown" and o.get("object_type") in {"angle","cusp"} and isinstance(o.get("availability"),dict) and o["availability"].get("status") in {"available","placeholder"}:add(e,"UNKNOWN_TIME_ANGLE_AVAILABLE_FORBIDDEN",q+".availability.status","unknown birth time cannot make angle/cusp available")
            elif coll=="houses":
                req(o,["house_number","cusp_longitude"],q,e); degree(o.get("cusp_longitude"),q+".cusp_longitude",e) if "cusp_longitude" in o else None
                if tp.get("birth_time_certainty")=="unknown" and isinstance(o.get("availability"),dict) and o["availability"].get("status") in {"available","placeholder"}:add(e,"UNKNOWN_TIME_HOUSE_AVAILABLE_FORBIDDEN",q+".availability.status","unknown birth time cannot make house available")
            elif coll=="aspects":
                req(o,["left_ref","right_ref","target_angle_deg","separation_deg","signed_error_deg","absolute_error_deg","applying_state"],q,e)
                if num(o.get("signed_error_deg")) and num(o.get("absolute_error_deg")) and not math.isclose(abs(float(o["signed_error_deg"])),float(o["absolute_error_deg"]),abs_tol=1e-9):add(e,"ASPECT_ERROR_INCONSISTENT",q,"absolute_error_deg must equal abs(signed_error_deg)")
    for i,x in enumerate(f.get("events",[]) if isinstance(f.get("events"),list) else []):
        q=f"$.facts.events[{i}]"; o=obj(x,q,e)
        if not o:continue
        req(o,["event_id","event_kind","availability","time","search_window_utc"],q,e); eid=o.get("event_id")
        if isinstance(eid,str):
            if eid in event_ids:add(e,"EVENT_ID_DUPLICATE",q+".event_id","event_id must be unique")
            event_ids.add(eid)
        k=o.get("event_kind"); enum(k,"event",q+".event_kind",e,"EVENT_KIND_INVALID") if k is not None else None; avail(o.get("availability"),q+".availability",e) if "availability" in o else None
        _,a,b=temporal(o.get("time"),q+".time",e) if "time" in o else (None,None,None); wa,wb=window(o.get("search_window_utc"),q+".search_window_utc",e) if "search_window_utc" in o else (None,None)
        if a and b and wa and wb and (a<wa or b>=wb):add(e,"EVENT_TIME_OUTSIDE_SEARCH_WINDOW",q+".time","event time must lie within [start,end)")
        if k in {"transit_to_natal","exact_aspect"}:
            req(o,["moving_body_ref","target_ref","aspect_target_deg","passage_index","motion_direction"],q,e); tr=o.get("target_ref")
            if k=="transit_to_natal" and isinstance(tr,str) and tr not in targets:add(e,"EVENT_TARGET_REF_UNRESOLVED",q+".target_ref","target_ref must resolve to facts.targets.fact_id")
            pi=o.get("passage_index"); key=(k,o.get("moving_body_ref"),tr,o.get("aspect_target_deg"),pi)
            if key in passages:add(e,"PASSAGE_IDENTITY_DUPLICATE",q,"semantic passage identity duplicated")
            passages.add(key)
        elif k=="station":req(o,["body_ref","transition","speed_before_deg_per_day","speed_at_root_deg_per_day","speed_after_deg_per_day"],q,e); enum(o.get("transition"),"station",q+".transition",e,"STATION_TRANSITION_INVALID") if "transition" in o else None
        elif k=="ingress":req(o,["body_ref","zodiac_system","boundary_longitude_deg","from_sign","to_sign","motion_direction","ingress_kind"],q,e); enum(o.get("ingress_kind"),"ingress",q+".ingress_kind",e,"INGRESS_KIND_INVALID") if "ingress_kind" in o else None
    return e

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("path",type=Path); ap.add_argument("--json",action="store_true"); a=ap.parse_args()
    try:r=json.loads(a.path.read_text(encoding="utf-8"))
    except Exception as x: print(json.dumps({"valid":False,"errors":[{"code":"INPUT_READ_OR_JSON_ERROR","path":"$","message":str(x)}]},indent=2) if a.json else f"INVALID: {x}"); return 2
    e=validate_record(r); out={"valid":not e,"error_count":len(e),"errors":e}; print(json.dumps(out,indent=2) if a.json else ("VALID" if not e else "INVALID\n"+"\n".join(f"- {x['code']} {x['path']}: {x['message']}" for x in e))); return 0 if not e else 1
if __name__=="__main__": raise SystemExit(main())
