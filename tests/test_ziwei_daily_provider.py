import unittest
from tools.ziwei_natal_provider import NormalizedNatalInput
from tools.ziwei_daily_provider import DailyTarget, calculate_daily

class ZiWeiDailyProviderTests(unittest.TestCase):
    def setUp(self):
        self.birth=NormalizedNatalInput(1987,5,20,"酉","fixture:daily")

    def test_daily_advances_from_monthly_parent(self):
        r=calculate_daily(self.birth,DailyTarget(
            gender="male",target_lunar_year=2026,target_lunar_month=9,target_lunar_day=5,
            target_is_leap_month=False,target_calendar_provenance="fixture:target"
        ))
        self.assertEqual("daily.monthly_parent_lunar_day_v1",r["profile"]["profile_id"])
        self.assertEqual("未",r["parent_scope"]["monthly_life_palace_branch"])
        self.assertEqual("亥",r["daily"]["life_palace_branch"])
        self.assertEqual(5,r["target"]["lunar_day"])
        self.assertFalse(r["interpretation_authority_granted"])
        self.assertEqual("not_computed",r["unsupported"]["day_pillar"])

    def test_day_one_equals_monthly_life_palace(self):
        r=calculate_daily(self.birth,DailyTarget(
            gender="male",target_lunar_year=2026,target_lunar_month=9,target_lunar_day=1,
            target_is_leap_month=False,target_calendar_provenance="fixture:target"
        ))
        self.assertEqual(r["parent_scope"]["monthly_life_palace_branch"],r["daily"]["life_palace_branch"])

    def test_leap_month_parent_policy_is_preserved(self):
        first=calculate_daily(self.birth,DailyTarget(
            gender="male",target_lunar_year=2023,target_lunar_month=2,target_lunar_day=15,
            target_is_leap_month=True,target_calendar_provenance="fixture:leap"
        ))
        second=calculate_daily(self.birth,DailyTarget(
            gender="male",target_lunar_year=2023,target_lunar_month=2,target_lunar_day=16,
            target_is_leap_month=True,target_calendar_provenance="fixture:leap"
        ))
        self.assertEqual(2,first["target"]["effective_month"])
        self.assertEqual(3,second["target"]["effective_month"])
        self.assertIn("day_1_15_as_same_month",first["target"]["leap_month_identity"])
        self.assertIn("day_16_plus_as_next_month",second["target"]["leap_month_identity"])

    def test_leap_month_12_cross_year_still_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"cross-year rollover is not admitted"):
            calculate_daily(self.birth,DailyTarget(
                gender="male",target_lunar_year=2033,target_lunar_month=12,target_lunar_day=16,
                target_is_leap_month=True,target_calendar_provenance="fixture:leap12"
            ))

if __name__=="__main__":
    unittest.main()
