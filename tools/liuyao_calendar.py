#!/usr/bin/env python3
"""Zero-dependency calendar facts needed by the Liuyao structural engine.

The provider accepts an offset-aware Gregorian timestamp and returns only the
calendar facts used by this Playbook: solar-term month branch, sexagenary day,
xunkong, and the day stem needed to start six spirits. It does not interpret a
reading.

Solar-term boundaries are solved from apparent solar longitude with a compact
Meeus-style solar model. The implementation is intentionally scoped to modern
runtime readings (1901-2099); outside that range it fails closed.
"""
from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timedelta, timezone
from typing import Any

PROVIDER_NAME = "ai-divination-playbook/lightweight-liuyao-calendar"
PROVIDER_VERSION = "1"
GAN = "甲乙丙丁戊己庚辛壬癸"
ZHI = "子丑寅卯辰巳午未申酉戌亥"
JIAZI = tuple(GAN[i % 10] + ZHI[i % 12] for i in range(60))

# The twelve Jie boundaries that start Liuyao solar months. Li Chun starts 寅.
JIE = (
    (315.0, "立春", "寅"), (345.0, "驚蟄", "卯"),
    (15.0, "清明", "辰"), (45.0, "立夏", "巳"),
    (75.0, "芒種", "午"), (105.0, "小暑", "未"),
    (135.0, "立秋", "申"), (165.0, "白露", "酉"),
    (195.0, "寒露", "戌"), (225.0, "立冬", "亥"),
    (255.0, "大雪", "子"), (285.0, "小寒", "丑"),
)
APPROX_MONTH_DAY = {
    "立春": (2, 4), "驚蟄": (3, 6), "清明": (4, 5), "立夏": (5, 6),
    "芒種": (6, 6), "小暑": (7, 7), "立秋": (8, 8), "白露": (9, 8),
    "寒露": (10, 8), "立冬": (11, 7), "大雪": (12, 7), "小寒": (1, 6),
}


def parse_timestamp(value: str) -> datetime:
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError("timestamp must be ISO-8601 with an explicit UTC offset")
    if not 1901 <= dt.year <= 2099:
        raise ValueError("calendar provider supports Gregorian years 1901-2099")
    return dt


def _julian_day(dt: datetime) -> float:
    u = dt.astimezone(timezone.utc)
    y, m = u.year, u.month
    d = u.day + (u.hour + (u.minute + (u.second + u.microsecond / 1_000_000) / 60) / 60) / 24
    if m <= 2:
        y -= 1
        m += 12
    a = y // 100
    b = 2 - a + a // 4
    return math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1)) + d + b - 1524.5


def _solar_longitude(dt: datetime) -> float:
    """Apparent geocentric solar longitude, degrees [0,360)."""
    t = (_julian_day(dt) - 2451545.0) / 36525.0
    l0 = (280.46646 + t * (36000.76983 + 0.0003032 * t)) % 360
    m = math.radians((357.52911 + t * (35999.05029 - 0.0001537 * t)) % 360)
    c = ((1.914602 - t * (0.004817 + 0.000014 * t)) * math.sin(m)
         + (0.019993 - 0.000101 * t) * math.sin(2 * m)
         + 0.000289 * math.sin(3 * m))
    omega = math.radians(125.04 - 1934.136 * t)
    return (l0 + c - 0.00569 - 0.00478 * math.sin(omega)) % 360


def _angle_diff(actual: float, target: float) -> float:
    return (actual - target + 180.0) % 360.0 - 180.0


def _jie_time(year: int, target: float, name: str) -> datetime:
    month, day = APPROX_MONTH_DAY[name]
    term_year = year
    guess = datetime(term_year, month, day, 8, tzinfo=timezone.utc)
    lo, hi = guess - timedelta(days=3), guess + timedelta(days=3)
    for _ in range(70):
        mid = lo + (hi - lo) / 2
        if _angle_diff(_solar_longitude(mid), target) < 0:
            lo = mid
        else:
            hi = mid
    return lo + (hi - lo) / 2


def _jie_boundaries(dt: datetime) -> list[tuple[datetime, str, str]]:
    tz = dt.tzinfo
    out: list[tuple[datetime, str, str]] = []
    for y in (dt.year - 1, dt.year, dt.year + 1):
        for target, name, branch in JIE:
            out.append((_jie_time(y, target, name).astimezone(tz), name, branch))
    return sorted(out)


def solar_month(dt: datetime) -> tuple[str, str, datetime]:
    previous = None
    for boundary in _jie_boundaries(dt):
        if boundary[0] <= dt:
            previous = boundary
        else:
            break
    if previous is None:
        raise ValueError("unable to resolve solar month boundary")
    when, name, branch = previous
    return branch, name, when


def _gregorian_jdn(year: int, month: int, day: int) -> int:
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    return day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045


def sexagenary_day(dt: datetime, *, zi_hour_changes_day: bool = True) -> tuple[int, str]:
    local = dt
    date = local.date()
    if zi_hour_changes_day and local.hour == 23:
        date += timedelta(days=1)
    index = (_gregorian_jdn(date.year, date.month, date.day) + 49) % 60
    return index, JIAZI[index]


def xunkong(day_index: int) -> tuple[str, str]:
    # In each 10-day xun, two Earthly Branches are not paired with a stem.
    start_branch = (day_index // 10 * 10) % 12
    return ZHI[(start_branch + 10) % 12], ZHI[(start_branch + 11) % 12]


def calendar_facts(timestamp: str | datetime, *, zi_hour_changes_day: bool = True) -> dict[str, Any]:
    dt = parse_timestamp(timestamp) if isinstance(timestamp, str) else timestamp
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError("timestamp must carry an explicit UTC offset")
    if not 1901 <= dt.year <= 2099:
        raise ValueError("calendar provider supports Gregorian years 1901-2099")
    month_branch, boundary_name, boundary_time = solar_month(dt)
    day_index, day_ganzhi = sexagenary_day(dt, zi_hour_changes_day=zi_hour_changes_day)
    kong = xunkong(day_index)
    return {
        "provider": PROVIDER_NAME,
        "provider_version": PROVIDER_VERSION,
        "timestamp": dt.isoformat(),
        "timezone_offset": dt.strftime("%z"),
        "month_branch": month_branch,
        "month_boundary": boundary_name,
        "month_boundary_time": boundary_time.isoformat(),
        "day_ganzhi": day_ganzhi,
        "day_gan": day_ganzhi[0],
        "day_branch": day_ganzhi[1],
        "xunkong": list(kong),
        "zi_hour_changes_day": zi_hour_changes_day,
        "interpretation_authority": False,
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Liuyao calendar fact provider")
    p.add_argument("--timestamp", required=True, help="offset-aware ISO-8601 timestamp")
    p.add_argument("--midnight-day-change", action="store_true",
                   help="use civil-midnight day change instead of 23:00 Zi-hour convention")
    args = p.parse_args()
    try:
        fact = calendar_facts(args.timestamp, zi_hour_changes_day=not args.midnight_day_change)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    print(json.dumps(fact, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
