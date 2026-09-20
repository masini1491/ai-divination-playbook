#!/usr/bin/env python3
"""Build or verify the derived ChatGPT cold-start load pack.

The pack is a retrieval cache only. Canonical Markdown owners remain authoritative.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "CHATGPT_LOAD_PACK.json"

FRAGMENT_SPECS = {
    "bootstrap": {
        "owner": "CHAT_INIT.md",
        "sections": [
            "## Default Interaction Profile｜只給 Repo 也能直接使用",
            "## ChatGPT Load Pack Fast Path｜one retrieval cache",
        ],
    },
    "ordinary_routing": {
        "owner": "METHOD_ROUTING.md",
        "sections": [
            "## Fast Path｜高信心命中就停止 routing",
            "## 1. User Method Override｜使用者已指定方法",
        ],
    },
    "runtime_fast_path": {
        "owner": "RUNTIME_DRAW.md",
        "sections": [
            "## Section Router｜最低必要載入",
            "## Fast Path｜普通占問預設",
        ],
    },
    "output_core": {
        "owner": "CHATGPT_OUTPUT.md",
        "sections": [
            "## Section Router｜依任務只讀最低必要段落",
            "## 1. 原題範圍是輸出硬邊界",
            "## 2. 區分事實、原始結果、Structured Fact、方法規則與象徵推論",
            "## 3. 先回答原題，再展開必要證據",
            "## 4. One Question = One Conclusion Surface",
            "## 5. 輸出層是按題型啟用，不是固定全部輸出",
            "## 6. 使用最低充分牌義／卦義／方法事實",
            "## 7. 信心語言要與證據相稱",
            "## 13. Pre-Send Gate｜送出前檢查實際最終草稿",
        ],
    },
}

PROFILES = {
    "ordinary_unspecified": {
        "fragments": ["bootstrap", "ordinary_routing", "runtime_fast_path", "output_core"],
        "required_followup": ["selected method owner"],
        "notes": "Use runtime fragment only when ChatGPT/AI actually performs a stochastic draw/cast.",
    },
    "explicit_tarot": {
        "fragments": ["bootstrap", "runtime_fast_path", "output_core"],
        "required_followup": ["TAROT.md"],
    },
    "explicit_meihua": {
        "fragments": ["bootstrap", "runtime_fast_path", "output_core"],
        "required_followup": ["MEIHUA.md"],
    },
    "explicit_liuyao": {
        "fragments": ["bootstrap", "runtime_fast_path", "output_core"],
        "required_followup": ["LIUYAO.md"],
    },
    "explicit_astrology": {
        "fragments": ["bootstrap", "output_core"],
        "required_followup": ["ASTROLOGY.md", "selected Astrology mode owner"],
        "notes": "Production Astrology only; after the root owner, load ASTROLOGY_NATAL.md or ASTROLOGY_TRANSIT.md by reading_mode. Research intent continues to bypass the pack.",
    },
    "continuation_stochastic": {
        "fragments": ["bootstrap", "runtime_fast_path", "output_core"],
        "required_followup": ["READING_LIFECYCLE.md", "selected method owner"],
        "notes": "READING_RECORD.md remains conditional on durable storage/cross-chat/audit intent.",
    },
}


def extract_section(text: str, heading: str) -> str:
    lines = text.splitlines()
    try:
        start = lines.index(heading)
    except ValueError as exc:
        raise ValueError(f"missing load-pack heading {heading!r}") from exc

    match = re.match(r"^(#+)\s", heading)
    if not match:
        raise ValueError(f"invalid heading spec {heading!r}")
    level = len(match.group(1))

    end = len(lines)
    for index in range(start + 1, len(lines)):
        next_match = re.match(r"^(#+)\s", lines[index])
        if next_match and len(next_match.group(1)) <= level:
            end = index
            break
    return "\n".join(lines[start:end]).rstrip() + "\n"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_pack(root: Path = ROOT) -> dict:
    fragments = {}
    for fragment_id, spec in FRAGMENT_SPECS.items():
        owner = root / spec["owner"]
        owner_text = owner.read_text(encoding="utf-8")
        excerpts = [extract_section(owner_text, heading) for heading in spec["sections"]]
        content = "\n".join(part.rstrip() for part in excerpts).rstrip() + "\n"
        fragments[fragment_id] = {
            "owner": spec["owner"],
            "sections": spec["sections"],
            "section_sha256": [sha256_text(part) for part in excerpts],
            "content": content,
        }

    return {
        "schema_version": 1,
        "authority": "derived-retrieval-cache-only",
        "canonical_rule": "Canonical Markdown owners always win. This file contains only verbatim hot-section excerpts.",
        "generated_by": "tools/build_chatgpt_load_pack.py",
        "fallback": "CHAT_INIT.md + task-specific canonical owners",
        "fragments": fragments,
        "profiles": PROFILES,
    }


def render_pack(pack: dict) -> str:
    return json.dumps(pack, ensure_ascii=False, indent=2, sort_keys=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if committed pack is stale")
    args = parser.parse_args()

    expected = build_pack()
    rendered = render_pack(expected)
    if args.check:
        if not OUTPUT.exists():
            raise SystemExit(f"missing generated load pack: {OUTPUT.relative_to(ROOT)}")
        current_text = OUTPUT.read_text(encoding="utf-8")
        try:
            current = json.loads(current_text)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"invalid CHATGPT_LOAD_PACK.json: {exc}") from exc
        if current != expected:
            canonical_current = render_pack(current)
            diff = "".join(
                difflib.unified_diff(
                    canonical_current.splitlines(keepends=True),
                    rendered.splitlines(keepends=True),
                    fromfile="committed/CHATGPT_LOAD_PACK.json",
                    tofile="generated/CHATGPT_LOAD_PACK.json",
                )
            )
            print(diff, end="")
            raise SystemExit(
                "CHATGPT_LOAD_PACK.json is stale; run "
                "python tools/build_chatgpt_load_pack.py and commit the result"
            )
        print("ChatGPT load pack: PASS")
        return 0

    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
