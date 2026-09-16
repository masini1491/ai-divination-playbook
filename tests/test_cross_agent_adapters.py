import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_cross_agent_adapters", ROOT / "tools" / "validate_cross_agent_adapters.py"
)
validator = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(validator)


class CrossAgentAdapterTests(unittest.TestCase):
    def test_repository_root_passes(self):
        self.assertEqual(validator.validate(ROOT), [])

    def test_missing_adapter_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            errors = validator.validate(root)
            self.assertTrue(any("missing cross-agent adapter" in error for error in errors))

    def test_normative_routing_duplication_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for relative, host in validator.ADAPTERS.items():
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                text = (ROOT / relative).read_text(encoding="utf-8").replace(host, host)
                if relative == "CLAUDE.md":
                    text += "\nPsychology → Tarot\n"
                path.write_text(text, encoding="utf-8")
            errors = validator.validate(root)
            self.assertTrue(any("duplicated normative policy token" in error for error in errors))

    def test_host_execution_admission_boundary_is_required(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for relative in validator.ADAPTERS:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                text = (ROOT / relative).read_text(encoding="utf-8")
                if relative == "CLAUDE.md":
                    text = text.replace(
                        "does not by itself grant this host canonical Playbook execution authority",
                        "is compatible with the repository",
                    )
                path.write_text(text, encoding="utf-8")
            errors = validator.validate(root)
            self.assertTrue(any("authority boundary missing phrase" in error for error in errors))

    def test_adapter_drift_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for relative in validator.ADAPTERS:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text((ROOT / relative).read_text(encoding="utf-8"), encoding="utf-8")
            with (root / "GEMINI.md").open("a", encoding="utf-8") as handle:
                handle.write("\nextra compatibility prose\n")
            errors = validator.validate(root)
            self.assertTrue(any("adapters drift" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
