import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_agent_skills", ROOT / "tools" / "validate_agent_skills.py"
)
validate_agent_skills = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(validate_agent_skills)


def write(root: Path, relative_path: str, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class AgentSkillsAdapterTests(unittest.TestCase):
    def make_repo(self) -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        root = Path(temp_dir.name)
        skill_text = (
            ROOT / ".agents" / "skills" / "ai-divination-playbook" / "SKILL.md"
        ).read_text(encoding="utf-8")
        write(root, ".agents/skills/ai-divination-playbook/SKILL.md", skill_text)
        write(root, "AGENTS.md", "# Governance\n")
        write(root, "CHAT_INIT.md", "# Bootstrap\n")
        write(root, "CHATGPT_LOAD_PACK.json", "{}\n")
        write(
            root,
            "PLAYBOOK_INDEX.json",
            json.dumps(
                {
                    "schema_version": 1,
                    "authority": "routing-only",
                    "bootstrap": {"path": "CHAT_INIT.md"},
                    "loader": {"cache_path": "CHATGPT_LOAD_PACK.json"},
                    "adapters": {},
                }
            ),
        )
        return root

    def test_repository_gateway_passes(self):
        self.assertEqual(validate_agent_skills.validate(ROOT), [])

    def test_minimal_gateway_fixture_passes(self):
        root = self.make_repo()
        self.assertEqual(validate_agent_skills.validate(root), [])

    def test_method_alias_directory_fails_gateway_first_mvp(self):
        root = self.make_repo()
        (root / ".agents/skills/tarot").mkdir(parents=True)
        errors = validate_agent_skills.validate(root)
        self.assertTrue(any("exactly one skill directory" in error for error in errors))

    def test_allowed_tools_is_rejected(self):
        root = self.make_repo()
        skill = root / ".agents/skills/ai-divination-playbook/SKILL.md"
        text = skill.read_text(encoding="utf-8").replace(
            "metadata:\n", "allowed-tools: Read Bash\nmetadata:\n", 1
        )
        skill.write_text(text, encoding="utf-8")
        errors = validate_agent_skills.validate(root)
        self.assertTrue(any("allowed-tools" in error for error in errors))

    def test_routing_policy_duplication_is_rejected(self):
        root = self.make_repo()
        skill = root / ".agents/skills/ai-divination-playbook/SKILL.md"
        skill.write_text(
            skill.read_text(encoding="utf-8") + "\nPsychology → Tarot\n",
            encoding="utf-8",
        )
        errors = validate_agent_skills.validate(root)
        self.assertTrue(any("method-routing" in error for error in errors))

    def test_pointer_conflict_with_index_fails(self):
        root = self.make_repo()
        skill = root / ".agents/skills/ai-divination-playbook/SKILL.md"
        text = skill.read_text(encoding="utf-8").replace(
            "playbook-chat-init: CHAT_INIT.md",
            "playbook-chat-init: OTHER_INIT.md",
            1,
        )
        write(root, "OTHER_INIT.md", "# Other\n")
        skill.write_text(text, encoding="utf-8")
        errors = validate_agent_skills.validate(root)
        self.assertTrue(any("conflicts with PLAYBOOK_INDEX bootstrap.path" in error for error in errors))

    def test_extra_gateway_resources_are_rejected(self):
        root = self.make_repo()
        write(root, ".agents/skills/ai-divination-playbook/scripts/helper.py", "print('x')\n")
        errors = validate_agent_skills.validate(root)
        self.assertTrue(any("must remain thin" in error for error in errors))

    def test_authority_boundary_is_required(self):
        root = self.make_repo()
        skill = root / ".agents/skills/ai-divination-playbook/SKILL.md"
        text = skill.read_text(encoding="utf-8").replace(
            "current canonical governance wins",
            "repository governance applies",
            1,
        )
        skill.write_text(text, encoding="utf-8")
        errors = validate_agent_skills.validate(root)
        self.assertTrue(any("authority boundary missing" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
