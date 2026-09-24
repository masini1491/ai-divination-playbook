from __future__ import annotations
import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]

class AstrologyMaterializationDiscoverabilityTests(unittest.TestCase):
    def setUp(self):
        self.index=json.loads((ROOT/"PLAYBOOK_INDEX.json").read_text(encoding="utf-8"))
        self.matrix=json.loads((ROOT/"evals"/"regression_matrix.json").read_text(encoding="utf-8"))
        self.contract=(ROOT/"ASTROLOGY_MATERIALIZATION.md").read_text(encoding="utf-8")
        self.scenario=(ROOT/"evals"/"ASTROLOGY_MATERIALIZATION_PRODUCT_SCENARIO.md").read_text(encoding="utf-8")

    def test_index_exposes_core_transport_without_owner_change(self):
        c=next(x for x in self.index["capabilities"] if x["id"]=="method.astrology")
        self.assertEqual("ASTROLOGY.md",c["owner"])
        self.assertEqual("ASTROLOGY_MATERIALIZATION.md",c["materialization_contract"])
        self.assertEqual("runtime/astrology/CHATGPT_DETERMINISTIC_CORE_BUNDLE.json",c["deterministic_core_transport_bundle"])
        self.assertEqual("tools/build_astrology_core_bundle.py",c["core_transport_generator"])
        self.assertIn("place-resolver-excluded",c["core_bundle_scope"])

    def test_supporting_scenario_registered_only(self):
        self.assertEqual("evals/ASTROLOGY_MATERIALIZATION_PRODUCT_SCENARIO.md",
                         self.matrix["supporting_product_scenarios"]["astrology-deterministic-materialization"])
        self.assertNotIn("ASTROLOGY-MAT-BEH-001",self.matrix["full_baseline"])
        self.assertIn("**does not** alter the existing strict-P4",self.scenario)

    def test_contract_keeps_core_and_place_resolution_separate(self):
        for phrase in (
            "local package miss ≠ Astrology unavailable",
            "astronomy-engine==2.1.19",
            "place resolver → separate admitted input-resolution authority",
            "does **not require pip/network installation afterward**",
        ):
            self.assertIn(phrase,self.contract)

    def test_root_owner_routes_runtime_miss_to_materialization(self):
        text=(ROOT/"ASTROLOGY.md").read_text(encoding="utf-8")
        self.assertIn("ASTROLOGY_MATERIALIZATION.md",text)
        self.assertIn("Core materialization只涵蓋 explicit coordinates + IANA timezone",text)

if __name__=="__main__": unittest.main()
