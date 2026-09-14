#!/usr/bin/env python3
"""Estimate ChatGPT repository-loading cost against a recorded pre-loader baseline.

This intentionally measures deterministic repository payload proxies, not network or
model wall-clock latency.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "evals" / "chatgpt_load_budget.json"


def path_bytes(root: Path, paths: list[str]) -> int:
    total = 0
    for relative in paths:
        path = root / relative
        if not path.is_file():
            raise FileNotFoundError(f"missing benchmark path: {relative}")
        total += len(path.read_bytes())
    return total


def evaluate(root: Path = ROOT, config_path: Path = DEFAULT_CONFIG) -> dict:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    results = {}
    overall_pass = True

    for name, spec in config["profiles"].items():
        baseline = spec["baseline"]
        optimized_paths = spec["optimized_paths"]
        optimized_bytes = path_bytes(root, optimized_paths)
        optimized_reads = len(optimized_paths)
        baseline_bytes = baseline["payload_bytes"]
        baseline_reads = baseline["file_reads"]
        ratio = optimized_bytes / baseline_bytes if baseline_bytes else 1.0

        checks = {
            "file_reads": optimized_reads <= spec["max_optimized_file_reads"],
            "payload_ratio": ratio <= spec["max_payload_ratio"],
            "no_read_regression": optimized_reads <= baseline_reads,
            "no_payload_regression": optimized_bytes <= baseline_bytes,
        }
        profile_pass = all(checks.values())
        overall_pass = overall_pass and profile_pass

        results[name] = {
            "baseline": {
                "file_reads": baseline_reads,
                "payload_bytes": baseline_bytes,
            },
            "optimized": {
                "file_reads": optimized_reads,
                "payload_bytes": optimized_bytes,
                "paths": optimized_paths,
            },
            "payload_ratio": round(ratio, 4),
            "reduction": {
                "file_reads": baseline_reads - optimized_reads,
                "payload_bytes": baseline_bytes - optimized_bytes,
            },
            "checks": checks,
            "pass": profile_pass,
        }

    return {
        "metric": config["metric"],
        "baseline_revision": config["baseline_revision"],
        "head_probe_excluded": True,
        "wall_clock_claim": False,
        "profiles": results,
        "pass": overall_pass,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="exit nonzero when a budget fails")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of a compact table")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    args = parser.parse_args()

    report = evaluate(config_path=args.config)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("profile\treads before→after\tbytes before→after\tratio\tstatus")
        for name, result in report["profiles"].items():
            before = result["baseline"]
            after = result["optimized"]
            status = "PASS" if result["pass"] else "FAIL"
            print(
                f"{name}\t{before['file_reads']}→{after['file_reads']}\t"
                f"{before['payload_bytes']}→{after['payload_bytes']}\t"
                f"{result['payload_ratio']:.4f}\t{status}"
            )
        print("ChatGPT load budget:", "PASS" if report["pass"] else "FAIL")

    if args.check and not report["pass"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
