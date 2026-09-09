#!/usr/bin/env python3
"""Thin adapter from canonical Liuyao raw lines to ichingshifa structured facts.

This file does not implement Liuyao calculations. It validates the handoff,
invokes the external deterministic engine, and packages provenance.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from typing import Any

ENGINE_NAME = "kentang2017/ichingshifa"
CHECKED_ENGINE_REF = "ac1a3f8d89708acc8d547868fc9634c8e2c61d67"
ADAPTER_VERSION = "1"


def parse_lines(raw: str) -> str:
    lines = raw.strip().replace(",", "").replace(" ", "")
    if len(lines) != 6 or any(ch not in "6789" for ch in lines):
        raise argparse.ArgumentTypeError(
            "--lines must contain exactly six values in {6,7,8,9}, bottom-to-top"
        )
    return lines


def parse_timestamp(raw: str) -> datetime:
    try:
        value = datetime.fromisoformat(raw)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "--timestamp must be ISO-8601, e.g. 2026-09-09T14:30:00+08:00"
        ) from exc
    if value.tzinfo is None:
        raise argparse.ArgumentTypeError("--timestamp must include a UTC offset")
    return value


def run_engine(lines: str, timestamp: datetime) -> dict[str, Any]:
    try:
        from ichingshifa import ichingshifa  # type: ignore
    except Exception as exc:
        raise RuntimeError(
            "ichingshifa is unavailable; do not fabricate structured Liuyao facts"
        ) from exc

    engine = ichingshifa.Iching()
    try:
        result = engine.qigua_manual(
            timestamp.year,
            timestamp.month,
            timestamp.day,
            timestamp.hour,
            timestamp.minute,
            lines,
        )
    except Exception as exc:
        raise RuntimeError("ichingshifa qigua_manual execution failed") from exc

    return {
        "adapter": "liuyao-engine-adapter",
        "adapter_version": ADAPTER_VERSION,
        "engine_name": ENGINE_NAME,
        "engine_checked_ref": CHECKED_ENGINE_REF,
        "engine_runtime_version": getattr(ichingshifa, "__version__", "unknown"),
        "input": {
            "raw_lines": [int(ch) for ch in lines],
            "raw_lines_string": lines,
            "line_order": "bottom-to-top",
            "cast_timestamp": timestamp.isoformat(),
        },
        "structured_method_fact": result,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Adapt canonical Liuyao 6/7/8/9 raw cast to ichingshifa structured facts"
    )
    parser.add_argument("--lines", required=True, type=parse_lines)
    parser.add_argument("--timestamp", required=True, type=parse_timestamp)
    parser.add_argument("--format", choices=("json",), default="json")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        payload = run_engine(args.lines, args.timestamp)
    except RuntimeError as exc:
        print(
            json.dumps(
                {
                    "status": "LIUYAO_STRUCTURED_FACT_UNAVAILABLE",
                    "error": str(exc),
                    "raw_lines": [int(ch) for ch in args.lines],
                    "line_order": "bottom-to-top",
                    "cast_timestamp": args.timestamp.isoformat(),
                    "engine_name": ENGINE_NAME,
                    "engine_checked_ref": CHECKED_ENGINE_REF,
                },
                ensure_ascii=False,
                indent=2,
            ),
            file=sys.stderr,
        )
        return 2

    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
