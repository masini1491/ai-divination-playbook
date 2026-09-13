#!/usr/bin/env python3
"""Deterministic research selector for versioned Astrology interpretation registries."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from typed_tradition_routing import TRADITION_DIMENSIONS, canonical_tradition_refs_for_claim, validate_taxonomy
from validate_interpretation_claim_registry import validate_registry

REGISTRY_SCHEMA = "interpretation_claim_registry"
REGISTRY_VERSION = "0.2.0-research"
LEGACY_REGISTRY_VERSION = "0.1.0-research"
SUPPORTED_REGISTRY_VERSIONS = {LEGACY_REGISTRY_VERSION, REGISTRY_VERSION}
BUNDLE_SCHEMA = "interpretation_retrieval_provenance_bundle"
BUNDLE_VERSION = "0.2.0-research"
LEGACY_BUNDLE_VERSION = "0.1.0-research"

CLAIM_ELIGIBLE = {"CLAIM_ELIGIBLE", "POLICY_PROVENANCE_ELIGIBLE"}
QUALIFIED_CONFIDENCE = {"qualified", "provisional", "conflicted"}
QUALIFIED_SUPPORT = {"tradition_bounded", "qualified", "architecture_only", "conflicted"}
TYPED_SYNTHESIS_MODES = {"synthesis:single_tradition", "synthesis:parallel_comparison", "synthesis:explicit_blend"}


def _as_set(value: Any) -> set[str]:
    if isinstance(value, str):
        return {value}
    if isinstance(value, list):
        return {item for item in value if isinstance(item, str)}
    return set()


def _has_locator(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return bool(value) and all(isinstance(item, str) and item.strip() for item in value)
    return False


def _context_index(taxonomy: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        row.get("context_id"): row
        for row in taxonomy.get("contexts", [])
        if isinstance(row, dict) and isinstance(row.get("context_id"), str)
    }


def _typed_query(query: dict[str, Any]) -> bool:
    return bool(query.get("tradition_context_refs_any")) or "synthesis_mode" in query


def validate_query(query: Any, taxonomy: dict[str, Any] | None = None) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    if not isinstance(query, dict):
        return [{"code": "QUERY_OBJECT_REQUIRED", "path": "$", "message": "query must be an object"}]
    if not isinstance(query.get("query_id"), str) or not query["query_id"].strip():
        errors.append({"code": "QUERY_ID_REQUIRED", "path": "$.query_id", "message": "non-empty query_id is required"})

    typed = _typed_query(query)
    array_keys = ["claim_types", "applies_to_all", "l2_fact_refs", "l3_policy_refs"]
    array_keys.append("tradition_context_refs_any" if typed else "tradition_tags_any")
    for key in array_keys:
        if key in query and (not isinstance(query[key], list) or not all(isinstance(item, str) for item in query[key])):
            errors.append({"code": "QUERY_STRING_ARRAY_REQUIRED", "path": f"$.{key}", "message": "must be a string array"})
    if not isinstance(query.get("claim_types"), list) or not query.get("claim_types"):
        errors.append({"code": "QUERY_CLAIM_TYPES_REQUIRED", "path": "$.claim_types", "message": "at least one claim type is required"})

    for key in ("requires_l2_facts", "requires_l3_policy", "allow_reference_only_qualified", "include_registry_guardrails"):
        if key in query and not isinstance(query[key], bool):
            errors.append({"code": "QUERY_BOOLEAN_REQUIRED", "path": f"$.{key}", "message": "must be boolean"})

    if typed:
        if query.get("tradition_tags_any"):
            errors.append({"code": "TRADITION_SELECTOR_MIXED", "path": "$", "message": "typed refs and legacy flat tags must not be mixed"})
        refs = query.get("tradition_context_refs_any", [])
        mode = query.get("synthesis_mode")
        if not refs:
            errors.append({"code": "TYPED_TRADITION_CONTEXT_REQUIRED", "path": "$.tradition_context_refs_any", "message": "typed retrieval requires at least one tradition context"})
        if mode not in TYPED_SYNTHESIS_MODES:
            errors.append({"code": "SYNTHESIS_MODE_INVALID", "path": "$.synthesis_mode", "message": "unsupported synthesis mode"})
        if mode == "synthesis:single_tradition" and len(refs) != 1:
            errors.append({"code": "SINGLE_TRADITION_CARDINALITY_INVALID", "path": "$.tradition_context_refs_any", "message": "single-tradition retrieval requires exactly one context"})
        if mode in {"synthesis:parallel_comparison", "synthesis:explicit_blend"} and len(refs) < 2:
            errors.append({"code": "MULTI_TRADITION_CARDINALITY_INVALID", "path": "$.tradition_context_refs_any", "message": "multi-tradition retrieval requires at least two contexts"})
        if taxonomy is None:
            errors.append({"code": "TAXONOMY_REQUIRED_FOR_TYPED_QUERY", "path": "$.taxonomy", "message": "typed retrieval requires taxonomy"})
        elif validate_taxonomy(taxonomy):
            errors.append({"code": "TAXONOMY_INVALID", "path": "$.taxonomy", "message": "taxonomy failed deterministic validation"})
        else:
            contexts = _context_index(taxonomy)
            for index, ref in enumerate(refs):
                row = contexts.get(ref)
                if row is None:
                    errors.append({"code": "TRADITION_CONTEXT_UNKNOWN", "path": f"$.tradition_context_refs_any[{index}]", "message": f"unknown context: {ref}"})
                elif row.get("dimension") not in TRADITION_DIMENSIONS:
                    errors.append({"code": "TRADITION_CONTEXT_DIMENSION_INVALID", "path": f"$.tradition_context_refs_any[{index}]", "message": "selector must be doctrinal_lineage or interpretive_school"})
    return errors


def _base_bundle(registry: dict[str, Any], query: dict[str, Any] | Any) -> dict[str, Any]:
    typed = isinstance(query, dict) and _typed_query(query)
    return {
        "schema_name": BUNDLE_SCHEMA,
        "schema_version": BUNDLE_VERSION if typed else LEGACY_BUNDLE_VERSION,
        "record_status": "REFERENCE-ONLY",
        "production_routable": False,
        "query_id": query.get("query_id") if isinstance(query, dict) else None,
        "registry_record_id": registry.get("record_id") if isinstance(registry, dict) else None,
        "registry_schema_name": registry.get("schema_name") if isinstance(registry, dict) else None,
        "registry_schema_version": registry.get("schema_version") if isinstance(registry, dict) else None,
        "retrieval_status": None,
        "selected_claim_ids": [],
        "claims": [],
        "conflicts": [],
        "guardrails": [],
        "excluded": [],
        "tradition_provenance": {},
        "precondition_provenance": {},
    }


def retrieve_claims(registry: dict[str, Any], query: dict[str, Any], taxonomy: dict[str, Any] | None = None) -> dict[str, Any]:
    bundle = _base_bundle(registry, query)
    query_errors = validate_query(query, taxonomy)
    if query_errors:
        bundle["retrieval_status"] = "invalid_query"
        bundle["errors"] = query_errors
        return bundle

    if not isinstance(registry, dict):
        bundle["retrieval_status"] = "registry_not_research_safe"
        bundle["errors"] = [{"code": "ROOT_OBJECT_REQUIRED", "path": "$", "message": "registry must be an object"}]
        return bundle
    if registry.get("schema_name") != REGISTRY_SCHEMA or registry.get("schema_version") not in SUPPORTED_REGISTRY_VERSIONS:
        bundle["retrieval_status"] = "registry_not_research_safe"
        bundle["errors"] = [{"code": "REGISTRY_SCHEMA_UNSUPPORTED", "path": "$", "message": f"registry must be {REGISTRY_SCHEMA} with version in {sorted(SUPPORTED_REGISTRY_VERSIONS)}"}]
        return bundle

    registry_taxonomy = taxonomy if registry.get("schema_version") == REGISTRY_VERSION else None
    registry_errors = validate_registry(registry, registry_taxonomy)
    if registry_errors:
        bundle["retrieval_status"] = "registry_not_research_safe"
        bundle["errors"] = registry_errors
        return bundle

    registry_preconditions = registry.get("retrieval_preconditions", {})
    if not isinstance(registry_preconditions, dict):
        registry_preconditions = {}
    query_requires_l2 = bool(query.get("requires_l2_facts"))
    query_requires_l3 = bool(query.get("requires_l3_policy"))
    registry_requires_l2 = bool(registry_preconditions.get("requires_l2_facts"))
    registry_requires_l3 = bool(registry_preconditions.get("requires_l3_policy"))
    effective_requires_l2 = query_requires_l2 or registry_requires_l2
    effective_requires_l3 = query_requires_l3 or registry_requires_l3
    bundle["precondition_provenance"] = {
        "query_requires_l2_facts": query_requires_l2,
        "query_requires_l3_policy": query_requires_l3,
        "registry_requires_l2_facts": registry_requires_l2,
        "registry_requires_l3_policy": registry_requires_l3,
        "effective_requires_l2_facts": effective_requires_l2,
        "effective_requires_l3_policy": effective_requires_l3,
    }

    failures: list[str] = []
    if effective_requires_l2 and not query.get("l2_fact_refs"):
        failures.append("l2_fact_refs_required")
    if effective_requires_l3 and not query.get("l3_policy_refs"):
        failures.append("l3_policy_refs_required")
    if failures:
        bundle["retrieval_status"] = "precondition_failed"
        bundle["precondition_failures"] = failures
        return bundle

    sources = {source.get("source_id"): source for source in registry.get("sources", []) if isinstance(source, dict) and isinstance(source.get("source_id"), str)}
    conflicts = {group.get("conflict_group_id"): group for group in registry.get("conflict_groups", []) if isinstance(group, dict) and isinstance(group.get("conflict_group_id"), str)}

    requested_types = set(query["claim_types"])
    requested_traditions = set(query.get("tradition_tags_any", []))
    requested_typed = set(query.get("tradition_context_refs_any", []))
    required_applicability = set(query.get("applies_to_all", []))
    allow_reference_only = bool(query.get("allow_reference_only_qualified"))
    typed = bool(requested_typed)

    selected: list[dict[str, Any]] = []
    excluded: list[dict[str, str]] = []
    for claim in registry.get("claims", []):
        if not isinstance(claim, dict) or not isinstance(claim.get("claim_id"), str):
            continue
        claim_id = claim["claim_id"]
        if claim.get("claim_type") not in requested_types:
            excluded.append({"claim_id": claim_id, "reason": "claim_type_mismatch"})
            continue

        claim_typed = canonical_tradition_refs_for_claim(claim, taxonomy) if typed and taxonomy is not None else set()
        if typed and not (claim_typed & requested_typed):
            excluded.append({"claim_id": claim_id, "reason": "tradition_context_mismatch"})
            continue
        claim_traditions = _as_set(claim.get("tradition_tags"))
        if not typed and requested_traditions and not (claim_traditions & requested_traditions):
            excluded.append({"claim_id": claim_id, "reason": "tradition_mismatch"})
            continue

        claim_applicability = _as_set(claim.get("applies_to"))
        if required_applicability and not required_applicability.issubset(claim_applicability):
            excluded.append({"claim_id": claim_id, "reason": "applicability_mismatch"})
            continue

        source_refs = [ref for ref in claim.get("source_refs", []) if isinstance(ref, str)]
        resolved_sources = [sources[ref] for ref in source_refs if ref in sources]
        if not source_refs or len(resolved_sources) != len(source_refs):
            excluded.append({"claim_id": claim_id, "reason": "source_ref_unresolved"})
            continue

        admission_sets = [_as_set(source.get("admission_status")) for source in resolved_sources]
        eligible_count = sum(bool(statuses & CLAIM_ELIGIBLE) for statuses in admission_sets)
        reference_only_count = sum(statuses == {"REFERENCE_ONLY"} for statuses in admission_sets)
        qualified_claim = claim.get("confidence_status") in QUALIFIED_CONFIDENCE and claim.get("support_status") in QUALIFIED_SUPPORT
        if eligible_count == len(resolved_sources):
            admission_mode = "claim_eligible"
        elif eligible_count > 0 and reference_only_count > 0 and allow_reference_only and qualified_claim:
            admission_mode = "mixed_claim_eligible_and_reference_only"
        elif reference_only_count == len(resolved_sources) and allow_reference_only and qualified_claim:
            admission_mode = "qualified_reference_only"
        else:
            excluded.append({"claim_id": claim_id, "reason": "source_admission_insufficient"})
            continue

        source_provenance: list[dict[str, Any]] = []
        citation_ready = True
        for source in resolved_sources:
            locator = source.get("locator")
            if not _has_locator(locator):
                citation_ready = False
            source_provenance.append({
                "source_id": source["source_id"], "title": source.get("title"), "author_or_org": source.get("author_or_org"),
                "source_role": source.get("source_role"), "admission_status": source.get("admission_status"), "locator": locator,
                "edition": source.get("edition"), "immutable_revision": source.get("immutable_revision"),
                "publication_or_release_date": source.get("publication_or_release_date"), "license_status": source.get("license_status"),
                "copyright_status": source.get("copyright_status"),
            })

        selected.append({
            "claim_id": claim_id,
            "layer": claim.get("layer"),
            "claim_type": claim.get("claim_type"),
            "normalized_statement": claim.get("normalized_statement"),
            "tradition_tags": claim.get("tradition_tags", []),
            "tradition_context_refs": sorted(claim_typed) if typed else list(claim.get("tradition_context_refs", [])),
            "applies_to": claim.get("applies_to", []),
            "scope": claim.get("scope"),
            "confidence_status": claim.get("confidence_status"),
            "support_status": claim.get("support_status"),
            "cautions": claim.get("cautions", []),
            "source_refs": source_refs,
            "source_locator_refs": claim.get("source_locator_refs", []),
            "source_admission_mode": admission_mode,
            "citation_ready": citation_ready,
            "source_provenance": source_provenance,
            "conflict_group_ids": claim.get("conflict_group_ids", []),
        })

    bundle["selected_claim_ids"] = [claim["claim_id"] for claim in selected]
    bundle["claims"] = selected
    bundle["excluded"] = excluded

    selected_ids = set(bundle["selected_claim_ids"])
    used_conflict_ids = sorted({conflict_id for claim in selected for conflict_id in claim.get("conflict_group_ids", []) if isinstance(conflict_id, str)})
    used_conflicts: list[dict[str, Any]] = []
    for conflict_id in used_conflict_ids:
        group = conflicts.get(conflict_id)
        if not group:
            continue
        all_claim_refs = [ref for ref in group.get("claim_refs", []) if isinstance(ref, str)]
        used_conflicts.append({
            "conflict_group_id": conflict_id,
            "conflict_class": group.get("conflict_class", group.get("conflict_types", [])),
            "resolution_status": group.get("resolution_status"),
            "resolution_note": group.get("resolution_note"),
            "selected_claim_refs": [ref for ref in all_claim_refs if ref in selected_ids],
            "external_claim_refs": [ref for ref in all_claim_refs if ref not in selected_ids],
        })
    bundle["conflicts"] = used_conflicts
    if query.get("include_registry_guardrails"):
        bundle["guardrails"] = list(registry.get("non_admitted_claims", []))

    if not selected:
        bundle["retrieval_status"] = "no_match"
    elif all(claim["citation_ready"] for claim in selected):
        bundle["retrieval_status"] = "citation_ready"
    else:
        bundle["retrieval_status"] = "provenance_incomplete"

    if typed:
        covered = sorted({ref for claim in selected for ref in claim.get("tradition_context_refs", []) if ref in requested_typed})
        missing = [ref for ref in query.get("tradition_context_refs_any", []) if ref not in covered]
        bundle["tradition_provenance"] = {
            "requested_tradition_contexts": list(query.get("tradition_context_refs_any", [])),
            "requested_synthesis_mode": query.get("synthesis_mode"),
            "covered_tradition_contexts": covered,
            "missing_tradition_contexts": missing,
        }
        if missing and query.get("synthesis_mode") in {"synthesis:parallel_comparison", "synthesis:explicit_blend"}:
            bundle["retrieval_status"] = "tradition_coverage_incomplete"
            bundle["guardrails"].append("Requested multi-tradition synthesis is incomplete; do not silently substitute another tradition.")

    bundle["synthesis_provenance"] = {
        "l2_fact_refs": list(query.get("l2_fact_refs", [])),
        "l3_policy_refs": list(query.get("l3_policy_refs", [])),
        "claim_refs": list(bundle["selected_claim_ids"]),
        "conflict_group_refs": [group["conflict_group_id"] for group in used_conflicts],
        "tradition_context_refs": list(query.get("tradition_context_refs_any", [])),
        "synthesis_mode": query.get("synthesis_mode"),
        "registry_retrieval_preconditions": dict(registry_preconditions),
        "effective_requires_l2_facts": effective_requires_l2,
        "effective_requires_l3_policy": effective_requires_l3,
    }
    return bundle


def main() -> int:
    parser = argparse.ArgumentParser(description="Retrieve source-backed Astrology interpretation claims from a versioned research registry.")
    parser.add_argument("registry", type=Path)
    parser.add_argument("query", type=Path)
    parser.add_argument("--taxonomy", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    try:
        registry = json.loads(args.registry.read_text(encoding="utf-8"))
        query = json.loads(args.query.read_text(encoding="utf-8"))
        taxonomy = json.loads(args.taxonomy.read_text(encoding="utf-8")) if args.taxonomy else None
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"retrieval_status": "load_error", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2
    result = retrieve_claims(registry, query, taxonomy)
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"{result['query_id']}: {result['retrieval_status']}")
        for claim_id in result["selected_claim_ids"]:
            print(f"  {claim_id}")
    return 0 if result["retrieval_status"] in {"citation_ready", "no_match", "precondition_failed", "tradition_coverage_incomplete"} else 1


if __name__ == "__main__":
    raise SystemExit(main())