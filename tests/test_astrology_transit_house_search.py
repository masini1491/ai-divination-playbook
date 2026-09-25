from __future__ import annotations

import unittest

from tools.astrology_orchestrator import OrchestrationInputError, run_request
from tools.astrology_runtime import gate_bundle
from tools.astrology_transit_provider import (
    TransitProviderInputError,
    build_transit_bundle,
    search_house_ingresses,
    transit_house_context,
)


def synthetic_whole_sign_natal(*, certainty: str = "exact") -> dict:
    houses = [
        {
            "fact_id": f"fact:house:{house}",
            "house_number": house,
            "cusp_longitude_deg": float((house - 1) * 30),
            "sign_index": house - 1,
            "sign": (
                "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
            )[house - 1],
            "sign_degree": 0.0,
        }
        for house in range(1, 13)
    ]
    return {
        "schema_name": "astrology_fact_bundle",
        "schema_version": "1.0.0",
        "method": "Astrology",
        "reading_mode": "natal",
        "fact_source": "user_supplied_structured_export",
        "calculation_verification": "user_asserted",
        "subject_ref": "subject:house-search-fixture",
        "birth_time_certainty": certainty,
        "configuration": {"zodiac_system": "tropical", "center": "geocentric", "house_system": "Whole Sign"},
        "facts": {"objects": [], "houses": houses, "aspects": [], "events": []},
    }


