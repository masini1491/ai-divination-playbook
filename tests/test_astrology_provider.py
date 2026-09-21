from __future__ import annotations

import json
import unittest
from pathlib import Path

from tools.astrology_provider import (
    ProviderInputError,
    _resolve_local_time,
    build_natal_bundle,
    build_unknown_time_natal_bundle,
)
from tools.astrology_runtime import gate_bundle

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "astrology_provider_sydney_1990.json"


def _objects_by_id(bundle: dict) -> dict[str, dict]:
    return {row["object_id"]: row for row in bundle["facts"]["objects"]}


def _houses_by_number(bundle: dict) -> dict[int, dict]:
    return {row["house_number"]: row for row in bundle["facts"]["houses"]}


class AstrologyProviderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        inp = cls.fixture["input"]
        cls.bundle = build_natal_bundle(
            local_datetime=inp["local_datetime"],
            timezone_name=inp["timezone_name"],
            latitude=inp["latitude"],
            longitude=inp["longitude"],
            house_system=inp["house_system"],
            subject_ref="subject:synthetic-sydney-1990",
        )

    def test_provider_output_passes_production_runtime_gate(self):
        result = gate_bundle(self.bundle)
        self.assertEqual("admitted", result["status"])
        self.assertTrue(result["interpretation_allowed"])

    def test_provider_provenance_is_explicit(self):
        self.assertEqual("approved_provider", self.bundle["fact_source"])
        self.assertEqual("verified_provider", self.bundle["calculation_verification"])
        provider = self.bundle["provider"]
        self.assertEqual("astronomy-engine-natal-v1", provider["provider_id"])
        self.assertEqual("astronomy-engine==2.1.19", provider["astronomy_engine_package"])
        self.assertEqual("Australia/Sydney", provider["timezone_name"])
        self.assertEqual("1990-06-15T00:00:00+00:00", provider["resolved_utc_iso"])

    def test_sydney_fixture_angles_match_upstream_within_one_arcminute(self):
        expected = self.fixture["expected"]
        tol = self.fixture["tolerance_deg"]
        objects = _objects_by_id(self.bundle)
        self.assertAlmostEqual(expected["ascendant"], objects["Ascendant"]["longitude_deg"], delta=tol)
        self.assertAlmostEqual(expected["midheaven"], objects["Midheaven"]["longitude_deg"], delta=tol)

    def test_sydney_fixture_planet_longitudes_match_upstream_within_one_arcminute(self):
        expected = self.fixture["expected"]
        tol = self.fixture["tolerance_deg"]
        objects = _objects_by_id(self.bundle)
        for body, longitude in expected["longitudes"].items():
            with self.subTest(body=body):
                self.assertAlmostEqual(longitude, objects[body]["longitude_deg"], delta=tol)

    def test_sydney_fixture_placidus_cusps_match_upstream(self):
        expected = self.fixture["expected"]
        tol = self.fixture["tolerance_deg"]
        houses = _houses_by_number(self.bundle)
        for house_text, longitude in expected["cusps"].items():
            house = int(house_text)
            with self.subTest(house=house):
                self.assertAlmostEqual(longitude, houses[house]["cusp_longitude_deg"], delta=tol)

    def test_sydney_fixture_house_assignments_match_upstream(self):
        expected = self.fixture["expected"]["houses"]
        objects = _objects_by_id(self.bundle)
        for body, house in expected.items():
            with self.subTest(body=body):
                self.assertEqual(house, objects[body]["house_number"])

    def test_whole_sign_houses_start_at_ascendant_sign_boundary(self):
        bundle = build_natal_bundle(
            local_datetime="1990-06-15T10:00:00",
            timezone_name="Australia/Sydney",
            latitude=-33.8688,
            longitude=151.2093,
            house_system="Whole Sign",
            subject_ref="subject:synthetic-whole-sign",
        )
        objects = _objects_by_id(bundle)
        houses = _houses_by_number(bundle)
        expected_first = int(objects["Ascendant"]["longitude_deg"] // 30) * 30.0
        self.assertEqual(expected_first, houses[1]["cusp_longitude_deg"])
        self.assertEqual((expected_first + 180.0) % 360.0, houses[7]["cusp_longitude_deg"])
        self.assertTrue(gate_bundle(bundle)["interpretation_allowed"])

    def test_dst_nonexistent_wall_time_fails_closed(self):
        with self.assertRaisesRegex(ProviderInputError, "nonexistent"):
            _resolve_local_time("2024-03-10T02:30:00", "America/New_York")

    def test_dst_ambiguous_wall_time_fails_closed(self):
        with self.assertRaisesRegex(ProviderInputError, "ambiguous"):
            _resolve_local_time("2024-11-03T01:30:00", "America/New_York")

    def test_fixed_offset_is_not_accepted_as_timezone_identity(self):
        with self.assertRaises(ProviderInputError):
            _resolve_local_time("1990-06-15T10:00:00", "+10:00")

    def test_placidus_high_latitude_fails_closed(self):
        with self.assertRaisesRegex(ProviderInputError, "Placidus"):
            build_natal_bundle(
                local_datetime="2001-01-15T12:00:00",
                timezone_name="Europe/Helsinki",
                latitude=67.0,
                longitude=24.0,
                house_system="Placidus",
                subject_ref="subject:synthetic-high-latitude",
            )

    def test_known_time_provider_still_rejects_unknown_birth_time(self):
        with self.assertRaisesRegex(ProviderInputError, "exact or approximate"):
            build_natal_bundle(
                local_datetime="1990-06-15T12:00:00",
                timezone_name="Australia/Sydney",
                latitude=-33.8688,
                longitude=151.2093,
                house_system="Whole Sign",
                subject_ref="subject:synthetic-unknown-time",
                birth_time_certainty="unknown",
            )

    def test_unknown_time_provider_emits_invariant_signs_without_noon_substitution(self):
        bundle = build_unknown_time_natal_bundle(
            local_date="2006-03-14",
            timezone_name="Asia/Taipei",
            subject_ref="subject:synthetic-date-only",
        )
        self.assertEqual("unknown", bundle["birth_time_certainty"])
        self.assertIsNone(bundle["configuration"]["house_system"])
        self.assertEqual([], bundle["facts"]["houses"])
        self.assertEqual([], bundle["facts"]["aspects"])
        self.assertFalse(bundle["provider"]["noon_substitution"])
        objects = _objects_by_id(bundle)
        self.assertIn("Sun", objects)
        self.assertEqual("Pisces", objects["Sun"]["sign"])
        for row in objects.values():
            self.assertNotIn("longitude_deg", row)
            self.assertNotIn("sign_degree", row)
            self.assertNotIn("house_number", row)
            self.assertNotIn(row.get("object_type"), {"angle", "cusp"})
        self.assertTrue(gate_bundle(bundle)["interpretation_allowed"])

    def test_aspects_reference_existing_object_facts_and_obey_runtime_orbs(self):
        object_ids = {row["fact_id"] for row in self.bundle["facts"]["objects"]}
        self.assertGreater(len(self.bundle["facts"]["aspects"]), 0)
        for aspect in self.bundle["facts"]["aspects"]:
            self.assertIn(aspect["left_ref"], object_ids)
            self.assertIn(aspect["right_ref"], object_ids)
        self.assertTrue(gate_bundle(self.bundle)["interpretation_allowed"])


if __name__ == "__main__":
    unittest.main()
