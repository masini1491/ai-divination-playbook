from __future__ import annotations
import argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/"indexes/ziwei/star_palace_coverage_v1.json"
REGISTRY=ROOT/"references/ziwei/ziwei_interpretation_claim_registry_star_palace_context_v1.json"
DECISIONS=ROOT/"references/ziwei/STAR_PALACE_COVERAGE_DECISIONS_V1.json"
STARS=["紫微","天機","太陽","武曲","天同","廉貞","天府","太陰","貪狼","巨門","天相","天梁","七殺","破軍"]
PALACES=["命宮","兄弟宮","夫妻宮","子女宮","財帛宮","疾厄宮","遷移宮","奴僕宮","官祿宮","田宅宮","福德宮","父母宮"]
def load(path): return json.loads(path.read_text(encoding="utf-8"))
def build():
    reg=load(REGISTRY); ds=load(DECISIONS)
    dedicated={(c["star"],c["palace"]):c["claim_id"] for c in reg["claims"]}
    nonprod={(d["star"],d["palace"]):d for d in ds["decisions"]}
    overlap=set(dedicated)&set(nonprod)
    if overlap: raise SystemExit(f"coverage decision duplicates production cell(s): {sorted(overlap)}")
    cells=[]
    for star in STARS:
        for palace in PALACES:
            key=(star,palace)
            cell={"cell_key":f"{star}×{palace}","star":star,"palace":palace,"review_status":"UNREVIEWED","routing_mode":"UNREVIEWED","resolved":False}
            if key in dedicated:
                cell.update({"review_status":"REVIEWED","routing_mode":"DEDICATED_L4","resolved":True,"claim_ref":dedicated[key],"research_state":"PRODUCTION-ADMITTED"})
            elif key in nonprod:
                d=nonprod[key]
                cell.update({"review_status":"REVIEWED","routing_mode":d["routing_mode"],"resolved":bool(d["resolved"]),"research_ref":d["research_ref"],"research_state":d["research_state"]})
            cells.append(cell)
    if len(cells)!=168 or len({c["cell_key"] for c in cells})!=168: raise SystemExit("coverage grid must contain exactly 168 unique cells")
    metrics={"reviewed_cells":sum(c["review_status"]=="REVIEWED" for c in cells),"resolved_cells":sum(c["resolved"] for c in cells),"unreviewed_cells":sum(c["review_status"]=="UNREVIEWED" for c in cells),"dedicated_l4":sum(c["routing_mode"]=="DEDICATED_L4" for c in cells),"bounded_l5_composition":sum(c["routing_mode"]=="BOUNDED_L5_COMPOSITION" for c in cells),"conditional_only":sum(c["routing_mode"]=="CONDITIONAL_ONLY" for c in cells),"high_risk_bounded":sum(c["routing_mode"]=="HIGH_RISK_BOUNDED" for c in cells),"deferred_evidence":sum(c["routing_mode"]=="DEFERRED_EVIDENCE" for c in cells)}
    if metrics["reviewed_cells"]+metrics["unreviewed_cells"]!=168: raise SystemExit("reviewed + unreviewed must equal 168")
    if metrics["resolved_cells"]>metrics["reviewed_cells"]: raise SystemExit("resolved must not exceed reviewed")
    if metrics["dedicated_l4"]!=len(dedicated): raise SystemExit("dedicated L4 count mismatch")
    return {"schema_version":1,"authority":"routing_coverage_index_only","generated_by":"tools/build_ziwei_star_palace_coverage.py","source_registry":"references/ziwei/ziwei_interpretation_claim_registry_star_palace_context_v1.json","decision_input":"references/ziwei/STAR_PALACE_COVERAGE_DECISIONS_V1.json","total_cells":168,"metrics":metrics,"cells":cells}
def render(obj): return json.dumps(obj,ensure_ascii=False,separators=(",",":"))+"\n"
def main():
    p=argparse.ArgumentParser(); p.add_argument("--check",action="store_true"); a=p.parse_args()
    out=render(build())
    if a.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8")!=out: raise SystemExit(f"{OUTPUT.relative_to(ROOT)} is stale; run generator")
        print(f"PASS {OUTPUT.relative_to(ROOT)} ({len(out.encode('utf-8'))} bytes)"); return
    OUTPUT.parent.mkdir(parents=True,exist_ok=True); OUTPUT.write_text(out,encoding="utf-8")
    print(f"WROTE {OUTPUT.relative_to(ROOT)} ({len(out.encode('utf-8'))} bytes)")
if __name__=="__main__": main()
