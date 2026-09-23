#!/usr/bin/env python3
"""Optional brightness-enabled production binding for Zi Wei Scope-A."""
from __future__ import annotations
from typing import Any

from tools.ziwei_brightness_provider import calculate_brightness
from tools.ziwei_natal_provider import NormalizedNatalInput, calculate_scope_a_natal
from tools.ziwei_scope_a_pipeline import _compose_scope_a_chart

PIPELINE_ID="ziwei-scope-a-brightness-production-pipeline-v1"
PIPELINE_VERSION="1.0.0"

def run_scope_a_natal_with_brightness(
    data:NormalizedNatalInput, *,
    request_id:str,
    requested_subjects:tuple[str,...]=(),
    enabled_source_ids:tuple[str,...]=(),
) -> dict[str,Any]:
    chart=calculate_scope_a_natal(data)
    brightness=calculate_brightness(chart["major_star_placements"])
    augmented=dict(chart)
    augmented["retrieval_facts"]=list(chart["retrieval_facts"])+list(brightness["retrieval_facts"])
    unsupported=dict(chart["unsupported"])
    unsupported["brightness"]="computed_by_optional_profile"
    augmented["unsupported"]=unsupported
    result=_compose_scope_a_chart(
        augmented,
        request_id=request_id,
        requested_subjects=requested_subjects,
        enabled_source_ids=enabled_source_ids,
    )
    result["pipeline_id"]=PIPELINE_ID
    result["pipeline_version"]=PIPELINE_VERSION
    result["scope"]="bounded_natal_first_layer+optional_brightness_v1"
    result["calculation"]["unsupported"]=unsupported
    result["calculation"]["brightness"]=brightness
    result["authority"]["brightness_profile_admitted"]=True
    result["authority"]["brightness_only_doctrine_admitted"]=False
    return result