class AstrologyTransitHouseSearchTests(unittest.TestCase):
    def test_sun_crosses_synthetic_first_house_cusp(self):
        natal = synthetic_whole_sign_natal()
        self.assertTrue(gate_bundle(natal)["interpretation_allowed"])
        events = search_house_ingresses(
            natal,
            start_utc="2026-03-19T00:00:00Z",
            end_utc="2026-03-22T00:00:00Z",
            moving_bodies=["Sun"],
        )
        hits = [row for row in events if row["to_house"] == 1]
        self.assertEqual(1, len(hits))
        self.assertEqual(12, hits[0]["from_house"])
        self.assertEqual("house_ingress", hits[0]["event_kind"])
        self.assertEqual("Whole Sign", hits[0]["house_system"])
        self.assertAlmostEqual(0.0, hits[0]["cusp_longitude_deg"], places=9)

    def test_point_in_time_house_context_is_deterministic(self):
        natal = synthetic_whole_sign_natal()
        rows = transit_house_context(
            natal,
            at_utc="2026-03-20T12:00:00Z",
            moving_bodies=["Sun"],
        )
        self.assertEqual(1, len(rows))
        self.assertEqual("house_context", rows[0]["event_kind"])
        self.assertEqual("Whole Sign", rows[0]["house_system"])
        self.assertEqual(12, rows[0]["house_number"])
        self.assertEqual("2026-03-20T12:00:00Z", rows[0]["exact_time_utc"])

    def test_point_in_time_house_context_requires_exact_birth_time(self):
        natal = synthetic_whole_sign_natal(certainty="approximate")
        with self.assertRaisesRegex(TransitProviderInputError, "exact birth time"):
            transit_house_context(
                natal,
                at_utc="2026-03-20T12:00:00Z",
                moving_bodies=["Sun"],
            )

    def test_house_search_requires_exact_birth_time(self):
        natal = synthetic_whole_sign_natal(certainty="approximate")
        self.assertTrue(gate_bundle(natal)["interpretation_allowed"])
        with self.assertRaisesRegex(TransitProviderInputError, "exact birth time"):
            search_house_ingresses(
                natal,
                start_utc="2026-03-19T00:00:00Z",
                end_utc="2026-03-22T00:00:00Z",
                moving_bodies=["Sun"],
            )

    def test_house_only_bundle_does_not_require_dummy_aspects(self):
        natal = synthetic_whole_sign_natal()
        bundle = build_transit_bundle(
            natal,
            start_utc="2026-03-19T00:00:00Z",
            end_utc="2026-03-22T00:00:00Z",
            subject_ref="subject:house-search-fixture",
            moving_bodies=["Sun"],
            natal_targets=[],
            aspects=[],
            include_transit_to_natal=False,
            include_stations=False,
            include_ingresses=False,
            include_house_ingresses=True,
        )
        self.assertTrue(gate_bundle(bundle)["interpretation_allowed"])
        self.assertTrue(bundle["facts"]["events"])
        self.assertTrue(all(row["event_kind"] == "house_ingress" for row in bundle["facts"]["events"]))

    def test_orchestrator_accepts_standalone_house_search(self):
        request = {
            "schema_name": "astrology_reading_request",
            "schema_version": "1.0.0",
            "reading_mode": "transit",
            "subject_ref": "fixture-house-only",
            "birth": {
                "local_datetime": "1990-06-15T10:00:00",
                "birth_time_certainty": "exact",
                "house_system": "Whole Sign",
                "location": {
                    "coordinates": {
                        "latitude": 35.6895,
                        "longitude": 139.6917,
                        "timezone_name": "Asia/Tokyo",
                    }
                },
            },
            "transit": {
                "start_utc": "2026-03-01T00:00:00Z",
                "end_utc": "2026-04-15T00:00:00Z",
                "moving_bodies": ["Sun"],
                "include_transit_to_natal": False,
                "include_stations": False,
                "include_ingresses": False,
                "include_house_ingresses": True,
            },
        }
        result = run_request(request)
        events = result["fact_bundles"]["transit"]["facts"]["events"]
        self.assertTrue(events)
        self.assertTrue(all(row["event_kind"] == "house_ingress" for row in events))

    def test_orchestrator_accepts_point_in_time_house_context(self):
        request = {
            "schema_name": "astrology_reading_request",
            "schema_version": "1.0.0",
            "reading_mode": "transit",
            "subject_ref": "fixture-house-context",
            "birth": {
                "local_datetime": "1990-06-15T10:00:00",
                "birth_time_certainty": "exact",
                "house_system": "Whole Sign",
                "location": {"coordinates": {"latitude": 35.6895, "longitude": 139.6917, "timezone_name": "Asia/Tokyo"}},
            },
            "transit": {
                "start_utc": "2026-03-01T00:00:00Z",
                "end_utc": "2026-04-15T00:00:00Z",
                "moving_bodies": ["Sun"],
                "include_transit_to_natal": False,
                "include_stations": False,
                "include_ingresses": False,
                "include_house_ingresses": False,
                "include_house_context": True,
                "house_context_utc": "2026-03-20T12:00:00Z",
            },
        }
        result = run_request(request)
        events = result["fact_bundles"]["transit"]["facts"]["events"]
        self.assertEqual(1, len(events))
        self.assertEqual("house_context", events[0]["event_kind"])
        self.assertIn(events[0]["house_number"], range(1, 13))

    def test_orchestrator_rejects_context_outside_bounded_window(self):
        request = {
            "schema_name": "astrology_reading_request",
            "schema_version": "1.0.0",
            "reading_mode": "transit",
            "subject_ref": "fixture-house-context-outside",
            "birth": {
                "local_datetime": "1990-06-15T10:00:00",
                "birth_time_certainty": "exact",
                "house_system": "Whole Sign",
                "location": {"coordinates": {"latitude": 35.6895, "longitude": 139.6917, "timezone_name": "Asia/Tokyo"}},
            },
            "transit": {
                "start_utc": "2026-03-01T00:00:00Z",
                "end_utc": "2026-04-15T00:00:00Z",
                "moving_bodies": ["Sun"],
                "include_transit_to_natal": False,
                "include_stations": False,
                "include_ingresses": False,
                "include_house_ingresses": False,
                "include_house_context": True,
                "house_context_utc": "2026-05-01T00:00:00Z",
            },
        }
        with self.assertRaisesRegex(TransitProviderInputError, "must fall within"):
            run_request(request)

    def test_orchestrator_rejects_approximate_house_search(self):
        request = {
            "schema_name": "astrology_reading_request",
            "schema_version": "1.0.0",
            "reading_mode": "transit",
            "subject_ref": "fixture-house-approx",
            "birth": {
                "local_datetime": "1990-06-15T10:00:00",
                "birth_time_certainty": "approximate",
                "house_system": "Whole Sign",
                "location": {
                    "coordinates": {
                        "latitude": 35.6895,
                        "longitude": 139.6917,
                        "timezone_name": "Asia/Tokyo",
                    }
                },
            },
            "transit": {
                "start_utc": "2026-03-01T00:00:00Z",
                "end_utc": "2026-04-15T00:00:00Z",
                "moving_bodies": ["Sun"],
                "include_transit_to_natal": False,
                "include_stations": False,
                "include_ingresses": False,
                "include_house_ingresses": True,
            },
        }
        with self.assertRaisesRegex(OrchestrationInputError, "requires birth_time_certainty=exact"):
            run_request(request)


if __name__ == "__main__":
    unittest.main()
