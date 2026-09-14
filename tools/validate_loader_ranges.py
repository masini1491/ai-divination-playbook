#!/usr/bin/env python3
"""Validate generated bounded loader line-range hints.

The generator owns start_line/end_line derivation. This validator additionally checks
that the committed generated ranges resolve to the declared canonical headings.
"""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "PLAYBOOK_INDEX.json"
H2_RE = re.compile(r"^##\s")
POLICY_KIND = "generated-ci-verified-line-range"


def _load_generator(root: Path):
    path = root / "tools" / "build_loader_ranges.py"
    spec = importlib.util.spec_from_file_location("build_loader_ranges", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


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
    if not isinstance(policy, dict) or policy.get("kind") != POLICY_KIND:
        errors.append(f"loader.range_locator_policy.kind must be {POLICY_KIND}")
    if not isinstance(policy, dict) or policy.get("generator") != "tools/build_loader_ranges.py":
        errors.append("loader.range_locator_policy.generator must be tools/build_loader_ranges.py")

    try:
        generator = _load_generator(root)
        errors.extend(generator.validate_generated(root, path))
    except (OSError, ValueError, ImportError) as exc:
        errors.append(f"cannot validate generated loader ranges: {exc}")

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
            errors.append(f"{range_id}: invalid generated start_line/end_line")
            continue

        owner_path = root / owner
        if not owner_path.is_file():
            errors.append(f"{range_id}: missing owner {owner}")
            continue
        lines = owner_path.read_text(encoding="utf-8").splitlines()
        if start > len(lines) or end > len(lines):
            errors.append(f"{range_id}: generated range exceeds {owner} length {len(lines)}")
            continue
        if lines[start - 1] != heading:
            errors.append(f"{range_id}: generated start_line does not resolve to declared heading")
            continue
        if end >= len(lines) or lines[end] != next_heading:
            errors.append(f"{range_id}: generated end_line does not stop immediately before next_heading")
            continue
        interior_h2 = [text for text in lines[start:end] if H2_RE.match(text)]
        if interior_h2:
            errors.append(f"{range_id}: unexpected H2 heading inside generated bounded range")

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
    print("ChatGPT generated loader ranges: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
