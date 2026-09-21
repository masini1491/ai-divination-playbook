#!/usr/bin/env python3
"""Build a bounded Astrology Production v1 interpretation evidence handoff.

This module does not choose astrological meanings, calculate chart facts, or
render final reading prose. It validates a caller-proposed minimum evidence
selection against one admitted ``astrology_reading_run@1.0.0`` and the bounded
production claim admissions declared by ``ASTROLOGY_PRODUCTION_ADMISSION_V1``.

The output is an auditable evidence package for ``ASTROLOGY.md`` plus
``CHATGPT_OUTPUT.md``. Research registries remain REFERENCE-ONLY as stored;
this adapter only allows individual claims whose registry and source admission
meet the current production manifest.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REQUEST_SCHEMA_NAME = "astrology_interpretation_request"
REQUEST_SCHEMA_VERSION = "1.0.0"
HANDOFF_SCHEMA_NAME = "astrology_interpretation_handoff"
HANDOFF_SCHEMA_VERSION = "1.0.0"
ADAPTER_ID = "astrology-interpretation-handoff-v1"
ADAPTER_VERSION = "1.0.0"
READING_RUN_SCHEMA_NAME = "astrology_reading_run"
READING_RUN_SCHEMA_VERSION = "1.0.0"
REQUEST_SCHEMA_PATH = "ASTROLOGY_INTERPRETATION_REQUEST_V1.schema.json"
PRODUCTION_MANIFEST_PATH = "ASTROLOGY_PRODUCTION_ADMISSION_V1.json"


class InterpretationHandoffError(ValueError):
    """The proposed interpretation evidence selection is not production-admissible."""


def _root_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def _load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise InterpretationHandoffError(f"cannot load {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise InterpretationHandoffError(f"{path} must contain a JSON object")
    return data


def _object(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise InterpretationHandoffError(f"{path} must be an object")
    return value


def _exact_keys(data: dict[str, Any], *, allowed: set[str], required: set[str], path: str) -> None:
    missing = sorted(required - data.keys())
    if missing:
        raise InterpretationHandoffError(f"{path} missing required field(s): {', '.join(missing)}")
    extra = sorted(data.keys() - allowed)
    if extra:
        raise InterpretationHandoffError(f"{path} contains unsupported field(s): {', '.join(extra)}")


def _text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InterpretationHandoffError(f"{path} must be a non-empty string")
    return value.strip()


def _string_list(value: Any, path: str) -> list[str]:
    if not isinstance(value, list):
        raise InterpretationHandoffError(f"{path} must be an array")
    output: list[str] = []
    for index, item in enumerate(value):
        text = _text(item, f"{path}[{index}]")
        if text in output:
            raise InterpretationHandoffError(f"{path} must not contain duplicates: {text}")
        output.append(text)
    return output


def _normalize_fact_ref(value: Any, path: str) -> dict[str, str]:
    ref = _object(value, path)
    _exact_keys(ref, allowed={"bundle", "fact_id"}, required={"bundle", "fact_id"}, path=path)
    bundle = _text(ref["bundle"], f"{path}.bundle")
    if bundle not in {"natal", "transit"}:
        raise InterpretationHandoffError(f"{path}.bundle must be natal or transit")
    return {"bundle": bundle, "fact_id": _text(ref["fact_id"], f"{path}.fact_id")}


def _ref_key(ref: dict[str, str]) -> tuple[str, str]:
    return ref["bundle"], ref["fact_id"]


def normalize_request(data: Any) -> dict[str, Any]:
    root = _object(data, "$")
    _exact_keys(
        root,
        allowed={
            "schema_name",
            "schema_version",
            "question_id",
            "question",
            "focus",
            "exclusions",
            "fact_refs",
            "claim_requests",
            "unsupported_factors",
        },
        required={"schema_name", "schema_version", "question_id", "question", "fact_refs", "claim_requests"},
        path="$",
    )
    if root["schema_name"] != REQUEST_SCHEMA_NAME:
        raise InterpretationHandoffError(f"$.schema_name must equal {REQUEST_SCHEMA_NAME}")
    if root["schema_version"] != REQUEST_SCHEMA_VERSION:
        raise InterpretationHandoffError(f"$.schema_version must equal {REQUEST_SCHEMA_VERSION}")

    if not isinstance(root["fact_refs"], list) or not root["fact_refs"]:
        raise InterpretationHandoffError("$.fact_refs must be a non-empty array")
    fact_refs = [_normalize_fact_ref(row, f"$.fact_refs[{index}]") for index, row in enumerate(root["fact_refs"])]
    keys = [_ref_key(ref) for ref in fact_refs]
    if len(set(keys)) != len(keys):
        raise InterpretationHandoffError("$.fact_refs must not contain duplicates")
    selected_keys = set(keys)

    if not isinstance(root["claim_requests"], list):
        raise InterpretationHandoffError("$.claim_requests must be an array")
    claim_requests: list[dict[str, Any]] = []
    seen_claims: set[tuple[str, str]] = set()
    for index, raw in enumerate(root["claim_requests"]):
        path = f"$.claim_requests[{index}]"
        row = _object(raw, path)
        _exact_keys(
            row,
            allowed={"registry_record_id", "claim_id", "fact_refs"},
            required={"registry_record_id", "claim_id", "fact_refs"},
            path=path,
        )
        registry_id = _text(row["registry_record_id"], f"{path}.registry_record_id")
        claim_id = _text(row["claim_id"], f"{path}.claim_id")
        identity = (registry_id, claim_id)
        if identity in seen_claims:
            raise InterpretationHandoffError(f"duplicate claim request: {registry_id} / {claim_id}")
        seen_claims.add(identity)
        if not isinstance(row["fact_refs"], list) or not row["fact_refs"]:
            raise InterpretationHandoffError(f"{path}.fact_refs must be a non-empty array")
        links = [_normalize_fact_ref(item, f"{path}.fact_refs[{j}]") for j, item in enumerate(row["fact_refs"])]
        link_keys = [_ref_key(ref) for ref in links]
        if len(set(link_keys)) != len(link_keys):
            raise InterpretationHandoffError(f"{path}.fact_refs must not contain duplicates")
        unknown_links = [ref for ref in links if _ref_key(ref) not in selected_keys]
        if unknown_links:
            raise InterpretationHandoffError(f"{path}.fact_refs must reference entries already selected in $.fact_refs")
        claim_requests.append({"registry_record_id": registry_id, "claim_id": claim_id, "fact_refs": links})

    unsupported: list[dict[str, str]] = []
    raw_unsupported = root.get("unsupported_factors", [])
    if not isinstance(raw_unsupported, list):
        raise InterpretationHandoffError("$.unsupported_factors must be an array")
    for index, raw in enumerate(raw_unsupported):
        path = f"$.unsupported_factors[{index}]"
        row = _object(raw, path)
        _exact_keys(row, allowed={"factor", "reason"}, required={"factor", "reason"}, path=path)
        unsupported.append({"factor": _text(row["factor"], f"{path}.factor"), "reason": _text(row["reason"], f"{path}.reason")})

    return {
        "schema_name": REQUEST_SCHEMA_NAME,
        "schema_version": REQUEST_SCHEMA_VERSION,
        "question_id": _text(root["question_id"], "$.question_id"),
        "question": _text(root["question"], "$.question"),
        "focus": _string_list(root.get("focus", []), "$.focus"),
        "exclusions": _string_list(root.get("exclusions", []), "$.exclusions"),
        "fact_refs": fact_refs,
        "claim_requests": claim_requests,
        "unsupported_factors": unsupported,
    }


def _validate_run(run: Any) -> dict[str, Any]:
    data = _object(run, "$run")
    if data.get("schema_name") != READING_RUN_SCHEMA_NAME or data.get("schema_version") != READING_RUN_SCHEMA_VERSION:
        raise InterpretationHandoffError(
            f"reading run must be {READING_RUN_SCHEMA_NAME}@{READING_RUN_SCHEMA_VERSION}"
        )
    if data.get("status") != "admitted" or data.get("interpretation_allowed") is not True:
        raise InterpretationHandoffError("reading run is not admitted for interpretation")
    bundles = data.get("fact_bundles")
    gates = data.get("runtime_gates")
    if not isinstance(bundles, dict) or not isinstance(gates, dict):
        raise InterpretationHandoffError("reading run must contain fact_bundles and runtime_gates")
    for bundle_name, bundle in bundles.items():
        if bundle_name not in {"natal", "transit"} or not isinstance(bundle, dict):
            raise InterpretationHandoffError(f"unsupported fact bundle in reading run: {bundle_name}")
        gate = gates.get(bundle_name)
        if not isinstance(gate, dict) or gate.get("interpretation_allowed") is not True:
            raise InterpretationHandoffError(f"{bundle_name} bundle is missing an admitted runtime gate")
    return data


def _fact_index(run: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    index: dict[tuple[str, str], dict[str, Any]] = {}
    for bundle_name, bundle in run["fact_bundles"].items():
        facts = bundle.get("facts", {})
        if not isinstance(facts, dict):
            continue
        for collection in ("objects", "houses", "aspects", "events"):
            rows = facts.get(collection, [])
            if not isinstance(rows, list):
                continue
            for row in rows:
                if not isinstance(row, dict) or not isinstance(row.get("fact_id"), str):
                    continue
                key = (bundle_name, row["fact_id"])
                if key in index:
                    raise InterpretationHandoffError(f"duplicate fact identity in reading run: {bundle_name} / {row['fact_id']}")
                index[key] = {"bundle": bundle_name, "collection": collection, "fact": row}
    return index


def _registry_index(root: Path, admitted_ids: set[str]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    registry_dir = root / "references" / "astrology"
    for path in sorted(registry_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(data, dict):
            continue
        record_id = data.get("record_id")
        if record_id not in admitted_ids:
            continue
        if data.get("schema_name") != "interpretation_claim_registry":
            continue
        if record_id in index:
            raise InterpretationHandoffError(f"duplicate admitted registry record_id: {record_id}")
        index[record_id] = {"path": path.relative_to(root).as_posix(), "data": data}
    missing = sorted(admitted_ids - index.keys())
    if missing:
        raise InterpretationHandoffError(f"admitted registry file(s) not found: {', '.join(missing)}")
    return index


def _has_locator(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return bool(value) and all(isinstance(item, str) and item.strip() for item in value)
    return False


def _admit_claim(
    registry_entry: dict[str, Any],
    claim_id: str,
    source_policy: dict[str, Any],
) -> dict[str, Any]:
    registry = registry_entry["data"]
    claims = {row.get("claim_id"): row for row in registry.get("claims", []) if isinstance(row, dict)}
    claim = claims.get(claim_id)
    if not isinstance(claim, dict):
        raise InterpretationHandoffError(
            f"claim not found in admitted registry {registry.get('record_id')}: {claim_id}"
        )

    sources = {row.get("source_id"): row for row in registry.get("sources", []) if isinstance(row, dict)}
    required_any = set(source_policy.get("required_source_admission_any", []))
    forbidden = set(source_policy.get("forbidden_source_admission", []))
    source_refs = claim.get("source_refs", [])
    if not isinstance(source_refs, list) or not source_refs:
        raise InterpretationHandoffError(f"claim has no source_refs: {claim_id}")

    source_provenance: list[dict[str, Any]] = []
    for source_ref in source_refs:
        source = sources.get(source_ref)
        if not isinstance(source, dict):
            raise InterpretationHandoffError(f"claim source_ref is unresolved: {claim_id} -> {source_ref}")
        statuses = set(source.get("admission_status", [])) if isinstance(source.get("admission_status"), list) else set()
        if forbidden & statuses:
            raise InterpretationHandoffError(
                f"claim source is forbidden by production source policy: {claim_id} -> {source_ref}"
            )
        if required_any and not (required_any & statuses):
            raise InterpretationHandoffError(
                f"claim source lacks required production admission: {claim_id} -> {source_ref}"
            )
        if not _has_locator(source.get("locator")):
            raise InterpretationHandoffError(f"claim source lacks citation locator: {claim_id} -> {source_ref}")
        source_provenance.append(
            {
                "source_id": source_ref,
                "title": source.get("title"),
                "author_or_org": source.get("author_or_org"),
                "source_role": source.get("source_role"),
                "admission_status": source.get("admission_status", []),
                "locator": source.get("locator"),
                "edition": source.get("edition"),
                "immutable_revision": source.get("immutable_revision"),
                "publication_or_release_date": source.get("publication_or_release_date"),
            }
        )

    conflict_ids = [item for item in claim.get("conflict_group_ids", []) if isinstance(item, str)]
    conflicts_by_id = {
        row.get("conflict_group_id"): row
        for row in registry.get("conflict_groups", [])
        if isinstance(row, dict) and isinstance(row.get("conflict_group_id"), str)
    }
    conflicts = [conflicts_by_id[item] for item in conflict_ids if item in conflicts_by_id]

    return {
        "registry_record_id": registry.get("record_id"),
        "registry_path": registry_entry["path"],
        "claim_id": claim_id,
        "claim_type": claim.get("claim_type"),
        "normalized_statement": claim.get("normalized_statement"),
        "tradition_tags": claim.get("tradition_tags", []),
        "tradition_context_refs": claim.get("tradition_context_refs", []),
        "historical_context_refs": claim.get("historical_context_refs", []),
        "meta_context_refs": claim.get("meta_context_refs", []),
        "applies_to": claim.get("applies_to", []),
        "scope": claim.get("scope"),
        "confidence_status": claim.get("confidence_status"),
        "support_status": claim.get("support_status"),
        "cautions": claim.get("cautions", []),
        "source_refs": source_refs,
        "source_locator_refs": claim.get("source_locator_refs", []),
        "source_provenance": source_provenance,
        "conflicts": conflicts,
    }


def build_handoff(run: Any, request: Any, *, repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or _root_dir()
    admitted_run = _validate_run(run)
    normalized = normalize_request(request)
    manifest = _load_json(root / PRODUCTION_MANIFEST_PATH)
    if manifest.get("status") != "PRODUCTION_ADMITTED":
        raise InterpretationHandoffError("Astrology production manifest is not admitted")

    fact_index = _fact_index(admitted_run)
    selected_facts: list[dict[str, Any]] = []
    for ref in normalized["fact_refs"]:
        hit = fact_index.get(_ref_key(ref))
        if hit is None:
            raise InterpretationHandoffError(
                f"selected fact_ref does not exist in admitted reading run: {ref['bundle']} / {ref['fact_id']}"
            )
        selected_facts.append(hit)

    admitted_registry_ids = set(manifest.get("admitted_research_registries", []))
    registries = _registry_index(root, admitted_registry_ids)
    source_policy = manifest.get("source_policy", {})
    if not isinstance(source_policy, dict):
        raise InterpretationHandoffError("production source_policy is invalid")

    selected_claims: list[dict[str, Any]] = []
    used_conflicts: dict[str, dict[str, Any]] = {}
    disclosures: list[str] = []
    for claim_request in normalized["claim_requests"]:
        registry_id = claim_request["registry_record_id"]
        if registry_id not in admitted_registry_ids:
            raise InterpretationHandoffError(f"registry is not production-admitted: {registry_id}")
        registry_entry = registries[registry_id]
        admitted_claim = _admit_claim(registry_entry, claim_request["claim_id"], source_policy)
        admitted_claim["fact_refs"] = claim_request["fact_refs"]
        selected_claims.append(admitted_claim)
        for caution in admitted_claim.get("cautions", []):
            if isinstance(caution, str) and caution and caution not in disclosures:
                disclosures.append(caution)
        for conflict in admitted_claim.get("conflicts", []):
            conflict_id = conflict.get("conflict_group_id")
            if isinstance(conflict_id, str):
                used_conflicts[conflict_id] = conflict

    for bundle in admitted_run.get("fact_bundles", {}).values():
        if not isinstance(bundle, dict):
            continue
        if bundle.get("fact_source") == "user_supplied_structured_export":
            notice = "Selected Astrology facts include user-supplied structured data that this handoff did not independently recalculate."
            if notice not in disclosures:
                disclosures.append(notice)
        if bundle.get("birth_time_certainty") == "approximate":
            notice = "Birth time is approximate; time-sensitive houses and angles should be interpreted with corresponding uncertainty."
            if notice not in disclosures:
                disclosures.append(notice)

    if used_conflicts:
        disclosures.append("Registered interpretation conflicts are preserved below and must not be silently averaged or erased.")

    return {
        "schema_name": HANDOFF_SCHEMA_NAME,
        "schema_version": HANDOFF_SCHEMA_VERSION,
        "status": "ready_for_bounded_interpretation",
        "interpretation_allowed": True,
        "adapter": {
            "adapter_id": ADAPTER_ID,
            "adapter_version": ADAPTER_VERSION,
            "authority": "evidence_packaging_only",
            "semantic_selection_validated_not_authored": True,
            "final_prose_authority": False,
        },
        "owners": {
            "method_owner": "ASTROLOGY.md",
            "output_owner": "CHATGPT_OUTPUT.md",
            "production_manifest": PRODUCTION_MANIFEST_PATH,
            "request_schema": REQUEST_SCHEMA_PATH,
        },
        "question": {
            "question_id": normalized["question_id"],
            "text": normalized["question"],
            "focus": normalized["focus"],
            "exclusions": normalized["exclusions"],
        },
        "reading_run_identity": {
            "schema_name": admitted_run.get("schema_name"),
            "schema_version": admitted_run.get("schema_version"),
            "reading_mode": admitted_run.get("normalized_request", {}).get("reading_mode"),
            "subject_ref": admitted_run.get("normalized_request", {}).get("subject_ref"),
            "orchestrator": admitted_run.get("orchestrator"),
        },
        "selected_facts": selected_facts,
        "selected_claims": selected_claims,
        "conflicts": [used_conflicts[key] for key in sorted(used_conflicts)],
        "unsupported_factors": normalized["unsupported_factors"],
        "required_disclosures": disclosures,
        "synthesis_constraints": [
            "Use only selected facts and selected admitted claims for substantive Astrology interpretation.",
            "Treat normalized claim statements as source-backed symbolic material, not confirmed external reality.",
            "Preserve question exclusions, claim cautions, registered conflicts, and unsupported factors.",
            "Do not convert deterministic chart geometry or timing into guaranteed real-world outcomes.",
            "Final user-facing wording remains governed by ASTROLOGY.md and CHATGPT_OUTPUT.md.",
        ],
        "provenance": {
            "production_method_version": manifest.get("method_version"),
            "source_policy": source_policy,
            "admitted_registry_ids": sorted(admitted_registry_ids),
            "fact_bundle_sources": {
                name: {
                    "fact_source": bundle.get("fact_source"),
                    "calculation_verification": bundle.get("calculation_verification"),
                    "provider": bundle.get("provider"),
                }
                for name, bundle in admitted_run.get("fact_bundles", {}).items()
                if isinstance(bundle, dict)
            },
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate one Astrology reading run plus proposed evidence selection and emit a bounded interpretation handoff."
    )
    parser.add_argument("reading_run", type=Path, help="Path to astrology_reading_run@1.0.0 JSON")
    parser.add_argument("request", type=Path, help="Path to astrology_interpretation_request@1.0.0 JSON")
    args = parser.parse_args()
    try:
        run = json.loads(args.reading_run.read_text(encoding="utf-8"))
        request = json.loads(args.request.read_text(encoding="utf-8"))
        result = build_handoff(run, request)
    except (OSError, json.JSONDecodeError, InterpretationHandoffError) as exc:
        result = {
            "schema_name": HANDOFF_SCHEMA_NAME,
            "schema_version": HANDOFF_SCHEMA_VERSION,
            "status": "rejected",
            "interpretation_allowed": False,
            "error": str(exc),
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
