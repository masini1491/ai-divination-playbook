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
REGISTRY=ROOT/"references"/"ziwei"/"ziwei_interpretation_claim_registry_star_palace_context_v1.json"
VALIDATOR=ROOT/"references"/"ziwei"/"validate_interpretation_claim_registry.py"
ADMISSION=ROOT/"ZIWEI_STAR_PALACE_CONTEXT_ADMISSION_V1.json"

ADMITTED={
    ("天相","命宮"):"ZW-SP-TIANXIANG-MING-001",
    ("天梁","官祿宮"):"ZW-SP-TIANLIANG-CAREER-001",
    ("貪狼","夫妻宮"):"ZW-SP-TANLANG-SPOUSE-001",
    ("破軍","遷移宮"):"ZW-SP-POJUN-TRAVEL-001",
    ("武曲","田宅宮"):"ZW-SP-WUQU-PROPERTY-001",
    ("天機","田宅宮"):"ZW-SP-TIANJI-PROPERTY-001",
    ("破軍","夫妻宮"):"ZW-SP-POJUN-SPOUSE-001",
}

class ZiWeiStarPalaceContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry=json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_registry_validates_and_remains_sparse(self):
        p=subprocess.run([sys.executable,str(VALIDATOR),str(REGISTRY)],cwd=ROOT,text=True,capture_output=True)
        self.assertEqual(0,p.returncode,msg=p.stdout+"\n"+p.stderr)
        self.assertFalse(self.registry["production_routable"])
        self.assertEqual(7,len(self.registry["claims"]))
        self.assertEqual(
            {"天相×命宮","天梁×官祿宮","貪狼×夫妻宮","破軍×遷移宮","武曲×田宅宮","天機×田宅宮","破軍×夫妻宮"},
            set(self.registry["research_result"]["admitted_pairs"]),
        )
        self.assertFalse(self.registry["research_result"]["exhaustive_cartesian_dictionary"])

    def _find_star_in_palace_birth(self,star,palace):
        for year in range(1984,1991):
            for month in range(1,13):
                for hour in BRANCHES:
                    birth=NormalizedNatalInput(year,month,15,hour,"synthetic:star-palace-search")
                    chart=calculate_scope_a_natal(birth)
                    if star in chart["palace_occupancy"][palace]["major_stars"]:
                        return birth
        self.fail(f"no deterministic fixture found for {star}×{palace}")

    def test_each_admitted_context_activates_only_on_exact_occupancy(self):
        for (star,palace),claim_id in ADMITTED.items():
            with self.subTest(star=star,palace=palace):
                birth=self._find_star_in_palace_birth(star,palace)
                r=run_ziwei(ZiWeiReadingRequest(
                    request_id=f"sp-{star}-{palace}",
                    birth=birth,
                    requested_subjects=(star,palace),
                ))
                self.assertIn(claim_id,r["interpretation"]["selected_claim_ids"])
                selected={x["claim_id"]:x for x in r["interpretation"]["selected_claims"]}
                claim=selected[claim_id]
                self.assertEqual("star_palace_context",claim["claim_type"])
                self.assertEqual(star,claim["star"])
                self.assertEqual(palace,claim["palace"])
                self.assertGreater(claim["specificity"],SPECIFICITY["star_conditional"])
                facts=set(calculate_scope_a_natal(birth)["retrieval_facts"])
                self.assertIn("fact_available:palace_occupancy",facts)
                self.assertIn(f"star_in_palace:{star}:{palace}",facts)

    def test_tianxiang_ming_preserves_profile_conflict(self):
        birth=self._find_star_in_palace_birth("天相","命宮")
        r=run_ziwei(ZiWeiReadingRequest(
            request_id="sp-tianxiang-conflict",
            birth=birth,
            requested_subjects=("天相","命宮"),
        ))
        groups={x["conflict_group_id"]:x for x in r["interpretation"]["conflicts"]}
        self.assertIn("CG-SP-TIANXIANG-MING-AUTHORITY-001",groups)
        self.assertEqual(
            "PRESERVE_CONFLICT",
            groups["CG-SP-TIANXIANG-MING-AUTHORITY-001"]["resolution_status"],
        )
        self.assertIn("PRESENT_CONFLICT_SEPARATELY",r["delivery"]["actions"])

    def test_tanlang_spouse_is_historical_bounded_without_spouse_age(self):
        claim=next(x for x in self.registry["claims"] if x["claim_id"]=="ZW-SP-TANLANG-SPOUSE-001")
        self.assertEqual("historical_conditional",claim["assertion_class"])
        self.assertEqual("historical_only",claim["support_status"])
        self.assertIn("star_in_palace:貪狼:夫妻宮",claim["applicability"]["requires"])
        self.assertNotIn("年長",claim["normalized_statement"])
        self.assertNotIn("older",claim["normalized_statement"].lower())

    def test_pojun_travel_is_historical_bounded_and_event_safe(self):
        claim=next(x for x in self.registry["claims"] if x["claim_id"]=="ZW-SP-POJUN-TRAVEL-001")
        self.assertEqual("historical_conditional",claim["assertion_class"])
        self.assertEqual("historical_only",claim["support_status"])
        self.assertIn("SRC-NANYANG-QUANSHU-PALACES",claim["source_refs"])
        self.assertIn("star_in_palace:破軍:遷移宮",claim["applicability"]["requires"])
        self.assertIn("dignity_brightness",claim["applicability"]["modifiers"])
        self.assertIn("不得",claim["normalized_statement"])

    def test_wuqu_property_is_historical_bounded_and_outcome_safe(self):
        claim=next(x for x in self.registry["claims"] if x["claim_id"]=="ZW-SP-WUQU-PROPERTY-001")
        self.assertEqual("historical_conditional",claim["assertion_class"])
        self.assertEqual("historical_only",claim["support_status"])
        self.assertIn("SRC-NANYANG-QUANSHU-PALACES",claim["source_refs"])
        self.assertIn("star_in_palace:武曲:田宅宮",claim["applicability"]["requires"])
        self.assertIn("dignity_brightness",claim["applicability"]["modifiers"])
        self.assertIn("不得",claim["normalized_statement"])

    def test_tianji_property_is_historical_bounded_and_outcome_safe(self):
        claim=next(x for x in self.registry["claims"] if x["claim_id"]=="ZW-SP-TIANJI-PROPERTY-001")
        self.assertEqual("historical_conditional",claim["assertion_class"])
        self.assertEqual("historical_only",claim["support_status"])
        self.assertIn("SRC-NANYANG-QUANSHU-PALACES",claim["source_refs"])
        self.assertIn("star_in_palace:天機:田宅宮",claim["applicability"]["requires"])
        self.assertIn("dignity_brightness",claim["applicability"]["modifiers"])
        self.assertIn("不得",claim["normalized_statement"])

    def test_pojun_spouse_is_historical_bounded_and_relationship_safe(self):
        claim=next(x for x in self.registry["claims"] if x["claim_id"]=="ZW-SP-POJUN-SPOUSE-001")
        self.assertEqual("historical_conditional",claim["assertion_class"])
        self.assertEqual("historical_only",claim["support_status"])
        self.assertEqual(["SRC-NANYANG-QUANSHU-PALACES"],claim["source_refs"])
        self.assertIn("star_in_palace:破軍:夫妻宮",claim["applicability"]["requires"])
        self.assertIn("dignity_brightness",claim["applicability"]["modifiers"])
        self.assertIn("不得",claim["normalized_statement"])
        self.assertIn("guaranteed relationship event",claim["normalized_statement"])

    def test_reviewed_non_material_sun_career_pair_has_no_context_override(self):
        birth=self._find_star_in_palace_birth("太陽","官祿宮")
        r=run_ziwei(ZiWeiReadingRequest(
            request_id="sp-no-filler",
            birth=birth,
            requested_subjects=("太陽","官祿宮"),
        ))
        self.assertFalse(any(
            x["claim_type"]=="star_palace_context"
            for x in r["interpretation"]["selected_claims"]
        ))

    def test_admission_is_bounded_not_cartesian(self):
        m=json.loads(ADMISSION.read_text(encoding="utf-8"))
        self.assertEqual("PRODUCTION_ADMITTED_BOUNDED_INTERPRETATION",m["status"])
        self.assertEqual(7,m["scope"]["admitted_claims_added"])
        self.assertEqual(["天相×命宮","天梁×官祿宮","貪狼×夫妻宮","破軍×遷移宮","武曲×田宅宮","天機×田宅宮","破軍×夫妻宮"],m["scope"]["admitted_pairs"])
        self.assertFalse(m["scope"]["exhaustive_cartesian_dictionary"])
        self.assertFalse(m["deterministic_applicability"]["new_geometry_provider_required"])
        self.assertFalse(m["scientific_predictive_validity_claimed"])

if __name__=="__main__":
    unittest.main()
