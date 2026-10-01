import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("playbook_check", ROOT / "tools" / "playbook_check.py")
playbook_check = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(playbook_check)


def write(root: Path, relative_path: str, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class PlaybookCheckTests(unittest.TestCase):
    def make_repo(self) -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        root = Path(temp_dir.name)

        write(root, "CHAT_INIT.md", "# Init\n\n## 最低必要路由\n- x → `OWNER.md`\n")
        write(root, "OWNER.md", "# Owner\n\n## Section A\n")
        write(root, "BEHAVIORAL_EVAL.md", "# Eval\n\n### TAROT-BEH-001 — One\n")
        write(root, "SESSION_HANDOFF.md", "# Handoff\n")
        write(root, "SCHEMA.json", "{}\n")
        write(root, "tools/behavioral_eval.py", "print('ok')\n")
        write(root, "runtime/casting/randomizer.py", "print('runtime')\n")
        write(
            root,
            "evals/regression_matrix.json",
            json.dumps(
                {
                    "schema_version": 1,
                    "authority": "selection-only",
                    "full_baseline": ["TAROT-BEH-001"],
                    "change_classes": {"bootstrap": ["TAROT-BEH-001"]},
                }
            ),
        )
        write(
            root,
            "PLAYBOOK_INDEX.json",
            json.dumps(
                {
                    "schema_version": 1,
                    "authority": "routing-only",
                    "bootstrap": {"path": "CHAT_INIT.md"},
                    "capabilities": [
                        {
                            "id": "owner.a",
                            "owner": "OWNER.md",
                            "section": "Section A",
                            "kind": "contract",
                            "schema": "SCHEMA.json",
                        },
                        {
                            "id": "validation.behavioral",
                            "owner": "BEHAVIORAL_EVAL.md",
                            "kind": "contract",
                            "matrix": "evals/regression_matrix.json",
                            "runner": "tools/behavioral_eval.py",
                        },
                    ],
                    "adapters": {"handoff": "SESSION_HANDOFF.md"},
                    "behavioral_regression": {
                        "matrix": "evals/regression_matrix.json",
                        "runner": "tools/behavioral_eval.py",
                    },
                }
            ),
        )
        return root

    def test_repository_root_passes(self):
        self.assertEqual(playbook_check.validate(ROOT), [])

    def test_valid_repo_passes(self):
        root = self.make_repo()
        self.assertEqual(playbook_check.validate(root), [])

    def test_missing_manifest_section_fails(self):
        root = self.make_repo()
        data = json.loads((root / "PLAYBOOK_INDEX.json").read_text(encoding="utf-8"))
        data["capabilities"][0]["section"] = "Missing"
        (root / "PLAYBOOK_INDEX.json").write_text(json.dumps(data), encoding="utf-8")
        errors = playbook_check.validate(root)
        self.assertTrue(any("section missing" in error for error in errors))

    def test_missing_index_local_file_pointer_fails(self):
        root = self.make_repo()
        data = json.loads((root / "PLAYBOOK_INDEX.json").read_text(encoding="utf-8"))
        data["capabilities"][0]["schema"] = "MISSING_SCHEMA.json"
        (root / "PLAYBOOK_INDEX.json").write_text(json.dumps(data), encoding="utf-8")
        errors = playbook_check.validate(root)
        self.assertTrue(any("MISSING_SCHEMA.json" in error for error in errors))

    def test_cutover_runtime_implementation_local_pointer_passes(self):
        root = self.make_repo()
        data = json.loads((root / "PLAYBOOK_INDEX.json").read_text(encoding="utf-8"))
        data["capabilities"][0]["id"] = "runtime.draw"
        data["capabilities"][0]["implementation"] = "runtime/casting/randomizer.py"
        (root / "PLAYBOOK_INDEX.json").write_text(json.dumps(data), encoding="utf-8")
        self.assertEqual(playbook_check.validate(root), [])

    def test_cutover_runtime_implementation_missing_local_pointer_fails(self):
        root = self.make_repo()
        data = json.loads((root / "PLAYBOOK_INDEX.json").read_text(encoding="utf-8"))
        data["capabilities"][0]["id"] = "runtime.draw"
        data["capabilities"][0]["implementation"] = "runtime/casting/MISSING.py"
        (root / "PLAYBOOK_INDEX.json").write_text(json.dumps(data), encoding="utf-8")
        errors = playbook_check.validate(root)
        self.assertTrue(any("runtime/casting/MISSING.py" in error for error in errors))

    def test_cutover_liuyao_casting_implementation_missing_local_pointer_fails(self):
        root = self.make_repo()
        data = json.loads((root / "PLAYBOOK_INDEX.json").read_text(encoding="utf-8"))
        data["capabilities"][0]["id"] = "method.liuyao"
        data["capabilities"][0]["casting_implementation"] = "runtime/casting/MISSING.py"
        (root / "PLAYBOOK_INDEX.json").write_text(json.dumps(data), encoding="utf-8")
        errors = playbook_check.validate(root)
        self.assertTrue(any("runtime/casting/MISSING.py" in error for error in errors))

    def test_external_implementation_locator_is_not_treated_as_local_file(self):
        root = self.make_repo()
        data = json.loads((root / "PLAYBOOK_INDEX.json").read_text(encoding="utf-8"))
        data["capabilities"][0]["implementation"] = "owner/external-repo/tool.py"
        data["capabilities"][0]["casting_implementation"] = "owner/external-repo/casting.py"
        (root / "PLAYBOOK_INDEX.json").write_text(json.dumps(data), encoding="utf-8")
        self.assertEqual(playbook_check.validate(root), [])

    def test_non_path_metadata_is_not_treated_as_local_file(self):
        root = self.make_repo()
        data = json.loads((root / "PLAYBOOK_INDEX.json").read_text(encoding="utf-8"))
        data["capabilities"][0]["activation"] = "explicit-request-only"
        (root / "PLAYBOOK_INDEX.json").write_text(json.dumps(data), encoding="utf-8")
        self.assertEqual(playbook_check.validate(root), [])

    def test_valid_continuity_coordination_passes(self):
        root = self.make_repo()
        data = json.loads((root / "PLAYBOOK_INDEX.json").read_text(encoding="utf-8"))
        data["coordination"] = {
            "continuity": {
                "authority": "routing-only",
                "owner": "OWNER.md",
                "adapter": "SESSION_HANDOFF.md",
                "repository": "owner/repo",
                "threads": {
                    "astrology": {
                        "semantic_id": "continuity.astrology",
                        "issue_number": 11,
                        "title": "[continuity] Astrology",
                    },
                    "ziwei": {
                        "semantic_id": "continuity.ziwei",
                        "issue_number": 12,
                        "title": "[continuity] Zi Wei",
                    },
                    "palmistry": {
                        "semantic_id": "continuity.palmistry",
                        "issue_number": 13,
                        "title": "[continuity] Palmistry",
                    },
                },
            }
        }
        (root / "PLAYBOOK_INDEX.json").write_text(json.dumps(data), encoding="utf-8")
        self.assertEqual(playbook_check.validate(root), [])

    def test_continuity_coordination_invalid_issue_number_fails(self):
        root = self.make_repo()
        data = json.loads((root / "PLAYBOOK_INDEX.json").read_text(encoding="utf-8"))
        data["coordination"] = {
            "continuity": {
                "authority": "routing-only",
                "owner": "OWNER.md",
                "adapter": "SESSION_HANDOFF.md",
                "repository": "owner/repo",
                "threads": {
                    "astrology": {
                        "semantic_id": "continuity.astrology",
                        "issue_number": 0,
                        "title": "[continuity] Astrology",
                    },
                    "ziwei": {
                        "semantic_id": "continuity.ziwei",
                        "issue_number": 12,
                        "title": "[continuity] Zi Wei",
                    },
                    "palmistry": {
                        "semantic_id": "continuity.palmistry",
                        "issue_number": 13,
                        "title": "[continuity] Palmistry",
                    },
                },
            }
        }
        (root / "PLAYBOOK_INDEX.json").write_text(json.dumps(data), encoding="utf-8")
        errors = playbook_check.validate(root)
        self.assertTrue(any("issue_number must be a positive integer" in error for error in errors))

    def test_behavioral_matrix_drift_fails(self):
        root = self.make_repo()
        data = json.loads((root / "evals/regression_matrix.json").read_text(encoding="utf-8"))
        data["full_baseline"] = []
        (root / "evals/regression_matrix.json").write_text(json.dumps(data), encoding="utf-8")
        errors = playbook_check.validate(root)
        self.assertTrue(any("full_baseline" in error for error in errors))

    def test_missing_chat_init_route_fails(self):
        root = self.make_repo()
        (root / "OWNER.md").unlink()
        errors = playbook_check.validate(root)
        self.assertTrue(any("routed owner missing" in error for error in errors))

    def test_semantic_work_pointer_valid_heading_passes(self):
        root = self.make_repo()
        write(root, "BACKLOG.md", "# Backlog\n\n### AST-P1-190 — Completed work\n")
        write(root, "POINTERS.md", "owner: `BACKLOG.md#AST-P1-190`\n")
        self.assertEqual(playbook_check.validate(root), [])

    def test_semantic_work_pointer_missing_heading_fails(self):
        root = self.make_repo()
        write(root, "BACKLOG.md", "# Backlog\n\n- **AST-P1-190 — Completed work** — DONE.\n")
        write(root, "POINTERS.md", "owner: `BACKLOG.md#AST-P1-190`\n")
        errors = playbook_check.validate(root)
        self.assertTrue(any("semantic work pointer target heading missing" in error for error in errors))

    def test_semantic_work_pointer_in_json_fails_closed(self):
        root = self.make_repo()
        write(root, "BACKLOG.md", "# Backlog\n\n- AST-SHARED-003 done\n")
        data = json.loads((root / "PLAYBOOK_INDEX.json").read_text(encoding="utf-8"))
        data["capabilities"][0]["coordination_owner"] = "BACKLOG.md#AST-SHARED-003"
        (root / "PLAYBOOK_INDEX.json").write_text(json.dumps(data), encoding="utf-8")
        errors = playbook_check.validate(root)
        self.assertTrue(any("AST-SHARED-003" in error and "heading missing" in error for error in errors))

    def test_deprecated_repository_identity_fails(self):
        root = self.make_repo()
        deprecated = "tarot-" + "plum-randomizer"
        write(root, "STALE.md", f"legacy source: {deprecated}\n")
        errors = playbook_check.validate(root)
        self.assertTrue(any("deprecated canonical identifier" in error for error in errors))

    def test_legacy_deployment_url_in_casting_openapi_fails(self):
        root = self.make_repo()
        url = "https://tarot-" + "plum-randomizer-masini1491-9205.vercel.app"
        write(root, "runtime/casting/openapi.json", json.dumps({"servers": [{"url": url}]}))
        errors = playbook_check.validate(root)
        self.assertTrue(any("deprecated canonical identifier" in error for error in errors))

    def test_legacy_deployment_url_outside_casting_openapi_fails(self):
        root = self.make_repo()
        url = "https://tarot-" + "plum-randomizer-masini1491-9205.vercel.app"
        write(root, "STALE.md", f"deployment: {url}\n")
        errors = playbook_check.validate(root)
        self.assertTrue(any("deprecated canonical identifier" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
