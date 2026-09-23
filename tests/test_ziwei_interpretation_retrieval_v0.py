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

    def test_star_core_and_conditional_are_deterministically_selected(self):
        p=self.packet({"star_present:紫微"})
        r=retrieve_claims(p)
        ids=[x["claim_id"] for x in r["selected_claims"]]
        self.assertIn("ZW-B1-ZIWEI-CORE-001",ids)
        self.assertIn("ZW-B1-ZIWEI-COND-002",ids)
        self.assertFalse(r["production_authority_granted"])

    def test_missing_required_fact_skips_dignity_dependent_claim(self):
        p=self.packet({"star_present:太陰"},requested_subjects={"太陰"})
        r=retrieve_claims(p)
        ids=[x["claim_id"] for x in r["selected_claims"]]
        self.assertIn("ZW-B2-TAIYIN-CORE-001",ids)
        self.assertNotIn("ZW-B2-TAIYIN-COND-002",ids)
        reason={x["claim_id"]:x["reason"] for x in r["omissions"]}
        self.assertEqual("required_fact_missing",reason["ZW-B2-TAIYIN-COND-002"])

    def test_palace_claims_are_selected_without_cartesian_star_palace_claim(self):
        p=self.packet({"star_present:紫微","palace_present:命宮"})
        r=retrieve_claims(p)
        ids=[x["claim_id"] for x in r["selected_claims"]]
        self.assertIn("ZW-B1-ZIWEI-CORE-001",ids)
        self.assertIn("ZW-PAL-MING-DOM-001",ids)
        frame=compose_frame(p,r)
        self.assertIn("紫微",frame["subject_claims"])
        self.assertIn("命宮",frame["subject_claims"])
        self.assertEqual("frame_only_no_doctrine_generation",frame["rendering_boundary"])

    def test_registered_conflict_is_preserved(self):
        p=self.packet({"star_present:天機"},requested_subjects={"天機"})
        r=retrieve_claims(p)
        groups={x["conflict_group_id"]:x for x in r["conflicts"]}
        self.assertIn("CG-TIANJI-RELIEF-001",groups)
        self.assertEqual("PRESERVE_CONFLICT",groups["CG-TIANJI-RELIEF-001"]["resolution_status"])

    def test_dynamic_scope_fails_closed(self):
        p=self.packet({"star_present:紫微"},temporal_scope="yearly")
        r=retrieve_claims(p)
        self.assertEqual([],r["selected_claims"])

    def test_source_gate_can_exclude_claims(self):
        p=self.packet({"star_present:紫微"},enabled_source_ids={"SRC-NIHAI-TIANJI"})
        r=retrieve_claims(p)
        self.assertEqual([],r["selected_claims"])

if __name__=="__main__":
    unittest.main()
