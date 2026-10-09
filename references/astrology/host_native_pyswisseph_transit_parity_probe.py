#!/usr/bin/env python3
"""REFERENCE-ONLY PySwissEph vs admitted Astronomy Engine transit parity probe."""
from __future__ import annotations
import datetime as dt
import json
import math
import sys
from typing import Callable
import swisseph as swe
from tools import astrology_provider as ap
from tools import astrology_transit_provider as tp

UTC = dt.timezone.utc
SWE_IDS = {"Sun":swe.SUN,"Moon":swe.MOON,"Mercury":swe.MERCURY,"Venus":swe.VENUS,"Mars":swe.MARS,"Jupiter":swe.JUPITER,"Saturn":swe.SATURN,"Uranus":swe.URANUS,"Neptune":swe.NEPTUNE,"Pluto":swe.PLUTO}
REQUESTED_FLAGS = swe.FLG_SWIEPH | swe.FLG_SPEED

def backend_name(retflag:int)->str:
    if retflag & swe.FLG_JPLEPH: return "JPLEPH"
    if retflag & swe.FLG_SWIEPH: return "SWIEPH"
    if retflag & swe.FLG_MOSEPH: return "MOSEPH"
    return f"UNKNOWN({retflag})"

def julian_day(when:dt.datetime)->float:
    when=when.astimezone(UTC)
    hour=when.hour+when.minute/60+when.second/3600+when.microsecond/3_600_000_000
    return swe.julday(when.year,when.month,when.day,hour,swe.GREG_CAL)

def swiss_state(body:str,when:dt.datetime)->tuple[float,float,int]:
    values,retflag=swe.calc_ut(julian_day(when),SWE_IDS[body],REQUESTED_FLAGS)
    return float(values[0])%360.0,float(values[3]),int(retflag)

def swiss_backend(body:str,when:dt.datetime)->tuple[float,float]:
    lon,speed,_=swiss_state(body,when); return lon,speed

def circular_diff(a:float,b:float)->float: return abs((a-b+180.0)%360.0-180.0)
def parse_utc(v:str)->dt.datetime: return dt.datetime.fromisoformat(v.replace("Z","+00:00")).astimezone(UTC)
def percentile(values:list[float],fraction:float)->float:
    o=sorted(values); i=max(0,min(len(o)-1,math.ceil(fraction*len(o))-1)); return o[i]

def with_backend(fn:Callable,backend:Callable,*args,**kwargs):
    original=tp._longitude_and_speed; tp._longitude_and_speed=backend
    try: return fn(*args,**kwargs)
    finally: tp._longitude_and_speed=original

def minimal_natal(longitude_deg:float=110.0)->dict:
    return {"schema_name":"astrology_fact_bundle","schema_version":"1.0.0","method":"Astrology","reading_mode":"natal","fact_source":"user_supplied_structured_export","calculation_verification":"user_asserted","subject_ref":"subject:synthetic-transit-target","birth_time_certainty":"exact","configuration":{"zodiac_system":"tropical","center":"geocentric","house_system":None},"facts":{"objects":[{"fact_id":"fact:object:mercury","object_type":"planet","object_id":"Mercury","longitude_deg":longitude_deg}],"houses":[],"aspects":[],"events":[]}}

def whole_sign_natal()->dict:
    signs=("Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces")
    houses=[{"fact_id":f"fact:house:{h}","house_number":h,"cusp_longitude_deg":float((h-1)*30),"sign_index":h-1,"sign":signs[h-1],"sign_degree":0.0} for h in range(1,13)]
    return {"schema_name":"astrology_fact_bundle","schema_version":"1.0.0","method":"Astrology","reading_mode":"natal","fact_source":"user_supplied_structured_export","calculation_verification":"user_asserted","subject_ref":"subject:house-search-fixture","birth_time_certainty":"exact","configuration":{"zodiac_system":"tropical","center":"geocentric","house_system":"Whole Sign"},"facts":{"objects":[],"houses":houses,"aspects":[],"events":[]}}

def paired_times(a:list[dict],b:list[dict])->list[float]:
    if len(a)!=len(b): return []
    return [abs((parse_utc(x["exact_time_utc"])-parse_utc(y["exact_time_utc"])).total_seconds()) for x,y in zip(a,b)]

