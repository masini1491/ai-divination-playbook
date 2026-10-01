#!/usr/bin/env python3
"""Production Gregorian → normalized lunar input provider for Zi Wei Scope-A.

Runtime conversion is resolved from the admitted repo-local interval dataset.
The pinned lunar-python implementation remains build/parity provenance only and
is not imported by ordinary production execution.

Civil time remains the default.  The separately admitted optional true-solar
profile is applied only after shared IANA/DST validation and before the
Gregorian→lunar dataset lookup.
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
from tools.ziwei_true_solar_time import (
    PROFILE_ID as TRUE_SOLAR_PROFILE_ID,
    PROFILE_VERSION as TRUE_SOLAR_PROFILE_VERSION,
    TrueSolarTimeError,
    normalize_true_solar_time,
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
PROVIDER_VERSION = "2.2.0"
PROFILE_ID = "ziwei.calendar.civil_v2"
DEFAULT_TIMEZONE = "Asia/Taipei"
CLOCK_MODE = "civil_time"
TRUE_SOLAR_TIME = "explicit_profile_only"
LEAP_MONTH_POLICY = "split_after_day_15"
RAT_HOUR_POLICY = "next_day_at_23"
DATASET_PATH = "data/calendar/ziwei_tw_interval/v1"
ADMISSION_MANIFEST = "admissions/ziwei/ZIWEI_CALENDAR_ADMISSION_V1.json"
TRUE_SOLAR_ADMISSION_MANIFEST = "admissions/ziwei/ZIWEI_TRUE_SOLAR_TIME_ADMISSION_V1.json"
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
    true_solar_time_profile: str | None = None
    longitude_deg: float | None = None

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

    def _solar_requested(self) -> bool:
        has_profile=self.true_solar_time_profile is not None
        has_longitude=self.longitude_deg is not None
        if has_profile != has_longitude:
            raise ValueError(
                "true_solar_time_profile and longitude_deg must be supplied together"
            )
        return has_profile

    def resolve_clock(self):
        civil=self.resolve_civil_time()
        if not self._solar_requested():
            return civil,None
        try:
            solar=normalize_true_solar_time(
                civil,
                self.longitude_deg,
                profile_id=self.true_solar_time_profile,
            )
        except TrueSolarTimeError as exc:
            raise ValueError(str(exc)) from exc
        return civil,solar

    def as_data_birth(self, civil=None, solar=None) -> CandidateGregorianBirth:
        if civil is None:
            civil,solar=self.resolve_clock()
        local=(
            solar.apparent_solar_datetime
            if solar is not None
            else civil.validated_local_datetime
        )
        return CandidateGregorianBirth(
            local.year,local.month,local.day,local.hour,
            local.minute,local.second,self.timezone,
        )

    def validate(self) -> None:
        civil,solar=self.resolve_clock()
        self.as_data_birth(civil,solar).validate()

def normalize_gregorian_birth(data: GregorianBirthInput) -> dict[str,Any]:
    civil,solar=data.resolve_clock()
    data_birth=data.as_data_birth(civil,solar)
    data_birth.validate()
    resolved=normalize_candidate_birth(data_birth,DATASET_ROOT)
    raw_lunar=resolved["raw_lunar_conversion"]
    policy_lunar=resolved["policy_lunar_conversion"]
    data_contract=resolved["data_contract"]
    solar_provenance=solar.provenance() if solar is not None else None
    clock_mode="true_solar_time" if solar is not None else CLOCK_MODE

    provenance_parts=[
        f"{PROVIDER_ID}@{PROVIDER_VERSION}",
        f"dataset={data_contract['dataset_id']}@{data_contract['aggregate_hash']}",
        f"build_source={BUILD_SOURCE_REPOSITORY}@{BUILD_SOURCE_REVISION}",
        f"profile={PROFILE_ID}",
        f"timezone={data.timezone}",
        f"clock={clock_mode}",
        f"civil_normalizer={CIVIL_TIME_NORMALIZER_ID}@{CIVIL_TIME_NORMALIZER_VERSION}",
        f"resolved_utc={civil.resolved_utc_instant.isoformat()}",
    ]
    if solar is not None:
        provenance_parts.extend([
            f"true_solar_profile={TRUE_SOLAR_PROFILE_ID}@{TRUE_SOLAR_PROFILE_VERSION}",
            f"longitude_deg={solar.longitude_deg}",
            f"apparent_solar_local={solar.apparent_solar_datetime.isoformat()}",
            f"true_solar_correction_seconds={solar.total_correction_seconds}",
        ])
    provenance_parts.extend([
        f"rat_hour_policy={RAT_HOUR_POLICY}",
        f"leap_month_policy={LEAP_MONTH_POLICY}",
    ])
    provenance=";".join(provenance_parts)

    normalized={
        **resolved["normalized_natal_input"],
        "calendar_provenance":provenance,
    }
    input_payload={
        "calendar":"gregorian",
        "year":data.year,"month":data.month,"day":data.day,
        "hour":data.hour,"minute":data.minute,"second":data.second,
        "timezone":data.timezone,
    }
    if solar is not None:
        input_payload.update({
            "true_solar_time_profile":data.true_solar_time_profile,
            "longitude_deg":data.longitude_deg,
        })

    result={
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
            "clock_mode":clock_mode,
            "true_solar_time":(
                TRUE_SOLAR_PROFILE_ID if solar is not None else "disabled"
            ),
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
        "input":input_payload,
        "raw_lunar_conversion":raw_lunar,
        "policy_lunar_conversion":policy_lunar,
        "normalized_natal_input":normalized,
        "provenance":provenance,
        "boundaries":{
            "civil_time_validation_performed":True,
            "local_calendar_identity_preserved":solar is None,
            "utc_rebase_for_lunar_conversion":False,
            "resolved_utc_provenance_preserved":True,
            "true_solar_time_applied":solar is not None,
            "apparent_solar_fields_used_for_lunar_conversion":solar is not None,
            "birthplace_resolution_performed":False,
            "raw_lunar_preserved":True,
            "ziwei_policy_separated_from_calendar_conversion":True,
            "query_bounded_calendar_data":True,
            "runtime_lunar_python_dependency":False,
        },
    }
    if solar_provenance is not None:
        result["true_solar_time_normalization"]={
            **solar_provenance,
            "admission_manifest":TRUE_SOLAR_ADMISSION_MANIFEST,
        }
    return result
