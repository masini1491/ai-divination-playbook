#!/usr/bin/env python3
"""Validate strict P2/P4 loader closure claims.

P2 strict closure requires generated bounded ranges. P4 strict closure requires both
repository deterministic contract regression and actual fresh/bounded product run records.
The script never upgrades deterministic repository checks into product-behavior evidence.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "evals" / "loader_product_fresh_chat_manifest.json"
MATRIX = ROOT / "evals" / "regression_matrix.json"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def validate(root: Path = ROOT, *, require_product_evidence: bool = False) -> list[str]:
    errors: list[str] = []

    range_generator = load_module(root / "tools" / "build_loader_ranges.py", "build_loader_ranges")
    contract_runner = load_module(root / "tools" / "loader_contract_regression.py", "loader_contract_regression")
    behavioral = load_module(root / "tools" / "behavioral_eval.py", "behavioral_eval")

    errors.extend(f"P2: {error}" for error in range_generator.validate_generated(root))
    errors.extend(f"P4 deterministic: {error}" for error in contract_runner.validate(root))

    manifest_path = root / "evals" / "loader_product_fresh_chat_manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        matrix = json.loads((root / "evals" / "regression_matrix.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return errors + [f"P4 product manifest: {exc}"]

    required = manifest.get("required_scenarios")
    expected = matrix.get("change_classes", {}).get("loader-optimization")
    if required != expected:
        errors.append("P4 product manifest required_scenarios must exactly match loader-optimization matrix order")

    evidence_files = manifest.get("evidence_files")
    if not isinstance(evidence_files, list) or not all(isinstance(item, str) and item for item in evidence_files):
        errors.append("P4 product manifest evidence_files must be a list of non-empty paths")
        evidence_files = []

    records = []
    for relative in evidence_files:
        path = root / relative
        try:
            record = behavioral.load_record(path)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            errors.append(f"P4 product evidence {relative}: {exc}")
            continue
        for error in behavioral.validate_record(record):
            errors.append(f"P4 product evidence {relative}: {error}")
        records.append(record)

    product_executed = bool(manifest.get("product_fresh_chat_executed"))
    strict_complete = bool(manifest.get("strict_p4_complete"))

    if records:
        scenario_ids = [record.get("scenario_id") for record in records]
        classifications = [record.get("classification") for record in records]
        run_kinds = [record.get("run_kind", "formal") for record in records]
        shas = {record.get("playbook_sha") for record in records}
        if scenario_ids != required:
            errors.append("P4 product evidence must cover each required scenario exactly once in manifest order")
        if any(value != "PASS" for value in classifications):
            errors.append("P4 product evidence contains FAIL or INCONCLUSIVE classification")
        if any(value != "formal" for value in run_kinds):
            errors.append("P4 strict evidence requires formal run records")
        if len(shas) != 1:
            errors.append("P4 product evidence must use one fixed Playbook SHA")
        manifest_sha = manifest.get("playbook_sha")
        if len(shas) == 1 and manifest_sha != next(iter(shas)):
            errors.append("P4 product manifest playbook_sha must equal evidence Playbook SHA")

    evidence_complete = (
        bool(records)
        and required is not None
        and [record.get("scenario_id") for record in records] == required
        and all(record.get("classification") == "PASS" for record in records)
        and all(record.get("run_kind", "formal") == "formal" for record in records)
        and len({record.get("playbook_sha") for record in records}) == 1
    )

    if strict_complete != evidence_complete:
        errors.append("strict_p4_complete must exactly reflect validated fresh-chat evidence completeness")
    if product_executed != bool(records):
        errors.append("product_fresh_chat_executed must exactly reflect presence of product run records")
    if require_product_evidence and not evidence_complete:
        errors.append("P4 strict closure requires complete fresh/bounded product evidence")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--require-product-evidence",
        action="store_true",
        help="fail unless strict fresh/bounded product evidence is complete",
    )
    args = parser.parse_args()
    errors = validate(require_product_evidence=args.require_product_evidence)
    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    print("P2 generated locator closure: PASS")
    print("P4 deterministic repository closure: PASS")
    print(f"product_fresh_chat_executed: {str(manifest['product_fresh_chat_executed']).lower()}")
    print(f"strict_p4_complete: {str(manifest['strict_p4_complete']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
