import importlib.util
import pathlib
import unittest

MODULE_PATH = pathlib.Path(__file__).resolve().parents[1] / "tools" / "liuyao_calendar.py"
SPEC = importlib.util.spec_from_file_location("liuyao_calendar", MODULE_PATH)
calendar = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(calendar)


class LiuyaoCalendarTests(unittest.TestCase):
    def test_known_2026_baseline_matches_dual_oracle(self):
        # yaomancy/liuyao-engine calendar tests say 2026-08-12 10:30 local
        # is 丙申 month, 戊午 day, and 戊午 belongs to 甲寅旬空子丑.
        fact = calendar.calendar_facts("2026-08-12T10:30:00+08:00")
        self.assertEqual(fact["month_branch"], "申")
        self.assertEqual(fact["day_ganzhi"], "戊午")
        self.assertEqual(fact["day_gan"], "戊")
        self.assertEqual(fact["day_branch"], "午")
        self.assertEqual(set(fact["xunkong"]), {"子", "丑"})

    def test_month_branch_changes_at_precise_lichun_boundary(self):
        before = calendar.calendar_facts("2024-02-04T14:00:00+08:00")
        after = calendar.calendar_facts("2024-02-04T18:00:00+08:00")
        self.assertEqual(before["month_branch"], "丑")
        self.assertEqual(after["month_branch"], "寅")
        self.assertEqual(after["month_boundary"], "立春")
        # Independent oracle places 2024 Li Chun around 16:27 +08; compact
        # solar model should remain safely inside the 14:00/18:00 bracket.
        hhmm = after["month_boundary_time"][11:16]
        self.assertGreaterEqual(hhmm, "16:00")
        self.assertLess(hhmm, "17:00")

    def test_zi_hour_day_change_is_explicit(self):
        before = calendar.calendar_facts("2026-08-12T22:30:00+08:00")
        after = calendar.calendar_facts("2026-08-12T23:30:00+08:00")
        midnight_mode = calendar.calendar_facts(
            "2026-08-12T23:30:00+08:00", zi_hour_changes_day=False
        )
        self.assertEqual(before["day_ganzhi"], "戊午")
        self.assertEqual(after["day_ganzhi"], "己未")
        self.assertEqual(midnight_mode["day_ganzhi"], "戊午")

    def test_xunkong_rule_anchor(self):
        # 庚寅 is index 26 and belongs to 甲申旬, hence 空午未.
        self.assertEqual(set(calendar.xunkong(26)), {"午", "未"})

    def test_offset_required_and_range_fails_closed(self):
        with self.assertRaises(ValueError):
            calendar.calendar_facts("2026-08-12T10:30:00")
        with self.assertRaises(ValueError):
            calendar.calendar_facts("1800-01-01T10:30:00+08:00")


if __name__ == "__main__":
    unittest.main()
