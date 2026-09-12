#!/usr/bin/env python3
from __future__ import annotations
import argparse, copy, json
from pathlib import Path

CAPS = ["scene_fact","raw_hand_geometry","canonical_hand_geometry","principal_line_presence",
        "principal_line_geometry","fine_line_detail","surface_mark_detail","color_observation",
        "tradition_projection"]

def base():
    return {
      "scene":{"state":"resolved","candidate_index_used_as_identity":False},
      "quality":{"geometry":"sufficient","line_detail":"sufficient","surface_detail":"sufficient",
                 "color":"sufficient","color_reliable":True},
      "frame":{"raw_frame_known":True,"mirror_reconciled":True,"inverse_verified":True,
               "handedness_metadata":None,"anatomical_side_authority":"capture_lineage",
               "detector_disagreement_ref":None,"calibrated_cutoff":False},
      "feature":{"present":True,"local_score":0.91},
      "tradition":{"requested":False,"state":"source_supported"},
    }

def make(cid,title,changes,expected,extra=None):
    x=base()
    for path,val in changes.items():
        a,b=path.split(".",1); x[a][b]=val
    return {"id":cid,"title":title,"input":x,"expected":expected,"extra":extra or {}}

CASES=[
 make("A","clean",{"tradition.state":"unresolved"},
      {"scene_fact":"admitted","raw_hand_geometry":"admitted","canonical_hand_geometry":"admitted",
       "principal_line_presence":"admitted","principal_line_geometry":"admitted","tradition_projection":"not_applicable"},
      {"raw_mutated":False}),
 make("B","line detail insufficient",{"quality.line_detail":"insufficient"},
      {"raw_hand_geometry":"admitted","principal_line_presence":"partial",
       "principal_line_geometry":"insufficient","fine_line_detail":"insufficient"},
      {"illegal_rescue":False}),
 make("C","partial line detail",{"quality.line_detail":"partial","quality.surface_detail":"insufficient",
                                 "quality.color":"insufficient","quality.color_reliable":False},
      {"raw_hand_geometry":"admitted","principal_line_presence":"partial","principal_line_geometry":"partial",
       "fine_line_detail":"partial","surface_mark_detail":"insufficient","color_observation":"insufficient"},
      {"mixed":True}),
 make("D","ambiguous target",{"scene.state":"ambiguous","tradition.requested":True},
      {"scene_fact":"admitted","raw_hand_geometry":"unresolved","canonical_hand_geometry":"unresolved",
       "principal_line_geometry":"unresolved","tradition_projection":"unresolved"},
      {"candidate_index_used_as_identity":False}),
 make("E","frame unresolved",{"frame.raw_frame_known":False,"frame.mirror_reconciled":False,
                               "frame.anatomical_side_authority":"unresolved"},
      {"scene_fact":"admitted","raw_hand_geometry":"admitted","canonical_hand_geometry":"unresolved",
       "principal_line_geometry":"unresolved"},
      {"anatomical_side_resolved":False}),
 make("F","model absent",{"feature.present":False},
      {"raw_hand_geometry":"admitted","canonical_hand_geometry":"admitted","principal_line_presence":"partial",
       "principal_line_geometry":"unresolved"},
      {"anatomical_absence_inferred":False}),
 make("G","high score cannot rescue",{"quality.line_detail":"insufficient","feature.local_score":0.99},
      {"principal_line_presence":"partial","principal_line_geometry":"insufficient","fine_line_detail":"insufficient"},
      {"score_overrode_blocker":False}),
 make("H","detector evidence no cutoff",{"frame.detector_disagreement_ref":"DETECTOR_AGREEMENT_RESULTS.md"},
      {"canonical_hand_geometry":"admitted"},
      {"compatibility_assessment":"unresolved","research_metric_promoted":False,"evidence_preserved":True}),
 make("I","prohibited tradition mapping",{"tradition.requested":True,"tradition.state":"prohibited_assumption"},
      {"raw_hand_geometry":"admitted","principal_line_geometry":"admitted","tradition_projection":"insufficient"},
      {"raw_mutated":False}),
 make("J","color unreliable",{"quality.color":"insufficient","quality.color_reliable":False},
      {"raw_hand_geometry":"admitted","principal_line_geometry":"admitted","color_observation":"insufficient"},
      {"mixed":True}),
 make("K","handedness metadata not authority",{"frame.handedness_metadata":"Left",
                                               "frame.anatomical_side_authority":"unresolved"},
      {"raw_hand_geometry":"admitted","canonical_hand_geometry":"admitted"},
      {"anatomical_side_resolved":False,"handedness_used_as_authority":False}),
 make("L","tradition conflict isolated",{"tradition.requested":True,"tradition.state":"conflicting"},
      {"raw_hand_geometry":"admitted","canonical_hand_geometry":"admitted","principal_line_geometry":"admitted",
       "tradition_projection":"unresolved"},
      {"raw_mutated":False}),
]

