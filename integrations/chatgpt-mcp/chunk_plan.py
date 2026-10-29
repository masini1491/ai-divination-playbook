"""Stateless, no-draw chunk plan for safer ChatGPT batch receipt acknowledgement.

Planning does not consume randomness and requires no server storage. It cannot
recover a completely lost response; the caller must preserve an acknowledged
receipt group before starting the next. Every item in a chunk remains a normal
batch_divination item and is validated by the existing canonical router.
"""
from __future__ import annotations
import hashlib
import json
from typing import Any
from batch_cast import validate_batch, MAX_BATCH, _stable_hash
from auto_routing import classify_summary

DEFAULT_CHUNK_SIZE=3
MAX_CHUNK_SIZE=4
PROTOCOL="acknowledged-batch-chunks-v1"

def _digest(value: Any) -> str:
    # Exactly the same canonical JSON hash used by batch_divination.
    return _stable_hash(value)

def plan_chunks(items: Any, chunk_size: int=DEFAULT_CHUNK_SIZE) -> dict:
    """Validate all 1..12 questions before creating a deterministic chunk plan."""
    if type(chunk_size) is not int or not 1<=chunk_size<=MAX_CHUNK_SIZE:
        raise ValueError(f"chunk_size must be an integer between 1 and {MAX_CHUNK_SIZE}")
    plans=validate_batch(items)
    # Return exact normalized input objects for the next calls; never infer a
    # method from a summary a second time in this plan.
    normalized=[]
    for entry,original in zip(plans,items):
        plan=entry["plan"]
        classified=classify_summary(original["question_summary"])
        # Preserve completion/horizon gates already inferred by the server.
        # The planned batch must be valid even if its method is now explicit.
        resolved_completion=(original.get("has_completion_rule", False)
                             or classified.get("has_completion_rule",False))
        resolved_horizon=(original.get("has_horizon",False)
                          or classified.get("has_horizon",False))
        normalized.append({
            "label":entry["label"],
            "question_summary":original["question_summary"],
            "method_override":plan["selected_method"],
            "has_completion_rule": resolved_completion,
            "has_horizon":resolved_horizon,
            "tarot_count":plan["tarot_count"] if plan["selected_method"]=="tarot" else 3,
        })
    chunks=[]
    for start in range(0,len(normalized),chunk_size):
        group=normalized[start:start+chunk_size]
        chunks.append({"chunk_index":len(chunks),"labels":[x["label"] for x in group],
             "items":group,"request_sha256":_digest(group)})
    return {"status":"planned_no_cast","protocol":PROTOCOL,
            "max_batch_items":MAX_BATCH,"chunk_size":chunk_size,
            "total_items":len(normalized),"chunk_count":len(chunks),
            "plan_sha256":_digest(normalized),"chunks":chunks,
            "instructions":(
                "Call batch_divination for the FIRST chunk only. Before calling "
                "the next chunk, send exactly the planned items with "
                "expected_request_sha256 set to that chunk's request_sha256. "
                "Verify the returned request_sha256, status=batch_completed, "
                "all expected labels and count, a common batch_id, "
                "unique receipt_id, and "
                "save the complete returned receipt JSON outside the next tool "
                "response. Continue one chunk at a time. If an MCP tool call "
                "fails or its response is lost, STOP and mark that chunk "
                "UNKNOWN; do NOT automatically retry it because random casts "
                "may already have occurred. This protocol narrows the possible "
                "loss to one chunk, but does not provide recovery or exactly-once "
                "execution. No server-side storage or retry cache."
            )}
