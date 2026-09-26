#!/usr/bin/env python3
"""Deterministic Zi Wei Scope-A natal fact provider.

Boundary: accepts already-normalized traditional-lunar birth facts. It does not
perform Gregorian/lunisolar conversion, leap-month normalization, brightness,
auxiliary-star, Four-Transformation, or dynamic calculations.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

BRANCHES = ("子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥")
STEMS = ("甲","乙","丙","丁","戊","己","庚","辛","壬","癸")
PALACES = ("命宮","兄弟宮","夫妻宮","子女宮","財帛宮","疾厄宮","遷移宮","奴僕宮","官祿宮","田宅宮","福德宮","父母宮")
MAJOR_STARS = ("紫微","天機","太陽","武曲","天同","廉貞","天府","太陰","貪狼","巨門","天相","天梁","七殺","破軍")
BUREAU_TABLE = (
    (4,2,6,4,2,6),
    (2,6,5,2,6,5),
    (6,5,3,6,5,3),
    (5,3,4,5,3,4),
    (3,4,2,3,4,2),
)
BUREAU_LABELS = {2:"水二局",3:"木三局",4:"金四局",5:"土五局",6:"火六局"}
PROFILE_ID = "ziwei.scope_a.natal_v0"
RESEARCH_PROFILE = "ziwei.baseline.tw_v1"
PROVIDER_ID = "ziwei-scope-a-natal-python"
PROVIDER_VERSION = "0.2.0"

@dataclass(frozen=True)
class NormalizedNatalInput:
    lunar_year: int
    lunar_month: int
    lunar_day: int
    hour_branch: str
    calendar_provenance: str
    leap_month_identity: str = "normalized_upstream"

    def validate(self) -> None:
        if not isinstance(self.lunar_year, int):
            raise ValueError("lunar_year must be an integer")
        if not 1 <= self.lunar_month <= 12:
            raise ValueError("lunar_month must be in 1..12 after upstream normalization")
        if not 1 <= self.lunar_day <= 30:
            raise ValueError("lunar_day must be in 1..30")
        if self.hour_branch not in BRANCHES:
            raise ValueError("hour_branch must be one of 子丑寅卯辰巳午未申酉戌亥")
        if not self.calendar_provenance.strip():
            raise ValueError("calendar_provenance is required")
        if not self.leap_month_identity.strip():
            raise ValueError("leap_month_identity is required")

def _year_pillar(year: int) -> tuple[str, str]:
    return STEMS[(year - 4) % 10], BRANCHES[(year - 4) % 12]

def _ming_shen(month: int, hour_branch: str) -> tuple[str, str]:
    month_index = BRANCHES.index("寅") + month - 1
    hour_index = BRANCHES.index(hour_branch)
    return BRANCHES[(month_index-hour_index)%12], BRANCHES[(month_index+hour_index)%12]

def _palace_stems(year_stem: str) -> tuple[str, ...]:
    group = {
        "甲":0,"己":0,"乙":1,"庚":1,"丙":2,"辛":2,"丁":3,"壬":3,"戊":4,"癸":4
    }[year_stem]
    starts = (2,4,6,8,0)
    start = starts[group]
    return tuple(STEMS[(start+i)%10] for i in range(12))

def _bureau(ming_branch: str, palace_stems: tuple[str, ...]) -> int:
    yin_index = (BRANCHES.index(ming_branch)-2)%12
    ming_stem = palace_stems[yin_index]
    stem_group = STEMS.index(ming_stem)//2
    branch_group = BRANCHES.index(ming_branch)//2
    return BUREAU_TABLE[stem_group][branch_group]

def _ziwei_branch(bureau: int, day: int) -> str:
    quotient = (day + bureau - 1)//bureau
    shortfall = quotient*bureau-day
    signed = shortfall if shortfall%2==0 else -shortfall
    return BRANCHES[(BRANCHES.index("寅")+quotient-1+signed)%12]

def _major_star_branches(ziwei: str) -> dict[str,str]:
    z=BRANCHES.index(ziwei)
    f=2*BRANCHES.index("寅")-z
    offsets=(z,z-1,z-3,z-4,z-5,z-8,f,f+1,f+2,f+3,f+4,f+5,f+6,f+10)
    return {star:BRANCHES[i%12] for star,i in zip(MAJOR_STARS,offsets)}

def _palace_layout(ming: str) -> dict[str,str]:
    m=(BRANCHES.index(ming)-2)%12
    yin_order=BRANCHES[2:]+BRANCHES[:2]
    by_branch={}
    for i,branch in enumerate(yin_order):
        by_branch[branch]=PALACES[(m-i)%12]
    return by_branch

def _topology(layout: dict[str,str]) -> dict[str,dict[str,Any]]:
    branch_by_palace={p:b for b,p in layout.items()}
    result={}
    for palace,branch in branch_by_palace.items():
        idx=BRANCHES.index(branch)
        opposite=BRANCHES[(idx+6)%12]
        trine=(BRANCHES[(idx+4)%12],BRANCHES[(idx+8)%12])
        result[palace]={
            "branch":branch,
            "opposite_palace":layout[opposite],
            "sanfang_palaces":[layout[x] for x in trine],
        }
    return result

def _palace_occupancy(layout: dict[str,str], stars: dict[str,str]) -> dict[str,dict[str,Any]]:
    branch_by_palace={palace:branch for branch,palace in layout.items()}
    result={}
    for palace in PALACES:
        branch=branch_by_palace[palace]
        major_stars=[star for star in MAJOR_STARS if stars[star]==branch]
        result[palace]={
            "branch":branch,
            "major_stars":major_stars,
            "major_star_count":len(major_stars),
            "empty_major_star_palace":not major_stars,
            "temporal_scope":"natal_baseline",
        }
    return result

def calculate_scope_a_natal(data: NormalizedNatalInput) -> dict[str,Any]:
    data.validate()
    year_stem,year_branch=_year_pillar(data.lunar_year)
    ming,shen=_ming_shen(data.lunar_month,data.hour_branch)
    stems=_palace_stems(year_stem)
    bureau=_bureau(ming,stems)
    ziwei=_ziwei_branch(bureau,data.lunar_day)
    stars=_major_star_branches(ziwei)
    layout=_palace_layout(ming)
    yin_order=BRANCHES[2:]+BRANCHES[:2]
    palace_records=[
        {"branch":b,"palace":layout[b],"stem":stems[i]}
        for i,b in enumerate(yin_order)
    ]
    occupancy=_palace_occupancy(layout,stars)
    facts=[f"palace_present:{p}" for p in PALACES]
    facts.extend(f"star_present:{s}" for s in MAJOR_STARS)
    facts.append("fact_available:star_locations")
    facts.extend(f"star_branch:{star}:{branch}" for star,branch in stars.items())
    facts.append("fact_available:palace_occupancy")
    for palace in PALACES:
        record=occupancy[palace]
        facts.append(f"major_star_count:{palace}:{record['major_star_count']}")
        facts.extend(f"star_in_palace:{star}:{palace}" for star in record["major_stars"])
        if record["empty_major_star_palace"]:
            facts.append(f"empty_palace:{palace}")
    return {
        "schema_version":"0.2.0",
        "provider":{"id":PROVIDER_ID,"version":PROVIDER_VERSION,"authority":"G1 ADMITTED — SCOPE-A NATAL / NOT G7 PRODUCTION ADMISSION"},
        "calculation_profile":{
            "profile_id":PROFILE_ID,
            "research_parent":RESEARCH_PROFILE,
            "chart_mode":"tian_pan",
            "calendar":"traditional_lunar_normalized_upstream",
            "clock":"civil",
            "true_solar":"disabled",
            "brightness":"not_computed",
            "auxiliary_stars":"not_computed",
            "dynamic_scopes":"not_computed",
        },
        "input_provenance":{
            "calendar_provenance":data.calendar_provenance,
            "leap_month_identity":data.leap_month_identity,
        },
        "normalized_input":{
            "lunar_year":data.lunar_year,"lunar_month":data.lunar_month,
            "lunar_day":data.lunar_day,"hour_branch":data.hour_branch,
        },
        "year_pillar":{"stem":year_stem,"branch":year_branch},
        "life_palace":{"branch":ming},
        "body_palace":{"branch":shen,"policy":"overlay_not_thirteenth_palace"},
        "five_element_bureau":{"number":bureau,"label":BUREAU_LABELS[bureau]},
        "ziwei_branch":ziwei,
        "major_star_placements":stars,
        "palaces":palace_records,
        "palace_occupancy":occupancy,
        "topology":_topology(layout),
        "retrieval_facts":facts,
        "unsupported":{
            "brightness":"not_computed","auxiliary_stars":"not_computed",
            "four_transformations":"not_computed","dynamic":"not_computed",
        },
        "production_authority_granted":False,
    }
