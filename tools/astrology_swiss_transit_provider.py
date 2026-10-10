#!/usr/bin/env python3
"""ChatGPT host-native PySwissEph transit provider.

This provider reuses the canonical transit search kernel and supplies only the
ephemeris backend. It is admitted only for a bounded modern UTC window and only
when paired with a host-native PySwissEph natal baseline.
"""
from __future__ import annotations

import datetime as dt
import importlib
from typing import Any, Iterable

from tools.astrology_runtime import gate_bundle
from tools.astrology_transit_provider import (
    TransitProviderInputError,
    build_transit_bundle as build_shared_transit_bundle,
)

PROVIDER_ID = "pyswisseph-host-transit-v1"
PROVIDER_VERSION = "1.0.0"
PAIRED_NATAL_PROVIDER_ID = "swiss-host-natal-v1"
RUNTIME_SOURCE = "host_preinstalled_only"
MODERN_RANGE_START = dt.datetime(1950, 1, 1, tzinfo=dt.timezone.utc)
MODERN_RANGE_END = dt.datetime(2050, 1, 1, tzinfo=dt.timezone.utc)
BODY_ATTRIBUTE = {
    "Sun": "SUN",
    "Moon": "MOON",
    "Mercury": "MERCURY",
    "Venus": "VENUS",
    "Mars": "MARS",
    "Jupiter": "JUPITER",
    "Saturn": "SATURN",
    "Uranus": "URANUS",
    "Neptune": "NEPTUNE",
    "Pluto": "PLUTO",
}


class SwissTransitProviderUnavailable(RuntimeError):
    """Host-native PySwissEph transit capability is unavailable or unadmitted."""


class SwissTransitProviderInputError(ValueError):
    """Transit request falls outside the host-native PySwissEph admission."""


def _load_swisseph():
    try:
        return importlib.import_module("swisseph")
    except Exception as exc:
        raise SwissTransitProviderUnavailable(
            "host-preinstalled swisseph runtime unavailable"
        ) from exc


def _parse_utc(value: str) -> dt.datetime:
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise SwissTransitProviderInputError("UTC timestamp must be ISO-8601") from exc
    if parsed.tzinfo is None:
        raise SwissTransitProviderInputError("UTC timestamp must include timezone")
    return parsed.astimezone(dt.timezone.utc)


def _validate_modern_window(start_utc: str, end_utc: str) -> None:
    start = _parse_utc(start_utc)
    end = _parse_utc(end_utc)
    if start < MODERN_RANGE_START or end > MODERN_RANGE_END:
        raise SwissTransitProviderInputError(
            "pyswisseph-host-transit-v1 admits only search windows fully within "
            "1950-01-01T00:00:00Z..2050-01-01T00:00:00Z"
        )


def _backend_name(swe, retflag: int) -> str:
    if retflag & swe.FLG_JPLEPH:
        return "JPLEPH"
    if retflag & swe.FLG_SWIEPH:
        return "SWIEPH"
    if retflag & swe.FLG_MOSEPH:
        return "MOSEPH"
    return f"UNKNOWN({retflag})"


def _backend_summary(backends: set[str]) -> str:
    if backends == {"SWIEPH"}:
        return "SWIEPH_ONLY"
    if backends == {"MOSEPH"}:
        return "MOSEPH_ONLY"
    if backends and backends.issubset({"SWIEPH", "MOSEPH"}):
        return "MIXED_SWIEPH_MOSEPH"
    raise SwissTransitProviderUnavailable(
        "unadmitted effective backend(s): " + ",".join(sorted(backends))
    )


def _julian_day(swe, when: dt.datetime) -> float:
    when = when.astimezone(dt.timezone.utc)
    hour = (
        when.hour
        + when.minute / 60
        + when.second / 3600
        + when.microsecond / 3_600_000_000
    )
    return float(swe.julday(when.year, when.month, when.day, hour))


