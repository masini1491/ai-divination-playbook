from __future__ import annotations
import importlib.util, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"references"/"ziwei"/"validate_uncertainty_safety_delivery_v0.py"
s=importlib.util.spec_from_file_location("ziwei_delivery_v0",P); assert s and s.loader
m=importlib.util.module_from_spec(s); sys.modules[s.name]=m; s.loader.exec_module(m)

class ZiWeiDeliveryContractTests(unittest.TestCase):
    def test_plain_source_backed_can_allow(self):
        self.assertEqual(["ALLOW"],m.delivery_actions(evidence_states=["source_backed"]))
    def test_conflict_is_presented_separately(self):
        self.assertIn("PRESENT_CONFLICT_SEPARATELY",m.delivery_actions(evidence_states=["source_backed","conflicted"]))
    def test_insufficient_is_omitted(self):
        self.assertIn("OMIT_INSUFFICIENT",m.delivery_actions(evidence_states=["insufficient"]))
    def test_profile_specific_is_disclosed(self):
        self.assertIn("ALLOW_WITH_PROFILE_DISCLOSURE",m.delivery_actions(evidence_states=["profile_specific"]))
    def test_high_impact_is_bounded(self):
        self.assertIn("BOUND_HIGH_IMPACT",m.delivery_actions(evidence_states=["source_backed"],high_impact=["death"]))
    def test_unsupported_scope_blocks(self):
        self.assertEqual(["BLOCK_UNSUPPORTED_SCOPE"],m.delivery_actions(evidence_states=["source_backed"],unsupported_scope=True))
    def test_unknown_evidence_state_fails(self):
        with self.assertRaisesRegex(ValueError,"EVIDENCE_STATE_INVALID"):
            m.delivery_actions(evidence_states=["certain"])

if __name__=="__main__": unittest.main()
