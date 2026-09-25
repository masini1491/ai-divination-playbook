from __future__ import annotations
import unittest

from tools.ziwei_calendar_provider import normalize_gregorian_birth
from tools.ziwei_year_notation import (
    MinguoBirthInput,
    convert_minguo_birth,
    minguo_year_to_gregorian,
)

class ZiWeiYearNotationTests(unittest.TestCase):
    def test_minguo_year_conversion(self):
        self.assertEqual(1912, minguo_year_to_gregorian(1))
        self.assertEqual(1987, minguo_year_to_gregorian(76))
        self.assertEqual(2026, minguo_year_to_gregorian(115))

    def test_minguo_birth_reaches_existing_calendar_provider(self):
        converted=convert_minguo_birth(MinguoBirthInput(76,5,7,5,17))
        self.assertEqual("minguo",converted["source"]["year_notation"])
        self.assertEqual(76,converted["source"]["year"])
        self.assertEqual(1987,converted["converted"]["year"])
        result=normalize_gregorian_birth(converted["gregorian_birth"])
        self.assertEqual(1987,result["input"]["year"])
        self.assertEqual(5,result["input"]["month"])
        self.assertEqual(7,result["input"]["day"])

    def test_invalid_minguo_year_fails_closed(self):
        for value in (0,-1):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    minguo_year_to_gregorian(value)
        with self.assertRaises(ValueError):
            minguo_year_to_gregorian(True)

    def test_invalid_converted_date_still_uses_gregorian_validation(self):
        with self.assertRaises(ValueError):
            convert_minguo_birth(MinguoBirthInput(112,2,30,12))

if __name__=="__main__":
    unittest.main()
