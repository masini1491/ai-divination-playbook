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


class LoaderStrictClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.closure = load_module(
            ROOT / "tools" / "loader_strict_closure.py",
            "loader_strict_closure",
        )

    def test_current_status_is_internally_consistent(self):
        self.assertEqual(self.closure.validate(ROOT), [])

    def test_strict_p4_cannot_pass_without_product_evidence(self):
        errors = self.closure.validate(ROOT, require_product_evidence=True)
        self.assertIn(
            "P4 strict closure requires complete fresh/bounded product evidence",
            errors,
        )


if __name__ == "__main__":
    unittest.main()
