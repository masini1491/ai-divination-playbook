#!/usr/bin/env python3
from __future__ import annotations

from typing import Any

SCHEMA_VERSION = "0.1.0-candidate"
FACT_STATES = {"known","unknown","not_computed","ambiguous","not_applicable"}
TEMPORAL_SCOPES = {"natal_baseline","decadal","yearly","monthly","daily","hourly"}

def validate_fact(fact: dict[str, Any]) -> list[str]:
    errors=[]
    for key in ("fact_id","fact_type","state","source_provenance"):
        if key not in fact:
            errors.append(f"FACT_REQUIRED:{key}")
    state=fact.get("state")
    if state not in FACT_STATES:
        errors.append("FACT_STATE_INVALID")
    if state=="known" and "value" not in fact:
        errors.append("KNOWN_VALUE_REQUIRED")
    if state=="known" and not fact.get("source_provenance"):
        errors.append("KNOWN_PROVENANCE_REQUIRED")
    if fact.get("fact_type")=="brightness":
        if state=="known" and not fact.get("profile_scope",{}).get("brightness_profile_id"):
            errors.append("BRIGHTNESS_PROFILE_REQUIRED")
    if fact.get("fact_type")=="four_transformation":
        if state=="known" and not fact.get("profile_scope",{}).get("sihua_profile_id"):
            errors.append("SIHUA_PROFILE_REQUIRED")
    if fact.get("fact_type")=="temporal":
        ps=fact.get("profile_scope",{})
        if state=="known" and not all(ps.get(x) for x in ("temporal_scope","target_identity","boundary_profile")):
            errors.append("TEMPORAL_IDENTITY_REQUIRED")
    return errors

def validate_packet(packet: dict[str, Any]) -> list[str]:
    errors=[]
    for key in ("packet_id","schema_version","request_id","interpretation_profile","calculation_profile","temporal_context","facts","topology","ambiguity","validation","provenance_map"):
        if key not in packet:
            errors.append(f"PACKET_REQUIRED:{key}")
    if packet.get("schema_version") != SCHEMA_VERSION:
        errors.append("SCHEMA_VERSION_INVALID")
    scope=packet.get("temporal_context",{}).get("scope")
    if scope not in TEMPORAL_SCOPES:
        errors.append("TEMPORAL_SCOPE_INVALID")
    facts=packet.get("facts",[])
    if not isinstance(facts,list):
        errors.append("FACTS_NOT_ARRAY")
        return errors
    ids=set()
    for fact in facts:
        if not isinstance(fact,dict):
            errors.append("FACT_NOT_OBJECT")
            continue
        fid=fact.get("fact_id")
        if fid in ids:
            errors.append("FACT_ID_DUPLICATE")
        ids.add(fid)
        errors.extend(validate_fact(fact))
    return errors
