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
RUNTIME_VERSION = "4"

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


def _line_symbol(yin_yang: str) -> str:
    if yin_yang == "yang":
        return "━━━━━━"
    if yin_yang == "yin":
        return "━━ ━━"
    raise ValueError("yin_yang must be yang or yin")


def _change_marker(value: int) -> str:
    if value == 9:
        return "○"
    if value == 6:
        return "×"
    return ""


def _active_flags(line: dict[str, Any]) -> list[str]:
    flags = line.get("flags") or {}
    return [name for name in ("旬空", "月破", "日沖") if flags.get(name)]


def _joined_flags(flags: list[str]) -> str:
    return "、".join(flags) if flags else ""


def _fu_shen_text(items: list[dict[str, Any]]) -> str:
    if not items:
        return ""
    return "；".join(
        f"{item.get('six_relative') or ''} {item.get('najia') or ''}{item.get('five_element') or ''}".strip()
        for item in items
    )


def build_markdown_table(presentation: dict[str, Any]) -> str:
    """Render the derived presentation as a ChatGPT-ready Markdown table."""
    h = presentation["header"]
    xk = "、".join(h.get("xunkong") or []) or "—"
    lines = [
        f"起卦時間：{h.get('cast_timestamp') or '—'}｜月建：{h.get('month_branch') or '—'}｜日辰：{h.get('day_ganzhi') or '—'}｜旬空：{xk}",
        f"本卦：{h.get('ben_gua') or '—'}（{h.get('ben_palace') or '—'}宮／{h.get('ben_palace_type') or '—'}）｜之卦：{h.get('zhi_gua') or '無（無動爻）'}",
        "",
        "| 六獸 | 六親 | 世應 | 本卦 | 五行 | 之卦 | 伏神 |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in presentation["rows"]:
        primary_flags = _joined_flags(row["flags"])
        ben = f"{row['traditional_label']} {row['ben_line_symbol']}"
        if row["change_marker"]:
            ben += f" {row['change_marker']}"
        five = f"{row.get('ben_najia') or ''}{row.get('ben_five_element') or ''}"
        if primary_flags:
            five += f"（{primary_flags}）"
        changed = row.get("changed")
        if changed:
            changed_text = f"{changed['line_symbol']} {changed.get('najia') or ''}{changed.get('five_element') or ''} {changed.get('six_relative') or ''}".strip()
            changed_flags = _joined_flags(changed.get("flags") or [])
            if changed_flags:
                changed_text += f"（{changed_flags}）"
        else:
            changed_text = ""
        lines.append(
            "| " + " | ".join([
                row.get("six_spirit") or "",
                row.get("six_relative") or "",
                row.get("shi_ying") or "",
                ben,
                five,
                changed_text,
                _fu_shen_text(row.get("fu_shen") or []),
            ]) + " |"
        )
    return "\n".join(lines)


def build_human_display(structured: dict[str, Any]) -> dict[str, Any]:
    """Build non-authoritative top-to-bottom Liuyao chart-table metadata.

    Structured facts and raw line storage stay bottom-to-top. This function only
    derives labels/order and joins already-computed fields into a human-facing
    table. It never computes yongshen or interpretation and must never replace
    canonical ``raw_lines`` / chart ordering.
    """
    raw_lines = structured.get("raw_lines")
    if not isinstance(raw_lines, list) or len(raw_lines) != 6:
        raise ValueError("structured raw_lines must contain six canonical lines")

    ben = structured.get("ben_gua")
    if not isinstance(ben, dict) or not isinstance(ben.get("lines"), list):
        raise ValueError("structured ben_gua must contain line facts")
    zhi = structured.get("zhi_gua")
    moving = set(structured.get("moving_positions") or [])
    cal = structured.get("calendar_context") or {}

    ben_by_position = {int(line["position"]): line for line in ben["lines"]}
    zhi_by_position = (
        {int(line["position"]): line for line in zhi["lines"]}
        if isinstance(zhi, dict) and isinstance(zhi.get("lines"), list)
        else {}
    )
    fu_by_position: dict[int, list[dict[str, Any]]] = {}
    for item in structured.get("fu_shen") or []:
        fu_by_position.setdefault(int(item["position"]), []).append({
            "six_relative": item.get("six_relative"),
            "najia": item.get("najia"),
            "five_element": item.get("five_element"),
        })

    lines = []
    rows = []
    for position in range(6, 0, -1):
        value = int(raw_lines[position - 1])
        line_type, changing = LINE_TYPES[value]
        primary = ben_by_position[position]
        changed = zhi_by_position.get(position) if position in moving else None
        basic = {
            "position": position,
            "position_name": POSITION_NAMES[position],
            "traditional_label": traditional_line_label(value, position),
            "raw_value": value,
            "line_type": line_type,
            "changing": changing,
        }
        lines.append(basic)
        rows.append({
            **basic,
            "six_spirit": primary.get("six_spirit"),
            "six_relative": primary.get("six_relative"),
            "shi_ying": primary.get("shi_ying"),
            "ben_line_symbol": _line_symbol(primary["yin_yang"]),
            "change_marker": _change_marker(value),
            "ben_najia": primary.get("najia"),
            "ben_five_element": primary.get("five_element"),
            "flags": _active_flags(primary),
            "changed": ({
                "line_symbol": _line_symbol(changed["yin_yang"]),
                "six_relative": changed.get("six_relative"),
                "najia": changed.get("najia"),
                "five_element": changed.get("five_element"),
                "flags": _active_flags(changed),
            } if changed is not None else None),
            "fu_shen": fu_by_position.get(position, []),
        })

    presentation = {
        "authority": "derived-display-only",
        "display_order": "top-to-bottom",
        "canonical_storage_order": "bottom-to-top",
        "render_hint": "ChatGPT should render markdown_table before interpretation when a full Liuyao Structured Method Fact is available.",
        "header": {
            "cast_timestamp": cal.get("timestamp"),
            "day_ganzhi": cal.get("day_ganzhi"),
            "month_branch": cal.get("month_branch"),
            "xunkong": cal.get("xunkong"),
            "ben_gua": ben.get("name"),
            "ben_palace": ben.get("palace"),
            "ben_palace_element": ben.get("palace_element"),
            "ben_palace_type": ben.get("palace_type"),
            "zhi_gua": zhi.get("name") if isinstance(zhi, dict) else None,
        },
        "table_columns": [
            "六獸", "六親", "世應", "本卦", "五行", "之卦", "伏神"
        ],
        "rows": rows,
        "lines": lines,
    }
    presentation["markdown_table"] = build_markdown_table(presentation)
    return presentation


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
