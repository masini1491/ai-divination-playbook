#!/usr/bin/env python3
"""Production Gregorian → normalized lunar input provider for Zi Wei Scope-A.

Runtime conversion reads the admitted repo-local interval dataset. The pinned
lunar-python implementation remains build/parity evidence only and is not an
ordinary production runtime dependency.
"""
from __future__ import annotations
import json
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

PROVIDER_ID="ziwei-calendar-interval-data"
PROVIDER_VERSION="2.0.0"
PROFILE_ID="ziwei.calendar.tw_v1"
TIMEZONE="Asia/Taipei"; CLOCK_MODE="civil_time"; TRUE_SOLAR_TIME="disabled"
LEAP_MONTH_POLICY="split_after_day_15"; RAT_HOUR_POLICY="next_day_at_23"
HOUR_BRANCHES=("子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥")
ROOT=Path(__file__).resolve().parents[1]
DATASET_ROOT=ROOT/"data"/"calendar"/"ziwei_tw_interval"/"v1"
DATASET_ID="ziwei_tw_interval_1900_2100_candidate_v1"
DATASET_AGGREGATE_SHA256="4913a39e770afcd21eedc387523c572b8c4fc6469889c28f6ea75613f8984d79"
DATASET_SCHEMA_NAME="ziwei_calendar_interval_year_shard"
DATASET_SCHEMA_VERSION="0.1.0-poc"
DATASET_ARTIFACT_STATUS="RESEARCH_POC_NOT_PRODUCTION"
SUPPORTED_START=date(1900,1,1); SUPPORTED_END=date(2100,12,31); POLICY_TAIL_END=date(2101,12,31)
BUILD_DEPENDENCY_PACKAGE="lunar_python"; BUILD_DEPENDENCY_VERSION="1.4.8"
BUILD_DEPENDENCY_REPOSITORY="6tail/lunar-python"
BUILD_DEPENDENCY_REVISION="000c8a3d74eed098d6256a28fdd51b869324c559"
BUILD_DEPENDENCY_LICENSE="MIT"

class CalendarDataUnavailable(ValueError): pass

@dataclass(frozen=True)
class GregorianBirthInput:
    year:int; month:int; day:int; hour:int; minute:int=0; second:int=0; timezone:str=TIMEZONE
    def validate(self)->None:
        if self.timezone!=TIMEZONE: raise ValueError(f"timezone must be {TIMEZONE} for {PROFILE_ID}")
        if not all(isinstance(v,int) and not isinstance(v,bool) for v in (self.year,self.month,self.day,self.hour,self.minute,self.second)):
            raise ValueError("Gregorian birth date/time fields must be integers")
        if not 0<=self.hour<=23: raise ValueError("hour must be in 0..23")
        if not 0<=self.minute<=59: raise ValueError("minute must be in 0..59")
        if not 0<=self.second<=59: raise ValueError("second must be in 0..59")
        try: instant=datetime(self.year,self.month,self.day,self.hour,self.minute,self.second)
        except ValueError as exc: raise ValueError(f"invalid Gregorian birth date/time: {exc}") from exc
        civil=instant.date()
        if not SUPPORTED_START<=civil<=SUPPORTED_END:
            raise ValueError(f"Gregorian birth date outside admitted range: {civil.isoformat()} not in {SUPPORTED_START.isoformat()}..{SUPPORTED_END.isoformat()}")

