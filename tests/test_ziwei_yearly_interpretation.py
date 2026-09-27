import json
import unittest
from pathlib import Path
from tools.ziwei_runtime import run_ziwei_dynamic_v7_transport, run_ziwei_dynamic_v8_transport

ROOT=Path(__file__).resolve().parents[1]

def birth():
    return {
        "input_type":"normalized_lunar","lunar_year":1987,"lunar_month":5,"lunar_day":20,
        "hour_branch":"酉","calendar_provenance":"synthetic","leap_month_identity":"normalized_upstream"
    }

def p8(scope,target,subjects=None,sources=None):
    return {
        "schema_name":"ziwei_dynamic_request","schema_version":"8.0.0","request_id":"y-int-1",
        "temporal_scope":scope,"birth":birth(),"gender":"male","target":target,
        "requested_subjects":subjects or [],"enabled_source_ids":sources or []
    }

class ZiWeiYearlyInterpretationTests(unittest.TestCase):
    def test_admission_is_bounded_and_three_claims_only(self):
        a=json.loads((ROOT/"ZIWEI_YEARLY_INTERPRETATION_ADMISSION_V1.json").read_text(encoding="utf-8"))
        self.assertEqual("PRODUCTION_ADMITTED_BOUNDED_INTERPRETATION",a["status"])
        self.assertEqual("yearly",a["temporal_scope"])
        self.assertEqual(3,len(a["admitted_claim_ids"]))
        self.assertFalse(a["production_boundary"]["natal_claim_promotion"])
        self.assertFalse(a["production_boundary"]["decadal_claim_promotion"])
        self.assertFalse(a["production_boundary"]["yearly_sihua_interpretation"])

    def test_v8_yearly_selects_only_yearly_methodology_claims(self):
        r=run_ziwei_dynamic_v8_transport(p8("yearly",{"input_type":"lunar_year","lunar_year":2026}))
        self.assertEqual("PRODUCTION_ADMITTED",r["status"])
        self.assertEqual("bounded_yearly_calculation_v1+interpretation_v1",r["scope"])
        self.assertEqual("PRODUCTION_ADMITTED_BOUNDED",r["interpretation"]["status"])
        self.assertEqual(
            ["ZW-Y1-METHOD-BOUNDARY-003","ZW-Y1-METHOD-PARENT-002","ZW-Y1-METHOD-TOPOLOGY-001"],
            r["interpretation"]["selected_claim_ids"]
        )
        self.assertTrue(r["authority"]["interpretation_authority_granted"])
        for c in r["interpretation"]["selected_claims"]:
            self.assertEqual("yearly",c["temporal_scope"])

    def test_v8_decadal_preserves_v7_bounded_interpretation(self):
        r=run_ziwei_dynamic_v8_transport(p8("decadal",{"input_type":"lunar_year","lunar_year":2026}))
        self.assertEqual("PRODUCTION_ADMITTED_BOUNDED",r["interpretation"]["status"])
        self.assertEqual(
            ["ZW-D10-METHOD-CONTEXT-001","ZW-D10-METHOD-CORROBORATION-002"],
            r["interpretation"]["selected_claim_ids"]
        )

    def test_v8_other_lower_scopes_remain_not_admitted(self):
        m=run_ziwei_dynamic_v8_transport(p8("monthly",{
            "input_type":"normalized_lunar_month","lunar_year":2026,"lunar_month":8,"lunar_day":10,
            "is_leap_month":False,"calendar_provenance":"synthetic"
        }))
        self.assertEqual("NOT_ADMITTED",m["interpretation"]["status"])
        self.assertFalse(m["authority"]["interpretation_authority_granted"])

    def test_v7_yearly_remains_not_admitted(self):
        old=p8("yearly",{"input_type":"lunar_year","lunar_year":2026})
        old["schema_version"]="7.0.0"
        r=run_ziwei_dynamic_v7_transport(old)
        self.assertEqual("PRODUCTION_ADMITTED_CALCULATION_ONLY",r["status"])
        self.assertEqual("NOT_ADMITTED",r["interpretation"]["status"])

    def test_source_gate_can_exclude_yearly_claims(self):
        r=run_ziwei_dynamic_v8_transport(p8(
            "yearly",{"input_type":"lunar_year","lunar_year":2026},
            sources=["SRC-NOT-YEARLY"]
        ))
        self.assertEqual([],r["interpretation"]["selected_claim_ids"])

if __name__=="__main__":
    unittest.main()
