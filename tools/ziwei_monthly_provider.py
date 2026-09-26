#!/usr/bin/env python3
"""Deterministic Zi Wei monthly (流月) calculation provider.

Production boundary: computes only monthly.doujun_effective_month_split15_v1
calculation facts from an admitted yearly parent plus explicit normalized lunar
month target. The target leap-month policy is the project default
split_after_day_15. Leap-month 12 day>15 cross-year rollover remains fail-closed.
No monthly Si Hua, flow stars, daily/hourly facts, or interpretation are admitted.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Literal

from tools.ziwei_natal_provider import BRANCHES, PALACES, STEMS, NormalizedNatalInput, calculate_scope_a_natal
from tools.ziwei_yearly_provider import YearlyTarget, calculate_yearly

PROFILE_ID="monthly.doujun_effective_month_split15_v1"
PROVIDER_ID="ziwei-monthly-doujun-python"
PROVIDER_VERSION="1.0.0"
ENGINE_REVISION="project-reconstruction-v1"
TEMPORAL_SCOPE="monthly"
TARGET_CALENDAR="normalized_traditional_lunar_month"
MONTH_BOUNDARY_PROFILE="lunar_month_split_after_day_15_v1"
PARENT_SCOPE="yearly"

@dataclass(frozen=True)
class MonthlyTarget:
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
        if not 1 <= self.target_lunar_month <= 12:
            raise ValueError("target_lunar_month must be in 1..12")
        if not 1 <= self.target_lunar_day <= 30:
            raise ValueError("target_lunar_day must be in 1..30")
        if not isinstance(self.target_is_leap_month,bool):
            raise ValueError("target_is_leap_month must be boolean")
        if not isinstance(self.target_calendar_provenance,str) or not self.target_calendar_provenance.strip():
            raise ValueError("target_calendar_provenance is required")

def _effective_target_month(target:MonthlyTarget)->tuple[int,str]:
    month=target.target_lunar_month
    if not target.target_is_leap_month:
        return month,"non_leap_month"
    if target.target_lunar_day <= 15:
        return month,f"leap_month_{month}:day_1_15_as_same_month"
    if month == 12:
        raise ValueError("leap month 12 day>15 cross-year rollover is not admitted")
    return month+1,f"leap_month_{month}:day_16_plus_as_next_month"

def _palace_roles(life_branch:str)->list[dict[str,str]]:
    life_i=BRANCHES.index(life_branch)
    return [
        {"branch":branch,"monthly_palace":PALACES[(life_i-BRANCHES.index(branch))%12]}
        for branch in BRANCHES[2:]+BRANCHES[:2]
    ]

def _month_stem(year_stem:str,effective_month:int)->str:
    start_tiger=(STEMS.index(year_stem)%5)*2+2
    return STEMS[(start_tiger+effective_month-1)%10]

def calculate_monthly(natal_input:NormalizedNatalInput,target:MonthlyTarget)->dict[str,Any]:
    natal_input.validate(); target.validate()
    natal=calculate_scope_a_natal(natal_input)
    yearly=calculate_yearly(
        natal_input,
        YearlyTarget(gender=target.gender,target_lunar_year=target.target_lunar_year),
    )
    effective_month,leap_identity=_effective_target_month(target)
    year_branch=yearly["target"]["year_branch"]
    year_stem=yearly["target"]["year_stem"]
    birth_effective_month=natal_input.lunar_month
    birth_hour_index=BRANCHES.index(natal_input.hour_branch)
    year_branch_index=BRANCHES.index(year_branch)

    doujun_index=(year_branch_index-(birth_effective_month-1)+birth_hour_index)%12
    doujun_branch=BRANCHES[doujun_index]
    monthly_life_branch=BRANCHES[(doujun_index+effective_month-1)%12]
    month_stem=_month_stem(year_stem,effective_month)
    roles=_palace_roles(monthly_life_branch)
    branch_to_natal_palace={x["branch"]:x["palace"] for x in natal["palaces"]}

    return {
        "schema_name":"ziwei_monthly_fact_bundle",
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
            "provider_id":yearly["provider"]["id"],
            "provider_version":yearly["provider"]["version"],
            "profile_id":yearly["profile"]["profile_id"],
            "target_lunar_year":yearly["target"]["lunar_year"],
            "year_stem":year_stem,
            "year_branch":year_branch,
            "yearly_life_palace_branch":yearly["yearly"]["life_palace_branch"],
        },
        "profile":{
            "profile_id":PROFILE_ID,
            "identity_kind":"project_named_profile",
            "historical_uniqueness_claimed":False,
            "rules":{
                "doujun":"target_year_branch_minus_birth_effective_month_plus_birth_hour",
                "life_palace":"doujun_plus_effective_month_minus_1",
                "palace_roles":"reverse_from_monthly_life_palace",
                "month_boundary":MONTH_BOUNDARY_PROFILE,
                "leap_month_policy":"split_after_day_15",
                "palace_month_strategy":"effective_month",
            },
        },
        "target":{
            "calendar":TARGET_CALENDAR,
            "calendar_provenance":target.target_calendar_provenance,
            "lunar_year":target.target_lunar_year,
            "logical_lunar_month":target.target_lunar_month,
            "lunar_day":target.target_lunar_day,
            "is_leap_month":target.target_is_leap_month,
            "effective_month":effective_month,
            "leap_month_identity":leap_identity,
            "month_boundary_profile":MONTH_BOUNDARY_PROFILE,
            "gender":target.gender,
        },
        "monthly":{
            "doujun_branch":doujun_branch,
            "life_palace_branch":monthly_life_branch,
            "month_stem":month_stem,
            "natal_palace_at_life_branch":branch_to_natal_palace[monthly_life_branch],
            "palace_roles":roles,
        },
        "provenance":{
            "primary_calculation_reference":"RedSC1/js-ephemeris-lite@559d4957bc063a6e03a3c810066be4eccf3ea2be",
            "primary_reference_path":"packages/ziwei/src/limits.ts",
            "comparator_reference":"SylarLong/iztro@2c7ef9be669df7b19d1799f4dce335fed3794f78",
            "comparator_reference_path":"src/astro/FunctionalAstrolabe.ts",
            "leap_policy_owner":"ZIWEI_CALENDAR_ADMISSION_V1.json",
            "birth_calendar_provenance":natal_input.calendar_provenance,
            "birth_leap_month_identity":natal_input.leap_month_identity,
        },
        "unsupported":{
            "monthly_sihua":"not_computed",
            "flow_stars":"not_computed",
            "daily":"not_computed",
            "hourly":"not_computed",
            "dynamic_interpretation":"not_admitted",
            "leap_month_12_day_16_plus_cross_year":"not_admitted",
        },
        "production_authority_granted":True,
        "interpretation_authority_granted":False,
    }
