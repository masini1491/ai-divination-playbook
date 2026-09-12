#!/usr/bin/env python3
"""REFERENCE-ONLY V2 amendment for Palm Observation uncertainty composition validation.

V2 preserves the frozen V1 lower-layer rules and corrects the predeclared
tradition-dependency semantics for Cases A and J after the documented V1
post-freeze discrepancy.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import observation_uncertainty_composition_validator as v1

CASES = copy.deepcopy(v1.CASES)

def get_case(cid):
    for c in CASES:
        if c["id"] == cid:
            return c
    raise KeyError(cid)

a = get_case("A")
a["input"]["tradition"] = {
    "requested": True,
    "state": "unresolved",
    "required_capability": "principal_line_geometry",
}
a["expected"]["tradition_projection"] = "unresolved"

j = get_case("J")
j["input"]["tradition"] = {
    "requested": True,
    "state": "source_supported",
    "required_capability": "color_observation",
}
j["expected"]["tradition_projection"] = "insufficient"
j["extra"]["raw_mutated"] = False

def derive(inp):
    d = v1.derive(copy.deepcopy(inp))
    out = d["capabilities"]
    reasons = d["reasons"]
    t = inp["tradition"]
    resolved = inp["scene"]["state"] == "resolved"

    reasons["tradition_projection"] = []

    def put(state, reason):
        out["tradition_projection"] = state
        reasons["tradition_projection"].append(reason)

    if not t["requested"]:
        put("not_applicable", "not requested")
    elif not resolved:
        put("unresolved", "target unresolved")
    elif t["state"] == "prohibited_assumption":
        put("insufficient", "prohibited assumption")
    elif t["state"] in {"unresolved", "conflicting"}:
        put("unresolved", f"tradition {t['state']}")
    elif t["state"] == "source_supported":
        req = t.get("required_capability")
        dep = out.get(req) if req else "admitted"
        if dep == "insufficient":
            put("insufficient", f"required capability {req} insufficient")
        elif dep == "unresolved":
            put("unresolved", f"required capability {req} unresolved")
        elif dep == "partial":
            put("partial", f"required capability {req} partial")
        else:
            put("admitted", "source supported and required capability admitted")
    else:
        put("unresolved", "tradition state unknown")

    d["invariants"]["mixed"] = len({
        value for value in out.values() if value != "not_applicable"
    }) > 1
    return d

def validate(c):
    d = derive(copy.deepcopy(c["input"]))
    checks = []
    for key, expected in c["expected"].items():
        actual = d["capabilities"][key]
        checks.append({
            "key": key,
            "expected": expected,
            "actual": actual,
            "pass": actual == expected,
        })
    for key, expected in c["extra"].items():
        actual = d["invariants"][key]
        checks.append({
            "key": key,
            "expected": expected,
            "actual": actual,
            "pass": actual == expected,
        })
    for key, state in d["capabilities"].items():
        if state in {"partial", "insufficient", "unresolved"} and not d["reasons"][key]:
            checks.append({
                "key": key + ".reasons",
                "expected": "nonempty",
                "actual": [],
                "pass": False,
            })
    return {
        "id": c["id"],
        "title": c["title"],
        "input": c["input"],
        "derived": d,
        "checks": checks,
        "contract_result": "pass" if all(x["pass"] for x in checks) else "fail",
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()

    rows = [validate(c) for c in CASES]
    mixed = [r["id"] for r in rows if r["derived"]["invariants"]["mixed"]]

    result = {
        "status": "REFERENCE-ONLY / UNCERTAINTY COMPOSITION CONTRACT VALIDATION V2",
        "schema": "palm_uncertainty_composition_validation_v2",
        "amendment": {
            "supersedes_for_plan_closure": "V1 formal validation artifact",
            "v1_discrepancy": "Cases A and J did not exercise intended tradition dependencies",
            "v1_lower_layer_rules_reused": True,
        },
        "summary": {
            "cases_total": len(rows),
            "cases_pass": sum(r["contract_result"] == "pass" for r in rows),
            "cases_fail": sum(r["contract_result"] == "fail" for r in rows),
            "mixed_capability_cases": mixed,
            "authoritative_single_top_level_admission_state_sufficient": len(mixed) == 0,
            "recommended_top_level_admission_role": (
                "summary-only; capability-specific states remain authoritative"
                if mixed else "authoritative"
            ),
            "hard_dependency_fail_closed": not any(
                r["derived"]["invariants"]["illegal_rescue"] for r in rows
            ),
            "tradition_layer_isolated": not any(
                r["derived"]["invariants"]["raw_mutated"] for r in rows
            ),
            "local_scores_cannot_rescue_hard_blockers": not any(
                r["derived"]["invariants"]["score_overrode_blocker"] for r in rows
            ),
            "candidate_index_not_identity": not any(
                r["derived"]["invariants"]["candidate_index_used_as_identity"] for r in rows
            ),
            "detector_handedness_not_anatomical_authority": not any(
                r["derived"]["invariants"]["handedness_used_as_authority"] for r in rows
            ),
            "research_metrics_not_promoted_to_cutoff": not any(
                r["derived"]["invariants"]["research_metric_promoted"] for r in rows
            ),
        },
        "cases": rows,
        "boundary": v1.base()["tradition"] and {
            "production_threshold": False,
            "production_routing": False,
            "anatomical_truth": False,
            "biometric_identity": False,
            "palmistry_prediction_validity": False,
        },
    }

    text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")

    if result["summary"]["cases_fail"]:
        raise SystemExit(2)

if __name__ == "__main__":
    main()
