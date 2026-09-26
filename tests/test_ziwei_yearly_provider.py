import unittest
from tools.ziwei_natal_provider import NormalizedNatalInput
from tools.ziwei_yearly_provider import YearlyTarget, calculate_yearly

class ZiWeiYearlyProviderTests(unittest.TestCase):
    def setUp(self):
        self.birth=NormalizedNatalInput(1987,5,20,"酉","fixture:yearly")

    def test_2026_yearly_life_palace_and_parent(self):
        r=calculate_yearly(self.birth,YearlyTarget("male",2026))
        self.assertEqual("yearly.year_branch_common_v1",r["profile"]["profile_id"])
        self.assertEqual("丙",r["target"]["year_stem"])
        self.assertEqual("午",r["target"]["year_branch"])
        self.assertEqual("午",r["yearly"]["life_palace_branch"])
        self.assertEqual(3,r["parent_scope"]["decadal_index"])
        self.assertEqual(5,r["yearly"]["index_within_decadal"])
        self.assertEqual("sihua.default_v1",r["yearly_sihua"]["profile_id"])
        self.assertFalse(r["interpretation_authority_granted"])

    def test_palace_roles_reverse_from_year_branch(self):
        r=calculate_yearly(self.birth,YearlyTarget("male",2026))
        by_branch={x["branch"]:x["yearly_palace"] for x in r["yearly"]["palace_roles"]}
        self.assertEqual("命宮",by_branch["午"])
        self.assertEqual("兄弟宮",by_branch["巳"])
        self.assertEqual("父母宮",by_branch["未"])

    def test_target_before_first_decadal_fails_closed(self):
        with self.assertRaises(ValueError):
            calculate_yearly(self.birth,YearlyTarget("male",1987))

if __name__=="__main__":
    unittest.main()
