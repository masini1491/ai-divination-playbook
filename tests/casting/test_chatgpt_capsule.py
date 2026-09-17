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
        self.assertEqual(self.capsule["schema_version"], 2)
        self.assertEqual(self.capsule["authority"], "derived-transport-cache-only")
        self.assertEqual(self.capsule["source_repository"], "masini1491/ai-divination-playbook")
        self.assertEqual(self.capsule["source_path"], "runtime/casting/core.py")
        self.assertEqual(self.capsule["payload_encoding"], "base64+zlib")
        self.assertEqual(self.capsule["chunk_encoding"], "ascii")

    def test_capsule_declares_same_turn_chunked_retry_contract(self):
        self.assertEqual(
            self.capsule["transport_contract"],
            "chunked-model-mediated-opaque-handoff-v2",
        )
        self.assertFalse(self.capsule["automatic_object_bridge_required"])
        self.assertTrue(self.capsule["must_attempt_when_python_available"])
        self.assertTrue(self.capsule["same_turn_attempt_required"])
        self.assertTrue(self.capsule["missing_automatic_bridge_is_not_gap"])
        self.assertTrue(self.capsule["chunk_retry_required_on_mismatch"])
        self.assertEqual(self.capsule["chunk_reassembly"], "index-ascending-concat")
        self.assertEqual(self.capsule["chunk_retry_limit"], build_runtime_capsule.CHUNK_RETRY_LIMIT)
        self.assertEqual(
            self.capsule["chunk_retry_source"],
            "fresh-same-commit-capsule-read",
        )

    def test_capsule_declares_machine_visible_cache_contract(self):
        contract = self.capsule["cache_contract"]
        self.assertEqual(
            contract["marker_filename"],
            build_runtime_capsule.CACHE_MARKER_FILENAME,
        )
        self.assertEqual(
            contract["cache_locator_version"],
            build_runtime_capsule.CACHE_LOCATOR_VERSION,
        )
        self.assertTrue(contract["marker_write_required_before_execution"])
        self.assertTrue(contract["marker_readback_required_before_execution"])
        self.assertTrue(contract["post_write_probe_required_before_execution"])
        self.assertEqual(
            contract["required_marker_fields"],
            build_runtime_capsule.CACHE_REQUIRED_MARKER_FIELDS,
        )

    def test_each_chunk_has_exact_length_and_hash(self):
        chunks = self.capsule["chunks"]
        self.assertEqual(len(chunks), self.capsule["chunk_count"])
        self.assertEqual([chunk["index"] for chunk in chunks], list(range(len(chunks))))
        for chunk in chunks:
            payload = chunk["payload"]
            self.assertEqual(len(payload), chunk["encoded_length"])
            self.assertLessEqual(len(payload), build_runtime_capsule.MAX_CHUNK_CHARS)
            self.assertEqual(
                hashlib.sha256(payload.encode("ascii")).hexdigest(),
                chunk["encoded_sha256"],
            )

    def test_capsule_round_trips_exact_core_bytes(self):
        payload = "".join(chunk["payload"] for chunk in self.capsule["chunks"])
        self.assertEqual(len(payload), self.capsule["encoded_size"])
        decoded = zlib.decompress(base64.b64decode(payload, validate=True))
        self.assertEqual(decoded, self.core_bytes)
        self.assertEqual(len(decoded), self.capsule["decoded_size"])
        self.assertEqual(hashlib.sha256(decoded).hexdigest(), self.capsule["decoded_sha256"])

    def test_capsule_stays_bounded_for_model_mediated_transport(self):
        self.assertLessEqual(self.capsule["encoded_size"], 5000)
        self.assertLessEqual(self.capsule["chunk_size"], build_runtime_capsule.MAX_CHUNK_CHARS)
        self.assertLessEqual(self.capsule["decoded_size"], 8192)

    def test_generator_matches_committed_capsule(self):
        self.assertEqual(build_runtime_capsule.build_capsule(), self.capsule)

    def test_randomizer_reuses_canonical_core_execution(self):
        self.assertIs(randomizer.execute_stochastic, core.execute_stochastic)
        self.assertEqual(randomizer.ALGORITHM_VERSION, core.ALGORITHM_VERSION)
        self.assertEqual(randomizer.SCHEMA_VERSION, core.SCHEMA_VERSION)
        self.assertEqual(randomizer.SOURCE, core.SOURCE)
        self.assertEqual(randomizer.DECK, core.DECK)
        self.assertEqual(randomizer.TRIGRAM, core.TRIGRAM)
        self.assertEqual(randomizer.HEXAGRAM, core.HEXAGRAM)
        payload = core.execute_stochastic("tarot", count=1, source_commit="test")
        self.assertTrue(payload["generated_at_utc"].endswith("+00:00"))
        self.assertTrue(payload["generated_at_taipei"].endswith("+08:00"))
        self.assertEqual(payload["timezone"], "Asia/Taipei")
        self.assertEqual(payload["results"][0]["method"], "tarot")

    def test_core_exposes_no_public_bare_stochastic_primitive(self):
        for name in ("draw_tarot", "cast_plum", "cast_liuyao_coins", "make_result"):
            self.assertFalse(hasattr(core, name), name)

    def test_capsule_metadata_matches_core_identity(self):
        self.assertEqual(self.capsule["core_version"], core.CORE_VERSION)
        self.assertEqual(self.capsule["algorithm_version"], core.ALGORITHM_VERSION)
        self.assertEqual(self.capsule["supported_methods"], list(core.SUPPORTED_METHODS))


if __name__ == "__main__":
    unittest.main()
