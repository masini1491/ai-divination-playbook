#!/usr/bin/env python3
"""ChatGPT host-native Swiss known-time natal provider."""
from __future__ import annotations
import argparse, datetime as dt, importlib, json
from itertools import combinations
from typing import Any
from tools.astrology_runtime import MAJOR_ASPECT_ORBS, gate_bundle
from tools.civil_time_normalizer import CivilTimeNormalizationError, normalize_civil_time

PROVIDER_ID="swiss-host-natal-v1"
PROVIDER_VERSION="1.0.0"
CORE_BODY_NAMES=("Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Uranus","Neptune","Pluto","NorthNode")
BODY_ATTRIBUTE={"Sun":"SUN","Moon":"MOON","Mercury":"MERCURY","Venus":"VENUS","Mars":"MARS","Jupiter":"JUPITER","Saturn":"SATURN","Uranus":"URANUS","Neptune":"NEPTUNE","Pluto":"PLUTO","NorthNode":"MEAN_NODE"}
SIGNS=("Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces")
SUPPORTED_HOUSE_SYSTEMS={"Whole Sign","Placidus"}
PLACIDUS_MAX_ABS_LATITUDE=66.0
ASPECT_PARTICIPANT_POLICY_ID="aspect-participants-core-bodies-v1"
ASPECT_POLICY_ID="major-aspects-v1"
ORB_POLICY_ID="major-aspect-orbs-v1"
FORTUNE_POLICY_ID="fortune-day-night-v1"
SECT_POLICY_ID="sect-geometric-solar-altitude-v1"

class SwissProviderUnavailable(RuntimeError): pass
class SwissProviderInputError(ValueError): pass

def _load_swisseph():
    try: return importlib.import_module("swisseph")
    except Exception as exc: raise SwissProviderUnavailable("host-preinstalled swisseph runtime unavailable") from exc

def _resolve_local_time(local_value, timezone_name):
    try: r=normalize_civil_time(local_value, timezone_name)
    except CivilTimeNormalizationError as exc: raise SwissProviderInputError(str(exc)) from exc
    return r.validated_local_datetime, r.resolved_utc_instant, r.fold

def _julian_day(swe, when):
    h=when.hour+when.minute/60+when.second/3600+when.microsecond/3_600_000_000
    return float(swe.julday(when.year,when.month,when.day,h))

def _backend_name(swe, retflag):
    if retflag & swe.FLG_JPLEPH: return "JPLEPH"
    if retflag & swe.FLG_SWIEPH: return "SWIEPH"
    if retflag & swe.FLG_MOSEPH: return "MOSEPH"
    return f"UNKNOWN({retflag})"

