"""End-to-end deterministic Liuyao structured-fact runtime tests."""
import importlib.util
import pathlib
import unittest

MODULE_PATH = pathlib.Path(__file__).resolve().parents[1] / "tools" / "liuyao_runtime.py"
SPEC = importlib.util.spec_from_file_location("liuyao_runtime", MODULE_PATH)
runtime = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(runtime)


class LiuyaoRuntimeTests(unittest.TestCase):
    def test_calendar_and_structure_are_joined_without_changing_raw_cast(self):
        result = runtime.build_liuyao_fact(
            "789789",
            timestamp="2026-08-12T10:30:00+08:00",
        )
        fact = result["structured_method_fact"]
        self.assertEqual(fact["raw_lines"], [7, 8, 9, 7, 8, 9])
        self.assertEqual(fact["moving_positions"], [3, 6])
        self.assertEqual(fact["ben_gua"]["name"], "離為火")
        self.assertEqual(fact["zhi_gua"]["name"], "震為雷")
        self.assertEqual(fact["calendar_context"]["day_ganzhi"], "戊午")
        self.assertEqual(fact["calendar_context"]["month_branch"], "申")
        self.assertEqual(set(fact["calendar_context"]["xunkong"]), {"子", "丑"})
        self.assertEqual(fact["calendar_context"]["status"], "resolved")

    def test_calendar_facts_reach_line_flags_and_six_spirits(self):
        result = runtime.build_liuyao_fact(
            "789789",
            timestamp="2026-08-12T10:30:00+08:00",
        )
        lines = result["structured_method_fact"]["ben_gua"]["lines"]
        self.assertTrue(all(line["six_spirit"] is not None for line in lines))
        self.assertTrue(all(line["flags"] is not None for line in lines))
        self.assertEqual(lines[0]["six_spirit"], "勾陳")  # 戊日起勾陳

    def test_zi_hour_policy_flows_through_runtime(self):
        zi = runtime.build_liuyao_fact(
            "777777",
            timestamp="2026-08-12T23:30:00+08:00",
        )
        midnight = runtime.build_liuyao_fact(
            "777777",
            timestamp="2026-08-12T23:30:00+08:00",
            zi_hour_changes_day=False,
        )
        self.assertEqual(zi["structured_method_fact"]["calendar_context"]["day_ganzhi"], "己未")
        self.assertEqual(midnight["structured_method_fact"]["calendar_context"]["day_ganzhi"], "戊午")

    def test_runtime_has_no_interpretation_or_yongshen_authority(self):
        result = runtime.build_liuyao_fact(
            "777777",
            timestamp="2026-08-12T10:30:00+08:00",
        )
        self.assertFalse(result["interpretation_authority"])
        self.assertFalse(result["yongshen_selection_authority"])
        self.assertFalse(result["structured_method_fact"]["interpretation_authority"])
        self.assertFalse(result["structured_method_fact"]["yongshen_selection_authority"])

    def test_invalid_raw_cast_fails_closed(self):
        with self.assertRaises(ValueError):
            runtime.build_liuyao_fact(
                "77777",
                timestamp="2026-08-12T10:30:00+08:00",
            )


if __name__ == "__main__":
    unittest.main()
