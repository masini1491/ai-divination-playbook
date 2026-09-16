import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
EXPECTED = [
    "TAROT-BEH-001",
    "TAROT-BEH-002",
    "TAROT-BEH-005",
    "TAROT-BEH-006",
    "TAROT-BEH-011",
    "TAROT-BEH-012",
    "TAROT-BEH-016",
    "TAROT-BEH-017",
    "TAROT-BEH-018",
]


class AgentSkillsRegressionSelectionTests(unittest.TestCase):
    def test_agent_skills_change_class_covers_required_boundaries(self):
        matrix = json.loads((ROOT / "evals/regression_matrix.json").read_text(encoding="utf-8"))
        self.assertEqual(matrix["change_classes"]["agent-skills-adapter"], EXPECTED)


if __name__ == "__main__":
    unittest.main()
