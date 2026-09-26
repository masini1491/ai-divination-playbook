import unittest
from tools.ziwei_natal_provider import NormalizedNatalInput
from tools.ziwei_hourly_provider import HourlyTarget, calculate_hourly

class ZiWeiHourlyProviderTests(unittest.TestCase):
    def setUp(self):
        self.birth=NormalizedNatalInput(1987,5,20,"酉","fixture:hourly")

    def test_hourly_advances_from_daily_parent_by_hour_branch(self):
        r=calculate_hourly(self.birth,HourlyTarget(
            gender="male",target_lunar_year=2026,target_lunar_month=9,target_lunar_day=5,
            target_is_leap_month=False,target_hour_branch="午",
            target_rat_hour_policy="next_day_at_23",target_calendar_provenance="fixture:target"
        ))
        self.assertEqual("hourly.daily_parent_hour_branch_next_day_23_v1",r["profile"]["profile_id"])
        self.assertEqual("亥",r["parent_scope"]["daily_life_palace_branch"])
        self.assertEqual(6,r["target"]["hour_branch_index"])
        self.assertEqual("巳",r["hourly"]["life_palace_branch"])
        self.assertFalse(r["interpretation_authority_granted"])
        self.assertEqual("not_computed",r["unsupported"]["physical_hour_pillar"])

    def test_rat_hour_branch_zero_equals_daily_life_palace(self):
        r=calculate_hourly(self.birth,HourlyTarget(
            gender="male",target_lunar_year=2026,target_lunar_month=9,target_lunar_day=5,
            target_is_leap_month=False,target_hour_branch="子",
            target_rat_hour_policy="next_day_at_23",target_calendar_provenance="fixture:target"
        ))
        self.assertEqual(r["parent_scope"]["daily_life_palace_branch"],r["hourly"]["life_palace_branch"])

    def test_alternate_rat_hour_policy_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"next_day_at_23"):
            calculate_hourly(self.birth,HourlyTarget(
                gender="male",target_lunar_year=2026,target_lunar_month=9,target_lunar_day=5,
                target_is_leap_month=False,target_hour_branch="子",
                target_rat_hour_policy="current_day_until_midnight",target_calendar_provenance="fixture:target"
            ))

    def test_leap_parent_boundary_is_preserved(self):
        with self.assertRaisesRegex(ValueError,"cross-year rollover is not admitted"):
            calculate_hourly(self.birth,HourlyTarget(
                gender="male",target_lunar_year=2033,target_lunar_month=12,target_lunar_day=16,
                target_is_leap_month=True,target_hour_branch="午",
                target_rat_hour_policy="next_day_at_23",target_calendar_provenance="fixture:leap12"
            ))

if __name__=="__main__":
    unittest.main()