def _norm(v): return v%360.0
def _delta(a,b): return ((b-a+180.0)%360.0)-180.0
def _motion(speed): return "stationary" if abs(speed)<0.01 else ("retrograde" if speed<0 else "direct")
def _sign(lon):
    i=int(lon//30.0); return {"sign_index":i,"sign":SIGNS[i],"sign_degree":lon%30.0}
def _house_of(lon,cusps):
    for h in range(1,13):
        a,b=cusps[h],cusps[h%12+1]
        if (lon-a)%360.0 < (b-a)%360.0: return h
    raise RuntimeError("house assignment failed")
def _aspect(a,b):
    sep=abs(_delta(a,b)); targets={"conjunction":0.0,"sextile":60.0,"square":90.0,"trine":120.0,"opposition":180.0}
    name,orb=min(((n,abs(sep-t)) for n,t in targets.items()), key=lambda x:x[1])
    return (name,orb) if orb<=MAJOR_ASPECT_ORBS[name] else None

def _calc_body(swe,jd,body):
    vals,ret=swe.calc_ut(jd,getattr(swe,BODY_ATTRIBUTE[body]),swe.FLG_SWIEPH|swe.FLG_SPEED)
    return {"longitude_deg":float(vals[0])%360.0,"latitude_deg":float(vals[1]),"distance_au":float(vals[2]),"speed_deg_per_day":float(vals[3]),"retflag":int(ret),"effective_backend":_backend_name(swe,int(ret))}

def _house_geometry(swe,jd,lat,lon,system):
    if system=="Placidus" and abs(lat)>PLACIDUS_MAX_ABS_LATITUDE:
        raise SwissProviderInputError(f"Placidus is not admitted above |latitude|>{PLACIDUS_MAX_ABS_LATITUDE}° in production v1")
    code=b"P" if system=="Placidus" else b"W"
    try: raw,ascmc=swe.houses_ex(jd,lat,lon,code)
    except Exception as exc: raise SwissProviderInputError(f"{system} house geometry unavailable") from exc
    if len(raw)!=12 or len(ascmc)<2: raise SwissProviderInputError("incomplete house geometry")
    return [None]+[float(x)%360.0 for x in raw], float(ascmc[0])%360.0, float(ascmc[1])%360.0

def _sun_alt(swe,jd,lat,lon,sun):
    try:
        _,true,_=swe.azalt(jd,swe.ECL2HOR,(lon,lat,0.0),0.0,15.0,(sun["longitude_deg"],sun["latitude_deg"],sun["distance_au"]))
        return float(true)
    except Exception as exc: raise SwissProviderInputError("sect-geometric-solar-altitude-v1 calculation unavailable") from exc

def build_natal_bundle(*,local_datetime,timezone_name,latitude,longitude,house_system,subject_ref,birth_time_certainty="exact"):
    if not -90<=latitude<=90: raise SwissProviderInputError("latitude must be within [-90, 90]")
    if not -180<=longitude<=180: raise SwissProviderInputError("longitude must be within [-180, 180]")
    if house_system not in SUPPORTED_HOUSE_SYSTEMS: raise SwissProviderInputError(f"unsupported house system: {house_system}")
    if birth_time_certainty not in {"exact","approximate"}: raise SwissProviderInputError("host-native Swiss provider admits exact or approximate known-time natal only")
    if not subject_ref or not subject_ref.strip(): raise SwissProviderInputError("subject_ref is required")
    swe=_load_swisseph(); local,utc,fold=_resolve_local_time(local_datetime,timezone_name); jd=_julian_day(swe,utc)
    cusps,asc,mc=_house_geometry(swe,jd,latitude,longitude,house_system)
    data={b:_calc_body(swe,jd,b) for b in CORE_BODY_NAMES}
    alt=_sun_alt(swe,jd,latitude,longitude,data["Sun"]); sect="diurnal" if alt>0 else ("nocturnal" if alt<0 else None)
    if sect is None: raise SwissProviderInputError("sect-geometric-solar-altitude-v1 is undefined at exact 0 degree solar altitude")
    objs=[]
    for b in CORE_BODY_NAMES:
        d=data[b]; lon=d["longitude_deg"]; sp=d["speed_deg_per_day"]
        objs.append({"fact_id":f"fact:object:{b.lower()}","object_type":"point" if b=="NorthNode" else "planet","object_id":b,"longitude_deg":lon,"speed_deg_per_day":sp,"motion":_motion(sp),"house_number":_house_of(lon,cusps),**_sign(lon)})
    objs += [{"fact_id":"fact:angle:ascendant","object_type":"angle","object_id":"Ascendant","longitude_deg":asc,**_sign(asc)},{"fact_id":"fact:angle:midheaven","object_type":"angle","object_id":"Midheaven","longitude_deg":mc,**_sign(mc)}]
    sn=_norm(data["NorthNode"]["longitude_deg"]+180); desc=_norm(asc+180); ic=_norm(mc+180)
    objs += [
      {"fact_id":"fact:object:southnode","object_type":"point","object_id":"SouthNode","node_definition":"mean","longitude_deg":sn,"house_number":_house_of(sn,cusps),"derived_from":"fact:object:northnode","derivation_policy":"antipode-v1",**_sign(sn)},
      {"fact_id":"fact:angle:descendant","object_type":"angle","object_id":"Descendant","longitude_deg":desc,"derived_from":"fact:angle:ascendant","derivation_policy":"antipode-v1",**_sign(desc)},
      {"fact_id":"fact:angle:imumcoeli","object_type":"angle","object_id":"ImumCoeli","longitude_deg":ic,"derived_from":"fact:angle:midheaven","derivation_policy":"antipode-v1",**_sign(ic)}]
    fortune=_norm(asc + (data["Moon"]["longitude_deg"]-data["Sun"]["longitude_deg"] if sect=="diurnal" else data["Sun"]["longitude_deg"]-data["Moon"]["longitude_deg"]))
    objs.append({"fact_id":"fact:object:partoffortune","object_type":"point","object_id":"PartOfFortune","point_kind":"lot","longitude_deg":fortune,"house_number":_house_of(fortune,cusps),"derived_from":["fact:angle:ascendant","fact:object:sun","fact:object:moon"],"derivation_policy":FORTUNE_POLICY_ID,"sect_policy_id":SECT_POLICY_ID,"sect":sect,"sun_geometric_altitude_deg":alt,**_sign(fortune)})
    houses=[{"fact_id":f"fact:house:{h}","house_number":h,"cusp_longitude_deg":float(cusps[h]),**_sign(float(cusps[h]))} for h in range(1,13)]
    aspects=[]
    for l,r in combinations(CORE_BODY_NAMES,2):
        ar=_aspect(data[l]["longitude_deg"],data[r]["longitude_deg"])
        if ar:
            name,orb=ar; aspects.append({"fact_id":f"fact:aspect:{l.lower()}:{name}:{r.lower()}","aspect":name,"orb_deg":orb,"left_ref":f"fact:object:{l.lower()}","right_ref":f"fact:object:{r.lower()}","scope":"natal","participant_policy_id":ASPECT_PARTICIPANT_POLICY_ID,"aspect_policy_id":ASPECT_POLICY_ID,"orb_policy_id":ORB_POLICY_ID})
    bundle={"schema_name":"astrology_fact_bundle","schema_version":"1.0.0","method":"Astrology","reading_mode":"natal","fact_source":"approved_provider","calculation_verification":"verified_provider","subject_ref":subject_ref,"birth_time_certainty":birth_time_certainty,"configuration":{"zodiac_system":"tropical","center":"geocentric","house_system":house_system},"provider":{"provider_id":PROVIDER_ID,"provider_version":PROVIDER_VERSION,"runtime_source":"chatgpt_host_preinstalled","pyswisseph_version":getattr(swe,"version",None),"requested_ephemeris_flags":int(swe.FLG_SWIEPH|swe.FLG_SPEED),"actual_retflag_per_calculated_object":{b:data[b]["retflag"] for b in CORE_BODY_NAMES},"effective_backend_per_calculated_object":{b:data[b]["effective_backend"] for b in CORE_BODY_NAMES},"local_datetime":local_datetime,"timezone_name":timezone_name,"resolved_local_iso":local.isoformat(),"resolved_utc_iso":utc.isoformat(),"fold":fold,"latitude":latitude,"longitude":longitude,"julian_day_ut":jd,"aspect_policies":{"participant_policy_id":ASPECT_PARTICIPANT_POLICY_ID,"participant_object_ids":list(CORE_BODY_NAMES),"aspect_policy_id":ASPECT_POLICY_ID,"aspect_types":list(MAJOR_ASPECT_ORBS),"orb_policy_id":ORB_POLICY_ID,"max_orb_degrees":dict(MAJOR_ASPECT_ORBS),"extended_points_or_angles":"not_admitted"},"sect":{"classification":sect,"policy_id":SECT_POLICY_ID,"sun_geometric_altitude_deg":alt,"refraction":"Airless/true_altitude","sun_frame":"geocentric-ecliptic-to-horizontal"}},"facts":{"objects":objs,"houses":houses,"aspects":aspects,"events":[]}}
    gate=gate_bundle(bundle)
    if not gate["interpretation_allowed"]: raise RuntimeError("host-native Swiss provider emitted rejected bundle: "+json.dumps(gate["errors"],ensure_ascii=False))
    return bundle

def main():
    p=argparse.ArgumentParser(); p.add_argument("--local-datetime",required=True); p.add_argument("--timezone",required=True); p.add_argument("--latitude",type=float,required=True); p.add_argument("--longitude",type=float,required=True); p.add_argument("--house-system",choices=sorted(SUPPORTED_HOUSE_SYSTEMS),default="Placidus"); p.add_argument("--subject-ref",required=True); p.add_argument("--birth-time-certainty",choices=["exact","approximate"],default="exact"); a=p.parse_args()
    print(json.dumps(build_natal_bundle(local_datetime=a.local_datetime,timezone_name=a.timezone,latitude=a.latitude,longitude=a.longitude,house_system=a.house_system,subject_ref=a.subject_ref,birth_time_certainty=a.birth_time_certainty),ensure_ascii=False,indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
