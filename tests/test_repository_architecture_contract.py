from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class RepositoryArchitectureContractTests(unittest.TestCase):
    def test_canonical_owner_exists(self) -> None:
        path = ROOT / "REPOSITORY_ARCHITECTURE.md"
        self.assertTrue(path.is_file())
        text = path.read_text(encoding="utf-8")
        self.assertIn("REPO-LEVEL CANONICAL CONTRACT", text)
        self.assertIn("`data/` 不等於 upstream authority source", text)
        self.assertIn("upstream authority / admitted source bytes", text)
        self.assertIn("runtime transport", text)

    def test_agents_routes_without_duplicating_full_taxonomy(self) -> None:
        text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("REPOSITORY_ARCHITECTURE.md", text)
        self.assertNotIn(
            "tools/        executable authority / provider / resolver / generator",
            text,
        )

    def test_machine_index_exposes_repository_architecture_owner(self) -> None:
        data = json.loads((ROOT / "PLAYBOOK_INDEX.json").read_text(encoding="utf-8"))
        rows = {row["id"]: row for row in data["capabilities"]}
        row = rows["repository.architecture"]
        self.assertEqual("REPOSITORY_ARCHITECTURE.md", row["owner"])
        self.assertEqual("contract", row["kind"])
        self.assertEqual("repo-level", row["scope"])

    def test_runtime_and_data_are_distinct_layers(self) -> None:
        text = (ROOT / "REPOSITORY_ARCHITECTURE.md").read_text(encoding="utf-8")
        self.assertIn("data/         repo-local deterministic datasets", text)
        self.assertIn(
            "runtime/      ChatGPT execution / materialization transport artifacts",
            text,
        )
        self.assertIn("三層不可互相偷換 authority", text)


if __name__ == "__main__":
    unittest.main()
