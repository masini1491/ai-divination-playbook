#!/usr/bin/env python3
"""Dependency-free resolver for the Zi Wei repo-local interval calendar data.

The dataset MANIFEST is an integrity/provenance artifact, not admission
authority. Production permission is owned separately by
ZIWEI_CALENDAR_ADMISSION_V1.json, which allowlists the exact dataset identity,
aggregate hash and supported input range.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
DATASET_ROOT=ROOT/"data"/"calendar"/"ziwei_tw_interval"/"v1"
MANIFEST_NAME="MANIFEST.json"
DATASET_ID="ziwei_tw_interval_1900_2100_candidate_v1"
MANIFEST_SCHEMA_NAME="ziwei_calendar_interval_dataset_manifest"
MANIFEST_SCHEMA_VERSION="0.2.0-candidate"
MANIFEST_STATUS="RESEARCH_CANDIDATE_NOT_PRODUCTION"
SELECTED_RANGE_STATUS="SELECTED_CANDIDATE_NOT_PRODUCTION_ADMITTED"
START_DATE=date(1900,1,1)
END_DATE=date(2100,12,31)
TIMEZONE="Asia/Taipei"
HOUR_BRANCHES=("子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥")

class CalendarDataUnavailable(ValueError):
    pass

@dataclass(frozen=True)
class CandidateGregorianBirth:
    year:int
    month:int
    day:int
    hour:int
    minute:int=0
    second:int=0
    timezone:str=TIMEZONE

    def validate(self)->None:
        if self.timezone!=TIMEZONE:
            raise ValueError(f"timezone must be {TIMEZONE}")
        if not all(isinstance(v,int) for v in (self.year,self.month,self.day,self.hour,self.minute,self.second)):
            raise ValueError("Gregorian birth date/time fields must be integers")
        if not 0<=self.hour<=23 or not 0<=self.minute<=59 or not 0<=self.second<=59:
            raise ValueError("invalid Gregorian clock time")
        try:
            datetime(self.year,self.month,self.day,self.hour,self.minute,self.second)
        except ValueError as exc:
            raise ValueError(f"invalid Gregorian birth date/time: {exc}") from exc

def hour_branch(hour:int)->str:
    if hour in (23,0):
        return "子"
    return HOUR_BRANCHES[(hour+1)//2]

def _sha256(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load_manifest(root:Path=DATASET_ROOT)->dict[str,Any]:
    path=root/MANIFEST_NAME
    if not path.is_file():
        raise CalendarDataUnavailable(f"calendar dataset manifest unavailable: {path}")
    try:
        m=json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise CalendarDataUnavailable(f"calendar dataset manifest unreadable: {path}") from exc
    if m.get("schema_name")!=MANIFEST_SCHEMA_NAME or m.get("schema_version")!=MANIFEST_SCHEMA_VERSION:
        raise CalendarDataUnavailable("calendar dataset manifest schema mismatch")
    if m.get("dataset_id")!=DATASET_ID or m.get("status")!=MANIFEST_STATUS:
        raise CalendarDataUnavailable("calendar dataset manifest identity/status mismatch")
    selected=m.get("selected_product_range",{})
    if selected!={
        "start_date":"1900-01-01",
        "end_date":"2100-12-31",
        "selected":True,
        "production_admitted":False,
        "status":SELECTED_RANGE_STATUS,
    }:
        raise CalendarDataUnavailable("calendar dataset selected-range contract mismatch")
    if m.get("production_admitted") is not False:
        raise CalendarDataUnavailable("candidate dataset must remain non-production")
    return m

def required_shard_years(data:CandidateGregorianBirth)->tuple[int,...]:
    data.validate()
    raw=date(data.year,data.month,data.day)
    if not START_DATE<=raw<=END_DATE:
        raise CalendarDataUnavailable(
            f"Gregorian date outside selected candidate range: {raw.isoformat()}"
        )
    policy=raw+timedelta(days=1) if data.hour==23 else raw
    years=[raw.year]
    if policy.year!=raw.year:
        years.append(policy.year)
    return tuple(years)

def required_shard_paths(data:CandidateGregorianBirth)->tuple[str,...]:
    return tuple(f"years/{year:04d}.json" for year in required_shard_years(data))

def _manifest_shard(manifest:dict[str,Any],year:int)->dict[str,Any]:
    matches=[item for item in manifest.get("shards",[]) if int(item.get("year",-1))==year]
    if len(matches)!=1:
        raise CalendarDataUnavailable(f"calendar shard manifest entry unavailable/ambiguous: {year}")
    return matches[0]

def _load_verified_shard(root:Path,manifest:dict[str,Any],year:int)->dict[str,Any]:
    item=_manifest_shard(manifest,year)
    rel=Path(str(item["path"]))
    expected=Path("years")/f"{year:04d}.json"
    if rel!=expected:
        raise CalendarDataUnavailable(f"calendar shard path mismatch for {year}: {rel}")
    path=root/rel
    if not path.is_file():
        raise CalendarDataUnavailable(f"calendar shard unavailable: {rel.as_posix()}")
    if path.stat().st_size!=int(item["bytes"]):
        raise CalendarDataUnavailable(f"calendar shard byte-size mismatch: {rel.as_posix()}")
    if _sha256(path)!=item["sha256"]:
        raise CalendarDataUnavailable(f"calendar shard sha256 mismatch: {rel.as_posix()}")
    try:
        payload=json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise CalendarDataUnavailable(f"calendar shard unreadable: {rel.as_posix()}") from exc
    if payload.get("schema_name")!="ziwei_calendar_interval_year_shard":
        raise CalendarDataUnavailable(f"calendar shard schema mismatch: {rel.as_posix()}")
    if payload.get("schema_version")!="0.1.0-poc" or payload.get("status")!="RESEARCH_POC_NOT_PRODUCTION":
        raise CalendarDataUnavailable(f"calendar shard version/status mismatch: {rel.as_posix()}")
    if int(payload.get("gregorian_year",-1))!=year:
        raise CalendarDataUnavailable(f"calendar shard year mismatch: {rel.as_posix()}")
    if len(payload.get("intervals",[]))!=int(item["interval_count"]):
        raise CalendarDataUnavailable(f"calendar shard interval-count mismatch: {rel.as_posix()}")
    return payload

def _day_record(payload:dict[str,Any],target:date)->dict[str,int]:
    matches=[]
    for item in payload.get("intervals",[]):
        first=date.fromisoformat(item["start_date"])
        last=date.fromisoformat(item["end_date"])
        if first<=target<=last:
            matches.append((item,first))
    if len(matches)!=1:
        raise CalendarDataUnavailable(f"calendar interval unavailable/ambiguous: {target.isoformat()}")
    item,first=matches[0]
    lunar_day=(target-first).days+1
    if not 1<=lunar_day<=int(item["day_count"]):
        raise CalendarDataUnavailable(f"calendar interval offset invalid: {target.isoformat()}")
    return {
        "lunar_year":int(item["lunar_year"]),
        "signed_lunar_month":int(item["signed_lunar_month"]),
        "lunar_day":lunar_day,
    }

def _normalize_month(record:dict[str,int])->tuple[int,str]:
    signed=int(record["signed_lunar_month"])
    month=abs(signed)
    day=int(record["lunar_day"])
    if signed>=0:
        return month,"non_leap_month"
    if day<=15:
        return month,f"leap_month_{month}:day_1_15_as_same_month"
    return (month%12)+1,f"leap_month_{month}:day_16_plus_as_next_month"

def normalize_candidate_birth(
    data:CandidateGregorianBirth,
    root:Path=DATASET_ROOT,
)->dict[str,Any]:
    years=required_shard_years(data)
    manifest=load_manifest(root)
    shards={year:_load_verified_shard(root,manifest,year) for year in years}

    raw_date=date(data.year,data.month,data.day)
    policy_date=raw_date+timedelta(days=1) if data.hour==23 else raw_date
    raw=_day_record(shards[raw_date.year],raw_date)
    policy=_day_record(shards[policy_date.year],policy_date)
    month,leap_identity=_normalize_month(policy)
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
        "data_contract":{
            "dataset_id":manifest["dataset_id"],
            "dataset_root":"data/calendar/ziwei_tw_interval/v1",
            "selected_range":manifest["selected_product_range"],
            "required_shards":list(required_shard_paths(data)),
            "aggregate_hash":manifest["aggregate_hash"],
            "production_admitted":False,
        },
    }
