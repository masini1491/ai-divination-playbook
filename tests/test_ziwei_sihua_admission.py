from __future__ import annotations
import json
from pathlib import Path
import unittest

from tools.ziwei_natal_provider import BRANCHES, NormalizedNatalInput, calculate_scope_a_natal
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

    def test_manifest_admits_exact_three_source_explicit_claims(self):
        m=json.loads((ROOT/"ZIWEI_SIHUA_ADMISSION_V1.json").read_text(encoding="utf-8"))
        self.assertEqual("PRODUCTION_ADMITTED_OPTIONAL_MODULE",m["status"])
        self.assertEqual(SIHUA_MODULE,m["module_id"])
        self.assertEqual(SIHUA_PROFILE_ID,m["profile_id"])
        self.assertEqual(3,m["scope"]["admitted_claims_added"])
        self.assertTrue(m["scope"]["transformed_star_interpretation_admitted"])
        self.assertTrue(m["interpretation"]["new_claim_corpus"])
        self.assertEqual(
            "three_source_explicit_fact_gated_transformed_star_conditionals",
            m["interpretation"]["claim_scope"],
        )
        self.assertFalse(m["interpretation"]["generic_transform_outcome_dictionary"])
        self.assertFalse(m["interpretation"]["cross_profile_averaging"])

    def test_runtime_emits_profile_bound_sihua_and_no_unmatched_claim_widening(self):
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
        self.assertTrue(result["authority"]["sihua_transformed_star_claims_admitted"])
        self.assertFalse(result["authority"]["generic_sihua_outcome_doctrine_admitted"])
        self.assertEqual(
            base["interpretation"]["selected_claim_ids"],
            result["interpretation"]["selected_claim_ids"],
        )

    def _find_tanlang_four_grave_birth(self):
        targets={"辰","戌","丑","未"}
        for month in range(1,13):
            for day in range(1,31):
                for hour_branch in BRANCHES:
                    birth=NormalizedNatalInput(
                        1988,month,day,hour_branch,
                        "synthetic:sihua-activation-search",
                    )
                    chart=calculate_scope_a_natal(birth)
                    self.assertEqual("戊",chart["year_pillar"]["stem"])
                    if chart["major_star_placements"]["貪狼"] in targets:
                        return birth,chart["major_star_placements"]["貪狼"]
        self.fail("no deterministic 貪狼四墓 fixture found")

    def test_source_explicit_tanlang_claim_activates_only_with_exact_facts(self):
        birth,branch=self._find_tanlang_four_grave_birth()
        result=run_ziwei(ZiWeiReadingRequest(
            request_id="sihua-tanlang-active",
            birth=birth,
            requested_subjects=("貪狼",),
            optional_modules=(SIHUA_MODULE,),
            sihua_profile=SIHUA_PROFILE_ID,
        ))
        self.assertIn(branch,{"辰","戌","丑","未"})
        self.assertEqual("貪狼",result["calculation"]["sihua"]["by_transform"]["祿"])
        self.assertIn(
            "ZW-SIHUA-TANLANG-LU-001",
            result["interpretation"]["selected_claim_ids"],
        )
        selected={
            x["claim_id"]:x
            for x in result["interpretation"]["selected_claims"]
        }
        claim=selected["ZW-SIHUA-TANLANG-LU-001"]
        self.assertEqual("貪狼",claim["subject"])
        self.assertEqual("historical_conditional",claim["assertion_class"])

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

    def test_root_admission_counts_only_exact_bounded_claims(self):
        m=json.loads((ROOT/"ZIWEI_PRODUCTION_ADMISSION_V1.json").read_text(encoding="utf-8"))
        self.assertEqual(52,m["scope"]["admitted_claims"])
        self.assertEqual(59,m["scope"]["maximum_admitted_claims_with_optional_modules"])
        self.assertEqual(3,m["scope"]["optional_sihua_claims"])
        self.assertIn(SIHUA_MODULE,m["runtime"]["optional_modules"])
        entry=next(x for x in m["optional_module_admissions"] if x["module_id"]==SIHUA_MODULE)
        self.assertEqual(3,entry["admitted_claims_added"])
        self.assertEqual(
            ["ziwei_interpretation_claim_registry_sihua_v0.json"],
            entry["admitted_research_registries"],
        )
        self.assertTrue(entry["transformed_star_interpretation_admitted"])

if __name__=="__main__":
    unittest.main()
