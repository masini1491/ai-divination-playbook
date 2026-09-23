#!/usr/bin/env python3
"""Gregorian-input adapters for admitted Zi Wei Scope-A production pipelines."""
from __future__ import annotations
from typing import Any

from tools.ziwei_brightness_pipeline import run_scope_a_natal_with_brightness
from tools.ziwei_calendar_provider import GregorianBirthInput, normalize_gregorian_birth
from tools.ziwei_natal_provider import NormalizedNatalInput
from tools.ziwei_scope_a_pipeline import run_scope_a_natal

PIPELINE_ID="ziwei-gregorian-input-adapter-v1"
PIPELINE_VERSION="1.0.0"

def _to_natal_input(calendar:dict[str,Any]) -> NormalizedNatalInput:
    n=calendar["normalized_natal_input"]
    return NormalizedNatalInput(
        lunar_year=n["lunar_year"],
        lunar_month=n["lunar_month"],
        lunar_day=n["lunar_day"],
        hour_branch=n["hour_branch"],
        calendar_provenance=n["calendar_provenance"],
        leap_month_identity=n["leap_month_identity"],
    )

def _bind_calendar(result:dict[str,Any], calendar:dict[str,Any]) -> dict[str,Any]:
    bound=dict(result)
    bound["input_adapter"]={
        "pipeline_id":PIPELINE_ID,
        "pipeline_version":PIPELINE_VERSION,
        "calendar":calendar,
    }
    authority=dict(bound["authority"])
    authority["gregorian_input_adapter_admitted"]=True
    bound["authority"]=authority
    return bound

def run_scope_a_gregorian(
    data:GregorianBirthInput, *,
    request_id:str,
    requested_subjects:tuple[str,...]=(),
    enabled_source_ids:tuple[str,...]=(),
) -> dict[str,Any]:
    calendar=normalize_gregorian_birth(data)
    result=run_scope_a_natal(
        _to_natal_input(calendar),
        request_id=request_id,
        requested_subjects=requested_subjects,
        enabled_source_ids=enabled_source_ids,
    )
    return _bind_calendar(result,calendar)

def run_scope_a_gregorian_with_brightness(
    data:GregorianBirthInput, *,
    request_id:str,
    requested_subjects:tuple[str,...]=(),
    enabled_source_ids:tuple[str,...]=(),
) -> dict[str,Any]:
    calendar=normalize_gregorian_birth(data)
    result=run_scope_a_natal_with_brightness(
        _to_natal_input(calendar),
        request_id=request_id,
        requested_subjects=requested_subjects,
        enabled_source_ids=enabled_source_ids,
    )
    return _bind_calendar(result,calendar)
