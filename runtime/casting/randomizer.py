#!/usr/bin/env python3
"""Canonical stochastic casting CLI and importable runtime API for divination."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
from typing import Any

from core import (
    ALGORITHM_VERSION,
    COURT_SHORT,
    DECK,
    HEXAGRAM,
    LIUYAO_LINE_META,
    LIUYAO_POSITION_NAMES,
    MAJOR_SHORT,
    MAJORS,
    RANKS,
    SCHEMA_VERSION,
    SOURCE,
    SUITS,
    SUPPORTED_METHODS,
    TRIGRAM,
    UINT32_RANGE,
    execute_stochastic,
    fisher_yates,
    randbelow,
    resolve_liuyao_coin_values,
    runtime_invariants,
    short_name,
)

AI_SCHEMA_VERSION = "1"


def format_display_time(payload: dict[str, Any]) -> str:
    """Render canonical Taipei execution time for user-visible output."""
    taipei = datetime.fromisoformat(payload["generated_at_taipei"])
    return f"{taipei.strftime('%Y-%m-%d %H:%M:%S')}（{payload['timezone']}）"


def compact_ai_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Project a full canonical payload into a low-token AI transport shape."""
    compact_results: list[dict[str, Any]] = []
    for result in payload["results"]:
        compact: dict[str, Any] = {"method": result["method"]}
        tarot = result.get("tarot")
        if tarot:
            compact["tarot"] = {
                "count": tarot["count"],
                "cards": [[card["full_name"], card["orientation"]] for card in tarot["cards"]],
            }
        plum = result.get("plum")
        if plum:
            compact["plum"] = {
                "a": plum["a"],
                "b": plum["b"],
                "upper": plum["upper_trigram"],
                "lower": plum["lower_trigram"],
                "hexagram": plum["hexagram"],
                "moving_line": plum["moving_line"],
            }
        liuyao = result.get("liuyao")
        if liuyao:
            compact["liuyao"] = {
                "cast_method": liuyao["cast_method"],
                "line_order": liuyao["line_order"],
                "values": [line["value"] for line in liuyao["lines"]],
                "coin_values": [line["coin_values"] for line in liuyao["lines"]],
            }
        compact_results.append(compact)
    return {
        "source": payload["source"],
        "algorithm_version": payload["algorithm_version"],
        "schema_version": payload["schema_version"],
        "ai_schema_version": AI_SCHEMA_VERSION,
        "runtime_source_commit": payload["runtime_source_commit"],
        "generated_at_taipei": payload["generated_at_taipei"],
        "timezone": payload["timezone"],
        "results": compact_results,
    }


def generate_payload(
    command: str,
    *,
    count: int = 3,
    repeat: int = 1,
    counts: list[int] | None = None,
    method: str = "tarot",
    source_commit: str | None = None,
) -> dict[str, Any]:
    """Canonical import API; timestamp and RNG result are one atomic core execution."""
    return execute_stochastic(
        command,
        count=count,
        repeat=repeat,
        counts=counts,
        method=method,
        source_commit=source_commit,
    )


def render_text(payload: dict[str, Any]) -> str:
    lines = [
        f"來源：{payload['source']} v{payload['algorithm_version']}",
        f"時間：{format_display_time(payload)}",
    ]
    results = payload["results"]
    for idx, result in enumerate(results, start=1):
        if len(results) > 1:
            lines.extend(["", f"第 {idx} 題"])
        tarot = result.get("tarot")
        if tarot:
            lines.append(f"塔羅（{tarot['count']} 張）")
            lines.append("，".join(c["shorthand"] for c in tarot["cards"]))
        plum = result.get("plum")
        if plum:
            lines.extend([
                "梅花易數｜雙數起卦",
                f"{plum['a']}，{plum['b']}",
                f"本卦：{plum['hexagram']}",
                f"上卦：{plum['upper_trigram']}",
                f"下卦：{plum['lower_trigram']}",
                f"動爻：第 {plum['moving_line']} 爻",
                f"取卦規則：{plum['casting_rule']}",
            ])
        liuyao = result.get("liuyao")
        if liuyao:
            lines.append("六爻｜三錢法")
            for line in liuyao["lines"]:
                state = "動" if line["changing"] else "靜"
                coins = "/".join("陽" if f == "yang" else "陰" for f in line["coin_faces"])
                lines.append(f"{line['position_name']}：{line['value']} {line['line_type']}（{state}）｜{coins}")
            lines.append(f"起卦規則：{liuyao['casting_rule']}")
    return "\n".join(lines)


def parse_counts(raw: str) -> list[int]:
    try:
        values = [int(x.strip()) for x in raw.split(",") if x.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("--counts must be comma-separated integers") from exc
    if not values:
        raise argparse.ArgumentTypeError("--counts cannot be empty")
    if any(v < 1 or v > 24 for v in values):
        raise argparse.ArgumentTypeError("each count must be between 1 and 24")
    return values


def add_common_format(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--format", choices=("text", "json", "ai-json"), default="text")
    parser.add_argument("--source-commit", default=None)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Divination Casting Randomizer CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_tarot = sub.add_parser("tarot")
    p_tarot.add_argument("--count", type=int, default=3)
    p_tarot.add_argument("--repeat", type=int, default=1)
    add_common_format(p_tarot)

    p_plum = sub.add_parser("plum")
    p_plum.add_argument("--repeat", type=int, default=1)
    add_common_format(p_plum)

    p_liuyao = sub.add_parser("liuyao")
    p_liuyao.add_argument("--method", choices=("coins",), default="coins")
    p_liuyao.add_argument("--repeat", type=int, default=1)
    add_common_format(p_liuyao)

    p_both = sub.add_parser("both")
    p_both.add_argument("--count", type=int, default=3)
    p_both.add_argument("--repeat", type=int, default=1)
    add_common_format(p_both)

    p_batch = sub.add_parser("batch")
    p_batch.add_argument("--counts", type=parse_counts, required=True)
    p_batch.add_argument("--method", choices=("tarot", "both"), default="tarot")
    add_common_format(p_batch)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        payload = generate_payload(
            args.command,
            count=getattr(args, "count", 3),
            repeat=getattr(args, "repeat", 1),
            counts=getattr(args, "counts", None),
            method=getattr(args, "method", "tarot"),
            source_commit=args.source_commit,
        )
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    if args.format == "text":
        print(render_text(payload))
    elif args.format == "ai-json":
        print(json.dumps(compact_ai_payload(payload), ensure_ascii=False, separators=(",", ":")))
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
