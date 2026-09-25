#!/usr/bin/env python3
"""Deterministic Taiwan Minguo-year notation adapter for Zi Wei Gregorian input.

This module converts only the year notation. It does not perform lunar
conversion, timezone conversion, or Zi Wei policy normalization.
"""
from __future__ import annotations

from dataclasses import dataclass

from tools.ziwei_calendar_provider import GregorianBirthInput, TIMEZONE

MINGUO_EPOCH_OFFSET = 1911
NOTATION_ID = "minguo_year_notation_v1"

def minguo_year_to_gregorian(year: int) -> int:
    """Convert 民國 year to Gregorian year. 民國1年 == 1912."""
    if not isinstance(year, int) or isinstance(year, bool):
        raise ValueError("Minguo year must be an integer")
    if year < 1:
        raise ValueError("Minguo year must be >= 1; pre-Republic years are unsupported")
    return year + MINGUO_EPOCH_OFFSET

@dataclass(frozen=True)
class MinguoBirthInput:
    year: int
    month: int
    day: int
    hour: int
    minute: int = 0
    second: int = 0
    timezone: str = TIMEZONE

    def to_gregorian(self) -> GregorianBirthInput:
        return GregorianBirthInput(
            year=minguo_year_to_gregorian(self.year),
            month=self.month,
            day=self.day,
            hour=self.hour,
            minute=self.minute,
            second=self.second,
            timezone=self.timezone,
        )

def convert_minguo_birth(data: MinguoBirthInput) -> dict[str, object]:
    """Return explicit source/conversion facts plus the typed Gregorian input."""
    gregorian = data.to_gregorian()
    gregorian.validate()
    return {
        "notation_id": NOTATION_ID,
        "source": {
            "calendar": "gregorian",
            "year_notation": "minguo",
            "year": data.year,
            "month": data.month,
            "day": data.day,
            "hour": data.hour,
            "minute": data.minute,
            "second": data.second,
            "timezone": data.timezone,
        },
        "converted": {
            "calendar": "gregorian",
            "year_notation": "ce",
            "year": gregorian.year,
            "month": gregorian.month,
            "day": gregorian.day,
            "hour": gregorian.hour,
            "minute": gregorian.minute,
            "second": gregorian.second,
            "timezone": gregorian.timezone,
        },
        "gregorian_birth": gregorian,
    }
