from __future__ import annotations

import unittest

from tools.astrology_place_resolver import (
    PlaceResolutionError,
    normalize_place_query,
    resolve_country_timezone,
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

    def test_full_taiwan_admin_locality_normalizes_and_resolves(self):
        normalized = normalize_place_query("新北市樹林區")
        self.assertEqual("樹林區", normalized["normalized_name"])
        self.assertEqual("TW", normalized["effective_country_code"])
        self.assertEqual("新北市", normalized["admin_area"])
        self.assertTrue(normalized["hierarchy_validated"])

        result = resolve_place("新北市樹林區")
        row = result["resolved"]
        self.assertEqual(1668875, row["geoname_id"])
        self.assertEqual("TW", row["country_code"])
        self.assertEqual("Asia/Taipei", row["timezone_name"])
        self.assertEqual("taiwan-admin-locality-v1", result["query"]["normalization"]["normalization_policy_id"])

    def test_taiwan_script_variant_normalizes_before_hierarchy_match(self):
        normalized = normalize_place_query("台北市中正區")
        self.assertEqual("中正區", normalized["normalized_name"])
        self.assertEqual("臺北市", normalized["admin_area"])
        self.assertTrue(normalized["script_normalization_applied"])

    def test_invalid_taiwan_admin_pair_fails_closed(self):
        with self.assertRaisesRegex(PlaceResolutionError, "hierarchy mismatch"):
            normalize_place_query("新北市中正區")

    def test_taiwan_admin_input_conflicting_country_fails_closed(self):
        with self.assertRaisesRegex(PlaceResolutionError, "conflicts with supplied country_code"):
            resolve_place("新北市樹林區", country_code="JP")

    def test_taiwan_country_resolves_unique_timezone_without_coordinates(self):
        result = resolve_country_timezone("Taiwan", country_code="TW")
        row = result["resolved"]
        self.assertEqual("TW", row["country_code"])
        self.assertEqual("Asia/Taipei", row["timezone_name"])
        self.assertNotIn("latitude", row)
        self.assertNotIn("longitude", row)

    def test_multi_timezone_country_fails_closed(self):
        with self.assertRaisesRegex(PlaceResolutionError, "unique IANA timezone"):
            resolve_country_timezone("United States", country_code="US")

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
