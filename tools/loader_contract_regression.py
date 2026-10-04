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
                "AI 代抽／代起才進 `RUNTIME_DRAW.md`",
                "cache/acquisition/materialization/handoff細節只由該 owner決定",
                "language-model generation ≠ Runtime fact",
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
                "Current GitHub repository authority is **GitHub Connect-only**",
                "bootstrap／access／freshness細節由 `CHAT_INIT.md` 擁有",
                "required connector authority無法建立時 fail closed",
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
                "Identity-First Refresh｜合法 refresh trigger 成立後仍先比 runtime identity",
                "Refresh trigger成立 ≠ 必須重新 materialize",
                "compare cached runtime_source_commit ... current HEAD",
                "MUST NOT",
                "rematerialize only on material runtime identity change",
            ),
        )
    ],
    "TAROT-BEH-028": [
        (
            "RUNTIME_DRAW.md",
            (
                "Runtime Hot Path｜stochastic first-view recovery",
                "MISS ≠ unavailable",
                "Cold-start Recovery Gate｜Free ChatGPT 首次不可過早判 unavailable",
                "runtime.draw.materialization_contract",
                "core.execute_stochastic()",
            ),
        ),
        (
            "PLAYBOOK_INDEX.json",
            (
                '"id": "runtime.draw"',
                '"materialization_contract": "RUNTIME_DRAW.md"',
                '"cold_start_recovery_section": "Cold-start Recovery Gate"',
            ),
        ),
        (
            "CHATGPT_LOAD_PACK.json",
            (
                "Runtime Hot Path｜stochastic first-view recovery",
                "MISS ≠ unavailable",
                "Cold-start Recovery Gate",
            ),
        ),
        (
            "BEHAVIORAL_EVAL.md",
            (
                "TAROT-BEH-028 — Free ChatGPT cold-start discovers stochastic recovery before manual fallback",
                "cache MISS／import FAIL後未讀 recovery owner就宣告 runtime unavailable",
                "core.execute_stochastic()",
            ),
        ),
    ],
    "TAROT-BEH-029": [
        (
            "RUNTIME_DRAW.md",
            (
                "Free ChatGPT streaming capsule transport v3",
                "streaming-model-mediated-opaque-handoff-v3",
                "one fetch = one chunk",
                "verify encoded_length + encoded_sha256 immediately",
                "v2 compatibility fallback",
            ),
        ),
        (
            "PLAYBOOK_INDEX.json",
            (
                '"preferred_free_chatgpt_transport": "runtime/casting/capsule-v3/MANIFEST.json"',
                '"preferred_free_chatgpt_transport_contract": "streaming-model-mediated-opaque-handoff-v3"',
                '"compatibility_transport": "runtime/casting/CHATGPT_RUNTIME_CAPSULE.json"',
            ),
        ),
        (
            "runtime/casting/capsule-v3/MANIFEST.json",
            (
                '"schema_version":3',
                '"transport_contract":"streaming-model-mediated-opaque-handoff-v3"',
                '"streaming_fetch":"one-chunk-file-at-a-time"',
                '"verify_before_next_fetch":true',
                '"decoded_sha256":',
            ),
        ),
        (
            "BEHAVIORAL_EVAL.md",
            (
                "TAROT-BEH-029 — Streaming capsule v3 verifies each chunk before next fetch",
                "每次只 fetch一個 `chunk-XX.txt`",
                "final decoded SHA未通過仍執行抽牌",
            ),
        ),
    ],
    "TAROT-BEH-030": [
        (
            "RUNTIME_DRAW.md",
            (
                "source readable but not directly executable",
                "runtime.draw.materialization_contract",
                "Source readable but not directly executable",
                "Cold-start Recovery Gate",
            ),
        ),
        (
            "PLAYBOOK_INDEX.json",
            (
                '"id": "method.tarot"',
                '"stochastic_runtime": "runtime.draw"',
                '"casting_entrypoint": "core.execute_stochastic"',
                '"id": "method.meihua"',
                '"id": "method.liuyao"',
            ),
        ),
        (
            "CHATGPT_LOAD_PACK.json",
            (
                "source readable but not directly executable",
                "runtime.draw.materialization_contract",
                "stochastic_capability_gap_followup",
            ),
        ),
        (
            "BEHAVIORAL_EVAL.md",
            (
                "TAROT-BEH-030 — Direct-execution miss must continue into stochastic materialization",
                "source readable but not directly executable",
                "未 resolve `runtime.draw.materialization_contract` 就要求使用者自行抽牌／擲幣",
            ),
        ),
    ],
    "TAROT-BEH-031": [
        (
            "RUNTIME_DRAW.md",
            (
                "ordinary ChatGPT: /api/cast = unavailable-by-policy; DO NOT probe",
                "unavailable-by-policy",
                "DO NOT probe",
                "capsule-v3",
            ),
        ),
        (
            "PLAYBOOK_INDEX.json",
            (
                '"ordinary_chat_project_http_api": "unavailable-by-policy"',
                '"ordinary_chat_http_probe": "forbidden"',
                '"natural_entry_product_scenario": "evals/FREE_CHATGPT_STOCHASTIC_NATURAL_ENTRY_PRODUCT_SCENARIO.md"',
            ),
        ),
        (
            "CHATGPT_LOAD_PACK.json",
            (
                "ordinary ChatGPT: /api/cast = unavailable-by-policy; DO NOT probe",
                "unavailable-by-policy",
                "runtime.draw.materialization_contract",
            ),
        ),
        (
            "runtime/casting/API.md",
            (
                "不是 ordinary ChatGPT 代抽／代起卦的 admitted execution route",
                "ordinary ChatGPT MUST NOT probe",
                "RUNTIME_DRAW.md",
            ),
        ),
        (
            "BEHAVIORAL_EVAL.md",
            (
                "TAROT-BEH-031 — Natural ChatGPT entry must bypass project HTTP API",
                "用 repo 直接實抽",
                "production casting API",
            ),
        ),
        (
            "evals/FREE_CHATGPT_STOCHASTIC_NATURAL_ENTRY_PRODUCT_SCENARIO.md",
            (
                "用 repo 直接實抽",
                "MUST NOT probe",
                "core.execute_stochastic()",
            ),
        ),
    ],
    "TAROT-BEH-032": [
        (
            "RUNTIME_DRAW.md",
            (
                "connector read-only / cannot execute source ≠ host Python unavailable",
                "Forbidden Python-unavailability inference",
                "current-host capability evidence",
                "preferred capsule-v3",
            ),
        ),
        (
            "PLAYBOOK_INDEX.json",
            (
                '"connector_execution_miss_is_not_python_unavailable": true',
                '"python_unavailability_evidence_policy": "current-host-capability-evidence-only"',
                '"python_available_action": "same-turn-attempt-runtime.draw.materialization_contract-prefer-capsule-v3"',
            ),
        ),
        (
            "CHATGPT_LOAD_PACK.json",
            (
                "connector read-only / cannot execute source ≠ host Python unavailable",
                "current-host capability evidence",
                "runtime.draw.materialization_contract",
            ),
        ),
        (
            "BEHAVIORAL_EVAL.md",
            (
                "TAROT-BEH-032 — Connector execution limits must not masquerade as host-Python unavailability",
                "GitHub Connect不能執行 Python，因此我不能起卦／抽牌",
                "workflow dispatch",
            ),
        ),
        (
            "evals/FREE_CHATGPT_STOCHASTIC_NATURAL_ENTRY_PRODUCT_SCENARIO.md",
            (
                "Resolve host Python capability independently from GitHub Connect capability",
                "missing workflow dispatch",
                "same-conversation/session verified canonical Python execution",
            ),
        ),
    ],
    "TAROT-BEH-025": [
        (
            "MEIHUA_MATERIALIZATION.md",
            (
                "materialized_source_commit",
                "last_checked_repository_head",
                "Identity-first deterministic refresh",
                "tools/meihua_engine.py",
                "MUST NOT fetch bundle / rematerialize",
            ),
        ),
        (
            "LIUYAO_MATERIALIZATION.md",
            (
                "materialized_source_commit",
                "last_checked_repository_head",
                "Identity-first deterministic refresh",
                "tools/liuyao_calendar.py",
                "tools/liuyao_engine.py",
                "tools/liuyao_runtime.py",
                "current HEAD與 `materialized_source_commit` 不同本身不是 MISS",
            ),
        ),
        (
            "BEHAVIORAL_EVAL.md",
            (
                "TAROT-BEH-025 — Deterministic tool cache reuse forbids redundant rematerialization",
                "owned source paths全部 unchanged",
                "不得重新 fetch bundle、rematerialize或跑完整 acquisition",
            ),
        ),
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
                "Astrology 不參與 ordinary auto-routing",
                "ASTROLOGY_NATAL.md",
                "ASTROLOGY_TRANSIT.md",
                "不得因 provider unavailable 就偷偷改用 Tarot / Meihua / Liuyao",
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
    "TAROT-BEH-022": [
        (
            "CHAT_INIT.md",
            (
                "Shared Development Playbook Activation Gate｜共通上位規則啟用條件",
                "ordinary use → **project-native; no extra load**",
                "maintenance / governance / GitHub / validation → resolve baseline exact",
            ),
        ),
        (
            "tools/build_chatgpt_load_pack.py",
            (
                "## Shared Development Playbook Activation Gate｜共通上位規則啟用條件",
            ),
        ),
        (
            "CHATGPT_LOAD_PACK.json",
            (
                "Shared Development Playbook Activation Gate｜共通上位規則啟用條件",
                "ordinary use → **project-native; no extra load**",
            ),
        ),
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
