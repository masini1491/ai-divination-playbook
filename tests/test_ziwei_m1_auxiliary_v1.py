from __future__ import annotations

import json
import unittest
from pathlib import Path

from tools.ziwei_m0_auxiliary_provider import PROFILE_ID as M0_PROFILE_ID
from tools.ziwei_m1_auxiliary_provider import PROFILE_ID, STARS, calculate_m1_auxiliary
from tools.ziwei_natal_provider import MAJOR_STARS, NormalizedNatalInput, calculate_scope_a_natal
from tools.ziwei_runtime import (
    M0_MODULE,
    M1_MODULE,
    ZiWeiReadingRequest,
    request_from_transport,
    request_to_transport,
    run_ziwei,
)

ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/"references"/"ziwei"/"ziwei_interpretation_claim_registry_m1_auxiliary_v1.json"
ADMISSION=ROOT/"ZIWEI_M1_AUXILIARY_ADMISSION_V1.json"

class ZiWeiM1AuxiliaryV1Tests(unittest.TestCase):
    def major(self):
        return {star:"子" for star in MAJOR_STARS}

    def natal(self):
        return NormalizedNatalInput(2000,1,1,"子","synthetic:m1")

    def test_reconciled_year_stem_tables(self):
        expected={
            "甲":("寅","卯","丑","未"),
            "乙":("卯","辰","子","申"),
            "丙":("巳","午","亥","酉"),
            "丁":("午","未","亥","酉"),
            "戊":("巳","午","丑","未"),
            "己":("午","未","子","申"),
            "庚":("申","酉","丑","未"),
            "辛":("酉","戌","午","寅"),
            "壬":("亥","子","卯","巳"),
            "癸":("子","丑","卯","巳"),
        }
        for stem,(lu,yang,kui,yue) in expected.items():
            with self.subTest(stem=stem):
                r=calculate_m1_auxiliary(stem,"子","子",self.major())
                self.assertEqual(lu,r["placements"]["祿存"])
                self.assertEqual(yang,r["placements"]["擎羊"])
                self.assertEqual(kui,r["placements"]["天魁"])
                self.assertEqual(yue,r["placements"]["天鉞"])

    def test_tuoluo_is_one_branch_behind_lucun(self):
        branches=("子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥")
        for stem in "甲乙丙丁戊己庚辛壬癸":
            r=calculate_m1_auxiliary(stem,"子","子",self.major())
            lu=branches.index(r["placements"]["祿存"])
            self.assertEqual(branches[(lu-1)%12],r["placements"]["陀羅"])

    def test_year_branch_and_hour_rule_families(self):
        ma={
            "寅":"申","午":"申","戌":"申",
            "申":"寅","子":"寅","辰":"寅",
            "巳":"亥","酉":"亥","丑":"亥",
            "亥":"巳","卯":"巳","未":"巳",
        }
        base={
            "寅":("丑","卯"),"午":("丑","卯"),"戌":("丑","卯"),
            "申":("寅","戌"),"子":("寅","戌"),"辰":("寅","戌"),
            "巳":("卯","戌"),"酉":("卯","戌"),"丑":("卯","戌"),
            "亥":("酉","戌"),"卯":("酉","戌"),"未":("酉","戌"),
        }
        branches=("子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥")
        for year_branch in branches:
            for hour_index,hour in enumerate(branches):
                r=calculate_m1_auxiliary("甲",year_branch,hour,self.major())
                self.assertEqual(ma[year_branch],r["placements"]["天馬"])
                huo,ling=base[year_branch]
                self.assertEqual(branches[(branches.index(huo)+hour_index)%12],r["placements"]["火星"])
                self.assertEqual(branches[(branches.index(ling)+hour_index)%12],r["placements"]["鈴星"])
                self.assertEqual(branches[(11-hour_index)%12],r["placements"]["地空"])
                self.assertEqual(branches[(11+hour_index)%12],r["placements"]["地劫"])

    def test_m1_requires_m0_and_completes_bounded_auxiliary_domain(self):
        with self.assertRaisesRegex(ValueError,"requires m0_auxiliary_v1"):
            run_ziwei(ZiWeiReadingRequest(
                request_id="m1-alone",
                birth=self.natal(),
                optional_modules=(M1_MODULE,),
                m1_auxiliary_profile=PROFILE_ID,
            ))
        result=run_ziwei(ZiWeiReadingRequest(
            request_id="m0-m1",
            birth=self.natal(),
            optional_modules=(M0_MODULE,M1_MODULE),
            m0_auxiliary_profile=M0_PROFILE_ID,
            m1_auxiliary_profile=PROFILE_ID,
        ))
        self.assertEqual(set(STARS),set(result["calculation"]["m1_auxiliary"]["placements"]))
        self.assertEqual("computed_by_admitted_m0_plus_m1_profiles",result["calculation"]["unsupported"]["auxiliary_stars"])
        facts=set(result["calculation"]["m1_auxiliary"]["retrieval_facts"])
        self.assertIn("fact_available:m1_auxiliary_stars",facts)
        self.assertTrue(result["authority"]["m1_auxiliary_profile_admitted"])
        self.assertTrue(result["authority"]["bounded_auxiliary_domain_complete"])
        ids=set(result["interpretation"]["selected_claim_ids"])
        self.assertTrue(all(f"ZW-M1-" in cid for cid in ids if cid.startswith("ZW-M1-")))
        self.assertEqual(10,len([cid for cid in ids if cid.startswith("ZW-M1-")]))

    def test_generic_conditionals_gain_availability_only_with_m0_plus_m1(self):
        m0=run_ziwei(ZiWeiReadingRequest(
            request_id="m0-only",birth=self.natal(),
            optional_modules=(M0_MODULE,),m0_auxiliary_profile=M0_PROFILE_ID,
        ))
        both=run_ziwei(ZiWeiReadingRequest(
            request_id="m0-m1",birth=self.natal(),
            optional_modules=(M0_MODULE,M1_MODULE),
            m0_auxiliary_profile=M0_PROFILE_ID,m1_auxiliary_profile=PROFILE_ID,
        ))
        m0_states={x["claim_id"]:x["state"] for x in m0["interpretation"]["conditional_evaluations"]}
        both_states={x["claim_id"]:x["state"] for x in both["interpretation"]["conditional_evaluations"]}
        self.assertEqual("not_computed",m0_states["ZW-B2-TIANFU-COND-002"])
        self.assertIn(both_states["ZW-B2-TIANFU-COND-002"],{"satisfied","unsatisfied"})
        self.assertEqual("not_computed",m0_states["ZW-B1-WUQU-COND-002"])
        self.assertNotEqual("not_computed",both_states["ZW-B1-WUQU-COND-002"])

    def test_transport_round_trip_and_dependency(self):
        req=ZiWeiReadingRequest(
            request_id="m1-t",birth=self.natal(),
            optional_modules=(M0_MODULE,M1_MODULE),
            m0_auxiliary_profile=M0_PROFILE_ID,m1_auxiliary_profile=PROFILE_ID,
        )
        self.assertEqual(req,request_from_transport(request_to_transport(req)))
        with self.assertRaises(ValueError):
            run_ziwei(ZiWeiReadingRequest(
                request_id="bad-profile",birth=self.natal(),
                optional_modules=(M0_MODULE,M1_MODULE),
                m1_auxiliary_profile="unknown",
            ))

    def test_registry_is_bounded_policy_not_high_stakes_doctrine(self):
        d=json.loads(REGISTRY.read_text(encoding="utf-8"))
        self.assertEqual(10,len(d["claims"]))
        self.assertFalse(d["production_routable"])
        self.assertFalse(d["research_result"]["historical_semantic_core_admitted"])
        self.assertFalse(d["research_result"]["blanket_minor_star_admission"])
        joined=" ".join(x["normalized_statement"] for x in d["claims"])
        for phrase in ("一定死亡","必死","必然官司","保證升遷","保證富裕"):
            self.assertNotIn(phrase,joined)

    def test_admission_is_natal_only_and_m0_dependent(self):
        d=json.loads(ADMISSION.read_text(encoding="utf-8"))
        self.assertEqual("PRODUCTION_ADMITTED_OPTIONAL_MODULE",d["status"])
        self.assertEqual(["m0_auxiliary_v1"],d["requires_modules"])
        self.assertEqual("natal_baseline",d["scope"]["temporal_scope"])
        self.assertEqual(10,len(d["scope"]["stars"]))
        self.assertFalse(d["scope"]["blanket_minor_star_admission"])
        self.assertFalse(d["scientific_predictive_validity_claimed"])

if __name__=="__main__":
    unittest.main()
