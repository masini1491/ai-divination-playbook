from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools.build_ziwei_calendar_interval_dataset import (
    SELECTED_RANGE_STATUS,
    UNSELECTED_RANGE_STATUS,
    build_dataset,
    dependency_source_identity,
    range_contract,
)
from tools.validate_ziwei_calendar_interval_dataset import DatasetValidationError, validate_dataset

class ZiWeiCalendarIntervalDatasetTests(unittest.TestCase):
    def test_selected_candidate_range_contract(self):
        selected=range_contract(1900,2100)
        self.assertTrue(selected["selected"])
        self.assertEqual(SELECTED_RANGE_STATUS,selected["status"])
        self.assertFalse(selected["production_admitted"])
        ordinary=range_contract(1999,2001)
        self.assertFalse(ordinary["selected"])
        self.assertEqual(UNSELECTED_RANGE_STATUS,ordinary["status"])

    def test_dependency_source_identity_is_pinned(self):
        identity=dependency_source_identity()
        self.assertEqual(34,identity["file_count"])
        self.assertGreater(identity["total_bytes"],0)
        self.assertEqual(64,len(identity["sha256"]))

    def test_small_range_build_validate_and_rebuild(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            m=build_dataset(root,1999,2001)
            self.assertFalse(m["production_admitted"])
            self.assertFalse(m["selected_product_range"]["selected"])
            self.assertEqual({"start_year":1999,"end_year":2001},m["requested_gregorian_range"])
            self.assertEqual({"start_year":1999,"end_year":2002},m["materialized_year_range"])
            self.assertEqual(4,m["summary"]["shard_count"])
            self.assertTrue((root/"provenance.json").is_file())
            self.assertTrue((root/"ATTRIBUTION.md").is_file())
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

    def test_extra_shard_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            build_dataset(root,2000,2000)
            (root/"years"/"9999.json").write_text("{}\n",encoding="utf-8")
            with self.assertRaisesRegex(DatasetValidationError,"shard file inventory mismatch"):
                validate_dataset(root)

    def test_missing_shard_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            m=build_dataset(root,2000,2000)
            (root/m["shards"][0]["path"]).unlink()
            with self.assertRaisesRegex(DatasetValidationError,"shard file inventory mismatch|shard missing"):
                validate_dataset(root)

    def test_metadata_tamper_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            build_dataset(root,2000,2000)
            p=root/"provenance.json"
            p.write_text(p.read_text(encoding="utf-8")+"\n",encoding="utf-8")
            with self.assertRaisesRegex(DatasetValidationError,"metadata identity mismatch"):
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
