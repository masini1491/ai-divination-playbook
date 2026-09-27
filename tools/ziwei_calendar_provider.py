#!/usr/bin/env python3
"""Production Gregorian → normalized lunar input provider for Zi Wei Scope-A.

Runtime conversion is resolved from the admitted repo-local interval dataset.
The pinned lunar-python implementation remains build/parity provenance only and
is not imported by ordinary production execution.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from tools.civil_time_normalizer import (
    CivilTimeNormalizationError,
    NORMALIZER_ID as CIVIL_TIME_NORMALIZER_ID,
    NORMALIZER_VERSION as CIVIL_TIME_NORMALIZER_VERSION,
    normalize_civil_time,
)

from tools.ziwei_calendar_data_provider import (
    DATASET_ID,
    DATASET_ROOT,
    END_DATE,
    START_DATE,
    CandidateGregorianBirth,
    normalize_candidate_birth,
)

PROVIDER_ID = "ziwei-calendar-interval-data"
PROVIDER_VERSION = "2.1.0"
PROFILE_ID = "ziwei.calendar.civil_v2"
DEFAULT_TIMEZONE = "Asia/Taipei"
CLOCK_MODE = "civil_time"
TRUE_SOLAR_TIME = "disabled"
LEAP_MONTH_POLICY = "split_after_day_15"
RAT_HOUR_POLICY = "next_day_at_23"
DATASET_PATH = "data/calendar/ziwei_tw_interval/v1"
ADMISSION_MANIFEST = "ZIWEI_CALENDAR_ADMISSION_V1.json"
BUILD_SOURCE_PACKAGE = "lunar_python"
BUILD_SOURCE_VERSION = "1.4.8"
BUILD_SOURCE_REPOSITORY = "6tail/lunar-python"
BUILD_SOURCE_REVISION = "000c8a3d74eed098d6256a28fdd51b869324c559"
BUILD_SOURCE_LICENSE = "MIT"

@dataclass(frozen=True)
class GregorianBirthInput:
    year: int
    month: int
    day: int
    hour: int
    minute: int = 0
    second: int = 0
    timezone: str = DEFAULT_TIMEZONE

    def local_iso(self) -> str:
        if not all(isinstance(v,int) for v in (self.year,self.month,self.day,self.hour,self.minute,self.second)):
            raise ValueError("Gregorian birth date/time fields must be integers")
        try:
            return f"{self.year:04d}-{self.month:02d}-{self.day:02d}T{self.hour:02d}:{self.minute:02d}:{self.second:02d}"
        except ValueError as exc:
            raise ValueError(f"invalid Gregorian birth date/time: {exc}") from exc

    def resolve_civil_time(self):
        try:
            return normalize_civil_time(self.local_iso(),self.timezone)
        except CivilTimeNormalizationError as exc:
            raise ValueError(str(exc)) from exc

    def as_data_birth(self, resolved=None) -> CandidateGregorianBirth:
        resolved = resolved or self.resolve_civil_time()
        local = resolved.validated_local_datetime
        return CandidateGregorianBirth(
            local.year,local.month,local.day,local.hour,
            local.minute,local.second,self.timezone,
        )

    def validate(self) -> None:
        resolved=self.resolve_civil_time()
        self.as_data_birth(resolved).validate()

def normalize_gregorian_birth(data: GregorianBirthInput) -> dict[str,Any]:
    civil=data.resolve_civil_time()
    data_birth=data.as_data_birth(civil)
    data_birth.validate()
    resolved=normalize_candidate_birth(data_birth,DATASET_ROOT)
    raw_lunar=resolved["raw_lunar_conversion"]
    policy_lunar=resolved["policy_lunar_conversion"]
    data_contract=resolved["data_contract"]

    provenance=(
        f"{PROVIDER_ID}@{PROVIDER_VERSION};"
        f"dataset={data_contract['dataset_id']}@{data_contract['aggregate_hash']};"
        f"build_source={BUILD_SOURCE_REPOSITORY}@{BUILD_SOURCE_REVISION};"
        f"profile={PROFILE_ID};timezone={data.timezone};clock={CLOCK_MODE};"
        f"civil_normalizer={CIVIL_TIME_NORMALIZER_ID}@{CIVIL_TIME_NORMALIZER_VERSION};"
        f"resolved_utc={civil.resolved_utc_instant.isoformat()};"
        f"rat_hour_policy={RAT_HOUR_POLICY};leap_month_policy={LEAP_MONTH_POLICY}"
    )
    normalized={
        **resolved["normalized_natal_input"],
        "calendar_provenance":provenance,
    }
    return {
        "schema_version":"2.0.0",
        "provider":{
            "id":PROVIDER_ID,
            "version":PROVIDER_VERSION,
            "authority":"PRODUCTION-ADMITTED GREGORIAN INPUT NORMALIZER",
        },
        "calendar_profile":{
            "profile_id":PROFILE_ID,
            "timezone_mode":"explicit_IANA",
            "timezone":data.timezone,
            "clock_mode":CLOCK_MODE,
            "true_solar_time":TRUE_SOLAR_TIME,
            "rat_hour_policy":RAT_HOUR_POLICY,
            "leap_month_policy":LEAP_MONTH_POLICY,
            "supported_gregorian_range":{
                "start":START_DATE.isoformat(),
                "end":END_DATE.isoformat(),
            },
        },
        "civil_time_normalization":civil.provenance(),
        "dataset":{
            "id":DATASET_ID,
            "path":DATASET_PATH,
            "aggregate_sha256":data_contract["aggregate_hash"],
            "required_shards":data_contract["required_shards"],
            "admission_manifest":ADMISSION_MANIFEST,
        },
        "build_source":{
            "package":BUILD_SOURCE_PACKAGE,
            "version":BUILD_SOURCE_VERSION,
            "repository":BUILD_SOURCE_REPOSITORY,
            "revision":BUILD_SOURCE_REVISION,
            "license":BUILD_SOURCE_LICENSE,
            "runtime_dependency":False,
        },
        "input":{
            "calendar":"gregorian",
            "year":data.year,"month":data.month,"day":data.day,
            "hour":data.hour,"minute":data.minute,"second":data.second,
            "timezone":data.timezone,
        },
        "raw_lunar_conversion":raw_lunar,
        "policy_lunar_conversion":policy_lunar,
        "normalized_natal_input":normalized,
        "provenance":provenance,
        "boundaries":{
            "civil_time_validation_performed":True,
            "local_calendar_identity_preserved":True,
            "utc_rebase_for_lunar_conversion":False,
            "resolved_utc_provenance_preserved":True,
            "true_solar_time_applied":False,
            "raw_lunar_preserved":True,
            "ziwei_policy_separated_from_calendar_conversion":True,
            "query_bounded_calendar_data":True,
            "runtime_lunar_python_dependency":False,
        },
    }