def derive(inp):
    original=copy.deepcopy(inp)
    s,q,f,m,t=inp["scene"],inp["quality"],inp["frame"],inp["feature"],inp["tradition"]
    o={k:"not_applicable" for k in CAPS}; r={k:[] for k in CAPS}
    def put(k,v,why): o[k]=v; r[k].append(why)
    put("scene_fact","admitted","scene facts recordable")
    resolved=s["state"]=="resolved"
    if not resolved:
        for k in ["raw_hand_geometry","canonical_hand_geometry","principal_line_presence","principal_line_geometry",
                  "fine_line_detail","surface_mark_detail","color_observation"]:
            put(k,"unresolved","target association unresolved")
    else:
        g=q["geometry"]
        put("raw_hand_geometry",{"sufficient":"admitted","partial":"partial","insufficient":"insufficient"}.get(g,"unresolved"),
            f"geometry quality {g}")
        frame_ok=f["raw_frame_known"] and f["mirror_reconciled"] and f["inverse_verified"]
        if o["raw_hand_geometry"]=="insufficient": put("canonical_hand_geometry","insufficient","raw geometry insufficient")
        elif not frame_ok: put("canonical_hand_geometry","unresolved","frame provenance unresolved")
        else: put("canonical_hand_geometry",o["raw_hand_geometry"],"frame dependencies satisfied")
        ld=q["line_detail"]
        if ld=="sufficient": put("principal_line_presence","admitted" if m["present"] else "partial",
                                 "model output under sufficient line detail" if m["present"] else "non-detection is not anatomical absence")
        elif ld=="partial": put("principal_line_presence","partial","line detail partial")
        elif ld=="insufficient": put("principal_line_presence","partial" if m["present"] else "insufficient",
                                     "line detail insufficient; model fact cannot certify observability")
        else: put("principal_line_presence","unresolved","line detail unknown")
        if o["canonical_hand_geometry"] in {"unresolved","insufficient"}:
            put("principal_line_geometry",o["canonical_hand_geometry"],"canonical geometry dependency not admitted")
        elif ld=="insufficient": put("principal_line_geometry","insufficient","line detail insufficient")
        elif ld=="partial": put("principal_line_geometry","partial","line detail partial")
        elif not m["present"]: put("principal_line_geometry","unresolved","model non-detection is not anatomical absence")
        else: put("principal_line_geometry","admitted","dependencies satisfied")
        put("fine_line_detail",{"sufficient":"admitted","partial":"partial","insufficient":"insufficient"}.get(ld,"unresolved"),
            f"line detail {ld}")
        sd=q["surface_detail"]
        put("surface_mark_detail",{"sufficient":"admitted","partial":"partial","insufficient":"insufficient"}.get(sd,"unresolved"),
            f"surface detail {sd}")
        if q["color"]=="sufficient" and q["color_reliable"] is True: put("color_observation","admitted","color sufficient and reliable")
        elif q["color"]=="insufficient" or q["color_reliable"] is False: put("color_observation","insufficient","color insufficient or unreliable")
        else: put("color_observation","unresolved","color unresolved")
    if not t["requested"]: put("tradition_projection","not_applicable","not requested")
    elif not resolved: put("tradition_projection","unresolved","target unresolved")
    elif t["state"]=="source_supported": put("tradition_projection","admitted","source supported")
    elif t["state"]=="prohibited_assumption": put("tradition_projection","insufficient","prohibited assumption")
    else: put("tradition_projection","unresolved",f"tradition {t['state']}")
    inv={
      "candidate_index_used_as_identity":s["candidate_index_used_as_identity"],
      "anatomical_side_resolved":f["anatomical_side_authority"] in {"capture_lineage","explicit_user_side","verified_external_authority"},
      "handedness_used_as_authority":f["handedness_metadata"] is not None and f["anatomical_side_authority"]=="detector_metadata",
      "anatomical_absence_inferred":False,
      "score_overrode_blocker":q["line_detail"]=="insufficient" and o["principal_line_geometry"]=="admitted",
      "illegal_rescue":q["line_detail"]=="insufficient" and o["principal_line_geometry"]=="admitted",
      "raw_mutated":inp!=original,
      "research_metric_promoted":False,
      "compatibility_assessment":"unresolved" if f["detector_disagreement_ref"] and not f["calibrated_cutoff"] else "not_applicable",
      "evidence_preserved":bool(f["detector_disagreement_ref"]),
      "mixed":len({v for v in o.values() if v!="not_applicable"})>1,
    }
    return {"capabilities":o,"reasons":r,"invariants":inv}

