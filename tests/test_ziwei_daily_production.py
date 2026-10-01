import json
import unittest
from pathlib import Path
from tools.ziwei_runtime import run_ziwei_dynamic_v4_transport, run_ziwei_dynamic_v5_transport

ROOT=Path(__file__).resolve().parents[1]

def birth():
    return {
        "input_type":"normalized_lunar","lunar_year":1987,"lunar_month":5,"lunar_day":20,
        "hour_branch":"酉","calendar_provenance":"synthetic","leap_month_identity":"normalized_upstream"
    }

def p5(scope,target):
    return {
        "schema_name":"ziwei_dynamic_request","schema_version":"5.0.0","request_id":"day1",
        "temporal_scope":scope,"birth":birth(),"gender":"male","target":target,
        "requested_subjects":[],"enabled_source_ids":[]
    }

class ZiWeiDailyProductionTests(unittest.TestCase):
    def test_daily_admission_is_calculation_only(self):
        a=json.loads((ROOT/"admissions/ziwei/temporal/calculation/ZIWEI_DAILY_ADMISSION_V1.json").read_text(encoding="utf-8"))
        self.assertEqual("PRODUCTION_ADMITTED_CALCULATION_ONLY",a["status"])
        self.assertEqual("daily.monthly_parent_lunar_day_v1",a["profile"]["profile_id"])
        self.assertEqual("monthly",a["parent_scope"]["required"])
        self.assertEqual("NOT_ADMITTED",a["calendar_policy"]["physical_day_pillar"])
        self.assertFalse(a["ordinary_auto_routing"])

    def test_v5_daily_runs_and_parent_scopes_remain_available(self):
        target={
            "input_type":"normalized_lunar_day","lunar_year":2026,"lunar_month":9,"lunar_day":5,
            "is_leap_month":False,"calendar_provenance":"synthetic:target"
        }
        d=run_ziwei_dynamic_v5_transport(p5("daily",target))
        self.assertEqual("bounded_daily_calculation_v1",d["scope"])
        self.assertEqual("daily",d["runtime"]["temporal_scope"])
        self.assertEqual("NOT_ADMITTED",d["interpretation"]["status"])

        m=run_ziwei_dynamic_v5_transport(p5("monthly",{
            "input_type":"normalized_lunar_month","lunar_year":2026,"lunar_month":9,"lunar_day":5,
            "is_leap_month":False,"calendar_provenance":"synthetic:target"
        }))
        self.assertEqual("bounded_monthly_calculation_v1",m["scope"])
        y=run_ziwei_dynamic_v5_transport(p5("yearly",{"input_type":"lunar_year","lunar_year":2026}))
        self.assertEqual("bounded_yearly_calculation_v1",y["scope"])
        dec=run_ziwei_dynamic_v5_transport(p5("decadal",{"input_type":"lunar_year","lunar_year":2026}))
        self.assertEqual("bounded_decadal_calculation_v1",dec["scope"])

    def test_v4_remains_monthly_max_and_v5_rejects_hourly(self):
        old={
            "schema_name":"ziwei_dynamic_request","schema_version":"4.0.0","request_id":"old",
            "temporal_scope":"daily","birth":birth(),"gender":"male",
            "target":{"input_type":"normalized_lunar_month","lunar_year":2026,"lunar_month":9,"lunar_day":5,
                      "is_leap_month":False,"calendar_provenance":"synthetic:target"},
            "requested_subjects":[],"enabled_source_ids":[]
        }
        with self.assertRaises(ValueError):
            run_ziwei_dynamic_v4_transport(old)
        with self.assertRaises(ValueError):
            run_ziwei_dynamic_v5_transport(p5("hourly",{
                "input_type":"normalized_lunar_day","lunar_year":2026,"lunar_month":9,"lunar_day":5,
                "is_leap_month":False,"calendar_provenance":"synthetic:target"
            }))

    def test_daily_target_requires_daily_identity_and_provenance(self):
        wrong=p5("daily",{
            "input_type":"normalized_lunar_month","lunar_year":2026,"lunar_month":9,"lunar_day":5,
            "is_leap_month":False,"calendar_provenance":"synthetic:target"
        })
        with self.assertRaises(ValueError):
            run_ziwei_dynamic_v5_transport(wrong)
        missing=p5("daily",{
            "input_type":"normalized_lunar_day","lunar_year":2026,"lunar_month":9,"lunar_day":5,
            "is_leap_month":False
        })
        with self.assertRaises(ValueError):
            run_ziwei_dynamic_v5_transport(missing)

if __name__=="__main__":
    unittest.main()
