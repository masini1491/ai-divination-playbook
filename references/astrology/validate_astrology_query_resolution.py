#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_NAME = "astrology_query_resolution"
SCHEMA_VERSION = "0.1.0-research"
RISK_CLASSES = {
    "normal_symbolic",
    "private_motive_inference",
    "clinical_or_diagnostic",
    "high_stakes_external_outcome",
}
BASIS = {"user_text", "upstream_context", "research_fixture", "research_policy"}
SEMANTIC_ROUTE_FIELDS = {"claim_types", "tradition_tags_any", "applies_to_all"}


def add(errors: list[dict[str, str]], code: str, path: str, message: str) -> None:
    errors.append({"code": code, "path": path, "message": message})


def validate_query_resolution(data: Any, available_registry_ids: set[str] | None = None) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    if not isinstance(data, dict):
        return [{"code": "RESOLUTION_OBJECT_REQUIRED", "path": "$", "message": "resolution must be an object"}]

    if data.get("schema_name") != SCHEMA_NAME:
        add(errors, "SCHEMA_NAME_INVALID", "$.schema_name", f"must equal {SCHEMA_NAME}")
    if data.get("schema_version") != SCHEMA_VERSION:
        add(errors, "SCHEMA_VERSION_INVALID", "$.schema_version", f"must equal {SCHEMA_VERSION}")
    if data.get("record_status") != "REFERENCE-ONLY":
        add(errors, "RECORD_STATUS_INVALID", "$.record_status", "must remain REFERENCE-ONLY")
    if data.get("production_routable") is not False:
        add(errors, "PRODUCTION_ROUTABLE_FORBIDDEN", "$.production_routable", "must explicitly be false")

    status = data.get("resolution_status")
    if status not in {"resolved", "needs_clarification", "unsupported"}:
        add(errors, "RESOLUTION_STATUS_INVALID", "$.resolution_status", "unsupported resolution status")

    if not isinstance(data.get("query_id"), str) or not data.get("query_id"):
        add(errors, "QUERY_ID_REQUIRED", "$.query_id", "non-empty query_id required")

    question = data.get("user_question")
    if not isinstance(question, str) or not question.strip():
        add(errors, "USER_QUESTION_REQUIRED", "$.user_question", "non-empty user_question required")
        question = ""

    risk = data.get("question_risk_class")
    if risk not in RISK_CLASSES:
        add(errors, "RISK_CLASS_INVALID", "$.question_risk_class", "unsupported risk class")
    if status == "resolved" and risk != "normal_symbolic":
        add(errors, "RISK_CLASS_CANNOT_RESOLVE", "$.question_risk_class", "non-normal risk class must not resolve to astrology retrieval")

    registry_id = data.get("target_registry_record_id")
    if status == "resolved":
        if not isinstance(registry_id, str) or not registry_id:
            add(errors, "TARGET_REGISTRY_REQUIRED", "$.target_registry_record_id", "resolved route requires target registry")
        elif available_registry_ids is not None and registry_id not in available_registry_ids:
            add(errors, "TARGET_REGISTRY_UNKNOWN", "$.target_registry_record_id", "target registry is not available")
    elif registry_id not in (None, "") and available_registry_ids is not None and registry_id not in available_registry_ids:
        add(errors, "TARGET_REGISTRY_UNKNOWN", "$.target_registry_record_id", "target registry is not available")

    route = data.get("route")
    if status == "resolved":
        if not isinstance(route, dict):
            add(errors, "ROUTE_REQUIRED", "$.route", "resolved status requires route object")
            route = {}
        if route.get("query_id") != data.get("query_id"):
            add(errors, "ROUTE_QUERY_ID_MISMATCH", "$.route.query_id", "route query_id must match resolution query_id")

        for key in ("claim_types", "tradition_tags_any", "applies_to_all", "l2_fact_refs", "l3_policy_refs"):
            value = route.get(key)
            if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                add(errors, "ROUTE_STRING_ARRAY_REQUIRED", f"$.route.{key}", "must be a string array")
        if not isinstance(route.get("claim_types"), list) or not route.get("claim_types"):
            add(errors, "ROUTE_CLAIM_TYPES_REQUIRED", "$.route.claim_types", "at least one claim type required")

        for key in ("requires_l2_facts", "requires_l3_policy", "allow_reference_only_qualified", "include_registry_guardrails"):
            if not isinstance(route.get(key), bool):
                add(errors, "ROUTE_BOOLEAN_REQUIRED", f"$.route.{key}", "must be boolean")

        if route.get("requires_l2_facts") is True and not route.get("l2_fact_refs"):
            add(errors, "ROUTE_L2_REFS_REQUIRED", "$.route.l2_fact_refs", "required L2 facts need explicit refs")
        if route.get("requires_l3_policy") is True and not route.get("l3_policy_refs"):
            add(errors, "ROUTE_L3_REFS_REQUIRED", "$.route.l3_policy_refs", "required L3 policy needs explicit refs")
        if route.get("allow_reference_only_qualified") is True:
            reason = data.get("reference_only_justification")
            if not isinstance(reason, str) or not reason.strip():
                add(errors, "REFERENCE_ONLY_JUSTIFICATION_REQUIRED", "$.reference_only_justification", "explicit justification required when opting into REFERENCE_ONLY evidence")
    elif route not in (None, {}):
        add(errors, "ROUTE_FORBIDDEN_WHEN_UNRESOLVED", "$.route", "unresolved/unsupported status must not emit executable route")

    unresolved = data.get("unresolved_slots", [])
    if not isinstance(unresolved, list) or not all(isinstance(item, str) and item for item in unresolved):
        add(errors, "UNRESOLVED_SLOTS_INVALID", "$.unresolved_slots", "must be string array")
        unresolved = []
    if status == "needs_clarification" and not unresolved:
        add(errors, "UNRESOLVED_SLOTS_REQUIRED", "$.unresolved_slots", "clarification status requires at least one unresolved slot")
    if status == "resolved" and unresolved:
        add(errors, "UNRESOLVED_SLOTS_FORBIDDEN", "$.unresolved_slots", "resolved route cannot retain unresolved slots")

    if status == "needs_clarification":
        clarification = data.get("clarification_question")
        if not isinstance(clarification, str) or not clarification.strip():
            add(errors, "CLARIFICATION_QUESTION_REQUIRED", "$.clarification_question", "clarification status requires a question")
    if status == "unsupported":
        reason = data.get("unsupported_reason")
        if not isinstance(reason, str) or not reason.strip():
            add(errors, "UNSUPPORTED_REASON_REQUIRED", "$.unsupported_reason", "unsupported status requires a reason")

    assumptions = data.get("routing_assumptions", [])
    if not isinstance(assumptions, list):
        add(errors, "ROUTING_ASSUMPTIONS_ARRAY_REQUIRED", "$.routing_assumptions", "must be an array")
        assumptions = []

    mapped_fields: set[str] = set()
    for index, item in enumerate(assumptions):
        path = f"$.routing_assumptions[{index}]"
        if not isinstance(item, dict):
            add(errors, "ROUTING_ASSUMPTION_OBJECT_REQUIRED", path, "must be an object")
            continue

        field = item.get("field")
        basis = item.get("basis")
        if not isinstance(field, str) or not field:
            add(errors, "ROUTING_ASSUMPTION_FIELD_REQUIRED", path + ".field", "field required")
            continue
        mapped_fields.add(field)

        if basis not in BASIS:
            add(errors, "ROUTING_ASSUMPTION_BASIS_INVALID", path + ".basis", "unsupported basis")

        spans = item.get("evidence_spans", [])
        refs = item.get("evidence_refs", [])
        if not isinstance(spans, list) or not all(isinstance(value, str) and value for value in spans):
            add(errors, "EVIDENCE_SPANS_INVALID", path + ".evidence_spans", "must be string array")
            spans = []
        if not isinstance(refs, list) or not all(isinstance(value, str) and value for value in refs):
            add(errors, "EVIDENCE_REFS_INVALID", path + ".evidence_refs", "must be string array")
            refs = []

        if basis == "user_text":
            if not spans:
                add(errors, "USER_TEXT_EVIDENCE_REQUIRED", path + ".evidence_spans", "user_text basis requires evidence span")
            else:
                for span in spans:
                    if span not in question:
                        add(errors, "EVIDENCE_SPAN_NOT_IN_QUESTION", path + ".evidence_spans", f"span not found in user_question: {span}")
        if basis == "upstream_context" and not refs:
            add(errors, "UPSTREAM_CONTEXT_REF_REQUIRED", path + ".evidence_refs", "upstream_context basis requires evidence refs")

    if status == "resolved" and isinstance(route, dict):
        for field in SEMANTIC_ROUTE_FIELDS:
            values = route.get(field, [])
            if values and field not in mapped_fields:
                add(errors, "ROUTE_FIELD_UNGROUNDED", f"$.route.{field}", "non-empty semantic route field requires routing_assumption provenance")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a research Astrology query-resolution envelope.")
    parser.add_argument("path", type=Path)
    parser.add_argument("--registry-id", action="append", default=[], dest="registry_ids")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    try:
        data = json.loads(args.path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors = [{"code": "RESOLUTION_LOAD_ERROR", "path": "$", "message": str(exc)}]
    else:
        catalog = set(args.registry_ids) if args.registry_ids else None
        errors = validate_query_resolution(data, catalog)

    if args.as_json:
        print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    else:
        print("PASS" if not errors else "FAIL")
        for error in errors:
            print(f"  {error['code']} {error['path']}: {error['message']}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
