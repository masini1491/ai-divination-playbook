"""TEMPORARY AST-P1-005 query-bounded shard transport probe. MUST NOT MERGE."""
from __future__ import annotations
import hashlib, json, unittest
from astrology_place_shard_benchmark import EXPECTED_DATASETS, load_records, locate_data_dir, verify_dataset
from astrology_place_split_shard_benchmark import (
    alias_shard_bytes, build_split_shards, candidate_bucket_id,
    candidate_shard_bytes, sorted_routes,
)
ALIAS_HEX=3
CANDIDATE_HEX=3
MAX_QUERY_BYTES=100_000
CORPUS=(
 {"name":"樹林區","country_code":"TW"},
 {"name":"Tokyo","country_code":"JP"},
 {"name":"tokyo","country_code":"JP"},
 {"name":"  Tokyo  ","country_code":"JP"},
 {"name":"München","country_code":"DE"},
 {"name":"Munich","country_code":"DE"},
 {"name":"São Paulo","country_code":"BR"},
 {"name":"Sao Paulo","country_code":"BR"},
 {"name":"Springfield","country_code":None},
 {"name":"Springfield","country_code":"US"},
 {"name":"Paris","country_code":"FR"},
 {"name":"Paris","country_code":"US"},
 {"name":"DefinitelyNotARealPlaceNameForAstrologyProbe","country_code":None},
)
def digest_parts(parts):
 h=hashlib.sha256()
 for path,payload in sorted(parts):
  h.update(path.encode()); h.update(b"\0"); h.update(hashlib.sha256(payload).digest())
 return h.hexdigest()
def direct_routes(records,name,country_code):
 needle=name.strip().casefold(); wanted=country_code.upper() if country_code else None; rows={}
 for row in records.values():
  aliases={str(a).casefold() for a in row.get("alternatenames",[]) if str(a)}
  if needle not in aliases: continue
  if wanted and str(row.get("countrycode","")).upper()!=wanted: continue
  gid=int(row["geonameid"]); rows[gid]=[gid,str(row["countrycode"]),int(row.get("population",0)),str(row["name"])]
 return sorted(rows.values(),key=lambda r:(-int(r[2]),str(r[1]),str(r[3]),int(r[0])))
def serialize_profile(profile,aliases,candidates):
 parts=[]
 for bid,shard in aliases.items(): parts.append((f"profiles/{profile}/aliases/{bid[0]}/{bid[1:]}.json",alias_shard_bytes(profile,bid,shard)))
 for bid,shard in candidates.items(): parts.append((f"profiles/{profile}/candidates/{bid[0]}/{bid[1:]}.json",candidate_shard_bytes(profile,bid,shard)))
 return parts
class Probe(unittest.TestCase):
 def test_contract(self):
  data_dir,version=locate_data_dir(); self.assertEqual("3.0.2",version)
  result={"schema":"astrology-place-shard-transport-probe-v1","scope":"TEMPORARY_RESEARCH_ONLY","production_admission":"NOT_GRANTED",
   "thresholds_frozen_before_first_execution":{"source_identity_all_profiles":True,"deterministic_rebuild_digest_equal":True,"semantic_corpus_parity":1.0,"ambiguity_preview_candidate_records_max":10,"query_visible_bytes_max":MAX_QUERY_BYTES,"repeat_query_cache_fetch_bytes":0},"profiles":[]}
  overall=True
  for profile in sorted(EXPECTED_DATASETS):
   identity=verify_dataset(data_dir/f"cities{profile}.json",profile); self.assertTrue(identity["identity_match"])
   records=load_records(data_dir/f"cities{profile}.json")
   a1,c1=build_split_shards(records,alias_hex_chars=ALIAS_HEX,candidate_hex_chars=CANDIDATE_HEX)
   a2,c2=build_split_shards(records,alias_hex_chars=ALIAS_HEX,candidate_hex_chars=CANDIDATE_HEX)
   d1=digest_parts(serialize_profile(profile,a1,c1)); d2=digest_parts(serialize_profile(profile,a2,c2)); self.assertEqual(d1,d2)
   rows=[]; parity_count=0; max_bytes=0
   for f in CORPUS:
    expected=direct_routes(records,f["name"],f["country_code"])
    abid,actual=sorted_routes(a1,name=f["name"],country_code=f["country_code"],alias_hex_chars=ALIAS_HEX)
    parity=actual==expected; self.assertTrue(parity); parity_count+=int(parity)
    ap=alias_shard_bytes(profile,abid,a1[abid]) if abid in a1 else b""
    ids=[int(r[0]) for r in actual]; required=ids[:1] if len(ids)==1 else ids[:10]
    cbids=sorted({candidate_bucket_id(g,CANDIDATE_HEX) for g in required})
    cps=[candidate_shard_bytes(profile,b,c1[b]) for b in cbids]
    visible=len(ap)+sum(map(len,cps)); max_bytes=max(max_bytes,visible)
    self.assertLessEqual(len(required),10); self.assertLessEqual(visible,MAX_QUERY_BYTES)
    paths=(([f"profiles/{profile}/aliases/{abid[0]}/{abid[1:]}.json"] if ap else [])+[f"profiles/{profile}/candidates/{b[0]}/{b[1:]}.json" for b in cbids])
    payloads=(([ap] if ap else [])+cps); cache=set(); first=sum(len(p) for path,p in zip(paths,payloads) if path not in cache); cache.update(paths)
    repeat=sum(len(p) for path,p in zip(paths,payloads) if path not in cache); self.assertEqual(0,repeat)
    rows.append({**f,"match_count":len(actual),"preview_count":len(required),"visible_bytes":visible,"first_fetch_bytes":first,"repeat_fetch_bytes":repeat,"parity":parity})
   ratio=parity_count/len(CORPUS); self.assertEqual(1.0,ratio)
   result["profiles"].append({"profile":profile,"source_identity":identity,"aggregate_digest_first":d1,"aggregate_digest_second":d2,"deterministic_rebuild":d1==d2,"corpus_size":len(CORPUS),"semantic_parity_ratio":ratio,"max_query_visible_bytes":max_bytes,"corpus":rows})
   overall=overall and d1==d2 and ratio==1.0 and max_bytes<=MAX_QUERY_BYTES
  result["overall_probe_pass"]=overall
  print("ASTROLOGY_PLACE_TRANSPORT_JSON_BEGIN"); print(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)); print("ASTROLOGY_PLACE_TRANSPORT_JSON_END")
  self.assertTrue(overall)
if __name__=="__main__": unittest.main()
