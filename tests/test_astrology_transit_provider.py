from __future__ import annotations

import datetime as dt
import unittest

from tools.astrology_runtime import gate_bundle
from tools.astrology_transit_provider import (
    TransitProviderInputError,
    build_transit_bundle,
    search_ingresses,
    search_stations,
    search_transit_to_natal,
    search_transit_house_ingresses,
    transit_house_context,
)

UTC = dt.timezone.utc


def _minimal_natal_bundle(longitude_deg: float = 110.0) -> dict:
    return {
        "schema_name": "astrology_fact_bundle",
        "schema_version": "1.0.0",
        "method": "Astrology",
        "reading_mode": "natal",
        "fact_source": "user_supplied_structured_export",
        "calculation_verification": "user_asserted",
        "subject_ref": "subject:synthetic-transit-target",
        "birth_time_certainty": "exact",
        "configuration": {"zodiac_system": "tropical", "center": "geocentric", "house_system": None},
        "facts": {
            "objects": [
                {
                    "fact_id": "fact:object:mercury",
                    "object_type": "planet",
                    "object_id": "Mercury",
                    "longitude_deg": longitude_deg,
                }
            ],
            "houses": [],
            "aspects": [],
            "events": [],
        },
    }


def _parse(value: str) -> dt.datetime:
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


class AstrologyTransitProviderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.natal = _minimal_natal_bundle()
        assert gate_bundle(cls.natal)["interpretation_allowed"]

    def test_mercury_three_pass_conjunction_topology_matches_research(self):
        events = search_transit_to_natal(
            self.natal,
            start_utc="2026-06-01T00:00:00Z",
            end_utc="2026-08-10T00:00:00Z",
            moving_bodies=["Mercury"],
            natal_targets=["Mercury"],
            aspects=["conjunction"],
        )
        self.assertEqual(3, len(events))
        self.assertEqual(["direct", "retrograde", "direct"], [e["motion_direction"] for e in events])
        self.assertEqual([1, 2, 3], [e["passage_index"] for e in events])
        self.assertTrue(all(e["passage_count"] == 3 for e in events))

        expected = [
            "2026-06-16T15:44:17.088+00:00",
            "2026-07-14T03:53:27.175+00:00",
            "2026-08-01T13:51:40.891+00:00",
        ]
        for event, expected_time in zip(events, expected):
            delta = abs((_parse(event["exact_time_utc"]) - _parse(expected_time)).total_seconds())
            self.assertLess(delta, 600.0)
            self.assertLess(event["angular_residual_deg"], 1e-5)

    def test_tangential_exact_contact_at_station_is_not_missed(self):
        stations = search_stations(
            start_utc="2026-06-20T00:00:00Z",
            end_utc="2026-07-05T00:00:00Z",
            moving_bodies=["Mercury"],
        )
        self.assertEqual(1, len(stations))
        station = stations[0]
        tangent_natal = _minimal_natal_bundle(float(station["longitude_deg"]))
        events = search_transit_to_natal(
            tangent_natal,
            start_utc="2026-06-20T00:00:00Z",
            end_utc="2026-07-05T00:00:00Z",
            moving_bodies=["Mercury"],
            natal_targets=["Mercury"],
            aspects=["conjunction"],
        )
        self.assertGreaterEqual(len(events), 1)
        tangent = min(events, key=lambda e: abs((_parse(e["exact_time_utc"]) - _parse(station["exact_time_utc"])).total_seconds()))
        self.assertLess(abs((_parse(tangent["exact_time_utc"]) - _parse(station["exact_time_utc"])).total_seconds()), 2.0)
        self.assertEqual("tangential_station", tangent["root_kind"])
        self.assertLessEqual(tangent["angular_residual_deg"], 1e-4)

    def test_mercury_2026_station_topology_matches_research(self):
        events = search_stations(
            start_utc="2026-01-01T00:00:00Z",
            end_utc="2027-01-01T00:00:00Z",
            moving_bodies=["Mercury"],
        )
        self.assertEqual(6, len(events))
        self.assertEqual(
            [
                "direct_to_retrograde",
                "retrograde_to_direct",
                "direct_to_retrograde",
                "retrograde_to_direct",
                "direct_to_retrograde",
                "retrograde_to_direct",
            ],
            [event["transition"] for event in events],
        )

    def test_saturn_2026_station_topology_matches_research(self):
        events = search_stations(
            start_utc="2026-01-01T00:00:00Z",
            end_utc="2027-01-01T00:00:00Z",
            moving_bodies=["Saturn"],
        )
        self.assertEqual(2, len(events))
        self.assertEqual(["direct_to_retrograde", "retrograde_to_direct"], [e["transition"] for e in events])

    def test_venus_210_degree_crossing_has_ingress_return_and_reingress(self):
        events = search_ingresses(
            start_utc="2026-08-01T00:00:00Z",
            end_utc="2026-12-31T23:59:59Z",
            moving_bodies=["Venus"],
        )
        hits = [e for e in events if abs(float(e["boundary_longitude_deg"]) - 210.0) < 1e-9]
        self.assertEqual(3, len(hits))
        self.assertEqual(["direct", "retrograde", "direct"], [e["motion_direction"] for e in hits])
        self.assertEqual(
            [("Libra", "Scorpio"), ("Scorpio", "Libra"), ("Libra", "Scorpio")],
            [(e["from_sign"], e["to_sign"]) for e in hits],
        )
        self.assertEqual(
            ["direct_ingress", "retrograde_return", "direct_reingress"],
            [e["ingress_type"] for e in hits],
        )

    def test_transit_bundle_passes_existing_runtime_gate(self):
        bundle = build_transit_bundle(
            self.natal,
            start_utc="2026-06-01T00:00:00Z",
            end_utc="2026-08-10T00:00:00Z",
            subject_ref="subject:synthetic-transit",
            moving_bodies=["Mercury"],
            natal_targets=["Mercury"],
            aspects=["conjunction"],
            include_stations=True,
            include_ingresses=False,
        )
        gate = gate_bundle(bundle)
        self.assertTrue(gate["interpretation_allowed"])
        self.assertEqual("approved_provider", bundle["fact_source"])
        self.assertEqual("verified_provider", bundle["calculation_verification"])
        self.assertEqual("astronomy-engine-transit-v1", bundle["provider"]["provider_id"])
        self.assertGreaterEqual(len(bundle["facts"]["events"]), 5)

    def test_search_window_is_bounded(self):
        with self.assertRaisesRegex(TransitProviderInputError, "400"):
            search_stations(
                start_utc="2026-01-01T00:00:00Z",
                end_utc="2028-01-01T00:00:00Z",
                moving_bodies=["Mercury"],
            )

    def test_invalid_natal_bundle_fails_closed(self):
        bad = _minimal_natal_bundle()
        bad["fact_source"] = "model_calculated"
        with self.assertRaisesRegex(TransitProviderInputError, "admitted natal"):
            search_transit_to_natal(
                bad,
                start_utc="2026-06-01T00:00:00Z",
                end_utc="2026-07-01T00:00:00Z",
                moving_bodies=["Mercury"],
                natal_targets=["Mercury"],
                aspects=["conjunction"],
            )


    def test_transit_house_context_uses_admitted_natal_cusps(self):
        natal = _minimal_natal_bundle()
        natal["configuration"]["house_system"] = "Whole Sign"
        natal["facts"]["houses"] = [{"fact_id": f"fact:house:{n}", "house_number": n, "cusp_longitude_deg": float((n-1)*30)} for n in range(1,13)]
        rows = transit_house_context(natal, at_utc="2026-01-01T00:00:00Z", moving_bodies=["Sun"])
        self.assertEqual(1, len(rows))
        self.assertEqual("transit_house_context", rows[0]["event_kind"])
        self.assertTrue(1 <= rows[0]["house_number"] <= 12)

    def test_transit_house_ingress_preserves_direct_and_retrograde_direction(self):
        natal = _minimal_natal_bundle()
        natal["configuration"]["house_system"] = "Whole Sign"
        natal["facts"]["houses"] = [{"fact_id": f"fact:house:{n}", "house_number": n, "cusp_longitude_deg": float((n-1)*30)} for n in range(1,13)]
        rows = search_transit_house_ingresses(natal, start_utc="2026-06-01T00:00:00Z", end_utc="2026-08-10T00:00:00Z", moving_bodies=["Mercury"])
        self.assertTrue(rows)
        self.assertTrue(all(r["to_house"] != r["from_house"] for r in rows))
        self.assertTrue(all(r["motion_direction"] in {"direct","retrograde"} for r in rows))

    def test_transit_house_context_rejects_approximate_or_unknown_natal_time(self):
        for certainty in ("approximate","unknown"):
            natal = _minimal_natal_bundle()
            natal["birth_time_certainty"] = certainty
            natal["configuration"]["house_system"] = "Whole Sign"
            natal["facts"]["houses"] = [{"fact_id": f"fact:house:{n}", "house_number": n, "cusp_longitude_deg": float((n-1)*30)} for n in range(1,13)]
            with self.assertRaisesRegex(TransitProviderInputError, "admitted natal|exact or rectified"):
                transit_house_context(natal, at_utc="2026-01-01T00:00:00Z", moving_bodies=["Sun"])


if __name__ == "__main__":
    unittest.main()
