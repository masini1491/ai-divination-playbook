from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / 'references' / 'ziwei' / 'validate_interpretation_claim_registry.py'
REGISTRY = ROOT / 'references' / 'ziwei' / 'ziwei_interpretation_claim_registry_batch1.json'

class ZiWeiClaimRegistryValidationTests(unittest.TestCase):
    def test_batch1_registry_passes_validator(self):
        completed=subprocess.run([sys.executable,str(VALIDATOR),str(REGISTRY)],cwd=VALIDATOR.parent,check=False,capture_output=True,text=True)
        self.assertEqual(0,completed.returncode,completed.stderr or completed.stdout)
        self.assertIn('PASS',completed.stdout)

    def test_batch1_shape_and_guards(self):
        data=json.loads(REGISTRY.read_text(encoding='utf-8'))
        self.assertEqual('0.1.1-research',data['schema_version'])
        self.assertEqual(12,len(data['claims']))
        self.assertEqual({'紫微','天機','太陽','武曲','天同','廉貞'},set(data['subjects']))
        self.assertFalse(data['production_routable'])
        self.assertFalse(data['privacy']['contains_real_birth_data'])
        self.assertFalse(data['research_result']['production_authority_granted'])
        self.assertFalse(data['research_result']['scientific_predictive_validity_claimed'])
        nihai=next(x for x in data['sources'] if x['source_id']=='SRC-NIHAI-TIANJI')
        self.assertEqual(['REFERENCE_ONLY'],nihai['admission_status'])

    def test_tianji_conflict_is_preserved(self):
        data=json.loads(REGISTRY.read_text(encoding='utf-8'))
        group=next(x for x in data['conflict_groups'] if x['conflict_group_id']=='CG-TIANJI-RELIEF-001')
        self.assertEqual('PRESERVE_CONFLICT',group['resolution_status'])
        self.assertIn('ZW-B1-TIANJI-COND-002',group['claim_refs'])
        claim=next(x for x in data['claims'] if x['claim_id']=='ZW-B1-TIANJI-COND-002')
        self.assertEqual(['CG-TIANJI-RELIEF-001'],claim['conflict_group_ids'])

if __name__=='__main__': unittest.main()