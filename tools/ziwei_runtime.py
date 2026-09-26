#!/usr/bin/env python3
"""Canonical typed runtime for admitted Zi Wei production composition.

This owner normalizes the admitted request surface, selects optional modules,
binds deterministic providers to admitted claim retrieval/delivery, and emits
one versioned result shape. Legacy pipeline entrypoints are compatibility
adapters only.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from tools import ziwei_claim_retrieval as _retrieval
from tools import ziwei_delivery as _delivery
from tools.ziwei_brightness_provider import PROFILE_ID as BRIGHTNESS_PROFILE_ID, calculate_brightness
from tools.ziwei_calendar_provider import GregorianBirthInput, normalize_gregorian_birth
from tools.ziwei_natal_provider import NormalizedNatalInput, calculate_scope_a_natal
from tools.ziwei_m0_auxiliary_provider import PROFILE_ID as M0_PROFILE_ID, calculate_m0_auxiliary
from tools.ziwei_sihua_provider import PROFILE_ID as SIHUA_PROFILE_ID, calculate_sihua
from tools.ziwei_decadal_provider import DecadalTarget, calculate_decadal
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REF=ROOT/"references"/"ziwei"

RUNTIME_ID="ziwei-production-runtime-v1"
RUNTIME_VERSION="1.0.0"
REQUEST_SCHEMA="schemas/ziwei/ZIWEI_READING_REQUEST_V1.schema.json"
RESULT_SCHEMA="schemas/ziwei/ZIWEI_READING_RESULT_V1.schema.json"
DYNAMIC_RUNTIME_ID="ziwei-production-runtime-v2"
DYNAMIC_RUNTIME_VERSION="2.0.0"
DYNAMIC_REQUEST_SCHEMA="schemas/ziwei/ZIWEI_DYNAMIC_REQUEST_V2.schema.json"
DYNAMIC_RESULT_SCHEMA="schemas/ziwei/ZIWEI_DYNAMIC_RESULT_V2.schema.json"
INTERPRETATION_PROFILE="ziwei.interpretation.tw_v1"
TEMPORAL_SCOPE="natal_baseline"
BRIGHTNESS_MODULE="brightness_v1"
M0_MODULE="m0_auxiliary_v1"
SIHUA_MODULE="sihua_v1"
ADMITTED_REGISTRIES=(
    "ziwei_interpretation_claim_registry_batch1.json",
    "ziwei_interpretation_claim_registry_batch2.json",
    "ziwei_interpretation_claim_registry_palaces_v0.json",
)
M0_REGISTRY="ziwei_interpretation_claim_registry_m0_auxiliary_v1.json"
SIHUA_REGISTRY="ziwei_interpretation_claim_registry_sihua_v0.json"

@dataclass(frozen=True)
class ZiWeiReadingRequest:
    request_id: str
    birth: GregorianBirthInput | NormalizedNatalInput
    temporal_scope: Literal["natal_baseline"] = TEMPORAL_SCOPE
    requested_subjects: tuple[str,...] = ()
    enabled_source_ids: tuple[str,...] = ()
    optional_modules: tuple[str,...] = ()
    brightness_profile: str | None = None
    m0_auxiliary_profile: str | None = None
    sihua_profile: str | None = None

    def validate(self) -> None:
        if not isinstance(self.request_id,str) or not self.request_id.strip():
            raise ValueError("request_id is required")
        if self.temporal_scope != TEMPORAL_SCOPE:
            raise ValueError(f"unsupported temporal_scope: {self.temporal_scope}")
        if not isinstance(self.birth,(GregorianBirthInput,NormalizedNatalInput)):
            raise ValueError("birth must be GregorianBirthInput or NormalizedNatalInput")
        unknown=sorted(set(self.optional_modules)-{BRIGHTNESS_MODULE,M0_MODULE,SIHUA_MODULE})
        if unknown:
            raise ValueError(f"unsupported optional_modules: {','.join(unknown)}")
        if len(set(self.optional_modules)) != len(self.optional_modules):
            raise ValueError("optional_modules must be unique")
        if self.brightness_profile is not None and BRIGHTNESS_MODULE not in self.optional_modules:
            raise ValueError("brightness_profile requires brightness_v1")
        if BRIGHTNESS_MODULE in self.optional_modules:
            if self.brightness_profile not in (None,BRIGHTNESS_PROFILE_ID):
                raise ValueError(f"unsupported brightness_profile: {self.brightness_profile}")
        if self.m0_auxiliary_profile is not None and M0_MODULE not in self.optional_modules:
            raise ValueError("m0_auxiliary_profile requires m0_auxiliary_v1")
        if M0_MODULE in self.optional_modules and self.m0_auxiliary_profile not in (None,M0_PROFILE_ID):
            raise ValueError(f"unsupported m0_auxiliary_profile: {self.m0_auxiliary_profile}")
        if self.sihua_profile is not None and SIHUA_MODULE not in self.optional_modules:
            raise ValueError("sihua_profile requires sihua_v1")
        if SIHUA_MODULE in self.optional_modules and self.sihua_profile not in (None,SIHUA_PROFILE_ID):
            raise ValueError(f"unsupported sihua_profile: {self.sihua_profile}")

def request_to_transport(request:ZiWeiReadingRequest)->dict[str,Any]:
    """Serialize the typed request into the versioned JSON transport contract."""
    request.validate()
    if isinstance(request.birth,GregorianBirthInput):
        birth={
            "input_type":"gregorian",
            "year":request.birth.year,"month":request.birth.month,"day":request.birth.day,
            "hour":request.birth.hour,"minute":request.birth.minute,"second":request.birth.second,
            "timezone":request.birth.timezone,
        }
    else:
        birth={
            "input_type":"normalized_lunar",
            "lunar_year":request.birth.lunar_year,"lunar_month":request.birth.lunar_month,
            "lunar_day":request.birth.lunar_day,"hour_branch":request.birth.hour_branch,
            "calendar_provenance":request.birth.calendar_provenance,
            "leap_month_identity":request.birth.leap_month_identity,
        }
    payload={
        "schema_name":"ziwei_reading_request","schema_version":"1.0.0",
        "request_id":request.request_id,"temporal_scope":request.temporal_scope,
        "birth":birth,"optional_modules":list(request.optional_modules),
        "requested_subjects":list(request.requested_subjects),
        "enabled_source_ids":list(request.enabled_source_ids),
    }
    if request.brightness_profile is not None:
        payload["brightness_profile"]=request.brightness_profile
    if request.m0_auxiliary_profile is not None:
        payload["m0_auxiliary_profile"]=request.m0_auxiliary_profile
    if request.sihua_profile is not None:
        payload["sihua_profile"]=request.sihua_profile
    return payload

def request_from_transport(payload:dict[str,Any])->ZiWeiReadingRequest:
    """Parse the closed-world v1 JSON transport into the typed runtime request."""
    if not isinstance(payload,dict):
        raise ValueError("request transport must be an object")
    allowed={"schema_name","schema_version","request_id","temporal_scope","birth","optional_modules",
             "requested_subjects","enabled_source_ids","brightness_profile","m0_auxiliary_profile","sihua_profile"}
    required=allowed-{"brightness_profile","m0_auxiliary_profile","sihua_profile"}
    unknown=set(payload)-allowed
    missing=required-set(payload)
    if unknown:
        raise ValueError(f"unknown request fields: {','.join(sorted(unknown))}")
    if missing:
        raise ValueError(f"missing request fields: {','.join(sorted(missing))}")
    if payload["schema_name"]!="ziwei_reading_request" or payload["schema_version"]!="1.0.0":
        raise ValueError("unsupported Zi Wei request schema")
    birth=payload["birth"]
    if not isinstance(birth,dict):
        raise ValueError("birth must be an object")
    input_type=birth.get("input_type")
    if input_type=="gregorian":
        fields={"input_type","year","month","day","hour","minute","second","timezone"}
        if set(birth)!=fields:
            raise ValueError("gregorian birth fields do not match v1 schema")
        typed_birth=GregorianBirthInput(
            year=birth["year"],month=birth["month"],day=birth["day"],hour=birth["hour"],
            minute=birth["minute"],second=birth["second"],timezone=birth["timezone"],
        )
    elif input_type=="normalized_lunar":
        fields={"input_type","lunar_year","lunar_month","lunar_day","hour_branch","calendar_provenance","leap_month_identity"}
        if set(birth)!=fields:
            raise ValueError("normalized lunar birth fields do not match v1 schema")
        typed_birth=NormalizedNatalInput(
            lunar_year=birth["lunar_year"],lunar_month=birth["lunar_month"],lunar_day=birth["lunar_day"],
            hour_branch=birth["hour_branch"],calendar_provenance=birth["calendar_provenance"],
            leap_month_identity=birth["leap_month_identity"],
        )
    else:
        raise ValueError(f"unsupported birth input_type: {input_type}")
    for name in ("optional_modules","requested_subjects","enabled_source_ids"):
        if not isinstance(payload[name],list) or any(not isinstance(x,str) or not x for x in payload[name]):
            raise ValueError(f"{name} must be an array of non-empty strings")
        if len(set(payload[name]))!=len(payload[name]):
            raise ValueError(f"{name} must contain unique items")
    request=ZiWeiReadingRequest(
        request_id=payload["request_id"],birth=typed_birth,temporal_scope=payload["temporal_scope"],
        requested_subjects=tuple(payload["requested_subjects"]),enabled_source_ids=tuple(payload["enabled_source_ids"]),
        optional_modules=tuple(payload["optional_modules"]),brightness_profile=payload.get("brightness_profile"),
        m0_auxiliary_profile=payload.get("m0_auxiliary_profile"),sihua_profile=payload.get("sihua_profile"),
    )
    request.validate()
    return request

def run_ziwei_transport(payload:dict[str,Any])->dict[str,Any]:
    """Execute the versioned JSON transport contract through the canonical typed runtime."""
    return run_ziwei(request_from_transport(payload))

def _production_registries(optional_modules:tuple[str,...]=()):
    names=list(ADMITTED_REGISTRIES)
    if M0_MODULE in optional_modules:
        names.append(M0_REGISTRY)
    if SIHUA_MODULE in optional_modules:
        names.append(SIHUA_REGISTRY)
    regs=_retrieval.load_registries(REF/x for x in names)
    for name,reg in zip(names,regs):
        if reg.get("production_routable") is not False:
            raise ValueError(f"REGISTRY_HISTORY_MUTATED:{name}")
        if reg.get("interpretation_profile") != INTERPRETATION_PROFILE:
            raise ValueError(f"REGISTRY_PROFILE_MISMATCH:{name}")
    return regs

def _normalize_birth(birth:GregorianBirthInput|NormalizedNatalInput)->tuple[NormalizedNatalInput,dict[str,Any]|None]:
    if isinstance(birth,NormalizedNatalInput):
        birth.validate()
        return birth,None
    calendar=normalize_gregorian_birth(birth)
    n=calendar["normalized_natal_input"]
    return NormalizedNatalInput(
        lunar_year=n["lunar_year"], lunar_month=n["lunar_month"], lunar_day=n["lunar_day"],
        hour_branch=n["hour_branch"], calendar_provenance=n["calendar_provenance"],
        leap_month_identity=n["leap_month_identity"],
    ),calendar

def _compose(chart:dict[str,Any], request:ZiWeiReadingRequest, calendar:dict[str,Any]|None)->dict[str,Any]:
    packet=_retrieval.FactPacket(
        packet_id=f"{request.request_id}:facts",
        interpretation_profile=INTERPRETATION_PROFILE,
        temporal_scope=TEMPORAL_SCOPE,
        facts=frozenset(chart["retrieval_facts"]),
        requested_subjects=frozenset(request.requested_subjects),
        enabled_source_ids=frozenset(request.enabled_source_ids),
    )
    retrieval=_retrieval.retrieve_claims(packet,_production_registries(request.optional_modules))
    frame=_retrieval.compose_frame(packet,retrieval)
    conflicts=frame["conflicts"]
    evidence_states={"source_backed","project_adopted"}
    if conflicts:
        evidence_states.add("conflicted")
    actions=_delivery.delivery_actions(evidence_states=evidence_states)
    modules=list(request.optional_modules)
    result={
        "schema_name":"ziwei_reading_result",
        "schema_version":"1.0.0",
        "runtime":{
            "runtime_id":RUNTIME_ID,
            "runtime_version":RUNTIME_VERSION,
            "request_schema":REQUEST_SCHEMA,
            "result_schema":RESULT_SCHEMA,
            "temporal_scope":TEMPORAL_SCOPE,
            "optional_modules":modules,
        },
        "pipeline_id":"ziwei-scope-a-production-pipeline-v1",
        "pipeline_version":"1.2.0",
        "status":"PRODUCTION_ADMITTED",
        "scope":"bounded_natal_first_layer"+("+optional_brightness_v1" if BRIGHTNESS_MODULE in modules else "")+("+optional_m0_auxiliary_v1" if M0_MODULE in modules else "")+("+optional_sihua_v1" if SIHUA_MODULE in modules else ""),
        "request_id":request.request_id,
        "calculation":{
            "provider":chart["provider"], "calculation_profile":chart["calculation_profile"],
            "input_provenance":chart["input_provenance"], "normalized_input":chart["normalized_input"],
            "year_pillar":chart["year_pillar"], "life_palace":chart["life_palace"],
            "body_palace":chart["body_palace"], "five_element_bureau":chart["five_element_bureau"],
            "ziwei_branch":chart["ziwei_branch"], "major_star_placements":chart["major_star_placements"],
            "palaces":chart["palaces"], "palace_occupancy":chart["palace_occupancy"],
            "topology":chart["topology"], "unsupported":chart["unsupported"],
        },
        "interpretation":{
            "profile":INTERPRETATION_PROFILE, "temporal_scope":TEMPORAL_SCOPE,
            "selected_claims":retrieval["selected_claims"], "selected_claim_ids":frame["selected_claim_ids"],
            "conditional_evaluations":retrieval["conditional_evaluations"], "subject_claims":frame["subject_claims"],
            "conflicts":conflicts, "omissions":retrieval["omissions"],
        },
        "delivery":{
            "evidence_states":sorted(evidence_states), "actions":actions,
            "rendering_boundary":"admitted_claims_only_no_new_doctrine",
            "high_impact_requires_bounded_delivery":True,
        },
        "authority":{
            "production_authority_granted":True, "ordinary_auto_routing":False,
            "final_prose_authority":False, "scientific_predictive_validity_claimed":False,
        },
    }
    if calendar is not None:
        result["input_adapter"]={
            "pipeline_id":"ziwei-gregorian-input-adapter-v1",
            "pipeline_version":"1.0.0",
            "calendar":calendar,
        }
        result["authority"]["gregorian_input_adapter_admitted"]=True
    return result

def run_ziwei(request:ZiWeiReadingRequest)->dict[str,Any]:
    request.validate()
    natal,calendar=_normalize_birth(request.birth)
    chart=calculate_scope_a_natal(natal)
    if M0_MODULE in request.optional_modules:
        m0=calculate_m0_auxiliary(natal,chart["major_star_placements"])
        chart=dict(chart)
        chart["retrieval_facts"]=list(chart["retrieval_facts"])+list(m0["retrieval_facts"])
        unsupported=dict(chart["unsupported"])
        unsupported["m0_auxiliary_stars"]="computed_by_optional_m0_profile"
        chart["unsupported"]=unsupported
        chart["m0_auxiliary"]=m0
    if BRIGHTNESS_MODULE in request.optional_modules:
        brightness=calculate_brightness(chart["major_star_placements"])
        chart=dict(chart)
        chart["retrieval_facts"]=list(chart["retrieval_facts"])+list(brightness["retrieval_facts"])
        unsupported=dict(chart["unsupported"])
        unsupported["brightness"]="computed_by_optional_profile"
        chart["unsupported"]=unsupported
        chart["brightness"]=brightness
    if SIHUA_MODULE in request.optional_modules:
        sihua=calculate_sihua(chart["year_pillar"]["stem"],sihua_profile_id=request.sihua_profile or SIHUA_PROFILE_ID)
        chart=dict(chart)
        chart["retrieval_facts"]=list(chart["retrieval_facts"])+list(sihua["retrieval_facts"])
        unsupported=dict(chart["unsupported"])
        unsupported["four_transformations"]="computed_by_optional_sihua_profile"
        chart["unsupported"]=unsupported
        chart["sihua"]=sihua
    result=_compose(chart,request,calendar)
    if M0_MODULE in request.optional_modules:
        result["calculation"]["m0_auxiliary"]=chart["m0_auxiliary"]
        result["authority"]["m0_auxiliary_profile_admitted"]=True
        result["authority"]["blanket_minor_star_admission"]=False
    if BRIGHTNESS_MODULE in request.optional_modules:
        result["calculation"]["brightness"]=chart["brightness"]
        result["authority"]["brightness_profile_admitted"]=True
        result["authority"]["brightness_only_doctrine_admitted"]=False
    if SIHUA_MODULE in request.optional_modules:
        result["calculation"]["sihua"]=chart["sihua"]
        result["authority"]["sihua_profile_admitted"]=True
        result["authority"]["sihua_transformed_star_claims_admitted"]=True
        result["authority"]["generic_sihua_outcome_doctrine_admitted"]=False
    return result

def legacy_result(result:dict[str,Any], *, brightness:bool=False) -> dict[str,Any]:
    """Project the typed v1 result back to the pre-v1 public pipeline surface."""
    legacy=dict(result)
    legacy.pop("schema_name",None)
    legacy.pop("schema_version",None)
    legacy.pop("runtime",None)
    if brightness:
        legacy["pipeline_id"]="ziwei-scope-a-brightness-production-pipeline-v1"
        legacy["pipeline_version"]="1.0.0"
    return legacy


@dataclass(frozen=True)
class ZiWeiDecadalRequest:
    request_id: str
    birth: GregorianBirthInput | NormalizedNatalInput
    gender: Literal["male","female"]
    target_lunar_year: int
    temporal_scope: Literal["decadal"] = "decadal"
    requested_subjects: tuple[str,...] = ()
    enabled_source_ids: tuple[str,...] = ()

    def validate(self) -> None:
        if not isinstance(self.request_id,str) or not self.request_id.strip():
            raise ValueError("request_id is required")
        if self.temporal_scope != "decadal":
            raise ValueError(f"unsupported temporal_scope: {self.temporal_scope}")
        if not isinstance(self.birth,(GregorianBirthInput,NormalizedNatalInput)):
            raise ValueError("birth must be GregorianBirthInput or NormalizedNatalInput")
        if self.gender not in ("male","female"):
            raise ValueError("gender must be male or female")
        if not isinstance(self.target_lunar_year,int):
            raise ValueError("target_lunar_year must be an integer")
        for name,values in (
            ("requested_subjects",self.requested_subjects),
            ("enabled_source_ids",self.enabled_source_ids),
        ):
            if any(not isinstance(x,str) or not x for x in values):
                raise ValueError(f"{name} must contain non-empty strings")
            if len(set(values)) != len(values):
                raise ValueError(f"{name} must contain unique items")


def run_ziwei_decadal(request:ZiWeiDecadalRequest)->dict[str,Any]:
    """Execute admitted decadal calculation only; interpretation remains closed."""
    request.validate()
    natal,calendar=_normalize_birth(request.birth)
    calculation=calculate_decadal(
        natal,
        DecadalTarget(gender=request.gender,target_lunar_year=request.target_lunar_year),
    )
    result={
        "schema_name":"ziwei_dynamic_result",
        "schema_version":"2.0.0",
        "runtime":{
            "runtime_id":DYNAMIC_RUNTIME_ID,
            "runtime_version":DYNAMIC_RUNTIME_VERSION,
            "request_schema":DYNAMIC_REQUEST_SCHEMA,
            "result_schema":DYNAMIC_RESULT_SCHEMA,
            "temporal_scope":"decadal",
        },
        "status":"PRODUCTION_ADMITTED_CALCULATION_ONLY",
        "scope":"bounded_decadal_calculation_v1",
        "request_id":request.request_id,
        "calculation":calculation,
        "interpretation":{
            "status":"NOT_ADMITTED",
            "reason":"ZW-P1-040 decadal interpretation not yet admitted",
        },
        "authority":{
            "calculation_authority_granted":True,
            "interpretation_authority_granted":False,
            "ordinary_auto_routing":False,
        },
    }
    if calendar is not None:
        result["input_adapter"]={
            "pipeline_id":"ziwei-gregorian-input-adapter-v1",
            "pipeline_version":"1.0.0",
            "calendar":calendar,
        }
    return result


def run_ziwei_dynamic_transport(payload:dict[str,Any])->dict[str,Any]:
    """Parse the closed-world v2 decadal transport and execute calculation only."""
    if not isinstance(payload,dict):
        raise ValueError("dynamic request transport must be an object")
    allowed={
        "schema_name","schema_version","request_id","temporal_scope","birth","gender",
        "target_lunar_year","requested_subjects","enabled_source_ids",
    }
    required=allowed
    unknown=set(payload)-allowed
    missing=required-set(payload)
    if unknown:
        raise ValueError(f"unknown dynamic request fields: {','.join(sorted(unknown))}")
    if missing:
        raise ValueError(f"missing dynamic request fields: {','.join(sorted(missing))}")
    if payload["schema_name"]!="ziwei_dynamic_request" or payload["schema_version"]!="2.0.0":
        raise ValueError("unsupported Zi Wei dynamic request schema")
    if payload["temporal_scope"]!="decadal":
        raise ValueError(f"unsupported temporal_scope: {payload['temporal_scope']}")
    birth=payload["birth"]
    if not isinstance(birth,dict):
        raise ValueError("birth must be an object")
    input_type=birth.get("input_type")
    if input_type=="gregorian":
        expected={"input_type","year","month","day","hour","minute","second","timezone"}
        if set(birth)!=expected:
            raise ValueError("gregorian birth fields mismatch")
        typed_birth=GregorianBirthInput(
            year=birth["year"],month=birth["month"],day=birth["day"],hour=birth["hour"],
            minute=birth["minute"],second=birth["second"],timezone=birth["timezone"],
        )
    elif input_type=="normalized_lunar":
        expected={"input_type","lunar_year","lunar_month","lunar_day","hour_branch","calendar_provenance","leap_month_identity"}
        if set(birth)!=expected:
            raise ValueError("normalized_lunar birth fields mismatch")
        typed_birth=NormalizedNatalInput(
            lunar_year=birth["lunar_year"],lunar_month=birth["lunar_month"],lunar_day=birth["lunar_day"],
            hour_branch=birth["hour_branch"],calendar_provenance=birth["calendar_provenance"],
            leap_month_identity=birth["leap_month_identity"],
        )
    else:
        raise ValueError(f"unsupported birth input_type: {input_type}")
    for name in ("requested_subjects","enabled_source_ids"):
        values=payload[name]
        if not isinstance(values,list) or any(not isinstance(x,str) or not x for x in values):
            raise ValueError(f"{name} must be an array of non-empty strings")
        if len(set(values))!=len(values):
            raise ValueError(f"{name} must contain unique items")
    request=ZiWeiDecadalRequest(
        request_id=payload["request_id"],
        birth=typed_birth,
        gender=payload["gender"],
        target_lunar_year=payload["target_lunar_year"],
        temporal_scope=payload["temporal_scope"],
        requested_subjects=tuple(payload["requested_subjects"]),
        enabled_source_ids=tuple(payload["enabled_source_ids"]),
    )
    return run_ziwei_decadal(request)
