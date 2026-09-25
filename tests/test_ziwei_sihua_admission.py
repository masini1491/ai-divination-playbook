from __future__ import annotations

import json
from pathlib import Path
import unittest

from tools import ziwei_claim_retrieval as retrieval
from tools.ziwei_natal_provider import NormalizedNatalInput
from tools.ziwei_runtime import (
    SIHUA_MODULE,
    ZiWeiReadingRequest,
    request_from_transport,
    request_to_transport,
    run_ziwei,
)
from tools.ziwei_sihua_provider import PROFILE_ID as SIHUA_PROFILE_ID

ROOT=Path(__file__).resolve().parents[1]
SIHUA_REGISTRY=ROOT/"references"/"ziwei"/"ziwei_interpretation_claim_registry_sihua_v0.json"
CLAIM_IDS={
    "ZW-SIHUA-TANLANG-LU-001",
    "ZW-SIHUA-TAIYANG-JI-001",
    "ZW-SIHUA-TAIYIN-JI-001",
}

class ZiWeiSihuaAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.birth=NormalizedNatalInput(1987,5,20,"酉","synthetic:sihua-admission")

    def test_manifest_admits_profile_facts_and_three_bounded_claims(self):
        m=json.loads((ROOT/"ZIWEI_SIHUA_ADMISSION_V1.json").read_text(encoding="utf-8"))
        self.assertEqual("PRODUCTION_ADMITTED_OPTIONAL_MODULE",m["status"])
        self.assertEqual(SIHUA_MODULE,m["module_id"])
        self.assertEqual(SIHUA_PROFILE_ID,m["profile_id"])
        self.assertEqual(3,m["scope"]["admitted_claims_added"])
        self.assertTrue(m["scope"]["transformed_star_interpretation_admitted"])
        self.assertFalse(m["interpretation"]["facts_only"])
        self.assertEqual(
            "references/ziwei/ziwei_interpretation_claim_registry_sihua_v0.json",
            m["interpretation"]["claim_registry"],
        )
        self.assertEqual(CLAIM_IDS,set(m["interpretation"]["admitted_claim_ids"]))
        self.assertFalse(m["interpretation"]["generic_transform_outcome_dictionary"])
        self.assertFalse(m["interpretation"]["cross_profile_averaging"])

    def test_runtime_emits_profile_bound_sihua_facts_and_evaluates_claim_registry(self):
        result=run_ziwei(ZiWeiReadingRequest(
            request_id="sihua-on",birth=self.birth,requested_subjects=("紫微",),
            optional_modules=(SIHUA_MODULE,),sihua_profile=SIHUA_PROFILE_ID,
        ))
        self.assertEqual([SIHUA_MODULE],result["runtime"]["optional_modules"])
        sihua=result["calculation"]["sihua"]
        self.assertEqual("丁",sihua["year_stem"])
        self.assertEqual(
            {"祿":"太陰","權":"天同","科":"天機","忌":"巨門"},
            sihua["by_transform"],
        )
        self.assertEqual(
            "computed_by_optional_sihua_profile",
            result["calculation"]["unsupported"]["four_transformations"],
        )
        self.assertTrue(result["authority"]["sihua_profile_admitted"])
        self.assertTrue(result["authority"]["sihua_transformed_star_claims_admitted"])
        self.assertEqual(3,result["authority"]["sihua_admitted_transformed_star_claim_count"])
        self.assertFalse(result["authority"]["generic_sihua_outcome_doctrine_admitted"])

        evaluations={
            x["claim_id"]:x for x in result["interpretation"]["conditional_evaluations"]
            if x["claim_id"] in CLAIM_IDS
        }
        self.assertEqual(CLAIM_IDS,set(evaluations))
        # 丁 year does not satisfy the three exact transformed-star identities,
        # but availability must be present: these are unsatisfied, not not_computed.
        self.assertTrue(all(x["state"]=="unsatisfied" for x in evaluations.values()))
        self.assertTrue(all(not x["missing_availability"] for x in evaluations.values()))

    def test_exact_profile_sihua_and_location_fact_activate_only_matching_claim(self):
        reg=json.loads(SIHUA_REGISTRY.read_text(encoding="utf-8"))
        packet=retrieval.FactPacket(
            packet_id="sihua-claim-match",
            interpretation_profile="ziwei.interpretation.tw_v1",
            temporal_scope="natal_baseline",
            facts=frozenset({
                "star_present:太陽",
                "fact_available:sihua",
                "fact_available:star_locations",
                "sihua_profile:sihua.default_v1",
                "sihua:甲:忌:太陽",
                "star_branch:太陽:卯",
            }),
            requested_subjects=frozenset({"太陽"}),
            enabled_source_ids=frozenset(),
        )
        got=retrieval.retrieve_claims(packet,[reg])
        selected={x["claim_id"] for x in got["selected_claims"]}
        self.assertEqual({"ZW-SIHUA-TAIYANG-JI-001"},selected)

        wrong_location=retrieval.FactPacket(
            packet_id="sihua-claim-no-match",
            interpretation_profile=packet.interpretation_profile,
            temporal_scope=packet.temporal_scope,
            facts=frozenset(set(packet.facts)-{"star_branch:太陽:卯"}|{"star_branch:太陽:申"}),
            requested_subjects=packet.requested_subjects,
            enabled_source_ids=packet.enabled_source_ids,
        )
        got2=retrieval.retrieve_claims(wrong_location,[reg])
        self.assertNotIn(
            "ZW-SIHUA-TAIYANG-JI-001",
            {x["claim_id"] for x in got2["selected_claims"]},
        )

    def test_transport_round_trip_preserves_profile_selector(self):
        request=ZiWeiReadingRequest(
            request_id="sihua-transport",birth=self.birth,
            optional_modules=(SIHUA_MODULE,),sihua_profile=SIHUA_PROFILE_ID,
        )
        payload=request_to_transport(request)
        self.assertEqual(SIHUA_PROFILE_ID,payload["sihua_profile"])
        self.assertEqual(request,request_from_transport(payload))

    def test_unknown_profile_and_profile_without_module_fail_closed(self):
        with self.assertRaisesRegex(ValueError,"unsupported sihua_profile"):
            run_ziwei(ZiWeiReadingRequest(
                request_id="bad-sihua",birth=self.birth,
                optional_modules=(SIHUA_MODULE,),sihua_profile="sihua.other",
            ))
        with self.assertRaisesRegex(ValueError,"sihua_profile requires sihua_v1"):
            run_ziwei(ZiWeiReadingRequest(
                request_id="bad-selector",birth=self.birth,sihua_profile=SIHUA_PROFILE_ID,
            ))

    def test_root_admission_counts_and_registry_binding(self):
        m=json.loads((ROOT/"ZIWEI_PRODUCTION_ADMISSION_V1.json").read_text(encoding="utf-8"))
        self.assertEqual(52,m["scope"]["admitted_claims"])
        self.assertEqual(59,m["scope"]["maximum_admitted_claims_with_optional_modules"])
        self.assertIn(SIHUA_MODULE,m["runtime"]["optional_modules"])
        entry=next(x for x in m["optional_module_admissions"] if x["module_id"]==SIHUA_MODULE)
        self.assertEqual(3,entry["admitted_claims_added"])
        self.assertEqual(
            ["ziwei_interpretation_claim_registry_sihua_v0.json"],
            entry["admitted_research_registries"],
        )
        self.assertTrue(entry["transformed_star_interpretation_admitted"])
        self.assertFalse(entry["generic_transform_outcome_doctrine_admitted"])
        self.assertFalse(entry["cross_profile_averaging_allowed"])

if __name__=="__main__":
    unittest.main()
