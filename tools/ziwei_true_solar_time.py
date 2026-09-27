#!/usr/bin/env python3
"""Zi Wei-owned optional true-solar-time normalization.

Civil-time validation remains owned by tools/civil_time_normalizer.py.  This
module consumes one already-validated civil-time resolution plus an explicit
longitude and derives local apparent solar time using the project-admitted
NOAA fractional-year equation-of-time approximation.

It does not resolve birthplace, timezone, latitude, elevation, lunar date, or
Zi Wei-specific Rat-hour / leap-month policy.
"""
from __future__ import annotations

import calendar
import datetime as dt
import math
from dataclasses import dataclass

from tools.civil_time_normalizer import CivilTimeResolution

PROFILE_ID = "ziwei.true_solar.noaa_fractional_year_v1"
PROFILE_VERSION = "1.0.0"
ALGORITHM_ID = "noaa-fractional-year-equation-of-time"
LONGITUDE_CONVENTION = "east_positive_degrees"


class TrueSolarTimeError(ValueError):
    """True-solar-time input cannot be deterministically admitted."""


def _validate_longitude(value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TrueSolarTimeError("longitude_deg must be a finite number")
    longitude = float(value)
    if not math.isfinite(longitude):
        raise TrueSolarTimeError("longitude_deg must be a finite number")
    if not -180.0 <= longitude <= 180.0:
        raise TrueSolarTimeError("longitude_deg must be in -180..180")
    return longitude


def _round_seconds(value: float) -> int:
    """Deterministic nearest-second rounding, half away from zero."""
    return math.floor(value + 0.5) if value >= 0 else math.ceil(value - 0.5)


def equation_of_time_minutes(local_datetime: dt.datetime) -> float:
    """Return NOAA fractional-year equation of time in minutes."""
    if not isinstance(local_datetime, dt.datetime):
        raise TrueSolarTimeError("local_datetime must be datetime")
    local = local_datetime.replace(tzinfo=None)
    days = 366 if calendar.isleap(local.year) else 365
    day_of_year = local.timetuple().tm_yday
    fractional_hour = (
        local.hour + local.minute / 60.0 + local.second / 3600.0
        + local.microsecond / 3_600_000_000.0
    )
    gamma = 2.0 * math.pi / days * (
        day_of_year - 1 + (fractional_hour - 12.0) / 24.0
    )
    return 229.18 * (
        0.000075
        + 0.001868 * math.cos(gamma)
        - 0.032077 * math.sin(gamma)
        - 0.014615 * math.cos(2.0 * gamma)
        - 0.040849 * math.sin(2.0 * gamma)
    )


@dataclass(frozen=True)
class TrueSolarTimeResolution:
    source_civil_local_datetime: dt.datetime
    apparent_solar_datetime: dt.datetime
    timezone_name: str
    longitude_deg: float
    utc_offset_seconds: int
    equation_of_time_minutes: float
    longitude_correction_minutes: float
    total_correction_seconds: int
    profile_id: str = PROFILE_ID
    profile_version: str = PROFILE_VERSION
    algorithm_id: str = ALGORITHM_ID

    def provenance(self) -> dict[str, object]:
        return {
            "profile_id": self.profile_id,
            "profile_version": self.profile_version,
            "algorithm_id": self.algorithm_id,
            "longitude_convention": LONGITUDE_CONVENTION,
            "timezone_name": self.timezone_name,
            "longitude_deg": self.longitude_deg,
            "resolved_utc_offset_seconds": self.utc_offset_seconds,
            "source_civil_local_iso": self.source_civil_local_datetime.isoformat(),
            "apparent_solar_local_iso": self.apparent_solar_datetime.isoformat(),
            "equation_of_time_minutes": self.equation_of_time_minutes,
            "longitude_correction_minutes": self.longitude_correction_minutes,
            "total_correction_seconds": self.total_correction_seconds,
            "latitude_required": False,
            "birthplace_resolution_performed": False,
        }


def normalize_true_solar_time(
    civil: CivilTimeResolution,
    longitude_deg: float,
    *,
    profile_id: str = PROFILE_ID,
) -> TrueSolarTimeResolution:
    """Apply the explicit Zi Wei true-solar-time profile to validated civil time."""
    if not isinstance(civil, CivilTimeResolution):
        raise TrueSolarTimeError(
            "civil must be a validated CivilTimeResolution"
        )
    if profile_id != PROFILE_ID:
        raise TrueSolarTimeError(
            f"unsupported true_solar_time_profile: {profile_id}"
        )
    longitude = _validate_longitude(longitude_deg)
    source_local = civil.validated_local_datetime.replace(tzinfo=None)
    offset_hours = civil.resolved_utc_offset_seconds / 3600.0
    eq_minutes = equation_of_time_minutes(source_local)
    longitude_minutes = 4.0 * longitude - 60.0 * offset_hours
    total_seconds = _round_seconds((eq_minutes + longitude_minutes) * 60.0)
    apparent = source_local + dt.timedelta(seconds=total_seconds)
    return TrueSolarTimeResolution(
        source_civil_local_datetime=source_local,
        apparent_solar_datetime=apparent,
        timezone_name=civil.timezone_name,
        longitude_deg=longitude,
        utc_offset_seconds=civil.resolved_utc_offset_seconds,
        equation_of_time_minutes=eq_minutes,
        longitude_correction_minutes=longitude_minutes,
        total_correction_seconds=total_seconds,
    )
