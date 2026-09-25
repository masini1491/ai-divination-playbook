from __future__ import annotations
import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]

class ZiWeiMaterializationDiscoverabilityTests(unittest.TestCase):
    def setUp(self):
        self.index=json.loads((ROOT/"PLAYBOOK_INDEX.json").read_text(encoding="utf-8"))
        self.matrix=json.loads((ROOT/"evals"/"regression_matrix.json").read_text(encoding="utf-8"))
        self.contract=(ROOT/"ZIWEI_MATERIALIZATION.md").read_text(encoding="utf-8")
        self.scenario=(ROOT/"evals"/"ZIWEI_MATERIALIZATION_PRODUCT_SCENARIO.md").read_text(encoding="utf-8")

    def test_index_exposes_transport_without_owner_change(self):
        c=next(x for x in self.index["capabilities"] if x["id"]=="method.ziwei")
        self.assertEqual("ZIWEI.md",c["owner"])
        self.assertEqual("ZIWEI_MATERIALIZATION.md",c["materialization_contract"])
        self.assertEqual("runtime/ziwei/CHATGPT_DETERMINISTIC_TOOL_BUNDLE.json",c["deterministic_transport_bundle"])
        self.assertEqual("tools/build_ziwei_tool_bundle.py",c["transport_generator"])

    def test_supporting_scenario_registered_only(self):
        self.assertEqual("evals/ZIWEI_MATERIALIZATION_PRODUCT_SCENARIO.md",
                         self.matrix["supporting_product_scenarios"]["ziwei-deterministic-materialization"])
        self.assertNotIn("ZIWEI-MAT-BEH-001",self.matrix["full_baseline"])
        self.assertIn("TAROT-BEH-025",self.matrix["change_classes"]["ziwei-deterministic-materialization"])
        self.assertIn("does **not** alter the existing strict-P4",self.scenario)

    def test_contract_covers_query_bounded_calendar_materialization(self):
        for phrase in (
            "local cache miss ≠ Zi Wei unavailable",
            "query-bounded",
            "ordinary Gregorian request → 1 year shard",
            "31 December 23:00 cross-year edge → at most 2 year shards",
            "lunar_python==1.4.8",
            "build/parity dependency only",
            "does not require pip/network installation afterward",
            "probe /mnt/data/divination-ziwei-runtime/",
            "direct byte/file-aware handoff available",
            "No Full-Bundle-First Rule",
            "Acquisition: PASS | NOT ESTABLISHED",
            "Payload handoff: VERIFIED | UNAVAILABLE | NOT ESTABLISHED",
            "local cache existence does not mean the cache identity is verified",
        ):
            self.assertIn(phrase,self.contract)

    def test_product_scenario_prefers_cache_then_host_aware_fallback(self):
        for phrase in (
            "probes and verifies the local Zi Wei runtime cache before any bundle acquisition",
            "direct byte/file-aware connector→filesystem handoff",
            "must not move the whole bundle through model-visible context",
            "acquisition success does not imply payload handoff, materialization, integrity, or execution success",
        ):
            self.assertIn(phrase,self.scenario)

if __name__=="__main__": unittest.main()
