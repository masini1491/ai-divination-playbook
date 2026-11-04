"""Contract tests for independent Repo/MCP interpretation prompt packets.

Tests inspect *prompts only*, and never call or simulate two model runs.
"""
import copy
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = ROOT/"tools/build_mcp_interpretation_pair_packets.py"
spec = importlib.util.spec_from_file_location("interpretation_pair_packets", P)
packets = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = packets
spec.loader.exec_module(packets)
CASEBOOK, _ = packets.load_cases(packets.CASEBOOK)
PACK = json.loads(packets.POLICY_PACK.read_text(encoding="utf-8"))
MANIFEST = json.loads((ROOT/"integrations/chatgpt-mcp/source_manifest.json").read_text(encoding="utf-8"))


def candidate_policy_casebook():
    """Use frozen *synthetic* cases with exactly identical verified current owners.

    Only this in-memory evaluation request follows the generated policy source.
    The historical CASEBOOK file, its source pin and original facts remain intact.
    Production build_packets() still rejects any actual source disagreement.
    """
    source = PACK.get("source_commit")
    if not isinstance(source, str) or len(source) != 40 or any(c not in "0123456789abcdef" for c in source):
        raise ValueError("INVALID_CANDIDATE_SOURCE")
    if MANIFEST.get("commit") != source:
        raise ValueError("SOURCE_MANIFEST_MISMATCH")
    for name, expected_sha in CASEBOOK["policy_owner_digests"].items():
        owner = PACK.get("owners", {}).get(name, {})
        if not isinstance(owner, dict) or owner.get("sha256") != expected_sha:
            raise ValueError(f"POLICY_OWNER_DIGEST_MISMATCH:{name}")
        if not isinstance(owner.get("content"), str) or packets.digest(owner["content"]) != expected_sha:
            raise ValueError(f"POLICY_OWNER_CONTENT_MISMATCH:{name}")
    aligned = copy.deepcopy(CASEBOOK)
    aligned["policy_source_commit"] = source
    return aligned


CANDIDATE_CASEBOOK = candidate_policy_casebook()


class InterpretationPairedPacketTests(unittest.TestCase):
    def test_historical_source_mismatch_still_rejected(self):
        self.assertEqual(CASEBOOK["policy_source_commit"], "38898aec30668056459bb0551f77ba6e72f805d7")
        self.assertEqual(CANDIDATE_CASEBOOK["cases"], CASEBOOK["cases"])
        self.assertEqual(CANDIDATE_CASEBOOK["policy_owner_digests"], CASEBOOK["policy_owner_digests"])
        self.assertEqual(CANDIDATE_CASEBOOK["policy_source_commit"], PACK["source_commit"])
        if PACK["source_commit"] != CASEBOOK["policy_source_commit"]:
            with self.assertRaisesRegex(ValueError, "SOURCE_REVISION_MISMATCH"):
                packets.build_packets(CASEBOOK, PACK)

    def test_six_cases_two_independent_route_prompts(self):
        result = packets.build_packets(CANDIDATE_CASEBOOK, PACK)
        self.assertEqual(result["kind"], "PROMPTS_ONLY_NOT_MODEL_RESULTS")
        self.assertEqual(result["case_count"], 6)
        self.assertEqual(len(result["packets"]), 6)
        for case, record in zip(CASEBOOK["cases"], result["packets"]):
            with self.subTest(id=case["id"]):
                self.assertEqual(record["id"], case["id"])
                self.assertEqual(record["fixture_sha256"], packets.case_digest(case))
                self.assertIn(case["question"], record["repo"]["prompt"])
                self.assertIn(case["question"], record["mcp"]["prompt"])
                self.assertIn('get_interpretation_policy(', record["mcp"]["prompt"])
                self.assertIn("GitHub Connector", record["repo"]["prompt"])
                self.assertIn("INCONCLUSIVE", record["repo"]["prompt"])
                self.assertIn("INCONCLUSIVE", record["mcp"]["prompt"])
                self.assertIn("請勿抽牌、起卦", record["repo"]["prompt"])
                self.assertIn("請勿抽牌、起卦", record["mcp"]["prompt"])
                self.assertNotIn("get_interpretation_policy(", record["repo"]["prompt"])
                self.assertEqual(record["source_commit"], CANDIDATE_CASEBOOK["policy_source_commit"])
                self.assertEqual(record["repo"]["sha256"], packets.digest(record["repo"]["prompt"]))
                self.assertEqual(record["mcp"]["sha256"], packets.digest(record["mcp"]["prompt"]))
                for owner, sha in record["policy_owner_digests"].items():
                    self.assertEqual(sha, CASEBOOK["policy_owner_digests"][owner])
                    self.assertIn(sha, record["repo"]["prompt"])
                    self.assertIn(sha, record["mcp"]["prompt"])

    def test_identical_frozen_input_despite_distinct_route_instruction(self):
        result = packets.build_packets(CANDIDATE_CASEBOOK, PACK)
        anchor = "這是固定案例的塔羅／梅花／六爻象徵性解讀評測。"
        for item in result["packets"]:
            repo_body = item["repo"]["prompt"].split(anchor, 1)[1]
            mcp_body = item["mcp"]["prompt"].split(anchor, 1)[1]
            self.assertEqual(repo_body, mcp_body)
            self.assertEqual(
                packets.digest(anchor + repo_body),
                item["frozen_input_sha256"])

    def test_unknown_or_changed_policy_source_fails_closed(self):
        for mutation in (
            lambda x: x.update(source_commit="0"*40),
            lambda x: x["owners"]["TAROT.md"].update(sha256="0"*64),
            lambda x: x["owners"].pop("LIUYAO.md"),
        ):
            with self.subTest(mutation=str(mutation)):
                altered = copy.deepcopy(PACK)
                mutation(altered)
                with self.assertRaises(ValueError):
                    packets.build_packets(CANDIDATE_CASEBOOK, altered)

    def test_write_is_explicit_and_non_overwriting(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)/"paired"
            payload = packets.build_packets(CANDIDATE_CASEBOOK, PACK)
            written = packets.write_packets(payload, target)
            self.assertEqual(len(written), 13)
            self.assertTrue(all(x.is_file() for x in written))
            self.assertEqual(
                json.loads((target/"prompt_manifest.json").read_text(encoding="utf-8"))["kind"],
                "PROMPTS_ONLY_NOT_MODEL_RESULTS")
            with self.assertRaises(FileExistsError):
                packets.write_packets(payload, target)


if __name__ == "__main__":
    unittest.main()
