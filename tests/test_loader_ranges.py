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
        cls.generator = load_module(
            ROOT / "tools" / "build_loader_ranges.py",
            "build_loader_ranges",
        )
        cls.validator = load_module(
            ROOT / "tools" / "validate_loader_ranges.py",
            "validate_loader_ranges",
        )

    def test_generated_ranges_are_current(self):
        self.assertEqual(self.generator.validate_generated(ROOT), [])
        self.assertEqual(self.validator.validate(ROOT), [])

    def test_core_bypass_ranges_are_generated(self):
        index = json.loads((ROOT / "PLAYBOOK_INDEX.json").read_text(encoding="utf-8"))
        ranges = index["loader"]["bounded_ranges"]
        expected = {
            "bootstrap.default_interaction",
            "explicit_astrology.routing_scope",
            "explicit_astrology.natal_entry",
            "explicit_astrology.transit_entry",
            "explicit_research.intent_gate",
            "research.astrology.scope",
        }
        self.assertTrue(expected.issubset(ranges))
        policy = index["loader"]["range_locator_policy"]
        self.assertEqual(policy["kind"], "generated-ci-verified-line-range")
        self.assertEqual(policy["generator"], "tools/build_loader_ranges.py")

    def test_line_numbers_equal_fresh_derivation(self):
        index = json.loads((ROOT / "PLAYBOOK_INDEX.json").read_text(encoding="utf-8"))
        for range_id, committed in index["loader"]["bounded_ranges"].items():
            derived = self.generator.derive_range(ROOT, committed)
            self.assertEqual(committed, derived, range_id)


if __name__ == "__main__":
    unittest.main()
