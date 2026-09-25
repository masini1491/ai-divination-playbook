from __future__ import annotations
import importlib.util, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
GEN=ROOT/"tools"/"build_ziwei_tool_bundle.py"
BUNDLE=ROOT/"runtime"/"ziwei"/"CHATGPT_DETERMINISTIC_TOOL_BUNDLE.json"
DATA=ROOT/"data"/"calendar"/"ziwei_tw_interval"/"v1"

def load_gen():
    spec=importlib.util.spec_from_file_location("build_ziwei_tool_bundle",GEN)
    if spec is None or spec.loader is None: raise RuntimeError("cannot load generator")
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

class ZiWeiToolBundleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g=load_gen(); cls.b=json.loads(BUNDLE.read_text(encoding="utf-8"))

    def test_bundle_matches_generator_and_verifies(self):
        expected=self.g.build_bundle()
        self.assertEqual(self.g.render(expected),self.g.render(self.b))
        self.assertEqual([],self.g.verify_bundle(self.b))

    def test_transport_has_no_interpretation_authority(self):
        self.assertEqual("derived-transport-cache-only",self.b["authority"])
        self.assertEqual(2,self.b["schema_version"])
        self.assertFalse(self.b["execution_contract"]["interpretation_authority"])
        self.assertFalse(self.b["execution_contract"]["new_claim_authority"])

    def test_calendar_data_is_query_bounded_and_build_source_is_not_runtime_dependency(self):
        c=self.b["calendar_data"]
        self.assertEqual("ziwei_tw_interval_1900_2100_candidate_v1",c["dataset_id"])
        self.assertEqual("4913a39e770afcd21eedc387523c572b8c4fc6469889c28f6ea75613f8984d79",c["aggregate_sha256"])
        self.assertEqual(1,c["ordinary_query_max_files"])
        self.assertEqual(2,c["rat_hour_cross_year_max_files"])
        self.assertEqual("same-commit-query-bounded-github-connect",c["acquisition"])
        self.assertFalse(self.b["build_source"]["runtime_dependency"])
        origins={x["origin"] for x in self.b["source_files"]}
        self.assertEqual({"playbook"},origins)
        paths={x["path"] for x in self.b["source_files"]}
        self.assertIn("data/calendar/ziwei_tw_interval/v1/MANIFEST.json",paths)
        self.assertIn("tools/ziwei_calendar_data_provider.py",paths)
        self.assertFalse(any(x["path"].startswith("lunar_python/") for x in self.b["source_files"]))
        self.assertFalse(self.b["execution_contract"]["dependency_install_required_after_materialization"])

    def test_chunk_contract_is_bounded(self):
        a=self.b["archive"]
        self.assertEqual(444,a["chunk_size"]); self.assertEqual(len(self.b["chunks"]),a["chunk_count"])
        self.assertTrue(all(x["encoded_length"]<=444 for x in self.b["chunks"]))

    def test_materialized_runtime_executes_without_site_packages_after_bounded_shard_handoff(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            marker=self.g.materialize(self.b,root,"test-exact-commit")
            self.assertTrue(marker["verified"])
            self.assertEqual(self.b["calendar_data"],marker["calendar_data"])
            shard=root/"data"/"calendar"/"ziwei_tw_interval"/"v1"/"years"/"2000.json"
            shard.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(DATA/"years"/"2000.json",shard)
            script=root/"smoke.py"
            script.write_text(
                "import json\n"
                "from tools.ziwei_calendar_provider import GregorianBirthInput\n"
                "from tools.ziwei_gregorian_pipeline import run_scope_a_gregorian_with_brightness\n"
                "r=run_scope_a_gregorian_with_brightness(GregorianBirthInput(2000,8,16,5,30),request_id='bundle-smoke',requested_subjects=('太陽',))\n"
                "assert r['status']=='PRODUCTION_ADMITTED'\n"
                "assert r['authority']['gregorian_input_adapter_admitted'] is True\n"
                "assert r['authority']['brightness_profile_admitted'] is True\n"
                "assert r['input_adapter']['calendar']['raw_lunar_conversion']['day']==17\n"
                "assert r['input_adapter']['calendar']['dataset']['required_shards']==['years/2000.json']\n"
                "assert r['input_adapter']['calendar']['boundaries']['runtime_lunar_python_dependency'] is False\n"
                "print(json.dumps({'ok':True,'claims':r['interpretation']['selected_claim_ids']},ensure_ascii=False))\n",
                encoding="utf-8",
            )
            env=dict(os.environ); env["PYTHONPATH"]=str(root)
            p=subprocess.run([sys.executable,"-S",str(script)],cwd=root,env=env,text=True,capture_output=True)
            self.assertEqual(0,p.returncode,msg=p.stdout+"\n"+p.stderr)
            self.assertIn('"ok": true',p.stdout)

if __name__=="__main__": unittest.main()
