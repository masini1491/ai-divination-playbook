#!/usr/bin/env python3
"""Deterministic contract-surface regression for loader-related behavioral scenarios.

This checks that canonical owners still contain the policy clauses required by the
selected loader regression scenarios. It is stronger than scenario-ID selection,
but it is NOT a product-level fresh-chat behavioral execution.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "evals" / "regression_matrix.json"
CHANGE_CLASS = "loader-optimization"

CONTRACTS: dict[str, list[tuple[str, tuple[str, ...]]]] = {
    "TAROT-BEH-001": [
        (
            "CHAT_INIT.md",
            (
                "使用者可以直接以自然語言提問",
                "ordinary reading, method unspecified",
                "METHOD_ROUTING.md Fast Path",
            ),
        )
    ],
    "TAROT-BEH-002": [
        (
            "CHAT_INIT.md",
            (
                "ordinary reading, method unspecified",
                "Astrology v1 是 explicit-request only",
            ),
        ),
        (
            "METHOD_ROUTING.md",
            (
                "Fast Path｜高信心命中就停止 routing",
                "Tarot",
                "Meihua",
                "Liuyao",
            ),
        ),
    ],
    "TAROT-BEH-003": [
        (
            "CHAT_INIT.md",
            (
                "Language-model generation ≠ Runtime Draw / Cast",
                "actual canonical runtime execution",
                "Draw / Cast Fact fixed",
            ),
        ),
        (
            "AGENTS.md",
            (
                "fixed-cache probe FAIL／首次 acquisition",
                "必須先讀並實際嘗試 `RUNTIME_DRAW.md` 的 `Acquisition` admitted path",
                "取得 canonical source 本身不等於 acquisition complete",
                "connector payload → decode/write → hash／marker verify → import／CLI execute",
                "不得僅因 connector 與 Python capability 分離",
                "任何「已取得 canonical source」claim 必須有本 session 可觀察的 connector retrieval evidence",
                "不得先轉 Web／manual fallback",
                "要求使用者自行提供 Tarot／Meihua／Liuyao 隨機結果",
            ),
        ),
        (
            "RUNTIME_DRAW.md",
            (
                "Language-model generation ≠ random draw / cast",
                "Question Contract fixed",
                "Draw / Cast Fact fixed",
                "GitHub Connect base64 → Python decode",
                "不得只因 connector 與 Python 是不同 capability",
                "Canonical Execution Identity",
                "inline Python",
                "`secrets`／`random`／手寫 modulo",
                "不得用模型重寫 implementation 來補洞",
            ),
        ),
    ],
    "TAROT-BEH-005": [
        (
            "CHAT_INIT.md",
            (
                "Pre-Retrieval Transport Gate",
                "在第一次 **current GitHub repository-content read**",
                "先確認 GitHub connector / GitHub Connect capability",
                "不得聲稱已確認目前 Repo／首頁／最新版規則",
                "只有成功的 GitHub connector retrieval 才能建立 current GitHub repository-content authority",
                "GitHub public HTML",
                "URL preview／snippet",
                "generic Web search",
                "raw URL",
                "ACCESS BLOCKED",
            ),
        ),
        (
            "AGENTS.md",
            (
                "Pre-retrieval invariant",
                "before any current GitHub repository-content claim",
                "GitHub connector capability must be established",
                "不能 bootstrap 或驗證 current repo authority",
                "不得先引用、摘要或聲稱已確認 alternate transport 所見的 Repo 規則",
                "ACCESS BLOCKED",
            ),
        ),
    ],
    "TAROT-BEH-006": [
        (
            "RUNTIME_DRAW.md",
            (
                "GitHub Connect acquire exact revision runtime/casting/randomizer.py",
                "GitHub Connect base64 → Python decode",
                "base64.b64decode",
                "GitHub retrieval capability ≠ Python execution ≠ repository write authority",
                "cache_locator_version\":3",
                "runtime_source_repository\":\"masini1491/ai-divination-playbook",
            ),
        )
    ],
    "TAROT-BEH-012": [
        (
            "RUNTIME_DRAW.md",
            (
                "PASS 後：",
                "不抓 GitHub、不重新 materialize、不跑 full smoke",
                "Playbook HEAD 更新本身不是 Randomizer refresh trigger",
                "Fresh question means fresh RNG, not fresh program acquisition",
            ),
        )
    ],
    "TAROT-BEH-013": [
        (
            "CHAT_INIT.md",
            (
                "Playbook Freshness Probe｜只在 material trigger",
                "cheap HEAD/ref probe",
                "bounded diff",
                "時間經過本身不是 trigger",
            ),
        )
    ],
    "TAROT-BEH-016": [
        (
            "CHAT_INIT.md",
            (
                "explicit production Astrology",
                "ASTROLOGY.md",
                "raw birth data 不授權模型自行手算",
            ),
        ),
        (
            "ASTROLOGY.md",
            (
                "PRODUCTION V1 / EXPLICIT-REQUEST ONLY",
                "Astrology **不參與 ordinary auto-routing**",
                "若使用者明確指定 Astrology，不得因 provider unavailable 就偷偷改用 Tarot / Meihua / Liuyao",
            ),
        ),
    ],
    "TAROT-BEH-017": [
        (
            "ASTROLOGY.md",
            (
                "raw birth data",
                "model freehand calculation",
                "pretend verified chart",
                "admitted deterministic provider output",
                "user-supplied structured chart/export",
            ),
        )
    ],
    "TAROT-BEH-018": [
        (
            "RESEARCH_ROUTING.md",
            (
                "Astrology production reading 不屬於這個 gate",
                "explicit research intent",
                "named research README / owner",
                "不得因使用者明確指定 research task，又先把問題改寫成 production",
            ),
        ),
        (
            "references/astrology/README.md",
            (
                "REFERENCE-ONLY / RESEARCH V1 COMPLETE",
                "Production 與 research intent 明確分流",
                "Astrology Production v1 仍是 **explicit-request only**",
            ),
        ),
    ],
}


def selected_scenarios(root: Path = ROOT) -> list[str]:
    matrix = json.loads((root / "evals" / "regression_matrix.json").read_text(encoding="utf-8"))
    return list(matrix["change_classes"][CHANGE_CLASS])


def validate(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    selected = selected_scenarios(root)
    missing_contracts = sorted(set(selected) - set(CONTRACTS))
    extra_contracts = sorted(set(CONTRACTS) - set(selected))
    if missing_contracts:
        errors.append("selected scenarios missing deterministic contract checks: " + ", ".join(missing_contracts))
    if extra_contracts:
        errors.append("deterministic contract checks not selected by loader matrix: " + ", ".join(extra_contracts))

    for scenario_id in selected:
        checks = CONTRACTS.get(scenario_id, [])
        for relative, needles in checks:
            path = root / relative
            if not path.is_file():
                errors.append(f"{scenario_id}: missing owner {relative}")
                continue
            text = path.read_text(encoding="utf-8")
            for needle in needles:
                if needle not in text:
                    errors.append(f"{scenario_id}: {relative} missing required clause {needle!r}")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1
    for scenario_id in selected_scenarios():
        print(f"PASS CONTRACT {scenario_id}")
    print("Loader deterministic contract regression: PASS")
    print("product_fresh_chat_executed: false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
