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
                "必須先讀並實際走 `RUNTIME_DRAW.md` 的 `Acquisition` capability gates",
                "取得 canonical source 本身不等於 acquisition complete",
                "GitHub Connect source acquisition、connector→Python byte-preserving handoff、Python materialization／execution 是三個獨立 capability",
                "MATERIALIZATION HANDOFF CAPABILITY GAP",
                "任何「已取得 canonical source／payload 已交給 Python」claim 都必須有本 session 可觀察 evidence",
                "不得用模型轉錄 source 補洞",
                "不得先轉 Web／manual fallback",
            ),
        ),
        (
            "RUNTIME_DRAW.md",
            (
                "Language-model generation ≠ random draw / cast",
                "Question Contract fixed",
                "Draw / Cast Fact fixed",
                "Free ChatGPT verified bounded capsule transport",
                "chunked-model-mediated-opaque-handoff-v2",
                "per-chunk exact verification",
                "chunk_retry_required_on_mismatch",
                "fresh same-commit capsule read",
                "index-ascending-concat",
                "encoded_size",
                "base64+zlib",
                "decoded_size",
                "decoded_sha256",
                "cache_locator_version = 4",
                "MATERIALIZATION HANDOFF CAPABILITY GAP",
                "Canonical Execution Identity",
                "inline Python",
                "`secrets`／`random`／手寫 modulo",
                "不得用模型重寫 implementation 來補洞",
            ),
        ),
        (
            "BEHAVIORAL_EVAL.md",
            (
                "verified chunked capsule v2 path",
                "逐 chunk 驗 `encoded_length` + `encoded_sha256`",
                "只重取該 failed chunk",
                "ascending reassembly／encoded_size",
                "final decode/size/SHA evidence",
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
                "GitHub Connect fetch same exact commit runtime/casting/CHATGPT_RUNTIME_CAPSULE.json",
                "schema_version = 2",
                "derived-transport-cache-only",
                "chunked-model-mediated-opaque-handoff-v2",
                "chunk_encoding = ascii",
                "encoded_length",
                "encoded_sha256",
                "chunk_retry_limit",
                "fresh same-commit capsule read",
                "index-ascending-concat",
                "encoded_size",
                "base64.b64decode(..., validate=True)",
                "zlib.decompress",
                "verify exact decoded byte count == decoded_size",
                "verify SHA-256 == manifest decoded_sha256",
                "cache_locator_version = 4",
                "MATERIALIZATION HANDOFF CAPABILITY GAP",
                "GitHub retrieval capability ≠ connector→Python byte-preserving handoff capability ≠ Python execution ≠ repository write authority",
            ),
        ),
        (
            "runtime/casting/CHATGPT_RUNTIME_CAPSULE.json",
            (
                '"schema_version":2',
                '"authority":"derived-transport-cache-only"',
                '"transport_contract":"chunked-model-mediated-opaque-handoff-v2"',
                '"automatic_object_bridge_required":false',
                '"must_attempt_when_python_available":true',
                '"same_turn_attempt_required":true',
                '"missing_automatic_bridge_is_not_gap":true',
                '"chunk_retry_required_on_mismatch":true',
                '"chunk_reassembly":"index-ascending-concat"',
                '"chunk_retry_limit":2',
                '"chunk_retry_source":"fresh-same-commit-capsule-read"',
                '"source_path":"runtime/casting/core.py"',
                '"payload_encoding":"base64+zlib"',
                '"chunk_encoding":"ascii"',
                '"chunk_count":',
                '"encoded_size":',
                '"decoded_size":',
                '"decoded_sha256":',
                '"chunks":[',
                '"encoded_length":',
                '"encoded_sha256":',
            ),
        ),
        (
            "BEHAVIORAL_EVAL.md",
            (
                "chunked `CHATGPT_RUNTIME_CAPSULE.json` v2",
                "只重取失敗 chunk並依 `chunk_retry_limit` bounded retry",
                "`index-ascending-concat`",
                "per-chunk／reassembly／final size-SHA",
            ),
        ),
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