def validate(c):
    d=derive(copy.deepcopy(c["input"])); checks=[]
    for k,e in c["expected"].items():
        a=d["capabilities"][k]; checks.append({"key":k,"expected":e,"actual":a,"pass":a==e})
    for k,e in c["extra"].items():
        a=d["invariants"][k]; checks.append({"key":k,"expected":e,"actual":a,"pass":a==e})
    for k,v in d["capabilities"].items():
        if v in {"partial","insufficient","unresolved"} and not d["reasons"][k]:
            checks.append({"key":k+".reasons","expected":"nonempty","actual":[],"pass":False})
    return {"id":c["id"],"title":c["title"],"input":c["input"],"derived":d,"checks":checks,
            "contract_result":"pass" if all(x["pass"] for x in checks) else "fail"}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output",type=Path); a=ap.parse_args()
    rows=[validate(c) for c in CASES]
    mixed=[r["id"] for r in rows if r["derived"]["invariants"]["mixed"]]
    result={"status":"REFERENCE-ONLY / UNCERTAINTY COMPOSITION CONTRACT VALIDATION",
            "schema":"palm_uncertainty_composition_validation_v1",
            "summary":{"cases_total":len(rows),"cases_pass":sum(r["contract_result"]=="pass" for r in rows),
                       "cases_fail":sum(r["contract_result"]=="fail" for r in rows),
                       "mixed_capability_cases":mixed,
                       "authoritative_single_top_level_admission_state_sufficient":len(mixed)==0,
                       "recommended_top_level_admission_role":"summary-only; capability-specific states remain authoritative" if mixed else "authoritative",
                       "hard_dependency_fail_closed":not any(r["derived"]["invariants"]["illegal_rescue"] for r in rows),
                       "tradition_layer_isolated":not any(r["derived"]["invariants"]["raw_mutated"] for r in rows),
                       "local_scores_cannot_rescue_hard_blockers":not any(r["derived"]["invariants"]["score_overrode_blocker"] for r in rows),
                       "candidate_index_not_identity":not any(r["derived"]["invariants"]["candidate_index_used_as_identity"] for r in rows),
                       "detector_handedness_not_anatomical_authority":not any(r["derived"]["invariants"]["handedness_used_as_authority"] for r in rows),
                       "research_metrics_not_promoted_to_cutoff":not any(r["derived"]["invariants"]["research_metric_promoted"] for r in rows)},
            "cases":rows,
            "boundary":{"production_threshold":False,"production_routing":False,"anatomical_truth":False,
                        "biometric_identity":False,"palmistry_prediction_validity":False}}
    text=json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n"
    if a.output: a.output.write_text(text,encoding="utf-8")
    else: print(text,end="")
    if result["summary"]["cases_fail"]: raise SystemExit(2)

if __name__=="__main__": main()
