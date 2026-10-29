"""Plan and execution safety tests with no extra stochastic operations."""
import copy
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

BASE=Path(__file__).resolve().parents[2]/"integrations"/"chatgpt-mcp"
sys.path.insert(0,str(BASE))
from chunk_plan import plan_chunks, _digest
from batch_cast import execute_batch
from test_batch_cast import FakeBridge, mixed_twelve


class ChunkPlanTests(unittest.TestCase):
    def test_twelve_interleaved_methods_split_in_acknowledgeable_groups(self):
        items=mixed_twelve()
        with patch("batch_cast.secrets.token_hex", side_effect=AssertionError("NO RNG DURING PLAN")):
            plan=plan_chunks(items)
        self.assertEqual(plan["status"],"planned_no_cast")
        self.assertEqual(plan["total_items"],12)
        self.assertEqual(plan["chunk_count"],4)
        self.assertEqual([len(x["items"]) for x in plan["chunks"]],[3]*4)
        self.assertEqual([x["label"] for c in plan["chunks"] for x in c["items"]],
                         [x["label"] for x in items])
        self.assertEqual([x["method_override"] for c in plan["chunks"] for x in c["items"]],
                         [x["method_override"] for x in items])
        self.assertTrue(all(c["request_sha256"]==_digest(c["items"]) for c in plan["chunks"]))
        self.assertEqual(plan["plan_sha256"],_digest([x for c in plan["chunks"] for x in c["items"]]))
        self.assertIn("STOP",plan["instructions"])
        self.assertIn("do NOT automatically retry",plan["instructions"])

    def test_chunked_execution_yields_all_twelve_without_duplication(self):
        plan=plan_chunks(mixed_twelve(),chunk_size=2)
        engine=FakeBridge()
        outputs=[execute_batch(c["items"],lambda:engine) for c in plan["chunks"]]
        self.assertEqual([o["completed_count"] for o in outputs],[2]*6)
        receipts=[r for o in outputs for r in o["receipts"]]
        self.assertEqual(len(receipts),12)
        self.assertEqual(len({r["receipt_id"] for r in receipts}),12)
        self.assertEqual(len({o["batch_id"] for o in outputs}),6)
        self.assertEqual([r["selected_method"] for r in receipts],
                         [x["method_override"] for x in mixed_twelve()])

    def test_preflight_all_items_and_valid_chunk_size(self):
        for size in (0,5,True,1.5,"3"):
            with self.subTest(size=size),self.assertRaises(ValueError):
                plan_chunks(mixed_twelve(),chunk_size=size)
        for invalid in ([],mixed_twelve()+[mixed_twelve()[0]]):
            with self.assertRaises(ValueError):
                plan_chunks(invalid)
        bad=copy.deepcopy(mixed_twelve());bad[10]["label"]="R00"
        with self.assertRaises(ValueError):
            plan_chunks(bad)

    def test_failure_only_current_chunk_can_be_ambiguous(self):
        plan=plan_chunks(mixed_twelve(),chunk_size=3)
        ok=FakeBridge()
        first=execute_batch(plan["chunks"][0]["items"],lambda:ok)
        self.assertEqual(first["completed_count"],3)
        failure=FakeBridge(fail_on=2)
        second=execute_batch(plan["chunks"][1]["items"],lambda:failure)
        self.assertEqual(second["status"],"partial_failure")
        self.assertEqual(second["completed_count"],1)
        self.assertEqual([r["label"] for r in first["receipts"]],["R00","R01","R02"])
        self.assertEqual([r["label"] for r in second["receipts"]],["R03"])
        self.assertEqual([r["label"] for r in first["receipts"]],
                         ["R00","R01","R02"])
        self.assertEqual(len(ok.calls),3)
        self.assertEqual(len(failure.calls),2)

if __name__=="__main__":
    unittest.main()
