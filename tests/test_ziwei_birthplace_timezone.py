from __future__ import annotations

import unittest

from tools.ziwei_birthplace_timezone import (
    ZiWeiBirthplaceTimezoneError,
    gregorian_birth_from_birthplace,
    resolve_birthplace_timezone,
)
from tools.ziwei_calendar_provider import normalize_gregorian_birth

class ZiWeiBirthplaceTimezoneTests(unittest.TestCase):
    def test_shulin_resolves_to_taipei_timezone(self):
        r=resolve_birthplace_timezone("新北市樹林區")
        self.assertEqual("新北市",r.matched_region)
        self.assertEqual("Asia/Taipei",r.timezone)
        self.assertFalse(r.provenance()["coordinates_resolved"])
        self.assertFalse(r.provenance()["true_solar_time_activated"])

    def test_tai_script_variant_is_bounded(self):
        r=resolve_birthplace_timezone("台北市中正區")
        self.assertEqual("臺北市中正區",r.normalized_birthplace)
        self.assertEqual("臺北市",r.matched_region)

    def test_toufen_locality_alias_resolves_to_miaoli_timezone(self):
        r=resolve_birthplace_timezone("頭份市")
        self.assertEqual("苗栗縣",r.matched_region)
        self.assertEqual("Asia/Taipei",r.timezone)
        self.assertFalse(r.provenance()["coordinates_resolved"])
        self.assertFalse(r.provenance()["longitude_resolved"])

    def test_birthplace_pre_adapter_reaches_existing_calendar_path(self):
        birth, provenance=gregorian_birth_from_birthplace(
            birthplace="新北市樹林區",
            year=1987, month=5, day=7, hour=5, minute=17,
        )
        self.assertEqual("Asia/Taipei",birth.timezone)
        result=normalize_gregorian_birth(birth)
        self.assertEqual("Asia/Taipei",result["calendar_profile"]["timezone"])
        self.assertEqual("ziwei-birthplace-timezone-tw-v1",provenance["resolver_id"])

    def test_unsupported_non_taiwan_fails_closed(self):
        for value in ("Tokyo", "日本東京", "", "Mars Colony"):
            with self.subTest(value=value):
                with self.assertRaises(ZiWeiBirthplaceTimezoneError):
                    resolve_birthplace_timezone(value)

if __name__=="__main__":
    unittest.main()
