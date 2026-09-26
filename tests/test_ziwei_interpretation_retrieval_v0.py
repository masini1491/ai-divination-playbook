from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "references" / "ziwei" / "interpretation_retrieval_v0.py"
spec = importlib.util.spec_from_file_location("ziwei_retrieval_v0", ENGINE)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

FactPacket = mod.FactPacket
retrieve_claims = mod.retrieve_claims
compose_frame = mod.compose_frame

class ZiWeiExecutableRetrievalV0Tests(unittest.TestCase):
    def packet(self, facts, **kwargs):
        return FactPacket(
            packet_id="fixture",
            interpretation_profile="ziwei.interpretation.tw_v1",
            temporal_scope=kwargs.get("temporal_scope", "natal_baseline"),
            facts=frozenset(facts),
            requested_subjects=frozenset(kwargs.get("requested_subjects", [])),
            enabled_source_ids=frozenset(kwargs.get("enabled_source_ids", [])),
        )

    def activation(self, result, claim_id):
        return next(x for x in result["conditional_evaluations"] if x["claim_id"] == claim_id)

    def test_context_only_conditional_is_selected_without_chart_trigger(self):
        r=retrieve_claims(self.packet({"star_present:天機"},requested_subjects={"天機"}))
        ids=[x["claim_id"] for x in r["selected_claims"]]
        self.assertIn("ZW-B1-TIANJI-CORE-001",ids)
        self.assertIn("ZW-B1-TIANJI-COND-002",ids)
        self.assertEqual("not_required",self.activation(r,"ZW-B1-TIANJI-COND-002")["state"])

    def test_fact_gated_conditional_is_not_computed_without_domain(self):
        r=retrieve_claims(self.packet({"star_present:天相"},requested_subjects={"天相"}))
        ids=[x["claim_id"] for x in r["selected_claims"]]
        self.assertIn("ZW-B2-TIANXIANG-CORE-001",ids)
        self.assertNotIn("ZW-B2-TIANXIANG-COND-002",ids)
        self.assertEqual("not_computed",self.activation(r,"ZW-B2-TIANXIANG-COND-002")["state"])
        reason={x["claim_id"]:x["reason"] for x in r["omissions"]}
        self.assertEqual("conditional_fact_not_computed",reason["ZW-B2-TIANXIANG-COND-002"])

    def test_fact_gated_conditional_is_unsatisfied_when_domain_has_no_trigger(self):
        r=retrieve_claims(self.packet({"star_present:天相","fact_available:m0_auxiliary_stars"},requested_subjects={"天相"}))
        self.assertNotIn("ZW-B2-TIANXIANG-COND-002",[x["claim_id"] for x in r["selected_claims"]])
        self.assertEqual("unsatisfied",self.activation(r,"ZW-B2-TIANXIANG-COND-002")["state"])
        reason={x["claim_id"]:x["reason"] for x in r["omissions"]}
        self.assertEqual("conditional_condition_unsatisfied",reason["ZW-B2-TIANXIANG-COND-002"])

    def test_fact_gated_conditional_is_selected_when_trigger_is_demonstrated(self):
        r=retrieve_claims(self.packet({"star_present:天相","fact_available:m0_auxiliary_stars","modifier_present:天相:左輔"},requested_subjects={"天相"}))
        self.assertIn("ZW-B2-TIANXIANG-COND-002",[x["claim_id"] for x in r["selected_claims"]])
        a=self.activation(r,"ZW-B2-TIANXIANG-COND-002")
        self.assertEqual("satisfied",a["state"])
        self.assertEqual(["modifier_present:天相:左輔"],a["matched_satisfies_any"])

    def test_missing_brightness_domain_is_explicit_not_computed(self):
        r=retrieve_claims(self.packet({"star_present:太陰"},requested_subjects={"太陰"}))
        ids=[x["claim_id"] for x in r["selected_claims"]]
        self.assertIn("ZW-B2-TAIYIN-CORE-001",ids)
        self.assertNotIn("ZW-B2-TAIYIN-COND-002",ids)
        self.assertEqual("not_computed",self.activation(r,"ZW-B2-TAIYIN-COND-002")["state"])

    def test_palace_claims_are_selected_without_cartesian_star_palace_claim(self):
        p=self.packet({"star_present:紫微","palace_present:命宮"})
        r=retrieve_claims(p)
        ids=[x["claim_id"] for x in r["selected_claims"]]
        self.assertIn("ZW-B1-ZIWEI-CORE-001",ids)
        self.assertNotIn("ZW-B1-ZIWEI-COND-002",ids)
        self.assertIn("ZW-PAL-MING-DOM-001",ids)
        self.assertNotIn("ZW-PAL-MING-COND-002",ids)
        self.assertEqual("not_computed",self.activation(r,"ZW-PAL-MING-COND-002")["state"])
        reasons={x["claim_id"]:x["reason"] for x in r["omissions"]}
        self.assertEqual("conditional_fact_not_computed",reasons["ZW-PAL-MING-COND-002"])
        frame=compose_frame(p,r)
        self.assertIn("紫微",frame["subject_claims"])
        self.assertIn("命宮",frame["subject_claims"])

    def test_registered_context_only_conflict_is_preserved(self):
        r=retrieve_claims(self.packet({"star_present:天機"},requested_subjects={"天機"}))
        groups={x["conflict_group_id"]:x for x in r["conflicts"]}
        self.assertIn("CG-TIANJI-RELIEF-001",groups)
        self.assertEqual("PRESERVE_CONFLICT",groups["CG-TIANJI-RELIEF-001"]["resolution_status"])

    def test_dynamic_scope_fails_closed(self):
        r=retrieve_claims(self.packet({"star_present:紫微"},temporal_scope="yearly"))
        self.assertEqual([],r["selected_claims"])

    def test_source_gate_can_exclude_claims(self):
        r=retrieve_claims(self.packet({"star_present:紫微"},enabled_source_ids={"SRC-NIHAI-TIANJI"}))
        self.assertEqual([],r["selected_claims"])

if __name__=="__main__":
    unittest.main()
