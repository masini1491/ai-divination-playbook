#!/usr/bin/env python3
"""Deterministic Zi Wei yearly (流年) calculation provider.

Computes the admitted yearly.year_branch_common_v1 facts only. The target is
an explicit traditional-lunar year. The provider preserves the compatible
decadal parent, lays yearly palace roles from the target year branch, and
reuses the separately admitted project Si Hua fact provider for target-year
stem transformations. It grants no dynamic interpretation authority.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Literal

from tools.ziwei_natal_provider import BRANCHES, PALACES, STEMS, NormalizedNatalInput, calculate_scope_a_natal
from tools.ziwei_decadal_provider import DecadalTarget, calculate_decadal
from tools.ziwei_sihua_provider import PROFILE_ID as SIHUA_PROFILE_ID, calculate_sihua

PROFILE_ID="yearly.year_branch_common_v1"
PROVIDER_ID="ziwei-yearly-year-branch-python"
PROVIDER_VERSION="1.0.0"
ENGINE_REVISION="project-reconstruction-v1"
TEMPORAL_SCOPE="yearly"
TARGET_CALENDAR="traditional_lunar_year"
YEAR_BOUNDARY_PROFILE="lunar_year_explicit_v1"
PARENT_SCOPE="decadal"

@dataclass(frozen=True)
class YearlyTarget:
    gender: Literal["male","female"]
    target_lunar_year: int

    def validate(self)->None:
        if self.gender not in ("male","female"):
            raise ValueError("gender must be male or female")
        if not isinstance(self.target_lunar_year,int):
            raise ValueError("target_lunar_year must be an integer")

def _year_pillar(year:int)->tuple[str,str]:
    return STEMS[(year-4)%10],BRANCHES[(year-4)%12]

def _yearly_palace_roles(life_branch:str)->list[dict[str,str]]:
    life_i=BRANCHES.index(life_branch)
    rows=[]
    for branch in BRANCHES[2:]+BRANCHES[:2]:
        role_i=(life_i-BRANCHES.index(branch))%12
        rows.append({"branch":branch,"yearly_palace":PALACES[role_i]})
    return rows

def calculate_yearly(natal_input:NormalizedNatalInput,target:YearlyTarget)->dict[str,Any]:
    natal_input.validate(); target.validate()
    natal=calculate_scope_a_natal(natal_input)
    decadal=calculate_decadal(
        natal_input,
        DecadalTarget(gender=target.gender,target_lunar_year=target.target_lunar_year),
    )
    nominal_age=target.target_lunar_year-natal_input.lunar_year+1
    target_stem,target_branch=_year_pillar(target.target_lunar_year)
    yearly_index=nominal_age-decadal["decadal"]["start_nominal_age"]
    if not 0 <= yearly_index <= 9:
        raise ValueError(f"target is not compatible with parent decadal: yearly_index={yearly_index}")
    roles=_yearly_palace_roles(target_branch)
    branch_to_natal_palace={x["branch"]:x["palace"] for x in natal["palaces"]}
    sihua=calculate_sihua(target_stem,sihua_profile_id=SIHUA_PROFILE_ID)
    return {
        "schema_name":"ziwei_yearly_fact_bundle",
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
            "provider_id":decadal["provider"]["id"],
            "provider_version":decadal["provider"]["version"],
            "profile_id":decadal["profile"]["profile_id"],
            "decadal_index":decadal["decadal"]["index"],
            "start_nominal_age":decadal["decadal"]["start_nominal_age"],
            "end_nominal_age":decadal["decadal"]["end_nominal_age"],
        },
        "profile":{
            "profile_id":PROFILE_ID,
            "identity_kind":"project_named_profile",
            "historical_uniqueness_claimed":False,
            "rules":{
                "life_palace":"target_lunar_year_branch",
                "palace_roles":"reverse_from_yearly_life_palace",
                "year_boundary":YEAR_BOUNDARY_PROFILE,
                "age_basis":"traditional_nominal_age",
            },
        },
        "target":{
            "calendar":TARGET_CALENDAR,
            "year_boundary_profile":YEAR_BOUNDARY_PROFILE,
            "lunar_year":target.target_lunar_year,
            "year_stem":target_stem,
            "year_branch":target_branch,
            "nominal_age":nominal_age,
            "gender":target.gender,
        },
        "yearly":{
            "index_within_decadal":yearly_index,
            "life_palace_branch":target_branch,
            "natal_palace_at_life_branch":branch_to_natal_palace[target_branch],
            "palace_roles":roles,
        },
        "yearly_sihua":{
            "profile_id":sihua["profile"]["profile_id"],
            "profile_revision":sihua["profile"]["profile_revision"],
            "year_stem":target_stem,
            "by_transform":sihua["by_transform"],
            "provider":sihua["provider"],
            "interpretation_boundary":sihua["interpretation_boundary"],
        },
        "provenance":{
            "primary_calculation_reference":"matharts/ziwei@596f43c43ff6fbae526314c7f668bbf346445ff1",
            "primary_reference_path":"crates/ziwei/src/rules.rs",
            "comparator_reference":"SylarLong/iztro@2c7ef9be669df7b19d1799f4dce335fed3794f78",
            "comparator_reference_path":"src/astro/FunctionalAstrolabe.ts",
            "calendar_provenance":natal_input.calendar_provenance,
            "leap_month_identity":natal_input.leap_month_identity,
        },
        "unsupported":{
            "monthly":"not_computed",
            "daily":"not_computed",
            "hourly":"not_computed",
            "flow_stars":"not_admitted",
            "dynamic_interpretation":"not_admitted",
        },
        "production_authority_granted":True,
        "interpretation_authority_granted":False,
    }
