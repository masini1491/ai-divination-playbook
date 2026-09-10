"""Differential checks for the lightweight Liuyao structural core.

Reference evidence was acquired through GitHub Connect only.
Pinned references used when this test was authored:
- AdrienSterling/yigram-najia-rules @ 0bb53f14c1cd379afeeccaa5a3dbb8531686ffe9
- yaomancy/liuyao-engine @ 53291663a4c733c4cbdfa174a8d3075475c07fd3

These assertions intentionally cover only deterministic structural facts that do
not require a calendar engine or question/yongshen judgment.
"""
import importlib.util
import pathlib
import unittest

MODULE_PATH = pathlib.Path(__file__).resolve().parents[1] / "tools" / "liuyao_engine.py"
SPEC = importlib.util.spec_from_file_location("liuyao_engine", MODULE_PATH)
engine = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(engine)

# Independent table transcription from yigram-najia-rules/tables.json.
REF_TRIGRAM = {
    "乾": ("子寅辰", "午申戌"),
    "坤": ("未巳卯", "丑亥酉"),
    "震": ("子寅辰", "午申戌"),
    "巽": ("丑亥酉", "未巳卯"),
    "坎": ("寅辰午", "申戌子"),
    "離": ("卯丑亥", "酉未巳"),
    "艮": ("辰午申", "戌子寅"),
    "兌": ("巳卯丑", "亥酉未"),
}
REF_PALACE_ELEMENT = {
    "乾": "金", "兌": "金", "離": "火", "震": "木",
    "巽": "木", "坎": "水", "艮": "土", "坤": "土",
}
REF_GENERATION_SHI_YING = {
    0: (6, 3), 1: (1, 4), 2: (2, 5), 3: (3, 6),
    4: (4, 1), 5: (5, 2), 6: (4, 1), 7: (3, 6),
}
REF_PALACE_SEQUENCES = {
    "乾": ["111111","011111","001111","000111","000011","000001","000101","111101"],
    "坤": ["000000","100000","110000","111000","111100","111110","111010","000010"],
    "震": ["100100","000100","010100","011100","011000","011010","011110","100110"],
    "巽": ["011011","111011","101011","100011","100111","100101","100001","011001"],
    "坎": ["010010","110010","100010","101010","101110","101100","101000","010000"],
    "離": ["101101","001101","011101","010101","010001","010011","010111","101111"],
    "艮": ["001001","101001","111001","110001","110101","110111","110011","001011"],
    "兌": ["110110","010110","000110","001110","001010","001000","001100","110100"],
}


class LiuyaoReferenceParityTests(unittest.TestCase):
    def test_najia_branch_sequences_match_reference(self):
        for trigram, (inner, outer) in REF_TRIGRAM.items():
            with self.subTest(trigram=trigram):
                _, actual_inner, _, actual_outer = engine.NAJIA[trigram]
                self.assertEqual(actual_inner, inner)
                self.assertEqual(actual_outer, outer)

    def test_palace_elements_match_reference(self):
        self.assertEqual(engine.PALACE_WUXING, REF_PALACE_ELEMENT)

    def test_all_64_palace_generation_and_shi_ying_match_reference(self):
        seen = set()
        for palace, sequence in REF_PALACE_SEQUENCES.items():
            for generation_index, bits in enumerate(sequence):
                with self.subTest(palace=palace, generation=generation_index, bits=bits):
                    actual_palace, _, actual_shi = engine.PALACE_TABLE[bits]
                    expected_shi, expected_ying = REF_GENERATION_SHI_YING[generation_index]
                    self.assertEqual(actual_palace, palace)
                    self.assertEqual(actual_shi, expected_shi)
                    self.assertEqual(engine._ying_position(actual_shi), expected_ying)
                    seen.add(bits)
        self.assertEqual(len(seen), 64)
        self.assertEqual(seen, set(engine.GUA64))

    def test_six_relative_rule_matches_reference_semantics(self):
        # Reference semantics: generates_self=父母, self_generates=子孫,
        # self_controls=妻財, controls_self=官鬼, same=兄弟.
        self.assertEqual(engine.six_relative("金", "金"), "兄弟")
        self.assertEqual(engine.six_relative("土", "金"), "父母")
        self.assertEqual(engine.six_relative("水", "金"), "子孫")
        self.assertEqual(engine.six_relative("木", "金"), "妻財")
        self.assertEqual(engine.six_relative("火", "金"), "官鬼")


if __name__ == "__main__":
    unittest.main()
