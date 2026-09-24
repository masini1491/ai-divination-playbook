from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools.astrology_interpretation_handoff import (
    InterpretationHandoffError,
    build_handoff,
)

ROOT = Path(__file__).resolve().parents[1]


def admitted_run(*, approximate: bool = False) -> dict:
    return {
        "schema_name": "astrology_reading_run",
        "schema_version": "1.0.0",
        "status": "admitted",
        "interpretation_allowed": True,
        "orchestrator": {
            "orchestrator_id": "astrology-production-orchestrator-v1",
            "orchestrator_version": "1.0.0",
            "authority": "composition_only",
        },
        "normalized_request": {
            "reading_mode": "natal",
            "subject_ref": "fixture-subject",
        },
        "fact_bundles": {
            "natal": {
                "schema_name": "astrology_fact_bundle",
                "schema_version": "1.0.0",
                "method": "Astrology",
                "reading_mode": "natal",
                "fact_source": "approved_provider",
                "calculation_verification": "verified_provider",
                "subject_ref": "fixture-subject",
                "birth_time_certainty": "approximate" if approximate else "exact",
                "provider": {
                    "provider_id": "astronomy-engine-natal-v1",
                    "provider_version": "1.0.0",
                },
                "facts": {
                    "objects": [],
                    "houses": [],
                    "aspects": [
                        {
                            "fact_id": "fact:aspect:moon:opposition:saturn",
                            "aspect": "opposition",
                            "orb_deg": 1.2,
                            "left_ref": "fact:object:moon",
                            "right_ref": "fact:object:saturn",
                            "scope": "natal",
                        }
                    ],
                    "events": [],
                },
            }
        },
        "runtime_gates": {
            "natal": {
                "interpretation_allowed": True,
                "errors": [],
            }
        },
    }


def valid_request() -> dict:
    fact_ref = {
        "bundle": "natal",
        "fact_id": "fact:aspect:moon:opposition:saturn",
    }
    return {
        "schema_name": "astrology_interpretation_request",
        "schema_version": "1.0.0",
        "question_id": "fixture-question",
        "question": "What symbolic theme is most relevant to this Moon-Saturn opposition?",
        "focus": ["Moon-Saturn opposition"],
        "exclusions": ["literal childhood biography", "clinical diagnosis"],
        "fact_refs": [dict(fact_ref)],
        "claim_requests": [
            {
                "registry_record_id": "saturn-moon-major-aspects-research-v1",
                "claim_id": "claim:greene-moon-saturn-parent-image",
                "fact_refs": [dict(fact_ref)],
            }
        ],
        "unsupported_factors": [],
    }


