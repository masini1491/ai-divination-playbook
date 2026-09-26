#!/usr/bin/env python3
"""Production evaluator for the admitted query-bounded extended ephemeris dataset.

No network access is performed here. The evaluator consumes the project-owned
C1 Chebyshev coefficient manifest plus exactly the shard required by the query.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import math
import struct
from pathlib import Path
from typing import Any

PROVIDER_ID = "astrology-extended-ephemeris-c1-v1"
PROVIDER_VERSION = "1.0.0"
DATASET_ID = "astrology-extended-ephemeris-c1-v1"
DATASET_SHA256 = "460b310131149b012b615dde15fcf892b85142fd2490fa1c5f35613697b93cc3"
REPRESENTATION_ID = "c1-cheb-d7-w60"
OBJECT_IDS = ("Chiron", "Ceres", "Pallas", "Juno", "Vesta")
MANIFEST_RELATIVE = Path("data/astrology/extended_ephemeris/v1/MANIFEST.json")
CACHE_ROOT = Path("/mnt/data/divination-astrology-runtime/extended_ephemeris/v1")
SIGNS = (
    "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
    "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces",
)

class ExtendedEphemerisError(ValueError):
    pass

def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def _git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()

def _parse_utc(value: str | dt.datetime) -> dt.datetime:
    if isinstance(value, dt.datetime):
        parsed=value
    else:
        try:
            parsed=dt.datetime.fromisoformat(value.replace("Z","+00:00"))
        except (TypeError,ValueError) as exc:
            raise ExtendedEphemerisError("utc must be ISO-8601") from exc
    if parsed.tzinfo is None:
        raise ExtendedEphemerisError("utc must be timezone-aware")
    return parsed.astimezone(dt.timezone.utc)

def _default_data_root() -> Path:
    repo_root=Path(__file__).resolve().parents[1]
    repo_data=repo_root/"data"/"astrology"/"extended_ephemeris"/"v1"
    if (repo_data/"MANIFEST.json").exists():
        return repo_data
    return CACHE_ROOT

def load_manifest(data_root: Path | None = None) -> tuple[Path, dict[str,Any]]:
    root=Path(data_root) if data_root is not None else _default_data_root()
    path=root/"MANIFEST.json"
    try:
        manifest=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError) as exc:
        raise ExtendedEphemerisError("extended ephemeris manifest unavailable or invalid") from exc
    if manifest.get("schema_name")!="astrology_extended_ephemeris_dataset":
        raise ExtendedEphemerisError("extended ephemeris manifest schema mismatch")
    if manifest.get("dataset_id")!=DATASET_ID:
        raise ExtendedEphemerisError("extended ephemeris dataset id mismatch")
    if manifest.get("production_admission")!="PRODUCTION_ADMITTED":
        raise ExtendedEphemerisError("extended ephemeris dataset is not production-admitted")
    if manifest.get("dataset",{}).get("sha256")!=DATASET_SHA256:
        raise ExtendedEphemerisError("extended ephemeris dataset digest mismatch")
    if manifest.get("representation",{}).get("id")!=REPRESENTATION_ID:
        raise ExtendedEphemerisError("extended ephemeris representation mismatch")
    if tuple(manifest.get("representation",{}).get("object_order",()))!=OBJECT_IDS:
        raise ExtendedEphemerisError("extended ephemeris object order mismatch")
    return root,manifest

def required_shard_for_utc(utc: str | dt.datetime, manifest: dict[str,Any]) -> dict[str,Any]:
    when=_parse_utc(utc)
    rep=manifest["representation"]
    start=dt.datetime.fromisoformat(rep["coverage_start"])
    admitted_end=dt.datetime.fromisoformat(rep["admitted_output_window_end"])
    if when < start or when > admitted_end:
        raise ExtendedEphemerisError("date outside admitted extended ephemeris coverage")
    width=int(rep["segment_width_days"])
    segment_count=int(rep["segment_count"])
    offset=(when-start).total_seconds()/86400.0
    segment=min(int(offset//width),segment_count-1)
    for shard in manifest["dataset"]["shards"]:
        first=int(shard["first_segment"]); count=int(shard["segment_count"])
        if first <= segment < first+count:
            return {**shard,"segment_index":segment}
    raise ExtendedEphemerisError("required extended ephemeris shard not declared")

def _load_decoded_shard(root: Path, shard: dict[str,Any]) -> bytes:
    path=root/shard["path"]
    try:
        raw=path.read_bytes()
    except OSError as exc:
        raise ExtendedEphemerisError("required extended ephemeris shard missing") from exc
    if len(raw)!=int(shard["byte_size"]) or _sha256(raw)!=shard["sha256"]:
        raise ExtendedEphemerisError("extended ephemeris shard identity mismatch")
    if _git_blob_sha(raw)!=shard["git_blob_sha"]:
        raise ExtendedEphemerisError("extended ephemeris Git blob identity mismatch")
    return raw

def _basis(x: float, count: int) -> list[float]:
    if count<2: raise ExtendedEphemerisError("coefficient count invalid")
    out=[1.0,x]
    for _ in range(2,count):
        out.append(2.0*x*out[-1]-out[-2])
    return out

def _derivative_basis(x: float, count: int, width: float) -> list[float]:
    out=[0.0]*count
    out[1]=2.0/width
    if count>2:
        u_prev=1.0; u_curr=2.0*x
        out[2]=2.0*u_curr*(2.0/width)
        for n in range(3,count):
            u_next=2.0*x*u_curr-u_prev
            out[n]=n*u_next*(2.0/width)
            u_prev,u_curr=u_curr,u_next
    return out

def _sign_fields(longitude: float) -> dict[str,Any]:
    lon=longitude%360.0
    idx=int(lon//30)
    return {"sign_index":idx,"sign":SIGNS[idx],"sign_degree":lon-idx*30.0}

def _motion(speed: float) -> str:
    if abs(speed)<0.01: return "stationary"
    return "retrograde" if speed<0 else "direct"

def _house_of(longitude: float, house_facts: list[dict[str,Any]]) -> int | None:
    if not house_facts:
        return None
    cusps={int(row["house_number"]):float(row["cusp_longitude_deg"]) for row in house_facts}
    if set(cusps)!=set(range(1,13)):
        raise ExtendedEphemerisError("complete 12-house facts required for extended house placement")
    lon=longitude%360.0
    for house in range(1,13):
        a=cusps[house]%360.0; b=cusps[1 if house==12 else house+1]%360.0
        span=(b-a)%360.0
        if ((lon-a)%360.0)<span:
            return house
    raise ExtendedEphemerisError("extended object house placement failed")

def evaluate_object(
    object_id: str,
    utc: str | dt.datetime,
    *,
    data_root: Path | None = None,
) -> dict[str,Any]:
    if object_id not in OBJECT_IDS:
        raise ExtendedEphemerisError(f"unsupported extended object: {object_id}")
    when=_parse_utc(utc)
    root,manifest=load_manifest(data_root)
    shard=required_shard_for_utc(when,manifest)
    raw=_load_decoded_shard(root,shard)
    rep=manifest["representation"]
    width=float(rep["segment_width_days"])
    coeff_count=int(rep["coefficients_per_object_segment"])
    objects=rep["object_order"]
    segment=int(shard["segment_index"])
    within=segment-int(shard["first_segment"])
    obj_index=objects.index(object_id)
    record_size=coeff_count*8
    offset=(within*len(objects)+obj_index)*record_size
    record=raw[offset:offset+record_size]
    if len(record)!=record_size:
        raise ExtendedEphemerisError("extended ephemeris coefficient record truncated")
    coeff=list(struct.unpack("<"+"d"*coeff_count,record))
    start=dt.datetime.fromisoformat(rep["coverage_start"])
    offset_days=(when-start).total_seconds()/86400.0
    local_days=offset_days-segment*width
    x=-1.0+2.0*local_days/width
    b=_basis(x,coeff_count); db=_derivative_basis(x,coeff_count,width)
    longitude=sum(c*v for c,v in zip(coeff,b))%360.0
    speed=sum(c*v for c,v in zip(coeff,db))
    return {
        "object_id":object_id,
        "longitude_deg":longitude,
        "speed_deg_per_day":speed,
        "motion":_motion(speed),
        **_sign_fields(longitude),
        "segment_index":segment,
        "shard_index":int(shard["shard_index"]),
        "dataset_id":DATASET_ID,
        "dataset_sha256":DATASET_SHA256,
        "representation_id":REPRESENTATION_ID,
    }

def build_extended_object_rows(
    object_ids: list[str],
    utc: str | dt.datetime,
    *,
    house_facts: list[dict[str,Any]] | None = None,
    data_root: Path | None = None,
) -> tuple[list[dict[str,Any]],dict[str,Any]]:
    if not object_ids:
        raise ExtendedEphemerisError("at least one extended object is required")
    if len(set(object_ids))!=len(object_ids):
        raise ExtendedEphemerisError("extended object ids must be unique")
    unknown=[x for x in object_ids if x not in OBJECT_IDS]
    if unknown:
        raise ExtendedEphemerisError(f"unsupported extended object(s): {unknown}")
    rows=[]
    for object_id in object_ids:
        fact=evaluate_object(object_id,utc,data_root=data_root)
        row={
            "fact_id":f"fact:object:{object_id.lower()}",
            "object_type":"minor_planet",
            **fact,
        }
        if house_facts is not None:
            row["house_number"]=_house_of(float(row["longitude_deg"]),house_facts)
        rows.append(row)
    _,manifest=load_manifest(data_root)
    provider={
        "provider_id":PROVIDER_ID,
        "provider_version":PROVIDER_VERSION,
        "dataset_id":DATASET_ID,
        "dataset_sha256":DATASET_SHA256,
        "representation_id":REPRESENTATION_ID,
        "requested_object_ids":list(object_ids),
        "source_provider":manifest["source"]["provider"],
        "source_signature":manifest["source"]["observed_signature"],
        "ordinary_runtime_network_required":False,
        "semantic_interpretation_authority":False,
        "default_aspect_participation":False,
    }
    return rows,provider
