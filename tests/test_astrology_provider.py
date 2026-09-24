from __future__ import annotations

import json
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.astrology_provider import (
    ProviderInputError,
    _part_of_fortune_longitude,
    _resolve_local_time,
    _sect_from_geometric_altitude,
    _sun_geometric_altitude_deg,
    _unknown_time_invariant_sign,
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
        self.assertEqual("1.2.0", provider["provider_version"])
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

    def test_unknown_time_cross_sign_window_is_omitted(self):
        import datetime as dt

        start = dt.datetime(2006, 3, 14, 0, 0, tzinfo=dt.timezone.utc)
        end = start + dt.timedelta(minutes=10)
        samples = iter([29.0, 29.5, 30.1])
        with patch("tools.astrology_provider._ecliptic_longitude", side_effect=lambda *_: next(samples)):
            result = _unknown_time_invariant_sign("Moon", start, end)
        self.assertIsNone(result)

    def test_aspects_reference_existing_object_facts_and_obey_runtime_orbs(self):
        object_ids = {row["fact_id"] for row in self.bundle["facts"]["objects"]}
        self.assertGreater(len(self.bundle["facts"]["aspects"]), 0)
        for aspect in self.bundle["facts"]["aspects"]:
            self.assertIn(aspect["left_ref"], object_ids)
            self.assertIn(aspect["right_ref"], object_ids)
        self.assertTrue(gate_bundle(self.bundle)["interpretation_allowed"])


    def test_e1_known_time_derived_axes_are_antipodes_with_explicit_provenance(self):
        objects = _objects_by_id(self.bundle)
        cases = (
            ("SouthNode", "NorthNode", "fact:object:northnode"),
            ("Descendant", "Ascendant", "fact:angle:ascendant"),
            ("ImumCoeli", "Midheaven", "fact:angle:midheaven"),
        )
        for derived_id, parent_id, parent_ref in cases:
            with self.subTest(object_id=derived_id):
                derived = objects[derived_id]
                parent = objects[parent_id]
                expected = (parent["longitude_deg"] + 180.0) % 360.0
                self.assertAlmostEqual(expected, derived["longitude_deg"], delta=1e-9)
                self.assertEqual(parent_ref, derived["derived_from"])
                self.assertEqual("antipode-v1", derived["derivation_policy"])
        self.assertEqual("mean", objects["SouthNode"]["node_definition"])
        self.assertIn("house_number", objects["SouthNode"])

    def test_e1_derived_axes_do_not_expand_natal_aspect_participants(self):
        forbidden_refs = {
            "fact:object:southnode",
            "fact:angle:descendant",
            "fact:angle:imumcoeli",
        }
        for aspect in self.bundle["facts"]["aspects"]:
            self.assertNotIn(aspect["left_ref"], forbidden_refs)
            self.assertNotIn(aspect["right_ref"], forbidden_refs)

    def test_e1_derived_axes_are_not_emitted_for_unknown_birth_time(self):
        bundle = build_unknown_time_natal_bundle(
            local_date="2006-03-14",
            timezone_name="Asia/Taipei",
            subject_ref="subject:synthetic-date-only-e1-boundary",
        )
        ids = set(_objects_by_id(bundle))
        self.assertTrue({"SouthNode", "Descendant", "ImumCoeli"}.isdisjoint(ids))


    def test_e4_sect_parity_fixture_reproduces_astronomy_engine_altitudes(self):
        import datetime as dt

        fixture = json.loads(
            (ROOT / "references" / "astrology" / "extended_chart_e4_sect_parity_fixture.json").read_text(encoding="utf-8")
        )
        self.assertTrue(fixture["summary"]["all_classifications_match"])
        self.assertEqual(6, fixture["summary"]["classification_matches"])
        for case in fixture["cases"]:
            with self.subTest(fixture_id=case["fixture_id"]):
                when = dt.datetime.fromisoformat(case["utc_iso"])
                altitude = _sun_geometric_altitude_deg(
                    when,
                    case["latitude"],
                    case["longitude"],
                )
                self.assertAlmostEqual(
                    case["astronomy_engine_geometric_altitude_deg"],
                    altitude,
                    delta=1e-9,
                )
                self.assertEqual(
                    case["astronomy_engine_classification"],
                    _sect_from_geometric_altitude(altitude),
                )

    def test_e4_sect_policy_fails_closed_at_exact_horizon(self):
        with self.assertRaisesRegex(ProviderInputError, "exact 0 degree"):
            _sect_from_geometric_altitude(0.0)

    def test_e4_sect_calculation_unavailable_fails_closed(self):
        with patch("tools.astrology_provider.astronomy.GeoVector", side_effect=RuntimeError("synthetic failure")):
            with self.assertRaisesRegex(ProviderInputError, "calculation unavailable"):
                _sun_geometric_altitude_deg(
                    __import__("datetime").datetime(2000, 1, 1, tzinfo=__import__("datetime").timezone.utc),
                    0.0,
                    0.0,
                )

    def test_e4_part_of_fortune_formula_is_explicitly_sect_dependent(self):
        self.assertEqual(
            (10.0 + 100.0 - 40.0) % 360.0,
            _part_of_fortune_longitude(
                ascendant_deg=10.0,
                sun_deg=40.0,
                moon_deg=100.0,
                sect="diurnal",
            ),
        )
        self.assertEqual(
            (10.0 + 40.0 - 100.0) % 360.0,
            _part_of_fortune_longitude(
                ascendant_deg=10.0,
                sun_deg=40.0,
                moon_deg=100.0,
                sect="nocturnal",
            ),
        )

    def test_e4_provider_emits_fortune_with_sect_provenance(self):
        objects = _objects_by_id(self.bundle)
        fortune = objects["PartOfFortune"]
        provider_sect = self.bundle["provider"]["sect"]
        self.assertEqual("point", fortune["object_type"])
        self.assertEqual("lot", fortune["point_kind"])
        self.assertEqual("fortune-day-night-v1", fortune["derivation_policy"])
        self.assertEqual("sect-geometric-solar-altitude-v1", fortune["sect_policy_id"])
        self.assertEqual(provider_sect["classification"], fortune["sect"])
        self.assertAlmostEqual(
            provider_sect["sun_geometric_altitude_deg"],
            fortune["sun_geometric_altitude_deg"],
            delta=1e-12,
        )
        expected = _part_of_fortune_longitude(
            ascendant_deg=objects["Ascendant"]["longitude_deg"],
            sun_deg=objects["Sun"]["longitude_deg"],
            moon_deg=objects["Moon"]["longitude_deg"],
            sect=fortune["sect"],
        )
        self.assertAlmostEqual(expected, fortune["longitude_deg"], delta=1e-9)
        self.assertIn("house_number", fortune)

    def test_e4_fortune_does_not_expand_aspects_or_unknown_time(self):
        forbidden = "fact:object:partoffortune"
        for aspect in self.bundle["facts"]["aspects"]:
            self.assertNotEqual(forbidden, aspect["left_ref"])
            self.assertNotEqual(forbidden, aspect["right_ref"])
        unknown = build_unknown_time_natal_bundle(
            local_date="2006-03-14",
            timezone_name="Asia/Taipei",
            subject_ref="subject:synthetic-date-only-e4-boundary",
        )
        self.assertNotIn("PartOfFortune", _objects_by_id(unknown))
        self.assertNotIn("sect", unknown["provider"])


if __name__ == "__main__":
    unittest.main()
