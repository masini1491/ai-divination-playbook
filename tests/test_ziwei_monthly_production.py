import json
import unittest
from pathlib import Path
from tools.ziwei_runtime import (
    run_ziwei_dynamic_v3_transport,
    run_ziwei_dynamic_v4_transport,
)

ROOT=Path(__file__).resolve().parents[1]

def birth():
    return {
        "input_type":"normalized_lunar","lunar_year":1987,"lunar_month":5,"lunar_day":20,
        "hour_branch":"酉","calendar_provenance":"synthetic","leap_month_identity":"normalized_upstream"
    }

def p4(scope,target):
    return {
        "schema_name":"ziwei_dynamic_request","schema_version":"4.0.0","request_id":"m1",
        "temporal_scope":scope,"birth":birth(),"gender":"male","target":target,
        "requested_subjects":[],"enabled_source_ids":[]
    }

class ZiWeiMonthlyProductionTests(unittest.TestCase):
    def test_monthly_admission_is_calculation_only(self):
        a=json.loads((ROOT/"ZIWEI_MONTHLY_ADMISSION_V1.json").read_text(encoding="utf-8"))
        self.assertEqual("PRODUCTION_ADMITTED_CALCULATION_ONLY",a["status"])
        self.assertEqual("monthly.doujun_effective_month_split15_v1",a["profile"]["profile_id"])
        self.assertEqual("yearly",a["parent_scope"]["required"])
        self.assertEqual("split_after_day_15",a["calendar_policy"]["leap_month_policy"])
        self.assertFalse(a["ordinary_auto_routing"])

    def test_v4_monthly_runs_and_parent_scopes_remain_available(self):
        m=run_ziwei_dynamic_v4_transport(p4("monthly",{
            "input_type":"normalized_lunar_month","lunar_year":2026,"lunar_month":9,"lunar_day":1,
            "is_leap_month":False,"calendar_provenance":"synthetic:target"
        }))
        self.assertEqual("bounded_monthly_calculation_v1",m["scope"])
        self.assertEqual("monthly",m["runtime"]["temporal_scope"])
        self.assertEqual("NOT_ADMITTED",m["interpretation"]["status"])

        y=run_ziwei_dynamic_v4_transport(p4("yearly",{"input_type":"lunar_year","lunar_year":2026}))
        self.assertEqual("bounded_yearly_calculation_v1",y["scope"])
        d=run_ziwei_dynamic_v4_transport(p4("decadal",{"input_type":"lunar_year","lunar_year":2026}))
        self.assertEqual("bounded_decadal_calculation_v1",d["scope"])

    def test_v3_remains_yearly_max_and_v4_rejects_daily(self):
        old={
            "schema_name":"ziwei_dynamic_request","schema_version":"3.0.0","request_id":"old",
            "temporal_scope":"monthly","birth":birth(),"gender":"male","target_lunar_year":2026,
            "requested_subjects":[],"enabled_source_ids":[]
        }
        with self.assertRaises(ValueError):
            run_ziwei_dynamic_v3_transport(old)
        with self.assertRaises(ValueError):
            run_ziwei_dynamic_v4_transport(p4("daily",{
                "input_type":"normalized_lunar_month","lunar_year":2026,"lunar_month":9,"lunar_day":1,
                "is_leap_month":False,"calendar_provenance":"synthetic:target"
            }))

    def test_monthly_target_requires_explicit_leap_and_provenance(self):
        missing=p4("monthly",{
            "input_type":"normalized_lunar_month","lunar_year":2026,"lunar_month":9,"lunar_day":1,
            "is_leap_month":False
        })
        with self.assertRaises(ValueError):
            run_ziwei_dynamic_v4_transport(missing)

if __name__=="__main__":
    unittest.main()
