#!/usr/bin/env python3
"""Build audit-ready fixed-fact prompts for *independent* Repo/MCP model sessions.

Generates instructions and frozen inputs only. Never invokes a model, MCP
endpoint, or random casting engine, and never fabricates paired-run records.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.evaluate_mcp_interpretation_parity import load_cases

METHOD_OWNER = {"tarot": "TAROT.md", "meihua": "MEIHUA.md", "liuyao": "LIUYAO.md"}
REPOSITORY = "masini1491/ai-divination-playbook"
POLICY_PACK = ROOT / "integrations/chatgpt-mcp/policy_pack.json"
CASEBOOK = ROOT / "evals/mcp_interpretation_parity/cases.json"


def digest(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def case_digest(case: dict) -> str:
    return digest(json.dumps(case, sort_keys=True, ensure_ascii=False))


def verified_context(casebook: dict, pack: dict) -> None:
    """Fail closed if fixture policy is not the exact currently bundled release."""
    if pack.get("source_commit") != casebook.get("policy_source_commit"):
        raise ValueError("SOURCE_REVISION_MISMATCH")
    owners = pack.get("owners")
    if not isinstance(owners, dict):
        raise ValueError("INVALID_POLICY_PACK")
    for name, expected in casebook["policy_owner_digests"].items():
        owner = owners.get(name)
        if not isinstance(owner, dict) or not isinstance(owner.get("content"), str):
            raise ValueError(f"POLICY_OWNER_MISSING:{name}")
        content = owner["content"]
        if digest(content) != expected or owner.get("sha256") != expected:
            raise ValueError(f"POLICY_OWNER_DIGEST_MISMATCH:{name}")


def build_packets(casebook: dict, pack: dict) -> dict:
    verified_context(casebook, pack)
    commit = casebook["policy_source_commit"]
    packets = []
    for case in casebook["cases"]:
        name = METHOD_OWNER[case["method"]]
        owners = {n: casebook["policy_owner_digests"][n]
                  for n in (name, "CHATGPT_OUTPUT.md")}
        frozen_input = (
            "這是固定案例的塔羅／梅花／六爻象徵性解讀評測。請勿抽牌、起卦、"
            "重算成另一份隨機結果、猜測未提供的現實資料或沿用其他對話的占卜。\n"
            "請在取用下列兩份正式規則並核對原始 SHA-256 後，才依固定原題解讀："
            + "、".join(owners) + "。\n"
            "任何規則、來源、固定案例或所需方法事實無法確認，"
            "請回覆 INCONCLUSIVE 並指出缺失，不要補造資料。\n"
            "先回答原題，再提供最低充分的牌面／卦象證據、限制與不確定性；"
            "不要推導客觀百分比或保證結果。"
            "本次只產生一個主結論，不評斷已排除事項。\n"
            "固定測試案例（兩路徑完全相同，不要修改）：\n"
            + json.dumps({
                "id": case["id"], "method": case["method"], "question": case["question"],
                "contract": case["contract"], "facts": case["facts"],
            }, ensure_ascii=False, indent=2)
            + "\n"
            "評測時請在最後列出實際使用的規則文件及來源 Commit；"
            "不要自行宣稱兩路徑已等價，也不要填寫審核 PASS／FAIL。"
        )
        identity = (
            f"Repository: {REPOSITORY}\n"
            f"固定來源 Commit: {commit}\n"
            + "\n".join(f"規則檔案 {owner} SHA-256: {sha}" for owner, sha in owners.items())
        )
        repo_instructions = (
            "路徑：Repo。使用 GitHub Connector 取得以下 repository 與固定 Commit "
            "所指定的兩份正式 Markdown 原始文件全文，不得使用浮動 main、記憶或"
            " MCP 封裝文本代替 GitHub Connector。"
            "取得後依 UTF-8 計算 SHA-256 與下面期望值比較。"
            " 若 Connector 無法實際取到該版本，回覆 INCONCLUSIVE；不得假裝已讀取。\n"
            + identity + "\n\n"
        )
        mcp_instructions = (
            "路徑：MCP。使用已連接的 AI Divination Private – Git Sync "
            "之 get_interpretation_policy(method, owner, offset, max_chars) "
            "讀取該方法專屬規則與 CHATGPT_OUTPUT.md；遵照 next_offset "
            "將每個 owner 的完整分段文本重組、驗證 UTF-8 SHA-256、"
            " 同一來源 Commit 與一致的 owner identity。"
            "不得以 Production 的舊版工具、另一個外掛、GitHub Connector "
            "或臆測文本取代正式 MCP 呼叫。若工具不存在或不能回應，回覆 "
            "INCONCLUSIVE 並指出版本限制；不得假裝新版已上線。\n"
            + identity + "\n\n"
        )
        repo_prompt = repo_instructions + frozen_input
        mcp_prompt = mcp_instructions + frozen_input
        packets.append({
            "id": case["id"],
            "method": case["method"],
            "fixture_sha256": case_digest(case),
            "source_commit": commit,
            "policy_owner_digests": owners,
            "frozen_input_sha256": digest(frozen_input),
            "repo": {"prompt": repo_prompt, "sha256": digest(repo_prompt)},
            "mcp": {"prompt": mcp_prompt, "sha256": digest(mcp_prompt)},
        })
    return {"schema_version": 1, "kind": "PROMPTS_ONLY_NOT_MODEL_RESULTS",
            "source_repository": REPOSITORY, "source_commit": commit,
            "case_count": len(packets), "packets": packets}


def write_packets(data: dict, target: Path) -> list[Path]:
    """No overwrite or hidden writes; caller chooses an output directory."""
    if target.exists() and any(target.iterdir()):
        raise FileExistsError("OUTPUT_DIRECTORY_NOT_EMPTY")
    target.mkdir(parents=True, exist_ok=True)
    written = []
    for packet in data["packets"]:
        for route in ("repo", "mcp"):
            file = target / f'{packet["id"]}.{route}.txt'
            file.write_text(packet[route]["prompt"] + "\n", encoding="utf-8")
            written.append(file)
    manifest = target / "prompt_manifest.json"
    manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    written.append(manifest)
    return written


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--cases", type=Path, default=CASEBOOK)
    p.add_argument("--policy-pack", type=Path, default=POLICY_PACK)
    p.add_argument("--output-dir", type=Path, required=True)
    args = p.parse_args()
    casebook, _ = load_cases(args.cases)
    pack = json.loads(args.policy_pack.read_text(encoding="utf-8"))
    result = build_packets(casebook, pack)
    outputs = write_packets(result, args.output_dir)
    print(json.dumps({"status": "PROMPTS_GENERATED_NOT_EXECUTED",
                      "source_commit": result["source_commit"],
                      "case_count": result["case_count"], "files": len(outputs)},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
