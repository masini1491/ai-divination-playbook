#!/usr/bin/env python3
"""Deterministic Zi Wei decadal (大限) calculation provider.

Production boundary: computes only the admitted decadal.quanji_common_v1
calculation facts from an admitted natal-baseline chart plus explicit gender
and target traditional-lunar year. It does not perform yearly/monthly/daily/
hourly calculations and grants no interpretation authority.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Literal

from tools.ziwei_natal_provider import BRANCHES, STEMS, NormalizedNatalInput, calculate_scope_a_natal

PROFILE_ID="decadal.quanji_common_v1"
PROVIDER_ID="ziwei-decadal-quanji-common-python"
PROVIDER_VERSION="1.0.0"
ENGINE_REVISION="project-reconstruction-v1"
TEMPORAL_SCOPE="decadal"
AGE_BASIS="traditional_nominal_age"
TARGET_CALENDAR="traditional_lunar_year"
PARENT_SCOPE="natal_baseline"
GENDERS=("male","female")

@dataclass(frozen=True)
class DecadalTarget:
    gender: Literal["male","female"]
    target_lunar_year: int

    def validate(self) -> None:
        if self.gender not in GENDERS:
            raise ValueError("gender must be male or female")
        if not isinstance(self.target_lunar_year,int):
            raise ValueError("target_lunar_year must be an integer")

def _direction(year_stem:str, gender:str)->str:
    if year_stem not in STEMS:
        raise ValueError(f"unsupported year stem: {year_stem}")
    yang=STEMS.index(year_stem)%2==0
    return "forward" if (yang and gender=="male") or ((not yang) and gender=="female") else "reverse"

def _branch_step(branch:str, offset:int)->str:
    i=BRANCHES.index(branch)
    return BRANCHES[(i+offset)%12]

def calculate_decadal(
    natal_input:NormalizedNatalInput,
    target:DecadalTarget,
)->dict[str,Any]:
    natal_input.validate(); target.validate()
    natal=calculate_scope_a_natal(natal_input)
    birth_year=natal_input.lunar_year
    nominal_age=target.target_lunar_year-birth_year+1
    bureau=int(natal["five_element_bureau"]["number"])
    if nominal_age < bureau:
        raise ValueError(
            f"target precedes first admitted decadal: nominal_age={nominal_age}, first_start_age={bureau}"
        )
    index=(nominal_age-bureau)//10
    if not 0 <= index <= 11:
        raise ValueError(f"target outside admitted 12-decade range: nominal_age={nominal_age}")
    start_age=bureau+10*index
    end_age=start_age+9
    start_year=birth_year+start_age-1
    end_year=birth_year+end_age-1
    direction=_direction(natal["year_pillar"]["stem"],target.gender)
    step=index if direction=="forward" else -index
    life_branch=natal["life_palace"]["branch"]
    decade_life_branch=_branch_step(life_branch,step)
    branch_to_natal_palace={x["branch"]:x["palace"] for x in natal["palaces"]}
    return {
        "schema_name":"ziwei_decadal_fact_bundle",
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
            "provider_id":natal["provider"]["id"],
            "provider_version":natal["provider"]["version"],
            "profile_id":natal["calculation_profile"]["profile_id"],
        },
        "profile":{
            "profile_id":PROFILE_ID,
            "identity_kind":"project_named_profile",
            "historical_uniqueness_claimed":False,
            "rules":{
                "direction":"yang_male_yin_female_forward_else_reverse",
                "first_palace":"life_palace",
                "first_start_age":"five_element_bureau_number",
                "age_basis":AGE_BASIS,
                "period_length_years":10,
            },
        },
        "target":{
            "calendar":TARGET_CALENDAR,
            "lunar_year":target.target_lunar_year,
            "nominal_age":nominal_age,
            "gender":target.gender,
        },
        "decadal":{
            "index":index,
            "direction":direction,
            "start_nominal_age":start_age,
            "end_nominal_age":end_age,
            "start_lunar_year":start_year,
            "end_lunar_year":end_year,
            "life_palace_branch":decade_life_branch,
            "natal_palace_at_life_branch":branch_to_natal_palace[decade_life_branch],
        },
        "provenance":{
            "research_profile":PROFILE_ID,
            "age_basis_evidence":"matharts/ziwei@596f43c43ff6fbae526314c7f668bbf346445ff1",
            "direction_and_start_research":"references/ziwei/CALCULATION_ENGINE_RESEARCH.md#Decadal",
            "calendar_provenance":natal_input.calendar_provenance,
            "leap_month_identity":natal_input.leap_month_identity,
        },
        "unsupported":{
            "yearly":"not_computed",
            "monthly":"not_computed",
            "daily":"not_computed",
            "hourly":"not_computed",
            "dynamic_interpretation":"not_admitted",
        },
        "production_authority_granted":True,
        "interpretation_authority_granted":False,
    }
