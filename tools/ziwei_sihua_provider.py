#!/usr/bin/env python3
"""Deterministic Four Transformations provider for admitted Zi Wei sihua_v1.

This provider exposes profile-bound Four-Transformation facts only. It does
not create transformed-star interpretation doctrine; production interpretation
is separately allowlisted by ZIWEI_SIHUA_ADMISSION_V1.json and the source-explicit
claim registry.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from tools.ziwei_natal_provider import STEMS

PROFILE_ID="sihua.default_v1"
PROFILE_REVISION="1.0.0"
PROVIDER_ID="ziwei-sihua-project-default-python"
PROVIDER_VERSION="1.0.0"
TRANSFORMS=("祿","權","科","忌")
SOURCE_REPOSITORY="matharts/ziwei"
SOURCE_REVISION="596f43c43ff6fbae526314c7f668bbf346445ff1"
SOURCE_PATH="crates/ziwei/src/rules.rs"

# Pinned complete 10x4 base table from matharts/ziwei@SOURCE_REVISION.
# Order is 祿, 權, 科, 忌.
_BASE_TABLE={
    "甲":("廉貞","破軍","武曲","太陽"),
    "乙":("天機","天梁","紫微","太陰"),
    "丙":("天同","天機","文昌","廉貞"),
    "丁":("太陰","天同","天機","巨門"),
    "戊":("貪狼","太陰","右弼","天機"),
    "己":("武曲","貪狼","天梁","文曲"),
    "庚":("太陽","武曲","太陰","天同"),
    "辛":("巨門","太陽","文曲","文昌"),
    "壬":("天梁","紫微","左輔","武曲"),
    "癸":("破軍","巨門","太陰","貪狼"),
}

# Project-level profile decision from FOUR_TRANSFORMATION_VARIANT_REGISTRY.md.
# It must not be relabeled as matharts/common/Quanji/Quanshu/Zhongzhou.
_PROJECT_OVERRIDES={
    "庚":{"科":"天府"},
}

@dataclass(frozen=True)
class SihuaProfile:
    profile_id:str=PROFILE_ID

    def validate(self)->None:
        if self.profile_id!=PROFILE_ID:
            raise ValueError(f"unsupported sihua_profile_id: {self.profile_id}")

def _profile_table(profile:SihuaProfile)->dict[str,tuple[str,str,str,str]]:
    profile.validate()
    table={stem:tuple(stars) for stem,stars in _BASE_TABLE.items()}
    for stem,changes in _PROJECT_OVERRIDES.items():
        stars=list(table[stem])
        for transform,star in changes.items():
            stars[TRANSFORMS.index(transform)]=star
        table[stem]=tuple(stars)
    return table

def calculate_sihua(year_stem:str, *, sihua_profile_id:str=PROFILE_ID)->dict[str,Any]:
    if year_stem not in STEMS:
        raise ValueError(f"invalid year_stem: {year_stem}")
    profile=SihuaProfile(sihua_profile_id)
    table=_profile_table(profile)
    stars=table[year_stem]
    records=[
        {
            "year_stem":year_stem,
            "transform_kind":transform,
            "star":star,
            "sihua_profile_id":PROFILE_ID,
            "profile_revision":PROFILE_REVISION,
            "source_provenance":{
                "base_repository":SOURCE_REPOSITORY,
                "base_revision":SOURCE_REVISION,
                "base_path":SOURCE_PATH,
                "profile_decision_owner":"references/ziwei/FOUR_TRANSFORMATION_VARIANT_REGISTRY.md",
                "profile_decision_identity":"PROJECT-DEFAULT-V1",
            },
            "engine":{
                "provider_id":PROVIDER_ID,
                "provider_version":PROVIDER_VERSION,
            },
        }
        for transform,star in zip(TRANSFORMS,stars)
    ]
    retrieval_facts=[
        "fact_available:sihua",
        f"sihua_profile:{PROFILE_ID}",
        *(f"sihua:{year_stem}:{transform}:{star}" for transform,star in zip(TRANSFORMS,stars)),
    ]
    return {
        "schema_version":"1.0.0",
        "provider":{
            "id":PROVIDER_ID,
            "version":PROVIDER_VERSION,
            "authority":"OPTIONAL SIHUA V1 PRODUCTION-ADMITTED FACT PROVIDER",
        },
        "profile":{
            "profile_id":PROFILE_ID,
            "profile_revision":PROFILE_REVISION,
            "identity_kind":"project_composite_profile",
            "historical_uniqueness_claimed":False,
            "scientific_validity_claimed":False,
            "selection_basis":"project user-perceived-fit research; not historical/scientific uniqueness",
        },
        "base_source":{
            "repository":SOURCE_REPOSITORY,
            "revision":SOURCE_REVISION,
            "path":SOURCE_PATH,
            "role":"complete_10_stem_base_table",
        },
        "project_overrides":[
            {
                "year_stem":stem,
                "transform_kind":transform,
                "base_star":_BASE_TABLE[stem][TRANSFORMS.index(transform)],
                "selected_star":star,
                "decision_owner":"references/ziwei/FOUR_TRANSFORMATION_VARIANT_REGISTRY.md",
                "decision_identity":"PROJECT-DEFAULT-V1",
            }
            for stem,changes in sorted(_PROJECT_OVERRIDES.items())
            for transform,star in sorted(changes.items(),key=lambda kv:TRANSFORMS.index(kv[0]))
        ],
        "year_stem":year_stem,
        "records":records,
        "by_transform":{record["transform_kind"]:record["star"] for record in records},
        "retrieval_facts":retrieval_facts,
        "interpretation_boundary":{
            "transformed_star_claims_admitted_by_provider":False,
            "generic_transform_outcome_dictionary_admitted":False,
            "cross_profile_averaging_allowed":False,
        },
        "production_authority_granted":True,
    }
