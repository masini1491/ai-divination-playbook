from __future__ import annotations
import json
from pathlib import Path
import unittest

from tools.ziwei_natal_provider import NormalizedNatalInput
from tools.ziwei_runtime import (
    SIHUA_MODULE,
    ZiWeiReadingRequest,
    request_from_transport,
    request_to_transport,
    run_ziwei,
)
from tools.ziwei_sihua_provider import PROFILE_ID as SIHUA_PROFILE_ID

ROOT=Path(__file__).resolve().parents[1]

class ZiWeiSihuaAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.birth=NormalizedNatalInput(1987,5,20,"酉","synthetic:sihua-admission")

    def test_manifest_admits_facts_only_zero_claim_module(self):
        m=json.loads((ROOT/"ZIWEI_SIHUA_ADMISSION_V1.json").read_text(encoding="utf-8"))
        self.assertEqual("PRODUCTION_ADMITTED_OPTIONAL_MODULE",m["status"])
        self.assertEqual(SIHUA_MODULE,m["module_id"])
        self.assertEqual(SIHUA_PROFILE_ID,m["profile_id"])
        self.assertEqual(0,m["scope"]["admitted_claims_added"])
        self.assertFalse(m["scope"]["transformed_star_interpretation_admitted"])
        self.assertTrue(m["interpretation"]["facts_only"])
        self.assertFalse(m["interpretation"]["generic_transform_outcome_dictionary"])
        self.assertFalse(m["interpretation"]["cross_profile_averaging"])

    def test_runtime_emits_profile_bound_sihua_facts_without_new_claims(self):
        base=run_ziwei(ZiWeiReadingRequest(
            request_id="sihua-base",birth=self.birth,requested_subjects=("紫微",)
        ))
        result=run_ziwei(ZiWeiReadingRequest(
            request_id="sihua-on",birth=self.birth,requested_subjects=("紫微",),
            optional_modules=(SIHUA_MODULE,),sihua_profile=SIHUA_PROFILE_ID,
        ))
        self.assertEqual([SIHUA_MODULE],result["runtime"]["optional_modules"])
        sihua=result["calculation"]["sihua"]
        self.assertEqual("丁",sihua["year_stem"])
        self.assertEqual(
            {"祿":"太陰","權":"天同","科":"天機","忌":"巨門"},
            sihua["by_transform"],
        )
        self.assertEqual(
            "computed_by_optional_sihua_profile",
            result["calculation"]["unsupported"]["four_transformations"],
        )
        self.assertTrue(result["authority"]["sihua_profile_admitted"])
        self.assertFalse(result["authority"]["sihua_transformed_star_claims_admitted"])
        self.assertFalse(result["authority"]["generic_sihua_outcome_doctrine_admitted"])
        self.assertEqual(
            base["interpretation"]["selected_claim_ids"],
            result["interpretation"]["selected_claim_ids"],
        )

    def test_transport_round_trip_preserves_profile_selector(self):
        request=ZiWeiReadingRequest(
            request_id="sihua-transport",birth=self.birth,
            optional_modules=(SIHUA_MODULE,),sihua_profile=SIHUA_PROFILE_ID,
        )
        payload=request_to_transport(request)
        self.assertEqual(SIHUA_PROFILE_ID,payload["sihua_profile"])
        self.assertEqual(request,request_from_transport(payload))

    def test_unknown_profile_and_profile_without_module_fail_closed(self):
        with self.assertRaisesRegex(ValueError,"unsupported sihua_profile"):
            run_ziwei(ZiWeiReadingRequest(
                request_id="bad-sihua",birth=self.birth,
                optional_modules=(SIHUA_MODULE,),sihua_profile="sihua.other",
            ))
        with self.assertRaisesRegex(ValueError,"sihua_profile requires sihua_v1"):
            run_ziwei(ZiWeiReadingRequest(
                request_id="bad-selector",birth=self.birth,sihua_profile=SIHUA_PROFILE_ID,
            ))

    def test_root_admission_keeps_claim_counts_unchanged(self):
        m=json.loads((ROOT/"ZIWEI_PRODUCTION_ADMISSION_V1.json").read_text(encoding="utf-8"))
        self.assertEqual(52,m["scope"]["admitted_claims"])
        self.assertEqual(56,m["scope"]["maximum_admitted_claims_with_optional_modules"])
        self.assertIn(SIHUA_MODULE,m["runtime"]["optional_modules"])
        entry=next(x for x in m["optional_module_admissions"] if x["module_id"]==SIHUA_MODULE)
        self.assertEqual(0,entry["admitted_claims_added"])
        self.assertFalse(entry["transformed_star_interpretation_admitted"])

if __name__=="__main__":
    unittest.main()
