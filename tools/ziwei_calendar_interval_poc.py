#!/usr/bin/env python3
"""Research POC for compact Zi Wei Gregorian->lunar interval data.

Build-time generation may import pinned lunar_python. Runtime resolution reads
repo-local JSON year shards only. Nothing here is production-admitted.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

SCHEMA_NAME="ziwei_calendar_interval_year_shard"
SCHEMA_VERSION="0.1.0-poc"
STATUS="RESEARCH_POC_NOT_PRODUCTION"
TIMEZONE="Asia/Taipei"
HOUR_BRANCHES=("子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥")

class CalendarIntervalUnavailable(ValueError):
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

def shard_relative_path(year:int)->Path:
    return Path("years")/f"{year:04d}.json"

def _canonical_bytes(payload:dict[str,Any])->bytes:
    return (json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)+"\n").encode("utf-8")

def _ymd(solar:Any)->date:
    return date(int(solar.getYear()),int(solar.getMonth()),int(solar.getDay()))

def generate_year_shard(year:int)->dict[str,Any]:
    """Build-time only: emit lunar-month intervals intersecting Gregorian year."""
    from lunar_python import LunarYear, Solar

    start=date(year,1,1)
    end=date(year,12,31)
    intervals=[]
    seen=set()
    for lunar_year in range(year-1,year+2):
        for month in LunarYear.fromYear(lunar_year).getMonthsInYear():
            first=_ymd(Solar.fromJulianDay(month.getFirstJulianDay()))
            last=first+timedelta(days=int(month.getDayCount())-1)
            if last < start or first > end:
                continue
            key=(int(month.getYear()),int(month.getMonth()),first.isoformat())
            if key in seen:
                continue
            seen.add(key)
            intervals.append({
                "lunar_year":int(month.getYear()),
                "signed_lunar_month":int(month.getMonth()),
                "start_date":first.isoformat(),
                "day_count":int(month.getDayCount()),
                "end_date":last.isoformat(),
            })
    intervals.sort(key=lambda x:x["start_date"])
    return {
        "schema_name":SCHEMA_NAME,
        "schema_version":SCHEMA_VERSION,
        "status":STATUS,
        "coverage":"gregorian_year_intersection",
        "gregorian_year":year,
        "intervals":intervals,
    }

def write_year_shard(root:Path,year:int)->Path:
    payload=generate_year_shard(year)
    path=root/shard_relative_path(year)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(_canonical_bytes(payload))
    return path

def load_day_record(root:Path,target:date)->dict[str,int]:
    path=root/shard_relative_path(target.year)
    if not path.is_file():
        raise CalendarIntervalUnavailable(f"calendar interval shard unavailable: {path}")
    payload=json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_name") != SCHEMA_NAME or payload.get("schema_version") != SCHEMA_VERSION:
        raise CalendarIntervalUnavailable(f"calendar interval shard contract mismatch: {path}")
    if payload.get("status") != STATUS or payload.get("gregorian_year") != target.year:
        raise CalendarIntervalUnavailable(f"calendar interval shard key/status mismatch: {path}")
    matches=[]
    for item in payload.get("intervals",[]):
        first=date.fromisoformat(item["start_date"])
        last=date.fromisoformat(item["end_date"])
        if first <= target <= last:
            matches.append((item,first))
    if len(matches) != 1:
        raise CalendarIntervalUnavailable(f"calendar interval unavailable or ambiguous: {target.isoformat()}")
    item,first=matches[0]
    lunar_day=(target-first).days+1
    if not 1 <= lunar_day <= int(item["day_count"]):
        raise CalendarIntervalUnavailable(f"calendar interval offset invalid: {target.isoformat()}")
    return {
        "lunar_year":int(item["lunar_year"]),
        "signed_lunar_month":int(item["signed_lunar_month"]),
        "lunar_day":lunar_day,
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

def normalize_from_interval_data(data:GregorianBirth,root:Path)->dict[str,Any]:
    data.validate()
    raw_date=date(data.year,data.month,data.day)
    policy_date=raw_date+timedelta(days=1) if data.hour==23 else raw_date
    raw=load_day_record(root,raw_date)
    policy=load_day_record(root,policy_date)
    month,leap_identity=_normalize_record(policy)
    branch=hour_branch(data.hour)
    return {
        "raw_lunar_conversion":{
            "year":raw["lunar_year"],
            "month":abs(raw["signed_lunar_month"]),
            "signed_month":raw["signed_lunar_month"],
            "day":raw["lunar_day"],
            "is_leap_month":raw["signed_lunar_month"]<0,
            "time_branch":branch,
        },
        "policy_lunar_conversion":{
            "year":policy["lunar_year"],
            "month":abs(policy["signed_lunar_month"]),
            "signed_month":policy["signed_lunar_month"],
            "day":policy["lunar_day"],
            "is_leap_month":policy["signed_lunar_month"]<0,
            "time_branch":branch,
            "rat_hour_date_shift_applied":data.hour==23,
            "normalized_month":month,
            "leap_month_identity":leap_identity,
        },
        "normalized_natal_input":{
            "lunar_year":policy["lunar_year"],
            "lunar_month":month,
            "lunar_day":policy["lunar_day"],
            "hour_branch":branch,
            "leap_month_identity":leap_identity,
        },
    }

def aggregate_hash(root:Path,paths:list[Path])->str:
    digest=hashlib.sha256()
    for rel in sorted(paths,key=lambda p:p.as_posix()):
        digest.update(rel.as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update((root/rel).read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()
