from __future__ import annotations
import importlib.util, json, os, subprocess, sys, tempfile
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
GEN=ROOT/"tools"/"build_ziwei_tool_bundle.py"
BUNDLE=ROOT/"runtime"/"ziwei"/"CHATGPT_DETERMINISTIC_TOOL_BUNDLE.json"

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
        self.assertFalse(self.b["execution_contract"]["interpretation_authority"])
        self.assertFalse(self.b["execution_contract"]["new_claim_authority"])

    def test_calendar_data_is_query_bounded_and_dependency_not_bundled(self):
        d=self.b["build_dependency"]
        self.assertEqual("lunar_python",d["package"])
        self.assertEqual("1.4.8",d["version"])
        self.assertEqual("000c8a3d74eed098d6256a28fdd51b869324c559",d["revision"])
        self.assertFalse(d["runtime_bundled"])
        self.assertEqual(0,d["runtime_file_count"])
        self.assertFalse(self.b["execution_contract"]["dependency_install_required_after_materialization"])
        self.assertTrue(self.b["execution_contract"]["calendar_shard_materialization_required_for_gregorian_input"])
        c=self.b["calendar_data"]
        self.assertEqual("ziwei_tw_interval_1900_2100_candidate_v1",c["dataset_id"])
        self.assertEqual(1,c["ordinary_max_files"])
        self.assertEqual(2,c["year_edge_23_max_files"])
        self.assertEqual({"playbook"},{x["origin"] for x in self.b["source_files"]})
        paths={x["path"] for x in self.b["source_files"]}
        self.assertIn("tools/ziwei_calendar_data_provider.py",paths)
        self.assertIn("data/calendar/ziwei_tw_interval/v1/MANIFEST.json",paths)
        self.assertNotIn("tools/ziwei_calendar_lunar_python_reference.py",paths)

    def test_chunk_contract_is_bounded(self):
        a=self.b["archive"]
        self.assertEqual(444,a["chunk_size"]); self.assertEqual(len(self.b["chunks"]),a["chunk_count"])
        self.assertTrue(all(x["encoded_length"]<=444 for x in self.b["chunks"]))

    def test_materialized_runtime_executes_without_site_packages(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            marker=self.g.materialize(self.b,root,"test-exact-commit")
            self.assertTrue(marker["verified"])
            shard=self.g.materialize_repo_data_file("data/calendar/ziwei_tw_interval/v1/years/2000.json",root)
            self.assertEqual(40,len(shard["git_blob_sha"]))
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
                "print(json.dumps({'ok':True,'claims':r['interpretation']['selected_claim_ids']},ensure_ascii=False))\n",
                encoding="utf-8",
            )
            env=dict(os.environ); env["PYTHONPATH"]=str(root)
            p=subprocess.run([sys.executable,"-S",str(script)],cwd=root,env=env,text=True,capture_output=True)
            self.assertEqual(0,p.returncode,msg=p.stdout+"\n"+p.stderr)
            self.assertIn('"ok": true',p.stdout)

if __name__=="__main__": unittest.main()