def build_transit_bundle(
    natal_bundle: dict[str, Any],
    *,
    start_utc: str,
    end_utc: str,
    subject_ref: str,
    moving_bodies: Iterable[str],
    natal_targets: Iterable[str],
    aspects: Iterable[str],
    include_transit_to_natal: bool = True,
    include_stations: bool = True,
    include_ingresses: bool = True,
    include_house_ingresses: bool = False,
    include_house_context: bool = False,
    house_context_utc: str | None = None,
) -> dict[str, Any]:
    _validate_modern_window(start_utc, end_utc)
    natal_provider = natal_bundle.get("provider", {}).get("provider_id")
    if natal_provider != PAIRED_NATAL_PROVIDER_ID:
        raise SwissTransitProviderInputError(
            "pyswisseph-host-transit-v1 requires a swiss-host-natal-v1 baseline "
            "to avoid mixed-backend transit-to-natal geometry"
        )

    swe = _load_swisseph()
    requested_flags = int(swe.FLG_SWIEPH | swe.FLG_SPEED)
    retflags_by_body: dict[str, set[int]] = {}
    backends_by_body: dict[str, set[str]] = {}

    def longitude_and_speed(body: str, when: dt.datetime) -> tuple[float, float]:
        attribute = BODY_ATTRIBUTE.get(body)
        if attribute is None:
            raise SwissTransitProviderInputError(
                f"host-native PySwissEph transit backend does not admit body: {body}"
            )
        values, retflag = swe.calc_ut(
            _julian_day(swe, when),
            getattr(swe, attribute),
            requested_flags,
        )
        retflag = int(retflag)
        backend = _backend_name(swe, retflag)
        if backend not in {"SWIEPH", "MOSEPH"}:
            raise SwissTransitProviderUnavailable(
                f"unadmitted PySwissEph transit effective backend: {backend}"
            )
        retflags_by_body.setdefault(body, set()).add(retflag)
        backends_by_body.setdefault(body, set()).add(backend)
        return float(values[0]) % 360.0, float(values[3])

    metadata = {
        "provider_id": PROVIDER_ID,
        "provider_version": PROVIDER_VERSION,
        "provider_api_family": "PySwissEph",
        "runtime_source": RUNTIME_SOURCE,
        "pyswisseph_version": getattr(swe, "version", None),
        "requested_ephemeris_flags": requested_flags,
        "admitted_search_range_utc": {
            "start_inclusive": "1950-01-01T00:00:00Z",
            "end_inclusive_for_window_end": "2050-01-01T00:00:00Z",
        },
        "event_time_semantics": (
            "provider_model_root_with_0.5s_numerical_tolerance;"
            " modern-range accuracy independently benchmarked against JPL_DE440S"
        ),
        "independent_oracle_evidence": (
            "references/astrology/JPL_DE440S_TRANSIT_ORACLE_ADJUDICATION.md"
        ),
    }

    try:
        bundle = build_shared_transit_bundle(
            natal_bundle,
            start_utc=start_utc,
            end_utc=end_utc,
            subject_ref=subject_ref,
            moving_bodies=moving_bodies,
            natal_targets=natal_targets,
            aspects=aspects,
            include_transit_to_natal=include_transit_to_natal,
            include_stations=include_stations,
            include_ingresses=include_ingresses,
            include_house_ingresses=include_house_ingresses,
            include_house_context=include_house_context,
            house_context_utc=house_context_utc,
            longitude_and_speed=longitude_and_speed,
            provider_metadata=metadata,
        )
    except TransitProviderInputError as exc:
        raise SwissTransitProviderInputError(str(exc)) from exc

    all_backends = {
        backend
        for values in backends_by_body.values()
        for backend in values
    }
    bundle["provider"]["actual_retflags_per_moving_body"] = {
        body: sorted(values) for body, values in sorted(retflags_by_body.items())
    }
    bundle["provider"]["effective_backends_per_moving_body"] = {
        body: sorted(values) for body, values in sorted(backends_by_body.items())
    }
    bundle["provider"]["effective_backend_summary"] = _backend_summary(all_backends)
    bundle["provider"]["natal_source_provider"] = natal_provider

    gate = gate_bundle(bundle)
    if not gate["interpretation_allowed"]:
        raise RuntimeError(
            "host-native PySwissEph transit provider emitted rejected bundle: "
            + str(gate["errors"])
        )
    return bundle
