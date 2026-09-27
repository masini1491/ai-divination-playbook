import json
import unittest
from pathlib import Path
from tools.ziwei_runtime import run_ziwei_dynamic_v10_transport, run_ziwei_dynamic_v11_transport
ROOT=Path(__file__).resolve().parents[1]

def birth():
    return {"input_type":"normalized_lunar","lunar_year":1987,"lunar_month":5,"lunar_day":20,"hour_branch":"酉","calendar_provenance":"synthetic","leap_month_identity":"normalized_upstream"}

def p11(scope,target,subjects=None,sources=None):
    return {"schema_name":"ziwei_dynamic_request","schema_version":"11.0.0","request_id":"h-int-1","temporal_scope":scope,"birth":birth(),"gender":"male","target":target,"requested_subjects":subjects or [],"enabled_source_ids":sources or []}

HOUR={"input_type":"normalized_lunar_hour","lunar_year":2026,"lunar_month":8,"lunar_day":10,"is_leap_month":False,"hour_branch":"午","rat_hour_policy":"next_day_at_23","calendar_provenance":"synthetic"}

class ZiWeiHourlyInterpretationTests(unittest.TestCase):
    def test_admission_is_bounded_and_three_claims_only(self):
        a=json.loads((ROOT/"ZIWEI_HOURLY_INTERPRETATION_ADMISSION_V1.json").read_text(encoding="utf-8"))
        self.assertEqual("PRODUCTION_ADMITTED_BOUNDED_INTERPRETATION",a["status"])
        self.assertEqual("hourly",a["temporal_scope"])
        self.assertEqual(3,len(a["admitted_claim_ids"]))
        self.assertFalse(a["production_boundary"]["daily_claim_promotion"])
        self.assertFalse(a["production_boundary"]["physical_hour_pillar_interpretation"])
        self.assertFalse(a["production_boundary"]["hourly_sihua_interpretation"])

    def test_v11_hourly_selects_only_hourly_methodology_claims(self):
        r=run_ziwei_dynamic_v11_transport(p11("hourly",HOUR))
        self.assertEqual("PRODUCTION_ADMITTED",r["status"])
        self.assertEqual("bounded_hourly_calculation_v1+interpretation_v1",r["scope"])
        self.assertEqual("PRODUCTION_ADMITTED_BOUNDED",r["interpretation"]["status"])
        self.assertEqual(["ZW-H1-METHOD-BOUNDARY-003","ZW-H1-METHOD-IDENTITY-001","ZW-H1-METHOD-PARENT-002"],r["interpretation"]["selected_claim_ids"])
        self.assertTrue(r["authority"]["interpretation_authority_granted"])
        for c in r["interpretation"]["selected_claims"]: self.assertEqual("hourly",c["temporal_scope"])

    def test_v11_daily_preserves_v10_interpretation(self):
        r=run_ziwei_dynamic_v11_transport(p11("daily",{"input_type":"normalized_lunar_day","lunar_year":2026,"lunar_month":8,"lunar_day":10,"is_leap_month":False,"calendar_provenance":"synthetic"}))
        self.assertEqual("PRODUCTION_ADMITTED_BOUNDED",r["interpretation"]["status"])
        self.assertEqual(["ZW-D1-METHOD-BOUNDARY-003","ZW-D1-METHOD-IDENTITY-001","ZW-D1-METHOD-PARENT-002"],r["interpretation"]["selected_claim_ids"])

    def test_v10_hourly_remains_not_admitted(self):
        old=p11("hourly",HOUR); old["schema_version"]="10.0.0"
        r=run_ziwei_dynamic_v10_transport(old)
        self.assertEqual("PRODUCTION_ADMITTED_CALCULATION_ONLY",r["status"])
        self.assertEqual("NOT_ADMITTED",r["interpretation"]["status"])

    def test_source_gate_can_exclude_hourly_claims(self):
        r=run_ziwei_dynamic_v11_transport(p11("hourly",HOUR,sources=["SRC-NOT-HOURLY"]))
        self.assertEqual([],r["interpretation"]["selected_claim_ids"])

if __name__=="__main__": unittest.main()
