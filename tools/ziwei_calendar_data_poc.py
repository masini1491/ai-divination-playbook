#!/usr/bin/env python3
"""Research POC for repo-local Zi Wei Gregorian→lunar calendar data.

This module intentionally separates two roles:
- build-time generation may import pinned lunar_python;
- runtime resolution reads repo-local JSON shards only.

Nothing in this file is production-admitted. Production authority remains
ZIWEI_CALENDAR_ADMISSION_V1.json + tools/ziwei_calendar_provider.py until a
separate admission changes that contract.
"""
from __future__ import annotations

import calendar as _calendar
import hashlib
import json
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

SCHEMA_NAME="ziwei_calendar_day_shard"
SCHEMA_VERSION="0.1.0-poc"
STATUS="RESEARCH_POC_NOT_PRODUCTION"
TIMEZONE="Asia/Taipei"
HOUR_BRANCHES=("子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥")

class CalendarDataUnavailable(ValueError):
    pass

@dataclass(frozen=True)
class GregorianBirth:
    year:int
    month:int
    day:int
    hour:int
    minute:int=0
    second:int=0
    timezone:str=TIMEZONE

    def validate(self)->None:
        if self.timezone != TIMEZONE:
            raise ValueError(f"timezone must be {TIMEZONE}")
        if not all(isinstance(v,int) for v in (self.year,self.month,self.day,self.hour,self.minute,self.second)):
            raise ValueError("Gregorian birth date/time fields must be integers")
        if not 0 <= self.hour <= 23 or not 0 <= self.minute <= 59 or not 0 <= self.second <= 59:
            raise ValueError("invalid Gregorian clock time")
        datetime(self.year,self.month,self.day,self.hour,self.minute,self.second)

def hour_branch(hour:int)->str:
    if hour in (23,0):
        return "子"
    return HOUR_BRANCHES[(hour+1)//2]

def shard_relative_path(year:int,month:int)->Path:
    return Path("years")/f"{year:04d}"/f"{month:02d}.json"

def _canonical_bytes(payload:dict[str,Any])->bytes:
    return (json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)+"\n").encode("utf-8")

def load_day_record(root:Path, target:date)->dict[str,int]:
    path=root/shard_relative_path(target.year,target.month)
    if not path.is_file():
        raise CalendarDataUnavailable(f"calendar shard unavailable: {path}")
    payload=json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_name") != SCHEMA_NAME or payload.get("schema_version") != SCHEMA_VERSION:
        raise CalendarDataUnavailable(f"calendar shard contract mismatch: {path}")
    if payload.get("status") != STATUS:
        raise CalendarDataUnavailable(f"calendar shard status mismatch: {path}")
    if payload.get("gregorian_year") != target.year or payload.get("gregorian_month") != target.month:
        raise CalendarDataUnavailable(f"calendar shard key mismatch: {path}")
    matches=[r for r in payload.get("records",[]) if r.get("day")==target.day]
    if len(matches) != 1:
        raise CalendarDataUnavailable(f"calendar date unavailable or duplicated: {target.isoformat()}")
    record=matches[0]
    return {
        "lunar_year":int(record["lunar_year"]),
        "signed_lunar_month":int(record["signed_lunar_month"]),
        "lunar_day":int(record["lunar_day"]),
    }

def _normalize_record(record:dict[str,int])->tuple[int,str]:
    signed=int(record["signed_lunar_month"])
    month=abs(signed)
    day=int(record["lunar_day"])
    if signed >= 0:
        return month,"non_leap_month"
    if day <= 15:
        return month,f"leap_month_{month}:day_1_15_as_same_month"
    return (month%12)+1,f"leap_month_{month}:day_16_plus_as_next_month"

def normalize_from_data(data:GregorianBirth,root:Path)->dict[str,Any]:
    data.validate()
    raw_date=date(data.year,data.month,data.day)
    policy_date=raw_date+timedelta(days=1) if data.hour==23 else raw_date
    raw=load_day_record(root,raw_date)
    policy=load_day_record(root,policy_date)
    month,leap_identity=_normalize_record(policy)
    return {
        "raw_lunar_conversion":{
            "year":raw["lunar_year"],
            "month":abs(raw["signed_lunar_month"]),
            "signed_month":raw["signed_lunar_month"],
            "day":raw["lunar_day"],
            "is_leap_month":raw["signed_lunar_month"]<0,
            "time_branch":hour_branch(data.hour),
        },
        "policy_lunar_conversion":{
            "year":policy["lunar_year"],
            "month":abs(policy["signed_lunar_month"]),
            "signed_month":policy["signed_lunar_month"],
            "day":policy["lunar_day"],
            "is_leap_month":policy["signed_lunar_month"]<0,
            "time_branch":hour_branch(data.hour),
            "rat_hour_date_shift_applied":data.hour==23,
            "normalized_month":month,
            "leap_month_identity":leap_identity,
        },
        "normalized_natal_input":{
            "lunar_year":policy["lunar_year"],
            "lunar_month":month,
            "lunar_day":policy["lunar_day"],
            "hour_branch":hour_branch(data.hour),
            "leap_month_identity":leap_identity,
        },
    }

def generate_month_shard(year:int,month:int)->dict[str,Any]:
    """Build-time only: generate one complete Gregorian-month shard."""
    from lunar_python import Solar
    records=[]
    for day in range(1,_calendar.monthrange(year,month)[1]+1):
        lunar=Solar.fromYmdHms(year,month,day,12,0,0).getLunar()
        records.append({
            "day":day,
            "lunar_year":int(lunar.getYear()),
            "signed_lunar_month":int(lunar.getMonth()),
            "lunar_day":int(lunar.getDay()),
        })
    return {
        "coverage":"complete_month",
        "gregorian_month":month,
        "gregorian_year":year,
        "records":records,
        "schema_name":SCHEMA_NAME,
        "schema_version":SCHEMA_VERSION,
        "status":STATUS,
    }

def write_month_shard(root:Path,year:int,month:int)->Path:
    payload=generate_month_shard(year,month)
    path=root/shard_relative_path(year,month)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(_canonical_bytes(payload))
    return path

def aggregate_hash(root:Path,paths:list[Path])->str:
    digest=hashlib.sha256()
    for rel in sorted(paths,key=lambda p:p.as_posix()):
        digest.update(rel.as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update((root/rel).read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()
