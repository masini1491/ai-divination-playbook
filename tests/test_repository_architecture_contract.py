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

    def test_supporting_surface_semantics_delegate_to_shared_baseline(self) -> None:
        text = (ROOT / "REPOSITORY_ARCHITECTURE.md").read_text(encoding="utf-8")
        self.assertIn("generic semantics 不由本檔重定義", text)
        self.assertIn("upstream `AI_CONTEXT.md`", text)
        self.assertIn("upstream `REPOSITORY_EXECUTION.md`", text)
        self.assertNotIn("## 3. Information surface admission / retrieval-intent gate", text)
        self.assertNotIn("index = control plane", text)

    def test_method_scoped_backlog_topology_is_explicit(self) -> None:
        text = (ROOT / "REPOSITORY_ARCHITECTURE.md").read_text(encoding="utf-8")
        for name in (
            "ASTROLOGY_BACKLOG.md",
            "ZIWEI_BACKLOG.md",
            "PALMISTRY_BACKLOG.md",
        ):
            self.assertIn(name, text)
        self.assertIn("不建立 root `BACKLOG.md` aggregate", text)

    def test_coordination_write_mapping_is_owned_by_repository_architecture(self) -> None:
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        architecture = (ROOT / "REPOSITORY_ARCHITECTURE.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("ChatGPT Coordination Write Mapping", agents)
        self.assertIn("REPOSITORY_ARCHITECTURE.md", agents)
        for path in (
            "/ASTROLOGY_BACKLOG.md",
            "/ZIWEI_BACKLOG.md",
            "/PALMISTRY_BACKLOG.md",
        ):
            self.assertIn(path, architecture)
        self.assertIn("coordination-only persistence", architecture)
        self.assertNotIn("/ASTROLOGY_BACKLOG.md", agents)

    def test_adoption_record_tracks_current_shared_review_and_local_backlogs(self) -> None:
        text = (ROOT / "references" / "ai-development-playbook.md").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "Last reviewed source revision：`1aea805c0674960945d5588842a18bc37f0c96d9`",
            text,
        )
        self.assertIn("Method-scoped coordination topology", text)
        self.assertIn("connector-backed artifact/file handoff", text)
        self.assertIn("producer-vs-consumer closure", text)
        self.assertNotIn(
            "TASKS / BACKLOG / coordination surfaces（除非本 Repo未來另行 opt-in）",
            text,
        )

    def test_astrology_place_backlog_uses_same_repo_data_contract(self) -> None:
        text = (ROOT / "ASTROLOGY_BACKLOG.md").read_text(encoding="utf-8")
        self.assertIn("data/astrology/place/v1/**", text)
        self.assertIn("same-commit GitHub Connect bounded shard retrieval", text)
        self.assertNotIn("freeze external repository / manifest", text)


if __name__ == "__main__":
    unittest.main()
