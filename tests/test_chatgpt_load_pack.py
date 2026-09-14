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


class ChatGPTLoadPackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.builder = load_module(
            ROOT / "tools" / "build_chatgpt_load_pack.py",
            "build_chatgpt_load_pack",
        )

    def test_committed_pack_matches_canonical_sections(self):
        expected = self.builder.build_pack(ROOT)
        actual = json.loads((ROOT / "CHATGPT_LOAD_PACK.json").read_text(encoding="utf-8"))
        self.assertEqual(expected, actual)

    def test_pack_is_non_authoritative_and_profiles_keep_owner_followup(self):
        pack = self.builder.build_pack(ROOT)
        self.assertEqual(pack["authority"], "derived-retrieval-cache-only")
        self.assertEqual(pack["fragments"]["ordinary_routing"]["owner"], "METHOD_ROUTING.md")
        self.assertIn("TAROT.md", pack["profiles"]["explicit_tarot"]["required_followup"])
        self.assertIn(
            "selected method owner",
            pack["profiles"]["ordinary_unspecified"]["required_followup"],
        )

    def test_pack_contains_verbatim_sections_not_generated_policy(self):
        pack = self.builder.build_pack(ROOT)
        for fragment in pack["fragments"].values():
            owner_text = (ROOT / fragment["owner"]).read_text(encoding="utf-8")
            for heading in fragment["sections"]:
                excerpt = self.builder.extract_section(owner_text, heading)
                self.assertIn(excerpt.rstrip(), fragment["content"])


if __name__ == "__main__":
    unittest.main()
