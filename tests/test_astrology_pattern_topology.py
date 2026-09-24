from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from tools.astrology_pattern_topology import (
    PatternTopologyError,
    build_pattern_topology_projection,
)
from tools.astrology_provider import build_natal_bundle

ROOT = Path(__file__).resolve().parents[1]
PARTICIPANT = "aspect-participants-core-bodies-v1"
ASPECT = "major-aspects-v1"
ORB = "major-aspect-orbs-v1"
PATTERN = "aspect-pattern-topology-major-v1"
REPORT_ALL = "pattern-projection-report-all-valid-v1"
SUPPRESS = "pattern-projection-suppress-strict-subsets-v1"


def base_bundle() -> dict:
    return build_natal_bundle(
        local_datetime="1990-06-15T12:00:00",
        timezone_name="UTC",
        latitude=51.5074,
        longitude=0.0,
        house_system="Whole Sign",
        subject_ref="subject:synthetic-e6",
    )


def aspect(left: str, name: str, right: str, n: int) -> dict:
    return {
        "fact_id": f"fact:aspect:synthetic:{n}",
        "aspect": name,
        "orb_deg": 0.0,
        "left_ref": f"fact:object:{left.lower()}",
        "right_ref": f"fact:object:{right.lower()}",
        "scope": "natal",
        "participant_policy_id": PARTICIPANT,
        "aspect_policy_id": ASPECT,
        "orb_policy_id": ORB,
    }


def projected(bundle: dict, policy: str = REPORT_ALL) -> dict:
    return build_pattern_topology_projection(
        bundle,
        participant_policy_id=PARTICIPANT,
        aspect_policy_id=ASPECT,
        orb_policy_id=ORB,
        pattern_policy_id=PATTERN,
        pattern_projection_policy_id=policy,
    )


class AstrologyPatternTopologyTests(unittest.TestCase):
    def test_t_square_is_detected_with_full_policy_provenance(self):
        bundle = base_bundle()
        bundle["facts"]["aspects"] = [
            aspect("Sun", "square", "Moon", 1),
            aspect("Sun", "opposition", "Mars", 2),
            aspect("Moon", "square", "Mars", 3),
        ]
        result = projected(bundle)
        rows = [row for row in result["patterns"] if row["pattern_type"] == "T-Square"]
        self.assertEqual(1, len(rows))
        row = rows[0]
        self.assertEqual(PATTERN, row["pattern_policy_id"])
        self.assertEqual(PARTICIPANT, row["participant_policy_id"])
        self.assertEqual(ASPECT, row["aspect_policy_id"])
        self.assertEqual(ORB, row["orb_policy_id"])
        self.assertEqual("conjunction-clusters-transitive-v1", row["conjunction_cluster_policy_id"])
        self.assertEqual(3, len(row["supporting_aspect_ids"]))

    def test_grand_cross_report_all_and_suppress_nested_are_distinct_policies(self):
        bundle = base_bundle()
        bundle["facts"]["aspects"] = [
            aspect("Sun", "square", "Moon", 1),
            aspect("Sun", "opposition", "Mars", 2),
            aspect("Sun", "square", "Jupiter", 3),
            aspect("Moon", "square", "Mars", 4),
            aspect("Moon", "opposition", "Jupiter", 5),
            aspect("Mars", "square", "Jupiter", 6),
        ]
        all_types = [row["pattern_type"] for row in projected(bundle, REPORT_ALL)["patterns"]]
        suppressed_types = [row["pattern_type"] for row in projected(bundle, SUPPRESS)["patterns"]]
        self.assertIn("Grand Cross", all_types)
        self.assertIn("T-Square", all_types)
        self.assertEqual(["Grand Cross"], suppressed_types)

    def test_conjunctions_form_transitive_vertex_clusters(self):
        bundle = base_bundle()
        bundle["facts"]["aspects"] = [
            aspect("Sun", "conjunction", "Moon", 1),
            aspect("Sun", "trine", "Mars", 2),
            aspect("Moon", "trine", "Jupiter", 3),
            aspect("Mars", "trine", "Jupiter", 4),
        ]
        result = projected(bundle)
        rows = [row for row in result["patterns"] if row["pattern_type"] == "Grand Trine"]
        self.assertEqual(1, len(rows))
        clusters = rows[0]["vertex_clusters"]
        self.assertIn(["Moon", "Sun"], clusters)
        self.assertIn(["Mars"], clusters)
        self.assertIn(["Jupiter"], clusters)

    def test_e6_rejects_spoofed_provider_participant_set(self):
        bundle = base_bundle()
        bundle["provider"]["aspect_policies"]["participant_object_ids"].append("Descendant")
        with self.assertRaisesRegex(PatternTopologyError, "requires an admitted Astrology fact bundle|participant_object_ids"):
            projected(bundle)

    def test_e6_rejects_extended_object_even_with_core_policy_labels(self):
        bundle = base_bundle()
        bundle["fact_source"] = "user_supplied_structured_export"
        bundle["calculation_verification"] = "user_asserted"
        bundle["facts"]["objects"].append(
            {
                "fact_id": "fact:object:syntheticdesc",
                "object_type": "angle",
                "object_id": "Descendant",
            }
        )
        bundle["facts"]["aspects"] = [
            {
                "fact_id": "fact:aspect:synthetic:extended",
                "aspect": "square",
                "orb_deg": 0.0,
                "left_ref": "fact:object:sun",
                "right_ref": "fact:object:syntheticdesc",
                "scope": "natal",
                "participant_policy_id": PARTICIPANT,
                "aspect_policy_id": ASPECT,
                "orb_policy_id": ORB,
            }
        ]
        with self.assertRaisesRegex(PatternTopologyError, "requires an admitted Astrology fact bundle|outside admitted E5 participant policy"):
            projected(bundle)

    def test_policy_ids_are_explicit_and_fail_closed(self):
        bundle = base_bundle()
        with self.assertRaisesRegex(PatternTopologyError, "participant_policy_id"):
            build_pattern_topology_projection(
                bundle,
                participant_policy_id="aspect-participants-core-plus-angles-v1",
                aspect_policy_id=ASPECT,
                orb_policy_id=ORB,
                pattern_policy_id=PATTERN,
                pattern_projection_policy_id=REPORT_ALL,
            )
        with self.assertRaisesRegex(PatternTopologyError, "pattern_projection_policy_id"):
            build_pattern_topology_projection(
                bundle,
                participant_policy_id=PARTICIPANT,
                aspect_policy_id=ASPECT,
                orb_policy_id=ORB,
                pattern_policy_id=PATTERN,
                pattern_projection_policy_id="default",
            )

    def test_current_policy_does_not_admit_yod_stellium_or_quintile_patterns(self):
        manifest = json.loads((ROOT / "ASTROLOGY_PRODUCTION_ADMISSION_V1.json").read_text(encoding="utf-8"))
        policy = manifest["orchestration"]["policy_projections"]["pattern_topology"]
        self.assertEqual(
            ["T-Square", "Grand Trine", "Grand Cross", "Kite", "Mystic Rectangle", "Cradle", "Grand Sextile"],
            policy["admitted_pattern_types"],
        )
        self.assertIn("Yod", policy["unsupported_pattern_types"])
        self.assertIn("Stellium", policy["unsupported_pattern_types"])
        self.assertIn("Grand Quintile", policy["unsupported_pattern_types"])
        self.assertEqual("forbidden", policy["silent_default"])
        self.assertFalse(policy["semantic_interpretation_authority"])


if __name__ == "__main__":
    unittest.main()
