from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.astrology_runtime import gate_bundle
from tools.astrology_swiss_provider import build_natal_bundle

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = json.loads(
    (ROOT / "tests" / "fixtures" / "astrology_provider_sydney_1990.json").read_text(
        encoding="utf-8"
    )
)


class FakeSwiss:
    FLG_JPLEPH = 1
    FLG_SWIEPH = 2
    FLG_MOSEPH = 4
    FLG_SPEED = 256
    ECL2HOR = 0
    SUN, MOON, MERCURY, VENUS, MARS = range(5)
    JUPITER, SATURN, URANUS, NEPTUNE, PLUTO = range(5, 10)
    MEAN_NODE = 10
    version = "2.10.03-fake"

    BODY = {
        SUN: ("Sun", 0.95),
        MOON: ("Moon", 13.2),
        MERCURY: ("Mercury", 1.6),
        VENUS: ("Venus", 1.1),
        MARS: ("Mars", 0.7),
        JUPITER: ("Jupiter", 0.2),
        SATURN: ("Saturn", -0.05),
        URANUS: ("Uranus", -0.03),
        NEPTUNE: ("Neptune", -0.02),
        PLUTO: ("Pluto", -0.02),
        MEAN_NODE: ("NorthNode", -0.05),
    }

    @staticmethod
    def julday(*_args):
        return 2448057.5

    @staticmethod
    def calc_ut(_jd, body, _flags):
        name, speed = FakeSwiss.BODY[body]
        lon = FIXTURE["expected"]["longitudes"][name]
        retflag = 258 if name == "NorthNode" else 260
        return (lon, 0.0, 1.0, speed, 0.0, 0.0), retflag

    @staticmethod
    def houses_ex(_jd, _lat, _lon, code):
        e = FIXTURE["expected"]
        if code == b"W":
            asc = e["ascendant"]
            start = int(asc // 30) * 30.0
            cusps = tuple((start + i * 30.0) % 360.0 for i in range(12))
        else:
            c = e["cusps"]
            known = {
                1:c["1"], 2:c["2"], 3:c["3"],
                10:c["10"], 11:c["11"], 12:c["12"],
            }
            known[4]=(known[10]+180)%360
            known[5]=(known[11]+180)%360
            known[6]=(known[12]+180)%360
            known[7]=(known[1]+180)%360
            known[8]=(known[2]+180)%360
            known[9]=(known[3]+180)%360
            cusps=tuple(known[i] for i in range(1,13))
        return cusps, (e["ascendant"], e["midheaven"], 0,0,0,0,0,0)

    @staticmethod
    def azalt(*_args):
        return 0.0, 30.0, 30.0


class AstrologySwissProviderTests(unittest.TestCase):
    def _fake_bundle(self, house_system="Placidus"):
        inp = FIXTURE["input"]
        with patch(
            "tools.astrology_swiss_provider._load_swisseph",
            return_value=FakeSwiss,
        ):
            return build_natal_bundle(
                local_datetime=inp["local_datetime"],
                timezone_name=inp["timezone_name"],
                latitude=inp["latitude"],
                longitude=inp["longitude"],
                house_system=house_system,
                subject_ref="subject:synthetic-swiss-sydney",
            )

    def test_fake_host_runtime_emits_runtime_admitted_fact_bundle(self):
        bundle = self._fake_bundle()
        self.assertTrue(gate_bundle(bundle)["interpretation_allowed"])
        self.assertEqual("swiss-host-natal-v1", bundle["provider"]["provider_id"])
        self.assertEqual("chatgpt_host_preinstalled", bundle["provider"]["runtime_source"])

    def test_provenance_preserves_effective_backend_and_retflags(self):
        provider = self._fake_bundle()["provider"]
        self.assertEqual(260, provider["actual_retflag_per_calculated_object"]["Sun"])
        self.assertEqual(258, provider["actual_retflag_per_calculated_object"]["NorthNode"])
        self.assertEqual("MOSEPH", provider["effective_backend_per_calculated_object"]["Sun"])
        self.assertEqual("SWIEPH", provider["effective_backend_per_calculated_object"]["NorthNode"])

    def test_sydney_fixture_house_placements_match(self):
        bundle = self._fake_bundle()
        objects = {row["object_id"]:row for row in bundle["facts"]["objects"]}
        for body, house in FIXTURE["expected"]["houses"].items():
            self.assertEqual(house, objects[body]["house_number"])

    def test_whole_sign_uses_same_fact_bundle_contract(self):
        bundle = self._fake_bundle("Whole Sign")
        self.assertTrue(gate_bundle(bundle)["interpretation_allowed"])
        self.assertEqual("Whole Sign", bundle["configuration"]["house_system"])

    @unittest.skipUnless(
        importlib.util.find_spec("swisseph") is not None,
        "host swisseph not installed",
    )
    def test_live_host_sydney_core_geometry_within_existing_tolerance(self):
        inp = FIXTURE["input"]
        bundle = build_natal_bundle(
            local_datetime=inp["local_datetime"],
            timezone_name=inp["timezone_name"],
            latitude=inp["latitude"],
            longitude=inp["longitude"],
            house_system=inp["house_system"],
            subject_ref="subject:live-host-swiss-sydney",
        )
        tol = FIXTURE["tolerance_deg"]
        objects = {row["object_id"]:row for row in bundle["facts"]["objects"]}
        for body, lon in FIXTURE["expected"]["longitudes"].items():
            self.assertAlmostEqual(lon, objects[body]["longitude_deg"], delta=tol)
        self.assertAlmostEqual(
            FIXTURE["expected"]["ascendant"],
            objects["Ascendant"]["longitude_deg"],
            delta=tol,
        )
        self.assertAlmostEqual(
            FIXTURE["expected"]["midheaven"],
            objects["Midheaven"]["longitude_deg"],
            delta=tol,
        )


if __name__ == "__main__":
    unittest.main()
