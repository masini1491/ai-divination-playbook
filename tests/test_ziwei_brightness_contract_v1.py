from __future__ import annotations
import json
import unittest
from pathlib import Path

from tools.ziwei_brightness_provider import PROFILE_ID, calculate_brightness
from tools.ziwei_brightness_pipeline import run_scope_a_natal_with_brightness
from tools.ziwei_natal_provider import NormalizedNatalInput, calculate_scope_a_natal
from tools.ziwei_scope_a_pipeline import run_scope_a_natal

ROOT=Path(__file__).resolve().parents[1]

class ZiWeiBrightnessContractV1Tests(unittest.TestCase):
    def test_optional_manifest_is_bounded(self):
        m=json.loads((ROOT/"ZIWEI_BRIGHTNESS_ADMISSION_V1.json").read_text(encoding="utf-8"))
        self.assertEqual("PRODUCTION_ADMITTED_OPTIONAL",m["status"])
        self.assertTrue(m["default_scope_unchanged"])
        self.assertEqual(0,m["scope"]["admitted_claims_added"])
        self.assertFalse(m["calculation"]["historical_uniqueness_claimed"])
        self.assertFalse(m["interpretation"]["brightness_only_doctrine"])

    def test_provider_covers_all_major_stars_with_profile_identity(self):
        chart=calculate_scope_a_natal(NormalizedNatalInput(1987,5,20,"酉","synthetic:brightness-test"))
        b=calculate_brightness(chart["major_star_placements"])
        self.assertEqual(PROFILE_ID,b["brightness_profile"]["profile_id"])
        self.assertEqual(14,len(b["records"]))
        self.assertIn("fact_available:dignity",b["retrieval_facts"])
        self.assertFalse(b["brightness_profile"]["historical_uniqueness_claimed"])

    def test_default_scope_a_remains_without_brightness(self):
        r=run_scope_a_natal(NormalizedNatalInput(1987,5,20,"酉","synthetic:brightness-test"),request_id="base")
        self.assertEqual("not_computed",r["calculation"]["unsupported"]["brightness"])
        self.assertNotIn("brightness",r["calculation"])

    def test_optional_pipeline_adds_brightness_without_new_claim_corpus(self):
        r=run_scope_a_natal_with_brightness(
            NormalizedNatalInput(1987,5,20,"酉","synthetic:brightness-test"),
            request_id="bright",
        )
        self.assertEqual("computed_by_optional_profile",r["calculation"]["unsupported"]["brightness"])
        self.assertEqual(14,len(r["calculation"]["brightness"]["records"]))
        self.assertTrue(r["authority"]["brightness_profile_admitted"])
        self.assertFalse(r["authority"]["brightness_only_doctrine_admitted"])

    def test_dignity_dependent_existing_claims_unlock(self):
        base=run_scope_a_natal(
            NormalizedNatalInput(1987,5,20,"酉","synthetic:brightness-test"),
            request_id="base2",
            requested_subjects=("太陽","太陰"),
        )
        bright=run_scope_a_natal_with_brightness(
            NormalizedNatalInput(1987,5,20,"酉","synthetic:brightness-test"),
            request_id="bright2",
            requested_subjects=("太陽","太陰"),
        )
        self.assertNotIn("ZW-B1-TAIYANG-COND-002",base["interpretation"]["selected_claim_ids"])
        self.assertNotIn("ZW-B2-TAIYIN-COND-002",base["interpretation"]["selected_claim_ids"])
        self.assertIn("ZW-B1-TAIYANG-COND-002",bright["interpretation"]["selected_claim_ids"])
        self.assertIn("ZW-B2-TAIYIN-COND-002",bright["interpretation"]["selected_claim_ids"])
        states={x["claim_id"]:x["state"] for x in bright["interpretation"]["conditional_evaluations"]}
        self.assertEqual("satisfied",states["ZW-B1-TAIYANG-COND-002"])
        self.assertEqual("satisfied",states["ZW-B2-TAIYIN-COND-002"])

if __name__=="__main__":
    unittest.main()
