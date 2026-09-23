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

def _claim_matches(packet: FactPacket, claim: dict[str, Any]) -> tuple[bool, str]:
    app = claim.get("applicability", {})
    if app.get("temporal_scope") != packet.temporal_scope:
        return False, "temporal_scope_mismatch"
    if packet.temporal_scope != SUPPORTED_TEMPORAL_SCOPE:
        return False, "dynamic_scope_not_admitted"
    if packet.requested_subjects and claim.get("subject") not in packet.requested_subjects:
        return False, "subject_not_requested"
    requires = set(app.get("requires", []))
    if not requires.issubset(packet.facts):
        return False, "required_fact_missing"
    forbids = set(app.get("forbids", []))
    if forbids.intersection(packet.facts):
        return False, "forbidden_fact_present"
    return True, "matched"

def retrieve_claims(
    packet: FactPacket,
    registries: Iterable[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    regs = list(registries) if registries is not None else load_registries()
    selected: list[dict[str, Any]] = []
    omissions: list[dict[str, str]] = []
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
            matched, reason = _claim_matches(packet, claim)
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
                "temporal_scope": claim.get("applicability", {}).get("temporal_scope"),
            })

    selected.sort(key=lambda x: (-x["specificity"], x["claim_id"]))
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
        "frame_version": "0.1.0-research",
        "packet_id": packet.packet_id,
        "interpretation_profile": packet.interpretation_profile,
        "temporal_scope": packet.temporal_scope,
        "selected_claim_ids": [x["claim_id"] for x in claims],
        "subject_claims": by_subject,
        "conflicts": retrieval["conflicts"],
        "omission_count": len(retrieval["omissions"]),
        "rendering_boundary": "frame_only_no_doctrine_generation",
        "production_authority_granted": False,
    }
