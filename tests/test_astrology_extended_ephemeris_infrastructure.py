from __future__ import annotations

import json
import unittest
from pathlib import Path

from tools.astrology_extended_ephemeris import (
    DATASET_ID,
    DATASET_SHA256,
    OBJECT_IDS,
    REPRESENTATION_ID,
    ExtendedEphemerisError,
    required_shard_for_utc,
)

ROOT=Path(__file__).resolve().parents[1]

class AstrologyExtendedEphemerisInfrastructureTests(unittest.TestCase):
    def test_admission_is_fail_closed_pending_data_publish(self):
        data=json.loads((ROOT/"ASTROLOGY_EXTENDED_EPHEMERIS_ADMISSION_V1.json").read_text())
        self.assertEqual("AWAITING_DATA_PUBLISH",data["status"])
        self.assertEqual("explicit_request_only",data["activation"])
        self.assertEqual(list(OBJECT_IDS),data["object_ids"])
        self.assertEqual(DATASET_ID,data["dataset"]["dataset_id"])
        self.assertEqual(DATASET_SHA256,data["dataset"]["expected_sha256"])
        self.assertEqual(REPRESENTATION_ID,data["dataset"]["representation_id"])
        self.assertIsNone(data["dataset"]["exact_data_commit"])
        self.assertFalse(data["calculation_policy"]["default_aspect_participation"])
        self.assertFalse(data["calculation_policy"]["semantic_interpretation_authority"])
        self.assertEqual("not_admitted",data["calculation_policy"]["transit"])
        self.assertEqual("not_admitted",data["calculation_policy"]["unknown_time"])

    def test_publisher_is_digest_pinned_and_non_force(self):
        text=(ROOT/".github/workflows/publish-astrology-extended-ephemeris.yml").read_text()
        self.assertIn(DATASET_SHA256,text)
        self.assertIn("data/astrology-extended-ephemeris-v1",text)
        self.assertIn("git push origin",text)
        self.assertNotIn("--force",text)
        self.assertIn("generated_bytes",text)

    def test_generator_output_is_dataset_root_not_nested_repo_path(self):
        text=(ROOT/"tools/generate_astrology_extended_ephemeris.py").read_text()
        self.assertIn("root = OUTPUT",text)
        self.assertNotIn('root = OUTPUT / "data" / "astrology" / "extended_ephemeris" / "v1"',text)

    def test_evaluator_has_no_network_fallback(self):
        text=(ROOT/"tools/astrology_extended_ephemeris.py").read_text()
        self.assertNotIn("urllib",text)
        self.assertNotIn("requests",text)
        self.assertIn("required extended ephemeris shard missing",text)

    def test_required_shard_contract_rejects_out_of_range(self):
        manifest={
          "representation":{
            "coverage_start":"1825-04-01T00:00:00+00:00",
            "admitted_output_window_end":"2350-10-01T00:00:00+00:00",
            "segment_width_days":60,
            "segment_count":3199,
          },
          "dataset":{"shards":[{"shard_index":0,"first_segment":0,"segment_count":192}]},
        }
        with self.assertRaises(ExtendedEphemerisError):
            required_shard_for_utc("1800-01-01T00:00:00Z",manifest)

if __name__=="__main__":
    unittest.main()
