from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
GENERATOR_PATH = ROOT / "tools" / "build_liuyao_tool_bundle.py"
BUNDLE_PATH = ROOT / "runtime" / "liuyao" / "CHATGPT_DETERMINISTIC_TOOL_BUNDLE.json"


def load_generator():
    spec = importlib.util.spec_from_file_location("build_liuyao_tool_bundle", GENERATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Liuyao bundle generator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class LiuyaoToolBundleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.generator = load_generator()
        cls.bundle = json.loads(BUNDLE_PATH.read_text(encoding="utf-8"))

    def test_committed_bundle_matches_generator(self) -> None:
        expected = self.generator.build_bundle()
        self.assertEqual(self.generator.render(expected), self.generator.render(self.bundle))
        self.assertEqual([], self.generator.verify_bundle(self.bundle))

    def test_bundle_is_derived_transport_only(self) -> None:
        self.assertEqual("derived-transport-cache-only", self.bundle["authority"])
        self.assertEqual(
            "chunked-model-mediated-deterministic-tool-bundle-v1",
            self.bundle["contract"],
        )
        contract = self.bundle["execution_contract"]
        self.assertFalse(contract["interpretation_authority"])
        self.assertFalse(contract["yongshen_selection_authority"])

    def test_bundle_contains_only_deterministic_liuyao_tools(self) -> None:
        paths = [item["path"] for item in self.bundle["source_files"]]
        self.assertEqual(
            [
                "tools/liuyao_calendar.py",
                "tools/liuyao_engine.py",
                "tools/liuyao_runtime.py",
            ],
            paths,
        )
        self.assertNotIn("runtime/casting/core.py", paths)
        self.assertNotIn("runtime/casting/randomizer.py", paths)

    def test_bundle_requires_preserving_existing_cast_identity(self) -> None:
        contract = self.bundle["execution_contract"]
        self.assertTrue(contract["must_attempt_after_verified_local_cache_miss"])
        self.assertTrue(contract["preserve_raw_cast"])
        self.assertTrue(contract["preserve_cast_timestamp"])
        self.assertTrue(contract["verify_each_chunk_before_reassembly"])
        self.assertTrue(contract["verify_archive_before_unpack"])
        self.assertTrue(contract["verify_each_file_before_write_or_import"])

    def test_cache_contract_separates_source_and_current_head(self) -> None:
        cache = self.bundle["cache_contract"]
        self.assertEqual("/mnt/data/divination-liuyao-runtime", cache["cache_dir"])
        self.assertEqual("bundle_verification.json", cache["marker"])
        self.assertIn("materialized_source_commit", cache["required_marker_fields"])
        self.assertIn("last_checked_repository_head", cache["required_marker_fields"])
        self.assertNotIn("playbook_commit", cache["required_marker_fields"])
        self.assertTrue(cache["reuse_only_when_all_source_file_identities_match"])

    def test_chunk_contract_is_bounded_and_retryable(self) -> None:
        archive = self.bundle["archive"]
        self.assertEqual(444, archive["chunk_size"])
        self.assertEqual(2, archive["chunk_retry_limit"])
        self.assertEqual("index-ascending-concat", archive["reassembly"])
        self.assertEqual(len(self.bundle["chunks"]), archive["chunk_count"])
        self.assertTrue(all(item["encoded_length"] <= 444 for item in self.bundle["chunks"]))


if __name__ == "__main__":
    unittest.main()
