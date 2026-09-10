import importlib.util
import pathlib
import unittest

MODULE_PATH = pathlib.Path(__file__).resolve().parents[1] / "tools" / "liuyao_engine.py"
SPEC = importlib.util.spec_from_file_location("liuyao_engine", MODULE_PATH)
engine = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(engine)


class LiuyaoEngineTests(unittest.TestCase):
    def test_palace_table_covers_all_hexagrams(self):
        self.assertEqual(len(engine.PALACE_TABLE), 64)
        self.assertEqual(set(engine.PALACE_TABLE), set(engine.GUA64))

    def test_raw_line_conversion_and_change(self):
        fact = engine.build_structured_fact("789789")
        self.assertEqual(fact["raw_lines"], [7,8,9,7,8,9])
        self.assertEqual(fact["moving_positions"], [3,6])
        self.assertEqual(fact["ben_gua"]["bits"], "101101")
        self.assertEqual(fact["ben_gua"]["name"], "離為火")
        self.assertEqual(fact["zhi_gua"]["bits"], "100100")
        self.assertEqual(fact["zhi_gua"]["name"], "震為雷")

    def test_changed_line_relatives_use_primary_palace(self):
        # 889877 = 風山漸（艮宮）三爻動 → 風地觀（乾宮 metadata）。
        # 化爻六親仍必須以本卦艮宮土為基準，而不是變卦乾宮金。
        fact = engine.build_structured_fact("889877")
        self.assertEqual(fact["ben_gua"]["name"], "風山漸")
        self.assertEqual(fact["ben_gua"]["palace"], "艮")
        self.assertEqual(fact["zhi_gua"]["name"], "風地觀")
        self.assertEqual(fact["zhi_gua"]["palace"], "乾")
        self.assertEqual(fact["zhi_gua"]["six_relative_reference_palace"], "艮")
        self.assertEqual(fact["zhi_gua"]["six_relative_reference_element"], "土")
        # 三爻化卯木；木剋艮宮土，故六親為官鬼。
        self.assertEqual(fact["zhi_gua"]["lines"][2]["zhi"], "卯")
        self.assertEqual(fact["zhi_gua"]["lines"][2]["six_relative"], "官鬼")
        # 防止 regression 回到以變卦乾宮金計算（會得到妻財）。
        self.assertNotEqual(fact["zhi_gua"]["lines"][2]["six_relative"], "妻財")

    def test_no_moving_lines_has_no_changed_chart(self):
        fact = engine.build_structured_fact("777777")
        self.assertEqual(fact["ben_gua"]["name"], "乾為天")
        self.assertEqual(fact["moving_positions"], [])
        self.assertIsNone(fact["zhi_gua"])

    def test_calendar_optional_and_authority_boundaries(self):
        fact = engine.build_structured_fact(
            "789789", day_gan="甲", month_branch="午",
            day_branch="戌", xunkong=("申","酉"),
        )
        self.assertEqual(fact["calendar_context"]["status"], "provided")
        self.assertFalse(fact["interpretation_authority"])
        self.assertFalse(fact["yongshen_selection_authority"])
        self.assertEqual(fact["ben_gua"]["lines"][0]["six_spirit"], "青龍")

    def test_invalid_raw_lines_fail_closed(self):
        for bad in ("77777", "777770", "77777x"):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    engine.build_structured_fact(bad)


if __name__ == "__main__":
    unittest.main()
