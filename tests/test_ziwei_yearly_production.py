import json
import unittest
from pathlib import Path
from tools.ziwei_runtime import run_ziwei_dynamic_transport, run_ziwei_dynamic_v3_transport

ROOT=Path(__file__).resolve().parents[1]

def payload(version,scope):
    return {
      "schema_name":"ziwei_dynamic_request","schema_version":version,"request_id":"y1","temporal_scope":scope,
      "birth":{"input_type":"normalized_lunar","lunar_year":1987,"lunar_month":5,"lunar_day":20,"hour_branch":"酉","calendar_provenance":"synthetic","leap_month_identity":"normalized_upstream"},
      "gender":"male","target_lunar_year":2026,"requested_subjects":[],"enabled_source_ids":[]
    }

class ZiWeiYearlyProductionTests(unittest.TestCase):
    def test_yearly_admission_is_calculation_only(self):
        a=json.loads((ROOT/"ZIWEI_YEARLY_ADMISSION_V1.json").read_text(encoding="utf-8"))
        self.assertEqual("PRODUCTION_ADMITTED_CALCULATION_ONLY",a["status"])
        self.assertEqual("yearly.year_branch_common_v1",a["profile"]["profile_id"])
        self.assertEqual("decadal",a["parent_scope"]["required"])
        self.assertFalse(a["ordinary_auto_routing"])

    def test_v3_yearly_runs_and_v3_decadal_remains_available(self):
        y=run_ziwei_dynamic_v3_transport(payload("3.0.0","yearly"))
        self.assertEqual("bounded_yearly_calculation_v1",y["scope"])
        self.assertEqual("yearly",y["runtime"]["temporal_scope"])
        self.assertEqual("NOT_ADMITTED",y["interpretation"]["status"])
        d=run_ziwei_dynamic_v3_transport(payload("3.0.0","decadal"))
        self.assertEqual("bounded_decadal_calculation_v1",d["scope"])

    def test_v2_remains_decadal_only_and_v3_rejects_monthly(self):
        with self.assertRaises(ValueError):
            run_ziwei_dynamic_transport(payload("2.0.0","yearly"))
        with self.assertRaises(ValueError):
            run_ziwei_dynamic_v3_transport(payload("3.0.0","monthly"))

if __name__=="__main__":
    unittest.main()
