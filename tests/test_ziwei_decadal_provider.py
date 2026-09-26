import unittest

from tools.ziwei_natal_provider import NormalizedNatalInput
from tools.ziwei_decadal_provider import DecadalTarget, calculate_decadal

class ZiWeiDecadalProviderTests(unittest.TestCase):
    def setUp(self):
        self.birth=NormalizedNatalInput(1987,5,20,"酉","fixture:decadal")

    def test_yin_year_male_runs_reverse_from_life_palace(self):
        r=calculate_decadal(self.birth,DecadalTarget("male",2026))
        self.assertEqual("decadal.quanji_common_v1",r["profile"]["profile_id"])
        self.assertEqual("traditional_nominal_age",r["profile"]["rules"]["age_basis"])
        self.assertEqual(40,r["target"]["nominal_age"])
        self.assertEqual(3,r["decadal"]["index"])
        self.assertEqual("reverse",r["decadal"]["direction"])
        self.assertEqual(35,r["decadal"]["start_nominal_age"])
        self.assertEqual(44,r["decadal"]["end_nominal_age"])
        self.assertEqual(2021,r["decadal"]["start_lunar_year"])
        self.assertEqual(2030,r["decadal"]["end_lunar_year"])
        self.assertEqual("午",r["decadal"]["life_palace_branch"])
        self.assertTrue(r["production_authority_granted"])
        self.assertFalse(r["interpretation_authority_granted"])

    def test_yin_year_female_runs_forward(self):
        r=calculate_decadal(self.birth,DecadalTarget("female",2026))
        self.assertEqual("forward",r["decadal"]["direction"])
        self.assertEqual("子",r["decadal"]["life_palace_branch"])

    def test_first_decade_starts_at_bureau_number(self):
        r=calculate_decadal(self.birth,DecadalTarget("male",1991))
        self.assertEqual(5,r["target"]["nominal_age"])
        self.assertEqual(0,r["decadal"]["index"])
        self.assertEqual(5,r["decadal"]["start_nominal_age"])
        self.assertEqual(14,r["decadal"]["end_nominal_age"])
        self.assertEqual(r["parent_scope"]["scope"],"natal_baseline")

    def test_target_before_first_decade_fails_closed(self):
        with self.assertRaises(ValueError):
            calculate_decadal(self.birth,DecadalTarget("male",1987))

    def test_invalid_gender_and_far_target_fail_closed(self):
        with self.assertRaises(ValueError):
            calculate_decadal(self.birth,DecadalTarget("other",2026))
        with self.assertRaises(ValueError):
            calculate_decadal(self.birth,DecadalTarget("male",2200))

if __name__=="__main__":
    unittest.main()
