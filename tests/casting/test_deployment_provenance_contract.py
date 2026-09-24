from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "validation.yml"
VERCEL_CONFIG = ROOT / "runtime" / "casting" / "vercel.json"


class CastingDeploymentProvenanceContractTests(unittest.TestCase):
    def test_production_smoke_validates_deployed_runtime_tree_not_monorepo_head_identity(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("fetch-depth: 0", workflow)
        self.assertIn('CURRENT_SHA: ${{ github.sha }}', workflow)
        self.assertIn('git("merge-base", "--is-ancestor"', workflow)
        self.assertIn('git("rev-parse", f"{current}:runtime/casting")', workflow)
        self.assertIn('git("rev-parse", f"{deployed}:runtime/casting")', workflow)
        self.assertIn("runtime/casting tree mismatch", workflow)
        self.assertNotIn("EXPECTED_SHA:", workflow)
        self.assertNotIn('payload.get("runtime_source_commit") != expected', workflow)

    def test_vercel_skips_deployments_when_casting_root_is_unchanged(self):
        config = json.loads(VERCEL_CONFIG.read_text(encoding="utf-8"))

        self.assertEqual("https://openapi.vercel.sh/vercel.json", config["$schema"])
        self.assertEqual("git diff --quiet HEAD^ HEAD ./", config["ignoreCommand"])


if __name__ == "__main__":
    unittest.main()
