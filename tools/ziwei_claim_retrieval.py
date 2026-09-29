#!/usr/bin/env python3
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_ROOT = ROOT / "references" / "ziwei"
DEFAULT_REGISTRIES = (
    REGISTRY_ROOT / "ziwei_interpretation_claim_registry_batch1.json",
    REGISTRY_ROOT / "ziwei_interpretation_claim_registry_batch2.json",
    REGISTRY_ROOT / "ziwei_interpretation_claim_registry_palaces_v0.json",
)
SUPPORTED_TEMPORAL_SCOPES = frozenset({"natal_baseline","decadal","yearly","monthly","daily","hourly"})
ELIGIBLE_ADOPTION = "RESEARCH_CLAIM_ELIGIBLE"
CONDITIONAL_CLAIM_TYPES = {"star_conditional", "palace_conditional"}
ACTIVE_CONDITIONAL_STATES = {"not_required", "satisfied"}

SPECIFICITY = {
    "star_palace_context": 47,
    "body_palace_overlay": 45,
    "same_palace_pair": 50,
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
    if packet.temporal_scope not in SUPPORTED_TEMPORAL_SCOPES:
        return False, "dynamic_scope_not_admitted", None
    claim_subjects=set(str(x) for x in claim.get("subjects",[]) if isinstance(x,str) and x)
    if not claim_subjects:
        subject=claim.get("subject")
        if isinstance(subject,str) and subject:
            claim_subjects.add(subject)
    if packet.requested_subjects and not claim_subjects.intersection(packet.requested_subjects):
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
                "subjects": list(claim.get("subjects", [claim["subject"]])),
                "pair_members": list(claim.get("pair_members", [])),
                "overlay_palace": claim.get("overlay_palace"),
                "star": claim.get("star"),
                "palace": claim.get("palace"),
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

NATAL_SYNTHESIS_VERSION = "1.0.0"
NATAL_SYNTHESIS_FOCUS_MIN = 4
NATAL_SYNTHESIS_FOCUS_MAX = 6
NATAL_SYNTHESIS_EXACT_TYPES = frozenset({"same_palace_pair", "star_palace_context", "body_palace_overlay"})
NATAL_SYNTHESIS_CONDITIONAL_TYPES = frozenset({"star_conditional", "palace_conditional"})


def select_natal_synthesis_focus(
    packet: FactPacket,
    retrieval: dict[str, Any],
    *,
    eligible_claim_ids: frozenset[str] | set[str],
    target_min: int = NATAL_SYNTHESIS_FOCUS_MIN,
    target_max: int = NATAL_SYNTHESIS_FOCUS_MAX,
) -> dict[str, Any]:
    """Select a small evidence-bounded natal focus without generating doctrine."""
    if not (1 <= target_min <= target_max):
        raise ValueError("invalid natal synthesis focus target")

    allow = set(eligible_claim_ids)
    claims = [
        claim for claim in retrieval.get("selected_claims", [])
        if claim.get("claim_id") in allow
    ]
    by_subject_type: dict[tuple[str, str], dict[str, Any]] = {}
    for claim in claims:
        subject = claim.get("subject")
        claim_type = claim.get("claim_type")
        if isinstance(subject, str) and isinstance(claim_type, str):
            by_subject_type[(subject, claim_type)] = claim

    candidates: list[dict[str, Any]] = []
    exact_star_palace: set[tuple[str, str]] = set()

    def add_claim_signal(claim: dict[str, Any], tier: int) -> None:
        subjects = tuple(str(x) for x in claim.get("subjects", []) if isinstance(x, str) and x)
        if not subjects and isinstance(claim.get("subject"), str):
            subjects = (claim["subject"],)
        candidates.append({
            "signal_id": f"claim:{claim['claim_id']}",
            "signal_type": claim["claim_type"],
            "claim_ids": [claim["claim_id"]],
            "subjects": list(subjects),
            "tier": tier,
            "specificity": int(claim.get("specificity", 0)),
        })

    for claim in claims:
        ctype = claim.get("claim_type")
        if ctype in NATAL_SYNTHESIS_EXACT_TYPES:
            add_claim_signal(claim, 3)
            if (
                ctype == "star_palace_context"
                and isinstance(claim.get("star"), str)
                and isinstance(claim.get("palace"), str)
            ):
                exact_star_palace.add((claim["star"], claim["palace"]))

    for claim in claims:
        if claim.get("claim_type") not in NATAL_SYNTHESIS_CONDITIONAL_TYPES:
            continue
        activation = claim.get("conditional_activation")
        if isinstance(activation, dict) and activation.get("state") == "satisfied":
            add_claim_signal(claim, 2)

    occupancies: list[tuple[str, str]] = []
    for fact in sorted(packet.facts):
        if not fact.startswith("star_in_palace:"):
            continue
        parts = fact.split(":", 2)
        if len(parts) == 3:
            occupancies.append((parts[1], parts[2]))

    for star, palace in occupancies:
        if (star, palace) in exact_star_palace:
            continue
        star_claim = by_subject_type.get((star, "star_core"))
        palace_claim = by_subject_type.get((palace, "palace_domain"))
        if star_claim is None or palace_claim is None:
            continue
        candidates.append({
            "signal_id": f"bounded_l5:{star}:{palace}",
            "signal_type": "bounded_l5_composition",
            "claim_ids": [star_claim["claim_id"], palace_claim["claim_id"]],
            "subjects": [star, palace],
            "star": star,
            "palace": palace,
            "tier": 1,
            "specificity": int(star_claim.get("specificity", 0)) + int(palace_claim.get("specificity", 0)),
            "life_palace_starting_point": palace == "命宮",
        })

    candidates.sort(key=lambda x: (
        -int(x["tier"]),
        -int(bool(x.get("life_palace_starting_point"))),
        -int(x["specificity"]),
        x["signal_id"],
    ))

    chosen: list[dict[str, Any]] = []
    covered_subjects: set[str] = set()
    chosen_ids: set[str] = set()
    for candidate in candidates:
        subjects = set(candidate["subjects"])
        if subjects and subjects.issubset(covered_subjects):
            continue
        chosen.append(candidate)
        chosen_ids.add(candidate["signal_id"])
        covered_subjects.update(subjects)
        if len(chosen) >= target_max:
            break

    if len(chosen) < target_min:
        for candidate in candidates:
            if candidate["signal_id"] in chosen_ids:
                continue
            chosen.append(candidate)
            chosen_ids.add(candidate["signal_id"])
            if len(chosen) >= target_min:
                break

    relations: list[dict[str, Any]] = []
    for i, left in enumerate(chosen):
        left_subjects = set(left["subjects"])
        for right in chosen[i + 1:]:
            shared = sorted(left_subjects.intersection(right["subjects"]))
            if shared:
                relations.append({
                    "relation": "shared_subject",
                    "signal_ids": [left["signal_id"], right["signal_id"]],
                    "shared_subjects": shared,
                })

    focus_claim_ids = sorted({cid for signal in chosen for cid in signal["claim_ids"]})
    return {
        "module_id": "natal_synthesis_v1",
        "version": NATAL_SYNTHESIS_VERSION,
        "authority": "selection-only-admitted-claims-no-new-doctrine",
        "eligible_scope": "default_70_base_natal_claims_only",
        "focus_target": {"min": target_min, "max": target_max},
        "eligible_claim_count": len(claims),
        "candidate_signal_count": len(candidates),
        "focus_count": len(chosen),
        "focus_signal_ids": [x["signal_id"] for x in chosen],
        "focus_claim_ids": focus_claim_ids,
        "focus_signals": chosen,
        "relations": relations,
        "under_target": len(chosen) < target_min,
        "under_target_reason": "eligible_signals_below_target" if len(chosen) < target_min else None,
        "deduplication": "higher_specificity_then_subject_diversity",
        "rendering_boundary": "use_only_referenced_admitted_claim_statements_no_new_doctrine",
        "final_prose_authority": False,
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
