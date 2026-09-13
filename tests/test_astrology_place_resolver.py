from __future__ import annotations

import unittest

from tools.astrology_place_resolver import (
    PlaceResolutionError,
    resolve_place,
    search_place_candidates,
)


class AstrologyPlaceResolverTests(unittest.TestCase):
    def test_tokyo_resolves_offline_with_country_code(self):
        result = resolve_place("Tokyo", country_code="JP")
        row = result["resolved"]
        self.assertEqual("JP", row["country_code"])
        self.assertEqual("Asia/Tokyo", row["timezone_name"])
        self.assertAlmostEqual(35.6895, row["latitude"], delta=0.25)
        self.assertAlmostEqual(139.6917, row["longitude"], delta=0.25)
        self.assertEqual("GeoNames", result["resolver"]["dataset_origin"])
        self.assertEqual("CC-BY-4.0", result["resolver"]["dataset_license"])

    def test_taipei_resolves_with_country_code_when_present(self):
        result = resolve_place("Taipei", country_code="TW")
        row = result["resolved"]
        self.assertEqual("TW", row["country_code"])
        self.assertEqual("Asia/Taipei", row["timezone_name"])
        self.assertAlmostEqual(25.0478, row["latitude"], delta=0.35)
        self.assertAlmostEqual(121.5319, row["longitude"], delta=0.35)

    def test_ambiguous_name_fails_closed(self):
        candidates = search_place_candidates("Springfield", min_city_population=500)
        self.assertGreater(len(candidates), 1)
        with self.assertRaisesRegex(PlaceResolutionError, "ambiguous"):
            resolve_place("Springfield", min_city_population=500)

    def test_missing_place_fails_closed(self):
        with self.assertRaisesRegex(PlaceResolutionError, "not found"):
            resolve_place("DefinitelyNotARealCityXYZ123")

    def test_invalid_population_dataset_fails_closed(self):
        with self.assertRaisesRegex(PlaceResolutionError, "min_city_population"):
            resolve_place("Tokyo", country_code="JP", min_city_population=1234)


if __name__ == "__main__":
    unittest.main()
