import json
import unittest
from pathlib import Path
from tools.ziwei_runtime import run_ziwei_dynamic_v5_transport, run_ziwei_dynamic_v6_transport

ROOT=Path(__file__).resolve().parents[1]

def birth():
    return {
        "input_type":"normalized_lunar","lunar_year":1987,"lunar_month":5,"lunar_day":20,
        "hour_branch":"酉","calendar_provenance":"synthetic","leap_month_identity":"normalized_upstream"
    }

def p6(scope,target):
    return {
        "schema_name":"ziwei_dynamic_request","schema_version":"6.0.0","request_id":"hour1",
        "temporal_scope":scope,"birth":birth(),"gender":"male","target":target,
        "requested_subjects":[],"enabled_source_ids":[]
    }

class ZiWeiHourlyProductionTests(unittest.TestCase):
    def test_hourly_admission_is_calculation_only(self):
        a=json.loads((ROOT/"ZIWEI_HOURLY_ADMISSION_V1.json").read_text(encoding="utf-8"))
        self.assertEqual("PRODUCTION_ADMITTED_CALCULATION_ONLY",a["status"])
        self.assertEqual("hourly.daily_parent_hour_branch_next_day_23_v1",a["profile"]["profile_id"])
        self.assertEqual("daily",a["parent_scope"]["required"])
        self.assertEqual("next_day_at_23",a["calendar_policy"]["rat_hour_policy"])
        self.assertEqual("NOT_ADMITTED",a["calendar_policy"]["physical_hour_pillar"])
        self.assertFalse(a["ordinary_auto_routing"])

    def test_v6_hourly_runs_and_parent_scopes_remain_available(self):
        target={
            "input_type":"normalized_lunar_hour","lunar_year":2026,"lunar_month":9,"lunar_day":5,
            "is_leap_month":False,"hour_branch":"午","rat_hour_policy":"next_day_at_23",
            "calendar_provenance":"synthetic:target"
        }
        h=run_ziwei_dynamic_v6_transport(p6("hourly",target))
        self.assertEqual("bounded_hourly_calculation_v1",h["scope"])
        self.assertEqual("hourly",h["runtime"]["temporal_scope"])
        self.assertEqual("NOT_ADMITTED",h["interpretation"]["status"])

        d=run_ziwei_dynamic_v6_transport(p6("daily",{
            "input_type":"normalized_lunar_day","lunar_year":2026,"lunar_month":9,"lunar_day":5,
            "is_leap_month":False,"calendar_provenance":"synthetic:target"
        }))
        self.assertEqual("bounded_daily_calculation_v1",d["scope"])
        m=run_ziwei_dynamic_v6_transport(p6("monthly",{
            "input_type":"normalized_lunar_month","lunar_year":2026,"lunar_month":9,"lunar_day":5,
            "is_leap_month":False,"calendar_provenance":"synthetic:target"
        }))
        self.assertEqual("bounded_monthly_calculation_v1",m["scope"])
        y=run_ziwei_dynamic_v6_transport(p6("yearly",{"input_type":"lunar_year","lunar_year":2026}))
        self.assertEqual("bounded_yearly_calculation_v1",y["scope"])
        dec=run_ziwei_dynamic_v6_transport(p6("decadal",{"input_type":"lunar_year","lunar_year":2026}))
        self.assertEqual("bounded_decadal_calculation_v1",dec["scope"])

    def test_v5_remains_daily_max_and_v6_rejects_bad_rat_policy(self):
        old={
            "schema_name":"ziwei_dynamic_request","schema_version":"5.0.0","request_id":"old",
            "temporal_scope":"hourly","birth":birth(),"gender":"male",
            "target":{"input_type":"normalized_lunar_day","lunar_year":2026,"lunar_month":9,"lunar_day":5,
                      "is_leap_month":False,"calendar_provenance":"synthetic:target"},
            "requested_subjects":[],"enabled_source_ids":[]
        }
        with self.assertRaises(ValueError):
            run_ziwei_dynamic_v5_transport(old)
        bad=p6("hourly",{
            "input_type":"normalized_lunar_hour","lunar_year":2026,"lunar_month":9,"lunar_day":5,
            "is_leap_month":False,"hour_branch":"子","rat_hour_policy":"current_day_until_midnight",
            "calendar_provenance":"synthetic:target"
        })
        with self.assertRaises(ValueError):
            run_ziwei_dynamic_v6_transport(bad)

    def test_hourly_target_requires_hour_identity_and_provenance(self):
        wrong=p6("hourly",{
            "input_type":"normalized_lunar_day","lunar_year":2026,"lunar_month":9,"lunar_day":5,
            "is_leap_month":False,"hour_branch":"午","rat_hour_policy":"next_day_at_23",
            "calendar_provenance":"synthetic:target"
        })
        with self.assertRaises(ValueError):
            run_ziwei_dynamic_v6_transport(wrong)
        missing=p6("hourly",{
            "input_type":"normalized_lunar_hour","lunar_year":2026,"lunar_month":9,"lunar_day":5,
            "is_leap_month":False,"hour_branch":"午","rat_hour_policy":"next_day_at_23"
        })
        with self.assertRaises(ValueError):
            run_ziwei_dynamic_v6_transport(missing)

if __name__=="__main__":
    unittest.main()
