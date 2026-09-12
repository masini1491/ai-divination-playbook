from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import struct
import zipfile
from collections import Counter
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np

EXPECTED_MP_VERSION = "1.0.1"
EXPECTED_MODEL_SHA256 = "fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1"
EXPECTED_ARCHIVE_SHA256 = "b5854b545f3ff0193b51cc02278efdbca25e1e3d1147a8559c7bb042ff2b7ca0"
EXPECTED_DEVICES = {
    "Google Pixel 5": "D1",
    "Google Pixel 10 pro": "D2",
}
EXPECTED_PER_DEVICE = 15
EXPECTED_TOTAL = 30
ANATOMICAL_SIDE = "left"
SIDE_AUTHORITY = "explicit_bodily_self_report"
MAX_WORK_DIM = 1600
ANCHORS = (0, 5, 17)
EPS = 1e-12
METRIC_KEYS = (
    "raw_21_mean",
    "raw_21_median",
    "raw_21_max",
    "anchor_mean",
    "anchor_max",
    "axis_angle_deg",
    "width_rel",
    "height_rel",
    "canonical_mean",
    "canonical_max",
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def exif_orientation_from_jpeg(data: bytes) -> int | None:
    """Read JPEG EXIF Orientation without retaining unrelated EXIF metadata."""
    if len(data) < 4 or data[:2] != b"\xff\xd8":
        return None
    pos = 2
    while pos + 4 <= len(data):
        if data[pos] != 0xFF:
            pos += 1
            continue
        marker = data[pos + 1]
        pos += 2
        if marker in (0xD8, 0xD9):
            continue
        if marker == 0xDA:
            break
        if pos + 2 > len(data):
            break
        seg_len = int.from_bytes(data[pos:pos + 2], "big")
        if seg_len < 2 or pos + seg_len > len(data):
            break
        payload = data[pos + 2:pos + seg_len]
        pos += seg_len
        if marker != 0xE1 or not payload.startswith(b"Exif\x00\x00"):
            continue
        tiff = payload[6:]
        if len(tiff) < 8:
            return None
        byte_order = tiff[:2]
        if byte_order == b"II":
            endian = "<"
        elif byte_order == b"MM":
            endian = ">"
        else:
            return None
        if struct.unpack(endian + "H", tiff[2:4])[0] != 42:
            return None
        ifd0 = struct.unpack(endian + "I", tiff[4:8])[0]
        if ifd0 + 2 > len(tiff):
            return None
        count = struct.unpack(endian + "H", tiff[ifd0:ifd0 + 2])[0]
        base = ifd0 + 2
        for i in range(count):
            off = base + 12 * i
            if off + 12 > len(tiff):
                return None
            tag, typ, n = struct.unpack(endian + "HHI", tiff[off:off + 8])
            if tag != 0x0112:
                continue
            if typ != 3 or n < 1:
                return None
            return int(struct.unpack(endian + "H", tiff[off + 8:off + 10])[0])
        return None
    return None


def decode_stored_jpeg(data: bytes) -> np.ndarray | None:
    arr = np.frombuffer(data, dtype=np.uint8)
    flags = int(cv2.IMREAD_COLOR)
    if hasattr(cv2, "IMREAD_IGNORE_ORIENTATION"):
        flags |= int(cv2.IMREAD_IGNORE_ORIENTATION)
    return cv2.imdecode(arr, flags)


def resize_for_detector(img: np.ndarray) -> tuple[np.ndarray, float, float]:
    h, w = img.shape[:2]
    m = max(h, w)
    if m <= MAX_WORK_DIM:
        return img, 1.0, 1.0
    q = MAX_WORK_DIM / float(m)
    nw = int(round(w * q))
    nh = int(round(h * q))
    out = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_AREA)
    return out, nw / float(w), nh / float(h)


def category_name(category) -> str | None:
    return getattr(category, "category_name", None) or getattr(category, "display_name", None)