def hour_branch(hour:int)->str:
    if hour in (23,0): return "子"
    return HOUR_BRANCHES[(hour+1)//2]

def shard_relative_path(year:int)->Path: return Path("years")/f"{year:04d}.json"

def required_calendar_shards(data:GregorianBirthInput)->tuple[str,...]:
    data.validate(); raw=date(data.year,data.month,data.day); years=[raw.year]
    if data.hour==23:
        policy=raw+timedelta(days=1)
        if policy.year!=raw.year: years.append(policy.year)
    base=Path("data/calendar/ziwei_tw_interval/v1")
    return tuple((base/shard_relative_path(y)).as_posix() for y in years)

def _load_day_record(target:date)->dict[str,int]:
    if target>POLICY_TAIL_END: raise CalendarDataUnavailable(f"calendar policy date outside materialized tail: {target.isoformat()}")
    path=DATASET_ROOT/shard_relative_path(target.year)
    if not path.is_file(): raise CalendarDataUnavailable(f"calendar interval shard unavailable: {path}")
    try: payload=json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc: raise CalendarDataUnavailable(f"calendar interval shard unreadable: {path}: {exc}") from exc
    if payload.get("schema_name")!=DATASET_SCHEMA_NAME or payload.get("schema_version")!=DATASET_SCHEMA_VERSION:
        raise CalendarDataUnavailable(f"calendar interval shard contract mismatch: {path}")
    if payload.get("status")!=DATASET_ARTIFACT_STATUS or payload.get("gregorian_year")!=target.year:
        raise CalendarDataUnavailable(f"calendar interval shard key/status mismatch: {path}")
    matches=[]
    for item in payload.get("intervals",[]):
        first=date.fromisoformat(item["start_date"]); last=date.fromisoformat(item["end_date"])
        if first<=target<=last: matches.append((item,first))
    if len(matches)!=1: raise CalendarDataUnavailable(f"calendar interval unavailable or ambiguous: {target.isoformat()}")
    item,first=matches[0]; lunar_day=(target-first).days+1
    if not 1<=lunar_day<=int(item["day_count"]): raise CalendarDataUnavailable(f"calendar interval offset invalid: {target.isoformat()}")
    return {"lunar_year":int(item["lunar_year"]),"signed_lunar_month":int(item["signed_lunar_month"]),"lunar_day":lunar_day}

def _lunar_record(record:dict[str,int],branch:str)->dict[str,Any]:
    signed=int(record["signed_lunar_month"])
    return {"year":int(record["lunar_year"]),"month":abs(signed),"signed_month":signed,"day":int(record["lunar_day"]),"is_leap_month":signed<0,"time_branch":branch}

def _apply_leap_month_policy(r:dict[str,Any])->tuple[int,str]:
    month=int(r["month"]); day=int(r["day"])
    if not r["is_leap_month"]: return month,"non_leap_month"
    if day<=15: return month,f"leap_month_{month}:day_1_15_as_same_month"
    return (month%12)+1,f"leap_month_{month}:day_16_plus_as_next_month"

def normalize_gregorian_birth(data:GregorianBirthInput)->dict[str,Any]:
    data.validate(); raw_date=date(data.year,data.month,data.day)
    policy_date=raw_date+timedelta(days=1) if data.hour==23 else raw_date
    branch=hour_branch(data.hour)
    raw=_lunar_record(_load_day_record(raw_date),branch); policy=_lunar_record(_load_day_record(policy_date),branch)
    normalized_month,leap_identity=_apply_leap_month_policy(policy)
    provenance=(f"{PROVIDER_ID}@{PROVIDER_VERSION};dataset={DATASET_ID};aggregate_sha256={DATASET_AGGREGATE_SHA256};"
                f"build_source={BUILD_DEPENDENCY_REPOSITORY}@{BUILD_DEPENDENCY_REVISION};profile={PROFILE_ID};timezone={TIMEZONE};"
                f"clock={CLOCK_MODE};rat_hour_policy={RAT_HOUR_POLICY};leap_month_policy={LEAP_MONTH_POLICY}")
    normalized={"lunar_year":policy["year"],"lunar_month":normalized_month,"lunar_day":policy["day"],"hour_branch":branch,
                "calendar_provenance":provenance,"leap_month_identity":leap_identity}
    return {
      "schema_version":"1.0.0",
      "provider":{"id":PROVIDER_ID,"version":PROVIDER_VERSION,"authority":"PRODUCTION-ADMITTED GREGORIAN INPUT NORMALIZER"},
      "calendar_profile":{"profile_id":PROFILE_ID,"timezone":TIMEZONE,"clock_mode":CLOCK_MODE,"true_solar_time":TRUE_SOLAR_TIME,
        "rat_hour_policy":RAT_HOUR_POLICY,"leap_month_policy":LEAP_MONTH_POLICY,
        "supported_gregorian_range":{"start":SUPPORTED_START.isoformat(),"end":SUPPORTED_END.isoformat()}},
      "dataset":{"dataset_id":DATASET_ID,"root":"data/calendar/ziwei_tw_interval/v1","aggregate_sha256":DATASET_AGGREGATE_SHA256,
        "artifact_status":DATASET_ARTIFACT_STATUS,"production_use":"admitted_by_ZIWEI_CALENDAR_ADMISSION_V1",
        "required_shards":list(required_calendar_shards(data))},
      "dependency":{"package":BUILD_DEPENDENCY_PACKAGE,"version":BUILD_DEPENDENCY_VERSION,"repository":BUILD_DEPENDENCY_REPOSITORY,
        "revision":BUILD_DEPENDENCY_REVISION,"license":BUILD_DEPENDENCY_LICENSE,"role":"build_parity_only","runtime_required":False},
      "input":{"calendar":"gregorian","year":data.year,"month":data.month,"day":data.day,"hour":data.hour,"minute":data.minute,"second":data.second,"timezone":data.timezone},
      "raw_lunar_conversion":raw,
      "policy_lunar_conversion":{**policy,"rat_hour_date_shift_applied":data.hour==23,"normalized_month":normalized_month,"leap_month_identity":leap_identity},
      "normalized_natal_input":normalized,"provenance":provenance,
      "boundaries":{"timezone_conversion_performed":False,"true_solar_time_applied":False,"raw_lunar_preserved":True,
        "ziwei_policy_separated_from_calendar_conversion":True,"runtime_upstream_package_required":False},
    }
