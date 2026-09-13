#!/usr/bin/env python3
"""REFERENCE-ONLY typed tradition routing adapter for Astrology research.

This module bridges legacy claim ``tradition_tags`` and the research tradition
Taxonomy without silently promoting broad discovery tags into doctrine selectors.
It does not perform astrology interpretation or production routing.
"""
from __future__ import annotations

from typing import Any

ALLOWED_RESOLUTION_STATUS = {
    "explicit",
    "inferred_from_named_school",
    "unspecified",
    "ambiguous",
    "unsupported",
}
ALLOWED_SYNTHESIS_MODES = {
    "synthesis:single_tradition",
    "synthesis:parallel_comparison",
    "synthesis:explicit_blend",
}
TRADITION_DIMENSIONS = {"doctrinal_lineage", "interpretive_school"}


def _mapping_index(taxonomy: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        row.get("tag"): row
        for row in taxonomy.get("legacy_tag_mappings", [])
        if isinstance(row, dict) and isinstance(row.get("tag"), str)
    }


def _context_index(taxonomy: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        row.get("context_id"): row
        for row in taxonomy.get("contexts", [])
        if isinstance(row, dict) and isinstance(row.get("context_id"), str)
    }


def validate_taxonomy(taxonomy: Any) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    if not isinstance(taxonomy, dict):
        return [{"code": "TAXONOMY_OBJECT_REQUIRED", "path": "$", "message": "taxonomy must be an object"}]
    if taxonomy.get("schema_name") != "astrology_tradition_taxonomy":
        errors.append({"code": "TAXONOMY_SCHEMA_INVALID", "path": "$.schema_name", "message": "unexpected taxonomy schema"})
    if taxonomy.get("schema_version") != "0.1.0-research":
        errors.append({"code": "TAXONOMY_VERSION_INVALID", "path": "$.schema_version", "message": "unsupported taxonomy version"})
    if taxonomy.get("record_status") != "REFERENCE-ONLY" or taxonomy.get("production_routable") is not False:
        errors.append({"code": "TAXONOMY_RESEARCH_GUARD_FAILED", "path": "$", "message": "taxonomy must remain REFERENCE-ONLY and non-production-routable"})

    contexts = _context_index(taxonomy)
    for context_id, row in contexts.items():
        parent = row.get("parent_id")
        if parent is not None and parent not in contexts:
            errors.append({"code": "TAXONOMY_PARENT_UNKNOWN", "path": f"$.contexts[{context_id}]", "message": f"unknown parent: {parent}"})
        seen: set[str] = set()
        cursor = context_id
        while cursor in contexts:
            if cursor in seen:
                errors.append({"code": "TAXONOMY_PARENT_CYCLE", "path": f"$.contexts[{context_id}]", "message": "parent cycle detected"})
                break
            seen.add(cursor)
            parent = contexts[cursor].get("parent_id")
            if not isinstance(parent, str):
                break
            cursor = parent

    mappings = _mapping_index(taxonomy)
    for tag, row in mappings.items():
        for ref in row.get("context_refs", []):
            if ref not in contexts:
                errors.append({"code": "TAXONOMY_MAPPING_REF_UNKNOWN", "path": f"$.legacy_tag_mappings[{tag}]", "message": f"unknown context ref: {ref}"})
    return errors


def canonical_tradition_refs_for_claim(claim: dict[str, Any], taxonomy: dict[str, Any]) -> set[str]:
    explicit = claim.get("tradition_context_refs")
    if isinstance(explicit, list):
        return {value for value in explicit if isinstance(value, str)}

    mappings = _mapping_index(taxonomy)
    contexts = _context_index(taxonomy)
    refs: set[str] = set()
    for tag in claim.get("tradition_tags", []):
        if not isinstance(tag, str):
            continue
        mapping = mappings.get(tag)
        if not mapping or mapping.get("mapping_status") != "canonical":
            continue
        for ref in mapping.get("context_refs", []):
            row = contexts.get(ref)
            if row and row.get("dimension") in TRADITION_DIMENSIONS:
                refs.add(ref)
    return refs


