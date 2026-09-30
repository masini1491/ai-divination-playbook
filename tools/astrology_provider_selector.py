#!/usr/bin/env python3
"""Astrology natal provider preference/fallback selector.

Swiss is used only as a capability already present in the current ChatGPT host.
This repository does not install, declare, vendor, or distribute PySwissEph or
Swiss Ephemeris data. All non-ChatGPT routes use the portable Astronomy Engine
provider.
"""
from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ROUTING_MANIFEST_PATH = ROOT / "ASTROLOGY_PROVIDER_ROUTING_V1.json"
SWISS_ADMISSION_PATH = ROOT / "ASTROLOGY_SWISS_PROVIDER_ADMISSION_V1.json"

CHATGPT_HOST = "chatgpt"
PORTABLE_HOST = "portable"
SWISS_PROVIDER_ID = "swiss-host-natal-v1"
ASTRONOMY_PROVIDER_ID = "astronomy-engine-natal-v1"


class ProviderSelectionError(ValueError):
    pass


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProviderSelectionError(
            f"cannot load provider routing contract {path.name}: {exc}"
        ) from exc
    if not isinstance(value, dict):
        raise ProviderSelectionError(f"{path.name} must contain a JSON object")
    return value


def probe_host_swisseph() -> dict[str, Any]:
    try:
        swe = importlib.import_module("swisseph")
        jd = swe.julday(2000, 1, 1, 12.0)
        values, retflag = swe.calc_ut(
            jd, swe.SUN, swe.FLG_SWIEPH | swe.FLG_SPEED
        )
        cusps, ascmc = swe.houses_ex(jd, 25.0330, 121.5654, b"P")
        if len(values) < 4 or len(cusps) != 12 or len(ascmc) < 2:
            raise RuntimeError("incomplete swisseph natal baseline result")
    except Exception as exc:
        return {"available": False, "error": repr(exc)}
    return {
        "available": True,
        "version": getattr(swe, "version", None),
        "library_path": (
            swe.get_library_path() if hasattr(swe, "get_library_path") else None
        ),
        "sun_retflag": int(retflag),
        "sun_effective_backend": (
            "JPLEPH" if retflag & swe.FLG_JPLEPH
            else "SWIEPH" if retflag & swe.FLG_SWIEPH
            else "MOSEPH" if retflag & swe.FLG_MOSEPH
            else f"UNKNOWN({int(retflag)})"
        ),
        "capability_kind": "PYSWISSEPH_API_EXECUTABLE",
        "sun_longitude_deg": float(values[0]) % 360.0,
        "ascendant_deg": float(ascmc[0]) % 360.0,
        "midheaven_deg": float(ascmc[1]) % 360.0,
    }


def _fallback(reason_codes, *, preferred=None, runtime_probe=None):
    return {
        "selected_provider_id": ASTRONOMY_PROVIDER_ID,
        "preferred_provider_id": preferred,
        "fallback_used": preferred not in (None, ASTRONOMY_PROVIDER_ID),
        "reason_codes": reason_codes,
        "runtime_probe": runtime_probe,
    }


def select_natal_provider(
    *,
    host_family: str,
    reading_mode: str,
    birth_time_certainty: str,
    runtime_probe=None,
    routing_manifest=None,
    swiss_admission=None,
):
    routing = routing_manifest or _load_json(ROUTING_MANIFEST_PATH)
    swiss = swiss_admission or _load_json(SWISS_ADMISSION_PATH)
    host = host_family.strip().lower()
    if host not in {CHATGPT_HOST, PORTABLE_HOST}:
        raise ProviderSelectionError(f"unsupported host_family: {host_family}")
    if reading_mode != "natal":
        return _fallback(["TRANSIT_PORTABLE_ROUTE"])
    if birth_time_certainty not in {"exact", "approximate"}:
        return _fallback(["UNKNOWN_TIME_PORTABLE_ROUTE"])
    if host != CHATGPT_HOST:
        return _fallback(["PORTABLE_HOST_DEFAULT"])

    route = routing.get("routes", {}).get("chatgpt", {}).get(
        "known_time_natal", {}
    )
    preferred = route.get("preferred_provider_id")
    fallback = route.get("fallback_provider_id")
    if preferred != SWISS_PROVIDER_ID or fallback != ASTRONOMY_PROVIDER_ID:
        raise ProviderSelectionError(
            "ChatGPT known-time natal routing manifest is inconsistent"
        )

    reasons = []
    if swiss.get("status") != "PRODUCTION_ADMITTED":
        reasons.append("SWISS_PROVIDER_NOT_ADMITTED")
    boundary = swiss.get("dependency_boundary", {})
    if (
        boundary.get("runtime_source") != "host_preinstalled_only"
        or boundary.get("non_chatgpt_use") != "forbidden"
    ):
        reasons.append("SWISS_HOST_BOUNDARY_INVALID")
    implementation = swiss.get("implementation", {})
    if (
        implementation.get("status") != "PRODUCTION_ADMITTED"
        or implementation.get("runtime_owner") != "tools/astrology_swiss_provider.py"
    ):
        reasons.append("SWISS_IMPLEMENTATION_NOT_ADMITTED")
    if "natal_known_time" not in set(swiss.get("target_scope", [])):
        reasons.append("SWISS_REQUEST_SCOPE_NOT_ADMITTED")

    probe = runtime_probe if runtime_probe is not None else probe_host_swisseph()
    if not probe.get("available"):
        reasons.append("SWISS_RUNTIME_UNAVAILABLE")

    if reasons:
        return _fallback(reasons, preferred=preferred, runtime_probe=probe)

    return {
        "selected_provider_id": SWISS_PROVIDER_ID,
        "preferred_provider_id": SWISS_PROVIDER_ID,
        "fallback_used": False,
        "reason_codes": ["CHATGPT_HOST_SWISS_PREFERRED"],
        "runtime_probe": probe,
        "provider_version": swiss.get("provider_version"),
        "runtime_source": "host_preinstalled_only",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host-family", choices=[CHATGPT_HOST, PORTABLE_HOST], required=True)
    parser.add_argument("--reading-mode", choices=["natal", "transit"], default="natal")
    parser.add_argument("--birth-time-certainty", choices=["exact", "approximate", "unknown"], default="exact")
    args = parser.parse_args()
    print(json.dumps(select_natal_provider(
        host_family=args.host_family,
        reading_mode=args.reading_mode,
        birth_time_certainty=args.birth_time_certainty,
    ), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
