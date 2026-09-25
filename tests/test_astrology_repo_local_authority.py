from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
ASTRO=ROOT/"ASTROLOGY.md"

class AstrologyRepoLocalAuthorityTests(unittest.TestCase):
 def test_ordinary_production_is_repo_local_first(self):
  text=ASTRO.read_text(encoding="utf-8")
  self.assertIn("Ordinary Astrology production execution MUST use the current `ai-divination-playbook` repo-local admitted authority first.",text)
  self.assertIn("MUST NOT routinely load or consult other public Astrology repositories",text)
 def test_explicit_external_research_exceptions_remain(self):
  text=ASTRO.read_text(encoding="utf-8")
  for term in ("research, comparison, provenance/source verification, licensing review, or development/admission work","shared `ai-development-playbook` activation contract","does not promote `references/astrology/**` into production authority"):
   self.assertIn(term,text)

if __name__=="__main__": unittest.main()
