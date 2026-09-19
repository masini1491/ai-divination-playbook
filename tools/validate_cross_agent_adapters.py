#!/usr/bin/env python3
"""Validate thin cross-agent bootstrap adapters without granting them Playbook authority."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
ADAPTERS = {
    "GEMINI.md": "Gemini CLI",
    ".github/copilot-instructions.md": "GitHub Copilot",
}
REQUIRED_POINTERS = ("\`AGENTS.md\`", "\`CHAT_INIT.md\`", "\`PLAYBOOK_INDEX.json\`", "\`CHATGPT_LOAD_PACK.json\`")
REQUIRED_PHRASES = (
    "not a Playbook authority",
    "does not create a second current-state policy source",
    "current canonical governance wins",
    "compatibility handoff only, never as parallel authority",
    "does not alter the repository's \`Project AI mode: ChatGPT-Only\`",
    "does not by itself grant this host canonical Playbook execution authority",
)
FORBIDDEN_POLICY_TOKENS = (
    "Psychology → Tarot",
    "Process → Meihua",
    "Outcome → Liuyao",
    "explicit-request-only",
    "draw_tarot(",
    "cast_plum(",
    "cast_liuyao(",
    "capsule_verification.json",
    "cache_locator_version",
)


def validate(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    texts: dict[str, str] = {}

    for relative, host in ADAPTERS.items():
        path = root / relative
        if not path.is_file():
            errors.append(f"missing cross-agent adapter: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        texts[relative] = text
        if host not in text:
            errors.append(f"{relative}: host identity missing: {host}")
        for pointer in REQUIRED_POINTERS:
            if pointer not in text:
                errors.append(f"{relative}: canonical bootstrap pointer missing: {pointer}")
        for phrase in REQUIRED_PHRASES:
            if phrase not in text:
                errors.append(f"{relative}: authority boundary missing phrase: {phrase!r}")
        for token in FORBIDDEN_POLICY_TOKENS:
            if token in text:
                errors.append(f"{relative}: duplicated normative policy token forbidden: {token!r}")
        if "\`\`\`" in text or "~~~" in text:
            errors.append(f"{relative}: fenced policy/code blocks are not admitted in thin adapters")
        if len(text.splitlines()) > 40:
            errors.append(f"{relative}: adapter is too large for a thin bootstrap shim")

    if len(texts) == len(ADAPTERS):
        normalized = []
        for relative, host in ADAPTERS.items():
            text = texts[relative].replace(host, "<HOST>")
            normalized.append(text)
        if len(set(normalized)) != 1:
            errors.append("cross-agent adapters drift: bodies must remain identical except for host identity")

    return errors


def main() -> int:
    errors = validate(ROOT)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Cross-agent bootstrap adapter validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
