from __future__ import annotations
import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
class Tests(unittest.TestCase):
 def test_index_route(self):
  idx=json.loads((ROOT/"PLAYBOOK_INDEX.json").read_text(encoding="utf-8")); z=next(x for x in idx["capabilities"] if x["id"]=="method.ziwei"); c=z["star_palace_coverage"]
  self.assertEqual((168,52,34,116,8),(c["total_cells"],c["reviewed_cells"],c["resolved_cells"],c["unreviewed_cells"],c["dedicated_l4"]))
  self.assertEqual("indexes/ziwei/star_palace_coverage_v1.json",c["index"]); self.assertEqual("tools/build_ziwei_star_palace_coverage.py",c["generator"])
  self.assertEqual("routing-control-plane-only",c["authority"]); self.assertFalse(c["dedicated_cartesian_expansion"])
if __name__=="__main__": unittest.main()
