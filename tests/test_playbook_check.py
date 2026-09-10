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
        write(root, "tools/behavioral_eval.py", "print('ok')\n")
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

    def test_deprecated_repository_identity_fails(self):
        root = self.make_repo()
        deprecated = "tarot-" + "plum-randomizer"
        write(root, "STALE.md", f"legacy source: {deprecated}\n")
        errors = playbook_check.validate(root)
        self.assertTrue(any("deprecated canonical identifier" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
