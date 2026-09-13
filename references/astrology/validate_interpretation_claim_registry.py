#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from typed_tradition_routing import TRADITION_DIMENSIONS, validate_taxonomy

SOURCE_ROLES = {"PRIMARY_TEXT", "SCHOLARLY_SECONDARY", "PRACTITIONER_REFERENCE", "REFERENCE_IMPLEMENTATION", "UNVERIFIED_WEB_SOURCE", "PROJECT_SYNTHESIS"}
ADMISSION = {"REJECTED", "REFERENCE_ONLY", "CLAIM_ELIGIBLE", "POLICY_PROVENANCE_ELIGIBLE", "CORPUS_STORAGE_ELIGIBLE", "PRODUCTION_ADMITTED"}
STORAGE = {"metadata_only", "metadata_plus_locator", "normalized_paraphrase", "short_excerpt_with_citation", "licensed_module_copy", "public_domain_text_copy", "project_authored_synthesis", "metadata_locator_normalized_paraphrase", "metadata_revision_normalized_paraphrase"}
INDEPENDENCE = {"independent_evidence", "likely_derivative", "explicit_derivative", "shared_upstream", "unknown", "primary_witness", "secondary_analysis_of_multiple_primary_sources", "derivative_practitioner_synthesis"}
SCHEMA_NAME = "interpretation_claim_registry"
SCHEMA_VERSION = "0.2.0-research"
LEGACY_SCHEMA_VERSION = "0.1.0-research"
SUPPORTED_SCHEMA_VERSIONS = {LEGACY_SCHEMA_VERSION, SCHEMA_VERSION}
LAYERS = {"L3", "L4"}
CONFIDENCE = {"supported", "qualified", "provisional", "conflicted", "unsupported"}
SUPPORT = {"single_source_supported", "multi_source_supported", "tradition_bounded", "qualified", "conflicted", "historical_only", "architecture_only", "unsupported"}
CONTEXT_FIELD_DIMENSIONS = {
    "tradition_context_refs": TRADITION_DIMENSIONS,
    "historical_context_refs": {"historical_context"},
    "meta_context_refs": {"meta_perspective"},
}
PRECONDITION_BOOLEAN_FIELDS = {"requires_l2_facts", "requires_l3_policy"}


def add(errors: list[dict[str, str]], code: str, path: str, message: str) -> None:
    errors.append({"code": code, "path": path, "message": message})


def aset(value: Any) -> set[str]:
    if isinstance(value, str):
        return {value}
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return set(value)
    return set()


def arr(value: Any, path: str, errors: list[dict[str, str]], nonempty: bool = False) -> list[Any]:
    if not isinstance(value, list):
        add(errors, "ARRAY_REQUIRED", path, "must be an array")
        return []
    if nonempty and not value:
        add(errors, "NONEMPTY_ARRAY_REQUIRED", path, "must not be empty")
    return value


def _context_index(taxonomy: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        row.get("context_id"): row
        for row in taxonomy.get("contexts", [])
        if isinstance(row, dict) and isinstance(row.get("context_id"), str)
    }


def _validate_context_refs(
    claim: dict[str, Any],
    claim_path: str,
    field: str,
    allowed_dimensions: set[str],
    contexts: dict[str, dict[str, Any]],
    errors: list[dict[str, str]],
    *,
    required: bool = False,
) -> None:
    if field not in claim:
        if required:
            add(errors, "TYPED_CONTEXT_FIELD_REQUIRED", f"{claim_path}.{field}", f"v0.2 registry requires explicit {field} array")
        return
    refs = claim.get(field)
    if not isinstance(refs, list) or not all(isinstance(ref, str) and ref for ref in refs):
        add(errors, "TYPED_CONTEXT_REFS_INVALID", f"{claim_path}.{field}", "must be a string array")
        return
    if len(refs) != len(set(refs)):
        add(errors, "TYPED_CONTEXT_REF_DUPLICATE", f"{claim_path}.{field}", "context refs must not contain duplicates")
    for index, ref in enumerate(refs):
        row = contexts.get(ref)
        path = f"{claim_path}.{field}[{index}]"
        if row is None:
            add(errors, "TYPED_CONTEXT_REF_UNKNOWN", path, f"unknown taxonomy context: {ref}")
        elif row.get("dimension") not in allowed_dimensions:
            allowed = ", ".join(sorted(allowed_dimensions))
            add(errors, "TYPED_CONTEXT_DIMENSION_INVALID", path, f"context {ref} must belong to: {allowed}")


