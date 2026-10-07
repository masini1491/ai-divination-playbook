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
        cls.v3_manifest_path = CASTING_ROOT / "capsule-v3" / "MANIFEST.json"
        cls.core_bytes = cls.core_path.read_bytes()
        cls.capsule = json.loads(cls.capsule_path.read_text(encoding="utf-8"))
        cls.v3_manifest = json.loads(cls.v3_manifest_path.read_text(encoding="utf-8"))

    def test_streaming_v3_manifest_contract(self):
        manifest = self.v3_manifest
        self.assertEqual(manifest["schema_version"], 3)
        self.assertEqual(manifest["authority"], "derived-transport-cache-only")
        self.assertEqual(
            manifest["transport_contract"],
            "streaming-model-mediated-opaque-handoff-v3",
        )
        self.assertEqual(manifest["streaming_fetch"], "one-chunk-file-at-a-time")
        self.assertTrue(manifest["verify_before_next_fetch"])
        self.assertEqual(manifest["chunk_source_identity"], "git-blob-sha1")
        self.assertTrue(manifest["source_identity_before_payload_handoff"])
        self.assertEqual(manifest["chunk_file_terminator"], "LF")
        self.assertEqual(
            manifest["verified_payload_extraction"],
            "exclude-at-most-one-terminal-lf",
        )
        self.assertTrue(manifest["verified_payload_reuse_required"])
        self.assertEqual(
            manifest["chunk_reassembly"],
            "index-ascending-concat-of-retained-verified-payloads",
        )
        self.assertEqual(
            manifest["fallback_transport"],
            "runtime/casting/CHATGPT_RUNTIME_CAPSULE.json",
        )
        self.assertEqual(manifest["source_path"], "runtime/casting/core.py")

    def test_streaming_v3_chunk_files_match_manifest_and_round_trip(self):
        manifest = self.v3_manifest
        parts = []
        self.assertEqual(
            [entry["index"] for entry in manifest["chunks"]],
            list(range(manifest["chunk_count"])),
        )
        for entry in manifest["chunks"]:
            path = ROOT / entry["path"]
            self.assertTrue(path.is_file(), entry["path"])
            raw_bytes = path.read_bytes()
            self.assertEqual(len(raw_bytes), entry["raw_file_size"])
            self.assertEqual(
                build_runtime_capsule._git_blob_sha1(raw_bytes),
                entry["git_blob_sha1"],
            )
            raw = raw_bytes.decode("ascii")
            self.assertFalse(raw.endswith("\n\n"))
            payload = raw[:-1] if raw.endswith("\n") else raw
            self.assertEqual(len(payload), entry["encoded_length"])
            self.assertEqual(
                hashlib.sha256(payload.encode("ascii")).hexdigest(),
                entry["encoded_sha256"],
            )
            parts.append(payload)
        encoded = "".join(parts)
        self.assertEqual(len(encoded), manifest["encoded_size"])
        decoded = zlib.decompress(base64.b64decode(encoded, validate=True))
        self.assertEqual(decoded, self.core_bytes)
        self.assertEqual(len(decoded), manifest["decoded_size"])
        self.assertEqual(hashlib.sha256(decoded).hexdigest(), manifest["decoded_sha256"])

    def test_streaming_v3_and_v2_share_exact_core_identity(self):
        self.assertEqual(self.v3_manifest["decoded_size"], self.capsule["decoded_size"])
        self.assertEqual(self.v3_manifest["decoded_sha256"], self.capsule["decoded_sha256"])
        self.assertEqual(self.v3_manifest["core_version"], self.capsule["core_version"])
        self.assertEqual(self.v3_manifest["algorithm_version"], self.capsule["algorithm_version"])
        self.assertEqual(self.v3_manifest["runtime_invariants"], self.capsule["runtime_invariants"])

    def test_streaming_v3_generator_file_set_matches_committed_artifacts(self):
        expected = build_runtime_capsule._expected_v3_files()
        actual = {p for p in (CASTING_ROOT / "capsule-v3").glob("*") if p.is_file()}
        self.assertEqual(actual, set(expected))
        for path, content in expected.items():
            self.assertEqual(path.read_text(encoding="utf-8"), content)

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
        manifest, _payloads = build_runtime_capsule.build_capsule_v3()
        self.assertEqual(manifest, self.v3_manifest)

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

    def test_capsule_publishes_stable_post_write_probe(self):
        expected = {
            "supported_methods": ["tarot", "plum", "liuyao"],
            "tarot_deck_size": 78,
            "tarot_unique_cards": 78,
            "meihua_trigram_count": 8,
            "meihua_hexagram_pairs": 64,
            "liuyao_line_count": 6,
            "liuyao_line_values": [6, 7, 8, 9],
            "execution_entrypoint": "execute_stochastic",
        }
        self.assertEqual(core.runtime_invariants(), expected)
        self.assertEqual(randomizer.runtime_invariants(), expected)
        self.assertEqual(self.capsule["runtime_invariants"], expected)


if __name__ == "__main__":
    unittest.main()
