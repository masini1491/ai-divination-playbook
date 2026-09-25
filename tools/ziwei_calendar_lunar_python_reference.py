#!/usr/bin/env python3
"""Build/parity-only lunar-python reference for Zi Wei Gregorian conversion.

This preserves the pre-migration option-A calculation as an independent parity
oracle. It is not production-admitted and must not be used as runtime fallback.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from lunar_python import Solar
TIMEZONE="Asia/Taipei"; HOUR_BRANCHES=("子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥")
@dataclass(frozen=True)
class GregorianBirthInput:
    year:int; month:int; day:int; hour:int; minute:int=0; second:int=0; timezone:str=TIMEZONE
    def validate(self)->None:
        if self.timezone!=TIMEZONE: raise ValueError(f"timezone must be {TIMEZONE}")
        if not all(isinstance(v,int) and not isinstance(v,bool) for v in (self.year,self.month,self.day,self.hour,self.minute,self.second)): raise ValueError("fields must be integers")
        datetime(self.year,self.month,self.day,self.hour,self.minute,self.second)
def hour_branch(hour:int)->str:
    if hour in (23,0): return "子"
    return HOUR_BRANCHES[(hour+1)//2]
def _record(lunar:Any)->dict[str,Any]:
    signed=int(lunar.getMonth())
    return {"year":int(lunar.getYear()),"month":abs(signed),"signed_month":signed,"day":int(lunar.getDay()),"is_leap_month":signed<0,"time_branch":lunar.getTimeZhi()}
def _policy(r):
    m=int(r["month"]); d=int(r["day"])
    if not r["is_leap_month"]: return m,"non_leap_month"
    if d<=15: return m,f"leap_month_{m}:day_1_15_as_same_month"
    return (m%12)+1,f"leap_month_{m}:day_16_plus_as_next_month"
def normalize_gregorian_birth(data:GregorianBirthInput)->dict[str,Any]:
    data.validate(); solar=Solar.fromYmdHms(data.year,data.month,data.day,data.hour,data.minute,data.second)
    raw=_record(solar.getLunar()); policy=_record((solar.nextDay(1) if data.hour==23 else solar).getLunar())
    month,identity=_policy(policy); branch=hour_branch(data.hour)
    return {"raw_lunar_conversion":raw,"policy_lunar_conversion":{**policy,"rat_hour_date_shift_applied":data.hour==23,"normalized_month":month,"leap_month_identity":identity},
      "normalized_natal_input":{"lunar_year":policy["year"],"lunar_month":month,"lunar_day":policy["day"],"hour_branch":branch,"leap_month_identity":identity}}
