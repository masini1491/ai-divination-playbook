from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
OWNER = ROOT / "ASTROLOGY_NATAL_SYNTHESIS.md"
BACKLOG = ROOT / "ASTROLOGY_BACKLOG.md"


class AstrologyNatalSynthesisGapGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.owner = OWNER.read_text(encoding="utf-8")
        cls.backlog = BACKLOG.read_text(encoding="utf-8")

    def test_gate_accepts_only_concrete_passage_level_failure_classes(self):
        for token in (
            "too_generic",
            "repetitive",
            "tension_not_integrated",
            "unsupported_leakage",
        ):
            self.assertIn(token, self.owner)
        self.assertIn("no_repo_work", self.owner)
        self.assertIn("主觀回饋只能作 locator，不是 semantic evidence", self.owner)

    def test_output_gap_requires_synthetic_reproduction(self):
        self.assertIn("output_contract_gap", self.owner)
        self.assertIn("只有 synthetic regression 可重現時", self.owner)
        self.assertIn("bounded synthesis / output-guard fix", self.owner)

    def test_semantic_gap_cannot_bypass_sparse_exact_claim_policy(self):
        self.assertIn("semantic_resolution_gap", self.owner)
        self.assertIn("EXACT_CLAIM_ADMISSION_POLICY_V1.md", self.owner)
        self.assertIn("只有 research_candidate 才可建立 bounded exact-claim research", self.owner)

    def test_public_repo_persistence_excludes_private_reading_material(self):
        self.assertIn("真實私人 reading", self.owner)
        self.assertIn("不得寫入 public repo", self.owner)
        self.assertIn("synthetic regression", self.owner)

    def test_backlog_declares_one_shot_non_harness_scope(self):
        self.assertIn("AST-P1-250 — Post-Reading Natal Gap Escalation Gate", self.backlog)
        self.assertIn("status: IN_PROGRESS", self.backlog)
        self.assertIn("no accuracy score", self.backlog)
        self.assertIn("no repeated-run harness or theme-stability KPI", self.backlog)
        self.assertIn("no permanent evaluation queue", self.backlog)


if __name__ == "__main__":
    unittest.main()