def _validate_retrieval_preconditions(data: dict[str, Any], errors: list[dict[str, str]]) -> None:
    if "retrieval_preconditions" not in data:
        return
    value = data.get("retrieval_preconditions")
    if not isinstance(value, dict):
        add(errors, "RETRIEVAL_PRECONDITIONS_OBJECT_REQUIRED", "$.retrieval_preconditions", "must be an object")
        return
    for field in PRECONDITION_BOOLEAN_FIELDS:
        if field in value and not isinstance(value[field], bool):
            add(errors, "RETRIEVAL_PRECONDITION_BOOLEAN_REQUIRED", f"$.retrieval_preconditions.{field}", "must be boolean")


def validate_registry(data: Any, taxonomy: dict[str, Any] | None = None) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    if not isinstance(data, dict):
        add(errors, "ROOT_OBJECT_REQUIRED", "$", "registry must be an object")
        return errors

    for key in ("record_status", "record_kind", "record_id", "sources", "claims"):
        if key not in data:
            add(errors, "REQUIRED_FIELD_MISSING", f"$.{key}", "required field is missing")
    if data.get("record_status") != "REFERENCE-ONLY":
        add(errors, "RECORD_STATUS_INVALID", "$.record_status", "research registry must be REFERENCE-ONLY")
    if data.get("record_kind") != "interpretation_claim_family_registry":
        add(errors, "RECORD_KIND_INVALID", "$.record_kind", "must equal interpretation_claim_family_registry")

    versioned = "schema_name" in data or "schema_version" in data
    version = data.get("schema_version") if versioned else None
    v2 = version == SCHEMA_VERSION
    contexts: dict[str, dict[str, Any]] = {}
    if versioned:
        if data.get("schema_name") != SCHEMA_NAME:
            add(errors, "SCHEMA_NAME_INVALID", "$.schema_name", f"must equal {SCHEMA_NAME}")
        if version not in SUPPORTED_SCHEMA_VERSIONS:
            add(errors, "SCHEMA_VERSION_UNSUPPORTED", "$.schema_version", f"must be one of {sorted(SUPPORTED_SCHEMA_VERSIONS)}")
        if data.get("production_routable") is not False:
            add(errors, "PRODUCTION_ROUTABLE_EXPLICIT_FALSE_REQUIRED", "$.production_routable", "versioned research registry must explicitly set production_routable=false")
        if not isinstance(data.get("conflict_groups"), list):
            add(errors, "CONFLICT_GROUPS_REQUIRED", "$.conflict_groups", "versioned registry must declare conflict_groups array")
        privacy = data.get("privacy")
        if not isinstance(privacy, dict) or privacy.get("contains_real_birth_data") is not False:
            add(errors, "PRIVACY_FALSE_REQUIRED", "$.privacy.contains_real_birth_data", "versioned registry must explicitly declare contains_real_birth_data=false")
        _validate_retrieval_preconditions(data, errors)

    if v2:
        if taxonomy is None:
            add(errors, "TAXONOMY_REQUIRED_FOR_REGISTRY_V2", "$.taxonomy", "v0.2 typed registry validation requires taxonomy")
        else:
            taxonomy_errors = validate_taxonomy(taxonomy)
            if taxonomy_errors:
                add(errors, "TAXONOMY_INVALID_FOR_REGISTRY_V2", "$.taxonomy", "taxonomy failed deterministic validation")
            else:
                contexts = _context_index(taxonomy)

    if data.get("production_routable") is True:
        add(errors, "PRODUCTION_ROUTABLE_FORBIDDEN", "$.production_routable", "research registry cannot be production-routable")
    research_result = data.get("research_result")
    if isinstance(research_result, dict):
        if research_result.get("production_authority_granted") is True:
            add(errors, "PRODUCTION_AUTHORITY_FORBIDDEN", "$.research_result.production_authority_granted", "research registry cannot grant production authority")
        if research_result.get("scientific_predictive_validity_claimed") is True:
            add(errors, "SCIENTIFIC_VALIDITY_PROMOTION_FORBIDDEN", "$.research_result.scientific_predictive_validity_claimed", "claim registry cannot promote scientific predictive validity")
    privacy = data.get("privacy")
    if isinstance(privacy, dict) and privacy.get("contains_real_birth_data") is True:
        add(errors, "REAL_BIRTH_DATA_FORBIDDEN", "$.privacy.contains_real_birth_data", "source-evidence registry fixtures must not contain real birth data")

    sources = arr(data.get("sources"), "$.sources", errors, True)
    claims = arr(data.get("claims"), "$.claims", errors, True)
    conflicts = arr(data.get("conflict_groups", []), "$.conflict_groups", errors)

    source_by_id: dict[str, dict[str, Any]] = {}
    for index, source in enumerate(sources):
        path = f"$.sources[{index}]"
        if not isinstance(source, dict):
            add(errors, "SOURCE_OBJECT_REQUIRED", path, "source entry must be an object")
            continue
        source_id = source.get("source_id")
        if not isinstance(source_id, str) or not source_id:
            add(errors, "SOURCE_ID_REQUIRED", path + ".source_id", "non-empty source_id is required")
            continue
        if source_id in source_by_id:
            add(errors, "SOURCE_ID_DUPLICATE", path + ".source_id", "source_id must be unique")
        source_by_id[source_id] = source
        roles = aset(source.get("source_role"))
        if not roles:
            add(errors, "SOURCE_ROLE_REQUIRED", path + ".source_role", "source_role must be string or string array")
        for value in roles - SOURCE_ROLES:
            add(errors, "SOURCE_ROLE_INVALID", path + ".source_role", f"unsupported source role: {value}")
        admission = aset(source.get("admission_status", source.get("admission_state")))
        if not admission:
            add(errors, "ADMISSION_STATUS_REQUIRED", path, "admission_state or admission_status is required")
        for value in admission - ADMISSION:
            add(errors, "ADMISSION_STATUS_INVALID", path, f"unsupported admission status: {value}")
        if "PRODUCTION_ADMITTED" in admission:
            add(errors, "PRODUCTION_ADMISSION_FORBIDDEN", path, "research validator forbids PRODUCTION_ADMITTED")
        if "UNVERIFIED_WEB_SOURCE" in roles and admission & {"CLAIM_ELIGIBLE", "POLICY_PROVENANCE_ELIGIBLE", "PRODUCTION_ADMITTED"}:
            add(errors, "UNVERIFIED_WEB_PROMOTION_FORBIDDEN", path, "unverified web source cannot be claim/policy/production admitted")
        storage = aset(source.get("storage_mode"))
        if not storage:
            add(errors, "STORAGE_MODE_REQUIRED", path + ".storage_mode", "storage_mode must be declared")
        for value in storage - STORAGE:
            add(errors, "STORAGE_MODE_INVALID", path + ".storage_mode", f"unsupported storage mode: {value}")
        independence = source.get("independence_status")
        if independence is not None and independence not in INDEPENDENCE:
            add(errors, "INDEPENDENCE_STATUS_INVALID", path + ".independence_status", f"unsupported independence status: {independence}")
        if versioned:
            if "admission_state" in source:
                add(errors, "LEGACY_SOURCE_FIELD_FORBIDDEN", path + ".admission_state", "versioned registry must use admission_status")
            if "admission_status" not in source:
                add(errors, "CANONICAL_ADMISSION_STATUS_REQUIRED", path + ".admission_status", "versioned registry requires admission_status")
            if not isinstance(source.get("admission_status"), list):
                add(errors, "CANONICAL_ADMISSION_STATUS_ARRAY_REQUIRED", path + ".admission_status", "versioned admission_status must be an array")
            if not isinstance(source.get("storage_mode"), list):
                add(errors, "CANONICAL_STORAGE_MODE_ARRAY_REQUIRED", path + ".storage_mode", "versioned storage_mode must be an array")
            if "author" in source:
                add(errors, "LEGACY_SOURCE_FIELD_FORBIDDEN", path + ".author", "versioned registry must use author_or_org")
            if "revision" in source:
                add(errors, "LEGACY_SOURCE_FIELD_FORBIDDEN", path + ".revision", "versioned registry must use immutable_revision")
            if independence is None:
                add(errors, "CANONICAL_INDEPENDENCE_STATUS_REQUIRED", path + ".independence_status", "versioned registry requires independence_status")

    for index, source in enumerate(sources):
        if not isinstance(source, dict) or not isinstance(source.get("source_id"), str):
            continue
        source_id = source["source_id"]
        refs = source.get("upstream_source_refs", [])
        if refs is None:
            refs = []
        if not isinstance(refs, list) or not all(isinstance(ref, str) for ref in refs):
            add(errors, "UPSTREAM_SOURCE_REFS_INVALID", f"$.sources[{index}].upstream_source_refs", "must be string array")
            continue
        for ref in refs:
            if ref == source_id:
                add(errors, "UPSTREAM_SOURCE_SELF_REFERENCE", f"$.sources[{index}].upstream_source_refs", "source cannot cite itself as upstream")
            elif ref not in source_by_id:
                add(errors, "UPSTREAM_SOURCE_REF_UNKNOWN", f"$.sources[{index}].upstream_source_refs", f"unknown upstream source: {ref}")

    conflict_by_id: dict[str, dict[str, Any]] = {}
    for index, group in enumerate(conflicts):
        path = f"$.conflict_groups[{index}]"
        if not isinstance(group, dict):
            add(errors, "CONFLICT_OBJECT_REQUIRED", path, "conflict group must be an object")
            continue
        conflict_id = group.get("conflict_group_id")
        if not isinstance(conflict_id, str) or not conflict_id:
            add(errors, "CONFLICT_ID_REQUIRED", path + ".conflict_group_id", "non-empty conflict_group_id is required")
            continue
        if conflict_id in conflict_by_id:
            add(errors, "CONFLICT_ID_DUPLICATE", path + ".conflict_group_id", "conflict_group_id must be unique")
        conflict_by_id[conflict_id] = group

    claim_by_id: dict[str, dict[str, Any]] = {}
    for index, claim in enumerate(claims):
        path = f"$.claims[{index}]"
        if not isinstance(claim, dict):
            add(errors, "CLAIM_OBJECT_REQUIRED", path, "claim must be an object")
            continue
        claim_id = claim.get("claim_id")
        if not isinstance(claim_id, str) or not claim_id:
            add(errors, "CLAIM_ID_REQUIRED", path + ".claim_id", "non-empty claim_id is required")
            continue
        if claim_id in claim_by_id:
            add(errors, "CLAIM_ID_DUPLICATE", path + ".claim_id", "claim_id must be unique")
        claim_by_id[claim_id] = claim
        if claim.get("layer") not in LAYERS:
            add(errors, "CLAIM_LAYER_INVALID", path + ".layer", "claim layer must be L3 or L4")
        statement = claim.get("normalized_statement", claim.get("statement"))
        if not isinstance(statement, str) or not statement.strip():
            add(errors, "CLAIM_STATEMENT_REQUIRED", path, "statement or normalized_statement is required")
        source_refs = arr(claim.get("source_refs"), path + ".source_refs", errors, True)
        string_source_refs = [ref for ref in source_refs if isinstance(ref, str)]
        if len(string_source_refs) != len(source_refs):
            add(errors, "CLAIM_SOURCE_REF_TYPE_INVALID", path + ".source_refs", "source_refs must contain strings only")
        for ref in string_source_refs:
            if ref not in source_by_id:
                add(errors, "CLAIM_SOURCE_REF_UNKNOWN", path + ".source_refs", f"unknown source: {ref}")
        confidence = claim.get("confidence_status", claim.get("confidence"))
        if confidence is not None and confidence not in CONFIDENCE:
            add(errors, "CLAIM_CONFIDENCE_INVALID", path, f"unsupported confidence: {confidence}")
        support = claim.get("support_status")
        if support is not None and support not in SUPPORT:
            add(errors, "CLAIM_SUPPORT_STATUS_INVALID", path + ".support_status", f"unsupported support status: {support}")
        if versioned:
            for legacy, canonical in (("statement", "normalized_statement"), ("confidence", "confidence_status"), ("conflict_group_refs", "conflict_group_ids")):
                if legacy in claim:
                    add(errors, "LEGACY_CLAIM_FIELD_FORBIDDEN", path + "." + legacy, f"versioned registry must use {canonical}")
            if not isinstance(claim.get("normalized_statement"), str) or not claim.get("normalized_statement", "").strip():
                add(errors, "CANONICAL_STATEMENT_REQUIRED", path + ".normalized_statement", "versioned registry requires normalized_statement")
            if claim.get("confidence_status") not in CONFIDENCE:
                add(errors, "CANONICAL_CONFIDENCE_REQUIRED", path + ".confidence_status", "versioned registry requires canonical confidence_status")
            if claim.get("support_status") not in SUPPORT:
                add(errors, "CANONICAL_SUPPORT_STATUS_REQUIRED", path + ".support_status", "versioned registry requires canonical support_status")
            if not isinstance(claim.get("conflict_group_ids"), list):
                add(errors, "CANONICAL_CONFLICT_IDS_REQUIRED", path + ".conflict_group_ids", "versioned registry requires conflict_group_ids array")
        if v2 and contexts:
            for field, dimensions in CONTEXT_FIELD_DIMENSIONS.items():
                _validate_context_refs(claim, path, field, dimensions, contexts, errors, required=(field == "tradition_context_refs"))
        elif v2 and "tradition_context_refs" not in claim:
            add(errors, "TYPED_CONTEXT_FIELD_REQUIRED", path + ".tradition_context_refs", "v0.2 registry requires explicit tradition_context_refs array")

        conflict_refs = claim.get("conflict_group_ids", claim.get("conflict_group_refs", []))
        if conflict_refs is None:
            conflict_refs = []
        if not isinstance(conflict_refs, list) or not all(isinstance(ref, str) for ref in conflict_refs):
            add(errors, "CLAIM_CONFLICT_REFS_INVALID", path, "conflict refs must be string array")
        else:
            for ref in conflict_refs:
                if ref not in conflict_by_id:
                    add(errors, "CLAIM_CONFLICT_REF_UNKNOWN", path, f"unknown conflict group: {ref}")

        admissions = [aset(source_by_id[ref].get("admission_status", source_by_id[ref].get("admission_state"))) for ref in string_source_refs if ref in source_by_id]
        if string_source_refs and admissions and all("REFERENCE_ONLY" in admission and len(admission) == 1 for admission in admissions):
            if confidence == "supported" or support in {"single_source_supported", "multi_source_supported"}:
                add(errors, "REFERENCE_ONLY_AUTHORITY_PROMOTION", path, "REFERENCE_ONLY sources cannot by themselves support an unqualified supported claim")
        if support == "multi_source_supported":
            if len(set(string_source_refs)) < 2:
                add(errors, "MULTI_SOURCE_COUNT_INSUFFICIENT", path + ".source_refs", "multi_source_supported requires >=2 distinct sources")
            roots: set[str] = set()
            for ref in set(string_source_refs):
                source = source_by_id.get(ref, {})
                upstream = source.get("upstream_source_refs", [])
                if isinstance(upstream, list) and upstream:
                    roots.update(item for item in upstream if isinstance(item, str))
                else:
                    roots.add(ref)
            if len(roots) < 2:
                add(errors, "MULTI_SOURCE_INDEPENDENCE_INSUFFICIENT", path + ".source_refs", "multi_source_supported requires >=2 evidence roots")

    for index, group in enumerate(conflicts):
        if not isinstance(group, dict):
            continue
        refs = group.get("claim_refs")
        if refs is None:
            continue
        if not isinstance(refs, list) or not all(isinstance(ref, str) for ref in refs):
            add(errors, "CONFLICT_CLAIM_REFS_INVALID", f"$.conflict_groups[{index}].claim_refs", "claim_refs must be string array")
            continue
        for ref in refs:
            if ref not in claim_by_id:
                add(errors, "CONFLICT_CLAIM_REF_UNKNOWN", f"$.conflict_groups[{index}].claim_refs", f"unknown claim: {ref}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--taxonomy", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    try:
        taxonomy = json.loads(args.taxonomy.read_text(encoding="utf-8")) if args.taxonomy else None
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"valid": False, "errors": [{"code": "TAXONOMY_LOAD_ERROR", "path": "$.taxonomy", "message": str(exc)}]}, ensure_ascii=False, indent=2))
        return 2
    output = []
    failed = False
    for path in args.paths:
        try:
            errors = validate_registry(json.loads(path.read_text(encoding="utf-8")), taxonomy)
        except (OSError, json.JSONDecodeError) as exc:
            errors = [{"code": "REGISTRY_LOAD_ERROR", "path": "$", "message": str(exc)}]
        valid = not errors
        failed |= not valid
        output.append({"path": str(path), "valid": valid, "errors": errors})
    if args.as_json:
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        for result in output:
            print(f"{result['path']}: {'PASS' if result['valid'] else 'FAIL'}")
            for error in result["errors"]:
                print(f"  {error['code']} {error['path']}: {error['message']}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())