from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PRODUCT_RUNS = ROOT / "evals" / "product_runs"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class BehavioralProductRunRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.behavioral = load_module(
            ROOT / "tools" / "behavioral_eval.py",
            "behavioral_eval_product_runs",
        )

    def test_all_committed_product_run_records_validate(self):
        paths = sorted(PRODUCT_RUNS.glob("*.json"))
        self.assertTrue(paths)
        for path in paths:
            with self.subTest(path=path.name):
                record = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(
                    self.behavioral.validate_record(record),
                    [],
                )


if __name__ == "__main__":
    unittest.main()
