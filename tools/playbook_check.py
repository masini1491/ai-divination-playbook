#!/usr/bin/env python3
"""Deterministic structural checks for ai-divination-playbook."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any
from urllib.parse import unquote

IGNORED_DIRS = {".git", ".venv", "venv", "__pycache__"}
MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
FENCE_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})(.*)$")
CODE_SPAN_RE = re.compile(r"`([^`\n]+)`")
URL_SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
BEHAVIOR_ID_RE = re.compile(r"^###\s+(TAROT-BEH-\d{3})\b", re.MULTILINE)
INDEX_NAME = "PLAYBOOK_INDEX.json"
INDEX_SCHEMA_VERSION = 1
INDEX_AUTHORITY = "routing-only"
INDEX_LOCAL_PATH_SUFFIXES = (".md", ".json", ".py")
INDEX_EXTERNAL_LOCATOR_KEYS = {"implementation", "casting_implementation"}
MATRIX_SCHEMA_VERSION = 1
MATRIX_AUTHORITY = "selection-only"
TEXT_SUFFIXES = {".md", ".json", ".py"}
DEPRECATED_IDENTIFIERS = (
    "tarot-" + "plum-randomizer",
    "tarot-meihua-" + "question-playbook",
)
ALLOWED_LEGACY_DEPLOYMENT_URLS = (
    "https://tarot-plum-randomizer-masini1491-9205.vercel.app",
)


def outside_fence_lines(text: str):
    fence: tuple[str, int] | None = None
    for line_no, line in enumerate(text.splitlines(), 1):
        match = FENCE_RE.match(line)
        if match:
            marker = match.group(1)
            if fence is None:
                fence = (marker[0], len(marker))
            elif marker[0] == fence[0] and len(marker) >= fence[1]:
                fence = None
            continue
        if fence is None:
            yield line_no, line


def github_slug(heading: str) -> str:
    heading = re.sub(r"!?\[([^\]]+)\]\([^)]+\)", r"\1", heading)
    heading = re.sub(r"<[^>]+>", "", heading)
    heading = heading.replace("`", "").lower().strip()
    chars: list[str] = []
    for char in heading:
        if char.isspace():
            chars.append("-")
        elif char.isalnum() or char in {"-", "_"}:
            chars.append(char)
    return "".join(chars)


def heading_names(text: str) -> set[str]:
    names: set[str] = set()
    for _line_no, line in outside_fence_lines(text):
        match = HEADING_RE.match(line)
        if match:
            names.add(match.group(2).strip())
    return names


def heading_anchors(text: str) -> set[str]:
    anchors: set[str] = set()
    counts: dict[str, int] = {}
    for _line_no, line in outside_fence_lines(text):
        match = HEADING_RE.match(line)
        if not match:
            continue
        base = github_slug(match.group(2))
        if not base:
            continue
        count = counts.get(base, 0)
        anchors.add(base if count == 0 else f"{base}-{count}")
        counts[base] = count + 1
    return anchors


def markdown_files(root: Path) -> list[Path]:
    result: list[Path] = []
    for path in root.rglob("*.md"):
        rel = path.relative_to(root)
        if any(part in IGNORED_DIRS for part in rel.parts):
            continue
        if path.is_file():
            result.append(path)
    return sorted(result)


def text_files(root: Path) -> list[Path]:
    result: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        rel = path.relative_to(root)
        if any(part in IGNORED_DIRS for part in rel.parts):
            continue
        result.append(path)
    return sorted(result)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def local_target(source: Path, root: Path, raw: str) -> tuple[Path, str | None] | None:
    target = raw.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1].strip()
    elif " " in target:
        target = target.split(None, 1)[0]
    target = unquote(target)
    if not target or target.startswith("//") or URL_SCHEME_RE.match(target):
        return None
    path_part, sep, fragment = target.partition("#")
    resolved = source if not path_part else (root / path_part.lstrip("/") if path_part.startswith("/") else source.parent / path_part)
    return resolved.resolve(), fragment if sep else None


def check_markdown_links(root: Path) -> list[str]:
    errors: list[str] = []
    anchor_cache: dict[Path, set[str]] = {}
    root_resolved = root.resolve()
    for path in markdown_files(root):
        text = path.read_text(encoding="utf-8")
        for line_no, line in outside_fence_lines(text):
            for match in MARKDOWN_LINK_RE.finditer(line):
                resolved_target = local_target(path, root, match.group(1))
                if resolved_target is None:
                    continue
                resolved, fragment = resolved_target
                try:
                    resolved.relative_to(root_resolved)
                except ValueError:
                    errors.append(f"{path.relative_to(root)}:{line_no}: local link escapes repository: {match.group(1)}")
                    continue
                if not resolved.exists():
                    errors.append(f"{path.relative_to(root)}:{line_no}: missing local link target: {match.group(1)}")
                    continue
                if fragment and resolved.is_file() and resolved.suffix.lower() == ".md":
                    anchors = anchor_cache.setdefault(resolved, heading_anchors(resolved.read_text(encoding="utf-8")))
                    if fragment not in anchors:
                        errors.append(f"{path.relative_to(root)}:{line_no}: missing Markdown anchor: {match.group(1)}")
    return errors


def check_deprecated_identifiers(root: Path) -> list[str]:
    errors: list[str] = []
    for path in text_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        scan_text = text
        for deployment_url in ALLOWED_LEGACY_DEPLOYMENT_URLS:
            scan_text = scan_text.replace(deployment_url, "")
        for identifier in DEPRECATED_IDENTIFIERS:
            if identifier in scan_text:
                errors.append(f"{path.relative_to(root)}: deprecated canonical identifier: {identifier}")
    return errors


def check_index_local_file_value(root: Path, prefix: str, value: Any) -> list[str]:
    if not isinstance(value, str) or not value.lower().endswith(INDEX_LOCAL_PATH_SUFFIXES):
        return []
    if not (root / value).is_file():
        return [f"{prefix} must point to an existing local file: {value}"]
    return []


def check_index(root: Path) -> list[str]:
    errors: list[str] = []
    path = root / INDEX_NAME
    if not path.exists():
        return [f"{INDEX_NAME}: missing"]
    try:
        data = load_json(path)
    except Exception as exc:
        return [f"{INDEX_NAME}: invalid JSON: {exc}"]
    if not isinstance(data, dict):
        return [f"{INDEX_NAME}: top-level value must be an object"]
    if data.get("schema_version") != INDEX_SCHEMA_VERSION:
        errors.append(f"{INDEX_NAME}: schema_version must be {INDEX_SCHEMA_VERSION}")
    if data.get("authority") != INDEX_AUTHORITY:
        errors.append(f"{INDEX_NAME}: authority must be {INDEX_AUTHORITY}")

    bootstrap = data.get("bootstrap")
    bootstrap_path = bootstrap.get("path") if isinstance(bootstrap, dict) else None
    if not isinstance(bootstrap_path, str) or not (root / bootstrap_path).is_file():
        errors.append(f"{INDEX_NAME}: bootstrap.path must point to an existing file")

    capabilities = data.get("capabilities")
    if not isinstance(capabilities, list) or not capabilities:
        errors.append(f"{INDEX_NAME}: capabilities must be a non-empty array")
        capabilities = []
    ids: set[str] = set()
    for i, item in enumerate(capabilities):
        prefix = f"{INDEX_NAME}: capabilities[{i}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        cap_id = item.get("id")
        if not isinstance(cap_id, str) or not cap_id.strip():
            errors.append(f"{prefix}.id must be non-empty")
        elif cap_id in ids:
            errors.append(f"{prefix}.id duplicate: {cap_id}")
        else:
            ids.add(cap_id)
        owner = item.get("owner")
        if not isinstance(owner, str) or not (root / owner).is_file():
            errors.append(f"{prefix}.owner must point to an existing file")
            continue
        section = item.get("section")
        if section is not None:
            if not isinstance(section, str) or section not in heading_names((root / owner).read_text(encoding="utf-8")):
                errors.append(f"{prefix}.section missing in {owner}: {section}")
        for key, value in item.items():
            if key in {"owner", "section"} or key in INDEX_EXTERNAL_LOCATOR_KEYS:
                continue
            errors.extend(check_index_local_file_value(root, f"{prefix}.{key}", value))

    adapters = data.get("adapters", {})
    if not isinstance(adapters, dict):
        errors.append(f"{INDEX_NAME}: adapters must be an object")
    else:
        for name, target in adapters.items():
            if not isinstance(target, str) or not (root / target).is_file():
                errors.append(f"{INDEX_NAME}: adapters.{name} must point to an existing file")

    behavioral = data.get("behavioral_regression", {})
    if not isinstance(behavioral, dict):
        errors.append(f"{INDEX_NAME}: behavioral_regression must be an object")
    else:
        for key in ("matrix", "runner"):
            target = behavioral.get(key)
            if not isinstance(target, str) or not (root / target).is_file():
                errors.append(f"{INDEX_NAME}: behavioral_regression.{key} must point to an existing file")
    return errors


def section_ranges(text: str, heading: str) -> list[tuple[int, int]]:
    lines = text.splitlines()
    ranges: list[tuple[int, int]] = []
    for i, line in enumerate(lines):
        match = HEADING_RE.match(line)
        if not match or match.group(2).strip() != heading:
            continue
        level = len(match.group(1))
        end = len(lines)
        for j in range(i + 1, len(lines)):
            next_match = HEADING_RE.match(lines[j])
            if next_match and len(next_match.group(1)) <= level:
                end = j
                break
        ranges.append((i, end))
    return ranges


def check_unique_owner_sections(root: Path, manifests: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    for manifest in manifests:
        owner = root / manifest["owner"]
        text = owner.read_text(encoding="utf-8")
        for section in manifest.get("required_sections", []):
            count = len(section_ranges(text, section))
            if count != 1:
                errors.append(f"{manifest['owner']}: section must appear exactly once: {section} (found {count})")
    return errors


def load_required_manifests(root: Path) -> tuple[list[dict[str, Any]], list[str]]:
    errors: list[str] = []
    manifests: list[dict[str, Any]] = []
    for path in sorted(root.glob("*_ADMISSION_V1.json")):
        try:
            data = load_json(path)
        except Exception as exc:
            errors.append(f"{path.name}: invalid JSON: {exc}")
            continue
        if not isinstance(data, dict):
            errors.append(f"{path.name}: top-level value must be an object")
            continue
        owner = data.get("owner")
        required_sections = data.get("required_sections", [])
        if owner is not None and isinstance(required_sections, list):
            manifests.append({"manifest": path.name, "owner": owner, "required_sections": required_sections})
    return manifests, errors


def check_manifest_owner_sections(root: Path) -> list[str]:
    manifests, errors = load_required_manifests(root)
    for manifest in manifests:
        owner = root / manifest["owner"]
        if not owner.is_file():
            errors.append(f"{manifest['manifest']}: owner missing: {manifest['owner']}")
    valid = [m for m in manifests if (root / m["owner"]).is_file()]
    errors.extend(check_unique_owner_sections(root, valid))
    return errors


def behavioral_ids(text: str) -> set[str]:
    return set(BEHAVIOR_ID_RE.findall(text))


def check_behavioral_matrix(root: Path) -> list[str]:
    errors: list[str] = []
    matrix_path = root / "evals" / "regression_matrix.json"
    eval_path = root / "BEHAVIORAL_EVAL.md"
    if not matrix_path.is_file() or not eval_path.is_file():
        return errors
    try:
        matrix = load_json(matrix_path)
    except Exception as exc:
        return [f"evals/regression_matrix.json: invalid JSON: {exc}"]
    if not isinstance(matrix, dict):
        return ["evals/regression_matrix.json: top-level value must be an object"]
    if matrix.get("schema_version") != MATRIX_SCHEMA_VERSION:
        errors.append(f"evals/regression_matrix.json: schema_version must be {MATRIX_SCHEMA_VERSION}")
    if matrix.get("authority") != MATRIX_AUTHORITY:
        errors.append(f"evals/regression_matrix.json: authority must be {MATRIX_AUTHORITY}")
    known = behavioral_ids(eval_path.read_text(encoding="utf-8"))
    full = matrix.get("full_baseline", [])
    if not isinstance(full, list) or not full:
        errors.append("evals/regression_matrix.json: full_baseline must be a non-empty array")
        full = []
    for scenario in full:
        if scenario not in known:
            errors.append(f"evals/regression_matrix.json: unknown full_baseline scenario: {scenario}")
    change_classes = matrix.get("change_classes", {})
    if not isinstance(change_classes, dict):
        errors.append("evals/regression_matrix.json: change_classes must be an object")
    else:
        for name, scenarios in change_classes.items():
            if not isinstance(scenarios, list) or not scenarios:
                errors.append(f"evals/regression_matrix.json: change_classes.{name} must be a non-empty array")
                continue
            for scenario in scenarios:
                if scenario not in known:
                    errors.append(f"evals/regression_matrix.json: unknown scenario in {name}: {scenario}")
    return errors


def check_chat_init_routes(root: Path) -> list[str]:
    errors: list[str] = []
    path = root / "CHAT_INIT.md"
    if not path.is_file():
        return ["CHAT_INIT.md: missing"]
    text = path.read_text(encoding="utf-8")
    for match in CODE_SPAN_RE.finditer(text):
        value = match.group(1)
        if not value.endswith(".md") or "/" in value:
            continue
        if value in {"CHAT_INIT.md"}:
            continue
        if not (root / value).is_file():
            errors.append(f"CHAT_INIT.md: routed owner missing: {value}")
    return errors


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    errors.extend(check_markdown_links(root))
    errors.extend(check_deprecated_identifiers(root))
    errors.extend(check_index(root))
    errors.extend(check_manifest_owner_sections(root))
    errors.extend(check_behavioral_matrix(root))
    errors.extend(check_chat_init_routes(root))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()
    errors = validate(Path(args.root))
    if errors:
        for error in errors:
            print(error)
        return 1
    print("playbook structure OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
