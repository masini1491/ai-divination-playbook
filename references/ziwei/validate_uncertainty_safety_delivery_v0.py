#!/usr/bin/env python3
from __future__ import annotations

from typing import Iterable

EVIDENCE_STATES={"source_backed","project_adopted","profile_specific","conflicted","insufficient","case_inference_only"}
ACTIONS={"ALLOW","ALLOW_WITH_PROFILE_DISCLOSURE","ALLOW_WITH_UNCERTAINTY_DISCLOSURE","PRESENT_CONFLICT_SEPARATELY","OMIT_INSUFFICIENT","BOUND_HIGH_IMPACT","BLOCK_UNSUPPORTED_SCOPE"}
HIGH_IMPACT={"health","disease","death","legal","imprisonment","financial_ruin","guaranteed_wealth","pregnancy","fertility","violence","severe_harm"}

def delivery_actions(*, evidence_states: Iterable[str], high_impact: Iterable[str]=(), unsupported_scope: bool=False) -> list[str]:
    states=set(evidence_states)
    impact=set(high_impact)
    unknown=states-EVIDENCE_STATES
    if unknown:
        raise ValueError("EVIDENCE_STATE_INVALID")
    if unsupported_scope:
        return ["BLOCK_UNSUPPORTED_SCOPE"]
    out=[]
    if impact & HIGH_IMPACT:
        out.append("BOUND_HIGH_IMPACT")
    if "insufficient" in states:
        out.append("OMIT_INSUFFICIENT")
    if "conflicted" in states:
        out.append("PRESENT_CONFLICT_SEPARATELY")
    if "profile_specific" in states:
        out.append("ALLOW_WITH_PROFILE_DISCLOSURE")
    if "case_inference_only" in states:
        out.append("ALLOW_WITH_UNCERTAINTY_DISCLOSURE")
    if not out:
        out.append("ALLOW")
    return out
