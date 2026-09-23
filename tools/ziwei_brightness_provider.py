#!/usr/bin/env python3
"""Optional deterministic brightness fact provider for Zi Wei Scope-A.

This module admits one named implementation profile only. It does not claim a
unique historical brightness table and it does not create interpretation
doctrine from brightness labels.
"""
from __future__ import annotations

from typing import Any, Mapping

from tools.ziwei_natal_provider import BRANCHES, MAJOR_STARS

PROFILE_ID = "ziwei.brightness.iztro_v1"
PROVIDER_ID = "ziwei-brightness-iztro-python"
PROVIDER_VERSION = "1.0.0"
SOURCE_REPOSITORY = "SylarLong/iztro"
SOURCE_REVISION = "2c7ef9be669df7b19d1799f4dce335fed3794f78"
SOURCE_PATH = "src/data/stars.ts"
SOURCE_BRANCH_ORDER = ("寅","卯","辰","巳","午","未","申","酉","戌","亥","子","丑")
LABELS = {
    "miao":"廟",
    "wang":"旺",
    "de":"得",
    "li":"利",
    "ping":"平",
    "bu":"不",
    "xian":"陷",
}
_TABLE = {
    "紫微": ("wang","wang","de","wang","miao","miao","wang","wang","de","wang","ping","miao"),
    "天機": ("de","wang","li","ping","miao","xian","de","wang","li","ping","miao","xian"),
    "太陽": ("wang","miao","wang","wang","wang","de","de","ping","bu","xian","xian","bu"),
    "武曲": ("de","li","miao","ping","wang","miao","de","li","miao","ping","wang","miao"),
    "天同": ("li","ping","ping","miao","xian","bu","wang","ping","ping","miao","wang","bu"),
    "廉貞": ("miao","ping","li","xian","ping","li","miao","ping","li","xian","ping","li"),
    "天府": ("miao","de","miao","de","wang","miao","de","wang","miao","de","miao","miao"),
    "太陰": ("wang","xian","xian","xian","bu","bu","li","wang","wang","miao","miao","miao"),
    "貪狼": ("ping","li","miao","xian","wang","miao","ping","li","miao","xian","wang","miao"),
    "巨門": ("miao","miao","xian","wang","wang","bu","miao","miao","xian","wang","wang","bu"),
    "天相": ("miao","xian","de","de","miao","de","miao","xian","de","de","miao","miao"),
    "天梁": ("miao","miao","miao","xian","miao","wang","xian","de","miao","xian","miao","wang"),
    "七殺": ("miao","wang","miao","ping","wang","miao","miao","wang","miao","ping","wang","miao"),
    "破軍": ("de","xian","wang","ping","miao","wang","de","xian","wang","ping","miao","wang"),
}

def calculate_brightness(major_star_placements: Mapping[str,str]) -> dict[str,Any]:
    if set(major_star_placements) != set(MAJOR_STARS):
        missing=sorted(set(MAJOR_STARS)-set(major_star_placements))
        extra=sorted(set(major_star_placements)-set(MAJOR_STARS))
        raise ValueError(f"major_star_placements identity mismatch: missing={missing}, extra={extra}")
    records=[]
    facts=["fact_available:dignity"]
    for star in MAJOR_STARS:
        branch=major_star_placements[star]
        if branch not in BRANCHES:
            raise ValueError(f"invalid branch for {star}: {branch}")
        idx=SOURCE_BRANCH_ORDER.index(branch)
        code=_TABLE[star][idx]
        label=LABELS[code]
        records.append({"star":star,"branch":branch,"brightness_code":code,"brightness_label":label})
        facts.extend((f"dignity:{star}:{code}",f"dignity_label:{star}:{label}"))
    return {
        "schema_version":"1.0.0",
        "provider":{
            "id":PROVIDER_ID,
            "version":PROVIDER_VERSION,
            "authority":"OPTIONAL BRIGHTNESS V1 PRODUCTION-ADMITTED PROFILE",
        },
        "brightness_profile":{
            "profile_id":PROFILE_ID,
            "identity_kind":"named_implementation_profile",
            "historical_uniqueness_claimed":False,
            "source_repository":SOURCE_REPOSITORY,
            "source_revision":SOURCE_REVISION,
            "source_path":SOURCE_PATH,
            "branch_order":"寅→丑",
        },
        "records":records,
        "retrieval_facts":facts,
        "interpretation_boundary":"facts_only_no_brightness_only_doctrine",
        "scientific_predictive_validity_claimed":False,
    }
