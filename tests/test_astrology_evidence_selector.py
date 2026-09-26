from __future__ import annotations

import json
import unittest
from pathlib import Path

from tools.astrology_evidence_selector import (
    AstrologyEvidenceSelectionError,
    select_evidence,
    selection_to_interpretation_request,
)
from tools.astrology_interpretation_handoff import build_handoff
from tools.astrology_orchestrator import run_request

ROOT = Path(__file__).resolve().parents[1]
NATAL_READING = ROOT / "tests" / "fixtures" / "astrology_pipeline_reading_request_natal_v1.json"
TRANSIT_READING = ROOT / "tests" / "fixtures" / "astrology_reading_request_transit_v1.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def natal_typed_request() -> dict:
    return {
        "schema_name": "astrology_typed_evidence_selection_request",
        "schema_version": "1.0.0",
        "question_id": "typed-natal-seventh",
        "question": "What symbolic relationship theme is supported by the admitted seventh-house evidence?",
        "focus": ["seventh house"],
        "exclusions": ["specific partner motives", "guaranteed relationship outcomes"],
        "fact_selectors": [
            {
                "selector_id": "fact-house-7",
                "selector_kind": "house",
                "bundle": "natal",
                "cardinality": "exactly_one",
                "house_number": 7,
            }
        ],
        "claim_selectors": [
            {
                "selector_id": "claim-seventh-marriage",
                "registry_record_id": "first-seventh-house-axis-research-v1",
                "claim_type": "historical_doctrine",
                "applies_to_all": ["natal", "seventh house", "marriage"],
                "tradition_context_refs_any": ["lineage:hellenistic"],
                "fact_selector_ids": ["fact-house-7"],
            }
        ],
        "unsupported_factors": [
            {
                "factor": "specific partner motives",
                "reason": "House symbolism does not establish another person's private motives.",
            }
        ],
    }


def north_node_typed_request() -> dict:
    return {
        "schema_name": "astrology_typed_evidence_selection_request",
        "schema_version": "1.0.0",
        "question_id": "typed-north-node-sign",
        "question": "What bounded symbolic North Node sign interpretation is admitted?",
        "fact_selectors": [{
            "selector_id": "node", "selector_kind": "object", "bundle": "natal",
            "cardinality": "exactly_one", "object_id": "NorthNode", "object_type": "point",
        }],
        "claim_selectors": [
            {
                "selector_id": "node-function",
                "registry_record_id": "north-node-sign-semantics-research-v1",
                "semantic_profile": "composable-symbolic-modern-v1",
                "claim_type": "north_node_function",
                "applicability_scope": "north_node_core",
                "applies_to_all": ["natal"],
                "fact_selector_ids": ["node"],
            },
            {
                "selector_id": "node-sign-style",
                "registry_record_id": "planet-sign-composable-semantics-research-v1",
                "semantic_profile": "composable-symbolic-modern-v1",
                "claim_type": "sign_style",
                "applicability_scope": "north_node_sign_style",
                "applies_to_all": ["natal"],
                "fact_selector_ids": ["node"],
            },
        ],
        "unsupported_factors": [],
    }


