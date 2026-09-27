from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
import unittest

from tools.ziwei_claim_retrieval import SPECIFICITY
from tools.ziwei_natal_provider import BRANCHES, PALACES, NormalizedNatalInput, calculate_scope_a_natal
from tools.ziwei_runtime import ZiWeiReadingRequest, run_ziwei

ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/"references"/"ziwei"/"ziwei_interpretation_claim_registry_body_palace_overlay_v1.json"
VALIDATOR=ROOT/"references"/"ziwei"/"validate_interpretation_claim_registry.py"
ADMISSION=ROOT/"ZIWEI_BODY_PALACE_OVERLAY_ADMISSION_V1.json"

OVERLAY_IDS={
    "夫妻宮":"ZW-BODY-SPOUSE-001",
    "財帛宮":"ZW-BODY-WEALTH-001",
    "官祿宮":"ZW-BODY-CAREER-001",
    "遷移宮":"ZW-BODY-MOBILITY-001",
}

class ZiWeiBodyPalaceOverlayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry=json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_registry_validates_and_remains_sparse(self):
        p=subprocess.run([sys.executable,str(VALIDATOR),str(REGISTRY)],cwd=ROOT,text=True,capture_output=True)
        self.assertEqual(0,p.returncode,msg=p.stdout+"\n"+p.stderr)
        self.assertFalse(self.registry["production_routable"])
        self.assertEqual(5,len(self.registry["claims"]))
        self.assertEqual(4,self.registry["research_result"]["overlay_claim_count"])
        self.assertFalse(self.registry["research_result"]["exhaustive_overlay_dictionary"])

    def test_provider_projects_body_branch_onto_existing_palace_only(self):
        chart=calculate_scope_a_natal(NormalizedNatalInput(1987,5,20,"酉","synthetic:body-overlay"))
        self.assertEqual("卯",chart["body_palace"]["branch"])
        self.assertEqual("遷移宮",chart["body_palace"]["overlay_palace"])
        self.assertEqual("overlay_not_thirteenth_palace",chart["body_palace"]["policy"])
        self.assertIn(chart["body_palace"]["overlay_palace"],PALACES)
        self.assertNotIn("身宮",{x["palace"] for x in chart["palaces"]})
        self.assertEqual(12,len(chart["palaces"]))
        facts=set(chart["retrieval_facts"])
        self.assertIn("fact_available:body_palace_overlay",facts)
        self.assertIn("body_palace_overlay:遷移宮",facts)

    def _find_overlay_birth(self,palace):
        for month in range(1,13):
            for hour in BRANCHES:
                birth=NormalizedNatalInput(1987,month,15,hour,"synthetic:body-overlay-search")
                chart=calculate_scope_a_natal(birth)
                if chart["body_palace"]["overlay_palace"]==palace:
                    return birth
        self.fail(f"no deterministic body-palace overlay fixture found for {palace}")

    def test_each_admitted_overlay_claim_activates_on_exact_fact(self):
        for palace,claim_id in OVERLAY_IDS.items():
            with self.subTest(palace=palace):
                birth=self._find_overlay_birth(palace)
                r=run_ziwei(ZiWeiReadingRequest(
                    request_id=f"body-{palace}",
                    birth=birth,
                    requested_subjects=(palace,),
                ))
                self.assertIn(claim_id,r["interpretation"]["selected_claim_ids"])
                selected={x["claim_id"]:x for x in r["interpretation"]["selected_claims"]}
                self.assertEqual("body_palace_overlay",selected[claim_id]["claim_type"])
                self.assertEqual(palace,selected[claim_id]["overlay_palace"])
                self.assertGreater(selected[claim_id]["specificity"],SPECIFICITY["star_core"])

    def test_body_subject_retrieves_methodology_and_exact_overlay(self):
        birth=self._find_overlay_birth("遷移宮")
        r=run_ziwei(ZiWeiReadingRequest(
            request_id="body-subject",
            birth=birth,
            requested_subjects=("身宮",),
        ))
        ids=set(r["interpretation"]["selected_claim_ids"])
        self.assertIn("ZW-BODY-METHOD-001",ids)
        self.assertIn("ZW-BODY-MOBILITY-001",ids)
        self.assertTrue(set(OVERLAY_IDS.values())-{OVERLAY_IDS["遷移宮"]} > set())

    def test_unadmitted_overlay_context_has_methodology_but_no_overlay_filler(self):
        admitted=set(OVERLAY_IDS)
        candidate=None
        for month in range(1,13):
            for hour in BRANCHES:
                birth=NormalizedNatalInput(1987,month,15,hour,"synthetic:body-overlay-unadmitted")
                palace=calculate_scope_a_natal(birth)["body_palace"]["overlay_palace"]
                if palace not in admitted:
                    candidate=(birth,palace)
                    break
            if candidate:
                break
        self.assertIsNotNone(candidate)
        birth,palace=candidate
        r=run_ziwei(ZiWeiReadingRequest(
            request_id="body-unadmitted",
            birth=birth,
            requested_subjects=("身宮",),
        ))
        ids=set(r["interpretation"]["selected_claim_ids"])
        self.assertIn("ZW-BODY-METHOD-001",ids)
        self.assertTrue(set(OVERLAY_IDS.values()).isdisjoint(ids))

    def test_admission_is_overlay_not_thirteenth_palace(self):
        m=json.loads(ADMISSION.read_text(encoding="utf-8"))
        self.assertEqual("PRODUCTION_ADMITTED_BOUNDED_INTERPRETATION",m["status"])
        self.assertEqual(5,m["scope"]["admitted_claims_added"])
        self.assertEqual(4,m["scope"]["overlay_claims"])
        self.assertEqual("overlay_not_thirteenth_palace",m["scope"]["body_palace_policy"])
        self.assertFalse(m["scope"]["exhaustive_overlay_dictionary"])
        self.assertFalse(m["deterministic_applicability"]["thirteenth_palace_created"])
        self.assertFalse(m["scientific_predictive_validity_claimed"])

if __name__=="__main__":
    unittest.main()
