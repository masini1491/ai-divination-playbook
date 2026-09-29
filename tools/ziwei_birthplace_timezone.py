#!/usr/bin/env python3
"""Deterministic Taiwan birthplace-to-timezone pre-adapter for Zi Wei.

This module resolves only the IANA timezone identity for clearly recognized
Taiwan administrative-region input. It does not geocode coordinates, infer
longitude, or activate true-solar-time policy.
"""
from __future__ import annotations

from dataclasses import dataclass

from tools.ziwei_calendar_provider import GregorianBirthInput

RESOLVER_ID = "ziwei-birthplace-timezone-tw-v1"
RESOLVER_VERSION = "1.0.0"
TIMEZONE = "Asia/Taipei"

TAIWAN_TOP_LEVEL_REGIONS = (
    "臺北市","新北市","桃園市","臺中市","臺南市","高雄市",
    "基隆市","新竹市","嘉義市",
    "新竹縣","苗栗縣","彰化縣","南投縣","雲林縣","嘉義縣",
    "屏東縣","宜蘭縣","花蓮縣","臺東縣","澎湖縣","金門縣","連江縣",
)

class ZiWeiBirthplaceTimezoneError(ValueError):
    """Birthplace cannot be resolved under the admitted Zi Wei policy."""

@dataclass(frozen=True)
class ResolvedBirthplaceTimezone:
    raw_birthplace: str
    normalized_birthplace: str
    matched_region: str
    timezone: str = TIMEZONE

    def provenance(self) -> dict[str, object]:
        return {
            "resolver_id": RESOLVER_ID,
            "resolver_version": RESOLVER_VERSION,
            "scope": "taiwan_top_level_admin_region_to_iana_timezone_only",
            "raw_birthplace": self.raw_birthplace,
            "normalized_birthplace": self.normalized_birthplace,
            "matched_region": self.matched_region,
            "timezone": self.timezone,
            "coordinates_resolved": False,
            "longitude_resolved": False,
            "true_solar_time_activated": False,
        }

def normalize_taiwan_birthplace(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ZiWeiBirthplaceTimezoneError("birthplace is required")
    return value.strip().replace("台", "臺")

def resolve_birthplace_timezone(birthplace: str) -> ResolvedBirthplaceTimezone:
    normalized = normalize_taiwan_birthplace(birthplace)
    matches = [region for region in TAIWAN_TOP_LEVEL_REGIONS if normalized.startswith(region)]
    if len(matches) != 1:
        raise ZiWeiBirthplaceTimezoneError(
            "unsupported or ambiguous birthplace for Zi Wei timezone resolution; provide explicit IANA timezone"
        )
    return ResolvedBirthplaceTimezone(
        raw_birthplace=birthplace,
        normalized_birthplace=normalized,
        matched_region=matches[0],
    )

def gregorian_birth_from_birthplace(
    *,
    birthplace: str,
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int = 0,
    second: int = 0,
) -> tuple[GregorianBirthInput, dict[str, object]]:
    resolved = resolve_birthplace_timezone(birthplace)
    birth = GregorianBirthInput(
        year=year, month=month, day=day, hour=hour,
        minute=minute, second=second, timezone=resolved.timezone,
    )
    birth.validate()
    return birth, resolved.provenance()
