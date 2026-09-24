#!/usr/bin/env python3
"""Production binding for Zi Wei Scope-A bounded natal first layer."""
from __future__ import annotations
from pathlib import Path
from typing import Any

from tools.ziwei_natal_provider import NormalizedNatalInput, calculate_scope_a_natal
from tools import ziwei_claim_retrieval as _retrieval
from tools import ziwei_delivery as _delivery

ROOT=Path(__file__).resolve().parents[1]
REF=ROOT/"references"/"ziwei"

PIPELINE_ID="ziwei-scope-a-production-pipeline-v1"
PIPELINE_VERSION="1.1.0"
INTERPRETATION_PROFILE="ziwei.interpretation.tw_v1"
TEMPORAL_SCOPE="natal_baseline"
ADMITTED_REGISTRIES=(
    "ziwei_interpretation_claim_registry_batch1.json",
    "ziwei_interpretation_claim_registry_batch2.json",
    "ziwei_interpretation_claim_registry_palaces_v0.json",
)

def _production_registries():
    regs=_retrieval.load_registries(REF/x for x in ADMITTED_REGISTRIES)
    for name,reg in zip(ADMITTED_REGISTRIES,regs):
        if reg.get("production_routable") is not False:
            raise ValueError(f"REGISTRY_HISTORY_MUTATED:{name}")
        if reg.get("interpretation_profile") != INTERPRETATION_PROFILE:
            raise ValueError(f"REGISTRY_PROFILE_MISMATCH:{name}")
    return regs

def _compose_scope_a_chart(
    chart:dict[str,Any], *,
    request_id:str,
    requested_subjects:tuple[str,...]=(),
    enabled_source_ids:tuple[str,...]=(),
) -> dict[str,Any]:
    if not request_id.strip():
        raise ValueError("request_id is required")
    packet=_retrieval.FactPacket(
        packet_id=f"{request_id}:facts",
        interpretation_profile=INTERPRETATION_PROFILE,
        temporal_scope=TEMPORAL_SCOPE,
        facts=frozenset(chart["retrieval_facts"]),
        requested_subjects=frozenset(requested_subjects),
        enabled_source_ids=frozenset(enabled_source_ids),
    )
    retrieval=_retrieval.retrieve_claims(packet,_production_registries())
    frame=_retrieval.compose_frame(packet,retrieval)
    conflicts=frame["conflicts"]
    evidence_states={"source_backed","project_adopted"}
    if conflicts:
        evidence_states.add("conflicted")
    actions=_delivery.delivery_actions(evidence_states=evidence_states)
    return {
        "pipeline_id":PIPELINE_ID,
        "pipeline_version":PIPELINE_VERSION,
        "status":"PRODUCTION_ADMITTED",
        "scope":"bounded_natal_first_layer",
        "request_id":request_id,
        "calculation":{
            "provider":chart["provider"],
            "calculation_profile":chart["calculation_profile"],
            "input_provenance":chart["input_provenance"],
            "normalized_input":chart["normalized_input"],
            "year_pillar":chart["year_pillar"],
            "life_palace":chart["life_palace"],
            "body_palace":chart["body_palace"],
            "five_element_bureau":chart["five_element_bureau"],
            "ziwei_branch":chart["ziwei_branch"],
            "major_star_placements":chart["major_star_placements"],
            "palaces":chart["palaces"],
            "topology":chart["topology"],
            "unsupported":chart["unsupported"],
        },
        "interpretation":{
            "profile":INTERPRETATION_PROFILE,
            "temporal_scope":TEMPORAL_SCOPE,
            "selected_claims":retrieval["selected_claims"],
            "selected_claim_ids":frame["selected_claim_ids"],
            "conditional_evaluations":retrieval["conditional_evaluations"],
            "subject_claims":frame["subject_claims"],
            "conflicts":conflicts,
            "omissions":retrieval["omissions"],
        },
        "delivery":{
            "evidence_states":sorted(evidence_states),
            "actions":actions,
            "rendering_boundary":"admitted_claims_only_no_new_doctrine",
            "high_impact_requires_bounded_delivery":True,
        },
        "authority":{
            "production_authority_granted":True,
            "ordinary_auto_routing":False,
            "final_prose_authority":False,
            "scientific_predictive_validity_claimed":False,
        },
    }


def run_scope_a_natal(
    data:NormalizedNatalInput, *,
    request_id:str,
    requested_subjects:tuple[str,...]=(),
    enabled_source_ids:tuple[str,...]=(),
) -> dict[str,Any]:
    chart=calculate_scope_a_natal(data)
    return _compose_scope_a_chart(
        chart,
        request_id=request_id,
        requested_subjects=requested_subjects,
        enabled_source_ids=enabled_source_ids,
    )
