#!/usr/bin/env python3
"""REFERENCE-ONLY typed tradition pipeline integration for Astrology research.

This module connects the research tradition taxonomy to the existing
query-resolution -> retrieval -> L5 synthesis pipeline without changing
production routing. It preserves typed tradition provenance end to end and
fails closed when a requested comparison is only partially covered.
"""
from __future__ import annotations

import copy
from typing import Any

from compose_interpretation_synthesis import compose_synthesis
from retrieve_interpretation_claims import retrieve_claims
from typed_tradition_routing import (
    ALLOWED_SYNTHESIS_MODES,
    TRADITION_DIMENSIONS,
    canonical_tradition_refs_for_claim,
    resolve_tradition_request,
    validate_taxonomy,
)
from validate_astrology_query_resolution import validate_query_resolution


def _context_index(taxonomy: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        row.get("context_id"): row
        for row in taxonomy.get("contexts", [])
        if isinstance(row, dict) and isinstance(row.get("context_id"), str)
    }


def _valid_typed_refs(values: Any, taxonomy: dict[str, Any]) -> list[str]:
    if not isinstance(values, list):
        return []
    contexts = _context_index(taxonomy)
    out: list[str] = []
    for value in values:
        row = contexts.get(value) if isinstance(value, str) else None
        if row and row.get("dimension") in TRADITION_DIMENSIONS:
            out.append(value)
    return list(dict.fromkeys(out))


def _selected_context_coverage(claims: list[dict[str, Any]], taxonomy: dict[str, Any]) -> set[str]:
    covered: set[str] = set()
    for claim in claims:
        if isinstance(claim, dict):
            covered.update(canonical_tradition_refs_for_claim(claim, taxonomy))
    return covered


def validate_typed_resolution(
    resolution: Any,
    taxonomy: dict[str, Any],
    available_registry_ids: set[str] | None = None,
) -> list[dict[str, str]]:
    """Validate typed tradition metadata plus the existing query contract."""
    errors: list[dict[str, str]] = []
    if not isinstance(resolution, dict):
        return [{"code": "RESOLUTION_OBJECT_REQUIRED", "path": "$", "message": "resolution must be an object"}]

    taxonomy_errors = validate_taxonomy(taxonomy)
    if taxonomy_errors:
        return [{"code": "TAXONOMY_INVALID", "path": "$.taxonomy", "message": "taxonomy failed deterministic validation"}]

    route = resolution.get("route")
    if resolution.get("resolution_status") == "resolved" and isinstance(route, dict):
        typed_refs = route.get("tradition_context_refs_any", [])
        legacy_tags = route.get("tradition_tags_any", [])

        if typed_refs and legacy_tags:
            errors.append({
                "code": "TRADITION_SELECTOR_MIXED",
                "path": "$.route",
                "message": "typed tradition refs and legacy flat tradition tags must not be mixed",
            })

        if typed_refs:
            valid_refs = _valid_typed_refs(typed_refs, taxonomy)
            if valid_refs != typed_refs:
                errors.append({
                    "code": "TRADITION_CONTEXT_INVALID",
                    "path": "$.route.tradition_context_refs_any",
                    "message": "all typed refs must resolve to doctrinal_lineage or interpretive_school contexts",
                })

            requested = resolution.get("requested_tradition_contexts")
            if requested != typed_refs:
                errors.append({
                    "code": "TRADITION_CONTEXT_ROUTE_MISMATCH",
                    "path": "$.requested_tradition_contexts",
                    "message": "requested_tradition_contexts must exactly match the executable route",
                })

            tradition_status = resolution.get("tradition_resolution_status")
            if tradition_status not in {"explicit", "inferred_from_named_school"}:
                errors.append({
                    "code": "TRADITION_RESOLUTION_NOT_EXECUTABLE",
                    "path": "$.tradition_resolution_status",
                    "message": "resolved typed route requires explicit or inferred_from_named_school status",
                })

            mode = resolution.get("requested_synthesis_mode")
            if mode not in ALLOWED_SYNTHESIS_MODES:
                errors.append({
                    "code": "SYNTHESIS_MODE_INVALID",
                    "path": "$.requested_synthesis_mode",
                    "message": "unsupported typed synthesis mode",
                })
            if route.get("synthesis_mode") != mode:
                errors.append({
                    "code": "SYNTHESIS_MODE_ROUTE_MISMATCH",
                    "path": "$.route.synthesis_mode",
                    "message": "route synthesis_mode must match requested_synthesis_mode",
                })

            if mode == "synthesis:single_tradition" and len(typed_refs) != 1:
                errors.append({
                    "code": "SINGLE_TRADITION_CARDINALITY_INVALID",
                    "path": "$.route.tradition_context_refs_any",
                    "message": "single-tradition synthesis requires exactly one tradition context",
                })
            if mode in {"synthesis:parallel_comparison", "synthesis:explicit_blend"} and len(typed_refs) < 2:
                errors.append({
                    "code": "MULTI_TRADITION_CARDINALITY_INVALID",
                    "path": "$.route.tradition_context_refs_any",
                    "message": "parallel comparison or explicit blend requires at least two tradition contexts",
                })

    # Existing validator does not know typed fields. Validate a compatibility copy
    # with typed selection removed from the legacy selector surface.
    compatibility = copy.deepcopy(resolution)
    compatibility_route = compatibility.get("route")
    if isinstance(compatibility_route, dict) and compatibility_route.get("tradition_context_refs_any"):
        compatibility_route.setdefault("tradition_tags_any", [])
        compatibility_route.pop("tradition_context_refs_any", None)
        compatibility_route.pop("synthesis_mode", None)
        compatibility["routing_assumptions"] = [
            item for item in compatibility.get("routing_assumptions", [])
            if not isinstance(item, dict)
            or item.get("field") not in {"tradition_context_refs_any", "synthesis_mode"}
        ]

    errors.extend(validate_query_resolution(compatibility, available_registry_ids))
    return errors


