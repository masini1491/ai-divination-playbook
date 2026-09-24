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

    def test_indexes_are_routing_only_control_plane(self) -> None:
        text = (ROOT / "REPOSITORY_ARCHITECTURE.md").read_text(encoding="utf-8")
        self.assertIn("indexes/      routing / lookup metadata only", text)
        self.assertIn("index 不複製被路由內容本體", text)
        self.assertIn("index = control plane", text)

    def test_optional_surfaces_are_not_mandatory_taxonomy(self) -> None:
        text = (ROOT / "REPOSITORY_ARCHITECTURE.md").read_text(encoding="utf-8")
        self.assertIn("optional supporting surfaces", text)
        self.assertIn("不為目錄對稱或形式完整而新增 surface", text)
        self.assertIn("evidence ≠ policy / architecture / method authority", text)
        self.assertIn("fixture PASS 不等於全域 production validity", text)

    def test_retrieval_intent_and_control_data_plane_are_explicit(self) -> None:
        text = (ROOT / "REPOSITORY_ARCHITECTURE.md").read_text(encoding="utf-8")
        self.assertIn("Information surface admission / retrieval-intent gate", text)
        self.assertIn("control plane", text)
        self.assertIn("data plane", text)
        self.assertIn("Control plane 不複製 data plane 本體", text)


if __name__ == "__main__":
    unittest.main()
