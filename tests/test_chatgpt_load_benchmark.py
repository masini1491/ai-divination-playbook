from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ChatGPTLoadBenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.benchmark = load_module(
            ROOT / "tools" / "chatgpt_load_benchmark.py",
            "chatgpt_load_benchmark",
        )

    def test_all_loader_budgets_pass(self):
        report = self.benchmark.evaluate(ROOT)
        self.assertTrue(report["pass"], report)

    def test_primary_ordinary_profiles_reduce_reads(self):
        report = self.benchmark.evaluate(ROOT)
        for name in ("ordinary_tarot", "ordinary_meihua", "ordinary_liuyao"):
            result = report["profiles"][name]
            self.assertLess(
                result["optimized"]["file_reads"],
                result["baseline"]["file_reads"],
            )
            self.assertLess(
                result["optimized"]["payload_bytes"],
                result["baseline"]["payload_bytes"],
            )

    def test_benchmark_does_not_claim_wall_clock_latency(self):
        report = self.benchmark.evaluate(ROOT)
        self.assertFalse(report["wall_clock_claim"])
        self.assertTrue(report["head_probe_excluded"])


if __name__ == "__main__":
    unittest.main()