def detect_candidates(landmarker, work: np.ndarray, raw_w: int, raw_h: int, sx: float, sy: float) -> list[dict]:
    rgb = cv2.cvtColor(work, cv2.COLOR_BGR2RGB)
    result = landmarker.detect(
        mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(rgb))
    )
    work_h, work_w = work.shape[:2]
    candidates = []
    for i, landmarks in enumerate(result.hand_landmarks):
        raw_xy = []
        raw_norm_xy = []
        z = []
        for p in landmarks:
            x = float(p.x) * work_w / sx
            y = float(p.y) * work_h / sy
            raw_xy.append([x, y])
            raw_norm_xy.append([x / raw_w, y / raw_h])
            z.append(float(p.z))
        label = None
        score = None
        if i < len(result.handedness) and result.handedness[i]:
            label = category_name(result.handedness[i][0])
            score = float(result.handedness[i][0].score)
        candidates.append({
            "raw_xy": raw_xy,
            "raw_norm_xy": raw_norm_xy,
            "z": z,
            "handedness": label,
            "handedness_score": score,
        })
    return candidates


def angular_delta_deg(a: float, b: float) -> float:
    return abs((b - a + 180.0) % 360.0 - 180.0)


def canonical_basis(candidate: dict) -> dict:
    pts = np.asarray(candidate["raw_xy"], dtype=float)
    p0 = pts[0]
    p5 = pts[5]
    p17 = pts[17]
    midpoint = (p5 + p17) / 2.0

    ey_vec = midpoint - p0
    height = float(np.linalg.norm(ey_vec))
    if height <= EPS:
        raise RuntimeError("degenerate palm height")
    ey = ey_vec / height

    raw_ex = p5 - p17
    projected = raw_ex - float(np.dot(raw_ex, ey)) * ey
    projected_norm = float(np.linalg.norm(projected))
    if projected_norm <= EPS:
        raise RuntimeError("degenerate projected palm width")
    ex = projected / projected_norm
    if float(np.dot(ex, p5 - midpoint)) < 0.0:
        ex = -ex

    width = float(np.dot(p5 - p17, ex))
    if width <= EPS:
        raise RuntimeError("non-positive projected palm width")

    canonical = []
    for p in pts:
        v = p - p0
        canonical.append([
            float(np.dot(v, ex) / width),
            float(np.dot(v, ey) / height),
        ])

    return {
        "width_px": width,
        "height_px": height,
        "axis_deg": float(math.degrees(math.atan2(float(ey[1]), float(ey[0])))),
        "canonical_xy": canonical,
    }


def pair_metrics(a: dict, b: dict) -> dict:
    ar = np.asarray(a["raw_norm_xy"], dtype=float)
    br = np.asarray(b["raw_norm_xy"], dtype=float)
    raw_delta = np.linalg.norm(ar - br, axis=1)
    anchor_delta = raw_delta[list(ANCHORS)]

    ba = canonical_basis(a)
    bb = canonical_basis(b)
    ca = np.asarray(ba["canonical_xy"], dtype=float)
    cb = np.asarray(bb["canonical_xy"], dtype=float)
    canonical_delta = np.linalg.norm(ca - cb, axis=1)

    wa, wb = ba["width_px"], bb["width_px"]
    ha, hb = ba["height_px"], bb["height_px"]

    return {
        "raw_21_mean": float(raw_delta.mean()),
        "raw_21_median": float(np.median(raw_delta)),
        "raw_21_max": float(raw_delta.max()),
        "anchor_mean": float(anchor_delta.mean()),
        "anchor_max": float(anchor_delta.max()),
        "axis_angle_deg": angular_delta_deg(ba["axis_deg"], bb["axis_deg"]),
        "width_rel": abs(wa - wb) / ((wa + wb) / 2.0),
        "height_rel": abs(ha - hb) / ((ha + hb) / 2.0),
        "canonical_mean": float(canonical_delta.mean()),
        "canonical_max": float(canonical_delta.max()),
        "handedness_a": a.get("handedness"),
        "handedness_b": b.get("handedness"),
        "handedness_agreement": bool(a.get("handedness") == b.get("handedness")),
    }