class AstrologyInterpretationHandoffTests(unittest.TestCase):
    def test_admitted_claim_and_fact_produce_bounded_handoff(self):
        result = build_handoff(admitted_run(), valid_request(), repo_root=ROOT)

        self.assertEqual("astrology_interpretation_handoff", result["schema_name"])
        self.assertEqual("1.0.0", result["schema_version"])
        self.assertEqual("ready_for_bounded_interpretation", result["status"])
        self.assertTrue(result["interpretation_allowed"])
        self.assertEqual("evidence_packaging_only", result["adapter"]["authority"])
        self.assertFalse(result["adapter"]["final_prose_authority"])
        self.assertEqual("ASTROLOGY.md", result["owners"]["method_owner"])
        self.assertEqual("CHATGPT_OUTPUT.md", result["owners"]["output_owner"])
        self.assertEqual(
            "fact:aspect:moon:opposition:saturn",
            result["selected_facts"][0]["fact"]["fact_id"],
        )
        claim = result["selected_claims"][0]
        self.assertEqual("claim:greene-moon-saturn-parent-image", claim["claim_id"])
        self.assertEqual("saturn-moon-major-aspects-research-v1", claim["registry_record_id"])
        self.assertTrue(claim["source_provenance"])
        self.assertTrue(claim["cautions"])
        self.assertTrue(result["conflicts"])
        self.assertTrue(result["required_disclosures"])

    def test_reference_only_source_is_rejected_even_in_admitted_registry(self):
        request = valid_request()
        request["claim_requests"][0]["claim_id"] = "claim:reference-square-friction"
        with self.assertRaisesRegex(InterpretationHandoffError, "forbidden by production source policy"):
            build_handoff(admitted_run(), request, repo_root=ROOT)

    def test_unadmitted_registry_is_rejected(self):
        request = valid_request()
        request["claim_requests"][0]["registry_record_id"] = "not-admitted-registry"
        with self.assertRaisesRegex(InterpretationHandoffError, "not production-admitted"):
            build_handoff(admitted_run(), request, repo_root=ROOT)

    def test_unknown_fact_ref_is_rejected(self):
        request = valid_request()
        request["fact_refs"][0]["fact_id"] = "fact:missing"
        request["claim_requests"][0]["fact_refs"][0]["fact_id"] = "fact:missing"
        with self.assertRaisesRegex(InterpretationHandoffError, "does not exist"):
            build_handoff(admitted_run(), request, repo_root=ROOT)

    def test_claim_link_must_be_part_of_selected_fact_refs(self):
        request = valid_request()
        request["claim_requests"][0]["fact_refs"][0]["fact_id"] = "fact:not-selected"
        with self.assertRaisesRegex(InterpretationHandoffError, "already selected"):
            build_handoff(admitted_run(), request, repo_root=ROOT)

    def test_rejected_reading_run_cannot_enter_handoff(self):
        run = admitted_run()
        run["status"] = "rejected"
        run["interpretation_allowed"] = False
        with self.assertRaisesRegex(InterpretationHandoffError, "not admitted"):
            build_handoff(run, valid_request(), repo_root=ROOT)

    def test_approximate_birth_time_adds_disclosure(self):
        result = build_handoff(admitted_run(approximate=True), valid_request(), repo_root=ROOT)
        self.assertTrue(any("approximate" in item for item in result["required_disclosures"]))

    def test_cli_emits_handoff(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            run_path = Path(temp_dir) / "run.json"
            request_path = Path(temp_dir) / "request.json"
            run_path.write_text(json.dumps(admitted_run()), encoding="utf-8")
            request_path.write_text(json.dumps(valid_request()), encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "tools.astrology_interpretation_handoff",
                    str(run_path),
                    str(request_path),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(0, completed.returncode, completed.stderr or completed.stdout)
        result = json.loads(completed.stdout)
        self.assertEqual("ready_for_bounded_interpretation", result["status"])


    def test_exact_reference_pipeline_rejects_e1_fact_only_claim_binding(self):
        run = admitted_run()
        run["fact_bundles"]["natal"]["facts"]["objects"].append(
            {
                "fact_id": "fact:angle:descendant",
                "object_type": "angle",
                "object_id": "Descendant",
                "longitude_deg": 180.0,
                "derived_from": "fact:angle:ascendant",
                "derivation_policy": "antipode-v1",
            }
        )
        request = valid_request()
        descendant_ref = {"bundle": "natal", "fact_id": "fact:angle:descendant"}
        request["fact_refs"] = [descendant_ref]
        request["claim_requests"][0]["fact_refs"] = [descendant_ref]
        with self.assertRaisesRegex(
            InterpretationHandoffError,
            "claim binding is not admitted for fact-only object: Descendant",
        ):
            build_handoff(run, request, repo_root=ROOT)

    def test_exact_reference_pipeline_rejects_e4_fact_only_claim_binding(self):
        run = admitted_run()
        run["fact_bundles"]["natal"]["facts"]["objects"].append(
            {
                "fact_id": "fact:object:partoffortune",
                "object_type": "point",
                "object_id": "PartOfFortune",
                "longitude_deg": 123.0,
                "derivation_policy": "fortune-day-night-v1",
                "sect_policy_id": "sect-geometric-solar-altitude-v1",
            }
        )
        request = valid_request()
        fortune_ref = {"bundle": "natal", "fact_id": "fact:object:partoffortune"}
        request["fact_refs"] = [fortune_ref]
        request["claim_requests"][0]["fact_refs"] = [fortune_ref]
        with self.assertRaisesRegex(
            InterpretationHandoffError,
            "claim binding is not admitted for fact-only object: PartOfFortune",
        ):
            build_handoff(run, request, repo_root=ROOT)

    def test_fact_only_object_can_be_selected_without_claim_binding(self):
        run = admitted_run()
        run["fact_bundles"]["natal"]["facts"]["objects"].append(
            {
                "fact_id": "fact:object:southnode",
                "object_type": "point",
                "object_id": "SouthNode",
                "longitude_deg": 42.0,
                "node_definition": "mean",
                "derived_from": "fact:object:northnode",
                "derivation_policy": "antipode-v1",
            }
        )
        request = valid_request()
        request["fact_refs"] = [{"bundle": "natal", "fact_id": "fact:object:southnode"}]
        request["claim_requests"] = []
        result = build_handoff(run, request, repo_root=ROOT)
        self.assertEqual("ready_for_bounded_interpretation", result["status"])
        self.assertEqual([], result["selected_claims"])
        self.assertEqual("SouthNode", result["selected_facts"][0]["fact"]["object_id"])


if __name__ == "__main__":
    unittest.main()
