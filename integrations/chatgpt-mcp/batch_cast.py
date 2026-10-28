"""Stateless, mixed-method batches with compact and independently identified casts.

This adapter NEVER repeats policy text or stores user reading data.
Original irreversible random choices are returned in compact per-item receipts:
Tarot cards/orientations, Meihua A/B, Liuyao six raw lines and coin triples.
Other line/hexagram metadata can be reconstructed with the pinned engine.
"""
from __future__ import annotations

import hashlib
import json
import re
import secrets
from typing import Any

from auto_routing import route_from_summary, execute_auto_route
from policy_adapter import policy_identity

MAX_BATCH = 12
MAX_SUMMARY_CHARS = 100
RECEIPT_FORMAT = "compact-original-cast-v2"
_LABEL = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,31}$")
_ALLOWED_KEYS = frozenset({
    "label", "question_summary", "method_override", "has_completion_rule",
    "has_horizon", "tarot_count",
})
_SOURCE_FIELDS = (
    "source", "algorithm_version", "schema_version", "runtime_source_commit",
    "generated_at_utc", "generated_at_taipei", "timezone", "rng",
)


def _stable_hash(value: Any) -> str:
    content = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def validate_batch(items: Any) -> list[dict]:
    """Preflight the WHOLE mixed-method request before any RNG is consumed."""
    if not isinstance(items, list) or not 1 <= len(items) <= MAX_BATCH:
        raise ValueError(f"batch items must contain 1..{MAX_BATCH} independent questions")
    labels: set[str] = set()
    approved = []
    for item in items:
        if not isinstance(item, dict) or set(item) - _ALLOWED_KEYS:
            raise ValueError("each item must be an object containing only approved fields")
        label = item.get("label")
        if not isinstance(label, str) or not _LABEL.fullmatch(label) or label in labels:
            raise ValueError("each item requires a unique ASCII label of 1..32 characters")
        labels.add(label)
        summary = item.get("question_summary")
        if not isinstance(summary, str) or len(summary) > MAX_SUMMARY_CHARS:
            raise ValueError(f"{label}: anonymous question_summary must have <= {MAX_SUMMARY_CHARS} chars")
        plan = route_from_summary(
            summary, method_override=item.get("method_override", "auto"),
            has_horizon=item.get("has_horizon", False),
            has_completion_rule=item.get("has_completion_rule", False),
            tarot_count=item.get("tarot_count", 3),
        )
        if plan.get("status") != "ready":
            raise ValueError(f"{label}: {plan.get('reason_code', 'question_not_ready')}")
        approved.append({"label": label, "plan": plan})
    return approved