def retrieve_typed_claims(
    registry: dict[str, Any],
    resolution: dict[str, Any],
    taxonomy: dict[str, Any],
) -> dict[str, Any]:
    """Run deterministic retrieval with typed tradition filtering and coverage."""
    route = resolution.get("route", {}) if isinstance(resolution.get("route"), dict) else {}
    requested_refs = _valid_typed_refs(route.get("tradition_context_refs_any", []), taxonomy)

    registry_view = copy.deepcopy(registry)
    if requested_refs:
        filtered_claims = []
        for claim in registry_view.get("claims", []):
            if not isinstance(claim, dict):
                continue
            claim_refs = canonical_tradition_refs_for_claim(claim, taxonomy)
            if claim_refs & set(requested_refs):
                enriched = copy.deepcopy(claim)
                enriched["tradition_context_refs"] = sorted(claim_refs)
                filtered_claims.append(enriched)
        registry_view["claims"] = filtered_claims

    legacy_route = copy.deepcopy(route)
    if requested_refs:
        legacy_route["tradition_tags_any"] = []
        legacy_route.pop("tradition_context_refs_any", None)
        legacy_route.pop("synthesis_mode", None)

    bundle = retrieve_claims(registry_view, legacy_route)
    bundle["tradition_provenance"] = {
        "tradition_resolution_status": resolution.get("tradition_resolution_status"),
        "requested_tradition_contexts": list(requested_refs),
        "requested_synthesis_mode": resolution.get("requested_synthesis_mode"),
    }

    for claim in bundle.get("claims", []):
        if isinstance(claim, dict):
            claim["tradition_context_refs"] = sorted(
                canonical_tradition_refs_for_claim(claim, taxonomy)
            )

    if requested_refs:
        covered = _selected_context_coverage(bundle.get("claims", []), taxonomy)
        missing = [ref for ref in requested_refs if ref not in covered]
        bundle["tradition_provenance"]["covered_tradition_contexts"] = sorted(covered & set(requested_refs))
        bundle["tradition_provenance"]["missing_tradition_contexts"] = missing
        mode = resolution.get("requested_synthesis_mode")
        if missing and mode in {"synthesis:parallel_comparison", "synthesis:explicit_blend"}:
            bundle["retrieval_status"] = "tradition_coverage_incomplete"
            bundle.setdefault("guardrails", []).append(
                "Requested multi-tradition synthesis is incomplete; do not silently substitute another tradition."
            )

    return bundle


