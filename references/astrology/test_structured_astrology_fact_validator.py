#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
VALIDATOR_PATH = HERE / "validate_structured_astrology_fact.py"
EXAMPLE_PATH = HERE / "structured_astrology_fact_example.json"

spec = importlib.util.spec_from_file_location("saf_validator", VALIDATOR_PATH)
validator = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = validator
spec.loader.exec_module(validator)


def codes(errors):
    return {error["code"] if isinstance(error, dict) else error.code for error in errors}


class StructuredAstrologyFactValidatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))

    def validate(self, record):
        return validator.validate_record(record)

    def test_reference_example_is_valid(self):
        self.assertEqual(self.validate(copy.deepcopy(self.base)), [])

    def test_effective_backend_is_required(self):
        record = copy.deepcopy(self.base)
        del record["provenance"]["engine"]["effective_backend"]
        self.assertIn("ENGINE_EFFECTIVE_BACKEND_REQUIRED", codes(self.validate(record)))

    def test_sidereal_requires_ayanamsa(self):
        record = copy.deepcopy(self.base)
        record["configuration"]["zodiac_system"] = "sidereal"
        record["configuration"]["ayanamsa"] = None
        self.assertIn("SIDEREAL_AYANAMSA_REQUIRED", codes(self.validate(record)))

    def test_exact_degree_range_is_enforced(self):
        record = copy.deepcopy(self.base)
        record["facts"]["targets"][0]["longitude"]["exact_deg"] = 360.0
        self.assertIn("DEGREE_RANGE_INVALID", codes(self.validate(record)))

    def test_bounded_degree_requires_ranges(self):
        record = copy.deepcopy(self.base)
        record["facts"]["targets"][0]["longitude"] = {"status": "bounded"}
        self.assertIn("DEGREE_BOUNDED_RANGES_REQUIRED", codes(self.validate(record)))

    def test_ambiguous_time_requires_multiple_candidates(self):
        record = copy.deepcopy(self.base)
        record["facts"]["events"][0]["time"] = {
            "status": "ambiguous",
            "candidate_utc": ["2026-06-16T15:44:17.088Z"],
        }
        self.assertIn("TEMPORAL_AMBIGUOUS_CANDIDATES_REQUIRED", codes(self.validate(record)))

    def test_event_must_be_inside_search_window(self):
        record = copy.deepcopy(self.base)
        record["facts"]["events"][0]["time"]["exact_utc"] = "2026-08-11T00:00:00Z"
        self.assertIn("EVENT_TIME_OUTSIDE_SEARCH_WINDOW", codes(self.validate(record)))

    def test_transit_target_ref_must_resolve(self):
        record = copy.deepcopy(self.base)
        record["facts"]["events"][0]["target_ref"] = "target:missing"
        self.assertIn("EVENT_TARGET_REF_UNRESOLVED", codes(self.validate(record)))

    def test_duplicate_semantic_passage_identity_is_rejected(self):
        record = copy.deepcopy(self.base)
        dup = copy.deepcopy(record["facts"]["events"][0])
        dup["event_id"] = "event:duplicate-but-new-id"
        record["facts"]["events"].append(dup)
        self.assertIn("PASSAGE_IDENTITY_DUPLICATE", codes(self.validate(record)))

    def test_unknown_birth_time_cannot_make_house_available(self):
        record = copy.deepcopy(self.base)
        record["record_kind"] = "chart_snapshot"
        record["provenance"]["time"]["birth_time_certainty"] = "unknown"
        record["facts"]["houses"] = [{
            "fact_id": "house:1",
            "evidence_layer": "L2",
            "availability": {"status": "available"},
            "house_number": 1,
            "cusp_longitude": {"status": "exact", "exact_deg": 15.0},
        }]
        self.assertIn("UNKNOWN_TIME_HOUSE_AVAILABLE_FORBIDDEN", codes(self.validate(record)))

    def test_unknown_birth_time_cannot_make_angle_available(self):
        record = copy.deepcopy(self.base)
        record["record_kind"] = "chart_snapshot"
        record["provenance"]["time"]["birth_time_certainty"] = "unknown"
        record["facts"]["objects"] = [{
            "fact_id": "object:asc",
            "evidence_layer": "L2",
            "availability": {"status": "available"},
            "object_id": "Ascendant",
            "object_type": "angle",
            "longitude": {"status": "exact", "exact_deg": 15.0},
        }]
        self.assertIn("UNKNOWN_TIME_ANGLE_AVAILABLE_FORBIDDEN", codes(self.validate(record)))

    def test_l3_l4_policy_fields_are_rejected_from_fact_core(self):
        record = copy.deepcopy(self.base)
        record["facts"]["targets"][0]["score"] = 99
        self.assertIn("L3_L4_FIELD_FORBIDDEN", codes(self.validate(record)))

    def test_ambiguous_local_wall_time_must_not_choose_resolved_utc(self):
        record = copy.deepcopy(self.base)
        record["provenance"]["time"] = {
            "input_kind": "local_wall_time",
            "original_value": "2026-10-25 02:30:00",
            "iana_timezone": "Europe/Stockholm",
            "resolution_status": "ambiguous",
            "candidate_utc": ["2026-10-25T00:30:00Z", "2026-10-25T01:30:00Z"],
            "resolved_utc": "2026-10-25T00:30:00Z",
        }
        self.assertIn("TIME_AMBIGUOUS_RESOLUTION_FORBIDDEN", codes(self.validate(record)))

    def test_nonexistent_local_wall_time_must_not_resolve(self):
        record = copy.deepcopy(self.base)
        record["provenance"]["time"] = {
            "input_kind": "local_wall_time",
            "original_value": "2026-03-29 02:30:00",
            "iana_timezone": "Europe/Stockholm",
            "resolution_status": "nonexistent",
            "resolved_utc": "2026-03-29T01:30:00Z",
        }
        self.assertIn("TIME_NONEXISTENT_RESOLUTION_FORBIDDEN", codes(self.validate(record)))

    def test_bounded_target_and_bounded_event_time_are_valid(self):
        record = copy.deepcopy(self.base)
        target = record["facts"]["targets"][0]
        target["availability"] = {"status": "bounded", "reasons": ["synthetic uncertainty interval"]}
        target["longitude"] = {
            "status": "bounded",
            "ranges_deg": [{"start_deg": 109.5, "end_deg": 110.5}],
        }
        event = record["facts"]["events"][0]
        event["availability"] = {"status": "bounded", "reasons": ["target longitude bounded"]}
        event["time"] = {
            "status": "bounded",
            "start_utc": "2026-06-16T02:49:00Z",
            "end_utc": "2026-06-17T05:06:00Z",
        }
        record["facts"]["events"] = [event]
        self.assertEqual(self.validate(record), [])

    def test_ambiguous_local_time_provenance_can_be_valid_without_calculated_facts(self):
        record = copy.deepcopy(self.base)
        record["record_kind"] = "chart_snapshot"
        record["provenance"]["time"] = {
            "input_kind": "local_wall_time",
            "original_value": "2026-10-25 02:30:00",
            "iana_timezone": "Europe/Stockholm",
            "resolution_status": "ambiguous",
            "candidate_utc": ["2026-10-25T00:30:00Z", "2026-10-25T01:30:00Z"],
        }
        record["facts"] = {"targets": [], "objects": [], "houses": [], "aspects": [], "events": []}
        self.assertEqual(self.validate(record), [])

    def test_unknown_time_unavailable_house_is_valid(self):
        record = copy.deepcopy(self.base)
        record["record_kind"] = "chart_snapshot"
        record["provenance"]["time"]["birth_time_certainty"] = "unknown"
        record["facts"] = {
            "targets": [],
            "objects": [],
            "houses": [{
                "fact_id": "house:1",
                "evidence_layer": "L2",
                "availability": {"status": "unavailable", "reasons": ["birth time required"]},
                "house_number": 1,
                "cusp_longitude": {"status": "unavailable"},
            }],
            "aspects": [],
            "events": [],
        }
        self.assertEqual(self.validate(record), [])

    def test_station_and_ingress_event_shapes_are_valid(self):
        record = copy.deepcopy(self.base)
        record["facts"]["targets"] = []
        record["facts"]["events"] = [
            {
                "event_id": "event:mercury-station-1",
                "event_kind": "station",
                "availability": {"status": "available"},
                "time": {"status": "exact", "exact_utc": "2026-06-29T17:35:59Z"},
                "search_window_utc": {"start": "2026-06-01T00:00:00Z", "end": "2026-08-10T00:00:00Z"},
                "body_ref": "Mercury",
                "transition": "direct_to_retrograde",
                "speed_before_deg_per_day": 0.1,
                "speed_at_root_deg_per_day": 0.0,
                "speed_after_deg_per_day": -0.1,
            },
            {
                "event_id": "event:venus-ingress-1",
                "event_kind": "ingress",
                "availability": {"status": "available"},
                "time": {"status": "exact", "exact_utc": "2026-07-20T00:00:00Z"},
                "search_window_utc": {"start": "2026-06-01T00:00:00Z", "end": "2026-08-10T00:00:00Z"},
                "body_ref": "Venus",
                "zodiac_system": "tropical",
                "boundary_longitude_deg": 120.0,
                "from_sign": "Cancer",
                "to_sign": "Leo",
                "motion_direction": "direct",
                "ingress_kind": "direct_ingress",
            },
        ]
        self.assertEqual(self.validate(record), [])

    def test_aspect_absolute_error_must_match_signed_error(self):
        record = copy.deepcopy(self.base)
        record["facts"]["aspects"] = [{
            "fact_id": "aspect:test",
            "evidence_layer": "L2",
            "availability": {"status": "available"},
            "left_ref": "Mercury",
            "right_ref": "Sun",
            "target_angle_deg": 60.0,
            "separation_deg": 60.2,
            "signed_error_deg": 0.2,
            "absolute_error_deg": 0.3,
            "applying_state": "separating",
        }]
        self.assertIn("ASPECT_ERROR_INCONSISTENT", codes(self.validate(record)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
