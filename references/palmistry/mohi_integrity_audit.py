from __future__ import annotations

from pathlib import Path
import argparse
import csv
import hashlib
import io
import json
import zipfile
from collections import defaultdict

ZIP_DEFAULT = Path(r"C:\Users\user\Documents\X\MOHI_sample_10p_3s_5i.zip")
RESULT_DEFAULT = Path(r"C:\Users\user\Documents\X\MOHI_repeatability_results.json")
OUT_DEFAULT = Path(r"C:\Users\user\Documents\X\MOHI_integrity_audit.json")

METRIC_KEYS = (
    "anchor_mean",
    "anchor_max",
    "angle_deg",
    "width_rel",
    "height_rel",
    "canonical_mean",
    "canonical_max",
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_manifest(zf: zipfile.ZipFile):
    if "manifest.tsv" not in zf.namelist():
        raise RuntimeError("manifest.tsv missing")

    text = zf.read("manifest.tsv").decode("utf-8", errors="strict")
    rows = list(csv.DictReader(io.StringIO(text), delimiter="\t"))
    required = {"sample_path", "dataset_person_id", "session", "image_index", "sha256"}
    if not rows:
        raise RuntimeError("manifest.tsv has no data rows")
    missing = required - set(rows[0])
    if missing:
        raise RuntimeError(f"manifest missing columns: {sorted(missing)}")
    return rows


def metric_zero(metrics: dict) -> bool:
    vals = [metrics.get(k) for k in METRIC_KEYS]
    present = [v for v in vals if isinstance(v, (int, float))]
    return bool(present) and all(float(v) == 0.0 for v in present)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", default=str(ZIP_DEFAULT))
    ap.add_argument("--results", default=str(RESULT_DEFAULT))
    ap.add_argument("--output", default=str(OUT_DEFAULT))
    args = ap.parse_args()

    zip_path = Path(args.zip)
    result_path = Path(args.results)
    out_path = Path(args.output)

    if not zip_path.exists():
        raise FileNotFoundError(zip_path)
    if not result_path.exists():
        raise FileNotFoundError(result_path)

    report = {
        "status": "REFERENCE-ONLY / MOHI SAMPLE INTEGRITY AUDIT",
        "zip": str(zip_path),
        "results": str(result_path),
        "manifest_rows": 0,
        "zip_image_entries": 0,
        "manifest_hash_mismatch": [],
        "duplicate_sha_groups": [],
        "duplicate_sha_group_count": 0,
        "duplicate_image_count": 0,
        "exact_zero_geometry_groups": [],
        "exact_zero_geometry_group_count": 0,
        "notes": [],
    }

    with zipfile.ZipFile(zip_path) as zf:
        rows = load_manifest(zf)
        report["manifest_rows"] = len(rows)
        names = set(zf.namelist())

        sha_to_paths = defaultdict(list)
        manifest_by_key = {}

        for r in rows:
            p = r["sample_path"]
            key = (
                int(r["dataset_person_id"]),
                int(r["session"]),
                int(r["image_index"]),
            )
            manifest_by_key[key] = p

            if p not in names:
                report["manifest_hash_mismatch"].append(
                    {"sample_path": p, "reason": "missing_zip_entry"}
                )
                continue

            data = zf.read(p)
            got = sha256_bytes(data)
            expected = r["sha256"].strip().lower()
            if got != expected:
                report["manifest_hash_mismatch"].append(
                    {
                        "sample_path": p,
                        "reason": "sha256_mismatch",
                        "expected": expected,
                        "actual": got,
                    }
                )
            sha_to_paths[got].append(p)

        report["zip_image_entries"] = sum(
            1 for n in names if n.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"))
        )

        dup_groups = []
        for digest, paths in sorted(sha_to_paths.items()):
            if len(paths) > 1:
                dup_groups.append({"sha256": digest, "paths": sorted(paths)})
        report["duplicate_sha_groups"] = dup_groups
        report["duplicate_sha_group_count"] = len(dup_groups)
        report["duplicate_image_count"] = sum(len(g["paths"]) for g in dup_groups)

    result = json.loads(result_path.read_text(encoding="utf-8"))
    images = result.get("images", [])

    geometry_to_items = defaultdict(list)
    for rec in images:
        if not rec.get("usable"):
            continue
        hand = rec.get("hand", {})
        basis = rec.get("basis", {})
        payload = {
            "lm": hand.get("lm"),
            "w": basis.get("w"),
            "h": basis.get("h"),
            "ang": basis.get("ang"),
            "can": basis.get("can"),
        }
        sig = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        geometry_to_items[sig].append(
            {
                "person": rec.get("p"),
                "session": rec.get("s"),
                "image_index": rec.get("i"),
                "file": rec.get("file"),
            }
        )

    geom_dups = []
    for sig, items in sorted(geometry_to_items.items()):
        if len(items) > 1:
            geom_dups.append({"geometry_sha256": sig, "items": items})
    report["exact_zero_geometry_groups"] = geom_dups
    report["exact_zero_geometry_group_count"] = len(geom_dups)

    # Cross-check any repeated geometry against repeated source bytes.
    duplicate_path_sets = [set(g["paths"]) for g in report["duplicate_sha_groups"]]
    for g in report["exact_zero_geometry_groups"]:
        paths = {i["file"] for i in g["items"]}
        g["same_source_bytes"] = any(paths.issubset(s) for s in duplicate_path_sets)

    if report["manifest_hash_mismatch"]:
        report["notes"].append("Manifest/content integrity mismatch exists; repeatability statistics require caution.")
    else:
        report["notes"].append("All manifest SHA256 values match ZIP content.")

    if report["duplicate_sha_groups"]:
        report["notes"].append("Exact duplicate source-image bytes exist in the 150-image sample.")
    else:
        report["notes"].append("No exact duplicate source-image bytes were found among manifest entries.")

    if report["exact_zero_geometry_groups"]:
        report["notes"].append("One or more usable images produced byte-identical serialized detector geometry; inspect group membership and source hashes.")
    else:
        report["notes"].append("No byte-identical serialized detector-geometry duplicates were found.")

    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({
        "manifest_rows": report["manifest_rows"],
        "zip_image_entries": report["zip_image_entries"],
        "manifest_hash_mismatch_count": len(report["manifest_hash_mismatch"]),
        "duplicate_sha_group_count": report["duplicate_sha_group_count"],
        "duplicate_image_count": report["duplicate_image_count"],
        "exact_zero_geometry_group_count": report["exact_zero_geometry_group_count"],
        "output": str(out_path),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
