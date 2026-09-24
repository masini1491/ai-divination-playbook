#!/usr/bin/env python3
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parent
DEFAULT_REGISTRIES = (
    ROOT / "ziwei_interpretation_claim_registry_batch1.json",
    ROOT / "ziwei_interpretation_claim_registry_batch2.json",
    ROOT / "ziwei_interpretation_claim_registry_palaces_v0.json",
)
SUPPORTED_TEMPORAL_SCOPE = "natal_baseline"
ELIGIBLE_ADOPTION = "RESEARCH_CLAIM_ELIGIBLE"
CONDITIONAL_CLAIM_TYPES = {"star_conditional", "palace_conditional"}
ACTIVE_CONDITIONAL_STATES = {"not_required", "satisfied"}

SPECIFICITY = {
    "star_conditional": 40,
    "palace_conditional": 35,
    "star_core": 20,
    "palace_domain": 10,
    "methodology": 5,
}

@dataclass(frozen=True)
class FactPacket:
    packet_id: str
    interpretation_profile: str
    temporal_scope: str
    facts: frozenset[str]
    requested_subjects: frozenset[str] = frozenset()
    enabled_source_ids: frozenset[str] = frozenset()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FactPacket":
        return cls(
            packet_id=str(data["packet_id"]),
            interpretation_profile=str(data["interpretation_profile"]),
            temporal_scope=str(data["temporal_scope"]),
            facts=frozenset(str(x) for x in data.get("facts", [])),
            requested_subjects=frozenset(str(x) for x in data.get("requested_subjects", [])),
            enabled_source_ids=frozenset(str(x) for x in data.get("enabled_source_ids", [])),
        )

def load_registries(paths: Iterable[Path] = DEFAULT_REGISTRIES) -> list[dict[str, Any]]:
    return [json.loads(Path(path).read_text(encoding="utf-8")) for path in paths]

def _evaluate_conditional_activation(packet: FactPacket, claim: dict[str, Any]) -> dict[str, Any] | None:
    if claim.get("claim_type") not in CONDITIONAL_CLAIM_TYPES:
        return None
    meta = claim.get("applicability", {}).get("conditional_activation")
    if not isinstance(meta, dict):
        return {
            "mode": "missing",
            "state": "not_computed",
            "reason": "conditional_activation_metadata_missing",
            "availability_requires": [],
            "missing_availability": [],
            "satisfies_all": [],
            "satisfies_any": [],
            "forbids": [],
            "matched_satisfies_all": [],
            "matched_satisfies_any": [],
            "matched_forbids": [],
        }
    mode = str(meta.get("mode", ""))
    availability = tuple(str(x) for x in meta.get("availability_requires", []))
    satisfies_all = tuple(str(x) for x in meta.get("satisfies_all", []))
    satisfies_any = tuple(str(x) for x in meta.get("satisfies_any", []))
    forbids = tuple(str(x) for x in meta.get("forbids", []))
    if mode == "context_only":
        state, reason = "not_required", "context_only_rule"
    elif mode == "fact_gated":
        missing_availability = sorted(set(availability) - packet.facts)
        if missing_availability:
            state, reason = "not_computed", "conditional_fact_not_computed"
        elif set(forbids).intersection(packet.facts):
            state, reason = "unsatisfied", "conditional_condition_unsatisfied"
        elif not set(satisfies_all).issubset(packet.facts):
            state, reason = "unsatisfied", "conditional_condition_unsatisfied"
        elif satisfies_any and not set(satisfies_any).intersection(packet.facts):
            state, reason = "unsatisfied", "conditional_condition_unsatisfied"
        else:
            state, reason = "satisfied", "conditional_condition_satisfied"
    else:
        state, reason = "not_computed", "conditional_activation_mode_invalid"
    return {
        "mode": mode,
        "state": state,
        "reason": reason,
        "availability_requires": list(availability),
        "missing_availability": sorted(set(availability) - packet.facts),
        "satisfies_all": list(satisfies_all),
        "satisfies_any": list(satisfies_any),
        "forbids": list(forbids),
        "matched_satisfies_all": sorted(set(satisfies_all).intersection(packet.facts)),
        "matched_satisfies_any": sorted(set(satisfies_any).intersection(packet.facts)),
        "matched_forbids": sorted(set(forbids).intersection(packet.facts)),
    }

