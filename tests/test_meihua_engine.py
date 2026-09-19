import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("meihua_engine", ROOT / "tools" / "meihua_engine.py")
engine = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(engine)


class MeihuaEngineTests(unittest.TestCase):
    def test_observing_plum_fixture_074_803(self):
        fact = engine.derive(
            a="074",
            b="803",
            upper_trigram="兌",
            lower_trigram="離",
            hexagram="澤火革",
            moving_line=1,
        )
        self.assertEqual(fact["cast_fact"]["hexagram"], "澤火革")
        self.assertEqual(fact["derived"]["mutual_hexagram"]["name"], "天風姤")
        self.assertEqual(fact["derived"]["mutual_hexagram"]["upper_trigram"], "乾")
        self.assertEqual(fact["derived"]["mutual_hexagram"]["lower_trigram"], "巽")
        self.assertEqual(fact["derived"]["changed_hexagram"]["name"], "澤山咸")
        self.assertEqual(fact["derived"]["body"], {"trigram":"兌","element":"金","source":"static-trigram"})
        self.assertEqual(fact["derived"]["use"], {"trigram":"離","element":"火","source":"moving-trigram"})
        self.assertEqual(fact["derived"]["body_use_relation"], "用剋體")

    def test_same_input_is_deterministic(self):
        first = engine.derive(a=74, b=803)
        second = engine.derive(a="074", b="803")
        self.assertEqual(first, second)

    def test_cast_assertion_mismatch_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "cast fact mismatch"):
            engine.derive(a="074", b="803", hexagram="乾為天")

    def test_upper_moving_line_assigns_upper_as_use(self):
        fact = engine.derive(a="001", b="004")
        self.assertGreaterEqual(fact["cast_fact"]["moving_line"], 1)
        self.assertLessEqual(fact["cast_fact"]["moving_line"], 6)
        if fact["cast_fact"]["moving_line"] >= 4:
            self.assertEqual(fact["derived"]["use"]["trigram"], fact["cast_fact"]["upper_trigram"])
            self.assertEqual(fact["derived"]["body"]["trigram"], fact["cast_fact"]["lower_trigram"])


if __name__ == "__main__":
    unittest.main()
