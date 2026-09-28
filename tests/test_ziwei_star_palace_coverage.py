from __future__ import annotations
import json,subprocess,sys
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/"indexes/ziwei/star_palace_coverage_v1.json"
REGISTRY=ROOT/"references/ziwei/ziwei_interpretation_claim_registry_star_palace_context_v1.json"
class Tests(unittest.TestCase):
 def setUp(self):
  self.index=json.loads(INDEX.read_text(encoding="utf-8")); self.registry=json.loads(REGISTRY.read_text(encoding="utf-8")); self.cells={x["cell_key"]:x for x in self.index["cells"]}
 def test_grid(self):
  self.assertEqual(168,self.index["total_cells"]); self.assertEqual(168,len(self.index["cells"])); self.assertEqual(168,len(self.cells))
  self.assertEqual(14,len({x["star"] for x in self.index["cells"]})); self.assertEqual(12,len({x["palace"] for x in self.index["cells"]}))
 def test_metrics(self):
  m=self.index["metrics"]; self.assertEqual((36,22,132,7,15,14),(m["reviewed_cells"],m["resolved_cells"],m["unreviewed_cells"],m["dedicated_l4"],m["bounded_l5_composition"],m["deferred_evidence"]))
  self.assertEqual(168,m["reviewed_cells"]+m["unreviewed_cells"]); self.assertLessEqual(m["resolved_cells"],m["reviewed_cells"])
 def test_dedicated_map(self):
  exp={f'{c["star"]}×{c["palace"]}':c["claim_id"] for c in self.registry["claims"]}
  act={k:v["claim_ref"] for k,v in self.cells.items() if v["routing_mode"]=="DEDICATED_L4"}
  self.assertEqual(exp,act)
 def test_backfill(self):
  for k in ("太陽×財帛宮","太陽×官祿宮","紫微×官祿宮","紫微×遷移宮","天機×財帛宮","巨門×奴僕宮","破軍×福德宮","太陽×父母宮","太陰×父母宮","天梁×父母宮","天同×福德宮","太陰×福德宮","巨門×福德宮","天梁×福德宮","七殺×福德宮"): self.assertEqual("BOUNDED_L5_COMPOSITION",self.cells[k]["routing_mode"])
  for k in ("武曲×財帛宮","巨門×夫妻宮","天相×官祿宮","貪狼×遷移宮","天機×福德宮","紫微×奴僕宮","天同×財帛宮","紫微×福德宮","太陽×福德宮","武曲×福德宮","廉貞×福德宮","天府×福德宮","貪狼×福德宮","天相×福德宮"): self.assertEqual("DEFERRED_EVIDENCE",self.cells[k]["routing_mode"])
 def test_unreviewed(self):
  c=self.cells["紫微×兄弟宮"]; self.assertEqual("UNREVIEWED",c["routing_mode"]); self.assertFalse(c["resolved"]); self.assertNotIn("claim_ref",c)
 def test_compact(self): self.assertLess(INDEX.stat().st_size,45000)
 def test_current(self): subprocess.run([sys.executable,str(ROOT/"tools/build_ziwei_star_palace_coverage.py"),"--check"],check=True,cwd=ROOT)
if __name__=="__main__": unittest.main()
