from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
import unittest

from tools.ziwei_claim_retrieval import SPECIFICITY
from tools.ziwei_natal_provider import BRANCHES, NormalizedNatalInput, calculate_scope_a_natal
from tools.ziwei_runtime import ZiWeiReadingRequest, run_ziwei

ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/"references"/"ziwei"/"ziwei_interpretation_claim_registry_same_palace_pairs_v1.json"
VALIDATOR=ROOT/"references"/"ziwei"/"validate_interpretation_claim_registry.py"
ADMISSION=ROOT/"ZIWEI_SAME_PALACE_PAIR_ADMISSION_V1.json"

PAIR_IDS={
    "兄弟宮":"ZW-PAIR-WUQU-TIANXIANG-SIBLINGS-001",
    "官祿宮":"ZW-PAIR-WUQU-TIANXIANG-CAREER-001",
}

class ZiWeiSamePalacePairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry=json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_registry_validates_as_sparse_pair_family(self):
        p=subprocess.run([sys.executable,str(VALIDATOR),str(REGISTRY)],cwd=ROOT,text=True,capture_output=True)
        self.assertEqual(0,p.returncode,msg=p.stdout+"\n"+p.stderr)
        self.assertFalse(self.registry["production_routable"])
        self.assertEqual(2,len(self.registry["claims"]))
        self.assertEqual(1,self.registry["research_result"]["pair_count"])
        self.assertFalse(self.registry["research_result"]["exhaustive_pair_dictionary"])
        self.assertFalse(self.registry["research_result"]["cartesian_expansion"])
        self.assertEqual(
            {("武曲","天相")},
            {tuple(claim["pair_members"]) for claim in self.registry["claims"]},
        )

    def test_pair_claims_require_exact_canonical_occupancy_facts(self):
        for claim in self.registry["claims"]:
            palace=claim["applicability"]["palace_scope"][0]
            requires=set(claim["applicability"]["requires"])
            self.assertIn("fact_available:palace_occupancy",requires)
            self.assertIn(f"star_in_palace:武曲:{palace}",requires)
            self.assertIn(f"star_in_palace:天相:{palace}",requires)
            self.assertEqual({"武曲","天相"},set(claim["pair_members"]))
            self.assertTrue({"武曲","天相",palace}.issubset(set(claim["subjects"])))

    def _find_pair_birth(self,palace):
        for year in (1984,1985,1986,1987,1988):
            for month in range(1,13):
                for day in range(1,31):
                    for hour in BRANCHES:
                        birth=NormalizedNatalInput(year,month,day,hour,"synthetic:same-palace-search")
                        chart=calculate_scope_a_natal(birth)
                        stars=set(chart["palace_occupancy"][palace]["major_stars"])
                        if {"武曲","天相"}.issubset(stars):
                            return birth
        self.fail(f"no deterministic 武曲×天相 fixture found for {palace}")

    def test_each_admitted_palace_claim_activates_only_on_exact_pair(self):
        for palace,claim_id in PAIR_IDS.items():
            with self.subTest(palace=palace):
                birth=self._find_pair_birth(palace)
                r=run_ziwei(ZiWeiReadingRequest(
                    request_id=f"pair-{palace}",
                    birth=birth,
                    requested_subjects=(palace,),
                ))
                ids=r["interpretation"]["selected_claim_ids"]
                self.assertIn(claim_id,ids)
                selected={x["claim_id"]:x for x in r["interpretation"]["selected_claims"]}
                self.assertEqual("same_palace_pair",selected[claim_id]["claim_type"])
                self.assertEqual(["武曲","天相"],selected[claim_id]["pair_members"])
                self.assertGreater(
                    selected[claim_id]["specificity"],
                    SPECIFICITY["star_core"],
                )

    def test_requested_star_can_retrieve_matching_pair_claim(self):
        birth=self._find_pair_birth("兄弟宮")
        r=run_ziwei(ZiWeiReadingRequest(
            request_id="pair-star-subject",
            birth=birth,
            requested_subjects=("武曲",),
        ))
        self.assertIn(PAIR_IDS["兄弟宮"],r["interpretation"]["selected_claim_ids"])

    def test_unmatched_chart_does_not_select_pair_claims(self):
        birth=NormalizedNatalInput(1987,5,20,"酉","synthetic:pair-unmatched")
        chart=calculate_scope_a_natal(birth)
        for palace in PAIR_IDS:
            stars=set(chart["palace_occupancy"][palace]["major_stars"])
            if {"武曲","天相"}.issubset(stars):
                self.skipTest("chosen baseline unexpectedly matches admitted pair")
        r=run_ziwei(ZiWeiReadingRequest(request_id="pair-unmatched",birth=birth))
        self.assertTrue(set(PAIR_IDS.values()).isdisjoint(r["interpretation"]["selected_claim_ids"]))

    def test_admission_is_exactly_two_practitioner_bounded_claims(self):
        m=json.loads(ADMISSION.read_text(encoding="utf-8"))
        self.assertEqual("PRODUCTION_ADMITTED_BOUNDED_INTERPRETATION",m["status"])
        self.assertEqual(2,m["scope"]["admitted_claims_added"])
        self.assertEqual(1,m["scope"]["admitted_pair_count"])
        self.assertFalse(m["scope"]["exhaustive_pair_dictionary"])
        self.assertFalse(m["scope"]["cartesian_expansion"])
        self.assertFalse(m["scientific_predictive_validity_claimed"])

if __name__=="__main__":
    unittest.main()
