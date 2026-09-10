#!/usr/bin/env python3
"""Integrated Liuyao structured-fact runtime.

This module joins the zero-dependency calendar provider with the zero-dependency
structural Liuyao engine. Raw stochastic casting remains owned by the separate
Divination Casting Randomizer; this file accepts already-fixed 6/7/8/9 facts.

Authority boundary:
- input raw lines: stochastic fact supplied by caller
- calendar provider: deterministic time facts only
- structural engine: deterministic chart facts only
- presentation: derived display metadata only; never changes canonical facts
- no yongshen selection, no auspiciousness judgment, no interpretation

Canonical storage/calculation order remains bottom-to-top (初爻 -> 上爻).
Human-facing hexagram display is top-to-bottom (上爻 -> 初爻), matching normal
printed Liuyao layout. Traditional labels use 九 for yang and 六 for yin:
初九/初六, 九二/六二 ... 上九/上六.
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
RUNTIME_VERSION = "2"

POSITION_NAMES = {
    1: "初爻",
    2: "二爻",
    3: "三爻",
    4: "四爻",
    5: "五爻",
    6: "上爻",
}
POSITION_TOKENS = {1: "初", 2: "二", 3: "三", 4: "四", 5: "五", 6: "上"}
LINE_TYPES = {
    6: ("老陰", True),
    7: ("少陽", False),
    8: ("少陰", False),
    9: ("老陽", True),
}


def traditional_line_label(value: int, position: int) -> str:
    """Return the conventional爻名 for one fixed 6/7/8/9 line value."""
    if value not in LINE_TYPES:
        raise ValueError("line value must be one of 6,7,8,9")
    if position not in POSITION_NAMES:
        raise ValueError("position must be in 1..6")
    yin_yang_name = "九" if value in {7, 9} else "六"
    if position == 1:
        return f"初{yin_yang_name}"
    if position == 6:
        return f"上{yin_yang_name}"
    return f"{yin_yang_name}{POSITION_TOKENS[position]}"


def build_human_display(structured: dict[str, Any]) -> dict[str, Any]:
    """Build non-authoritative top-to-bottom display metadata.

    Structured facts and raw line storage stay bottom-to-top. This function only
    derives labels/order for human presentation and must never be written back as
    a replacement for canonical ``raw_lines`` or ``ben_gua.lines`` ordering.
    """
    raw_lines = structured.get("raw_lines")
    if not isinstance(raw_lines, list) or len(raw_lines) != 6:
        raise ValueError("structured raw_lines must contain six canonical lines")

    lines = []
    for position in range(6, 0, -1):
        value = int(raw_lines[position - 1])
        line_type, changing = LINE_TYPES[value]
        lines.append({
            "position": position,
            "position_name": POSITION_NAMES[position],
            "traditional_label": traditional_line_label(value, position),
            "raw_value": value,
            "line_type": line_type,
            "changing": changing,
        })

    return {
        "authority": "derived-display-only",
        "display_order": "top-to-bottom",
        "canonical_storage_order": "bottom-to-top",
        "lines": lines,
    }


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
        "presentation": build_human_display(structured),
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