class AstrologyEvidenceSelectorTests(unittest.TestCase):
    def test_natal_typed_selection_materializes_existing_handoff_request(self):
        run = run_request(load(NATAL_READING))
        selection = select_evidence(run, natal_typed_request(), repo_root=ROOT)

        self.assertEqual("selected", selection["status"])
        self.assertTrue(selection["selection_allowed"])
        self.assertEqual(
            "deterministic_evidence_selection_only",
            selection["selector"]["authority"],
        )
        self.assertFalse(selection["selector"]["natural_language_understanding_authority"])
        self.assertFalse(selection["selector"]["semantic_meaning_authority"])
        self.assertEqual(
            [{"bundle": "natal", "fact_id": "fact:house:7"}],
            selection["fact_refs"],
        )
        self.assertEqual(
            "claim:valens-seventh-place-marriage",
            selection["claim_requests"][0]["claim_id"],
        )

        handoff = build_handoff(
            run,
            selection_to_interpretation_request(selection),
            repo_root=ROOT,
        )
        self.assertEqual("ready_for_bounded_interpretation", handoff["status"])
        self.assertEqual("fact:house:7", handoff["selected_facts"][0]["fact"]["fact_id"])

    def test_transit_typed_selection_uses_runtime_event_fields_not_fact_id(self):
        run = run_request(load(TRANSIT_READING))
        event = next(
            row
            for row in run["fact_bundles"]["transit"]["facts"]["events"]
            if row.get("event_kind") == "transit_to_natal"
        )
        typed = {
            "schema_name": "astrology_typed_evidence_selection_request",
            "schema_version": "1.0.0",
            "question_id": "typed-transit-boundary",
            "question": "What deterministic transit fact is present and what production boundary applies?",
            "fact_selectors": [
                {
                    "selector_id": "transit-contact",
                    "selector_kind": "event",
                    "bundle": "transit",
                    "cardinality": "exactly_one",
                    "event_kind": "transit_to_natal",
                    "moving_body": event["moving_body"],
                    "natal_target": event["natal_target"],
                    "aspect": event["aspect"],
                    "passage_index": event["passage_index"],
                }
            ],
            "claim_selectors": [
                {
                    "selector_id": "transit-policy",
                    "registry_record_id": "transit-interpretation-research-v1",
                    "claim_type": "transit_policy",
                    "applies_to_all": ["transit", "exact passage"],
                    "fact_selector_ids": ["transit-contact"],
                }
            ],
            "unsupported_factors": [],
        }

        selection = select_evidence(run, typed, repo_root=ROOT)
        self.assertEqual(event["fact_id"], selection["fact_refs"][0]["fact_id"])
        self.assertEqual(
            "claim:project-transit-facts-before-interpretation",
            selection["claim_requests"][0]["claim_id"],
        )

    def test_object_core_claim_binds_planet_identity_from_matched_fact(self):
        run = run_request(load(NATAL_READING))
        typed = {
            "schema_name": "astrology_typed_evidence_selection_request",
            "schema_version": "1.0.0",
            "question_id": "typed-sun-core",
            "question": "What bounded symbolic function is admitted for the Sun?",
            "fact_selectors": [
                {
                    "selector_id": "sun",
                    "selector_kind": "object",
                    "bundle": "natal",
                    "cardinality": "exactly_one",
                    "object_id": "Sun",
                    "object_type": "planet",
                }
            ],
            "claim_selectors": [
                {
                    "selector_id": "sun-core",
                    "registry_record_id": "planet-sign-composable-semantics-research-v1",
                    "semantic_profile": "composable-symbolic-modern-v1",
                    "claim_type": "planet_function",
                    "applicability_scope": "object_core",
                    "applies_to_all": ["natal"],
                    "fact_selector_ids": ["sun"],
                }
            ],
        }
        selection = select_evidence(run, typed, repo_root=ROOT)
        self.assertEqual("claim:planet-function:sun", selection["claim_requests"][0]["claim_id"])
        handoff = build_handoff(run, selection_to_interpretation_request(selection), repo_root=ROOT)
        self.assertEqual("ready_for_bounded_interpretation", handoff["status"])

    def test_sign_style_claim_binds_actual_sign_without_caller_copying_it(self):
        run = run_request(load(NATAL_READING))
        sun = next(row for row in run["fact_bundles"]["natal"]["facts"]["objects"] if row.get("object_id") == "Sun")
        typed = {
            "schema_name": "astrology_typed_evidence_selection_request",
            "schema_version": "1.0.0",
            "question_id": "typed-sun-sign",
            "question": "What bounded sign style is admitted for the Sun's actual sign?",
            "fact_selectors": [
                {
                    "selector_id": "sun",
                    "selector_kind": "object",
                    "bundle": "natal",
                    "cardinality": "exactly_one",
                    "object_id": "Sun",
                    "object_type": "planet",
                }
            ],
            "claim_selectors": [
                {
                    "selector_id": "sun-sign-style",
                    "registry_record_id": "planet-sign-composable-semantics-research-v1",
                    "semantic_profile": "composable-symbolic-modern-v1",
                    "claim_type": "sign_style",
                    "applicability_scope": "sign_style",
                    "applies_to_all": ["natal"],
                    "fact_selector_ids": ["sun"],
                }
            ],
        }
        selection = select_evidence(run, typed, repo_root=ROOT)
        expected = "claim:sign-style:" + sun["sign"].lower()
        self.assertEqual(expected, selection["claim_requests"][0]["claim_id"])

    def test_sign_style_cannot_be_redirected_to_wrong_sign_by_caller(self):
        run = run_request(load(NATAL_READING))
        sun = next(row for row in run["fact_bundles"]["natal"]["facts"]["objects"] if row.get("object_id") == "Sun")
        wrong = next(sign for sign in ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"] if sign != sun["sign"])
        typed = {
            "schema_name": "astrology_typed_evidence_selection_request",
            "schema_version": "1.0.0",
            "question_id": "typed-wrong-sign",
            "question": "Try to bind the Sun to a wrong sign meaning.",
            "fact_selectors": [
                {
                    "selector_id": "sun",
                    "selector_kind": "object",
                    "bundle": "natal",
                    "cardinality": "exactly_one",
                    "object_id": "Sun",
                    "object_type": "planet",
                }
            ],
            "claim_selectors": [
                {
                    "selector_id": "wrong-sign",
                    "registry_record_id": "planet-sign-composable-semantics-research-v1",
                    "semantic_profile": "composable-symbolic-modern-v1",
                    "claim_type": "sign_style",
                    "applicability_scope": "sign_style",
                    "applies_to_all": ["natal", wrong],
                    "fact_selector_ids": ["sun"],
                }
            ],
        }
        with self.assertRaisesRegex(AstrologyEvidenceSelectionError, "matched no admitted claims"):
            select_evidence(run, typed, repo_root=ROOT)

    def test_north_node_does_not_inherit_planet_sign_semantics(self):
        run = run_request(load(NATAL_READING))
        typed = {
            "schema_name": "astrology_typed_evidence_selection_request",
            "schema_version": "1.0.0",
            "question_id": "typed-node-sign",
            "question": "Do not silently treat the North Node as a planet semantic claim.",
            "fact_selectors": [
                {
                    "selector_id": "node",
                    "selector_kind": "object",
                    "bundle": "natal",
                    "cardinality": "exactly_one",
                    "object_id": "NorthNode",
                    "object_type": "point",
                }
            ],
            "claim_selectors": [
                {
                    "selector_id": "node-sign",
                    "registry_record_id": "planet-sign-composable-semantics-research-v1",
                    "semantic_profile": "composable-symbolic-modern-v1",
                    "claim_type": "sign_style",
                    "applicability_scope": "sign_style",
                    "applies_to_all": ["natal"],
                    "fact_selector_ids": ["node"],
                }
            ],
        }
        with self.assertRaisesRegex(AstrologyEvidenceSelectionError, "requires planet object facts"):
            select_evidence(run, typed, repo_root=ROOT)

    def test_unknown_time_taiwan_sun_pisces_semantics_reaches_handoff(self):
        reading = {
            "schema_name": "astrology_reading_request",
            "schema_version": "1.0.0",
            "reading_mode": "natal",
            "subject_ref": "fixture-date-only-taiwan-semantics",
            "birth": {
                "local_date": "2006-03-14",
                "birth_time_certainty": "unknown",
                "house_system": None,
                "location": {"country": {"name": "Taiwan", "country_code": "TW"}},
            },
        }
        run = run_request(reading)
        sun = next(row for row in run["fact_bundles"]["natal"]["facts"]["objects"] if row.get("object_id") == "Sun")
        self.assertEqual("Pisces", sun["sign"])

        typed = {
            "schema_name": "astrology_typed_evidence_selection_request",
            "schema_version": "1.0.0",
            "question_id": "typed-date-only-sun-pisces",
            "question": "What bounded symbolic interpretation is supported for the admitted Sun-in-Pisces fact?",
            "fact_selectors": [
                {
                    "selector_id": "sun",
                    "selector_kind": "object",
                    "bundle": "natal",
                    "cardinality": "exactly_one",
                    "object_id": "Sun",
                    "object_type": "planet",
                }
            ],
            "claim_selectors": [
                {
                    "selector_id": "sun-core",
                    "registry_record_id": "planet-sign-composable-semantics-research-v1",
                    "semantic_profile": "composable-symbolic-modern-v1",
                    "claim_type": "planet_function",
                    "applicability_scope": "object_core",
                    "applies_to_all": ["natal"],
                    "fact_selector_ids": ["sun"],
                },
                {
                    "selector_id": "sun-sign",
                    "registry_record_id": "planet-sign-composable-semantics-research-v1",
                    "semantic_profile": "composable-symbolic-modern-v1",
                    "claim_type": "sign_style",
                    "applicability_scope": "sign_style",
                    "applies_to_all": ["natal"],
                    "fact_selector_ids": ["sun"],
                },
            ],
            "unsupported_factors": [],
        }
        selection = select_evidence(run, typed, repo_root=ROOT)
        claim_ids = {row["claim_id"] for row in selection["claim_requests"]}
        self.assertEqual({"claim:planet-function:sun", "claim:sign-style:pisces"}, claim_ids)

        handoff = build_handoff(run, selection_to_interpretation_request(selection), repo_root=ROOT)
        self.assertEqual("ready_for_bounded_interpretation", handoff["status"])
        self.assertEqual(2, len(handoff["selected_claims"]))
        for claim in handoff["selected_claims"]:
            self.assertEqual(["context:modern_contemporary"], claim["historical_context_refs"])

    def test_planet_sign_registry_requires_explicit_semantic_profile(self):
        run = run_request(load(NATAL_READING))
        typed = {
            "schema_name": "astrology_typed_evidence_selection_request",
            "schema_version": "1.0.0",
            "question_id": "typed-missing-semantic-profile",
            "question": "Do not silently choose a planet-sign interpretation framework.",
            "fact_selectors": [
                {
                    "selector_id": "sun",
                    "selector_kind": "object",
                    "bundle": "natal",
                    "cardinality": "exactly_one",
                    "object_id": "Sun",
                    "object_type": "planet",
                }
            ],
            "claim_selectors": [
                {
                    "selector_id": "sun-core",
                    "registry_record_id": "planet-sign-composable-semantics-research-v1",
                    "claim_type": "planet_function",
                    "applicability_scope": "object_core",
                    "applies_to_all": ["natal"],
                    "fact_selector_ids": ["sun"],
                }
            ],
        }
        with self.assertRaisesRegex(AstrologyEvidenceSelectionError, "requires semantic_profile=composable-symbolic-modern-v1"):
            select_evidence(run, typed, repo_root=ROOT)

    def test_ambiguous_claim_selector_fails_closed(self):
        run = run_request(load(NATAL_READING))
        typed = natal_typed_request()
        selector = typed["claim_selectors"][0]
        selector.pop("registry_record_id")
        selector.pop("tradition_context_refs_any")
        selector["applies_to_all"] = ["natal", "seventh house", "marriage"]

        with self.assertRaisesRegex(AstrologyEvidenceSelectionError, "ambiguous"):
            select_evidence(run, typed, repo_root=ROOT)

    def test_fact_claim_applicability_mismatch_fails_closed(self):
        run = run_request(load(NATAL_READING))
        typed = natal_typed_request()
        typed["fact_selectors"][0]["house_number"] = 12

        with self.assertRaisesRegex(
            AstrologyEvidenceSelectionError,
            "matched no admitted claims after fact-applicability binding",
        ):
            select_evidence(run, typed, repo_root=ROOT)

    def test_unknown_fact_selector_reference_is_rejected(self):
        run = run_request(load(NATAL_READING))
        typed = natal_typed_request()
        typed["claim_selectors"][0]["fact_selector_ids"] = ["missing-selector"]

        with self.assertRaisesRegex(AstrologyEvidenceSelectionError, "unknown selector"):
            select_evidence(run, typed, repo_root=ROOT)

    def test_reference_only_claim_cannot_bypass_typed_applicability(self):
        run = run_request(load(TRANSIT_READING))
        event = next(
            row
            for row in run["fact_bundles"]["transit"]["facts"]["events"]
            if row.get("event_kind") == "transit_to_natal"
        )
        typed = {
            "schema_name": "astrology_typed_evidence_selection_request",
            "schema_version": "1.0.0",
            "question_id": "typed-reference-only-block",
            "question": "Use the reference-only transit meaning.",
            "fact_selectors": [
                {
                    "selector_id": "transit-contact",
                    "selector_kind": "event",
                    "bundle": "transit",
                    "cardinality": "exactly_one",
                    "event_kind": "transit_to_natal",
                    "moving_body": event["moving_body"],
                    "natal_target": event["natal_target"],
                    "aspect": event["aspect"],
                    "passage_index": event["passage_index"],
                }
            ],
            "claim_selectors": [
                {
                    "selector_id": "reference-only-meaning",
                    "registry_record_id": "transit-interpretation-research-v1",
                    "claim_type": "transit_meaning",
                    "applies_to_all": ["transit", "natal promise", "activation"],
                    "fact_selector_ids": ["transit-contact"],
                }
            ],
        }

        with self.assertRaisesRegex(
            AstrologyEvidenceSelectionError,
            "matched no admitted claims after fact-applicability binding",
        ):
            select_evidence(run, typed, repo_root=ROOT)

    def test_unadmitted_registry_is_rejected(self):
        run = run_request(load(NATAL_READING))
        typed = natal_typed_request()
        typed["claim_selectors"][0]["registry_record_id"] = "high-value-planet-aspects-research-v1"

        with self.assertRaisesRegex(AstrologyEvidenceSelectionError, "unadmitted registry"):
            select_evidence(run, typed, repo_root=ROOT)


    def test_e1_descendant_fact_is_selectable_without_interpretation_claim(self):
        run = run_request(load(NATAL_READING))
        typed = {
            "schema_name": "astrology_typed_evidence_selection_request",
            "schema_version": "1.0.0",
            "question_id": "typed-e1-descendant-fact",
            "question": "Select the deterministic Descendant fact only.",
            "fact_selectors": [
                {
                    "selector_id": "desc",
                    "selector_kind": "object",
                    "bundle": "natal",
                    "cardinality": "exactly_one",
                    "object_id": "Descendant",
                    "object_type": "angle",
                }
            ],
            "claim_selectors": [],
        }
        selection = select_evidence(run, typed, repo_root=ROOT)
        self.assertEqual(
            [{"bundle": "natal", "fact_id": "fact:angle:descendant"}],
            selection["fact_refs"],
        )
        self.assertEqual([], selection["claim_requests"])

    def test_e1_descendant_allows_only_source_backed_admitted_claim_binding(self):
        run = run_request(load(NATAL_READING))
        typed = {
            "schema_name": "astrology_typed_evidence_selection_request",
            "schema_version": "1.0.0",
            "question_id": "typed-e1-descendant-claim-admission",
            "question": "Select the admitted historical Descendant marriage claim.",
            "fact_selectors": [
                {
                    "selector_id": "desc",
                    "selector_kind": "object",
                    "bundle": "natal",
                    "cardinality": "exactly_one",
                    "object_id": "Descendant",
                    "object_type": "angle",
                }
            ],
            "claim_selectors": [
                {
                    "selector_id": "seventh",
                    "registry_record_id": "first-seventh-house-axis-research-v1",
                    "claim_type": "historical_doctrine",
                    "applies_to_all": ["natal", "seventh house", "marriage"],
                    "tradition_context_refs_any": ["lineage:hellenistic"],
                    "fact_selector_ids": ["desc"],
                }
            ],
        }
        selection = select_evidence(run, typed, repo_root=ROOT)
        self.assertEqual(
            "claim:valens-seventh-place-marriage",
            selection["claim_requests"][0]["claim_id"],
        )

    def test_e1_imumcoeli_allows_source_backed_admitted_claim_binding(self):
        run = run_request(load(NATAL_READING))
        typed = {
            "schema_name": "astrology_typed_evidence_selection_request",
            "schema_version": "1.0.0",
            "question_id": "typed-e1-ic-claim-admission",
            "question": "Select the admitted Hellenistic fourth-place claim for IC.",
            "fact_selectors": [
                {
                    "selector_id": "ic",
                    "selector_kind": "object",
                    "bundle": "natal",
                    "cardinality": "exactly_one",
                    "object_id": "ImumCoeli",
                    "object_type": "angle",
                }
            ],
            "claim_selectors": [
                {
                    "selector_id": "fourth",
                    "registry_record_id": "fourth-tenth-house-axis-research-v1",
                    "claim_type": "historical_doctrine",
                    "applies_to_all": ["natal", "fourth house", "home", "possessions", "activity"],
                    "tradition_context_refs_any": ["lineage:hellenistic"],
                    "fact_selector_ids": ["ic"],
                }
            ],
        }
        selection = select_evidence(run, typed, repo_root=ROOT)
        self.assertEqual(
            "claim:valens-fourth-place-home-possessions-activity",
            selection["claim_requests"][0]["claim_id"],
        )


    def test_e4_fortune_fact_is_selectable_without_interpretation_claim(self):
        run = run_request(load(NATAL_READING))
        typed = {
            "schema_name": "astrology_typed_evidence_selection_request",
            "schema_version": "1.0.0",
            "question_id": "typed-e4-fortune-fact",
            "question": "Select the deterministic Part of Fortune fact only.",
            "fact_selectors": [
                {
                    "selector_id": "fortune",
                    "selector_kind": "object",
                    "bundle": "natal",
                    "cardinality": "exactly_one",
                    "object_id": "PartOfFortune",
                    "object_type": "point",
                }
            ],
            "claim_selectors": [],
        }
        selection = select_evidence(run, typed, repo_root=ROOT)
        self.assertEqual(
            [{"bundle": "natal", "fact_id": "fact:object:partoffortune"}],
            selection["fact_refs"],
        )
        self.assertEqual([], selection["claim_requests"])

    def test_e4_fortune_rejects_unadmitted_interpretation_claims(self):
        run = run_request(load(NATAL_READING))
        typed = {
            "schema_name": "astrology_typed_evidence_selection_request",
            "schema_version": "1.0.0",
            "question_id": "typed-e4-fortune-claim-boundary",
            "question": "Do not infer interpretation admission from Fortune fact admission.",
            "fact_selectors": [
                {
                    "selector_id": "fortune",
                    "selector_kind": "object",
                    "bundle": "natal",
                    "cardinality": "exactly_one",
                    "object_id": "PartOfFortune",
                    "object_type": "point",
                }
            ],
            "claim_selectors": [
                {
                    "selector_id": "probe",
                    "registry_record_id": "planet-sign-composable-semantics-research-v1",
                    "semantic_profile": "composable-symbolic-modern-v1",
                    "claim_type": "planet_function",
                    "applicability_scope": "object_core",
                    "applies_to_all": ["natal"],
                    "fact_selector_ids": ["fortune"],
                }
            ],
        }
        with self.assertRaisesRegex(
            AstrologyEvidenceSelectionError,
            "matched no admitted claims after fact-applicability binding",
        ):
            select_evidence(run, typed, repo_root=ROOT)



    def test_north_node_sign_semantics_use_separate_claim_family_and_actual_sign(self):
        run = run_request(load(NATAL_READING))
        node = next(row for row in run["fact_bundles"]["natal"]["facts"]["objects"] if row.get("object_id") == "NorthNode")
        selection = select_evidence(run, north_node_typed_request(), repo_root=ROOT)
        self.assertEqual(
            {"claim:north-node-function:growth-edge", "claim:sign-style:" + node["sign"].lower()},
            {row["claim_id"] for row in selection["claim_requests"]},
        )
        handoff = build_handoff(run, selection_to_interpretation_request(selection), repo_root=ROOT)
        self.assertEqual("ready_for_bounded_interpretation", handoff["status"])
        self.assertEqual({"north_node_function", "sign_style"}, {row["claim_type"] for row in handoff["selected_claims"]})

    def test_north_node_sign_semantics_cannot_be_redirected_to_wrong_sign(self):
        run = run_request(load(NATAL_READING))
        node = next(row for row in run["fact_bundles"]["natal"]["facts"]["objects"] if row.get("object_id") == "NorthNode")
        wrong = next(sign for sign in ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"] if sign != node["sign"])
        typed = north_node_typed_request()
        typed["claim_selectors"][1]["applies_to_all"] = ["natal", wrong]
        with self.assertRaisesRegex(AstrologyEvidenceSelectionError, "matched no admitted claims"):
            select_evidence(run, typed, repo_root=ROOT)

    def test_north_node_semantics_fail_closed_when_provider_mean_provenance_is_missing(self):
        run = run_request(load(NATAL_READING))
        run["fact_bundles"]["natal"]["provider"]["provider_version"] = "unadmitted-version"
        with self.assertRaisesRegex(AstrologyEvidenceSelectionError, "requires mean NorthNode provenance"):
            select_evidence(run, north_node_typed_request(), repo_root=ROOT)

    def test_north_node_semantics_reject_explicit_non_mean_definition(self):
        run = run_request(load(NATAL_READING))
        node = next(row for row in run["fact_bundles"]["natal"]["facts"]["objects"] if row.get("object_id") == "NorthNode")
        node["node_definition"] = "true"
        with self.assertRaisesRegex(AstrologyEvidenceSelectionError, "requires mean NorthNode provenance"):
            select_evidence(run, north_node_typed_request(), repo_root=ROOT)

    def test_north_node_function_registry_requires_dedicated_core_scope(self):
        run = run_request(load(NATAL_READING))
        typed = north_node_typed_request()
        typed["claim_selectors"][0]["applicability_scope"] = "object_core"
        with self.assertRaisesRegex(AstrologyEvidenceSelectionError, "requires applicability_scope=north_node_core"):
            select_evidence(run, typed, repo_root=ROOT)

if __name__ == "__main__":
    unittest.main()
