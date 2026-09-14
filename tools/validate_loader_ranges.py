#!/usr/bin/env python3
"""Validate CI-verified line-range hints used by ChatGPT loader bypass paths.

Ranges are retrieval hints only. Canonical Markdown owners remain authoritative.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "PLAYBOOK_INDEX.json"
H2_RE = re.compile(r"^##\s")


def validate(root: Path = ROOT, index_path: Path | None = None) -> list[str]:
    errors: list[str] = []
    path = index_path or (root / "PLAYBOOK_INDEX.json")
    try:
        index = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot read loader index: {exc}"]

    loader = index.get("loader")
    if not isinstance(loader, dict):
        return ["PLAYBOOK_INDEX.json loader must be an object"]

    policy = loader.get("range_locator_policy")
    if not isinstance(policy, dict) or policy.get("kind") != "ci-verified-line-range":
        errors.append("loader.range_locator_policy.kind must be ci-verified-line-range")

    ranges = loader.get("bounded_ranges")
    if not isinstance(ranges, dict) or not ranges:
        return errors + ["loader.bounded_ranges must be a non-empty object"]

    for range_id, spec in ranges.items():
        if not isinstance(spec, dict):
            errors.append(f"{range_id}: range spec must be an object")
            continue
        owner = spec.get("owner")
        heading = spec.get("heading")
        next_heading = spec.get("next_heading")
        start = spec.get("start_line")
        end = spec.get("end_line")
        if not all(isinstance(value, str) and value for value in (owner, heading, next_heading)):
            errors.append(f"{range_id}: owner/heading/next_heading must be non-empty strings")
            continue
        if not isinstance(start, int) or not isinstance(end, int) or start < 1 or end < start:
            errors.append(f"{range_id}: invalid start_line/end_line")
            continue

        owner_path = root / owner
        if not owner_path.is_file():
            errors.append(f"{range_id}: missing owner {owner}")
            continue
        lines = owner_path.read_text(encoding="utf-8").splitlines()
        if end >= len(lines) + 1:
            errors.append(f"{range_id}: end_line {end} exceeds {owner} length {len(lines)}")
            continue
        if lines[start - 1] != heading:
            errors.append(
                f"{range_id}: start_line {start} is {lines[start - 1]!r}, expected {heading!r}"
            )
            continue
        if end >= len(lines) or lines[end] != next_heading:
            observed = lines[end] if end < len(lines) else "<EOF>"
            errors.append(
                f"{range_id}: line {end + 1} is {observed!r}, expected next heading {next_heading!r}"
            )
            continue

        interior_h2 = [
            (line_no, text)
            for line_no, text in enumerate(lines[start:end], start=start + 1)
            if H2_RE.match(text)
        ]
        if interior_h2:
            errors.append(
                f"{range_id}: unexpected H2 heading inside bounded range: {interior_h2[0]}"
            )

    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1
    index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    for range_id in index["loader"]["bounded_ranges"]:
        print(f"PASS {range_id}")
    print("ChatGPT loader ranges: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
