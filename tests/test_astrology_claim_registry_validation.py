from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "references" / "astrology" / "validate_interpretation_claim_registry.py"
TAXONOMY = ROOT / "references" / "astrology" / "tradition_taxonomy_example.json"
REGISTRY = ROOT / "references" / "astrology" / "planet_sign_composable_semantics_claim_family_registry.json"


class AstrologyClaimRegistryValidationTests(unittest.TestCase):
    def test_planet_sign_registry_passes_canonical_validator_in_ci(self):
        completed = subprocess.run(
            [
                sys.executable,
                str(VALIDATOR),
                "--taxonomy",
                str(TAXONOMY),
                str(REGISTRY),
            ],
            cwd=VALIDATOR.parent,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, completed.returncode, completed.stderr or completed.stdout)
        self.assertIn("PASS", completed.stdout)


if __name__ == "__main__":
    unittest.main()
