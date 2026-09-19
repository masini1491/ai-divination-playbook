from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class BehavioralEvalLoaderSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.behavioral_eval = load_module(
            ROOT / "tools" / "behavioral_eval.py",
            "behavioral_eval",
        )

    def test_current_matrix_is_valid_for_behavioral_eval_tool(self):
        matrix = json.loads(
            (ROOT / "evals" / "regression_matrix.json").read_text(encoding="utf-8")
        )
        self.assertEqual(self.behavioral_eval.validate_regression_matrix(matrix), [])

    def test_loader_change_class_covers_cold_start_runtime_freshness_and_astrology(self):
        matrix = json.loads(
            (ROOT / "evals" / "regression_matrix.json").read_text(encoding="utf-8")
        )
        selected = set(
            self.behavioral_eval.select_regression_scenarios(
                matrix,
                "loader-optimization",
            )
        )
        required = {
            "TAROT-BEH-001",
            "TAROT-BEH-002",
            "TAROT-BEH-003",
            "TAROT-BEH-005",
            "TAROT-BEH-013",
            "TAROT-BEH-016",
            "TAROT-BEH-018",
            "TAROT-BEH-019",
        }
        self.assertTrue(required.issubset(selected))


if __name__ == "__main__":
    unittest.main()
