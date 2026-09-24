from __future__ import annotations
import unittest
from tools.ziwei_natal_provider import NormalizedNatalInput, calculate_scope_a_natal
from tools.ziwei_m0_auxiliary_provider import PROFILE_ID, calculate_m0_auxiliary
from tools.ziwei_runtime import M0_MODULE, ZiWeiReadingRequest, request_from_transport, request_to_transport, run_ziwei
class ZiWeiM0AuxiliaryV1Tests(unittest.TestCase):
    def natal(self,month=1,hour="子"): return NormalizedNatalInput(2000,month,1,hour,"synthetic:m0")
    def test_exact_placement_rules(self):
        n=self.natal(); m=calculate_m0_auxiliary(n,calculate_scope_a_natal(n)["major_star_placements"])
        self.assertEqual(PROFILE_ID,m["profile"]["profile_id"]); self.assertEqual({"左輔":"辰","右弼":"戌","文昌":"戌","文曲":"辰"},m["placements"])
        n=self.natal(12,"午"); m=calculate_m0_auxiliary(n,calculate_scope_a_natal(n)["major_star_placements"])
        self.assertEqual({"左輔":"卯","右弼":"亥","文昌":"辰","文曲":"戌"},m["placements"])
    def test_all_month_and_hour_placement_rules(self):
        branches=("子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥")
        for month in range(1,13):
            n=self.natal(month,"子")
            m=calculate_m0_auxiliary(n,calculate_scope_a_natal(n)["major_star_placements"])
            self.assertEqual(branches[(4+month-1)%12],m["placements"]["左輔"])
            self.assertEqual(branches[(10-(month-1))%12],m["placements"]["右弼"])
        for hour_index,hour in enumerate(branches):
            n=self.natal(1,hour)
            m=calculate_m0_auxiliary(n,calculate_scope_a_natal(n)["major_star_placements"])
            self.assertEqual(branches[(10-hour_index)%12],m["placements"]["文昌"])
            self.assertEqual(branches[(4+hour_index)%12],m["placements"]["文曲"])
    def test_module_is_optional_and_bounded(self):
        base=run_ziwei(ZiWeiReadingRequest(request_id="base",birth=self.natal()))
        m0=run_ziwei(ZiWeiReadingRequest(request_id="m0",birth=self.natal(),optional_modules=(M0_MODULE,),m0_auxiliary_profile=PROFILE_ID))
        self.assertNotIn("m0_auxiliary",base["calculation"]); self.assertEqual("not_computed",base["calculation"]["unsupported"]["auxiliary_stars"])
        self.assertEqual("not_computed",m0["calculation"]["unsupported"]["auxiliary_stars"])
        self.assertEqual("computed_by_optional_m0_profile",m0["calculation"]["unsupported"]["m0_auxiliary_stars"])
        self.assertEqual({"左輔","右弼","文昌","文曲"},set(m0["calculation"]["m0_auxiliary"]["placements"]))
        facts=set(m0["calculation"]["m0_auxiliary"]["retrieval_facts"])
        self.assertIn("fact_available:m0_auxiliary_stars",facts)
        self.assertNotIn("fact_available:auxiliary_stars",facts)
        ids=set(m0["interpretation"]["selected_claim_ids"]); self.assertTrue({"ZW-M0-ZUOFU-CORE-001","ZW-M0-YOUBI-CORE-001","ZW-M0-WENCHANG-CORE-001","ZW-M0-WENQU-CORE-001"}.issubset(ids))
        self.assertFalse(any(x.startswith("ZW-M0-") for x in base["interpretation"]["selected_claim_ids"]))
        self.assertFalse(any(x["claim_id"].startswith("ZW-M0-") for x in base["interpretation"]["omissions"]))
        base_states={x["claim_id"]:x["state"] for x in base["interpretation"]["conditional_evaluations"]}
        m0_states={x["claim_id"]:x["state"] for x in m0["interpretation"]["conditional_evaluations"]}
        self.assertEqual("not_computed",base_states["ZW-B2-TIANXIANG-COND-002"])
        self.assertIn(m0_states["ZW-B2-TIANXIANG-COND-002"],{"satisfied","unsatisfied"})
        self.assertEqual("not_computed",m0_states["ZW-B1-ZIWEI-COND-002"])
    def test_brightness_and_m0_compose_without_domain_leakage(self):
        from tools.ziwei_runtime import BRIGHTNESS_MODULE
        req=ZiWeiReadingRequest(
            request_id="m0-brightness",birth=self.natal(),
            optional_modules=(BRIGHTNESS_MODULE,M0_MODULE),
            m0_auxiliary_profile=PROFILE_ID,
        )
        result=run_ziwei(req)
        self.assertIn("brightness",result["calculation"])
        self.assertIn("m0_auxiliary",result["calculation"])
        self.assertEqual("computed_by_optional_profile",result["calculation"]["unsupported"]["brightness"])
        self.assertEqual("not_computed",result["calculation"]["unsupported"]["auxiliary_stars"])
        self.assertEqual("computed_by_optional_m0_profile",result["calculation"]["unsupported"]["m0_auxiliary_stars"])
        self.assertTrue(result["authority"]["brightness_profile_admitted"])
        self.assertTrue(result["authority"]["m0_auxiliary_profile_admitted"])
        self.assertFalse(result["authority"]["blanket_minor_star_admission"])
    def test_baseline_transport_does_not_require_m0_profile(self):
        base=ZiWeiReadingRequest(request_id="base-t",birth=self.natal())
        self.assertEqual(base,request_from_transport(request_to_transport(base)))
    def test_transport_profile_binding_and_fail_closed(self):
        req=ZiWeiReadingRequest(request_id="m0-t",birth=self.natal(),optional_modules=(M0_MODULE,),m0_auxiliary_profile=PROFILE_ID)
        self.assertEqual(req,request_from_transport(request_to_transport(req)))
        with self.assertRaises(ValueError): run_ziwei(ZiWeiReadingRequest(request_id="bad",birth=self.natal(),optional_modules=(M0_MODULE,),m0_auxiliary_profile="unknown"))
        with self.assertRaises(ValueError): run_ziwei(ZiWeiReadingRequest(request_id="bad2",birth=self.natal(),m0_auxiliary_profile=PROFILE_ID))
if __name__=="__main__": unittest.main()
