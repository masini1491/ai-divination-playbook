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
        self.assertEqual("production-admitted-profile-500-query-bounded",c["place_resolver_materialization_status"])
        self.assertEqual("reports/astrology/ASTROLOGY_PLACE_RESOLVER_MATERIALIZATION_FEASIBILITY.md",c["place_resolver_materialization_decision"])
        self.assertIn("profile-500-query-bounded-shards",c["place_resolver_cold_start_fallback"])

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
            "The original whole-package / model-mediated A-MAT-2 transport remains rejected",
            "production-admitted for the default profile `500` only",
            "never silently substitute profile 500",
        ):
            self.assertIn(phrase,self.contract)

    def test_runtime_reuse_and_host_integration_binding(self):
        for phrase in (
            "Runtime Reuse / Host Integration Fast Path",
            "probe /mnt/data/divination-astrology-runtime/core_bundle_verification.json",
            "Current `main` 前進本身 **不等於 cache automatically invalid**",
            "Host Capability Gate / No Full-Bundle-First Rule",
            "direct byte/file-aware handoff",
            "不得在 cache reuse probe完成前",
            "Acquisition: PASS | NOT ESTABLISHED",
            "Payload handoff: VERIFIED | UNAVAILABLE | NOT ESTABLISHED",
            "GitHub Connect acquisition PASS 不等於 filesystem materialization VERIFIED",
        ):
            self.assertIn(phrase,self.contract)

    def test_product_scenario_prefers_cache_then_host_aware_fallback(self):
        for phrase in (
            "probes and verifies the local Astrology runtime cache before any bundle acquisition",
            "direct byte/file-aware connector→filesystem handoff",
            "must not move the whole bundle/chunks through model-visible context",
            "acquisition success does not imply payload handoff, materialization, integrity, or execution success",
            "whole GeoNames dataset is not transported merely to resolve one place",
        ):
            self.assertIn(phrase,self.scenario)

    def test_root_owner_routes_runtime_miss_to_materialization(self):
        text=(ROOT/"ASTROLOGY.md").read_text(encoding="utf-8")
        self.assertIn("ASTROLOGY_MATERIALIZATION.md",text)
        self.assertIn("verified cache reuse / Host Capability Gate",text)
        self.assertIn("禁止 full-bundle-first",text)
        self.assertIn("Core materialization只涵蓋 explicit coordinates + IANA timezone",text)

if __name__=="__main__": unittest.main()
