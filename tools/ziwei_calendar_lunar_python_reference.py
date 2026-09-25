#!/usr/bin/env python3
"""Build/parity-only lunar-python reference for Zi Wei Gregorian conversion.

Calendar conversion is delegated to the pinned lunar-python release. Zi Wei
normalization policy is applied separately and is always exposed in provenance.
The v1 production profile accepts Asia/Taipei civil time only; it does not
perform timezone conversion or true-solar-time correction.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from lunar_python import Solar

PROVIDER_ID = "ziwei-calendar-lunar-python"
PROVIDER_VERSION = "1.0.0"
PROFILE_ID = "ziwei.calendar.tw_v1"
DEPENDENCY_PACKAGE = "lunar_python"
DEPENDENCY_VERSION = "1.4.8"
DEPENDENCY_REPOSITORY = "6tail/lunar-python"
DEPENDENCY_REVISION = "000c8a3d74eed098d6256a28fdd51b869324c559"
DEPENDENCY_LICENSE = "MIT"
TIMEZONE = "Asia/Taipei"
CLOCK_MODE = "civil_time"
TRUE_SOLAR_TIME = "disabled"
LEAP_MONTH_POLICY = "split_after_day_15"
RAT_HOUR_POLICY = "next_day_at_23"
HOUR_BRANCHES = ("子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥")

@dataclass(frozen=True)
class GregorianBirthInput:
    year: int
    month: int
    day: int
    hour: int
    minute: int = 0
    second: int = 0
    timezone: str = TIMEZONE

    def validate(self) -> None:
        if self.timezone != TIMEZONE:
            raise ValueError(f"timezone must be {TIMEZONE} for ziwei.calendar.tw_v1")
        if not all(isinstance(v, int) for v in (self.year,self.month,self.day,self.hour,self.minute,self.second)):
            raise ValueError("Gregorian birth date/time fields must be integers")
        if not 0 <= self.hour <= 23:
            raise ValueError("hour must be in 0..23")
        if not 0 <= self.minute <= 59:
            raise ValueError("minute must be in 0..59")
        if not 0 <= self.second <= 59:
            raise ValueError("second must be in 0..59")
        try:
            datetime(self.year,self.month,self.day,self.hour,self.minute,self.second)
        except ValueError as exc:
            raise ValueError(f"invalid Gregorian birth date/time: {exc}") from exc

def hour_branch(hour: int) -> str:
    if hour in (23,0):
        return "子"
    return HOUR_BRANCHES[(hour+1)//2]

def _lunar_record(lunar: Any) -> dict[str,Any]:
    signed_month=int(lunar.getMonth())
    return {
        "year":int(lunar.getYear()),
        "month":abs(signed_month),
        "signed_month":signed_month,
        "day":int(lunar.getDay()),
        "is_leap_month":signed_month < 0,
        "time_branch":lunar.getTimeZhi(),
    }

def _apply_leap_month_policy(lunar_record: dict[str,Any]) -> tuple[int,str]:
    month=int(lunar_record["month"])
    day=int(lunar_record["day"])
    if not lunar_record["is_leap_month"]:
        return month,"non_leap_month"
    if day <= 15:
        return month,f"leap_month_{month}:day_1_15_as_same_month"
    return (month % 12)+1,f"leap_month_{month}:day_16_plus_as_next_month"

def normalize_gregorian_birth(data: GregorianBirthInput) -> dict[str,Any]:
    data.validate()
    try:
        solar=Solar.fromYmdHms(data.year,data.month,data.day,data.hour,data.minute,data.second)
    except Exception as exc:
        raise ValueError(f"invalid Gregorian birth date/time: {exc}") from exc

    raw_lunar=_lunar_record(solar.getLunar())

    policy_solar=solar.nextDay(1) if data.hour == 23 else solar
    policy_lunar=_lunar_record(policy_solar.getLunar())
    normalized_month,leap_identity=_apply_leap_month_policy(policy_lunar)
    branch=hour_branch(data.hour)

    provenance=(
        f"{PROVIDER_ID}@{PROVIDER_VERSION};"
        f"dependency={DEPENDENCY_REPOSITORY}@{DEPENDENCY_REVISION};"
        f"profile={PROFILE_ID};timezone={TIMEZONE};clock={CLOCK_MODE};"
        f"rat_hour_policy={RAT_HOUR_POLICY};leap_month_policy={LEAP_MONTH_POLICY}"
    )
    normalized={
        "lunar_year":policy_lunar["year"],
        "lunar_month":normalized_month,
        "lunar_day":policy_lunar["day"],
        "hour_branch":branch,
        "calendar_provenance":provenance,
        "leap_month_identity":leap_identity,
    }
    return {
        "schema_version":"1.0.0",
        "provider":{
            "id":PROVIDER_ID,
            "version":PROVIDER_VERSION,
            "authority":"REFERENCE-ONLY PARITY ORACLE",
        },
        "calendar_profile":{
            "profile_id":PROFILE_ID,
            "timezone":TIMEZONE,
            "clock_mode":CLOCK_MODE,
            "true_solar_time":TRUE_SOLAR_TIME,
            "rat_hour_policy":RAT_HOUR_POLICY,
            "leap_month_policy":LEAP_MONTH_POLICY,
        },
        "dependency":{
            "package":DEPENDENCY_PACKAGE,
            "version":DEPENDENCY_VERSION,
            "repository":DEPENDENCY_REPOSITORY,
            "revision":DEPENDENCY_REVISION,
            "license":DEPENDENCY_LICENSE,
        },
        "input":{
            "calendar":"gregorian",
            "year":data.year,"month":data.month,"day":data.day,
            "hour":data.hour,"minute":data.minute,"second":data.second,
            "timezone":data.timezone,
        },
        "raw_lunar_conversion":raw_lunar,
        "policy_lunar_conversion":{
            **policy_lunar,
            "rat_hour_date_shift_applied":data.hour == 23,
            "normalized_month":normalized_month,
            "leap_month_identity":leap_identity,
        },
        "normalized_natal_input":normalized,
        "provenance":provenance,
        "boundaries":{
            "timezone_conversion_performed":False,
            "true_solar_time_applied":False,
            "raw_lunar_preserved":True,
            "ziwei_policy_separated_from_calendar_conversion":True,
        },
    }
