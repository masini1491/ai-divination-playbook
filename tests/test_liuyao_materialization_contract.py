from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
OWNER = ROOT / "LIUYAO.md"
MATERIALIZATION = ROOT / "LIUYAO_MATERIALIZATION.md"


class LiuyaoMaterializationContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.owner = OWNER.read_text(encoding="utf-8")
        self.materialization = MATERIALIZATION.read_text(encoding="utf-8")

    def test_hot_owner_routes_local_miss_to_task_specific_contract(self) -> None:
        self.assertIn("LIUYAO_MATERIALIZATION.md", self.owner)
        self.assertIn(
            "Local deterministic-tool miss ≠ deterministic source unavailable",
            self.owner,
        )
        self.assertIn(
            "local file/cache miss 不能直接觸發本節",
            self.owner,
        )

    def test_canonical_deterministic_tools_are_named(self) -> None:
        for relative in (
            "tools/liuyao_calendar.py",
            "tools/liuyao_engine.py",
            "tools/liuyao_runtime.py",
        ):
            self.assertIn(relative, self.materialization)
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_exact_commit_and_byte_identity_are_required(self) -> None:
        required = (
            "same Playbook revision to exact commit",
            "byte-for-byte",
            "GitHub canonical blob identity",
            "hash / blob identity 未 PASS 前不得 import 或執行",
        )
        for phrase in required:
            self.assertIn(phrase, self.materialization)

    def test_original_cast_must_survive_recovery(self) -> None:
        self.assertIn(
            "deterministic recovery 使用**原起卦時間**與原 Raw Cast，不得另取現在時間、不重抽、不重卦",
            self.owner,
        )
        self.assertIn("保留原 cast_timestamp", self.materialization)

    def test_unavailable_requires_exhausted_materialization_paths(self) -> None:
        self.assertIn(
            "admitted materialization/execution paths exhausted + structural engine unavailable",
            self.owner,
        )
        self.assertIn(
            "只有以下情況才可把 deterministic layer 判定為 unavailable",
            self.materialization,
        )
        self.assertIn(
            "記錄實際 acquisition / verification / execution gap",
            self.owner,
        )


if __name__ == "__main__":
    unittest.main()
