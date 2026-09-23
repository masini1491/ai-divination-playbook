from __future__ import annotations

import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / 'references' / 'ziwei' / 'validate_interpretation_claim_registry.py'
PALACE = ROOT / 'references' / 'ziwei' / 'ziwei_interpretation_claim_registry_palaces_v0.json'
BATCH1 = ROOT / 'references' / 'ziwei' / 'ziwei_interpretation_claim_registry_batch1.json'
BATCH2 = ROOT / 'references' / 'ziwei' / 'ziwei_interpretation_claim_registry_batch2.json'

class ZiWeiPalaceClaimRegistryValidationTests(unittest.TestCase):
    def run_validator(self,path:Path):
        return subprocess.run([sys.executable,str(VALIDATOR),str(path)],cwd=VALIDATOR.parent,check=False,capture_output=True,text=True)

    def test_palace_registry_passes_v02(self):
        completed=self.run_validator(PALACE)
        self.assertEqual(0,completed.returncode,completed.stderr or completed.stdout)
        self.assertIn('PASS',completed.stdout)

    def test_existing_v01_registries_remain_valid(self):
        for path in (BATCH1,BATCH2):
            completed=self.run_validator(path)
            self.assertEqual(0,completed.returncode,completed.stderr or completed.stdout)

    def test_palace_shape_guards_and_scope_conflicts(self):
        data=json.loads(PALACE.read_text(encoding='utf-8'))
        self.assertEqual('0.2.0-research',data['schema_version'])
        self.assertEqual(24,len(data['claims']))
        self.assertEqual(12,len(data['subjects']))
        self.assertEqual('overlay_not_thirteenth_palace',data['body_palace_policy'])
        groups={x['conflict_group_id']:x for x in data['conflict_groups']}
        self.assertEqual('PRESERVE_SCOPE_DIFFERENCE',groups['CG-FUDE-SCOPE-001']['resolution_status'])
        self.assertEqual('PRESERVE_SCOPE_DIFFERENCE',groups['CG-NUPU-SCOPE-001']['resolution_status'])
        self.assertFalse(data['production_routable'])
        self.assertFalse(data['research_result']['production_authority_granted'])

    def test_v01_does_not_silently_accept_palace_claim_types(self):
        data=json.loads(PALACE.read_text(encoding='utf-8'))
        downgraded=copy.deepcopy(data)
        downgraded['schema_version']='0.1.0-research'
        tmp=ROOT / 'references' / 'ziwei' / '.tmp_palace_registry_v01_reject.json'
        try:
            tmp.write_text(json.dumps(downgraded,ensure_ascii=False),encoding='utf-8')
            completed=self.run_validator(tmp)
            self.assertNotEqual(0,completed.returncode)
            self.assertIn('CLAIM_TYPE_INVALID',completed.stdout)
        finally:
            tmp.unlink(missing_ok=True)

if __name__=='__main__': unittest.main()