import json
import unittest
from pathlib import Path
from tools.ziwei_runtime import run_ziwei_dynamic_v6_transport, run_ziwei_dynamic_v7_transport

ROOT=Path(__file__).resolve().parents[1]

def birth():
    return {
        "input_type":"normalized_lunar","lunar_year":1987,"lunar_month":5,"lunar_day":20,
        "hour_branch":"酉","calendar_provenance":"synthetic","leap_month_identity":"normalized_upstream"
    }

def p7(scope,target,subjects=None):
    return {
        "schema_name":"ziwei_dynamic_request","schema_version":"7.0.0","request_id":"d-int-1",
        "temporal_scope":scope,"birth":birth(),"gender":"male","target":target,
        "requested_subjects":subjects or [],"enabled_source_ids":[]
    }

class ZiWeiDecadalInterpretationTests(unittest.TestCase):
    def test_admission_is_bounded_and_two_claims_only(self):
        a=json.loads((ROOT/"ZIWEI_DECADAL_INTERPRETATION_ADMISSION_V1.json").read_text(encoding="utf-8"))
        self.assertEqual("PRODUCTION_ADMITTED_BOUNDED_INTERPRETATION",a["status"])
        self.assertEqual("decadal",a["temporal_scope"])
        self.assertEqual(2,len(a["admitted_claim_ids"]))
        self.assertFalse(a["production_boundary"]["natal_claim_promotion"])
        self.assertFalse(a["production_boundary"]["concrete_event_prediction"])

    def test_v7_decadal_selects_only_decadal_methodology_claims(self):
        r=run_ziwei_dynamic_v7_transport(p7("decadal",{"input_type":"lunar_year","lunar_year":2026}))
        self.assertEqual("PRODUCTION_ADMITTED",r["status"])
        self.assertEqual("bounded_decadal_calculation_v1+interpretation_v1",r["scope"])
        self.assertEqual("PRODUCTION_ADMITTED_BOUNDED",r["interpretation"]["status"])
        self.assertEqual(
            ["ZW-D10-METHOD-CONTEXT-001","ZW-D10-METHOD-CORROBORATION-002"],
            r["interpretation"]["selected_claim_ids"]
        )
        self.assertTrue(r["authority"]["interpretation_authority_granted"])
        for c in r["interpretation"]["selected_claims"]:
            self.assertEqual("decadal",c["applicability"]["temporal_scope"])

    def test_v7_subject_gate_can_omit_decadal_claims_without_fallback(self):
        r=run_ziwei_dynamic_v7_transport(p7("decadal",{"input_type":"lunar_year","lunar_year":2026},["不存在主題"]))
        self.assertEqual([],r["interpretation"]["selected_claim_ids"])
        self.assertEqual("PRODUCTION_ADMITTED_BOUNDED",r["interpretation"]["status"])

    def test_v7_other_dynamic_scopes_remain_interpretation_not_admitted(self):
        y=run_ziwei_dynamic_v7_transport(p7("yearly",{"input_type":"lunar_year","lunar_year":2026}))
        self.assertEqual("NOT_ADMITTED",y["interpretation"]["status"])
        self.assertFalse(y["authority"]["interpretation_authority_granted"])

    def test_v6_remains_calculation_only_for_decadal(self):
        old=p7("decadal",{"input_type":"lunar_year","lunar_year":2026})
        old["schema_version"]="6.0.0"
        r=run_ziwei_dynamic_v6_transport(old)
        self.assertEqual("PRODUCTION_ADMITTED_CALCULATION_ONLY",r["status"])
        self.assertEqual("NOT_ADMITTED",r["interpretation"]["status"])

if __name__=="__main__":
    unittest.main()
