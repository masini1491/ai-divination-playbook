#!/usr/bin/env python3
"""
REFERENCE-ONLY Astrology transit-to-natal / ingress / timezone-DST probe.

Research-only. Uses pyswisseph plus Python zoneinfo to exercise:
- transit to a fixed natal longitude target;
- repeated exact passages during retrograde;
- zodiac-sign ingress/re-entry roots;
- IANA timezone local-time classification (unique / ambiguous / nonexistent);
- local-day -> UTC interval resolution.

It does not own production astrology calculation, orb policy, interpretation, or routing.
"""
from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import swisseph as swe

UTC = timezone.utc
FLAGS = swe.FLG_SWIEPH | swe.FLG_SPEED
BODIES = {
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
}


def julian_day(when: datetime) -> float:
    when = when.astimezone(UTC)
    hour = (
        when.hour
        + when.minute / 60.0
        + when.second / 3600.0
        + when.microsecond / 3_600_000_000.0
    )
    return swe.julday(when.year, when.month, when.day, hour)


def position(body: str, when: datetime) -> dict:
    values, returned_flags = swe.calc_ut(julian_day(when), BODIES[body], FLAGS)
    return {
        "longitude": values[0] % 360.0,
        "speed": values[3],
        "returned_flags": returned_flags,
    }


def signed_angle(value: float) -> float:
    return ((value + 180.0) % 360.0) - 180.0


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


def find_longitude_crossings(
    body: str,
    target_longitude: float,
    start: datetime,
    end: datetime,
    step_hours: int = 3,
):
    """Find ordinary crossings of a fixed tropical longitude branch.

    This bounded probe detects sign-changing roots after shortest-angle normalization.
    Tangential roots at an exact station require a separate station-aware search.
    """
    step = timedelta(hours=step_hours)
    results = []
    current = start
    current_error = signed_angle(position(body, current)["longitude"] - target_longitude)

    while current < end:
        nxt = min(current + step, end)
        next_error = signed_angle(position(body, nxt)["longitude"] - target_longitude)

        if (
            current_error == 0
            or next_error == 0
            or (current_error * next_error < 0 and abs(current_error - next_error) < 180)
        ):
            exact = bisect_time(
                lambda when: signed_angle(
                    position(body, when)["longitude"] - target_longitude
                ),
                current,
                nxt,
            )
            if not results or abs((exact - results[-1]).total_seconds()) > 60:
                results.append(exact)

        current = nxt
        current_error = next_error

    return results


def passage_record(body: str, target_longitude: float, exact: datetime) -> dict:
    state = position(body, exact)
    if state["speed"] > 0:
        direction = "direct"
    elif state["speed"] < 0:
        direction = "retrograde"
    else:
        direction = "station"

    return {
        "exact_utc": exact.isoformat(),
        "target_longitude": target_longitude,
        "body_longitude": state["longitude"],
        "angular_residual_degrees": signed_angle(
            state["longitude"] - target_longitude
        ),
        "speed_deg_per_day": state["speed"],
        "direction": direction,
        "effective_flags": state["returned_flags"],
    }


def nearest_crossing(
    body: str,
    target_longitude: float,
    expected: datetime,
    search_days: float = 3.0,
) -> datetime:
    roots = find_longitude_crossings(
        body,
        target_longitude,
        expected - timedelta(days=search_days),
        expected + timedelta(days=search_days),
    )
    if not roots:
        raise RuntimeError("no nearby crossing found")
    return min(roots, key=lambda item: abs((item - expected).total_seconds()))


def fixed_target_uncertainty_sensitivity(
    body: str,
    center_target: float,
    center_passages: list[datetime],
    half_width_degrees: float,
) -> list[dict]:
    results = []
    low_target = center_target - half_width_degrees
    high_target = center_target + half_width_degrees
    for center in center_passages:
        low_time = nearest_crossing(body, low_target, center)
        high_time = nearest_crossing(body, high_target, center)
        earlier = min(low_time, high_time)
        later = max(low_time, high_time)
        results.append(
            {
                "center_exact_utc": center.isoformat(),
                "target_interval_degrees": [low_target, high_target],
                "low_target_exact_utc": low_time.isoformat(),
                "high_target_exact_utc": high_time.isoformat(),
                "earliest_possible_utc": earlier.isoformat(),
                "latest_possible_utc": later.isoformat(),
                "total_timing_span_hours": (later - earlier).total_seconds() / 3600.0,
            }
        )
    return results


def transit_to_fixed_natal_target() -> dict:
    # Synthetic source-neutral target. No person's birth data is stored.
    target = 110.0
    start = datetime(2026, 6, 1, tzinfo=UTC)
    end = datetime(2026, 8, 10, tzinfo=UTC)
    roots = find_longitude_crossings("Mercury", target, start, end)
    return {
        "synthetic_natal_target": {
            "target_type": "natal_planet_longitude_fixture",
            "longitude_degrees": target,
            "note": "Synthetic fixed point; not tied to any identifiable person.",
        },
        "moving_body": "Mercury",
        "aspect": "Conjunction",
        "passages": [passage_record("Mercury", target, root) for root in roots],
        "target_uncertainty_test": {
            "half_width_degrees": 0.5,
            "note": "Test parameter only; illustrates propagation of natal-target uncertainty into event-time uncertainty.",
            "passages": fixed_target_uncertainty_sensitivity(
                "Mercury", target, roots, 0.5
            ),
        },
    }


