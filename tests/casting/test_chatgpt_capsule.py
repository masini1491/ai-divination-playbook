import base64
import hashlib
import json
import sys
import unittest
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CASTING_ROOT = ROOT / "runtime" / "casting"
TOOLS_ROOT = ROOT / "tools"
for path in (CASTING_ROOT, TOOLS_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import core
import randomizer
import build_runtime_capsule


class ChatGPTRuntimeCapsuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core_path = CASTING_ROOT / "core.py"
        cls.capsule_path = CASTING_ROOT / "CHATGPT_RUNTIME_CAPSULE.json"
        cls.core_bytes = cls.core_path.read_bytes()
        cls.capsule = json.loads(cls.capsule_path.read_text(encoding="utf-8"))

    def test_capsule_is_derived_transport_only(self):
        self.assertEqual(self.capsule["schema_version"], 1)
        self.assertEqual(self.capsule["authority"], "derived-transport-cache-only")
        self.assertEqual(self.capsule["source_repository"], "masini1491/ai-divination-playbook")
        self.assertEqual(self.capsule["source_path"], "runtime/casting/core.py")
        self.assertEqual(self.capsule["payload_encoding"], "base64+zlib")

    def test_capsule_round_trips_exact_core_bytes(self):
        decoded = zlib.decompress(base64.b64decode(self.capsule["payload"], validate=True))
        self.assertEqual(decoded, self.core_bytes)
        self.assertEqual(len(decoded), self.capsule["decoded_size"])
        self.assertEqual(hashlib.sha256(decoded).hexdigest(), self.capsule["decoded_sha256"])

    def test_capsule_stays_bounded_for_model_mediated_transport(self):
        self.assertLessEqual(len(self.capsule["payload"]), 5000)
        self.assertLessEqual(self.capsule["decoded_size"], 8192)

    def test_generator_matches_committed_capsule(self):
        self.assertEqual(build_runtime_capsule.build_capsule(), self.capsule)

    def test_randomizer_reuses_canonical_core_functions(self):
        self.assertIs(randomizer.draw_tarot, core.draw_tarot)
        self.assertIs(randomizer.cast_plum, core.cast_plum)
        self.assertIs(randomizer.cast_liuyao_coins, core.cast_liuyao_coins)
        self.assertIs(randomizer.make_result, core.make_result)
        self.assertEqual(randomizer.ALGORITHM_VERSION, core.ALGORITHM_VERSION)
        self.assertEqual(randomizer.DECK, core.DECK)
        self.assertEqual(randomizer.TRIGRAM, core.TRIGRAM)
        self.assertEqual(randomizer.HEXAGRAM, core.HEXAGRAM)

    def test_capsule_metadata_matches_core_identity(self):
        self.assertEqual(self.capsule["core_version"], core.CORE_VERSION)
        self.assertEqual(self.capsule["algorithm_version"], core.ALGORITHM_VERSION)
        self.assertEqual(self.capsule["supported_methods"], list(core.SUPPORTED_METHODS))


if __name__ == "__main__":
    unittest.main()