def main()->int:
    dates=[dt.datetime(2026,m,d,12,0,tzinfo=UTC) for m in range(1,13) for d in (1,15)]
    dates += [parse_utc(v) for v in ("2026-02-26T06:48:00Z","2026-03-20T19:33:00Z","2026-06-16T15:44:00Z","2026-06-29T17:36:00Z","2026-07-14T03:53:00Z","2026-07-23T22:58:00Z","2026-08-01T13:52:00Z","2026-09-10T08:07:00Z","2026-10-24T07:13:00Z","2026-10-25T09:10:00Z","2026-11-13T15:54:00Z","2026-12-04T08:13:00Z","2026-12-10T23:31:00Z")]
    rows=[]
    for when in sorted(set(dates)):
        for body in SWE_IDS:
            ae_lon,ae_speed=ap._longitude_and_speed(body,when); sw_lon,sw_speed,retflag=swiss_state(body,when)
            rows.append({"time_utc":when.isoformat().replace("+00:00","Z"),"body":body,"longitude_difference_deg":circular_diff(ae_lon,sw_lon),"speed_difference_deg_per_day":abs(ae_speed-sw_speed),"retflag":retflag,"effective_backend":backend_name(retflag)})
    natal=minimal_natal()
    ae_three=with_backend(tp.search_transit_to_natal,ap._longitude_and_speed,natal,start_utc="2026-06-01T00:00:00Z",end_utc="2026-08-10T00:00:00Z",moving_bodies=["Mercury"],natal_targets=["Mercury"],aspects=["conjunction"])
    sw_three=with_backend(tp.search_transit_to_natal,swiss_backend,natal,start_utc="2026-06-01T00:00:00Z",end_utc="2026-08-10T00:00:00Z",moving_bodies=["Mercury"],natal_targets=["Mercury"],aspects=["conjunction"])
    ae_station=with_backend(tp.search_stations,ap._longitude_and_speed,start_utc="2026-06-20T00:00:00Z",end_utc="2026-07-05T00:00:00Z",moving_bodies=["Mercury"])[0]
    sw_station=with_backend(tp.search_stations,swiss_backend,start_utc="2026-06-20T00:00:00Z",end_utc="2026-07-05T00:00:00Z",moving_bodies=["Mercury"])[0]
    target=float(ae_station["longitude_deg"]); tn=minimal_natal(target)
    ae_tan=with_backend(tp.search_transit_to_natal,ap._longitude_and_speed,tn,start_utc="2026-06-20T00:00:00Z",end_utc="2026-07-05T00:00:00Z",moving_bodies=["Mercury"],natal_targets=["Mercury"],aspects=["conjunction"])
    sw_tan=with_backend(tp.search_transit_to_natal,swiss_backend,tn,start_utc="2026-06-20T00:00:00Z",end_utc="2026-07-05T00:00:00Z",moving_bodies=["Mercury"],natal_targets=["Mercury"],aspects=["conjunction"])
    lon=[x["longitude_difference_deg"] for x in rows]; speed=[x["speed_difference_deg_per_day"] for x in rows]
    out={"status":"REFERENCE-ONLY","production_authority":False,"runtime":{"python":sys.version.split()[0],"pyswisseph":swe.version,"requested_flags":REQUESTED_FLAGS,"effective_backends":sorted({x["effective_backend"] for x in rows})},"pointwise":{"sample_count":len(rows),"longitude_max_deg":max(lon),"longitude_p95_deg":percentile(lon,.95),"speed_max_deg_per_day":max(speed)},"mercury_three_pass":{"ae_count":len(ae_three),"sw_count":len(sw_three),"time_deltas_seconds":paired_times(ae_three,sw_three)},"tangential_station":{"station_longitude_difference_arcsec":circular_diff(float(ae_station["longitude_deg"]),float(sw_station["longitude_deg"]))*3600.0,"tolerance_arcsec":tp.TANGENTIAL_STATION_ANGLE_TOLERANCE_DEG*3600.0,"ae_exact_event_count":len(ae_tan),"sw_exact_event_count":len(sw_tan)}}
    print(json.dumps(out,ensure_ascii=False,indent=2)); return 0

if __name__=="__main__": raise SystemExit(main())
