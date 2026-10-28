"""Fail-closed regression tests for paired Repo/MCP interpretation parity reports."""
import copy
import hashlib
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "mcp_parity_eval", ROOT/"tools/evaluate_mcp_interpretation_parity.py")
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)
CASEBOOK, CASES = mod.load_cases(ROOT/"evals/mcp_interpretation_parity/cases.json")


def baseline():
    records = {"schema_version": 1, "cases": []}
    for case in CASEBOOK["cases"]:
        body = "FIXED FACTS. Rule checked. No violation. Verdict remains symbolic."
        checks = {x: {"satisfied": True, "evidence_quote": "Rule checked"}
                  for x in case["requirements"]}
        checks.update({x: {"satisfied": False, "evidence_quote": "No violation"}
                       for x in case["forbidden"]})
        # This is a synthetic evaluator fixture, not a real model test result.
        output = {"response": body, "checks": checks, "model_id": "fixture-model",
                  "model_config_id": "identical-config",
                  "policy_source_commit": CASEBOOK["policy_source_commit"],
                  "fixture_sha256": hashlib.sha256(
                      json.dumps(case, sort_keys=True, ensure_ascii=False).encode()).hexdigest()}
        records["cases"].append({"id": case["id"], "reviewed_by": "synthetic-unit-test",
                                 "fixture_sha256": output["fixture_sha256"],
                                 "outputs": {"repo": copy.deepcopy(output),
                                             "mcp": copy.deepcopy(output)}})
    return records


class PairedInterpretationEvalTests(unittest.TestCase):
    def test_six_fixed_cases_are_present(self):
        self.assertEqual(len(CASES), 6)
        self.assertEqual({x["method"] for x in CASES.values()},
                         {"tarot", "meihua", "liuyao"})

    def test_synthetic_positive_control(self):
        report = mod.evaluate(CASEBOOK, baseline())
        self.assertEqual(report["status"], "PASS")

    def test_real_records_missing_remain_inconclusive(self):
        report = mod.evaluate(CASEBOOK, {"schema_version": 1, "cases": []})
        self.assertEqual(report["status"], "INCONCLUSIVE")
        self.assertEqual(report["counts"]["INCONCLUSIVE"], 6)

    def test_actual_forbidden_behavior_fails(self):
        rec = baseline()
        one = rec["cases"][0]["outputs"]["mcp"]["checks"]["objective_percentage"]
        one["satisfied"] = True
        self.assertEqual(mod.evaluate(CASEBOOK, rec)["status"], "FAIL")

    def test_missing_quote_never_passes(self):
        rec = baseline()
        rec["cases"][0]["outputs"]["mcp"]["checks"]["same_fixed_cards"]["evidence_quote"] = "invented quote"
        self.assertEqual(mod.evaluate(CASEBOOK, rec)["status"], "INCONCLUSIVE")

    def test_method_or_model_or_source_mismatch_never_passes(self):
        for key, value in (("model_id", "different-model"),
                           ("model_config_id", "different-configuration"),
                           ("policy_source_commit", "wrong-source"),
                           ("fixture_sha256", "wrong-digest")):
            with self.subTest(key=key):
                rec = baseline()
                rec["cases"][0]["outputs"]["mcp"][key] = value
                self.assertEqual(mod.evaluate(CASEBOOK, rec)["status"], "INCONCLUSIVE")

    def test_unreviewed_response_remains_inconclusive(self):
        rec = baseline()
        rec["cases"][0]["reviewed_by"] = None
        self.assertEqual(mod.evaluate(CASEBOOK, rec)["status"], "INCONCLUSIVE")

    def test_truncated_one_route_remains_inconclusive(self):
        rec = baseline()
        rec["cases"][0]["outputs"].pop("mcp")
        self.assertEqual(mod.evaluate(CASEBOOK, rec)["status"], "INCONCLUSIVE")

    def test_unknown_case_and_duplicate_rejected(self):
        for value in ("TAROT-LIKELIHOOD", "UNRECOGNIZED"):
            rec = baseline()
            rec["cases"].append({**rec["cases"][0], "id": value})
            with self.subTest(value=value), self.assertRaises(ValueError):
                mod.evaluate(CASEBOOK, rec)


if __name__ == "__main__":
    unittest.main()
