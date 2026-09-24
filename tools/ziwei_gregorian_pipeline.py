#!/usr/bin/env python3
"""Compatibility adapters for admitted Zi Wei Gregorian entrypoints."""
from __future__ import annotations
from typing import Any

from tools.ziwei_calendar_provider import GregorianBirthInput
from tools.ziwei_runtime import BRIGHTNESS_MODULE, ZiWeiReadingRequest, legacy_result, run_ziwei

PIPELINE_ID="ziwei-gregorian-input-adapter-v1"
PIPELINE_VERSION="1.0.0"

def run_scope_a_gregorian(
    data:GregorianBirthInput, *,
    request_id:str,
    requested_subjects:tuple[str,...]=(),
    enabled_source_ids:tuple[str,...]=(),
) -> dict[str,Any]:
    return legacy_result(run_ziwei(ZiWeiReadingRequest(
        request_id=request_id,
        birth=data,
        requested_subjects=requested_subjects,
        enabled_source_ids=enabled_source_ids,
    )))

def run_scope_a_gregorian_with_brightness(
    data:GregorianBirthInput, *,
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
