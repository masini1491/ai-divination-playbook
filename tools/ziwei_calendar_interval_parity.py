#!/usr/bin/env python3
"""Full candidate-window parity and size verifier for interval calendar POC."""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
import time
from datetime import date, timedelta
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from tools.ziwei_calendar_interval_poc import GregorianBirth, normalize_from_interval_data, write_year_shard
from tools.ziwei_calendar_lunar_python_reference import GregorianBirthInput, normalize_gregorian_birth

def comparable_current(result):
    return {
        "raw_lunar_conversion":result["raw_lunar_conversion"],
        "policy_lunar_conversion":result["policy_lunar_conversion"],
        "normalized_natal_input":{
            "lunar_year":result["normalized_natal_input"]["lunar_year"],
            "lunar_month":result["normalized_natal_input"]["lunar_month"],
            "lunar_day":result["normalized_natal_input"]["lunar_day"],
            "hour_branch":result["normalized_natal_input"]["hour_branch"],
            "leap_month_identity":result["normalized_natal_input"]["leap_month_identity"],
        },
    }

def dates(start,end):
    d=start
    while d<=end:
        yield d
        d+=timedelta(days=1)

def compare(root,d,hour):
    got=normalize_from_interval_data(GregorianBirth(d.year,d.month,d.day,hour),root)
    cur=normalize_gregorian_birth(GregorianBirthInput(d.year,d.month,d.day,hour))
    exp=comparable_current(cur)
    return None if got==exp else {"date":d.isoformat(),"hour":hour,"expected":exp,"got":got}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--start",default="1900-01-01")
    ap.add_argument("--end",default="2100-12-31")
    ap.add_argument("--max-mismatches",type=int,default=20)
    args=ap.parse_args()
    start=date.fromisoformat(args.start); end=date.fromisoformat(args.end)
    if end<start: raise SystemExit("end before start")

    t0=time.monotonic()
    mismatches=[]
    ordinary=boundary23=fullhour=0
    with tempfile.TemporaryDirectory() as td:
        root=Path(td)
        for y in range(start.year,end.year+2):
            write_year_shard(root,y)

        for d in dates(start,end):
            detail=compare(root,d,12); ordinary+=1
            if detail and len(mismatches)<args.max_mismatches: mismatches.append(detail)

            nxt=d+timedelta(days=1)
            is_year_edge=nxt.year!=d.year
            if is_year_edge or d in (start,end):
                detail=compare(root,d,23); boundary23+=1
                if detail and len(mismatches)<args.max_mismatches: mismatches.append(detail)

            if d.month==1 and d.day==1:
                for hour in range(24):
                    detail=compare(root,d,hour); fullhour+=1
                    if detail and len(mismatches)<args.max_mismatches: mismatches.append(detail)

        paths=sorted((root/"years").glob("*.json"))
        sizes=[p.stat().st_size for p in paths]
        interval_counts=[len(json.loads(p.read_text(encoding="utf-8"))["intervals"]) for p in paths]

    report={
        "schema_name":"ziwei_calendar_interval_parity_report",
        "schema_version":"0.1.0",
        "status":"PASS" if not mismatches else "FAIL",
        "research_only":True,
        "production_admission_changed":False,
        "candidate_window":{"start":start.isoformat(),"end":end.isoformat()},
        "coverage":{
            "every_gregorian_date_at_12":ordinary,
            "year_edge_23_cases":boundary23,
            "full_24_hour_new_year_cases":fullhour,
        },
        "mismatch_count_observed":len(mismatches),
        "mismatch_samples":mismatches,
        "generated_year_shards":len(sizes),
        "interval_records":{
            "min_per_shard":min(interval_counts),
            "max_per_shard":max(interval_counts),
            "mean_per_shard":sum(interval_counts)/len(interval_counts),
            "total":sum(interval_counts),
        },
        "shard_size_bytes":{
            "min":min(sizes),"max":max(sizes),"mean":sum(sizes)/len(sizes),"total":sum(sizes)
        },
        "one_query_max_files":2,
        "elapsed_seconds":time.monotonic()-t0,
    }
    print(json.dumps(report,ensure_ascii=False,sort_keys=True))
    return 0 if report["status"]=="PASS" else 1

if __name__=="__main__":
    raise SystemExit(main())
