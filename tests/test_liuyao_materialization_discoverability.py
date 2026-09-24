from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "PLAYBOOK_INDEX.json"
MATRIX = ROOT / "evals" / "regression_matrix.json"
SCENARIO = ROOT / "evals" / "LIUYAO_MATERIALIZATION_PRODUCT_SCENARIO.md"


class LiuyaoMaterializationDiscoverabilityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.index = json.loads(INDEX.read_text(encoding="utf-8"))
        self.matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
        self.scenario = SCENARIO.read_text(encoding="utf-8")

    def test_machine_index_exposes_transport_without_changing_owner(self) -> None:
        capability = next(
            item for item in self.index["capabilities"] if item["id"] == "method.liuyao"
        )
        self.assertEqual("LIUYAO.md", capability["owner"])
        self.assertEqual(
            "LIUYAO_MATERIALIZATION.md",
            capability["materialization_contract"],
        )
        self.assertEqual(
            "runtime/liuyao/CHATGPT_DETERMINISTIC_TOOL_BUNDLE.json",
            capability["deterministic_transport_bundle"],
        )
        self.assertEqual(
            "tools/build_liuyao_tool_bundle.py",
            capability["transport_generator"],
        )
        self.assertEqual(
            "evals/LIUYAO_MATERIALIZATION_PRODUCT_SCENARIO.md",
            capability["materialization_product_scenario"],
        )

    def test_supporting_scenario_is_registered_without_expanding_strict_baseline(self) -> None:
        self.assertEqual(
            "evals/LIUYAO_MATERIALIZATION_PRODUCT_SCENARIO.md",
            self.matrix["supporting_product_scenarios"][
                "liuyao-deterministic-materialization"
            ],
        )
        self.assertNotIn("LIUYAO-MAT-BEH-001", self.matrix["full_baseline"])
        self.assertIn("LIUYAO-MAT-BEH-001", self.scenario)
        self.assertIn("does **not** alter the existing strict-P4", self.scenario)

    def test_materialization_regression_class_covers_existing_boundaries(self) -> None:
        self.assertEqual(
            [
                "TAROT-BEH-004",
                "TAROT-BEH-006",
                "TAROT-BEH-007",
                "TAROT-BEH-012",
                "TAROT-BEH-025",
            ],
            self.matrix["change_classes"]["liuyao-deterministic-materialization"],
        )

    def test_scenario_forbids_premature_unavailable_and_preserves_cast_identity(self) -> None:
        required = (
            "local cache miss as a materialization trigger",
            "same-commit deterministic bundle path",
            "bundle_verification.json",
            "Produce the Structured Method Fact before `LIUYAO.md` interpretation",
            "immediately classify the engine or Structured Method Fact as unavailable",
            "replace the original `cast_timestamp`",
        )
        for phrase in required:
            self.assertIn(phrase, self.scenario)


if __name__ == "__main__":
    unittest.main()
