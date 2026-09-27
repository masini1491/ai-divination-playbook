from __future__ import annotations

import unittest

from tools.civil_time_normalizer import normalize_civil_time
from tools.ziwei_true_solar_time import (
    PROFILE_ID,
    TrueSolarTimeError,
    equation_of_time_minutes,
    normalize_true_solar_time,
)


class ZiWeiTrueSolarTimeTests(unittest.TestCase):
    def test_noaa_equation_of_time_reference_shape(self):
        civil=normalize_civil_time("2000-01-01T12:00:00","Etc/UTC")
        value=equation_of_time_minutes(civil.validated_local_datetime)
        self.assertAlmostEqual(-2.90416896,value,places=6)
        result=normalize_true_solar_time(civil,0.0)
        self.assertEqual(-174,result.total_correction_seconds)
        self.assertEqual("2000-01-01T11:57:06",result.apparent_solar_datetime.isoformat())

    def test_taipei_explicit_longitude_applies_small_combined_correction(self):
        civil=normalize_civil_time("2000-08-16T05:30:00","Asia/Taipei")
        result=normalize_true_solar_time(civil,121.5654)
        self.assertEqual(PROFILE_ID,result.profile_id)
        self.assertEqual(28800,result.utc_offset_seconds)
        self.assertAlmostEqual(6.2616,result.longitude_correction_minutes,places=4)
        self.assertEqual(96,result.total_correction_seconds)
        self.assertEqual("2000-08-16T05:31:36",result.apparent_solar_datetime.isoformat())

    def test_tokyo_profile_uses_resolved_zone_offset(self):
        civil=normalize_civil_time("2000-01-01T00:30:00","Asia/Tokyo")
        result=normalize_true_solar_time(civil,139.6917)
        self.assertEqual(32400,result.utc_offset_seconds)
        self.assertEqual(965,result.total_correction_seconds)
        self.assertEqual("2000-01-01T00:46:05",result.apparent_solar_datetime.isoformat())

    def test_correction_can_cross_local_calendar_date(self):
        civil=normalize_civil_time("2000-01-01T00:30:00","Asia/Shanghai")
        result=normalize_true_solar_time(civil,87.6168)
        self.assertEqual("1999-12-31T22:17:47",result.apparent_solar_datetime.isoformat())

    def test_dst_uses_exact_resolved_offset(self):
        civil=normalize_civil_time("2024-06-01T12:00:00","America/New_York")
        result=normalize_true_solar_time(civil,-74.0060)
        self.assertEqual(-14400,result.utc_offset_seconds)
        self.assertEqual(-3213,result.total_correction_seconds)
        self.assertEqual("2024-06-01T11:06:27",result.apparent_solar_datetime.isoformat())

    def test_profile_and_longitude_fail_closed(self):
        civil=normalize_civil_time("2000-01-01T12:00:00","Etc/UTC")
        for value in (True,float("nan"),float("inf"),181,-181):
            with self.subTest(value=value):
                with self.assertRaises(TrueSolarTimeError):
                    normalize_true_solar_time(civil,value)
        with self.assertRaisesRegex(TrueSolarTimeError,"unsupported"):
            normalize_true_solar_time(civil,0,profile_id="unknown")


if __name__=="__main__":
    unittest.main()
