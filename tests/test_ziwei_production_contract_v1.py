from __future__ import annotations
import json
import unittest
from pathlib import Path

from tools.ziwei_natal_provider import NormalizedNatalInput
from tools.ziwei_scope_a_pipeline import run_scope_a_natal

ROOT=Path(__file__).resolve().parents[1]

class ZiWeiProductionContractV1Tests(unittest.TestCase):
    def test_manifest_is_bounded_and_not_auto_routed(self):
        m=json.loads((ROOT/"ZIWEI_PRODUCTION_ADMISSION_V1.json").read_text(encoding="utf-8"))
        self.assertEqual("PRODUCTION_ADMITTED",m["status"])
        self.assertEqual("explicit_user_request_only",m["activation"])
        self.assertFalse(m["ordinary_auto_routing"])
        self.assertEqual(56,m["scope"]["admitted_claims"])
        self.assertEqual(4,m["scope"]["optional_auxiliary_subjects"])
        self.assertEqual("1.1.0",m["pipeline"]["pipeline_version"])
        self.assertEqual("conditional_activation_v1",m["pipeline"]["conditional_activation_contract"])
        self.assertFalse(m["admission_decision"]["g8_ordinary_routing_admitted"])
        self.assertFalse(m["admission_decision"]["scientific_predictive_validity_claimed"])

    def test_pipeline_binds_provider_retrieval_and_delivery(self):
        r=run_scope_a_natal(NormalizedNatalInput(1987,5,20,"酉","synthetic:production-test"),request_id="r1")
        self.assertEqual("PRODUCTION_ADMITTED",r["status"])
        self.assertTrue(r["authority"]["production_authority_granted"])
        self.assertFalse(r["authority"]["ordinary_auto_routing"])
        self.assertFalse(r["authority"]["final_prose_authority"])
        self.assertEqual("ziwei.scope_a.natal_v0",r["calculation"]["calculation_profile"]["profile_id"])
        self.assertGreater(len(r["interpretation"]["selected_claim_ids"]),0)
        self.assertTrue(r["interpretation"]["conditional_evaluations"])
        self.assertIn("PRESENT_CONFLICT_SEPARATELY",r["delivery"]["actions"])

    def test_research_registries_remain_historically_non_routable(self):
        m=json.loads((ROOT/"ZIWEI_PRODUCTION_ADMISSION_V1.json").read_text(encoding="utf-8"))
        for name in m["admitted_research_registries"]:
            r=json.loads((ROOT/"references"/"ziwei"/name).read_text(encoding="utf-8"))
            self.assertFalse(r["production_routable"])

    def test_subject_gate_is_preserved(self):
        r=run_scope_a_natal(NormalizedNatalInput(1981,11,7,"丑","synthetic:production-test"),request_id="r2",requested_subjects=("紫微",))
        self.assertTrue(r["interpretation"]["selected_claim_ids"])
        self.assertEqual({"紫微"},set(r["interpretation"]["subject_claims"]))

    def test_uncomputed_fact_gated_conditional_is_not_selected(self):
        r=run_scope_a_natal(
            NormalizedNatalInput(1987,5,20,"酉","synthetic:production-test"),
            request_id="conditional",
            requested_subjects=("天相",),
        )
        self.assertNotIn("ZW-B2-TIANXIANG-COND-002",r["interpretation"]["selected_claim_ids"])
        states={x["claim_id"]:x["state"] for x in r["interpretation"]["conditional_evaluations"]}
        self.assertEqual("not_computed",states["ZW-B2-TIANXIANG-COND-002"])

    def test_normalization_boundary_remains_fail_closed(self):
        with self.assertRaises(ValueError):
            run_scope_a_natal(NormalizedNatalInput(1987,5,20,"酉",""),request_id="r3")
        with self.assertRaises(ValueError):
            run_scope_a_natal(NormalizedNatalInput(1987,5,20,"酉","synthetic"),request_id=" ")

    def test_unsupported_layers_stay_not_computed(self):
        r=run_scope_a_natal(NormalizedNatalInput(1987,5,20,"酉","synthetic"),request_id="r4")
        self.assertEqual("not_computed",r["calculation"]["unsupported"]["brightness"])
        self.assertEqual("not_computed",r["calculation"]["unsupported"]["auxiliary_stars"])
        self.assertEqual("not_computed",r["calculation"]["unsupported"]["four_transformations"])
        self.assertEqual("not_computed",r["calculation"]["unsupported"]["dynamic"])

if __name__=="__main__":
    unittest.main()
