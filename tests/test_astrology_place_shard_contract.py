from __future__ import annotations
import importlib.util, json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
GEN=ROOT/"tools"/"generate_astrology_place_shards.py"
MAN=ROOT/"data"/"astrology"/"place"/"v1"/"MANIFEST.json"
def load_gen():
 spec=importlib.util.spec_from_file_location("placegen",GEN); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
class PlaceShardContractTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.g=load_gen(); cls.m=json.loads(MAN.read_text())
 def test_manifest_freezes_nonproduction_contract(self):
  self.assertEqual("FORMAT_CONTRACT_FROZEN_DATA_NOT_YET_COMMITTED",self.m["status"]); self.assertEqual("NOT_GRANTED",self.m["production_admission"])
  self.assertEqual(3,self.m["format"]["alias_hex_chars"]); self.assertEqual(3,self.m["format"]["candidate_hex_chars"])
 def test_source_hashes_match_generator_authority(self):
  self.assertEqual(set(map(str,self.g.EXPECTED_DATASETS)),set(self.m["source_datasets"]))
  for profile,expected in self.g.EXPECTED_DATASETS.items():
   self.assertEqual(expected,self.m["source_datasets"][str(profile)])
 def test_path_is_query_derivable(self):
  bid=self.g.alias_bucket_id("tokyo"); path=self.g.shard_path(Path("data/astrology/place/v1"),500,"aliases",bid)
  self.assertEqual(Path("data/astrology/place/v1")/"profiles"/"500"/"aliases"/bid[0]/f"{bid[1:]}.json",path)
 def test_stable_serialization(self):
  row={"1":[1,"X","TW","01",1.0,2.0,"Asia/Taipei",3]}
  self.assertEqual(self.g.render("candidates",500,"abc",row),self.g.render("candidates",500,"abc",row))
if __name__=="__main__": unittest.main()
