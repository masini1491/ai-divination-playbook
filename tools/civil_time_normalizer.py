#!/usr/bin/env python3
"""Shared deterministic civil-time normalization for method-owned consumers.

This module validates a naive local civil wall time against an explicit IANA
timezone. It preserves local calendar identity and resolves the corresponding
UTC instant without applying birthplace lookup, true-solar-time correction, or
method-specific calendar policy.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

NORMALIZER_ID = "civil-time-zoneinfo-v1"
NORMALIZER_VERSION = "1.0.0"
RESOLUTION_UNIQUE = "UNIQUE"


class CivilTimeNormalizationError(ValueError):
    """Civil-time input cannot be deterministically admitted."""


@dataclass(frozen=True)
class CivilTimeResolution:
    source_local_datetime: str
    validated_local_datetime: dt.datetime
    timezone_name: str
    resolved_utc_offset_seconds: int
    resolved_utc_instant: dt.datetime
    fold: int
    resolution_status: str = RESOLUTION_UNIQUE
    normalizer_id: str = NORMALIZER_ID
    normalizer_version: str = NORMALIZER_VERSION

    def provenance(self) -> dict[str, object]:
        return {
            "normalizer_id": self.normalizer_id,
            "normalizer_version": self.normalizer_version,
            "source_local_datetime": self.source_local_datetime,
            "validated_local_iso": self.validated_local_datetime.isoformat(),
            "timezone_name": self.timezone_name,
            "resolved_utc_offset_seconds": self.resolved_utc_offset_seconds,
            "resolved_utc_iso": self.resolved_utc_instant.isoformat(),
            "fold": self.fold,
            "resolution_status": self.resolution_status,
            "timezone_rule_source": "python-zoneinfo",
        }


def _parse_local_datetime(value: str) -> dt.datetime:
    try:
        parsed = dt.datetime.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise CivilTimeNormalizationError(
            "local_datetime must be ISO-8601 local wall time"
        ) from exc
    if parsed.tzinfo is not None:
        raise CivilTimeNormalizationError(
            "local_datetime must be naive; timezone_name owns timezone resolution"
        )
    return parsed


def normalize_civil_time(local_datetime: str, timezone_name: str) -> CivilTimeResolution:
    local = _parse_local_datetime(local_datetime)
    if not isinstance(timezone_name, str) or not timezone_name:
        raise CivilTimeNormalizationError(
            "timezone_name must be an explicit IANA timezone"
        )
    try:
        zone = ZoneInfo(timezone_name)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise CivilTimeNormalizationError(
            f"unknown IANA timezone: {timezone_name}"
        ) from exc

    candidates: list[dt.datetime] = []
    for fold in (0, 1):
        aware = local.replace(tzinfo=zone, fold=fold)
        utc = aware.astimezone(dt.timezone.utc)
        roundtrip = utc.astimezone(zone).replace(tzinfo=None)
        if roundtrip == local:
            candidates.append(utc)

    if not candidates:
        raise CivilTimeNormalizationError(
            "local_datetime is nonexistent in timezone due to DST transition"
        )

    utc_values = set(candidates)
    if len(utc_values) > 1:
        raise CivilTimeNormalizationError(
            "local_datetime is ambiguous in timezone due to DST transition"
        )

    utc = candidates[0]
    validated_local = utc.astimezone(zone)
    offset = validated_local.utcoffset()
    if offset is None:
        raise CivilTimeNormalizationError(
            "timezone resolution produced no UTC offset"
        )

    return CivilTimeResolution(
        source_local_datetime=local_datetime,
        validated_local_datetime=validated_local,
        timezone_name=timezone_name,
        resolved_utc_offset_seconds=int(offset.total_seconds()),
        resolved_utc_instant=utc,
        fold=validated_local.fold,
    )
