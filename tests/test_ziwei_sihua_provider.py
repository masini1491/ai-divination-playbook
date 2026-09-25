from __future__ import annotations
import unittest

from tools.ziwei_sihua_provider import (
    PROFILE_ID,
    STEMS,
    TRANSFORMS,
    calculate_sihua,
)

EXPECTED={
    "甲":("廉貞","破軍","武曲","太陽"),
    "乙":("天機","天梁","紫微","太陰"),
    "丙":("天同","天機","文昌","廉貞"),
    "丁":("太陰","天同","天機","巨門"),
    "戊":("貪狼","太陰","右弼","天機"),
    "己":("武曲","貪狼","天梁","文曲"),
    "庚":("太陽","武曲","天府","天同"),
    "辛":("巨門","太陽","文曲","文昌"),
    "壬":("天梁","紫微","左輔","武曲"),
    "癸":("破軍","巨門","太陰","貪狼"),
}

class ZiWeiSihuaProviderCandidateTests(unittest.TestCase):
    def test_all_ten_stems_are_complete_and_ordered(self):
        self.assertEqual(tuple(STEMS),tuple(EXPECTED))
        for stem in STEMS:
            with self.subTest(stem=stem):
                r=calculate_sihua(stem)
                self.assertEqual(EXPECTED[stem],tuple(r["by_transform"][x] for x in TRANSFORMS))
                self.assertEqual(4,len(r["records"]))
                self.assertEqual(set(TRANSFORMS),set(r["by_transform"]))

    def test_project_default_has_one_explicit_base_override(self):
        r=calculate_sihua("庚")
        self.assertEqual([{
            "year_stem":"庚",
            "transform_kind":"科",
            "base_star":"太陰",
            "selected_star":"天府",
            "decision_owner":"references/ziwei/FOUR_TRANSFORMATION_VARIANT_REGISTRY.md",
            "decision_identity":"PROJECT-DEFAULT-V1",
        }],r["project_overrides"])
        self.assertEqual("天府",r["by_transform"]["科"])

    def test_profile_and_provenance_are_explicit(self):
        r=calculate_sihua("壬")
        self.assertEqual(PROFILE_ID,r["profile"]["profile_id"])
        self.assertEqual("project_composite_profile",r["profile"]["identity_kind"])
        self.assertFalse(r["profile"]["historical_uniqueness_claimed"])
        self.assertEqual("matharts/ziwei",r["base_source"]["repository"])
        self.assertEqual("596f43c43ff6fbae526314c7f668bbf346445ff1",r["base_source"]["revision"])
        self.assertTrue(r["production_authority_granted"])
        for record in r["records"]:
            self.assertEqual("matharts/ziwei",record["source_provenance"]["base_repository"])
            self.assertEqual("596f43c43ff6fbae526314c7f668bbf346445ff1",record["source_provenance"]["base_revision"])
            self.assertEqual(PROFILE_ID,record["sihua_profile_id"])
            self.assertEqual("ziwei-sihua-project-default-python",record["engine"]["provider_id"])
            self.assertEqual("1.0.0",record["engine"]["provider_version"])

    def test_unknown_profile_and_stem_fail_closed(self):
        with self.assertRaisesRegex(ValueError,"unsupported sihua_profile_id"):
            calculate_sihua("甲",sihua_profile_id="sihua.other")
        with self.assertRaisesRegex(ValueError,"invalid year_stem"):
            calculate_sihua("X")

    def test_provider_is_facts_only_even_after_admission(self):
        r=calculate_sihua("甲")
        self.assertTrue(r["production_authority_granted"])
        self.assertEqual("1.0.0",r["schema_version"])
        self.assertEqual("1.0.0",r["provider"]["version"])
        self.assertEqual("OPTIONAL SIHUA V1 PRODUCTION-ADMITTED FACT PROVIDER",r["provider"]["authority"])

    def test_no_generic_outcome_doctrine_is_emitted(self):
        r=calculate_sihua("甲")
        self.assertFalse(r["interpretation_boundary"]["transformed_star_claims_admitted"])
        self.assertFalse(r["interpretation_boundary"]["generic_transform_outcome_dictionary_admitted"])
        self.assertFalse(r["interpretation_boundary"]["cross_profile_averaging_allowed"])
        text=str(r)
        for forbidden in ("guaranteed money","guaranteed power","guaranteed fame","guaranteed disaster"):
            self.assertNotIn(forbidden,text)

if __name__=="__main__":
    unittest.main()
