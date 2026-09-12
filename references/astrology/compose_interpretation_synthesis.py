#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

SYNTHESIS_SCHEMA = "interpretation_synthesis_envelope"
SYNTHESIS_VERSION = "0.1.0-research"
BUNDLE_SCHEMA = "interpretation_retrieval_provenance_bundle"
BUNDLE_VERSION = "0.1.0-research"


def statement_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def compose_synthesis(resolution: dict[str, Any], bundle: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {
        "schema_name": SYNTHESIS_SCHEMA,
        "schema_version": SYNTHESIS_VERSION,
        "record_status": "REFERENCE-ONLY",
        "production_routable": False,
        "query_id": resolution.get("query_id") if isinstance(resolution, dict) else None,
        "registry_record_id": bundle.get("registry_record_id") if isinstance(bundle, dict) else None,
        "synthesis_status": None,
        "synthesis_units": [],
        "citation_units": [],
        "conflicts": [],
        "guardrails": [],
        "required_disclosures": [
            "REFERENCE-ONLY / RESEARCH / NOT PRODUCTION-ROUTABLE",
            "Source-backed claims and L5 synthesis must remain distinguishable.",
        ],
        "synthesis_provenance": {},
    }

    if not isinstance(resolution, dict) or resolution.get("resolution_status") != "resolved":
        out["synthesis_status"] = "blocked_resolution_not_resolved"
        return out
    if not isinstance(bundle, dict) or bundle.get("schema_name") != BUNDLE_SCHEMA or bundle.get("schema_version") != BUNDLE_VERSION:
        out["synthesis_status"] = "blocked_bundle_schema"
        return out
    if bundle.get("record_status") != "REFERENCE-ONLY" or bundle.get("production_routable") is not False:
        out["synthesis_status"] = "blocked_bundle_not_research_safe"
        return out
    if resolution.get("query_id") != bundle.get("query_id"):
        out["synthesis_status"] = "blocked_query_mismatch"
        return out
    if resolution.get("target_registry_record_id") != bundle.get("registry_record_id"):
        out["synthesis_status"] = "blocked_registry_mismatch"
        return out

    route = resolution.get("route", {}) if isinstance(resolution.get("route"), dict) else {}
    provenance = bundle.get("synthesis_provenance", {})
    if not isinstance(provenance, dict):
        out["synthesis_status"] = "blocked_provenance_mismatch"
        return out
    if provenance.get("l2_fact_refs", []) != route.get("l2_fact_refs", []):
        out["synthesis_status"] = "blocked_provenance_mismatch"
        return out
    if provenance.get("l3_policy_refs", []) != route.get("l3_policy_refs", []):
        out["synthesis_status"] = "blocked_provenance_mismatch"
        return out

    claims = bundle.get("claims", [])
    claim_ids = [claim.get("claim_id") for claim in claims if isinstance(claim, dict)]
    if bundle.get("selected_claim_ids", []) != claim_ids:
        out["synthesis_status"] = "blocked_provenance_mismatch"
        return out
    if provenance.get("claim_refs", []) != bundle.get("selected_claim_ids", []):
        out["synthesis_status"] = "blocked_provenance_mismatch"
        return out

    conflicts = bundle.get("conflicts", [])
    conflict_ids = [group.get("conflict_group_id") for group in conflicts if isinstance(group, dict)]
    if provenance.get("conflict_group_refs", []) != conflict_ids:
        out["synthesis_status"] = "blocked_provenance_mismatch"
        return out

    out["route_snapshot"] = {
        "claim_types": list(route.get("claim_types", [])),
        "tradition_tags_any": list(route.get("tradition_tags_any", [])),
        "applies_to_all": list(route.get("applies_to_all", [])),
        "l2_fact_refs": list(route.get("l2_fact_refs", [])),
        "l3_policy_refs": list(route.get("l3_policy_refs", [])),
    }
    out["resolution_provenance"] = list(resolution.get("routing_assumptions", []))

    retrieval_status = bundle.get("retrieval_status")
    if retrieval_status == "no_match":
        out["synthesis_status"] = "no_supported_claims"
        out["synthesis_provenance"] = provenance
        out["guardrails"] = list(bundle.get("guardrails", []))
        return out
    if retrieval_status == "provenance_incomplete":
        out["synthesis_status"] = "blocked_provenance_incomplete"
        return out
    if retrieval_status != "citation_ready":
        out["synthesis_status"] = "blocked_retrieval_status"
        return out
    if not isinstance(claims, list) or not claims:
        out["synthesis_status"] = "blocked_empty_claims"
        return out

    citation_by_key: dict[tuple[Any, ...], dict[str, Any]] = {}
    saw_reference_only = False
    saw_cautions = False

    for claim in claims:
        if not isinstance(claim, dict) or claim.get("citation_ready") is not True:
            out["synthesis_status"] = "blocked_provenance_incomplete"
            out["synthesis_units"] = []
            out["citation_units"] = []
            return out

        statement = claim.get("normalized_statement")
        if not isinstance(statement, str) or not statement.strip():
            out["synthesis_status"] = "blocked_claim_statement_missing"
            out["synthesis_units"] = []
            out["citation_units"] = []
            return out

        admission_mode = claim.get("source_admission_mode")
        if admission_mode in {"qualified_reference_only", "mixed_claim_eligible_and_reference_only"}:
            saw_reference_only = True

        cautions = [value for value in claim.get("cautions", []) if isinstance(value, str)]
        if cautions:
            saw_cautions = True

        unit = {
            "claim_id": claim.get("claim_id"),
            "statement": statement,
            "statement_sha256": statement_hash(statement),
            "claim_type": claim.get("claim_type"),
            "tradition_tags": list(claim.get("tradition_tags", [])),
            "applies_to": list(claim.get("applies_to", [])),
            "scope": claim.get("scope"),
            "confidence_status": claim.get("confidence_status"),
            "support_status": claim.get("support_status"),
            "source_admission_mode": admission_mode,
            "cautions": cautions,
            "conflict_group_ids": list(claim.get("conflict_group_ids", [])),
            "citation_source_ids": [],
            "semantic_policy": "registered_claim_only",
        }

        for source in claim.get("source_provenance", []):
            if not isinstance(source, dict):
                continue
            source_id = source.get("source_id")
            locator = source.get("locator")
            if not isinstance(source_id, str) or not source_id or locator in (None, "", []):
                out["synthesis_status"] = "blocked_provenance_incomplete"
                out["synthesis_units"] = []
                out["citation_units"] = []
                return out

            key = (source_id, repr(locator), source.get("immutable_revision"), source.get("edition"))
            if key not in citation_by_key:
                citation_by_key[key] = {
                    "source_id": source_id,
                    "title": source.get("title"),
                    "author_or_org": source.get("author_or_org"),
                    "source_role": source.get("source_role"),
                    "admission_status": source.get("admission_status"),
                    "locator": locator,
                    "edition": source.get("edition"),
                    "immutable_revision": source.get("immutable_revision"),
                    "publication_or_release_date": source.get("publication_or_release_date"),
                    "license_status": source.get("license_status"),
                    "copyright_status": source.get("copyright_status"),
                }
            unit["citation_source_ids"].append(source_id)

        out["synthesis_units"].append(unit)

    out["citation_units"] = list(citation_by_key.values())
    out["conflicts"] = list(conflicts)
    out["guardrails"] = list(bundle.get("guardrails", []))
    out["synthesis_provenance"] = dict(provenance)

    if saw_cautions:
        out["required_disclosures"].append("Preserve claim cautions in any user-facing synthesis.")
    if out["conflicts"]:
        out["required_disclosures"].append("Preserve registered conflicts; do not average them into consensus.")
    if out["guardrails"]:
        out["required_disclosures"].append("Do not assert registered non-admitted claims.")
    if saw_reference_only:
        out["required_disclosures"].append("Qualified REFERENCE_ONLY provenance is present and must remain explicitly qualified.")

    out["synthesis_status"] = "ready_for_l5"
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Compose an auditable research L5 synthesis envelope from a validated resolution and retrieval bundle.")
    parser.add_argument("resolution", type=Path)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    try:
        resolution = json.loads(args.resolution.read_text(encoding="utf-8"))
        bundle = json.loads(args.bundle.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"synthesis_status": "load_error", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2

    result = compose_synthesis(resolution, bundle)
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"{result['query_id']}: {result['synthesis_status']}")
        for unit in result["synthesis_units"]:
            print(f"  {unit['claim_id']}")

    return 0 if result["synthesis_status"] in {"ready_for_l5", "no_supported_claims"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
