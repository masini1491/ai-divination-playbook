#!/usr/bin/env python3
"""Deterministic Zi Wei daily (流日) calculation provider.

Production boundary: computes only daily.monthly_parent_lunar_day_v1 palace
calculation facts from a compatible admitted monthly parent plus explicit
normalized lunar-day identity. The daily Life Palace advances from the monthly
Life Palace by lunar_day - 1. Day pillars, daily Si Hua, flow stars, hourly
facts and dynamic interpretation remain unadmitted.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Literal

from tools.ziwei_natal_provider import BRANCHES, PALACES, NormalizedNatalInput, calculate_scope_a_natal
from tools.ziwei_monthly_provider import MonthlyTarget, calculate_monthly

PROFILE_ID="daily.monthly_parent_lunar_day_v1"
PROVIDER_ID="ziwei-daily-monthly-parent-python"
PROVIDER_VERSION="1.0.0"
ENGINE_REVISION="project-reconstruction-v1"
TEMPORAL_SCOPE="daily"
TARGET_CALENDAR="normalized_traditional_lunar_day"
DAY_BOUNDARY_PROFILE="explicit_lunar_day_identity_v1"
PARENT_SCOPE="monthly"

@dataclass(frozen=True)
class DailyTarget:
    gender: Literal["male","female"]
    target_lunar_year: int
    target_lunar_month: int
    target_lunar_day: int
    target_is_leap_month: bool
    target_calendar_provenance: str

    def validate(self)->None:
        if self.gender not in ("male","female"):
            raise ValueError("gender must be male or female")
        if not isinstance(self.target_lunar_year,int):
            raise ValueError("target_lunar_year must be an integer")
        if not isinstance(self.target_lunar_month,int) or not 1 <= self.target_lunar_month <= 12:
            raise ValueError("target_lunar_month must be in 1..12")
        if not isinstance(self.target_lunar_day,int) or not 1 <= self.target_lunar_day <= 30:
            raise ValueError("target_lunar_day must be in 1..30")
        if not isinstance(self.target_is_leap_month,bool):
            raise ValueError("target_is_leap_month must be boolean")
        if not isinstance(self.target_calendar_provenance,str) or not self.target_calendar_provenance.strip():
            raise ValueError("target_calendar_provenance is required")

def _palace_roles(life_branch:str)->list[dict[str,str]]:
    life_i=BRANCHES.index(life_branch)
    return [
        {"branch":branch,"daily_palace":PALACES[(life_i-BRANCHES.index(branch))%12]}
        for branch in BRANCHES[2:]+BRANCHES[:2]
    ]

def calculate_daily(natal_input:NormalizedNatalInput,target:DailyTarget)->dict[str,Any]:
    natal_input.validate(); target.validate()
    natal=calculate_scope_a_natal(natal_input)
    monthly=calculate_monthly(
        natal_input,
        MonthlyTarget(
            gender=target.gender,
            target_lunar_year=target.target_lunar_year,
            target_lunar_month=target.target_lunar_month,
            target_lunar_day=target.target_lunar_day,
            target_is_leap_month=target.target_is_leap_month,
            target_calendar_provenance=target.target_calendar_provenance,
        ),
    )
    monthly_life_branch=monthly["monthly"]["life_palace_branch"]
    daily_life_branch=BRANCHES[(BRANCHES.index(monthly_life_branch)+target.target_lunar_day-1)%12]
    roles=_palace_roles(daily_life_branch)
    branch_to_natal_palace={x["branch"]:x["palace"] for x in natal["palaces"]}
    return {
        "schema_name":"ziwei_daily_fact_bundle",
        "schema_version":"1.0.0",
        "provider":{
            "id":PROVIDER_ID,
            "version":PROVIDER_VERSION,
            "authority":"PRODUCTION_ADMITTED_CALCULATION_ONLY",
            "engine_revision":ENGINE_REVISION,
        },
        "temporal_scope":TEMPORAL_SCOPE,
        "parent_scope":{
            "scope":PARENT_SCOPE,
            "provider_id":monthly["provider"]["id"],
            "provider_version":monthly["provider"]["version"],
            "profile_id":monthly["profile"]["profile_id"],
            "target_lunar_year":monthly["target"]["lunar_year"],
            "logical_lunar_month":monthly["target"]["logical_lunar_month"],
            "effective_month":monthly["target"]["effective_month"],
            "leap_month_identity":monthly["target"]["leap_month_identity"],
            "monthly_life_palace_branch":monthly_life_branch,
        },
        "profile":{
            "profile_id":PROFILE_ID,
            "identity_kind":"project_named_profile",
            "historical_uniqueness_claimed":False,
            "rules":{
                "life_palace":"monthly_life_palace_plus_lunar_day_minus_1",
                "palace_roles":"reverse_from_daily_life_palace",
                "day_boundary":DAY_BOUNDARY_PROFILE,
                "parent_scope":"monthly",
            },
        },
        "target":{
            "calendar":TARGET_CALENDAR,
            "calendar_provenance":target.target_calendar_provenance,
            "lunar_year":target.target_lunar_year,
            "logical_lunar_month":target.target_lunar_month,
            "lunar_day":target.target_lunar_day,
            "is_leap_month":target.target_is_leap_month,
            "effective_month":monthly["target"]["effective_month"],
            "leap_month_identity":monthly["target"]["leap_month_identity"],
            "day_boundary_profile":DAY_BOUNDARY_PROFILE,
            "gender":target.gender,
        },
        "daily":{
            "life_palace_branch":daily_life_branch,
            "natal_palace_at_life_branch":branch_to_natal_palace[daily_life_branch],
            "palace_roles":roles,
        },
        "provenance":{
            "primary_calculation_reference":"RedSC1/js-ephemeris-lite@559d4957bc063a6e03a3c810066be4eccf3ea2be",
            "primary_reference_path":"packages/ziwei/src/limits.ts",
            "comparator_reference":"SylarLong/iztro@2c7ef9be669df7b19d1799f4dce335fed3794f78",
            "comparator_reference_path":"src/astro/FunctionalAstrolabe.ts",
            "calendar_policy_owner":"ZIWEI_CALENDAR_ADMISSION_V1.json",
            "birth_calendar_provenance":natal_input.calendar_provenance,
            "birth_leap_month_identity":natal_input.leap_month_identity,
        },
        "unsupported":{
            "day_pillar":"not_computed",
            "daily_sihua":"not_computed",
            "flow_stars":"not_computed",
            "hourly":"not_computed",
            "dynamic_interpretation":"not_admitted",
        },
        "production_authority_granted":True,
        "interpretation_authority_granted":False,
    }
