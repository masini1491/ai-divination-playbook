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

    def test_human_display_is_top_to_bottom_without_reordering_canonical_fact(self):
        result = runtime.build_liuyao_fact(
            "889877",
            timestamp="2026-09-10T08:06:38+08:00",
        )
        fact = result["structured_method_fact"]
        display = result["presentation"]
        self.assertEqual(fact["raw_lines"], [8, 8, 9, 8, 7, 7])
        self.assertEqual(display["authority"], "derived-display-only")
        self.assertEqual(display["display_order"], "top-to-bottom")
        self.assertEqual(display["canonical_storage_order"], "bottom-to-top")
        self.assertEqual(
            [(x["position"], x["traditional_label"], x["raw_value"], x["line_type"], x["changing"])
             for x in display["lines"]],
            [
                (6, "上九", 7, "少陽", False),
                (5, "九五", 7, "少陽", False),
                (4, "六四", 8, "少陰", False),
                (3, "九三", 9, "老陽", True),
                (2, "六二", 8, "少陰", False),
                (1, "初六", 8, "少陰", False),
            ],
        )

    def test_traditional_line_labels_follow_yang_nine_yin_six_convention(self):
        self.assertEqual(runtime.traditional_line_label(7, 1), "初九")
        self.assertEqual(runtime.traditional_line_label(8, 1), "初六")
        self.assertEqual(runtime.traditional_line_label(9, 3), "九三")
        self.assertEqual(runtime.traditional_line_label(6, 5), "六五")
        self.assertEqual(runtime.traditional_line_label(7, 6), "上九")
        self.assertEqual(runtime.traditional_line_label(8, 6), "上六")

    def test_invalid_raw_cast_fails_closed(self):
        with self.assertRaises(ValueError):
            runtime.build_liuyao_fact(
                "77777",
                timestamp="2026-08-12T10:30:00+08:00",
            )


if __name__ == "__main__":
    unittest.main()
