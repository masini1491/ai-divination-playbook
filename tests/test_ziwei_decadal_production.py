from __future__ import annotations
import json
import unittest
from pathlib import Path

from tools.ziwei_natal_provider import NormalizedNatalInput
from tools.ziwei_runtime import (
    ZiWeiDecadalRequest,
    request_from_transport,
    run_ziwei_decadal,
    run_ziwei_dynamic_transport,
)

ROOT=Path(__file__).resolve().parents[1]

class ZiWeiDecadalProductionTests(unittest.TestCase):
    def test_admission_is_calculation_only_and_profile_bound(self):
        a=json.loads((ROOT/"ZIWEI_DECADAL_ADMISSION_V1.json").read_text(encoding="utf-8"))
        self.assertEqual("PRODUCTION_ADMITTED_CALCULATION_ONLY",a["status"])
        self.assertEqual("decadal.quanji_common_v1",a["profile"]["profile_id"])
        self.assertEqual("traditional_nominal_age",a["profile"]["rules"]["age_basis"])
        self.assertFalse(a["ordinary_auto_routing"])
        self.assertIn("yearly",a["unsupported"])
        self.assertIn("no dynamic interpretation without separate ZW-P1-040 admission",a["fail_closed"])

    def test_typed_runtime_returns_calculation_without_interpretation(self):
        r=run_ziwei_decadal(ZiWeiDecadalRequest(
            request_id="d1",
            birth=NormalizedNatalInput(1987,5,20,"酉","synthetic:decadal"),
            gender="male",
            target_lunar_year=2026,
        ))
        self.assertEqual("PRODUCTION_ADMITTED_CALCULATION_ONLY",r["status"])
        self.assertEqual("bounded_decadal_calculation_v1",r["scope"])
        self.assertEqual("decadal",r["runtime"]["temporal_scope"])
        self.assertTrue(r["authority"]["calculation_authority_granted"])
        self.assertFalse(r["authority"]["interpretation_authority_granted"])
        self.assertEqual("NOT_ADMITTED",r["interpretation"]["status"])
        self.assertEqual(3,r["calculation"]["decadal"]["index"])

    def test_v2_transport_is_closed_world_and_rejects_yearly(self):
        p={
            "schema_name":"ziwei_dynamic_request","schema_version":"2.0.0",
            "request_id":"d2","temporal_scope":"decadal",
            "birth":{
                "input_type":"normalized_lunar","lunar_year":1987,"lunar_month":5,"lunar_day":20,
                "hour_branch":"酉","calendar_provenance":"synthetic","leap_month_identity":"normalized_upstream"
            },
            "gender":"male","target_lunar_year":2026,
            "requested_subjects":[],"enabled_source_ids":[]
        }
        r=run_ziwei_dynamic_transport(p)
        self.assertEqual("PRODUCTION_ADMITTED_CALCULATION_ONLY",r["status"])
        p2=dict(p); p2["temporal_scope"]="yearly"
        with self.assertRaises(ValueError):
            run_ziwei_dynamic_transport(p2)
        p3=dict(p); del p3["gender"]
        with self.assertRaises(ValueError):
            run_ziwei_dynamic_transport(p3)

    def test_v1_natal_transport_remains_natal_only(self):
        p={
            "schema_name":"ziwei_reading_request","schema_version":"1.0.0",
            "request_id":"v1","temporal_scope":"decadal",
            "birth":{
                "input_type":"normalized_lunar","lunar_year":1987,"lunar_month":5,"lunar_day":20,
                "hour_branch":"酉","calendar_provenance":"synthetic","leap_month_identity":"normalized_upstream"
            },
            "optional_modules":[],"requested_subjects":[],"enabled_source_ids":[]
        }
        with self.assertRaises(ValueError):
            request_from_transport(p)

    def test_root_admission_registers_separate_dynamic_runtime(self):
        a=json.loads((ROOT/"ZIWEI_PRODUCTION_ADMISSION_V1.json").read_text(encoding="utf-8"))
        d=a["separate_temporal_calculation_admissions"][0]
        self.assertEqual("decadal",d["temporal_scope"])
        self.assertFalse(d["interpretation_admitted"])
        self.assertNotIn("decadal",a["unsupported_scopes"])
        self.assertIn("yearly",a["unsupported_scopes"])

if __name__=="__main__":
    unittest.main()
