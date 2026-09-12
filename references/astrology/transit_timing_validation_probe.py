#!/usr/bin/env python3
"""
REFERENCE-ONLY Astrology transit/station validation probe.

Research-only. Produces deterministic geometry evidence from pyswisseph and
compares a small lunar-phase benchmark slice against pinned Astronomy Engine
test data. It does not own production astrology calculation or interpretation.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from statistics import mean, median

import swisseph as swe

UTC = timezone.utc
FLAGS = swe.FLG_SWIEPH | swe.FLG_SPEED

BODIES = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
    "Uranus": swe.URANUS,
    "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO,
}

# A bounded slice of cosinekitty/astronomy@865d3da...:
# generate/moonphase/moonphases.txt
# quarter code -> target Moon-Sun longitude = quarter * 90 degrees.
LUNAR_BENCHMARK = (
    (1, "2020-01-03T04:45:00Z"),
    (2, "2020-01-10T19:21:00Z"),
    (3, "2020-01-17T12:58:00Z"),
    (0, "2020-01-24T21:42:00Z"),
    (1, "2020-02-02T01:42:00Z"),
    (2, "2020-02-09T07:33:00Z"),
    (3, "2020-02-15T22:17:00Z"),
    (0, "2020-02-23T15:32:00Z"),
    (1, "2020-03-02T19:57:00Z"),
    (2, "2020-03-09T17:48:00Z"),
    (3, "2020-03-16T09:34:00Z"),
    (0, "2020-03-24T09:28:00Z"),
)


def parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def julian_day(when: datetime) -> float:
    when = when.astimezone(UTC)
    hour = (
        when.hour
        + when.minute / 60.0
        + when.second / 3600.0
        + when.microsecond / 3_600_000_000.0
    )
    return swe.julday(when.year, when.month, when.day, hour)


def position(body: str, when: datetime):
    values, returned_flags = swe.calc_ut(julian_day(when), BODIES[body], FLAGS)
    return {
        "longitude": values[0] % 360.0,
        "speed": values[3],
        "returned_flags": returned_flags,
    }


def signed_angle(value: float) -> float:
    return ((value + 180.0) % 360.0) - 180.0


def phase(body1: str, body2: str, when: datetime):
    first = position(body1, when)
    second = position(body2, when)
    return {
        "phase": (first["longitude"] - second["longitude"]) % 360.0,
        "relative_speed": first["speed"] - second["speed"],
        "body1": first,
        "body2": second,
    }


def phase_error(body1: str, body2: str, target: float, when: datetime) -> float:
    return signed_angle(phase(body1, body2, when)["phase"] - target)


def bisect_time(func, left: datetime, right: datetime, tolerance_seconds: float = 0.001):
    f_left = func(left)
    f_right = func(right)
    if f_left == 0:
        return left
    if f_right == 0:
        return right
    if f_left * f_right > 0:
        raise ValueError("root is not bracketed")
    for _ in range(120):
        middle = left + (right - left) / 2
        f_middle = func(middle)
        if abs(f_middle) < 1e-12 or (right - left).total_seconds() <= tolerance_seconds:
            return middle
        if f_left * f_middle <= 0:
            right = middle
            f_right = f_middle
        else:
            left = middle
            f_left = f_middle
    return left + (right - left) / 2


def find_phase_root_near(body1: str, body2: str, target: float, expected: datetime, search_hours: float = 18.0):
    start = expected - timedelta(hours=search_hours)
    end = expected + timedelta(hours=search_hours)
    step = timedelta(minutes=10)
    brackets = []
    current = start
    current_error = phase_error(body1, body2, target, current)
    while current < end:
        nxt = min(current + step, end)
        next_error = phase_error(body1, body2, target, nxt)
        if (
            current_error == 0
            or next_error == 0
            or (current_error * next_error < 0 and abs(current_error - next_error) < 180)
        ):
            brackets.append((current, nxt))
        current = nxt
        current_error = next_error
    if not brackets:
        raise RuntimeError("no target crossing found")
    left, right = min(
        brackets,
        key=lambda pair: abs((pair[0] + (pair[1] - pair[0]) / 2 - expected).total_seconds()),
    )
    return bisect_time(lambda when: phase_error(body1, body2, target, when), left, right)


def lunar_benchmark():
    records = []
    for quarter, expected_text in LUNAR_BENCHMARK:
        expected = parse_utc(expected_text)
        target = quarter * 90.0
        exact = find_phase_root_near("Moon", "Sun", target, expected)
        state = phase("Moon", "Sun", exact)
        records.append(
            {
                "quarter": quarter,
                "target_degrees": target,
                "benchmark_utc": expected.isoformat(),
                "calculated_utc": exact.isoformat(),
                "delta_seconds": (exact - expected).total_seconds(),
                "angular_residual_degrees": phase_error("Moon", "Sun", target, exact),
                "effective_flags": state["body1"]["returned_flags"],
            }
        )
    abs_deltas = [abs(item["delta_seconds"]) for item in records]
    return {
        "records": records,
        "summary": {
            "count": len(records),
            "max_abs_delta_seconds": max(abs_deltas),
            "mean_abs_delta_seconds": mean(abs_deltas),
            "median_abs_delta_seconds": median(abs_deltas),
        },
    }


def find_exact_aspect(body1: str, body2: str, target: float, start: datetime, end: datetime, step_minutes: int = 30):
    step = timedelta(minutes=step_minutes)
    current = start
    current_error = phase_error(body1, body2, target, current)
    while current < end:
        nxt = min(current + step, end)
        next_error = phase_error(body1, body2, target, nxt)
        if (
            current_error == 0
            or next_error == 0
            or (current_error * next_error < 0 and abs(current_error - next_error) < 180)
        ):
            exact = bisect_time(lambda when: phase_error(body1, body2, target, when), current, nxt)
            state = phase(body1, body2, exact)
            return {
                "exact_utc": exact.isoformat(),
                "target_degrees": target,
                "phase_degrees": state["phase"],
                "angular_residual_degrees": phase_error(body1, body2, target, exact),
                "relative_speed_deg_per_day": state["relative_speed"],
                "effective_flags": state["body1"]["returned_flags"],
            }
        current = nxt
        current_error = next_error
    raise RuntimeError("aspect not found in interval")


def geometry_window(body1: str, body2: str, target: float, exact: datetime, orb_degrees: float, bracket_hours: float = 12.0):
    entry = bisect_time(
        lambda when: phase_error(body1, body2, target, when) - orb_degrees,
        exact - timedelta(hours=bracket_hours),
        exact,
    )
    exit_ = bisect_time(
        lambda when: phase_error(body1, body2, target, when) + orb_degrees,
        exact,
        exact + timedelta(hours=bracket_hours),
    )
    samples = {}
    for offset_hours in (-6, -1, 1, 6):
        when = exact + timedelta(hours=offset_hours)
        error = phase_error(body1, body2, target, when)
        samples[str(offset_hours)] = {
            "utc": when.isoformat(),
            "signed_error_degrees": error,
            "distance_degrees": abs(error),
            "state": "applying" if offset_hours < 0 else "separating",
        }
    return {
        "test_orb_degrees": orb_degrees,
        "entry_utc": entry.isoformat(),
        "exact_utc": exact.isoformat(),
        "exit_utc": exit_.isoformat(),
        "entry_to_exact_seconds": (exact - entry).total_seconds(),
        "exact_to_exit_seconds": (exit_ - exact).total_seconds(),
        "total_window_seconds": (exit_ - entry).total_seconds(),
        "samples": samples,
    }


def find_stations(body: str, start: datetime, end: datetime, step_hours: int = 6):
    step = timedelta(hours=step_hours)
    results = []
    current = start
    current_speed = position(body, current)["speed"]
    while current < end:
        nxt = min(current + step, end)
        next_speed = position(body, nxt)["speed"]
        if current_speed == 0 or next_speed == 0 or current_speed * next_speed < 0:
            exact = bisect_time(lambda when: position(body, when)["speed"], current, nxt)
            state = position(body, exact)
            before = position(body, exact - timedelta(hours=12))["speed"]
            after = position(body, exact + timedelta(hours=12))["speed"]
            if before > 0 and after < 0:
                transition = "direct_to_retrograde"
            elif before < 0 and after > 0:
                transition = "retrograde_to_direct"
            else:
                transition = "unresolved"
            if not results or abs((exact - parse_utc(results[-1]["exact_utc"])).total_seconds()) > 3600:
                results.append(
                    {
                        "exact_utc": exact.isoformat(),
                        "transition": transition,
                        "speed_at_root_deg_per_day": state["speed"],
                        "speed_12h_before": before,
                        "speed_12h_after": after,
                        "effective_flags": state["returned_flags"],
                    }
                )
        current = nxt
        current_speed = next_speed
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    trine = find_exact_aspect(
        "Sun",
        "Moon",
        120.0,
        datetime(2026, 7, 5, tzinfo=UTC),
        datetime(2026, 7, 6, tzinfo=UTC),
    )
    trine_time = parse_utc(trine["exact_utc"])
    output = {
        "runtime": {
            "pyswisseph_version": swe.version,
            "requested_flags": FLAGS,
            "note": "Inspect effective_flags; requested SWIEPH may fall back to MOSEPH.",
        },
        "lunar_phase_benchmark": lunar_benchmark(),
        "sun_moon_trine_2026_07_05": {
            "event": trine,
            "geometry_window_1deg_test_parameter": geometry_window(
                "Sun", "Moon", 120.0, trine_time, 1.0
            ),
        },
        "stations_2026": {
            "Mercury": find_stations(
                "Mercury",
                datetime(2026, 1, 1, tzinfo=UTC),
                datetime(2027, 1, 1, tzinfo=UTC),
            ),
            "Saturn": find_stations(
                "Saturn",
                datetime(2026, 1, 1, tzinfo=UTC),
                datetime(2027, 1, 1, tzinfo=UTC),
            ),
        },
    }
    print(json.dumps(output, indent=2 if args.pretty else None, ensure_ascii=False))


if __name__ == "__main__":
    main()
