from __future__ import annotations

import json
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.astrology_swiss_transit_provider import (
    PROVIDER_ID,
    SwissTransitProviderInputError,
    build_transit_bundle,
)

ROOT = Path(__file__).resolve().parents[1]


class _FakeSwe:
    FLG_SWIEPH = 2
    FLG_MOSEPH = 4
    FLG_JPLEPH = 1
    FLG_SPEED = 256
    SUN = 0
    MOON = 1
    MERCURY = 2
    VENUS = 3
    MARS = 4
    JUPITER = 5
    SATURN = 6
    URANUS = 7
    NEPTUNE = 8
    PLUTO = 9
    version = "test-host"

    @staticmethod
    def julday(year, month, day, hour):
        # Only monotonicity matters for this deterministic test backend.
        return year * 372.0 + month * 31.0 + day + hour / 24.0

    @staticmethod
    def calc_ut(jd, body, flags):
        longitude = (jd * 0.1 + body * 7.0) % 360.0
        return [longitude, 0.0, 1.0, 0.1, 0.0, 0.0], _FakeSwe.FLG_MOSEPH | _FakeSwe.FLG_SPEED


def _natal(provider_id: str = "swiss-host-natal-v1") -> dict:
    signs = (
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
    )
    return {
        "schema_name": "astrology_fact_bundle",
        "schema_version": "1.0.0",
        "method": "Astrology",
        "reading_mode": "natal",
        "fact_source": "approved_provider",
        "calculation_verification": "verified_provider",
        "subject_ref": "subject:swiss-transit-test",
        "birth_time_certainty": "exact",
        "configuration": {
            "zodiac_system": "tropical",
            "center": "geocentric",
            "house_system": "Whole Sign",
        },
        "provider": {
            "provider_id": provider_id,
            "provider_version": "test",
        },
        "facts": {
            "objects": [
                {
                    "fact_id": "fact:object:mercury",
                    "object_type": "planet",
                    "object_id": "Mercury",
                    "longitude_deg": 110.0,
                }
            ],
            "houses": [
                {
                    "fact_id": f"fact:house:{house}",
                    "house_number": house,
                    "cusp_longitude_deg": float((house - 1) * 30),
                    "sign_index": house - 1,
                    "sign": signs[house - 1],
                    "sign_degree": 0.0,
                }
                for house in range(1, 13)
            ],
            "aspects": [],
            "events": [],
        },
    }


class AstrologySwissTransitProviderTests(unittest.TestCase):
    def test_host_provider_reuses_shared_kernel_and_records_effective_backend(self):
        with patch(
            "tools.astrology_swiss_transit_provider._load_swisseph",
            return_value=_FakeSwe,
        ):
            bundle = build_transit_bundle(
                _natal(),
                start_utc="2026-06-01T00:00:00Z",
                end_utc="2026-06-02T00:00:00Z",
                subject_ref="subject:swiss-transit-test",
                moving_bodies=["Mercury"],
                natal_targets=[],
                aspects=[],
                include_transit_to_natal=False,
                include_stations=False,
                include_ingresses=False,
                include_house_ingresses=False,
                include_house_context=True,
                house_context_utc="2026-06-01T12:00:00Z",
            )
        self.assertEqual(PROVIDER_ID, bundle["provider"]["provider_id"])
        self.assertEqual("PySwissEph", bundle["provider"]["provider_api_family"])
        self.assertEqual("MOSEPH_ONLY", bundle["provider"]["effective_backend_summary"])
        self.assertEqual([260], bundle["provider"]["actual_retflags_per_moving_body"]["Mercury"])
        self.assertEqual(["MOSEPH"], bundle["provider"]["effective_backends_per_moving_body"]["Mercury"])
        self.assertEqual("swiss-host-natal-v1", bundle["provider"]["natal_source_provider"])
        self.assertEqual(1, len(bundle["facts"]["events"]))
        self.assertEqual("house_context", bundle["facts"]["events"][0]["event_kind"])

    def test_mixed_backend_natal_baseline_is_rejected(self):
        with self.assertRaisesRegex(SwissTransitProviderInputError, "swiss-host-natal-v1"):
            build_transit_bundle(
                _natal("astronomy-engine-natal-v1"),
                start_utc="2026-01-01T00:00:00Z",
                end_utc="2026-02-01T00:00:00Z",
                subject_ref="subject:mixed-backend",
                moving_bodies=["Mercury"],
                natal_targets=["Mercury"],
                aspects=["conjunction"],
            )

    def test_window_outside_de440_validated_range_is_rejected(self):
        with self.assertRaisesRegex(SwissTransitProviderInputError, "1950"):
            build_transit_bundle(
                _natal(),
                start_utc="2049-12-15T00:00:00Z",
                end_utc="2050-01-15T00:00:00Z",
                subject_ref="subject:outside-window",
                moving_bodies=["Mercury"],
                natal_targets=["Mercury"],
                aspects=["conjunction"],
            )

    def test_de440_oracle_evidence_keeps_case_specific_scope(self):
        data = json.loads(
            (ROOT / "references/astrology/jpl_de440s_transit_oracle_adjudication.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(
            "pyswisseph_moseph_closer_to_de440s",
            data["mercury_station"]["adjudication"],
        )
        self.assertEqual(
            "pyswisseph_moseph_closer_to_de440s",
            data["venus_210_retrograde_return"]["adjudication"],
        )
        conclusion = data["conclusion"]
        self.assertFalse(conclusion["global_provider_superiority_established"])
        self.assertFalse(conclusion["production_change_authorized"])


if __name__ == "__main__":
    unittest.main()
