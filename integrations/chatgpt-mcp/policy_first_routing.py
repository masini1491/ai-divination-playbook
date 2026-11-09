"""Policy-first route contract for new MCP casts; no keyword method selection.

ChatGPT reads the SHA-pinned METHOD_ROUTING.md and chooses the judgment function
and method. The MCP only checks source identity and structural/contract gates.
Hash identity does NOT prove the model understood the natural-language policy.
"""
from __future__ import annotations
import hashlib
import json
from typing import Any

from auto_routing import FUNCTION_METHOD, TOOLS, _PII, _DATE
from policy_adapter import _bundle

POLICY_ROUTE_VERSION = "policy-first-v1"
ROUTE_BASIS = frozenset({"policy_routing", "user_method_override"})
DECISION_KEYS = frozenset({
    "source_commit", "policy_sha256", "selected_method",
    "judgment_function", "selection_basis", "has_completion_rule",
    "has_horizon",
})


def routing_identity() -> dict[str, str]:
    """Read verified generated owner; never fetch an unpinned URL."""
    pack = _bundle()  # validates all owners and the manifest
    owner = pack["owners"]["METHOD_ROUTING.md"]
    return {"source_commit": pack["source_commit"],
            "policy_sha256": owner["sha256"],
            "owner": "METHOD_ROUTING.md",
            "routing_version": POLICY_ROUTE_VERSION}


def _reject(status: str, reason_code: str, question: str | None = None) -> dict:
    result = {"status": status, "router_version": POLICY_ROUTE_VERSION,
              "reason_code": reason_code}
    if question is not None:
        result["question"] = question
    return result


def route_from_policy(question_summary: str, route_decision: dict,
                      tarot_count: int = 3) -> dict[str, Any]:
    """Validate caller-selected route WITHOUT keyword-reclassifying the question.

    Reject/clarify before invoking the stochastic engine. An explicit-method
    claim must actually reflect a user override; server cannot verify the
    private original question from the intentionally anonymous summary.
    """
    if (not isinstance(question_summary, str)
            or not 1 <= len(question_summary) <= 100
            or not question_summary.strip()):
        return _reject("invalid_input", "invalid_anonymous_summary")
    if _PII.search(_DATE.sub("", question_summary)):
        return _reject("invalid_input", "possible_contact_or_url")
    if type(tarot_count) is not int or not 1 <= tarot_count <= 24:
        return _reject("invalid_input", "invalid_tarot_count")
    if not isinstance(route_decision, dict) or set(route_decision) != DECISION_KEYS:
        return _reject("invalid_input", "invalid_route_decision_schema")
    if (type(route_decision["has_completion_rule"]) is not bool
            or type(route_decision["has_horizon"]) is not bool):
        return _reject("invalid_input", "boolean_flags_required")

    identity = routing_identity()
    if (route_decision["source_commit"] != identity["source_commit"]
            or route_decision["policy_sha256"] != identity["policy_sha256"]):
        return _reject("invalid_input", "ROUTING_POLICY_IDENTITY_MISMATCH")

    method = route_decision["selected_method"]
    judgment = route_decision["judgment_function"]
    basis = route_decision["selection_basis"]
    if not isinstance(method, str) or method not in TOOLS:
        return _reject("unsupported_method", "method_not_in_mcp_allowlist")
    if (not isinstance(judgment, str)
            or judgment not in {*FUNCTION_METHOD, "unclear"}
            or not isinstance(basis, str) or basis not in ROUTE_BASIS):
        return _reject("invalid_input", "invalid_route_function_or_basis")
    if basis == "policy_routing":
        if judgment == "unclear":
            return _reject("needs_clarification", "judgment_function_unclear",
                           "你要看人物心理／選項比較、事件演變，還是具體事件的結果？")
        if FUNCTION_METHOD[judgment] != method:
            return _reject("invalid_input", "ROUTE_FUNCTION_METHOD_MISMATCH")
    # User overrides may legitimately differ from the default function.
    # Route execution MUST NOT quietly reinterpret the selected method.
    if method == "liuyao" and (
            not route_decision["has_completion_rule"]
            or not route_decision["has_horizon"]):
        return _reject("needs_clarification", "completion_contract_incomplete",
                       "請確認這件事的可驗證完成條件與判定期限。")

    ticket = hashlib.sha256(json.dumps(
        {"question_summary": question_summary, "decision": route_decision,
         "tarot_count": tarot_count},
        sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")).hexdigest()
    return {
        "status": "ready",
        "router_version": POLICY_ROUTE_VERSION,
        "routing_source": "client_canonical_policy_read",
        "selection_reason": basis,
        "judgment_function": judgment,
        "selected_method": method,
        "selected_tool": TOOLS[method],
        "tarot_count": tarot_count if method == "tarot" else None,
        "routing_policy_identity": identity,
        "route_request_sha256": ticket,
    }
