from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools.build_ziwei_calendar_interval_dataset import build_dataset
from tools.validate_ziwei_calendar_interval_dataset import DatasetValidationError, validate_dataset

class ZiWeiCalendarIntervalDatasetTests(unittest.TestCase):
    def test_small_range_build_validate_and_rebuild(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            m=build_dataset(root,1999,2001)
            self.assertFalse(m["production_admitted"])
            self.assertEqual({"start_year":1999,"end_year":2001},m["requested_gregorian_range"])
            self.assertEqual({"start_year":1999,"end_year":2002},m["materialized_year_range"])
            self.assertEqual(4,m["summary"]["shard_count"])
            r=validate_dataset(root,rebuild=True)
            self.assertEqual("PASS",r["status"])
            self.assertTrue(r["deterministic_rebuild_match"])
            self.assertEqual(m["aggregate_hash"],r["aggregate_hash"])

    def test_tampered_shard_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            m=build_dataset(root,2000,2000)
            p=root/m["shards"][0]["path"]
            p.write_text(p.read_text(encoding="utf-8")+"\n",encoding="utf-8")
            with self.assertRaisesRegex(DatasetValidationError,"sha256 mismatch"):
                validate_dataset(root)

    def test_missing_shard_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            m=build_dataset(root,2000,2000)
            (root/m["shards"][0]["path"]).unlink()
            with self.assertRaisesRegex(DatasetValidationError,"shard missing"):
                validate_dataset(root)

    def test_manifest_dependency_tamper_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            build_dataset(root,2000,2000)
            p=root/"MANIFEST.json"
            m=json.loads(p.read_text(encoding="utf-8"))
            m["dependency"]["revision"]="wrong"
            p.write_text(json.dumps(m,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
            with self.assertRaisesRegex(DatasetValidationError,"dependency provenance mismatch"):
                validate_dataset(root)

    def test_invalid_range_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):
                build_dataset(Path(td),2100,1900)
            with self.assertRaises(ValueError):
                build_dataset(Path(td),9999,9999)

if __name__=="__main__":
    unittest.main()
