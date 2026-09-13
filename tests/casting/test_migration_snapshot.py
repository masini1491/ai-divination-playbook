import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CASTING_ROOT = ROOT / "runtime" / "casting"
MANIFEST_PATH = CASTING_ROOT / "MIGRATION_SOURCE.json"

if str(CASTING_ROOT) not in sys.path:
    sys.path.insert(0, str(CASTING_ROOT))

import randomizer

PINNED_LEGACY_COMMIT = "17cc4c84fd5c09b60de721b671c1d6511ab3d0e9"
PINNED_LEGACY_TREE = "f29bde4b6556fadd15ad69bd627f134a299cf94d"
EXPECTED_PRODUCTION_FILES = {
    "API.md",
    "api/__init__.py",
    "api/cast.py",
    "contract_vectors.json",
    "index.html",
    "openapi.json",
    "randomizer.py",
}


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


class MigrationSnapshotParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    def test_manifest_pins_non_authoritative_legacy_source(self):
        self.assertEqual(self.manifest["schema_version"], 1)
        self.assertEqual(self.manifest["authority"], "migration-candidate-only")
        self.assertEqual(self.manifest["source_repository"], "masini1491/divination-casting-randomizer")
        self.assertEqual(self.manifest["source_commit"], PINNED_LEGACY_COMMIT)
        self.assertEqual(self.manifest["source_tree"], PINNED_LEGACY_TREE)
        self.assertEqual(self.manifest["candidate_root"], "runtime/casting")
        self.assertEqual(self.manifest["cutover_state"], "not-authoritative")
        self.assertEqual(self.manifest["production_deployment_source"], "legacy-repository")

    def test_candidate_production_files_match_pinned_legacy_blobs(self):
        expected = self.manifest["production_files"]
        self.assertEqual(set(expected), EXPECTED_PRODUCTION_FILES)
        for relative_path, expected_blob_sha in sorted(expected.items()):
            with self.subTest(path=relative_path):
                candidate = CASTING_ROOT / relative_path
                self.assertTrue(candidate.is_file())
                self.assertEqual(git_blob_sha(candidate), expected_blob_sha)

    def test_runtime_identity_is_unchanged_by_relocation(self):
        identity = self.manifest["runtime_identity"]
        self.assertEqual(randomizer.SOURCE, identity["source"])
        self.assertEqual(randomizer.ALGORITHM_VERSION, identity["algorithm_version"])
        self.assertEqual(randomizer.SCHEMA_VERSION, identity["schema_version"])
        self.assertEqual(randomizer.AI_SCHEMA_VERSION, identity["ai_schema_version"])
        self.assertEqual(randomizer.SUPPORTED_METHODS, ("tarot", "plum", "liuyao"))


if __name__ == "__main__":
    unittest.main()
