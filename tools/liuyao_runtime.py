#!/usr/bin/env python3
"""Integrated Liuyao structured-fact runtime.

This module joins the zero-dependency calendar provider with the zero-dependency
structural Liuyao engine. Raw stochastic casting remains owned by the separate
Divination Casting Randomizer; this file accepts already-fixed 6/7/8/9 facts.

Authority boundary:
- input raw lines: stochastic fact supplied by caller
- calendar provider: deterministic time facts only
- structural engine: deterministic chart facts only
- no yongshen selection, no auspiciousness judgment, no interpretation
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent


def _load(name: str, filename: str):
    path = HERE / filename
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


calendar = _load("liuyao_calendar", "liuyao_calendar.py")
engine = _load("liuyao_engine", "liuyao_engine.py")

RUNTIME_NAME = "ai-divination-playbook/liuyao-runtime"
RUNTIME_VERSION = "1"


def build_liuyao_fact(raw_lines: str | list[int] | tuple[int, ...], *,
                       timestamp: str,
                       zi_hour_changes_day: bool = True) -> dict[str, Any]:
    """Build one complete deterministic Liuyao Structured Method Fact.

    ``raw_lines`` must already be fixed by the casting authority. This function
    never redraws or mutates them.
    """
    cal = calendar.calendar_facts(
        timestamp,
        zi_hour_changes_day=zi_hour_changes_day,
    )
    structured = engine.build_structured_fact(
        raw_lines,
        day_gan=cal["day_gan"],
        month_branch=cal["month_branch"],
        day_branch=cal["day_branch"],
        xunkong=tuple(cal["xunkong"]),
    )
    structured["calendar_context"].update({
        "timestamp": cal["timestamp"],
        "day_ganzhi": cal["day_ganzhi"],
        "month_boundary": cal["month_boundary"],
        "month_boundary_time": cal["month_boundary_time"],
        "calendar_provider": cal["provider"],
        "calendar_provider_version": cal["provider_version"],
        "zi_hour_changes_day": cal["zi_hour_changes_day"],
        "status": "resolved",
    })
    return {
        "runtime": RUNTIME_NAME,
        "runtime_version": RUNTIME_VERSION,
        "raw_cast_authority": "external-fixed-fact",
        "structured_method_fact": structured,
        "interpretation_authority": False,
        "yongshen_selection_authority": False,
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Build complete deterministic Liuyao structured facts")
    p.add_argument("--lines", required=True, help="six 6/7/8/9 values, bottom-to-top")
    p.add_argument("--timestamp", required=True, help="offset-aware ISO-8601 cast timestamp")
    p.add_argument("--midnight-day-change", action="store_true",
                   help="use civil-midnight day change instead of 23:00 Zi-hour convention")
    args = p.parse_args()
    try:
        payload = build_liuyao_fact(
            args.lines,
            timestamp=args.timestamp,
            zi_hour_changes_day=not args.midnight_day_change,
        )
    except (ValueError, RuntimeError) as exc:
        raise SystemExit(str(exc)) from exc
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
