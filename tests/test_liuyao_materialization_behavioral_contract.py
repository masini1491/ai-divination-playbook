from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "PLAYBOOK_INDEX.json"
SCENARIO = ROOT / "evals" / "LIUYAO_MATERIALIZATION_BEHAVIORAL.md"


class LiuyaoMaterializationBehavioralContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.index = json.loads(INDEX.read_text(encoding="utf-8"))
        self.scenario = SCENARIO.read_text(encoding="utf-8")

    def test_index_exposes_materialization_transport_and_behavior_scenario(self) -> None:
        capability = next(
            item for item in self.index["capabilities"] if item["id"] == "method.liuyao"
        )
        self.assertEqual("LIUYAO_MATERIALIZATION.md", capability["materialization_contract"])
        self.assertEqual(
            "runtime/liuyao/CHATGPT_DETERMINISTIC_TOOL_BUNDLE.json",
            capability["deterministic_transport_bundle"],
        )
        self.assertEqual(
            "tools/build_liuyao_tool_bundle.py",
            capability["transport_generator"],
        )
        self.assertEqual(
            "evals/LIUYAO_MATERIALIZATION_BEHAVIORAL.md",
            capability["materialization_behavioral_scenario"],
        )

    def test_behavior_scenario_guards_premature_local_miss_fallback(self) -> None:
        required = (
            "LIUYAO-BEH-001",
            "local deterministic-tool cache miss",
            "不得直接宣告 deterministic engine unavailable",
            "CHATGPT_DETERMINISTIC_TOOL_BUNDLE.json",
            "原 Raw Cast",
            "原 `cast_timestamp`",
            "bundle_verification.json",
            "LIUYAO STRUCTURED FACT UNAVAILABLE",
            "INCONCLUSIVE",
        )
        for phrase in required:
            self.assertIn(phrase, self.scenario)

    def test_supporting_scenario_does_not_claim_strict_p4_membership(self) -> None:
        self.assertIn("不改變 strict P4 scenario set", self.scenario)
        self.assertIn("SUPPORTING PRODUCT BEHAVIOR SCENARIO", self.scenario)


if __name__ == "__main__":
    unittest.main()
