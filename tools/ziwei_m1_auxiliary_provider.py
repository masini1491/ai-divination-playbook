#!/usr/bin/env python3
"""Deterministic M1 auxiliary-star provider for Zi Wei natal baseline."""
from __future__ import annotations
from typing import Any

from tools.ziwei_natal_provider import BRANCHES, MAJOR_STARS

PROFILE_ID="ziwei.auxiliary.m1.common_v1"
PROVIDER_ID="ziwei-m1-auxiliary-python"
PROVIDER_VERSION="1.0.0"
STARS=("天魁","天鉞","祿存","天馬","擎羊","陀羅","火星","鈴星","地空","地劫")
MALEFICS=frozenset(("擎羊","陀羅","火星","鈴星","地空","地劫"))

_LU_BY_STEM={
    "甲":"寅","乙":"卯","丙":"巳","丁":"午","戊":"巳",
    "己":"午","庚":"申","辛":"酉","壬":"亥","癸":"子",
}
_KUI_YUE_BY_STEM={
    "甲":("丑","未"),"乙":("子","申"),"丙":("亥","酉"),"丁":("亥","酉"),"戊":("丑","未"),
    "己":("子","申"),"庚":("丑","未"),"辛":("午","寅"),"壬":("卯","巳"),"癸":("卯","巳"),
}
_MA_BY_BRANCH={
    "寅":"申","午":"申","戌":"申",
    "申":"寅","子":"寅","辰":"寅",
    "巳":"亥","酉":"亥","丑":"亥",
    "亥":"巳","卯":"巳","未":"巳",
}
_HUO_LING_BASE={
    "寅":("丑","卯"),"午":("丑","卯"),"戌":("丑","卯"),
    "申":("寅","戌"),"子":("寅","戌"),"辰":("寅","戌"),
    "巳":("卯","戌"),"酉":("卯","戌"),"丑":("卯","戌"),
    "亥":("酉","戌"),"卯":("酉","戌"),"未":("酉","戌"),
}

def _shift(branch:str,delta:int)->str:
    return BRANCHES[(BRANCHES.index(branch)+delta)%12]

def calculate_m1_auxiliary(
    year_stem:str,
    year_branch:str,
    hour_branch:str,
    major_star_placements:dict[str,str],
)->dict[str,Any]:
    if year_stem not in _LU_BY_STEM or year_stem not in _KUI_YUE_BY_STEM:
        raise ValueError(f"unsupported year stem: {year_stem}")
    if year_branch not in _MA_BY_BRANCH or year_branch not in _HUO_LING_BASE:
        raise ValueError(f"unsupported year branch: {year_branch}")
    if hour_branch not in BRANCHES:
        raise ValueError(f"unsupported hour branch: {hour_branch}")
    if set(major_star_placements)!=set(MAJOR_STARS):
        raise ValueError("M1 auxiliary provider requires the admitted 14-major-star placement set")

    lu=_LU_BY_STEM[year_stem]
    kui,yue=_KUI_YUE_BY_STEM[year_stem]
    hour_index=BRANCHES.index(hour_branch)
    huo_base,ling_base=_HUO_LING_BASE[year_branch]
    placements={
        "天魁":kui,
        "天鉞":yue,
        "祿存":lu,
        "天馬":_MA_BY_BRANCH[year_branch],
        "擎羊":_shift(lu,1),
        "陀羅":_shift(lu,-1),
        "火星":_shift(huo_base,hour_index),
        "鈴星":_shift(ling_base,hour_index),
        "地空":_shift("亥",-hour_index),
        "地劫":_shift("亥",hour_index),
    }
    facts=["fact_available:m1_auxiliary_stars",*(f"star_present:{s}" for s in STARS)]
    relations=[]
    for subject,branch in major_star_placements.items():
        i=BRANCHES.index(branch)
        sanfang={BRANCHES[i],BRANCHES[(i+4)%12],BRANCHES[(i+8)%12]}
        related_malefic=False
        for auxiliary,aux_branch in placements.items():
            if aux_branch in sanfang:
                facts.append(f"modifier_present:{subject}:{auxiliary}")
                relations.append({"subject":subject,"auxiliary":auxiliary,"relation":"self_or_sanfang"})
                if auxiliary in MALEFICS:
                    related_malefic=True
        if related_malefic:
            facts.append(f"modifier_present:{subject}:malefic_stars")

    return {
        "schema_version":"1.0.0",
        "provider":{"id":PROVIDER_ID,"version":PROVIDER_VERSION,"authority":"OPTIONAL M1 PRODUCTION ADMISSION"},
        "profile":{
            "profile_id":PROFILE_ID,
            "temporal_scope":"natal_baseline",
            "implementation_references":[
                {"repository":"SylarLong/iztro","revision":"2c7ef9be669df7b19d1799f4dce335fed3794f78","path":"src/star/location.ts"},
                {"repository":"airicyu/fortel-ziweidoushu","revision":"2620cc895395f9f6994abd4927e739d31015c67d","path":"src/model/minorStar.ts"},
            ],
            "placement_rule_families":{
                "魁鉞":"year_stem",
                "祿存羊陀":"year_stem",
                "天馬":"year_branch_trine",
                "火鈴":"year_branch_group_plus_hour_branch",
                "空劫":"hour_branch_from_hai",
            },
            "relation_scope":"self_or_sanfang_only",
        },
        "placements":placements,
        "relations":relations,
        "retrieval_facts":facts,
        "production_authority_granted":True,
    }
