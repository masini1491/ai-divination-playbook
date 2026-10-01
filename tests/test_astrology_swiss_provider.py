from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.astrology_runtime import gate_bundle
from tools.astrology_evidence_selector import select_evidence
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


class FakeJplSwiss(FakeSwiss):
    @staticmethod
    def calc_ut(_jd, body, _flags):
        name, speed = FakeSwiss.BODY[body]
        lon = FIXTURE["expected"]["longitudes"][name]
        return (lon, 0.0, 1.0, speed, 0.0, 0.0), 257


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
        self.assertEqual("host_preinstalled_only", bundle["provider"]["runtime_source"])
        self.assertEqual("PySwissEph", bundle["provider"]["provider_api_family"])
        self.assertEqual("MIXED_SWIEPH_MOSEPH", bundle["provider"]["effective_backend_summary"])

    def test_provenance_preserves_effective_backend_and_retflags(self):
        provider = self._fake_bundle()["provider"]
        self.assertEqual(260, provider["actual_retflag_per_calculated_object"]["Sun"])
        self.assertEqual(258, provider["actual_retflag_per_calculated_object"]["NorthNode"])
        self.assertEqual("MOSEPH", provider["effective_backend_per_calculated_object"]["Sun"])
        self.assertEqual("SWIEPH", provider["effective_backend_per_calculated_object"]["NorthNode"])

    def test_backend_summary_does_not_relabel_mixed_as_swieph_data(self):
        provider = self._fake_bundle()["provider"]
        self.assertEqual("MIXED_SWIEPH_MOSEPH", provider["effective_backend_summary"])
        admission = json.loads(
            (ROOT / "admissions/astrology/ASTROLOGY_SWISS_PROVIDER_ADMISSION_V1.json").read_text(
                encoding="utf-8"
            )
        )
        wording = admission["calculation_policy"]["terminology_contract"][
            "MIXED_SWIEPH_MOSEPH"
        ]
        self.assertIn("must not imply all facts used Swiss Ephemeris data", wording)


    def test_sydney_fixture_house_placements_match(self):
        bundle = self._fake_bundle()
        objects = {row["object_id"]:row for row in bundle["facts"]["objects"]}
        for body, house in FIXTURE["expected"]["houses"].items():
            self.assertEqual(house, objects[body]["house_number"])

    def test_whole_sign_uses_same_fact_bundle_contract(self):
        bundle = self._fake_bundle("Whole Sign")
        self.assertTrue(gate_bundle(bundle)["interpretation_allowed"])
        self.assertEqual("Whole Sign", bundle["configuration"]["house_system"])

    def test_north_node_explicit_mean_provenance_reaches_typed_semantics(self):
        bundle = self._fake_bundle()
        node = next(
            row for row in bundle["facts"]["objects"]
            if row.get("object_id") == "NorthNode"
        )
        self.assertEqual("mean", node["node_definition"])

        run = {
            "schema_name": "astrology_reading_run",
            "schema_version": "1.0.0",
            "status": "admitted",
            "interpretation_allowed": True,
            "normalized_request": {
                "semantic_profile": "composable-symbolic-modern-v1",
                "semantic_profile_selection": "project_default",
            },
            "fact_bundles": {"natal": bundle},
            "runtime_gates": {"natal": gate_bundle(bundle)},
        }
        typed = {
            "schema_name": "astrology_typed_evidence_selection_request",
            "schema_version": "1.0.0",
            "question_id": "swiss-north-node-provenance",
            "question": "What bounded symbolic North Node interpretation is admitted?",
            "fact_selectors": [{
                "selector_id": "node",
                "selector_kind": "object",
                "bundle": "natal",
                "cardinality": "exactly_one",
                "object_id": "NorthNode",
                "object_type": "point",
            }],
            "claim_selectors": [{
                "selector_id": "node-function",
                "registry_record_id": "north-node-sign-semantics-research-v1",
                "semantic_profile": "composable-symbolic-modern-v1",
                "claim_type": "north_node_function",
                "applicability_scope": "north_node_core",
                "applies_to_all": ["natal"],
                "fact_selector_ids": ["node"],
            }],
            "unsupported_factors": [],
        }
        selection = select_evidence(run, typed, repo_root=ROOT)
        self.assertEqual("selected", selection["status"])
        self.assertEqual(
            "claim:north-node-function:growth-edge",
            selection["claim_requests"][0]["claim_id"],
        )

    def test_manifest_required_provenance_matches_emitted_provider_keys(self):
        bundle = self._fake_bundle()
        admission = json.loads(
            (ROOT / "admissions/astrology/ASTROLOGY_SWISS_PROVIDER_ADMISSION_V1.json").read_text(
                encoding="utf-8"
            )
        )
        provider = bundle["provider"]
        for key in admission["calculation_policy"]["required_provenance"]:
            self.assertIn(key, provider)


    def test_unadmitted_jpl_backend_fails_safe(self):
        inp = FIXTURE["input"]
        with patch(
            "tools.astrology_swiss_provider._load_swisseph",
            return_value=FakeJplSwiss,
        ):
            with self.assertRaisesRegex(
                Exception, "unadmitted effective backend"
            ):
                build_natal_bundle(
                    local_datetime=inp["local_datetime"],
                    timezone_name=inp["timezone_name"],
                    latitude=inp["latitude"],
                    longitude=inp["longitude"],
                    house_system=inp["house_system"],
                    subject_ref="subject:jpl-not-admitted",
                )

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
