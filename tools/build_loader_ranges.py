#!/usr/bin/env python3
"""Generate or verify bounded loader line-range locators.

The declarative locator identity is owner + heading + next_heading. start_line/end_line
are derived output only and must never become independent policy authority.
"""

from __future__ import annotations

import argparse
import json
import re
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "PLAYBOOK_INDEX.json"
GENERATOR = "tools/build_loader_ranges.py"
POLICY_KIND = "generated-ci-verified-line-range"
H2_RE = re.compile(r"^##\s")


def _unique_line(lines: list[str], value: str, *, after: int | None = None) -> int:
    start = 0 if after is None else after + 1
    matches = [index for index in range(start, len(lines)) if lines[index] == value]
    if len(matches) != 1:
        scope = "file" if after is None else "remaining file"
        raise ValueError(f"expected exactly one {value!r} in {scope}, found {len(matches)}")
    return matches[0]


def derive_range(root: Path, spec: dict) -> dict:
    owner = spec.get("owner")
    heading = spec.get("heading")
    next_heading = spec.get("next_heading")
    if not all(isinstance(value, str) and value for value in (owner, heading, next_heading)):
        raise ValueError("range spec requires non-empty owner/heading/next_heading")

    owner_path = root / owner
    if not owner_path.is_file():
        raise ValueError(f"missing range owner {owner}")
    lines = owner_path.read_text(encoding="utf-8").splitlines()
    start_index = _unique_line(lines, heading)
    next_index = _unique_line(lines, next_heading, after=start_index)
    if next_index <= start_index:
        raise ValueError(f"{owner}: next heading does not follow heading")

    interior_h2 = [
        (line_no, text)
        for line_no, text in enumerate(lines[start_index + 1 : next_index], start=start_index + 2)
        if H2_RE.match(text)
    ]
    if interior_h2:
        raise ValueError(
            f"{owner}: unexpected H2 before declared next_heading: {interior_h2[0]}"
        )

    return {
        "owner": owner,
        "heading": heading,
        "start_line": start_index + 1,
        "end_line": next_index,
        "next_heading": next_heading,
    }


def expected_index(root: Path = ROOT, index_path: Path = INDEX_PATH) -> dict:
    index = json.loads(index_path.read_text(encoding="utf-8"))
    loader = index.get("loader")
    if not isinstance(loader, dict):
        raise ValueError("PLAYBOOK_INDEX.json loader must be an object")
    ranges = loader.get("bounded_ranges")
    if not isinstance(ranges, dict) or not ranges:
        raise ValueError("loader.bounded_ranges must be a non-empty object")

    expected = deepcopy(index)
    expected_loader = expected["loader"]
    expected_loader["range_locator_policy"] = {
        "kind": POLICY_KIND,
        "generator": GENERATOR,
        "validator": "tools/validate_loader_ranges.py",
        "rule": (
            "owner/heading/next_heading declare locator identity; start_line/end_line are generated "
            "retrieval hints only. Canonical owner content remains authoritative."
        ),
    }
    expected_loader["bounded_ranges"] = {
        range_id: derive_range(root, spec) for range_id, spec in ranges.items()
    }
    return expected


def validate_generated(root: Path = ROOT, index_path: Path = INDEX_PATH) -> list[str]:
    try:
        current = json.loads(index_path.read_text(encoding="utf-8"))
        expected = expected_index(root, index_path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return [str(exc)]
    if current == expected:
        return []

    errors: list[str] = []
    current_loader = current.get("loader", {}) if isinstance(current, dict) else {}
    expected_loader = expected["loader"]
    if current_loader.get("range_locator_policy") != expected_loader["range_locator_policy"]:
        errors.append("loader.range_locator_policy is stale; regenerate PLAYBOOK_INDEX.json")
    if current_loader.get("bounded_ranges") != expected_loader["bounded_ranges"]:
        errors.append("loader.bounded_ranges is stale; regenerate PLAYBOOK_INDEX.json")
    if not errors:
        errors.append("PLAYBOOK_INDEX.json differs from generated loader-range output")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail when generated locator output is stale")
    args = parser.parse_args()

    errors = validate_generated()
    if args.check:
        if errors:
            for error in errors:
                print(f"FAIL {error}")
            return 1
        print("ChatGPT generated loader ranges: PASS")
        return 0

    expected = expected_index()
    INDEX_PATH.write_text(json.dumps(expected, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote generated loader ranges to {INDEX_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
