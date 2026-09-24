#!/usr/bin/env python3
"""Compatibility adapter for legacy Zi Wei Scope-A normalized-lunar callers."""
from __future__ import annotations
from typing import Any

from tools.ziwei_natal_provider import NormalizedNatalInput
from tools.ziwei_runtime import ZiWeiReadingRequest, run_ziwei

PIPELINE_ID="ziwei-scope-a-production-pipeline-v1"
PIPELINE_VERSION="1.1.0"
INTERPRETATION_PROFILE="ziwei.interpretation.tw_v1"
TEMPORAL_SCOPE="natal_baseline"

def _legacy_result(result:dict[str,Any])->dict[str,Any]:
    legacy=dict(result)
    legacy.pop("schema_name",None)
    legacy.pop("schema_version",None)
    legacy.pop("runtime",None)
    return legacy

def run_scope_a_natal(
    data:NormalizedNatalInput, *,
    request_id:str,
    requested_subjects:tuple[str,...]=(),
    enabled_source_ids:tuple[str,...]=(),
) -> dict[str,Any]:
    return _legacy_result(run_ziwei(ZiWeiReadingRequest(
        request_id=request_id,
        birth=data,
        requested_subjects=requested_subjects,
        enabled_source_ids=enabled_source_ids,
    )))
