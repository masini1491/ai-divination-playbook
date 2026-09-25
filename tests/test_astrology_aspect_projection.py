from __future__ import annotations
import json
import unittest
from pathlib import Path
from tools.astrology_aspect_projection import (
    ASPECT_POLICY_ID,
    ORB_POLICY_ID,
    PARTICIPANT_POLICIES,
    AspectProjectionError,
    build_aspect_projection,
)
from tools.astrology_provider import build_natal_bundle

ROOT = Path(__file__).resolve().parents[1]

def natal(certainty="exact"):
    return build_natal_bundle(
        local_datetime="1990-06-15T10:00:00",
        timezone_name="Asia/Tokyo",
        latitude=35.6895,
        longitude=139.6917,
        house_system="Whole Sign",
        subject_ref="fixture-extended-aspects",
        birth_time_certainty=certainty,
    )

def project(bundle, participant_policy_id):
    return build_aspect_projection(
        bundle,
        participant_policy_id=participant_policy_id,
        aspect_policy_id=ASPECT_POLICY_ID,
        orb_policy_id=ORB_POLICY_ID,
    )

class AstrologyExtendedAspectProjectionTests(unittest.TestCase):
    def test_core_plus_angles_is_explicit_and_semantics_free(self):
        result=project(natal(),"aspect-participants-core-plus-angles-v1")
        self.assertTrue(result["explicit_policy_required"])
        self.assertFalse(result["auto_include_new_objects"])
        self.assertFalse(result["semantic_interpretation_authority"])
        self.assertIn("Ascendant",result["participant_object_ids"])
        self.assertIn("Descendant",result["participant_object_ids"])
        self.assertTrue(all(row["participant_policy_id"]==result["participant_policy_id"] for row in result["aspects"]))

    def test_south_node_policy_does_not_auto_include_angles_or_fortune(self):
        result=project(natal("approximate"),"aspect-participants-core-plus-south-node-v1")
        self.assertIn("SouthNode",result["participant_object_ids"])
        self.assertNotIn("Ascendant",result["participant_object_ids"])
        self.assertNotIn("PartOfFortune",result["participant_object_ids"])

    def test_angle_and_fortune_policies_require_exact_time(self):
        approx=natal("approximate")
        for policy in ("aspect-participants-core-plus-angles-v1","aspect-participants-core-plus-fortune-v1"):
            with self.assertRaisesRegex(AspectProjectionError,"requires exact birth time"):
                project(approx,policy)

    def test_all_policy_ids_are_explicit_and_fail_closed(self):
        bundle=natal()
        with self.assertRaisesRegex(AspectProjectionError,"participant policy"):
            build_aspect_projection(
                bundle,
                participant_policy_id="aspect-participants-everything-v999",
                aspect_policy_id=ASPECT_POLICY_ID,
                orb_policy_id=ORB_POLICY_ID,
            )
        with self.assertRaisesRegex(AspectProjectionError,"aspect policy"):
            build_aspect_projection(
                bundle,
                participant_policy_id="aspect-participants-core-plus-south-node-v1",
                aspect_policy_id="major-aspects-v999",
                orb_policy_id=ORB_POLICY_ID,
            )
        with self.assertRaisesRegex(AspectProjectionError,"orb policy"):
            build_aspect_projection(
                bundle,
                participant_policy_id="aspect-participants-core-plus-south-node-v1",
                aspect_policy_id=ASPECT_POLICY_ID,
                orb_policy_id="major-aspect-orbs-v999",
            )

    def test_runtime_policy_membership_matches_machine_admission(self):
        manifest=json.loads((ROOT/"ASTROLOGY_PRODUCTION_ADMISSION_V1.json").read_text(encoding="utf-8"))
        definitions=manifest["aspect_policy"]["extended_participant_policies"]
        self.assertEqual(set(PARTICIPANT_POLICIES),set(definitions))
        for policy_id,runtime_policy in PARTICIPANT_POLICIES.items():
            admitted=definitions[policy_id]
            self.assertEqual(list(runtime_policy["object_ids"]),admitted["participant_object_ids"])
            self.assertEqual(runtime_policy["exact_birth_time_required"],admitted["exact_birth_time_required"])

if __name__=="__main__": unittest.main()
