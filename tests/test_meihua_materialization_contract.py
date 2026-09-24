from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
MATERIALIZATION = ROOT / "MEIHUA_MATERIALIZATION.md"
GENERATOR_PATH = ROOT / "tools" / "build_meihua_tool_bundle.py"
BUNDLE_PATH = ROOT / "runtime" / "meihua" / "CHATGPT_DETERMINISTIC_TOOL_BUNDLE.json"


def load_generator():
    spec = importlib.util.spec_from_file_location("build_meihua_tool_bundle", GENERATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Meihua bundle generator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MeihuaMaterializationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.materialization = MATERIALIZATION.read_text(encoding="utf-8")
        cls.generator = load_generator()
        cls.bundle = json.loads(BUNDLE_PATH.read_text(encoding="utf-8"))

    def test_committed_bundle_matches_generator(self) -> None:
        expected = self.generator.build_bundle()
        self.assertEqual(self.generator.render(expected), self.generator.render(self.bundle))
        self.assertEqual([], self.generator.verify(self.bundle))

    def test_persistent_cache_contract_is_explicit(self) -> None:
        cache = self.bundle["cache_contract"]
        self.assertEqual("/mnt/data/divination-meihua-runtime", cache["cache_dir"])
        self.assertEqual("bundle_verification.json", cache["marker"])
        self.assertIn("materialized_source_commit", cache["required_marker_fields"])
        self.assertIn("last_checked_repository_head", cache["required_marker_fields"])
        self.assertTrue(cache["reuse_only_when_source_file_identity_matches"])

    def test_identity_first_refresh_is_source_path_scoped(self) -> None:
        for phrase in (
            "materialized_source_commit",
            "last_checked_repository_head",
            "Identity-first deterministic refresh",
            "tools/meihua_engine.py",
            "MUST NOT fetch bundle / rematerialize",
        ):
            self.assertIn(phrase, self.materialization)


if __name__ == "__main__":
    unittest.main()
