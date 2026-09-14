import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CASTING_ROOT = ROOT / "runtime" / "casting"
MANIFEST_PATH = CASTING_ROOT / "MIGRATION_SOURCE.json"

PINNED_LEGACY_COMMIT = "17cc4c84fd5c09b60de721b671c1d6511ab3d0e9"
PINNED_LEGACY_TREE = "f29bde4b6556fadd15ad69bd627f134a299cf94d"
PINNED_LEGACY_PRODUCTION_FILES = {
    "API.md": "51d6dad99c6255ad0897c4ca0d8ba2d909e99d62",
    "api/__init__.py": "d79cebc3faf6afade6c32ce8d1a58ac530bc1deb",
    "api/cast.py": "89d0934d62ec4ca8860e5940d665c02a3a7d3b9c",
    "contract_vectors.json": "831fd7e8758d3b4f6ac92c17c758582cf4685c51",
    "index.html": "595ce514c3e4446b1b900d86a888cb5fc8c9b111",
    "openapi.json": "6100b09c9a86527302dfc3584be3f04ad9a00a90",
    "randomizer.py": "4bc4677459edec57e5dcb73d2d48e08fc3058663",
}
PINNED_LEGACY_RUNTIME_IDENTITY = {
    "source": "divination-casting-randomizer-python",
    "algorithm_version": "2",
    "schema_version": "4",
    "ai_schema_version": "1",
}


class MigrationProvenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    def test_manifest_preserves_legacy_import_provenance_after_production_cutover(self):
        self.assertEqual(self.manifest["schema_version"], 1)
        self.assertEqual(self.manifest["authority"], "migration-provenance")
        self.assertEqual(self.manifest["source_repository"], "masini1491/divination-casting-randomizer")
        self.assertEqual(self.manifest["source_commit"], PINNED_LEGACY_COMMIT)
        self.assertEqual(self.manifest["source_tree"], PINNED_LEGACY_TREE)
        self.assertEqual(self.manifest["candidate_root"], "runtime/casting")
        self.assertEqual(self.manifest["cutover_state"], "production-authoritative")
        self.assertEqual(self.manifest["runtime_repository"], "masini1491/ai-divination-playbook")
        self.assertEqual(self.manifest["runtime_path"], "runtime/casting/randomizer.py")
        self.assertEqual(self.manifest["production_deployment_source"], "monorepo")
        self.assertEqual(self.manifest["production_project"], "ai-divination-playbook-casting")
        self.assertEqual(self.manifest["production_root_directory"], "runtime/casting")

    def test_manifest_keeps_exact_legacy_import_blob_record(self):
        self.assertEqual(self.manifest["production_files"], PINNED_LEGACY_PRODUCTION_FILES)

    def test_manifest_keeps_import_time_runtime_identity_record(self):
        self.assertEqual(self.manifest["runtime_identity"], PINNED_LEGACY_RUNTIME_IDENTITY)


if __name__ == "__main__":
    unittest.main()
