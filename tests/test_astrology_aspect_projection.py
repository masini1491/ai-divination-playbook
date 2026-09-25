from __future__ import annotations
import unittest
from tools.astrology_aspect_projection import AspectProjectionError, build_aspect_projection
from tools.astrology_provider import build_natal_bundle

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

class AstrologyExtendedAspectProjectionTests(unittest.TestCase):
    def test_core_plus_angles_is_explicit_and_semantics_free(self):
        result=build_aspect_projection(natal(),participant_policy_id="aspect-participants-core-plus-angles-v1")
        self.assertTrue(result["explicit_policy_required"])
        self.assertFalse(result["auto_include_new_objects"])
        self.assertFalse(result["semantic_interpretation_authority"])
        self.assertIn("Ascendant",result["participant_object_ids"])
        self.assertIn("Descendant",result["participant_object_ids"])
        self.assertTrue(all(row["participant_policy_id"]==result["participant_policy_id"] for row in result["aspects"]))
    def test_south_node_policy_does_not_auto_include_angles_or_fortune(self):
        result=build_aspect_projection(natal("approximate"),participant_policy_id="aspect-participants-core-plus-south-node-v1")
        self.assertIn("SouthNode",result["participant_object_ids"])
        self.assertNotIn("Ascendant",result["participant_object_ids"])
        self.assertNotIn("PartOfFortune",result["participant_object_ids"])
    def test_angle_and_fortune_policies_require_exact_time(self):
        approx=natal("approximate")
        for policy in ("aspect-participants-core-plus-angles-v1","aspect-participants-core-plus-fortune-v1"):
            with self.assertRaisesRegex(AspectProjectionError,"requires exact birth time"):
                build_aspect_projection(approx,participant_policy_id=policy)
    def test_unknown_policy_fails_closed(self):
        with self.assertRaisesRegex(AspectProjectionError,"explicit admitted participant policy required"):
            build_aspect_projection(natal(),participant_policy_id="aspect-participants-everything-v999")

if __name__=="__main__": unittest.main()
