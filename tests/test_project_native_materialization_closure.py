from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ProjectNativeMaterializationClosureTests(unittest.TestCase):
    def test_repository_architecture_declares_project_native_execution_closure(self):
        text = (ROOT / "REPOSITORY_ARCHITECTURE.md").read_text(encoding="utf-8")
        self.assertIn("### Project-native execution closure invariant", text)
        self.assertIn(
            "Ordinary divination reading and production runtime execution must be able to close using canonical owners inside this repository.",
            text,
        )
        self.assertIn("not a required next hop", text)
        self.assertIn("final canonical identity established?", text)

    def test_astrology_materialization_closes_inside_repository(self):
        text = (ROOT / "ASTROLOGY_MATERIALIZATION.md").read_text(encoding="utf-8")
        for marker in (
            "Astrology production materialization在本 Repo內必須自足閉合",
            "resolve ai-divination-playbook current ref to one exact commit",
            "use this owner’s admitted exact-commit handoff artifact or deterministic core bundle fallback",
            "verify chunk/archive/per-file identity",
            "execute project-owned Astrology runtime/provider",
            "maintenance-only references, not production runtime dependencies",
        ):
            self.assertIn(marker, text)

    def test_ziwei_materialization_closes_inside_repository(self):
        text = (ROOT / "ZIWEI_MATERIALIZATION.md").read_text(encoding="utf-8")
        for marker in (
            "Zi Wei production materialization is self-contained in this repository",
            "resolve ai-divination-playbook current ref to one exact commit",
            "use this owner’s admitted exact-commit handoff artifact or deterministic tool-bundle fallback",
            "verify bundle chunk/archive/per-file identities",
            "execute tools/ziwei_runtime.py",
            "maintenance-only references, not production runtime dependencies",
        ):
            self.assertIn(marker, text)

    def test_ordinary_and_explicit_profiles_gain_no_new_compulsory_hop(self):
        pack = json.loads((ROOT / "CHATGPT_LOAD_PACK.json").read_text(encoding="utf-8"))
        self.assertEqual(
            pack["profiles"]["ordinary_unspecified"]["fragments"],
            ["bootstrap", "ordinary_routing", "runtime_fast_path", "output_core"],
        )
        self.assertEqual(
            pack["profiles"]["ordinary_unspecified"]["required_followup"],
            ["selected method owner"],
        )
        self.assertEqual(
            pack["profiles"]["explicit_astrology"]["fragments"],
            ["bootstrap", "output_core"],
        )
        self.assertEqual(
            pack["profiles"]["explicit_astrology"]["required_followup"],
            ["ASTROLOGY.md", "selected Astrology mode owner"],
        )
        self.assertEqual(
            pack["profiles"]["explicit_ziwei"]["fragments"],
            ["bootstrap", "output_core"],
        )
        self.assertEqual(
            pack["profiles"]["explicit_ziwei"]["required_followup"],
            ["ZIWEI.md"],
        )


if __name__ == "__main__":
    unittest.main()
