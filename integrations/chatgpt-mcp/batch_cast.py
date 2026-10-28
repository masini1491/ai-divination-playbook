"""Stateless multi-question casting with compact, recoverable original receipts.

A batch NEVER repeats policy text. The original stochastic result is retained
as a compact receipt, with every canonical raw card / coin / number and its
source/time provenance. Missing receipts cannot be recovered by this service.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any

from auto_routing import route_from_summary, execute_auto_route
from policy_adapter import policy_identity

MAX_BATCH = 5
_LABEL = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,31}$")
_ALLOWED_KEYS = frozenset({
    "label", "question_summary", "method_override", "has_completion_rule",
    "has_horizon", "tarot_count",
})


def _stable_hash(value: Any) -> str:
    content = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def validate_batch(items: Any) -> list[dict]:
    """Validate ALL labels, methods and completion contracts before RNG usage."""
    if not isinstance(items, list) or not 1 <= len(items) <= MAX_BATCH:
        raise ValueError("batch items must be an array of 1..5 independent questions")
    labels = set()
    approved = []
    for item in items:
        if not isinstance(item, dict) or set(item) - _ALLOWED_KEYS:
            raise ValueError("each item must be an object containing only approved fields")
        label = item.get("label")
        if not isinstance(label, str) or not _LABEL.fullmatch(label) or label in labels:
            raise ValueError("item labels must be unique ASCII identifiers of 1..32 characters")
        labels.add(label)
        summary = item.get("question_summary")
        if not isinstance(summary, str):
            raise ValueError(f"{label}: question_summary must be a short anonymous string")
        override = item.get("method_override", "auto")
        horizon = item.get("has_horizon", False)
        completion = item.get("has_completion_rule", False)
        count = item.get("tarot_count", 3)
        plan = route_from_summary(
            summary, method_override=override, has_horizon=horizon,
            has_completion_rule=completion, tarot_count=count,
        )
        if plan.get("status") != "ready":
            raise ValueError(f"{label}: {plan.get('reason_code', 'question_not_ready')}")
        approved.append({"label": label, "plan": plan})
    return approved


def _receipt(label: str, plan: dict, payload: dict) -> dict:
    """Store exact raw stochastic facts and a small display summary, not a huge chart.

    Do not remove original coin triples: they are the six-line raw evidence.
    """
    method = plan["selected_method"]
    execution = payload.get("execution", payload)
    if not isinstance(execution, dict) or not isinstance(execution.get("results"), list) \
            or len(execution["results"]) != 1:
        raise RuntimeError("BATCH_RAW_EXECUTION_MISSING")
    original = execution["results"][0]
    name = {"tarot": "tarot", "meihua": "plum", "liuyao": "liuyao"}[method]
    if not isinstance(original, dict) or original.get("method") != name \
            or not isinstance(original.get(name), dict):
        raise RuntimeError("BATCH_METHOD_FACT_MISMATCH")
    raw = original[name]
    stamp = execution.get("generated_at_taipei")
    if not isinstance(stamp, str) or not stamp:
        raise RuntimeError("BATCH_TIMESTAMP_MISSING")
    if method == "tarot":
        cards = raw.get("cards")
        if not isinstance(cards, list) or len(cards) != plan["tarot_count"]:
            raise RuntimeError("BATCH_TAROT_CARDS_MISSING")
        recovered = {"cards": [
            {"position": c["index"], "full_name": c["full_name"],
             "orientation": c["orientation"]} for c in cards
        ]}
    elif method == "meihua":
        recovered = {
            "a": raw["a"], "b": raw["b"], "primary_hexagram": raw["hexagram"],
            "upper_trigram": raw["upper_trigram"], "lower_trigram": raw["lower_trigram"],
            "moving_line": raw["moving_line"],
        }
        structured = payload.get("structured_method_fact", {})
        derived = structured.get("derived", {})
        if derived:
            recovered["mutual_hexagram"] = derived.get("mutual_hexagram", {}).get("name")
            recovered["changed_hexagram"] = derived.get("changed_hexagram", {}).get("name")
    else:
        lines = raw.get("lines")
        if not isinstance(lines, list) or len(lines) != 6 \
                or [x.get("position") for x in lines] != [1, 2, 3, 4, 5, 6]:
            raise RuntimeError("BATCH_LIUYAO_LINES_MISSING")
        recovered = {
            "raw_lines": [x["value"] for x in lines],
            "coin_values": [x["coin_values"] for x in lines],
            "line_order": "bottom-to-top",
            "cast_timestamp": stamp,
            "moving_positions": [x["position"] for x in lines if x["changing"]],
        }
        method_fact = payload.get("structured_method_fact", {}).get("structured_method_fact", {})
        if method_fact:
            recovered["primary_hexagram"] = method_fact.get("ben_gua", {}).get("name")
            zhi = method_fact.get("zhi_gua")
            recovered["changed_hexagram"] = zhi.get("name") if isinstance(zhi, dict) else None

    source = {
        k: execution[k] for k in (
            "source", "algorithm_version", "schema_version", "runtime_source_commit",
            "generated_at_utc", "generated_at_taipei", "timezone", "rng"
        ) if k in execution
    }
    evidence = {"method": method, "raw_cast": raw, "source": source}
    return {
        "label": label, "status": "cast_completed", "selected_method": method,
        "receipt_sha256": _stable_hash(evidence),
        "raw_cast": raw, "source": source,
        "summary": recovered,
        "policy_reference": {"method": method,
                             "read_complete_method_owner_before_interpreting": True},
    }


def execute_batch(items: Any, bridge_factory) -> dict:
    """No policy repetitions. Partial failure returns ALL completed receipts."""
    approved = validate_batch(items)
    pinned = policy_identity()  # fail closed before first stochastic cast
    completed = []
    for index, item in enumerate(approved):
        try:
            plan = execute_auto_route(item["plan"], bridge_factory)
            if plan.get("status") != "cast_completed":
                raise RuntimeError("BATCH_CAST_NOT_COMPLETED")
            completed.append(_receipt(item["label"], item["plan"], plan["cast_result"]))
        except Exception as error:
            return {
                "status": "partial_failure", "completed_count": len(completed),
                "total_count": len(approved), "receipts": completed,
                "failed_label": item["label"], "failed_index": index,
                "unattempted_labels": [x["label"] for x in approved[index + 1:]],
                "error_type": type(error).__name__,
                "next_step": ("Do NOT repeat completed labels. Save all receipts immediately. "
                              "Without a receipt, the original random cast cannot be recovered."),
                "policy_identity": pinned,
            }
    return {
        "status": "batch_completed", "completed_count": len(completed),
        "total_count": len(approved), "receipts": completed,
        "policy_identity": pinned,
        "next_step": ("Save every labeled original receipt before interpreting. "
                      "Load canonical method/output owners once per distinct method via "
                      "get_interpretation_policy; never recast for an interpretation failure. "
                      "These receipts are caller-held, not stored on this server."),
    }
