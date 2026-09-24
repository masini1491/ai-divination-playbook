#!/usr/bin/env python3
"""Compatibility adapter for the admitted Zi Wei brightness entrypoint."""
from __future__ import annotations
from typing import Any

from tools.ziwei_natal_provider import NormalizedNatalInput
from tools.ziwei_runtime import BRIGHTNESS_MODULE, ZiWeiReadingRequest, legacy_result, run_ziwei

PIPELINE_ID="ziwei-scope-a-brightness-production-pipeline-v1"
PIPELINE_VERSION="1.0.0"

def run_scope_a_natal_with_brightness(
    data:NormalizedNatalInput, *,
    request_id:str,
    requested_subjects:tuple[str,...]=(),
    enabled_source_ids:tuple[str,...]=(),
) -> dict[str,Any]:
    return legacy_result(run_ziwei(ZiWeiReadingRequest(
        request_id=request_id,
        birth=data,
        requested_subjects=requested_subjects,
        enabled_source_ids=enabled_source_ids,
        optional_modules=(BRIGHTNESS_MODULE,),
    )),brightness=True)
