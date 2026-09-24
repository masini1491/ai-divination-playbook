from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZIWEI = ROOT / "references" / "ziwei"
ENGINE = ZIWEI / "interpretation_retrieval_v0.py"
FIXTURES = ZIWEI / "ziwei_executable_behavioral_fixtures_v0.json"

spec = importlib.util.spec_from_file_location("ziwei_retrieval_behavioral_v0", ENGINE)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

class ZiWeiExecutableBehavioralValidationV0(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(FIXTURES.read_text(encoding="utf-8"))

    def test_fixture_contract_is_research_only(self):
        self.assertIn("NOT PRODUCTION-ROUTABLE", self.data["authority"])
        self.assertEqual("natal_baseline", self.data["temporal_scope"])

    def test_all_architecture_fixtures_have_executable_disposition(self):
        self.assertEqual([f"F{i}" for i in range(1,10)], [x["id"] for x in self.data["fixtures"]])

    def test_behavior_matches_declared_bounded_expectations(self):
        for fx in self.data["fixtures"]:
            with self.subTest(fixture=fx["id"]):
                packet = mod.FactPacket(
                    packet_id=fx["id"],
                    interpretation_profile=self.data["interpretation_profile"],
                    temporal_scope=self.data["temporal_scope"],
                    facts=frozenset(fx["facts"]),
                    requested_subjects=frozenset(fx.get("requested_subjects", [])),
                )
                result = mod.retrieve_claims(packet)
                ids = {x["claim_id"] for x in result["selected_claims"]}
                self.assertEqual(set(fx["expected_selected"]), ids)
                omitted = {x["claim_id"] for x in result["omissions"]}
                self.assertTrue(set(fx.get("expected_omitted", [])).issubset(omitted))
                conflicts = {x["conflict_group_id"] for x in result["conflicts"]}
                self.assertTrue(set(fx.get("expected_conflicts", [])).issubset(conflicts))
                states = {x["claim_id"]: x["state"] for x in result["conditional_evaluations"]}
                for claim_id, expected_state in fx.get("expected_conditional_states", {}).items():
                    self.assertEqual(expected_state, states[claim_id])
                self.assertFalse(result["production_authority_granted"])

    def test_blocked_context_is_never_represented_as_admitted_claim(self):
        for fx in self.data["fixtures"]:
            self.assertTrue(fx["blocked_dependencies"])
            self.assertIn(fx["classification"], {
                "PARTIAL_EXECUTABLE_CONTEXT_BLOCKED",
                "FAIL_CLOSED_PROFILE_BLOCKED",
                "PARTIAL_EXECUTABLE_CONFLICT_PRESERVED",
            })

if __name__ == "__main__":
    unittest.main()
