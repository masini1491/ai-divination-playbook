from __future__ import annotations
import importlib.util, json, os, subprocess, sys, tempfile
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
GEN=ROOT/"tools"/"build_astrology_core_bundle.py"
BUNDLE=ROOT/"runtime"/"astrology"/"CHATGPT_DETERMINISTIC_CORE_BUNDLE.json"

def load_gen():
    spec=importlib.util.spec_from_file_location("build_astrology_core_bundle",GEN)
    if spec is None or spec.loader is None: raise RuntimeError("cannot load generator")
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

class AstrologyCoreToolBundleTests(unittest.TestCase):
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

    def test_dependency_is_exact_and_core_only(self):
        d=self.b["dependency"]
        self.assertEqual("astronomy-engine",d["package"])
        self.assertEqual("2.1.19",d["version"])
        self.assertEqual("865d3da7d8112bbc7911238052c6af4aaf877181",d["revision"])
        self.assertEqual("pypi-wheel-2.1.19-runtime-files-pinned-by-sha256",d["byte_identity"])
        self.assertEqual(2,d["runtime_file_count"])
        self.assertFalse(self.b["execution_contract"]["dependency_install_required_after_materialization"])
        self.assertFalse(self.b["scope"]["place_resolver_included"])
        self.assertFalse(self.b["scope"]["geonamescache_included"])

    def test_chunk_contract_is_bounded_per_chunk(self):
        a=self.b["archive"]
        self.assertEqual(444,a["chunk_size"])
        self.assertEqual(len(self.b["chunks"]),a["chunk_count"])
        self.assertTrue(all(x["encoded_length"]<=444 for x in self.b["chunks"]))

    def test_materialized_coordinates_runtime_executes_without_site_packages(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            marker=self.g.materialize(self.b,root,"test-exact-commit")
            self.assertTrue(marker["verified"])
            script=root/"smoke.py"
            script.write_text(
                "import json\n"
                "from tools.astrology_orchestrator import run_request\n"
                "import tools.astrology_transit_provider\n"
                "q={'schema_name':'astrology_reading_request','schema_version':'1.0.0','reading_mode':'natal','subject_ref':'synthetic-core-bundle-fixture','birth':{'local_datetime':'2000-01-01T12:00:00','birth_time_certainty':'exact','house_system':'Whole Sign','location':{'coordinates':{'latitude':0.0,'longitude':0.0,'timezone_name':'UTC'}}}}\n"
                "r=run_request(q)\n"
                "assert r['status']=='admitted' and r['interpretation_allowed'] is True\n"
                "assert r['input_resolution']['resolution_mode']=='explicit_coordinates'\n"
                "assert r['fact_bundles']['natal']['provider']['provider_id']=='astronomy-engine-natal-v1'\n"
                "print(json.dumps({'ok':True,'mode':r['input_resolution']['resolution_mode']}))\n",
                encoding="utf-8",
            )
            env=dict(os.environ); env["PYTHONPATH"]=str(root)
            p=subprocess.run([sys.executable,"-S",str(script)],cwd=root,env=env,text=True,capture_output=True)
            self.assertEqual(0,p.returncode,msg=p.stdout+"\n"+p.stderr)
            self.assertIn('"ok": true',p.stdout)

if __name__=="__main__": unittest.main()
