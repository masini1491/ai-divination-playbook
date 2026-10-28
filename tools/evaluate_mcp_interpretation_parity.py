#!/usr/bin/env python3
"""Audit paired Repo-vs-MCP interpretation runs without judging prose similarity.

Usage:
  python tools/evaluate_mcp_interpretation_parity.py --cases evals/mcp_interpretation_parity/cases.json --records PATH
  python tools/evaluate_mcp_interpretation_parity.py --cases ... --records ... --output PATH

This does NOT invoke an LLM, draw cards, or auto-certify interpretation quality.
A record must contain two independently captured responses on the exact same
fixture and model/config, with reviewed rule IDs and source-tied evidence.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROUTES = ("repo", "mcp")
LABELS = ("PASS", "FAIL", "INCONCLUSIVE")
MAX_LEN = 20000


def load_cases(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise ValueError("unsupported cases schema")
    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("no fixtures")
    ids = [c["id"] for c in cases]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate fixture ids")
    for case in cases:
        if case.get("method") not in ("tarot", "meihua", "liuyao"):
            raise ValueError("unexpected method")
        if not case.get("contract") or not case.get("facts"):
            raise ValueError("missing fixed contract/facts")
        if not isinstance(case.get("requirements"), list) or not isinstance(case.get("forbidden"), list):
            raise ValueError("missing rubric")
        if set(case["requirements"]) & set(case["forbidden"]):
            raise ValueError("rubric collision")
    return data, {c["id"]: c for c in cases}


def _valid_evidence(response, quote):
    return isinstance(quote, str) and bool(quote.strip()) and quote in response


def evaluate(casebook: dict, records: dict) -> dict:
    cases = {c["id"]: c for c in casebook["cases"]}
    if records.get("schema_version") != 1:
        raise ValueError("unsupported records schema")
    known = records.get("cases")
    if not isinstance(known, list):
        raise ValueError("records.cases must be array")
    duplicates = [c.get("id") for c in known]
    if len(duplicates) != len(set(duplicates)):
        raise ValueError("duplicate record ids")
    if set(duplicates) - set(cases):
        raise ValueError("unknown fixture id")
    by_id = {c["id"]: c for c in known}
    report = []
    for case_id, fixture in cases.items():
        record = by_id.get(case_id)
        errors = []
        if not record:
            report.append({"id": case_id, "status": "INCONCLUSIVE",
                           "errors": ["MISSING_PAIRED_RECORD"]})
            continue
        outputs = record.get("outputs")
        if not isinstance(outputs, dict) or set(outputs) != set(ROUTES):
            errors.append("BOTH_ROUTES_REQUIRED")
            outputs = {}
        verdicts = {}
        for route in ROUTES:
            out = outputs.get(route, {})
            response = out.get("response") if isinstance(out, dict) else None
            flags = out.get("checks") if isinstance(out, dict) else None
            if not isinstance(response, str) or not response.strip() or len(response) > MAX_LEN:
                errors.append(f"{route}:RESPONSE_MISSING_OR_INVALID")
                continue
            if not isinstance(flags, dict):
                errors.append(f"{route}:CHECKS_REQUIRED")
                continue
            expected = set(fixture["requirements"]) | set(fixture["forbidden"])
            if set(flags) != expected:
                errors.append(f"{route}:INCOMPLETE_RUBRIC")
                continue
            # Every rubric point requires a human review decision with a quote
            # drawn from the actual response, not a self-asserted PASS.
            for item in expected:
                check = flags[item]
                if not isinstance(check, dict) or type(check.get("satisfied")) is not bool:
                    errors.append(f"{route}:{item}:UNREVIEWED")
                    continue
                if not _valid_evidence(response, check.get("evidence_quote")):
                    errors.append(f"{route}:{item}:EVIDENCE_NOT_IN_RESPONSE")
            verdicts[route] = out
        # Requiring matching IDs/config is necessary but not proof of LLM settings.
        for key in ("model_id", "model_config_id", "policy_source_commit", "fixture_sha256"):
            values = [outputs.get(route, {}).get(key) for route in ROUTES
                      if isinstance(outputs.get(route), dict)]
            if len(values) != 2 or not values[0] or values[0] != values[1]:
                errors.append(f"PAIRED_{key.upper()}_MISMATCH")
        expected_fixture_hash = hashlib.sha256(
            json.dumps(fixture, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
        if (record.get("fixture_sha256") != expected_fixture_hash
                or outputs.get("repo", {}).get("fixture_sha256") != expected_fixture_hash):
            errors.append("FIXTURE_DIGEST_NOT_PINNED")
        if outputs.get("repo", {}).get("policy_source_commit") != casebook.get("policy_source_commit"):
            errors.append("POLICY_REVISION_MISMATCH")
        if record.get("reviewed_by") in (None, ""):
            errors.append("REVIEWER_NOT_RECORDED")

        violation = []
        for route in ROUTES:
            out = verdicts.get(route)
            if not out:
                continue
            for requirement in fixture["requirements"]:
                if out["checks"][requirement].get("satisfied") is False:
                    violation.append(f"{route}:{requirement}:REQUIREMENT_FAILED")
            for forbidden in fixture["forbidden"]:
                if out["checks"][forbidden].get("satisfied") is True:
                    violation.append(f"{route}:{forbidden}:FORBIDDEN_BEHAVIOR")
        if errors:
            status = "INCONCLUSIVE"
        elif violation:
            status = "FAIL"
        else:
            status = "PASS"
        report.append({"id": case_id, "status": status, "errors": errors,
                       "violations": violation})
    counts = {status: sum(c["status"] == status for c in report) for status in LABELS}
    return {"status": "PASS" if counts["PASS"] == len(report) else
            "FAIL" if counts["FAIL"] else "INCONCLUSIVE",
            "counts": counts, "cases": report,
            "warning": "Structured human-verified paired behavioral evidence only; not deterministic LLM prose equivalence."}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--cases", type=Path, required=True)
    p.add_argument("--records", type=Path, required=True)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    casebook, _ = load_cases(args.cases)
    records = json.loads(args.records.read_text(encoding="utf-8"))
    outcome = evaluate(casebook, records)
    result = json.dumps(outcome, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(result + "\n", encoding="utf-8")
    else:
        print(result)
    return 0 if outcome["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
