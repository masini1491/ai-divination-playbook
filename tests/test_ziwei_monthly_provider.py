import unittest
from tools.ziwei_natal_provider import NormalizedNatalInput
from tools.ziwei_monthly_provider import MonthlyTarget, calculate_monthly

class ZiWeiMonthlyProviderTests(unittest.TestCase):
    def setUp(self):
        self.birth=NormalizedNatalInput(1987,5,20,"酉","fixture:monthly")

    def test_2026_non_leap_month_9(self):
        r=calculate_monthly(self.birth,MonthlyTarget(
            gender="male",target_lunar_year=2026,target_lunar_month=9,target_lunar_day=1,
            target_is_leap_month=False,target_calendar_provenance="fixture:target"
        ))
        self.assertEqual("monthly.doujun_effective_month_split15_v1",r["profile"]["profile_id"])
        self.assertEqual("亥",r["monthly"]["doujun_branch"])
        self.assertEqual("未",r["monthly"]["life_palace_branch"])
        self.assertEqual(9,r["target"]["effective_month"])
        self.assertEqual(3,r["parent_scope"]["provider_id"]=="ziwei-yearly-year-branch-python" and r["parent_scope"]["target_lunar_year"]==2026 and 3)
        self.assertFalse(r["interpretation_authority_granted"])

    def test_leap_month_split_after_day_15(self):
        first=calculate_monthly(self.birth,MonthlyTarget(
            gender="male",target_lunar_year=2023,target_lunar_month=2,target_lunar_day=15,
            target_is_leap_month=True,target_calendar_provenance="fixture:leap"
        ))
        second=calculate_monthly(self.birth,MonthlyTarget(
            gender="male",target_lunar_year=2023,target_lunar_month=2,target_lunar_day=16,
            target_is_leap_month=True,target_calendar_provenance="fixture:leap"
        ))
        self.assertEqual(2,first["target"]["effective_month"])
        self.assertEqual(3,second["target"]["effective_month"])
        self.assertEqual("酉",first["monthly"]["life_palace_branch"])
        self.assertEqual("戌",second["monthly"]["life_palace_branch"])
        self.assertIn("day_1_15_as_same_month",first["target"]["leap_month_identity"])
        self.assertIn("day_16_plus_as_next_month",second["target"]["leap_month_identity"])

    def test_leap_month_12_cross_year_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"cross-year rollover is not admitted"):
            calculate_monthly(self.birth,MonthlyTarget(
                gender="male",target_lunar_year=2033,target_lunar_month=12,target_lunar_day=16,
                target_is_leap_month=True,target_calendar_provenance="fixture:leap12"
            ))

if __name__=="__main__":
    unittest.main()
