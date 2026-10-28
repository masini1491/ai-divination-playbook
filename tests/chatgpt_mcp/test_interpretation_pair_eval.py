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
        owners = {owner: CASEBOOK['policy_owner_digests'][owner] for owner in (
            {'tarot': 'TAROT.md', 'meihua': 'MEIHUA.md', 'liuyao': 'LIUYAO.md'}[case['method']],
            'CHATGPT_OUTPUT.md')}
        output = {"response": body, "checks": checks, "model_id": "fixture-model",
                  "model_config_id": "identical-config",
                  "policy_source_commit": CASEBOOK["policy_source_commit"],
                  "fixture_sha256": hashlib.sha256(
                      json.dumps(case, sort_keys=True, ensure_ascii=False).encode()).hexdigest()}
        output["capture"] = {"session_id": "fixture-session-repo",
                             "transport": "github_connector",
                             "owner_sha256": owners,
                             "response_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest()}
        mcp = copy.deepcopy(output)
        mcp["capture"]["session_id"] = "fixture-session-mcp"
        mcp["capture"]["transport"] = "mcp"
        records["cases"].append({"id": case["id"], "reviewed_by": "synthetic-unit-test",
                                 "fixture_sha256": output["fixture_sha256"],
                                 "outputs": {"repo": copy.deepcopy(output), "mcp": mcp}})
    return records


class PairedInterpretationEvalTests(unittest.TestCase):
    def test_six_fixed_cases_are_present(self):
        self.assertEqual(len(CASES), 6)
        self.assertEqual({x["method"] for x in CASES.values()},
                         {"tarot", "meihua", "liuyao"})

    def test_all_fixture_facts_match_real_deterministic_engines(self):
        for case in CASEBOOK["cases"]:
            with self.subTest(id=case["id"]):
                self.assertIsNone(mod.verify_fixture_facts(case))

    def test_misreported_fixed_method_facts_are_rejected(self):
        mutations = (
            ("TAROT-LIKELIHOOD", "cards", lambda f: f["cards"][0].update(full_name="not-a-real-card")),
            ("TAROT-QUALITY", "cards", lambda f: f["cards"][1].update(position=1)),
            ("MEIHUA-EVOLUTION", "mutual", lambda f: f.update(mutual_hexagram="乾為天")),
            ("MEIHUA-EXPLICIT-YESNO", "body_use", lambda f: f.update(body_use_relation="體生用")),
            ("LIUYAO-VERIFIED-CALENDAR", "month", lambda f: f.update(month_branch="辰")),
            ("LIUYAO-VERIFIED-CALENDAR", "moving", lambda f: f.update(moving_positions=[2])),
            ("LIUYAO-NO-CALENDAR", "calendar", lambda f: f.update(day_ganzhi="乙亥")),
            ("LIUYAO-NO-CALENDAR", "hexagram", lambda f: f.update(changed_hexagram="乾為天")),
        )
        for cid, label, mutation in mutations:
            with self.subTest(id=cid, mutation=label):
                wrong = copy.deepcopy(CASES[cid])
                mutation(wrong["facts"])
                with self.assertRaisesRegex(ValueError, "FIXTURE_METHOD_FACT_MISMATCH"):
                    mod.verify_fixture_facts(wrong)

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

    def test_response_and_source_provenance_mismatches_fail_closed(self):
        cases = (
            ("response_digest", lambda x: x["capture"].update(response_sha256="0"*64)),
            ("source_owner", lambda x: x["capture"]["owner_sha256"].update({"TAROT.md": "0"*64})),
            ("wrong_transport", lambda x: x["capture"].update(transport="github_connector")),
            ("copied_session", lambda x: x["capture"].update(session_id="fixture-session-repo")),
        )
        for label, mutation in cases:
            with self.subTest(case=label):
                rec = baseline()
                mutation(rec["cases"][0]["outputs"]["mcp"])
                self.assertEqual(mod.evaluate(CASEBOOK, rec)["status"], "INCONCLUSIVE")

    def test_invalid_check_shape_is_inconclusive_not_exception(self):
        for bad in (None, True, [], {"satisfied": True}, {"satisfied": "yes", "evidence_quote": "Rule checked"}):
            with self.subTest(value=bad):
                rec = baseline()
                rec["cases"][0]["outputs"]["mcp"]["checks"]["same_fixed_cards"] = bad
                self.assertEqual(mod.evaluate(CASEBOOK, rec)["status"], "INCONCLUSIVE")

    def test_non_object_route_is_inconclusive_not_exception(self):
        for bad in (None, [], 1, "wrong"):
            with self.subTest(value=bad):
                rec = baseline()
                rec["cases"][0]["outputs"]["mcp"] = bad
                self.assertEqual(mod.evaluate(CASEBOOK, rec)["status"], "INCONCLUSIVE")

    def test_unknown_case_and_duplicate_rejected(self):
        for value in ("TAROT-LIKELIHOOD", "UNRECOGNIZED"):
            rec = baseline()
            rec["cases"].append({**rec["cases"][0], "id": value})
            with self.subTest(value=value), self.assertRaises(ValueError):
                mod.evaluate(CASEBOOK, rec)


if __name__ == "__main__":
    unittest.main()