def summary(values: list[float]) -> dict | None:
    if not values:
        return None
    x = np.asarray(values, dtype=float)
    return {
        "n": int(x.size),
        "mean": float(x.mean()),
        "median": float(np.median(x)),
        "p10": float(np.percentile(x, 10)),
        "p90": float(np.percentile(x, 90)),
        "p95": float(np.percentile(x, 95)),
        "min": float(x.min()),
        "max": float(x.max()),
        "std": float(x.std()),
    }


def summarize_pairs(pairs: list[dict]) -> dict:
    resolved = [p for p in pairs if p.get("metrics") is not None]
    handedness_total = len(resolved)
    handedness_equal = sum(int(p["metrics"]["handedness_agreement"]) for p in resolved)
    return {
        "pairs_expected": len(pairs),
        "pairs_resolved": len(resolved),
        "pairs_unresolved": len(pairs) - len(resolved),
        "metrics": {
            k: summary([float(p["metrics"][k]) for p in resolved])
            for k in METRIC_KEYS
        },
        "handedness_metadata": {
            "resolved_pairs": handedness_total,
            "label_agreement_pairs": handedness_equal,
            "label_agreement_rate": None if not handedness_total else handedness_equal / handedness_total,
        },
    }


def ordinal_stratum(index0: int) -> str:
    if index0 < 5:
        return "B1"
    if index0 < 10:
        return "B2"
    return "B3"


def parse_source_archive(zf: zipfile.ZipFile) -> list[dict]:
    files = [n for n in zf.namelist() if not n.endswith("/")]
    rows = []
    counts = Counter()
    for name in files:
        parts = Path(name).parts
        if len(parts) != 2:
            raise RuntimeError(f"unexpected archive path: {name}")
        folder, filename = parts
        if folder not in EXPECTED_DEVICES:
            raise RuntimeError(f"unexpected device folder: {folder}")
        if not filename.lower().endswith((".jpg", ".jpeg")):
            raise RuntimeError(f"unexpected non-JPEG source: {name}")
        counts[folder] += 1
        rows.append({
            "archive_path": name,
            "device_name": folder,
            "device_id": EXPECTED_DEVICES[folder],
            "filename": filename,
        })
    if len(rows) != EXPECTED_TOTAL:
        raise RuntimeError(f"unexpected total source files: {len(rows)}")
    for device_name in EXPECTED_DEVICES:
        if counts[device_name] != EXPECTED_PER_DEVICE:
            raise RuntimeError(f"unexpected count for {device_name}: {counts[device_name]}")

    ordered = []
    for device_name, device_id in EXPECTED_DEVICES.items():
        group = sorted((r for r in rows if r["device_name"] == device_name), key=lambda r: r["filename"])
        for i, r in enumerate(group):
            ordinal = i + 1
            ordered.append({
                **r,
                "device_id": device_id,
                "ordinal": ordinal,
                "stratum": ordinal_stratum(i),
                "entry_id": f"{device_id}-{ordinal:02d}",
            })
    return ordered


