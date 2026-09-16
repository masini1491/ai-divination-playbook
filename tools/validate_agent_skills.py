#!/usr/bin/env python3
"""Validate the thin Agent Skills gateway without granting it Playbook authority."""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = Path(".agents/skills")
GATEWAY_NAME = "ai-divination-playbook"
GATEWAY_PATH = SKILLS_ROOT / GATEWAY_NAME / "SKILL.md"
INDEX_PATH = Path("PLAYBOOK_INDEX.json")
EXPECTED_INDEX_ADAPTER_KEY = "agent_skills_gateway"
EXPECTED_METADATA = {
    "playbook-adapter-role": "agent-skills-discovery-activation-shim",
    "playbook-authority": "none",
    "playbook-repository": "masini1491/ai-divination-playbook",
    "playbook-bootstrap": "AGENTS.md",
    "playbook-chat-init": "CHAT_INIT.md",
    "playbook-index": "PLAYBOOK_INDEX.json",
    "playbook-load-pack": "CHATGPT_LOAD_PACK.json",
}
FORBIDDEN_FRONTMATTER_KEYS = {"allowed-tools"}
FORBIDDEN_ROUTING_TOKENS = {
    "tarot",
    "meihua",
    "liuyao",
    "astrology",
    "psychology",
    "comparison →",
    "process →",
    "evolution →",
    "outcome →",
    "completion →",
}
REQUIRED_BODY_PHRASES = (
    "non-authoritative Agent Skills interoperability shim",
    "must not become a second current-state policy source or a method router",
    "current canonical governance wins",
)
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _strip_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def parse_frontmatter(text: str) -> tuple[dict[str, object], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("SKILL.md must start with YAML frontmatter delimiter '---'")
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration as exc:
        raise ValueError("SKILL.md frontmatter is missing closing '---'") from exc

    data: dict[str, object] = {}
    current_map: dict[str, str] | None = None
    current_map_name: str | None = None
    for line_no, raw in enumerate(lines[1:end], 2):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        stripped = raw.strip()
        if ":" not in stripped:
            raise ValueError(f"frontmatter line {line_no} must be key: value")
        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip()
        if indent == 0:
            current_map = None
            current_map_name = None
            if not value:
                current_map = {}
                current_map_name = key
                data[key] = current_map
            else:
                data[key] = _strip_scalar(value)
        elif indent == 2 and current_map is not None and current_map_name == "metadata":
            if not value:
                raise ValueError(f"metadata value for {key!r} must be a string")
            current_map[key] = _strip_scalar(value)
        else:
            raise ValueError(f"unsupported frontmatter indentation at line {line_no}")

    body = "\n".join(lines[end + 1 :]).strip()
    return data, body


def validate(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    skill_path = root / GATEWAY_PATH
    skills_root = root / SKILLS_ROOT

    if not skill_path.is_file():
        return [f"missing gateway skill: {GATEWAY_PATH.as_posix()}"]

    if not skills_root.is_dir():
        errors.append(f"missing skills root: {SKILLS_ROOT.as_posix()}")
    else:
        child_dirs = sorted(path.name for path in skills_root.iterdir() if path.is_dir())
        child_files = sorted(path.name for path in skills_root.iterdir() if path.is_file())
        if child_dirs != [GATEWAY_NAME]:
            errors.append(
                f"gateway-first MVP permits exactly one skill directory {GATEWAY_NAME!r}; found {child_dirs}"
            )
        if child_files:
            errors.append(f"skills root must not contain standalone files: {child_files}")

    gateway_dir = skill_path.parent
    extra_entries = sorted(path.name for path in gateway_dir.iterdir() if path.name != "SKILL.md")
    if extra_entries:
        errors.append(
            "gateway skill must remain thin; scripts/references/assets/extra files are not admitted: "
            + ", ".join(extra_entries)
        )

    text = skill_path.read_text(encoding="utf-8")
    try:
        frontmatter, body = parse_frontmatter(text)
    except ValueError as exc:
        return errors + [str(exc)]

    name = frontmatter.get("name")
    description = frontmatter.get("description")
    if not isinstance(name, str) or not name:
        errors.append("frontmatter.name is required")
    else:
        if name != GATEWAY_NAME:
            errors.append(f"frontmatter.name must equal parent directory name {GATEWAY_NAME!r}")
        if len(name) > 64 or not NAME_RE.fullmatch(name):
            errors.append("frontmatter.name violates Agent Skills naming constraints")

    if not isinstance(description, str) or not description:
        errors.append("frontmatter.description is required")
    elif len(description) > 1024:
        errors.append("frontmatter.description exceeds 1024 characters")

    compatibility = frontmatter.get("compatibility")
    if compatibility is not None and (
        not isinstance(compatibility, str) or not compatibility or len(compatibility) > 500
    ):
        errors.append("frontmatter.compatibility must be a non-empty string <= 500 characters")

    for key in FORBIDDEN_FRONTMATTER_KEYS:
        if key in frontmatter:
            errors.append(f"experimental/frontmatter field is not admitted for gateway MVP: {key}")

    metadata = frontmatter.get("metadata")
    if not isinstance(metadata, dict):
        errors.append("frontmatter.metadata mapping is required for canonical pointers")
        metadata = {}
    else:
        for key, value in metadata.items():
            if not isinstance(key, str) or not isinstance(value, str):
                errors.append("frontmatter.metadata must contain only string keys and string values")
                break
    for key, expected in EXPECTED_METADATA.items():
        if metadata.get(key) != expected:
            errors.append(f"metadata.{key} must equal {expected!r}")

    for pointer_key in ("playbook-bootstrap", "playbook-chat-init", "playbook-index", "playbook-load-pack"):
        pointer = metadata.get(pointer_key)
        if isinstance(pointer, str) and not (root / pointer).is_file():
            errors.append(f"metadata.{pointer_key} points to missing repository file: {pointer}")

    index_file = root / INDEX_PATH
    try:
        index = json.loads(index_file.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"PLAYBOOK_INDEX.json unavailable or invalid: {exc}")
        index = {}
    if isinstance(index, dict):
        bootstrap = index.get("bootstrap")
        if isinstance(bootstrap, dict) and bootstrap.get("path") != metadata.get("playbook-chat-init"):
            errors.append("gateway chat-init pointer conflicts with PLAYBOOK_INDEX bootstrap.path")
        loader = index.get("loader")
        if isinstance(loader, dict) and loader.get("cache_path") != metadata.get("playbook-load-pack"):
            errors.append("gateway load-pack pointer conflicts with PLAYBOOK_INDEX loader.cache_path")
        adapters = index.get("adapters")
        expected_adapter_path = GATEWAY_PATH.as_posix()
        if isinstance(adapters, dict) and EXPECTED_INDEX_ADAPTER_KEY in adapters:
            if adapters.get(EXPECTED_INDEX_ADAPTER_KEY) != expected_adapter_path:
                errors.append(
                    f"PLAYBOOK_INDEX adapters.{EXPECTED_INDEX_ADAPTER_KEY} conflicts with {expected_adapter_path}"
                )

    lowered_description = description.lower() if isinstance(description, str) else ""
    lowered_body = body.lower()
    for token in sorted(FORBIDDEN_ROUTING_TOKENS):
        if token in lowered_description or token in lowered_body:
            errors.append(
                f"gateway must not encode method-routing/method-specific policy; forbidden token present: {token!r}"
            )

    if "```" in body or "~~~" in body:
        errors.append("gateway body must not embed fenced policy/code blocks")
    for phrase in REQUIRED_BODY_PHRASES:
        if phrase not in body:
            errors.append(f"gateway authority boundary missing required phrase: {phrase!r}")
    if len(body.splitlines()) > 120:
        errors.append("gateway SKILL.md body is too large for a thin activation adapter")

    return errors


def main() -> int:
    errors = validate(ROOT)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Agent Skills gateway validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