def resolve_tradition_request(request: dict[str, Any], taxonomy: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize one already-understood tradition intent.

    ``requested_labels`` contains user-facing legacy/named labels already identified
    by an upstream language-understanding stage. This function only applies the
    deterministic taxonomy contract.
    """
    result = {
        "tradition_resolution_status": None,
        "requested_tradition_contexts": [],
        "requested_synthesis_mode": None,
        "executable": False,
        "reason": None,
    }
    if validate_taxonomy(taxonomy):
        result["tradition_resolution_status"] = "unsupported"
        result["reason"] = "taxonomy_invalid"
        return result

    labels = request.get("requested_labels", [])
    if not isinstance(labels, list) or not all(isinstance(value, str) and value for value in labels):
        result["tradition_resolution_status"] = "unsupported"
        result["reason"] = "requested_labels_invalid"
        return result

    mappings = _mapping_index(taxonomy)
    contexts = _context_index(taxonomy)
    refs: list[str] = []
    status = "explicit"

    if not labels:
        result["tradition_resolution_status"] = "unspecified"
        result["reason"] = "no_silent_default_tradition"
        return result

    for label in labels:
        if label in contexts:
            row = contexts[label]
            if row.get("dimension") not in TRADITION_DIMENSIONS:
                result["tradition_resolution_status"] = "unsupported"
                result["reason"] = "non_tradition_context_cannot_select_doctrine"
                return result
            refs.append(label)
            continue

        mapping = mappings.get(label)
        if not mapping:
            result["tradition_resolution_status"] = "unsupported"
            result["reason"] = f"unknown_tradition_label:{label}"
            return result
        mapping_status = mapping.get("mapping_status")
        if mapping_status == "ambiguous":
            result["tradition_resolution_status"] = "ambiguous"
            result["reason"] = f"ambiguous_tradition_label:{label}"
            return result
        if mapping_status != "canonical":
            result["tradition_resolution_status"] = "unsupported"
            result["reason"] = f"non_selecting_tradition_label:{label}"
            return result

        mapped_tradition_refs = [
            ref for ref in mapping.get("context_refs", [])
            if ref in contexts and contexts[ref].get("dimension") in TRADITION_DIMENSIONS
        ]
        if not mapped_tradition_refs:
            result["tradition_resolution_status"] = "unsupported"
            result["reason"] = f"label_not_doctrine_selector:{label}"
            return result
        refs.extend(mapped_tradition_refs)
        if any(contexts[ref].get("dimension") == "interpretive_school" for ref in mapped_tradition_refs):
            status = "inferred_from_named_school"

    refs = list(dict.fromkeys(refs))
    explicit_mode = request.get("requested_synthesis_mode")
    if explicit_mode is not None and explicit_mode not in ALLOWED_SYNTHESIS_MODES:
        result["tradition_resolution_status"] = "unsupported"
        result["reason"] = "synthesis_mode_invalid"
        return result

    if len(refs) > 1:
        mode = explicit_mode or "synthesis:parallel_comparison"
    else:
        mode = explicit_mode or "synthesis:single_tradition"

    if mode == "synthesis:explicit_blend" and request.get("explicit_blend_requested") is not True:
        result["tradition_resolution_status"] = "unsupported"
        result["reason"] = "explicit_blend_requires_explicit_request"
        return result

    result.update({
        "tradition_resolution_status": status,
        "requested_tradition_contexts": refs,
        "requested_synthesis_mode": mode,
        "executable": True,
    })
    return result


def filter_claims_by_typed_tradition(
    claims: list[dict[str, Any]],
    requested_context_refs: list[str],
    taxonomy: dict[str, Any],
) -> list[dict[str, Any]]:
    requested = {value for value in requested_context_refs if isinstance(value, str)}
    if not requested:
        return []
    selected: list[dict[str, Any]] = []
    for claim in claims:
        if not isinstance(claim, dict):
            continue
        claim_refs = canonical_tradition_refs_for_claim(claim, taxonomy)
        if claim_refs & requested:
            selected.append(claim)
    return selected
