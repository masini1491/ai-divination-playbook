#!/usr/bin/env python3
"""EXIF-frame-aligned MOHI detector-agreement execution wrapper.

REFERENCE-ONLY. This preserves the frozen detector-agreement protocol and reuses
all metric/runtime helpers from detector_agreement_runner.py. The only execution
correction is source decoding in the same raw pixel frame as the frozen
MediaPipe evidence (ignore EXIF display orientation), plus an explicit raw-size
fail-closed guard.
"""

from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path

import cv2
import numpy as np

import detector_agreement_runner as base


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", type=Path, required=True)
    ap.add_argument("--mediapipe-results", type=Path, required=True)
    ap.add_argument("--checkpoint", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    runtime = base.validate_runtime()
    if args.checkpoint.name not in {base.EXPECTED_CHECKPOINT_NAME, "rtmpose-m-hand5.pth"}:
        raise RuntimeError(f"unexpected checkpoint filename: {args.checkpoint.name}")
    checkpoint_sha = base.sha256_file(args.checkpoint)
    if checkpoint_sha != base.EXPECTED_CHECKPOINT_SHA:
        raise RuntimeError(f"checkpoint SHA mismatch: {checkpoint_sha}")

    config = base.resolve_config()
    model = base.init_model(str(config), str(args.checkpoint), device="cpu")
    model.eval()

    rows, sha_groups = base.validate_source(args.zip)
    mp_data = base.validate_mediapipe_results(args.mediapipe_results, rows)
    mp_by_file = {r["file"]: r for r in mp_data["images"]}
    representative = {
        digest: sorted(paths)[0]
        for digest, paths in sha_groups.items()
    }

    output = {
        "status": "REFERENCE-ONLY / PREDECLARED DETECTOR AGREEMENT RAW EVIDENCE / EXIF-FRAME CORRECTED",
        "runtime": runtime,
        "config": str(config),
        "config_sha256": base.sha256_file(config),
        "checkpoint": str(args.checkpoint),
        "checkpoint_sha256": checkpoint_sha,
        "source_zip": str(args.zip),
        "source_zip_sha256": base.EXPECTED_ZIP_SHA,
        "mediapipe_results": str(args.mediapipe_results),
        "mediapipe_model_sha256": base.EXPECTED_MP_MODEL_SHA,
        "canonical_basis_owner": "NORMALIZATION_CONTRACT_DRAFT.md / normalization_probe.py",
        "decode_contract": "cv2.IMREAD_COLOR | cv2.IMREAD_IGNORE_ORIENTATION",
        "raw_frame_guard": "decoded [h,w] must exactly equal frozen MediaPipe rec['raw']",
        "supersedes_for_interpretation": "first execution metrics produced with EXIF-auto-oriented IMREAD_COLOR frame",
        "images": [],
    }

    decode_flag = cv2.IMREAD_COLOR | cv2.IMREAD_IGNORE_ORIENTATION

    with zipfile.ZipFile(args.zip) as zf:
        for n, source in enumerate(rows, 1):
            data = zf.read(source["file"])
            img = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), decode_flag)
            rec = {**source, "decode": img is not None}

            if img is None:
                rec.update({"rtmpose_usable": False, "failure": "decode_failed"})
                output["images"].append(rec)
                print(f"[{n:03d}/150] {source['file']}: decode failed")
                continue

            h, w = img.shape[:2]
            mp_rec = mp_by_file[source["file"]]
            mp_raw = mp_rec.get("raw")
            if mp_raw != [h, w]:
                rec.update({
                    "raw_size": [h, w],
                    "mediapipe_raw_size": mp_raw,
                    "rtmpose_usable": False,
                    "failure": f"raw_frame_mismatch: decoded={[h, w]} mediapipe={mp_raw}",
                })
                output["images"].append(rec)
                print(f"[{n:03d}/150] {source['file']}: FRAME MISMATCH")
                continue

            mp_xy = base.mp_points(mp_rec)
            try:
                rt_xy, scores = base.rtm_output(model, img)
                metrics = base.agreement(mp_xy, rt_xy, scores, w, h)
                base.palm_basis(rt_xy)
            except Exception as exc:
                rec.update({
                    "raw_size": [h, w],
                    "mediapipe_raw_size": mp_raw,
                    "rtmpose_usable": False,
                    "failure": f"{type(exc).__name__}: {exc}",
                })
            else:
                digest = source["sha256"]
                rec.update({
                    "raw_size": [h, w],
                    "mediapipe_raw_size": mp_raw,
                    "raw_frame_match": True,
                    "rtmpose_usable": True,
                    "unique_representative": representative[digest] == source["file"],
                    "mediapipe": {"xy": mp_xy.tolist()},
                    "rtmpose": {"xy": rt_xy.tolist(), "scores": scores.tolist()},
                    "agreement": metrics,
                })

            output["images"].append(rec)
            print(f"[{n:03d}/150] {source['file']}: {'usable' if rec.get('rtmpose_usable') else 'FAILED'}")

    usable = [r for r in output["images"] if r.get("rtmpose_usable")]
    primary = [r for r in usable if r.get("unique_representative")]

    if len(usable) != 150:
        output["execution"] = {
            "total": 150,
            "usable": len(usable),
            "primary_unique": len(primary),
            "stop": True,
        }
        args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
        raise RuntimeError(f"corrected RTMPose geometry usable on {len(usable)}/150; stop before interpretation")

    if len(primary) != 148:
        raise RuntimeError(f"expected 148 unique source-byte representatives, got {len(primary)}")

    duplicate_checks = []
    by_file = {r["file"]: r for r in usable}
    for digest, paths in sorted(sha_groups.items()):
        if len(paths) <= 1:
            continue
        base_rec = by_file[sorted(paths)[0]]
        for other_path in sorted(paths)[1:]:
            other = by_file[other_path]
            a = np.asarray(base_rec["rtmpose"]["xy"], float)
            b = np.asarray(other["rtmpose"]["xy"], float)
            sa = np.asarray(base_rec["rtmpose"]["scores"], float)
            sb = np.asarray(other["rtmpose"]["scores"], float)
            duplicate_checks.append({
                "sha256": digest,
                "a": base_rec["file"],
                "b": other["file"],
                "keypoints_exact_equal": bool(np.array_equal(a, b)),
                "scores_exact_equal": bool(np.array_equal(sa, sb)),
                "keypoints_max_abs_delta": float(np.max(np.abs(a - b))),
                "scores_max_abs_delta": float(np.max(np.abs(sa - sb))),
            })

    output["execution"] = {
        "total": 150,
        "usable": 150,
        "primary_unique": 148,
        "stop": False,
    }
    output["duplicate_consistency"] = duplicate_checks
    output["primary_148"] = base.summarize_primary(primary)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\nDONE")
    print(json.dumps(output["execution"], indent=2))
    print(args.output)


if __name__ == "__main__":
    main()
