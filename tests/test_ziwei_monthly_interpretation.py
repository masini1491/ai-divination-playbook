import json
import unittest
from pathlib import Path
from tools.ziwei_runtime import run_ziwei_dynamic_v8_transport, run_ziwei_dynamic_v9_transport

ROOT=Path(__file__).resolve().parents[1]

def birth():
    return {
        "input_type":"normalized_lunar","lunar_year":1987,"lunar_month":5,"lunar_day":20,
        "hour_branch":"酉","calendar_provenance":"synthetic","leap_month_identity":"normalized_upstream"
    }

def p9(scope,target,subjects=None,sources=None):
    return {
        "schema_name":"ziwei_dynamic_request","schema_version":"9.0.0","request_id":"m-int-1",
        "temporal_scope":scope,"birth":birth(),"gender":"male","target":target,
        "requested_subjects":subjects or [],"enabled_source_ids":sources or []
    }

MONTH={
  "input_type":"normalized_lunar_month","lunar_year":2026,"lunar_month":8,"lunar_day":10,
  "is_leap_month":False,"calendar_provenance":"synthetic"
}

class ZiWeiMonthlyInterpretationTests(unittest.TestCase):
    def test_admission_is_bounded_and_three_claims_only(self):
        a=json.loads((ROOT/"admissions/ziwei/temporal/interpretation/ZIWEI_MONTHLY_INTERPRETATION_ADMISSION_V1.json").read_text(encoding="utf-8"))
        self.assertEqual("PRODUCTION_ADMITTED_BOUNDED_INTERPRETATION",a["status"])
        self.assertEqual("monthly",a["temporal_scope"])
        self.assertEqual(3,len(a["admitted_claim_ids"]))
        self.assertFalse(a["production_boundary"]["yearly_claim_promotion"])
        self.assertFalse(a["production_boundary"]["monthly_sihua_interpretation"])

    def test_v9_monthly_selects_only_monthly_methodology_claims(self):
        r=run_ziwei_dynamic_v9_transport(p9("monthly",MONTH))
        self.assertEqual("PRODUCTION_ADMITTED",r["status"])
        self.assertEqual("bounded_monthly_calculation_v1+interpretation_v1",r["scope"])
        self.assertEqual("PRODUCTION_ADMITTED_BOUNDED",r["interpretation"]["status"])
        self.assertEqual(
            ["ZW-M1-METHOD-BOUNDARY-003","ZW-M1-METHOD-IDENTITY-001","ZW-M1-METHOD-PARENT-002"],
            r["interpretation"]["selected_claim_ids"]
        )
        self.assertTrue(r["authority"]["interpretation_authority_granted"])
        for c in r["interpretation"]["selected_claims"]:
            self.assertEqual("monthly",c["temporal_scope"])

    def test_v9_yearly_preserves_v8_interpretation(self):
        r=run_ziwei_dynamic_v9_transport(p9("yearly",{"input_type":"lunar_year","lunar_year":2026}))
        self.assertEqual("PRODUCTION_ADMITTED_BOUNDED",r["interpretation"]["status"])
        self.assertEqual(
            ["ZW-Y1-METHOD-BOUNDARY-003","ZW-Y1-METHOD-PARENT-002","ZW-Y1-METHOD-TOPOLOGY-001"],
            r["interpretation"]["selected_claim_ids"]
        )

    def test_v9_decadal_preserves_v8_interpretation(self):
        r=run_ziwei_dynamic_v9_transport(p9("decadal",{"input_type":"lunar_year","lunar_year":2026}))
        self.assertEqual("PRODUCTION_ADMITTED_BOUNDED",r["interpretation"]["status"])

    def test_v9_daily_and_hourly_remain_not_admitted(self):
        d=run_ziwei_dynamic_v9_transport(p9("daily",{
            "input_type":"normalized_lunar_day","lunar_year":2026,"lunar_month":8,"lunar_day":10,
            "is_leap_month":False,"calendar_provenance":"synthetic"
        }))
        self.assertEqual("NOT_ADMITTED",d["interpretation"]["status"])
        self.assertFalse(d["authority"]["interpretation_authority_granted"])

    def test_v8_monthly_remains_not_admitted(self):
        old=p9("monthly",MONTH); old["schema_version"]="8.0.0"
        r=run_ziwei_dynamic_v8_transport(old)
        self.assertEqual("PRODUCTION_ADMITTED_CALCULATION_ONLY",r["status"])
        self.assertEqual("NOT_ADMITTED",r["interpretation"]["status"])

    def test_source_gate_can_exclude_monthly_claims(self):
        r=run_ziwei_dynamic_v9_transport(p9("monthly",MONTH,sources=["SRC-NOT-MONTHLY"]))
        self.assertEqual([],r["interpretation"]["selected_claim_ids"])

if __name__=="__main__":
    unittest.main()
