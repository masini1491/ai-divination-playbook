from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / 'references' / 'ziwei' / 'validate_interpretation_claim_registry.py'
REGISTRY = ROOT / 'references' / 'ziwei' / 'ziwei_interpretation_claim_registry_batch2.json'

class ZiWeiClaimRegistryBatch2ValidationTests(unittest.TestCase):
    def test_batch2_registry_passes_existing_validator(self):
        completed=subprocess.run([sys.executable,str(VALIDATOR),str(REGISTRY)],cwd=VALIDATOR.parent,check=False,capture_output=True,text=True)
        self.assertEqual(0,completed.returncode,completed.stderr or completed.stdout)
        self.assertIn('PASS',completed.stdout)

    def test_batch2_shape_and_guards(self):
        data=json.loads(REGISTRY.read_text(encoding='utf-8'))
        self.assertEqual('0.1.1-research',data['schema_version'])
        self.assertEqual(16,len(data['claims']))
        self.assertEqual({'天府','太陰','貪狼','巨門','天相','天梁','七殺','破軍'},set(data['subjects']))
        self.assertFalse(data['production_routable'])
        self.assertFalse(data['privacy']['contains_real_birth_data'])
        self.assertFalse(data['research_result']['production_authority_granted'])
        self.assertFalse(data['research_result']['scientific_predictive_validity_claimed'])
        nihai=next(x for x in data['sources'] if x['source_id']=='SRC-NIHAI-TIANJI')
        self.assertEqual(['REFERENCE_ONLY'],nihai['admission_status'])

    def test_batch2_conflicts_are_preserved(self):
        data=json.loads(REGISTRY.read_text(encoding='utf-8'))
        groups={x['conflict_group_id']:x for x in data['conflict_groups']}
        self.assertEqual('PRESERVE_CONFLICT',groups['CG-TIANFU-RELIEF-001']['resolution_status'])
        self.assertEqual('PRESERVE_CONFLICT',groups['CG-TIANXIANG-AUTHORITY-001']['resolution_status'])
        tianfu=next(x for x in data['claims'] if x['claim_id']=='ZW-B2-TIANFU-COND-002')
        tianxiang=next(x for x in data['claims'] if x['claim_id']=='ZW-B2-TIANXIANG-COND-002')
        self.assertEqual(['CG-TIANFU-RELIEF-001'],tianfu['conflict_group_ids'])
        self.assertEqual(['CG-TIANXIANG-AUTHORITY-001'],tianxiang['conflict_group_ids'])

if __name__=='__main__': unittest.main()