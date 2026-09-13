#!/usr/bin/env python3
"""Validate and render a bounded Astrology Production v1 user-facing output draft.

This module is a deterministic compliance adapter. It does not calculate chart
facts, choose Astrology claims, or author semantic interpretation. It consumes
an admitted ``astrology_interpretation_handoff@1.0.0`` plus a ChatGPT-authored
``astrology_output_draft@1.0.0`` and verifies that every cited fact/claim is
already present in the handoff, that question identity and exclusions are
preserved, and that the caller attests the required Pre-Send checks.

The adapter then renders a stable final-output envelope. Semantic correctness
of the prose remains owned by ``ASTROLOGY.md`` and ``CHATGPT_OUTPUT.md``.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DRAFT_SCHEMA_NAME = "astrology_output_draft"
DRAFT_SCHEMA_VERSION = "1.0.0"
OUTPUT_SCHEMA_NAME = "astrology_user_facing_output"
OUTPUT_SCHEMA_VERSION = "1.0.0"
HANDOFF_SCHEMA_NAME = "astrology_interpretation_handoff"
HANDOFF_SCHEMA_VERSION = "1.0.0"
ADAPTER_ID = "astrology-output-guard-v1"
ADAPTER_VERSION = "1.0.0"
DRAFT_SCHEMA_PATH = "ASTROLOGY_OUTPUT_DRAFT_V1.schema.json"

ATTESTATION_KEYS = {
    "direct_answer_checked",
    "scope_and_exclusions_checked",
    "evidence_language_checked",
    "conclusion_consistency_checked",
    "unresolved_handling_checked",
    "eligible_layer_checked",
    "structured_fact_provenance_checked",
    "unsupported_factor_boundary_checked",
    "conflict_and_caution_checked",
}


class AstrologyOutputGuardError(ValueError):
    """The proposed user-facing Astrology draft violates the production contract."""


def _object(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise AstrologyOutputGuardError(f"{path} must be an object")
    return value


def _exact_keys(data: dict[str, Any], *, allowed: set[str], required: set[str], path: str) -> None:
    missing = sorted(required - data.keys())
    if missing:
        raise AstrologyOutputGuardError(f"{path} missing required field(s): {', '.join(missing)}")
    extra = sorted(data.keys() - allowed)
    if extra:
        raise AstrologyOutputGuardError(f"{path} contains unsupported field(s): {', '.join(extra)}")


def _text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AstrologyOutputGuardError(f"{path} must be a non-empty string")
    return value.strip()


def _fact_ref(value: Any, path: str) -> dict[str, str]:
    row = _object(value, path)
    _exact_keys(row, allowed={"bundle", "fact_id"}, required={"bundle", "fact_id"}, path=path)
    bundle = _text(row["bundle"], f"{path}.bundle")
    if bundle not in {"natal", "transit"}:
        raise AstrologyOutputGuardError(f"{path}.bundle must be natal or transit")
    return {"bundle": bundle, "fact_id": _text(row["fact_id"], f"{path}.fact_id")}


def _claim_ref(value: Any, path: str) -> dict[str, str]:
    row = _object(value, path)
    _exact_keys(
        row,
        allowed={"registry_record_id", "claim_id"},
        required={"registry_record_id", "claim_id"},
        path=path,
    )
    return {
        "registry_record_id": _text(row["registry_record_id"], f"{path}.registry_record_id"),
        "claim_id": _text(row["claim_id"], f"{path}.claim_id"),
    }


def _fact_key(ref: dict[str, str]) -> tuple[str, str]:
    return ref["bundle"], ref["fact_id"]


def _claim_key(ref: dict[str, str]) -> tuple[str, str]:
    return ref["registry_record_id"], ref["claim_id"]


def _normalize_unit(value: Any, path: str) -> dict[str, Any]:
    row = _object(value, path)
    _exact_keys(row, allowed={"text", "fact_refs", "claim_refs"}, required={"text", "fact_refs", "claim_refs"}, path=path)
    fact_refs_raw = row["fact_refs"]
    claim_refs_raw = row["claim_refs"]
    if not isinstance(fact_refs_raw, list) or not fact_refs_raw:
        raise AstrologyOutputGuardError(f"{path}.fact_refs must be a non-empty array")
    if not isinstance(claim_refs_raw, list):
        raise AstrologyOutputGuardError(f"{path}.claim_refs must be an array")
    fact_refs = [_fact_ref(item, f"{path}.fact_refs[{index}]") for index, item in enumerate(fact_refs_raw)]
    claim_refs = [_claim_ref(item, f"{path}.claim_refs[{index}]") for index, item in enumerate(claim_refs_raw)]
    if len({_fact_key(ref) for ref in fact_refs}) != len(fact_refs):
        raise AstrologyOutputGuardError(f"{path}.fact_refs must not contain duplicates")
    if len({_claim_key(ref) for ref in claim_refs}) != len(claim_refs):
        raise AstrologyOutputGuardError(f"{path}.claim_refs must not contain duplicates")
    text = _text(row["text"], f"{path}.text")
    if len(text) > 1600:
        raise AstrologyOutputGuardError(f"{path}.text exceeds 1600 characters")
    return {"text": text, "fact_refs": fact_refs, "claim_refs": claim_refs}


def normalize_draft(value: Any) -> dict[str, Any]:
    root = _object(value, "$")
    _exact_keys(
        root,
        allowed={"schema_name", "schema_version", "question_id", "conclusion", "evidence", "pre_send_attestations"},
        required={"schema_name", "schema_version", "question_id", "conclusion", "evidence", "pre_send_attestations"},
        path="$",
    )
    if root["schema_name"] != DRAFT_SCHEMA_NAME:
        raise AstrologyOutputGuardError(f"$.schema_name must equal {DRAFT_SCHEMA_NAME}")
    if root["schema_version"] != DRAFT_SCHEMA_VERSION:
        raise AstrologyOutputGuardError(f"$.schema_version must equal {DRAFT_SCHEMA_VERSION}")
    evidence_raw = root["evidence"]
    if not isinstance(evidence_raw, list) or not evidence_raw:
        raise AstrologyOutputGuardError("$.evidence must be a non-empty array")
    if len(evidence_raw) > 8:
        raise AstrologyOutputGuardError("$.evidence must contain at most 8 items")
    attestations = _object(root["pre_send_attestations"], "$.pre_send_attestations")
    _exact_keys(attestations, allowed=ATTESTATION_KEYS, required=ATTESTATION_KEYS, path="$.pre_send_attestations")
    false_keys = sorted(key for key in ATTESTATION_KEYS if attestations.get(key) is not True)
    if false_keys:
        raise AstrologyOutputGuardError(
            "all required Pre-Send attestations must be true: " + ", ".join(false_keys)
        )
    return {
        "schema_name": DRAFT_SCHEMA_NAME,
        "schema_version": DRAFT_SCHEMA_VERSION,
        "question_id": _text(root["question_id"], "$.question_id"),
        "conclusion": _normalize_unit(root["conclusion"], "$.conclusion"),
        "evidence": [_normalize_unit(item, f"$.evidence[{index}]") for index, item in enumerate(evidence_raw)],
        "pre_send_attestations": {key: True for key in sorted(ATTESTATION_KEYS)},
    }


def _validate_handoff(value: Any) -> dict[str, Any]:
    handoff = _object(value, "$handoff")
    if handoff.get("schema_name") != HANDOFF_SCHEMA_NAME or handoff.get("schema_version") != HANDOFF_SCHEMA_VERSION:
        raise AstrologyOutputGuardError(
            f"handoff must be {HANDOFF_SCHEMA_NAME}@{HANDOFF_SCHEMA_VERSION}"
        )
    if handoff.get("status") != "ready_for_bounded_interpretation" or handoff.get("interpretation_allowed") is not True:
        raise AstrologyOutputGuardError("handoff is not admitted for bounded interpretation")
    adapter = handoff.get("adapter")
    if not isinstance(adapter, dict) or adapter.get("authority") != "evidence_packaging_only":
        raise AstrologyOutputGuardError("handoff adapter authority is invalid")
    return handoff


def _selected_fact_index(handoff: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    output: dict[tuple[str, str], dict[str, Any]] = {}
    for index, row in enumerate(handoff.get("selected_facts", [])):
        if not isinstance(row, dict):
            raise AstrologyOutputGuardError(f"handoff selected_facts[{index}] must be an object")
        bundle = row.get("bundle")
        fact = row.get("fact")
        if not isinstance(bundle, str) or not isinstance(fact, dict) or not isinstance(fact.get("fact_id"), str):
            raise AstrologyOutputGuardError(f"handoff selected_facts[{index}] has invalid identity")
        key = (bundle, fact["fact_id"])
        if key in output:
            raise AstrologyOutputGuardError(f"duplicate selected fact in handoff: {bundle} / {fact['fact_id']}")
        output[key] = row
    if not output:
        raise AstrologyOutputGuardError("handoff contains no selected facts")
    return output


def _selected_claim_index(handoff: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    output: dict[tuple[str, str], dict[str, Any]] = {}
    for index, row in enumerate(handoff.get("selected_claims", [])):
        if not isinstance(row, dict):
            raise AstrologyOutputGuardError(f"handoff selected_claims[{index}] must be an object")
        registry_id = row.get("registry_record_id")
        claim_id = row.get("claim_id")
        if not isinstance(registry_id, str) or not isinstance(claim_id, str):
            raise AstrologyOutputGuardError(f"handoff selected_claims[{index}] has invalid identity")
        key = (registry_id, claim_id)
        if key in output:
            raise AstrologyOutputGuardError(f"duplicate selected claim in handoff: {registry_id} / {claim_id}")
        output[key] = row
    return output


def _validate_unit_refs(
    unit: dict[str, Any],
    *,
    path: str,
    fact_index: dict[tuple[str, str], dict[str, Any]],
    claim_index: dict[tuple[str, str], dict[str, Any]],
) -> None:
    for ref in unit["fact_refs"]:
        if _fact_key(ref) not in fact_index:
            raise AstrologyOutputGuardError(
                f"{path} cites fact outside admitted handoff: {ref['bundle']} / {ref['fact_id']}"
            )
    for ref in unit["claim_refs"]:
        if _claim_key(ref) not in claim_index:
            raise AstrologyOutputGuardError(
                f"{path} cites claim outside admitted handoff: {ref['registry_record_id']} / {ref['claim_id']}"
            )


def build_output(handoff: Any, draft: Any) -> dict[str, Any]:
    admitted_handoff = _validate_handoff(handoff)
    normalized = normalize_draft(draft)
    question = admitted_handoff.get("question")
    if not isinstance(question, dict):
        raise AstrologyOutputGuardError("handoff question metadata is missing")
    handoff_question_id = question.get("question_id")
    if normalized["question_id"] != handoff_question_id:
        raise AstrologyOutputGuardError(
            f"draft question_id does not match handoff: {normalized['question_id']} != {handoff_question_id}"
        )

    fact_index = _selected_fact_index(admitted_handoff)
    claim_index = _selected_claim_index(admitted_handoff)
    _validate_unit_refs(
        normalized["conclusion"],
        path="$.conclusion",
        fact_index=fact_index,
        claim_index=claim_index,
    )
    for index, unit in enumerate(normalized["evidence"]):
        _validate_unit_refs(
            unit,
            path=f"$.evidence[{index}]",
            fact_index=fact_index,
            claim_index=claim_index,
        )

    used_fact_keys = {
        _fact_key(ref)
        for unit in [normalized["conclusion"], *normalized["evidence"]]
        for ref in unit["fact_refs"]
    }
    used_claim_keys = {
        _claim_key(ref)
        for unit in [normalized["conclusion"], *normalized["evidence"]]
        for ref in unit["claim_refs"]
    }

    disclosures = [item for item in admitted_handoff.get("required_disclosures", []) if isinstance(item, str) and item.strip()]
    unsupported = [row for row in admitted_handoff.get("unsupported_factors", []) if isinstance(row, dict)]
    conflicts = [row for row in admitted_handoff.get("conflicts", []) if isinstance(row, dict)]

    rendered_lines = [normalized["conclusion"]["text"]]
    rendered_lines.extend(f"- {unit['text']}" for unit in normalized["evidence"])
    if unsupported:
        rendered_lines.append("Unsupported / unavailable factors:")
        rendered_lines.extend(
            f"- {row.get('factor')}: {row.get('reason')}"
            for row in unsupported
            if isinstance(row.get("factor"), str) and isinstance(row.get("reason"), str)
        )
    if disclosures:
        rendered_lines.append("Required disclosures:")
        rendered_lines.extend(f"- {item}" for item in disclosures)

    return {
        "schema_name": OUTPUT_SCHEMA_NAME,
        "schema_version": OUTPUT_SCHEMA_VERSION,
        "status": "ready_for_user",
        "output_allowed": True,
        "adapter": {
            "adapter_id": ADAPTER_ID,
            "adapter_version": ADAPTER_VERSION,
            "authority": "provenance_and_pre_send_validation_only",
            "semantic_interpretation_authored": False,
            "final_text_authored": False,
        },
        "owners": {
            "method_owner": "ASTROLOGY.md",
            "output_owner": "CHATGPT_OUTPUT.md",
            "draft_schema": DRAFT_SCHEMA_PATH,
        },
        "question": {
            "question_id": handoff_question_id,
            "text": question.get("text"),
            "focus": question.get("focus", []),
            "exclusions": question.get("exclusions", []),
        },
        "conclusion": normalized["conclusion"],
        "evidence": normalized["evidence"],
        "required_disclosures": disclosures,
        "unsupported_factors": unsupported,
        "conflicts": conflicts,
        "used_fact_refs": [
            {"bundle": bundle, "fact_id": fact_id}
            for bundle, fact_id in sorted(used_fact_keys)
        ],
        "used_claim_refs": [
            {"registry_record_id": registry_id, "claim_id": claim_id}
            for registry_id, claim_id in sorted(used_claim_keys)
        ],
        "source_provenance": [
            {
                "registry_record_id": claim["registry_record_id"],
                "claim_id": claim["claim_id"],
                "sources": claim.get("source_provenance", []),
                "cautions": claim.get("cautions", []),
            }
            for key, claim in sorted(claim_index.items())
            if key in used_claim_keys
        ],
        "pre_send_attestations": normalized["pre_send_attestations"],
        "rendered_text": "\n".join(rendered_lines),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a ChatGPT-authored Astrology output draft against an admitted interpretation handoff."
    )
    parser.add_argument("handoff", type=Path)
    parser.add_argument("draft", type=Path)
    args = parser.parse_args()
    try:
        handoff = json.loads(args.handoff.read_text(encoding="utf-8"))
        draft = json.loads(args.draft.read_text(encoding="utf-8"))
        result = build_output(handoff, draft)
    except (OSError, json.JSONDecodeError, AstrologyOutputGuardError) as exc:
        result = {
            "schema_name": OUTPUT_SCHEMA_NAME,
            "schema_version": OUTPUT_SCHEMA_VERSION,
            "status": "rejected",
            "output_allowed": False,
            "error": str(exc),
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