def _receipt(batch_id: str, index: int, label: str, plan: dict, payload: dict) -> dict:
    """Capture the original stochastic choices without duplicating huge charts."""
    method = plan["selected_method"]
    execution = payload.get("execution", payload)
    if (not isinstance(execution, dict)
            or not isinstance(execution.get("results"), list)
            or len(execution["results"]) != 1):
        raise RuntimeError("BATCH_RAW_EXECUTION_MISSING")
    original = execution["results"][0]
    kind = {"tarot": "tarot", "meihua": "plum", "liuyao": "liuyao"}[method]
    if (not isinstance(original, dict) or original.get("method") != kind
            or not isinstance(original.get(kind), dict)):
        raise RuntimeError("BATCH_METHOD_FACT_MISMATCH")
    raw = original[kind]
    if any(not isinstance(execution.get(key), str) or not execution[key]
           for key in _SOURCE_FIELDS):
        raise RuntimeError("BATCH_ORIGINAL_SOURCE_MISSING")
    source = {key: execution[key] for key in _SOURCE_FIELDS}

    if method == "tarot":
        cards = raw.get("cards")
        if not isinstance(cards, list) or len(cards) != plan["tarot_count"]:
            raise RuntimeError("BATCH_TAROT_CARDS_MISSING")
        compact = {"count": len(cards), "cards": [
            {"index": card["index"], "full_name": card["full_name"],
             "orientation": card["orientation"]} for card in cards
        ]}
        if ([card["index"] for card in compact["cards"]] != list(range(1, len(cards) + 1))
                or any(card["orientation"] not in ("正", "逆") for card in compact["cards"])):
            raise RuntimeError("BATCH_TAROT_CARDS_INVALID")
        summary = {"cards": compact["cards"]}
    elif method == "meihua":
        compact = {key: raw[key] for key in (
            "a", "b", "upper_trigram", "lower_trigram", "hexagram", "moving_line"
        )}
        if (not all(isinstance(compact[key], str) and len(compact[key]) == 3
                    and compact[key].isascii() and compact[key].isdigit()
                    for key in ("a", "b"))
                or type(compact["moving_line"]) is not int
                or not 1 <= compact["moving_line"] <= 6):
            raise RuntimeError("BATCH_MEIHUA_RAW_INVALID")
        structured = payload.get("structured_method_fact", {})
        derived = structured.get("derived", {})
        summary = {"primary_hexagram": compact["hexagram"],
                   "moving_line": compact["moving_line"]}
        if derived:
            summary["mutual_hexagram"] = derived.get("mutual_hexagram", {}).get("name")
            summary["changed_hexagram"] = derived.get("changed_hexagram", {}).get("name")
    else:
        lines = raw.get("lines")
        if (not isinstance(lines, list) or len(lines) != 6
                or [line.get("position") for line in lines] != [1, 2, 3, 4, 5, 6]):
            raise RuntimeError("BATCH_LIUYAO_LINES_MISSING")
        compact_lines = []
        for line in lines:
            coins = line.get("coin_values")
            value = line.get("value")
            if (not isinstance(coins, list) or len(coins) != 3
                    or any(type(v) is not int or v not in (2, 3) for v in coins)
                    or type(value) is not int or value != sum(coins)):
                raise RuntimeError("BATCH_LIUYAO_COIN_TRIPLE_INVALID")
            compact_lines.append({"position": line["position"],
                                  "value": value, "coin_values": coins})
        compact = {"cast_method": "three-coins", "line_order": "bottom-to-top",
                   "lines": compact_lines}
        summary = {"raw_lines": [line["value"] for line in compact_lines],
                   "moving_positions": [line["position"] for line in compact_lines
                                        if line["value"] in (6, 9)],
                   "cast_timestamp": source["generated_at_taipei"]}
        fact = payload.get("structured_method_fact", {}).get("structured_method_fact", {})
        if fact:
            summary["primary_hexagram"] = fact.get("ben_gua", {}).get("name")
            changed = fact.get("zhi_gua")
            summary["changed_hexagram"] = changed.get("name") if isinstance(changed, dict) else None

    receipt = {
        "batch_id": batch_id,
        "index": index, "label": label,
        "receipt_id": f"{batch_id}:{index:02d}:{label}",
        "status": "cast_completed", "selected_method": method,
        "raw_cast": compact, "source": source, "summary": summary,
    }
    # Digest binds the original facts to the invocation AND label/index, not
    # merely to a hexagram that might recur in another app or another batch.
    return {**receipt, "receipt_sha256": _stable_hash(receipt)}


def execute_batch(items: Any, bridge_factory) -> dict:
    """One mixed batch; separate invocations are independent and stateless.

    Preflight ALL questions, then policy integrity; only then allocate a batch
    identity and draw in user-specified order. On a later error, completed
    receipts remain available and MUST NOT be redrawn automatically.
    """
    approved = validate_batch(items)
    pinned = policy_identity()  # fail closed before any stochastic cast
    batch_id = secrets.token_hex(12)
    completed = []
    for index, item in enumerate(approved):
        try:
            plan = execute_auto_route(item["plan"], bridge_factory)
            if plan.get("status") != "cast_completed":
                raise RuntimeError("BATCH_CAST_NOT_COMPLETED")
            completed.append(_receipt(batch_id, index, item["label"], plan, plan["cast_result"]))
        except Exception as error:
            return {
                "status": "partial_failure", "batch_id": batch_id,
                "receipt_format": RECEIPT_FORMAT,
                "completed_count": len(completed), "total_count": len(approved),
                "receipts": completed, "failed_label": item["label"],
                "failed_index": index,
                "unattempted_labels": [x["label"] for x in approved[index + 1:]],
                "error_type": type(error).__name__,
                "policy_identity": pinned,
                "next_step": ("Keep already returned receipts and never retry their labels. "
                              "A failed or missing receipt cannot be recovered from this stateless server. "
                              "Do not assume the failed item did or did not consume randomness."),
            }
    return {
        "status": "batch_completed", "batch_id": batch_id,
        "receipt_format": RECEIPT_FORMAT,
        "completed_count": len(completed), "total_count": len(approved),
        "receipts": completed, "policy_identity": pinned,
        "next_step": ("Preserve all distinct batch_id/receipt_id/receipt_sha256 values before "
                      "interpreting. You may interleave subsequent batch_divination, "
                      "auto_divination or deterministic derive calls; never substitute "
                      "one receipt for another. Load each method's canonical policy "
                      "once per distinct method. No server-side reading storage."),
    }