def venus_scorpio_ingress_reentries() -> dict:
    # 210° tropical longitude = Scorpio 0°.
    target = 210.0
    start = datetime(2026, 8, 1, tzinfo=UTC)
    end = datetime(2026, 12, 20, tzinfo=UTC)
    roots = find_longitude_crossings("Venus", target, start, end)
    records = []
    for index, root in enumerate(roots):
        rec = passage_record("Venus", target, root)
        if rec["direction"] == "direct":
            rec["from_sign"] = "Libra"
            rec["to_sign"] = "Scorpio"
            rec["event_kind"] = "direct_ingress" if index == 0 else "direct_reingress"
        else:
            rec["from_sign"] = "Scorpio"
            rec["to_sign"] = "Libra"
            rec["event_kind"] = "retrograde_return_to_previous_sign"
        records.append(rec)
    return {
        "body": "Venus",
        "boundary": {
            "tropical_longitude_degrees": target,
            "sign_pair": ["Libra", "Scorpio"],
        },
        "crossings": records,
    }


def classify_local_time(local_naive: datetime, zone_name: str) -> dict:
    """Classify a naive wall time under an IANA timezone using round-trip validity."""
    if local_naive.tzinfo is not None:
        raise ValueError("local_naive must not include tzinfo")
    zone = ZoneInfo(zone_name)
    candidates = []
    for fold in (0, 1):
        aware = local_naive.replace(tzinfo=zone, fold=fold)
        utc = aware.astimezone(UTC)
        roundtrip = utc.astimezone(zone)
        valid = roundtrip.replace(tzinfo=None) == local_naive
        candidates.append(
            {
                "fold": fold,
                "offset_seconds": int(aware.utcoffset().total_seconds()),
                "utc": utc.isoformat(),
                "roundtrip_local": roundtrip.isoformat(),
                "valid": valid,
            }
        )

    valid_candidates = []
    seen_utc = set()
    for item in candidates:
        if item["valid"] and item["utc"] not in seen_utc:
            seen_utc.add(item["utc"])
            valid_candidates.append(item)

    if not valid_candidates:
        status = "nonexistent"
    elif len(valid_candidates) == 1:
        status = "unique"
    else:
        status = "ambiguous"

    return {
        "zone": zone_name,
        "local_wall_time": local_naive.isoformat(),
        "status": status,
        "valid_candidates": valid_candidates,
        "all_fold_probes": candidates,
    }


def local_day_utc_window(local_date: date, zone_name: str) -> dict:
    zone = ZoneInfo(zone_name)
    start_local = datetime(
        local_date.year, local_date.month, local_date.day, tzinfo=zone
    )
    next_date = local_date + timedelta(days=1)
    end_local = datetime(next_date.year, next_date.month, next_date.day, tzinfo=zone)
    start_utc = start_local.astimezone(UTC)
    end_utc = end_local.astimezone(UTC)
    return {
        "zone": zone_name,
        "local_date": local_date.isoformat(),
        "start_local": start_local.isoformat(),
        "end_local_exclusive": end_local.isoformat(),
        "start_utc": start_utc.isoformat(),
        "end_utc_exclusive": end_utc.isoformat(),
        "duration_hours": (end_utc - start_utc).total_seconds() / 3600.0,
    }


def timezone_probe() -> dict:
    summer_wall = datetime(2026, 7, 1, 12, 0)
    stockholm = classify_local_time(summer_wall, "Europe/Stockholm")
    fixed_plus_one_utc = summer_wall.replace(
        tzinfo=timezone(timedelta(hours=1))
    ).astimezone(UTC)

    return {
        "local_time_classification": [
            classify_local_time(datetime(2026, 3, 29, 2, 30), "Europe/Stockholm"),
            classify_local_time(datetime(2026, 10, 25, 2, 30), "Europe/Stockholm"),
            stockholm,
            classify_local_time(datetime(2026, 9, 12, 23, 18), "Asia/Taipei"),
        ],
        "local_day_windows": [
            local_day_utc_window(date(2026, 3, 29), "Europe/Stockholm"),
            local_day_utc_window(date(2026, 10, 25), "Europe/Stockholm"),
            local_day_utc_window(date(2026, 7, 14), "Europe/Stockholm"),
            local_day_utc_window(date(2026, 7, 14), "Asia/Taipei"),
        ],
        "iana_vs_fixed_offset_example": {
            "local_wall_time": summer_wall.isoformat(),
            "iana_zone": "Europe/Stockholm",
            "iana_resolved_utc": stockholm["valid_candidates"][0]["utc"],
            "iana_offset_seconds": stockholm["valid_candidates"][0]["offset_seconds"],
            "fixed_offset": "+01:00",
            "fixed_offset_resolved_utc": fixed_plus_one_utc.isoformat(),
            "note": "A fixed offset does not encode DST rules.",
        },
    }


def render_event_local_times(event_utc: datetime) -> dict:
    return {
        zone_name: event_utc.astimezone(ZoneInfo(zone_name)).isoformat()
        for zone_name in ("Asia/Taipei", "Europe/Stockholm")
    } | {"UTC": event_utc.astimezone(UTC).isoformat()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    transit = transit_to_fixed_natal_target()
    for item in transit["passages"]:
        exact = datetime.fromisoformat(item["exact_utc"])
        item["rendered_local_times"] = render_event_local_times(exact)

    output = {
        "runtime": {
            "pyswisseph_version": swe.version,
            "requested_flags": FLAGS,
            "note": "Inspect effective_flags; requested SWIEPH may fall back to MOSEPH.",
        },
        "transit_to_fixed_natal_target": transit,
        "venus_scorpio_ingress_reentries": venus_scorpio_ingress_reentries(),
        "timezone_dst": timezone_probe(),
    }
    print(json.dumps(output, indent=2 if args.pretty else None, ensure_ascii=False))


if __name__ == "__main__":
    main()
