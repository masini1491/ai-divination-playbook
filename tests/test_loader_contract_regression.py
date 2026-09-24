from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class LoaderContractRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.regression = load_module(
            ROOT / "tools" / "loader_contract_regression.py",
            "loader_contract_regression",
        )

    def test_selected_loader_scenarios_have_passing_contract_checks(self):
        self.assertEqual(self.regression.validate(ROOT), [])

    def test_contract_coverage_matches_loader_change_class_exactly(self):
        selected = set(self.regression.selected_scenarios(ROOT))
        declared = set(self.regression.CONTRACTS)
        self.assertEqual(selected, declared)
        self.assertEqual(len(selected), 12)


if __name__ == "__main__":
    unittest.main()