def compose_typed_synthesis(
    resolution: dict[str, Any],
    bundle: dict[str, Any],
) -> dict[str, Any]:
    """Compose L5 envelope while preserving typed tradition provenance."""
    if bundle.get("retrieval_status") == "tradition_coverage_incomplete":
        return {
            "schema_name": "interpretation_synthesis_envelope",
            "schema_version": "0.1.0-research",
            "record_status": "REFERENCE-ONLY",
            "production_routable": False,
            "query_id": resolution.get("query_id"),
            "registry_record_id": bundle.get("registry_record_id"),
            "synthesis_status": "blocked_tradition_coverage_incomplete",
            "synthesis_units": [],
            "citation_units": [],
            "conflicts": list(bundle.get("conflicts", [])),
            "guardrails": list(bundle.get("guardrails", [])),
            "required_disclosures": [
                "REFERENCE-ONLY / RESEARCH / NOT PRODUCTION-ROUTABLE",
                "Requested multi-tradition comparison/blend lacks complete tradition coverage.",
                "Do not silently substitute, collapse, or invent the missing tradition perspective.",
            ],
            "tradition_provenance": copy.deepcopy(bundle.get("tradition_provenance", {})),
            "synthesis_provenance": copy.deepcopy(bundle.get("synthesis_provenance", {})),
        }

    envelope = compose_synthesis(resolution, bundle)
    envelope["tradition_provenance"] = copy.deepcopy(bundle.get("tradition_provenance", {}))
    route_snapshot = envelope.setdefault("route_snapshot", {})
    route = resolution.get("route", {}) if isinstance(resolution.get("route"), dict) else {}
    route_snapshot["tradition_context_refs_any"] = list(route.get("tradition_context_refs_any", []))
    route_snapshot["synthesis_mode"] = route.get("synthesis_mode")

    for unit in envelope.get("synthesis_units", []):
        claim_id = unit.get("claim_id") if isinstance(unit, dict) else None
        source_claim = next(
            (claim for claim in bundle.get("claims", []) if isinstance(claim, dict) and claim.get("claim_id") == claim_id),
            None,
        )
        if source_claim is not None:
            unit["tradition_context_refs"] = list(source_claim.get("tradition_context_refs", []))

    if envelope.get("synthesis_status") == "ready_for_l5":
        mode = resolution.get("requested_synthesis_mode")
        if mode == "synthesis:parallel_comparison":
            envelope["required_disclosures"].append(
                "Keep requested traditions visibly separate in the user-facing comparison; do not average them into consensus."
            )
        elif mode == "synthesis:explicit_blend":
            envelope["required_disclosures"].append(
                "The user explicitly requested a blend; preserve each contributing tradition's provenance and registered conflicts."
            )
    return envelope


def run_typed_pipeline(
    registry: dict[str, Any],
    resolution: dict[str, Any],
    taxonomy: dict[str, Any],
    available_registry_ids: set[str] | None = None,
) -> dict[str, Any]:
    """Validate, retrieve, and compose one typed-tradition research pipeline."""
    errors = validate_typed_resolution(resolution, taxonomy, available_registry_ids)
    if errors:
        return {
            "pipeline_status": "invalid_resolution",
            "errors": errors,
        }
    bundle = retrieve_typed_claims(registry, resolution, taxonomy)
    envelope = compose_typed_synthesis(resolution, bundle)
    return {
        "pipeline_status": "complete" if envelope.get("synthesis_status") == "ready_for_l5" else "blocked",
        "retrieval": bundle,
        "synthesis": envelope,
    }
