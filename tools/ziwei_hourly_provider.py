#!/usr/bin/env python3
"""Deterministic Zi Wei hourly (流時) calculation provider.

Production boundary: computes only hourly.daily_parent_hour_branch_next_day_23_v1
palace calculation facts from a compatible admitted daily parent plus an
explicit normalized lunar hour identity. The hourly Life Palace advances from
the daily Life Palace by the target hour-branch index. Rat-hour date assignment
is upstream normalization under the admitted project policy next_day_at_23.
Physical hour pillars, hourly Si Hua, flow stars and dynamic interpretation
remain unadmitted.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Literal

from tools.ziwei_natal_provider import BRANCHES, PALACES, NormalizedNatalInput, calculate_scope_a_natal
from tools.ziwei_daily_provider import DailyTarget, calculate_daily

PROFILE_ID="hourly.daily_parent_hour_branch_next_day_23_v1"
PROVIDER_ID="ziwei-hourly-daily-parent-python"
PROVIDER_VERSION="1.0.0"
ENGINE_REVISION="project-reconstruction-v1"
TEMPORAL_SCOPE="hourly"
TARGET_CALENDAR="normalized_traditional_lunar_hour"
RAT_HOUR_POLICY="next_day_at_23"
PARENT_SCOPE="daily"

@dataclass(frozen=True)
class HourlyTarget:
    gender: Literal["male","female"]
    target_lunar_year: int
    target_lunar_month: int
    target_lunar_day: int
    target_is_leap_month: bool
    target_hour_branch: str
    target_rat_hour_policy: str
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
        if self.target_hour_branch not in BRANCHES:
            raise ValueError("target_hour_branch must be a traditional Earthly Branch")
        if self.target_rat_hour_policy != RAT_HOUR_POLICY:
            raise ValueError(f"target_rat_hour_policy must be {RAT_HOUR_POLICY}")
        if not isinstance(self.target_calendar_provenance,str) or not self.target_calendar_provenance.strip():
            raise ValueError("target_calendar_provenance is required")

def _palace_roles(life_branch:str)->list[dict[str,str]]:
    life_i=BRANCHES.index(life_branch)
    return [
        {"branch":branch,"hourly_palace":PALACES[(life_i-BRANCHES.index(branch))%12]}
        for branch in BRANCHES[2:]+BRANCHES[:2]
    ]

def calculate_hourly(natal_input:NormalizedNatalInput,target:HourlyTarget)->dict[str,Any]:
    natal_input.validate(); target.validate()
    natal=calculate_scope_a_natal(natal_input)
    daily=calculate_daily(
        natal_input,
        DailyTarget(
            gender=target.gender,
            target_lunar_year=target.target_lunar_year,
            target_lunar_month=target.target_lunar_month,
            target_lunar_day=target.target_lunar_day,
            target_is_leap_month=target.target_is_leap_month,
            target_calendar_provenance=target.target_calendar_provenance,
        ),
    )
    daily_life_branch=daily["daily"]["life_palace_branch"]
    hour_index=BRANCHES.index(target.target_hour_branch)
    hourly_life_branch=BRANCHES[(BRANCHES.index(daily_life_branch)+hour_index)%12]
    roles=_palace_roles(hourly_life_branch)
    branch_to_natal_palace={x["branch"]:x["palace"] for x in natal["palaces"]}
    return {
        "schema_name":"ziwei_hourly_fact_bundle",
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
            "provider_id":daily["provider"]["id"],
            "provider_version":daily["provider"]["version"],
            "profile_id":daily["profile"]["profile_id"],
            "target_lunar_year":daily["target"]["lunar_year"],
            "logical_lunar_month":daily["target"]["logical_lunar_month"],
            "lunar_day":daily["target"]["lunar_day"],
            "effective_month":daily["target"]["effective_month"],
            "leap_month_identity":daily["target"]["leap_month_identity"],
            "daily_life_palace_branch":daily_life_branch,
        },
        "profile":{
            "profile_id":PROFILE_ID,
            "identity_kind":"project_named_profile",
            "historical_uniqueness_claimed":False,
            "rules":{
                "life_palace":"daily_life_palace_plus_hour_branch_index",
                "palace_roles":"reverse_from_hourly_life_palace",
                "rat_hour_policy":RAT_HOUR_POLICY,
                "parent_scope":"daily",
            },
        },
        "target":{
            "calendar":TARGET_CALENDAR,
            "calendar_provenance":target.target_calendar_provenance,
            "lunar_year":target.target_lunar_year,
            "logical_lunar_month":target.target_lunar_month,
            "lunar_day":target.target_lunar_day,
            "is_leap_month":target.target_is_leap_month,
            "effective_month":daily["target"]["effective_month"],
            "leap_month_identity":daily["target"]["leap_month_identity"],
            "hour_branch":target.target_hour_branch,
            "hour_branch_index":hour_index,
            "rat_hour_policy":RAT_HOUR_POLICY,
            "gender":target.gender,
        },
        "hourly":{
            "life_palace_branch":hourly_life_branch,
            "natal_palace_at_life_branch":branch_to_natal_palace[hourly_life_branch],
            "palace_roles":roles,
        },
        "provenance":{
            "primary_calculation_reference":"RedSC1/js-ephemeris-lite@559d4957bc063a6e03a3c810066be4eccf3ea2be",
            "primary_reference_path":"packages/ziwei/src/limits.ts",
            "comparator_reference":"SylarLong/iztro@2c7ef9be669df7b19d1799f4dce335fed3794f78",
            "comparator_reference_path":"src/astro/FunctionalAstrolabe.ts",
            "calendar_policy_owner":"admissions/ziwei/ZIWEI_CALENDAR_ADMISSION_V1.json",
            "rat_hour_policy_owner":"admissions/ziwei/ZIWEI_CALENDAR_ADMISSION_V1.json",
            "birth_calendar_provenance":natal_input.calendar_provenance,
            "birth_leap_month_identity":natal_input.leap_month_identity,
        },
        "unsupported":{
            "physical_hour_pillar":"not_computed",
            "alternate_rat_hour_policy":"not_admitted",
            "hourly_sihua":"not_computed",
            "flow_stars":"not_computed",
            "dynamic_interpretation":"not_admitted",
        },
        "production_authority_granted":True,
        "interpretation_authority_granted":False,
    }
