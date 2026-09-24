from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class ZiWeiExecutionBoundaryTests(unittest.TestCase):
    def test_production_runtime_does_not_dynamic_load_reference_python(self):
        runtime=(ROOT/"tools"/"ziwei_runtime.py").read_text(encoding="utf-8")
        adapter=(ROOT/"tools"/"ziwei_scope_a_pipeline.py").read_text(encoding="utf-8")
        self.assertNotIn("importlib.util",runtime)
        self.assertNotIn("interpretation_retrieval_v0.py",runtime)
        self.assertNotIn("validate_uncertainty_safety_delivery_v0.py",runtime)
        self.assertIn("ziwei_claim_retrieval",runtime)
        self.assertIn("ziwei_delivery",runtime)
        self.assertIn("from tools.ziwei_runtime import",adapter)
        self.assertNotIn("ziwei_claim_retrieval",adapter)
        self.assertNotIn("ziwei_delivery",adapter)

    def test_canonical_retriever_keeps_research_registries_as_data_dependencies(self):
        text=(ROOT/"tools"/"ziwei_claim_retrieval.py").read_text(encoding="utf-8")
        self.assertIn('REGISTRY_ROOT = ROOT / "references" / "ziwei"',text)
        self.assertNotIn('DEFAULT_REGISTRIES = (\n    ROOT / "ziwei_interpretation_claim_registry_batch1.json"',text)

    def test_bundle_has_no_reference_python_executables(self):
        text=(ROOT/"tools"/"build_ziwei_tool_bundle.py").read_text(encoding="utf-8")
        self.assertIn('"tools/ziwei_claim_retrieval.py"',text)
        self.assertIn('"tools/ziwei_delivery.py"',text)
        self.assertNotIn('"references/ziwei/interpretation_retrieval_v0.py"',text)
        self.assertNotIn('"references/ziwei/validate_uncertainty_safety_delivery_v0.py"',text)

    def test_admission_points_to_production_execution_owners(self):
        data=json.loads((ROOT/"ZIWEI_PRODUCTION_ADMISSION_V1.json").read_text(encoding="utf-8"))
        self.assertEqual("tools/ziwei_claim_retrieval.py",data["pipeline"]["claim_retrieval_runtime"])
        self.assertEqual("tools/ziwei_delivery.py",data["pipeline"]["delivery_runtime"])
        self.assertNotIn("research_retriever",data["pipeline"])

    def test_reference_modules_are_compatibility_shims(self):
        retrieval=(ROOT/"references"/"ziwei"/"interpretation_retrieval_v0.py").read_text(encoding="utf-8")
        delivery=(ROOT/"references"/"ziwei"/"validate_uncertainty_safety_delivery_v0.py").read_text(encoding="utf-8")
        self.assertIn("compatibility shim",retrieval)
        self.assertIn("from tools.ziwei_claim_retrieval import *",retrieval)
        self.assertIn("compatibility shim",delivery)
        self.assertIn("from tools.ziwei_delivery import *",delivery)

if __name__=="__main__":
    unittest.main()
