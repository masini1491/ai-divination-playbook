from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
VALIDATOR=ROOT/"references"/"ziwei"/"validate_interpretation_claim_registry.py"
REGISTRY=ROOT/"references"/"ziwei"/"ziwei_interpretation_claim_registry_sihua_v0.json"

class ZiWeiSihuaClaimRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_registry_passes_existing_validator(self):
        p=subprocess.run([sys.executable,str(VALIDATOR),str(REGISTRY)],cwd=ROOT,text=True,capture_output=True)
        self.assertEqual(0,p.returncode,msg=p.stdout+"\n"+p.stderr)

    def test_registry_is_research_only_and_source_explicit(self):
        self.assertFalse(self.data["production_routable"])
        self.assertFalse(self.data["research_result"]["production_authority_granted"])
        self.assertEqual(3,len(self.data["claims"]))
        sources={s["source_id"]:s for s in self.data["sources"]}
        for claim in self.data["claims"]:
            self.assertEqual("star_conditional",claim["claim_type"])
            self.assertEqual("fact_gated",claim["applicability"]["conditional_activation"]["mode"])
            self.assertTrue(claim["source_refs"])
            self.assertTrue(claim["source_locators"])
            for ref in claim["source_refs"]:
                self.assertIn("CLAIM_ELIGIBLE",sources[ref]["admission_status"])

    def test_each_claim_requires_profile_sihua_and_location_facts(self):
        for claim in self.data["claims"]:
            a=claim["applicability"]["conditional_activation"]
            self.assertEqual(
                {"fact_available:sihua","fact_available:star_locations"},
                set(a["availability_requires"]),
            )
            self.assertIn("sihua_profile:sihua.default_v1",a["satisfies_all"])
            self.assertTrue(any(x.startswith("sihua:") for x in a["satisfies_all"]))
            self.assertTrue(a["satisfies_any"])
            self.assertTrue(all(x.startswith("star_branch:") for x in a["satisfies_any"]))

    def test_no_generic_transformation_outcome_claims(self):
        rendered=json.dumps(self.data,ensure_ascii=False)
        for forbidden in (
            "化祿 = guaranteed money",
            "化權 = guaranteed power",
            "化科 = guaranteed fame",
            "化忌 = guaranteed disaster",
            "必然發財",
            "必然成功",
            "必然災難",
        ):
            self.assertNotIn(forbidden,rendered)
        self.assertFalse(self.data["research_result"]["generic_transformation_outcomes_admitted"])

    def test_project_profile_facts_match_candidate_provider(self):
        expected={
            "ZW-SIHUA-TANLANG-LU-001":"sihua:戊:祿:貪狼",
            "ZW-SIHUA-TAIYANG-JI-001":"sihua:甲:忌:太陽",
            "ZW-SIHUA-TAIYIN-JI-001":"sihua:乙:忌:太陰",
        }
        for claim in self.data["claims"]:
            self.assertIn(expected[claim["claim_id"]],claim["applicability"]["conditional_activation"]["satisfies_all"])

if __name__=="__main__":
    unittest.main()