def make_pair(a: dict, b: dict, family: str) -> dict:
    rec = {
        "family": family,
        "a": a["entry_id"],
        "b": b["entry_id"],
        "device_a": a["device_id"],
        "device_b": b["device_id"],
        "stratum_a": a["stratum"],
        "stratum_b": b["stratum"],
        "metrics": None,
        "reason": None,
    }
    if not a["usable"] or not b["usable"]:
        rec["reason"] = "one_or_both_entries_unresolved"
        return rec
    try:
        rec["metrics"] = pair_metrics(a["candidate"], b["candidate"])
    except Exception as exc:
        rec["reason"] = f"pair_metric_error:{type(exc).__name__}:{exc}"
    return rec


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", required=True, dest="zip_path")
    ap.add_argument("--model", required=True, dest="model_path")
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    zip_path = Path(args.zip_path)
    model_path = Path(args.model_path)
    output_path = Path(args.output)

    if getattr(mp, "__version__", "") != EXPECTED_MP_VERSION:
        raise RuntimeError(f"MediaPipe version mismatch: {getattr(mp, '__version__', None)}")
    archive_sha = sha256_file(zip_path)
    if archive_sha != EXPECTED_ARCHIVE_SHA256:
        raise RuntimeError(f"source archive SHA mismatch: {archive_sha}")
    model_sha = sha256_file(model_path)
    if model_sha != EXPECTED_MODEL_SHA256:
        raise RuntimeError(f"model SHA mismatch: {model_sha}")

    options = mp.tasks.vision.HandLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=str(model_path)),
        running_mode=mp.tasks.vision.RunningMode.IMAGE,
        num_hands=2,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    result = {
        "status": "REFERENCE-ONLY / TWO-DEVICE REPEATED-REPOSITION FIRST-UPLOAD PILOT RAW EVIDENCE",
        "scope": {
            "formal_three_session_b2_closure_data": False,
            "collection_blocks_per_device": 1,
            "ordinal_strata_are_sessions": False,
            "biometric_identity_claim": False,
            "production_threshold": False,
            "production_routing": False,
        },
        "provenance": {
            "source_archive_sha256": archive_sha,
            "model_sha256": model_sha,
            "mediapipe_version": EXPECTED_MP_VERSION,
            "running_mode": "IMAGE",
            "num_hands": 2,
            "min_hand_detection_confidence": 0.5,
            "min_hand_presence_confidence": 0.5,
            "min_tracking_confidence": 0.5,
            "max_work_dim": MAX_WORK_DIM,
            "anatomical_side": ANATOMICAL_SIDE,
            "side_authority": SIDE_AUTHORITY,
            "canonical_width_contract": "projected L5-L17 orthogonal to ey",
        },
        "entries": [],
    }

    source_hashes = []
    with zipfile.ZipFile(zip_path) as zf:
        rows = parse_source_archive(zf)
        with mp.tasks.vision.HandLandmarker.create_from_options(options) as landmarker:
            for row in rows:
                data = zf.read(row["archive_path"])
                source_sha = sha256_bytes(data)
                source_hashes.append(source_sha)
                orientation = exif_orientation_from_jpeg(data)
                image = decode_stored_jpeg(data)
                rec = {
                    "entry_id": row["entry_id"],
                    "device_id": row["device_id"],
                    "device_name": row["device_name"],
                    "ordinal": row["ordinal"],
                    "stratum": row["stratum"],
                    "source_sha256": source_sha,
                    "exif_orientation": orientation,
                    "decode_ok": image is not None,
                    "raw_shape": None,
                    "work_shape": None,
                    "candidate_count": None,
                    "usable": False,
                    "unresolved_reason": None,
                    "candidate": None,
                }
                if orientation != 1:
                    rec["unresolved_reason"] = f"unexpected_exif_orientation:{orientation}"
                    result["entries"].append(rec)
                    continue
                if image is None:
                    rec["unresolved_reason"] = "decode_failed"
                    result["entries"].append(rec)
                    continue

                raw_h, raw_w = image.shape[:2]
                work, sx, sy = resize_for_detector(image)
                candidates = detect_candidates(landmarker, work, raw_w, raw_h, sx, sy)
                rec["raw_shape"] = [raw_h, raw_w]
                rec["work_shape"] = list(work.shape[:2])
                rec["candidate_count"] = len(candidates)
                if len(candidates) == 1:
                    rec["usable"] = True
                    rec["candidate"] = candidates[0]
                elif len(candidates) == 0:
                    rec["unresolved_reason"] = "zero_candidates"
                else:
                    rec["unresolved_reason"] = "multi_candidate_target_not_assumed"
                result["entries"].append(rec)

    duplicate_counts = Counter(source_hashes)
    duplicate_groups = [h for h, n in duplicate_counts.items() if n > 1]
    if duplicate_groups:
        raise RuntimeError(f"unexpected byte-identical duplicate groups: {len(duplicate_groups)}")

    entries = result["entries"]
    by_device = {
        d: [e for e in entries if e["device_id"] == d]
        for d in ("D1", "D2")
    }

    within_device_pairs = []
    within_by_device = {}
    for device_id in ("D1", "D2"):
        pairs = [make_pair(a, b, "within_device") for a, b in itertools.combinations(by_device[device_id], 2)]
        within_device_pairs.extend(pairs)
        within_by_device[device_id] = summarize_pairs(pairs)

    cross_device_pairs = [
        make_pair(a, b, "cross_device")
        for a in by_device["D1"]
        for b in by_device["D2"]
    ]

    strata = {}
    for s in ("B1", "B2", "B3"):
        per_device = {}
        for device_id in ("D1", "D2"):
            group = [e for e in by_device[device_id] if e["stratum"] == s]
            pairs = [make_pair(a, b, f"{s}_within_device") for a, b in itertools.combinations(group, 2)]
            per_device[device_id] = summarize_pairs(pairs)
        d1 = [e for e in by_device["D1"] if e["stratum"] == s]
        d2 = [e for e in by_device["D2"] if e["stratum"] == s]
        cross = [make_pair(a, b, f"{s}_cross_device") for a in d1 for b in d2]
        strata[s] = {
            "role": "ordinal_diagnostic_only_not_session",
            "within_device": per_device,
            "cross_device": summarize_pairs(cross),
        }

    candidate_distribution = Counter(
        "decode_failed" if not e["decode_ok"] else str(e["candidate_count"])
        for e in entries
    )
    per_device_candidate_distribution = {
        device_id: dict(sorted(Counter(
            "decode_failed" if not e["decode_ok"] else str(e["candidate_count"])
            for e in group
        ).items()))
        for device_id, group in by_device.items()
    }
    label_distribution = Counter(
        e["candidate"].get("handedness")
        for e in entries
        if e["usable"] and e.get("candidate") is not None
    )

    result["accounting"] = {
        "source_entries": len(entries),
        "unique_source_sha256": len(set(source_hashes)),
        "duplicate_groups": len(duplicate_groups),
        "device_counts": {d: len(v) for d, v in by_device.items()},
        "candidate_distribution": dict(sorted(candidate_distribution.items())),
        "per_device_candidate_distribution": per_device_candidate_distribution,
        "usable_entries": sum(int(e["usable"]) for e in entries),
        "unresolved_entries": sum(int(not e["usable"]) for e in entries),
        "detector_handedness_label_distribution_metadata_only": dict(sorted((str(k), v) for k, v in label_distribution.items())),
    }
    result["pair_families"] = {
        "within_device_all_pairs": {
            "all_devices": summarize_pairs(within_device_pairs),
            "per_device": within_by_device,
        },
        "cross_device_all_pairs": summarize_pairs(cross_device_pairs),
        "ordinal_strata_diagnostic_only": strata,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({
        "status": result["status"],
        "source_archive_sha256": archive_sha,
        "model_sha256": model_sha,
        "mediapipe_version": EXPECTED_MP_VERSION,
        "source_entries": result["accounting"]["source_entries"],
        "unique_source_sha256": result["accounting"]["unique_source_sha256"],
        "duplicate_groups": result["accounting"]["duplicate_groups"],
        "device_counts": result["accounting"]["device_counts"],
        "candidate_distribution": result["accounting"]["candidate_distribution"],
        "usable_entries": result["accounting"]["usable_entries"],
        "unresolved_entries": result["accounting"]["unresolved_entries"],
        "within_device_pairs_expected": len(within_device_pairs),
        "cross_device_pairs_expected": len(cross_device_pairs),
        "ordinal_strata_are_sessions": False,
    }, ensure_ascii=False, indent=2))
    print(output_path)


if __name__ == "__main__":
    main()
