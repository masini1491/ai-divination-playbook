#!/usr/bin/env python3
"""Deterministic M0 auxiliary-star provider for Zi Wei natal baseline."""
from __future__ import annotations
from typing import Any
from tools.ziwei_natal_provider import BRANCHES, MAJOR_STARS, NormalizedNatalInput
PROFILE_ID="ziwei.auxiliary.m0.iztro_v1"; PROVIDER_ID="ziwei-m0-auxiliary-python"; PROVIDER_VERSION="1.0.0"
STARS=("左輔","右弼","文昌","文曲")
def _idx(branch:str)->int: return BRANCHES.index(branch)
def calculate_m0_auxiliary(data:NormalizedNatalInput, major_star_placements:dict[str,str])->dict[str,Any]:
    data.validate()
    if set(major_star_placements)!=set(MAJOR_STARS): raise ValueError("M0 auxiliary provider requires the admitted 14-major-star placement set")
    month=data.lunar_month; hour=_idx(data.hour_branch)
    placements={"左輔":BRANCHES[(_idx("辰")+month-1)%12],"右弼":BRANCHES[(_idx("戌")-(month-1))%12],"文昌":BRANCHES[(_idx("戌")-hour)%12],"文曲":BRANCHES[(_idx("辰")+hour)%12]}
    facts=["fact_available:m0_auxiliary_stars",*(f"star_present:{s}" for s in STARS)]; relations=[]
    for subject,branch in major_star_placements.items():
        i=_idx(branch); sanfang={BRANCHES[i],BRANCHES[(i+4)%12],BRANCHES[(i+8)%12]}
        for auxiliary,aux_branch in placements.items():
            if aux_branch in sanfang:
                facts.append(f"modifier_present:{subject}:{auxiliary}"); relations.append({"subject":subject,"auxiliary":auxiliary,"relation":"self_or_sanfang"})
    return {"schema_version":"1.0.0","provider":{"id":PROVIDER_ID,"version":PROVIDER_VERSION,"authority":"OPTIONAL M0 PRODUCTION ADMISSION"},"profile":{"profile_id":PROFILE_ID,"implementation_reference":{"repository":"SylarLong/iztro","revision":"2c7ef9be669df7b19d1799f4dce335fed3794f78","path":"src/star/location.ts"},"placement_rules":{"左輔":"normalized lunar month: 辰起正月順行","右弼":"normalized lunar month: 戌起正月逆行","文昌":"hour branch: 戌起子時逆行","文曲":"hour branch: 辰起子時順行"},"relation_scope":"self_or_sanfang_only"},"placements":placements,"relations":relations,"retrieval_facts":facts,"production_authority_granted":True}
