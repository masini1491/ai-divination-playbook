from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MOD=ROOT/"references"/"ziwei"/"validate_production_schema_candidates_v0.py"
spec=importlib.util.spec_from_file_location("ziwei_prod_schema_candidate",MOD)
assert spec and spec.loader
m=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=m
spec.loader.exec_module(m)

class ZiWeiProductionSchemaCandidateTests(unittest.TestCase):
    def packet(self,facts,scope="natal_baseline"):
        return {
            "packet_id":"p1","schema_version":"0.1.0-candidate","request_id":"r1",
            "interpretation_profile":"ziwei.interpretation.tw_v1",
            "calculation_profile":{"profile_id":"ziwei.baseline.tw_v1","production_admitted":False},
            "temporal_context":{"scope":scope},"facts":facts,"topology":{},
            "ambiguity":[],"validation":{},"provenance_map":{}
        }

    def test_known_fact_requires_value_and_provenance(self):
        f={"fact_id":"x","fact_type":"star_presence","state":"known","source_provenance":[]}
        e=m.validate_packet(self.packet([f]))
        self.assertIn("KNOWN_VALUE_REQUIRED",e)
        self.assertIn("KNOWN_PROVENANCE_REQUIRED",e)

    def test_unknown_fact_is_structurally_valid_without_value(self):
        f={"fact_id":"x","fact_type":"brightness","state":"not_computed","source_provenance":[]}
        self.assertEqual([],m.validate_packet(self.packet([f])))

    def test_known_brightness_requires_profile_identity(self):
        f={"fact_id":"x","fact_type":"brightness","state":"known","value":"廟","source_provenance":["engine:test"]}
        self.assertIn("BRIGHTNESS_PROFILE_REQUIRED",m.validate_packet(self.packet([f])))

    def test_known_sihua_requires_profile_identity(self):
        f={"fact_id":"x","fact_type":"four_transformation","state":"known","value":"化祿","source_provenance":["engine:test"]}
        self.assertIn("SIHUA_PROFILE_REQUIRED",m.validate_packet(self.packet([f])))

    def test_known_temporal_fact_requires_scope_target_boundary(self):
        f={"fact_id":"x","fact_type":"temporal","state":"known","value":"x","source_provenance":["engine:test"],"profile_scope":{"temporal_scope":"yearly"}}
        self.assertIn("TEMPORAL_IDENTITY_REQUIRED",m.validate_packet(self.packet([f],"yearly")))

    def test_duplicate_fact_ids_fail(self):
        f={"fact_id":"x","fact_type":"star_presence","state":"unknown","source_provenance":[]}
        self.assertIn("FACT_ID_DUPLICATE",m.validate_packet(self.packet([f,f])))

if __name__=="__main__":
    unittest.main()