def _claim_matches(packet: FactPacket, claim: dict[str, Any]) -> tuple[bool, str, dict[str, Any] | None]:
    app = claim.get("applicability", {})
    if app.get("temporal_scope") != packet.temporal_scope:
        return False, "temporal_scope_mismatch", None
    if packet.temporal_scope != SUPPORTED_TEMPORAL_SCOPE:
        return False, "dynamic_scope_not_admitted", None
    if packet.requested_subjects and claim.get("subject") not in packet.requested_subjects:
        return False, "subject_not_requested", None
    requires = set(app.get("requires", []))
    if not requires.issubset(packet.facts):
        return False, "required_fact_missing", None
    forbids = set(app.get("forbids", []))
    if forbids.intersection(packet.facts):
        return False, "forbidden_fact_present", None
    activation = _evaluate_conditional_activation(packet, claim)
    if activation is not None and activation["state"] not in ACTIVE_CONDITIONAL_STATES:
        return False, activation["reason"], activation
    return True, "matched", activation

def retrieve_claims(
    packet: FactPacket,
    registries: Iterable[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    regs = list(registries) if registries is not None else load_registries()
    selected: list[dict[str, Any]] = []
    omissions: list[dict[str, str]] = []
    conditional_evaluations: list[dict[str, Any]] = []
    conflict_defs: dict[str, dict[str, Any]] = {}

    for registry in regs:
        if registry.get("production_routable") is not False:
            raise ValueError("research retriever refuses production-routable registry")
        if registry.get("interpretation_profile") != packet.interpretation_profile:
            continue
        for group in registry.get("conflict_groups", []):
            conflict_defs[group["conflict_group_id"]] = group
        for claim in registry.get("claims", []):
            cid = claim.get("claim_id", "")
            if claim.get("adoption_state") != ELIGIBLE_ADOPTION:
                omissions.append({"claim_id": cid, "reason": "claim_not_research_eligible"})
                continue
            if packet.enabled_source_ids and not set(claim.get("source_refs", [])).intersection(packet.enabled_source_ids):
                omissions.append({"claim_id": cid, "reason": "source_not_enabled"})
                continue
            matched, reason, activation = _claim_matches(packet, claim)
            if activation is not None:
                conditional_evaluations.append({
                    "claim_id": cid,
                    "subject": claim.get("subject"),
                    "claim_type": claim.get("claim_type"),
                    "conflict_group_ids": list(claim.get("conflict_group_ids", [])),
                    **activation,
                })
            if not matched:
                omissions.append({"claim_id": cid, "reason": reason})
                continue
            selected.append({
                "claim_id": cid,
                "subject": claim["subject"],
                "claim_type": claim["claim_type"],
                "assertion_class": claim["assertion_class"],
                "normalized_statement": claim["normalized_statement"],
                "source_refs": list(claim.get("source_refs", [])),
                "source_locators": list(claim.get("source_locators", [])),
                "conflict_group_ids": list(claim.get("conflict_group_ids", [])),
                "specificity": SPECIFICITY.get(claim.get("claim_type"), 0),
                "matched_requires": list(claim.get("applicability", {}).get("requires", [])),
                "conditional_activation": activation,
                "temporal_scope": claim.get("applicability", {}).get("temporal_scope"),
            })

    selected.sort(key=lambda x: (-x["specificity"], x["claim_id"]))
    conditional_evaluations.sort(key=lambda x: x["claim_id"])
    active_groups = sorted({gid for claim in selected for gid in claim["conflict_group_ids"]})
    conflicts = [{
        "conflict_group_id": gid,
        "resolution_status": conflict_defs.get(gid, {}).get("resolution_status", "UNRESOLVED"),
        "selected_claim_ids": [x["claim_id"] for x in selected if gid in x["conflict_group_ids"]],
    } for gid in active_groups]

    return {
        "authority": "REFERENCE-ONLY / RESEARCH EXECUTABLE / NOT PRODUCTION-ROUTABLE",
        "packet_id": packet.packet_id,
        "interpretation_profile": packet.interpretation_profile,
        "temporal_scope": packet.temporal_scope,
        "selected_claims": selected,
        "conditional_evaluations": conditional_evaluations,
        "conflicts": conflicts,
        "omissions": omissions,
        "production_authority_granted": False,
    }

def compose_frame(packet: FactPacket, retrieval: dict[str, Any]) -> dict[str, Any]:
    claims = retrieval["selected_claims"]
    by_subject: dict[str, list[str]] = {}
    for claim in claims:
        by_subject.setdefault(claim["subject"], []).append(claim["claim_id"])
    return {
        "authority": "REFERENCE-ONLY / RESEARCH EXECUTABLE / NOT PRODUCTION-ROUTABLE",
        "frame_version": "0.2.0-research",
        "packet_id": packet.packet_id,
        "interpretation_profile": packet.interpretation_profile,
        "temporal_scope": packet.temporal_scope,
        "selected_claim_ids": [x["claim_id"] for x in claims],
        "subject_claims": by_subject,
        "conditional_evaluations": retrieval["conditional_evaluations"],
        "conflicts": retrieval["conflicts"],
        "omission_count": len(retrieval["omissions"]),
        "rendering_boundary": "frame_only_no_doctrine_generation",
        "production_authority_granted": False,
    }
