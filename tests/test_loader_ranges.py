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


class LoaderRangeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = load_module(
            ROOT / "tools" / "validate_loader_ranges.py",
            "validate_loader_ranges",
        )

    def test_current_ranges_are_valid(self):
        self.assertEqual(self.validator.validate(ROOT), [])

    def test_core_bypass_ranges_are_declared(self):
        index = json.loads((ROOT / "PLAYBOOK_INDEX.json").read_text(encoding="utf-8"))
        ranges = index["loader"]["bounded_ranges"]
        expected = {
            "bootstrap.default_interaction",
            "explicit_astrology.routing_scope",
            "explicit_research.intent_gate",
            "research.astrology.scope",
        }
        self.assertTrue(expected.issubset(ranges))
        self.assertEqual(
            index["loader"]["range_locator_policy"]["kind"],
            "ci-verified-line-range",
        )


if __name__ == "__main__":
    unittest.main()
