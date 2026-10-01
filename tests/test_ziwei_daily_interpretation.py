import json
import unittest
from pathlib import Path
from tools.ziwei_runtime import run_ziwei_dynamic_v9_transport, run_ziwei_dynamic_v10_transport

ROOT=Path(__file__).resolve().parents[1]

def birth():
    return {
        "input_type":"normalized_lunar","lunar_year":1987,"lunar_month":5,"lunar_day":20,
        "hour_branch":"酉","calendar_provenance":"synthetic","leap_month_identity":"normalized_upstream"
    }

def p10(scope,target,subjects=None,sources=None):
    return {
        "schema_name":"ziwei_dynamic_request","schema_version":"10.0.0","request_id":"d-int-1",
        "temporal_scope":scope,"birth":birth(),"gender":"male","target":target,
        "requested_subjects":subjects or [],"enabled_source_ids":sources or []
    }

DAY={
  "input_type":"normalized_lunar_day","lunar_year":2026,"lunar_month":8,"lunar_day":10,
  "is_leap_month":False,"calendar_provenance":"synthetic"
}

class ZiWeiDailyInterpretationTests(unittest.TestCase):
    def test_admission_is_bounded_and_three_claims_only(self):
        a=json.loads((ROOT/"admissions/ziwei/temporal/interpretation/ZIWEI_DAILY_INTERPRETATION_ADMISSION_V1.json").read_text(encoding="utf-8"))
        self.assertEqual("PRODUCTION_ADMITTED_BOUNDED_INTERPRETATION",a["status"])
        self.assertEqual("daily",a["temporal_scope"])
        self.assertEqual(3,len(a["admitted_claim_ids"]))
        self.assertFalse(a["production_boundary"]["monthly_claim_promotion"])
        self.assertFalse(a["production_boundary"]["day_pillar_interpretation"])
        self.assertFalse(a["production_boundary"]["daily_sihua_interpretation"])

    def test_v10_daily_selects_only_daily_methodology_claims(self):
        r=run_ziwei_dynamic_v10_transport(p10("daily",DAY))
        self.assertEqual("PRODUCTION_ADMITTED",r["status"])
        self.assertEqual("bounded_daily_calculation_v1+interpretation_v1",r["scope"])
        self.assertEqual("PRODUCTION_ADMITTED_BOUNDED",r["interpretation"]["status"])
        self.assertEqual(
            ["ZW-D1-METHOD-BOUNDARY-003","ZW-D1-METHOD-IDENTITY-001","ZW-D1-METHOD-PARENT-002"],
            r["interpretation"]["selected_claim_ids"]
        )
        self.assertTrue(r["authority"]["interpretation_authority_granted"])
        for c in r["interpretation"]["selected_claims"]:
            self.assertEqual("daily",c["temporal_scope"])

    def test_v10_monthly_preserves_v9_interpretation(self):
        r=run_ziwei_dynamic_v10_transport(p10("monthly",{
            "input_type":"normalized_lunar_month","lunar_year":2026,"lunar_month":8,"lunar_day":10,
            "is_leap_month":False,"calendar_provenance":"synthetic"
        }))
        self.assertEqual("PRODUCTION_ADMITTED_BOUNDED",r["interpretation"]["status"])
        self.assertEqual(
            ["ZW-M1-METHOD-BOUNDARY-003","ZW-M1-METHOD-IDENTITY-001","ZW-M1-METHOD-PARENT-002"],
            r["interpretation"]["selected_claim_ids"]
        )

    def test_v10_hourly_remains_not_admitted(self):
        h=run_ziwei_dynamic_v10_transport(p10("hourly",{
            "input_type":"normalized_lunar_hour","lunar_year":2026,"lunar_month":8,"lunar_day":10,
            "is_leap_month":False,"hour_branch":"午","rat_hour_policy":"next_day_at_23",
            "calendar_provenance":"synthetic"
        }))
        self.assertEqual("NOT_ADMITTED",h["interpretation"]["status"])
        self.assertFalse(h["authority"]["interpretation_authority_granted"])

    def test_v9_daily_remains_not_admitted(self):
        old=p10("daily",DAY); old["schema_version"]="9.0.0"
        r=run_ziwei_dynamic_v9_transport(old)
        self.assertEqual("PRODUCTION_ADMITTED_CALCULATION_ONLY",r["status"])
        self.assertEqual("NOT_ADMITTED",r["interpretation"]["status"])

    def test_source_gate_can_exclude_daily_claims(self):
        r=run_ziwei_dynamic_v10_transport(p10("daily",DAY,sources=["SRC-NOT-DAILY"]))
        self.assertEqual([],r["interpretation"]["selected_claim_ids"])

if __name__=="__main__":
    unittest.main()
