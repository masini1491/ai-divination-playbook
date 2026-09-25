#!/usr/bin/env python3
"""Production Gregorian → normalized lunar input provider for Zi Wei Scope-A.

Production conversion is resolved through the admitted repo-local interval
calendar dataset. lunar_python is retained only as pinned build/parity evidence.
"""
from __future__ import annotations
from typing import Any
from tools.ziwei_calendar_data_provider import (
    CalendarDataUnavailable,
    CandidateGregorianBirth,
    DATASET_ID,
    DATASET_ROOT,
    END_DATE,
    START_DATE,
    TIMEZONE,
    load_manifest,
    normalize_candidate_birth,
    required_shard_paths,
)

PROVIDER_ID="ziwei-calendar-interval-data"
PROVIDER_VERSION="2.0.0"
PROFILE_ID="ziwei.calendar.tw_v1"
CLOCK_MODE="civil_time"
TRUE_SOLAR_TIME="disabled"
LEAP_MONTH_POLICY="split_after_day_15"
RAT_HOUR_POLICY="next_day_at_23"
DATASET_AGGREGATE_SHA256="4913a39e770afcd21eedc387523c572b8c4fc6469889c28f6ea75613f8984d79"
BUILD_DEPENDENCY_PACKAGE="lunar_python"
BUILD_DEPENDENCY_VERSION="1.4.8"
BUILD_DEPENDENCY_REPOSITORY="6tail/lunar-python"
BUILD_DEPENDENCY_REVISION="000c8a3d74eed098d6256a28fdd51b869324c559"
BUILD_DEPENDENCY_LICENSE="MIT"

GregorianBirthInput=CandidateGregorianBirth

def _admission_call(fn, *args):
    try:
        return fn(*args)
    except CalendarDataUnavailable as exc:
        message=str(exc)
        if "outside selected candidate range" in message:
            message=message.replace("outside selected candidate range","outside admitted range")
        raise ValueError(message) from exc

def required_calendar_shards(data:GregorianBirthInput)->tuple[str,...]:
    paths=_admission_call(required_shard_paths,data)
    return tuple(f"data/calendar/ziwei_tw_interval/v1/{path}" for path in paths)

def normalize_gregorian_birth(data:GregorianBirthInput)->dict[str,Any]:
    resolved=_admission_call(normalize_candidate_birth,data)
    manifest=load_manifest()
    raw=dict(resolved["raw_lunar_conversion"])
    policy=dict(resolved["policy_lunar_conversion"])
    n=dict(resolved["normalized_natal_input"])
    provenance=(
        f"{PROVIDER_ID}@{PROVIDER_VERSION};"
        f"dataset={DATASET_ID};aggregate_sha256={DATASET_AGGREGATE_SHA256};"
        f"build_source={BUILD_DEPENDENCY_REPOSITORY}@{BUILD_DEPENDENCY_REVISION};"
        f"profile={PROFILE_ID};timezone={TIMEZONE};clock={CLOCK_MODE};"
        f"rat_hour_policy={RAT_HOUR_POLICY};leap_month_policy={LEAP_MONTH_POLICY}"
    )
    n["calendar_provenance"]=provenance
    return {
        "schema_version":"1.0.0",
        "provider":{
            "id":PROVIDER_ID,
            "version":PROVIDER_VERSION,
            "authority":"PRODUCTION-ADMITTED GREGORIAN INPUT NORMALIZER",
        },
        "calendar_profile":{
            "profile_id":PROFILE_ID,
            "timezone":TIMEZONE,
            "clock_mode":CLOCK_MODE,
            "true_solar_time":TRUE_SOLAR_TIME,
            "rat_hour_policy":RAT_HOUR_POLICY,
            "leap_month_policy":LEAP_MONTH_POLICY,
            "supported_gregorian_range":{
                "start":START_DATE.isoformat(),
                "end":END_DATE.isoformat(),
            },
        },
        "dataset":{
            "dataset_id":DATASET_ID,
            "root":"data/calendar/ziwei_tw_interval/v1",
            "aggregate_sha256":manifest["aggregate_hash"],
            "artifact_status":manifest["status"],
            "artifact_production_admitted":manifest["production_admitted"],
            "production_use":"admitted_by_ZIWEI_CALENDAR_ADMISSION_V1",
            "required_shards":list(required_calendar_shards(data)),
        },
        "dependency":{
            "package":BUILD_DEPENDENCY_PACKAGE,
            "version":BUILD_DEPENDENCY_VERSION,
            "repository":BUILD_DEPENDENCY_REPOSITORY,
            "revision":BUILD_DEPENDENCY_REVISION,
            "license":BUILD_DEPENDENCY_LICENSE,
            "role":"build_parity_only",
            "runtime_required":False,
        },
        "input":{
            "calendar":"gregorian",
            "year":data.year,"month":data.month,"day":data.day,
            "hour":data.hour,"minute":data.minute,"second":data.second,
            "timezone":data.timezone,
        },
        "raw_lunar_conversion":raw,
        "policy_lunar_conversion":policy,
        "normalized_natal_input":n,
        "provenance":provenance,
        "boundaries":{
            "timezone_conversion_performed":False,
            "true_solar_time_applied":False,
            "raw_lunar_preserved":True,
            "ziwei_policy_separated_from_calendar_conversion":True,
            "runtime_upstream_package_required":False,
        },
    }
