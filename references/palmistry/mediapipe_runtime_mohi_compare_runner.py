#!/usr/bin/env python3
"""Controlled MediaPipe 1.0.1 vs 1.0.0 runtime-only MOHI comparison.

REFERENCE-ONLY research runner.  It deliberately separates:

1. controller-side JPEG decode / resize / RGB preparation;
2. runtime-specific MediaPipe inference in isolated Python interpreters;
3. controller-side candidate association and geometry comparison.

No compatibility cutoff is implemented here.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import itertools
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

import cv2
import numpy as np
from PIL import Image


EXPECTED_ZIP_SHA256 = "6309f2390b0013858928c6c77344b4aa869edc8c0aeb9a61db93b73ae83feec2"
EXPECTED_MODEL_SHA256 = "fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1"
EXPECTED_PHASE0_101_SHA256 = "cc31a3d5120663f36b5f6ae47206d53465a38cdf861dd8d3b0f6f46cc023f357"
EXPECTED_PHASE0_100_SHA256 = "e1fb2836891b863bbe8fd5edb311c00482cd7e6c1d950d3666bf2bed330d7485"
EXPECTED_PYTHON = "3.12.14"
EXPECTED_NUMPY = "2.5.3"
EXPECTED_OPENCV = "5.0.0"
EXPECTED_RUNTIME_101 = "1.0.1"
EXPECTED_RUNTIME_100 = "1.0.0"
EXPECTED_ROWS = 150
EXPECTED_UNIQUE_BYTES = 148
EXPECTED_DUPLICATE_GROUPS = {
    frozenset({(5, 1, 1), (5, 3, 2)}),
    frozenset({(1, 3, 3), (1, 3, 5)}),
}
MAX_DIM = 1600
ANCHORS = (0, 5, 17)
TIE_TOL = 1e-15


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def bytes_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def array_sha256(array: np.ndarray) -> str:
    a = np.ascontiguousarray(array)
    return hashlib.sha256(a.tobytes(order="C")).hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def summary(values: list[float]) -> dict | None:
    if not values:
        return None
    x = np.asarray(values, dtype=float)
    return {
        "n": int(x.size),
        "mean": float(x.mean()),
        "median": float(np.median(x)),
        "p90": float(np.percentile(x, 90)),
        "p95": float(np.percentile(x, 95)),
        "min": float(x.min()),
        "max": float(x.max()),
        "std": float(x.std()),
    }


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
    if height <= 1e-12:
        raise RuntimeError("degenerate palm height")
    ey = ey_vec / height

    raw_ex = p5 - p17
    projected = raw_ex - float(np.dot(raw_ex, ey)) * ey
    projected_norm = float(np.linalg.norm(projected))
    if projected_norm <= 1e-12:
        raise RuntimeError("degenerate projected palm width")
    ex = projected / projected_norm
    if float(np.dot(ex, p5 - midpoint)) < 0.0:
        ex = -ex

    width = float(np.dot(p5 - p17, ex))
    if width <= 1e-12:
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

    label_a = a.get("handedness")
    label_b = b.get("handedness")
    score_a = a.get("handedness_score")
    score_b = b.get("handedness_score")

    return {
        "raw_21_delta": [float(x) for x in raw_delta],
        "raw_21_mean": float(raw_delta.mean()),
        "raw_21_median": float(np.median(raw_delta)),
        "raw_21_max": float(raw_delta.max()),
        "anchor_delta": [float(x) for x in anchor_delta],
        "anchor_mean": float(anchor_delta.mean()),
        "anchor_max": float(anchor_delta.max()),
        "axis_angle_deg": angular_delta_deg(ba["axis_deg"], bb["axis_deg"]),
        "width_rel": abs(wa - wb) / ((wa + wb) / 2.0),
        "height_rel": abs(ha - hb) / ((ha + hb) / 2.0),
        "canonical_21_delta": [float(x) for x in canonical_delta],
        "canonical_mean": float(canonical_delta.mean()),
        "canonical_max": float(canonical_delta.max()),
        "handedness_a": label_a,
        "handedness_b": label_b,
        "handedness_agreement": bool(label_a == label_b),
        "handedness_score_a": score_a,
        "handedness_score_b": score_b,
        "handedness_score_abs_delta": (
            None if score_a is None or score_b is None else abs(float(score_a) - float(score_b))
        ),
        "basis_a": ba,
        "basis_b": bb,
    }


def anchor_pair_cost(a: dict, b: dict) -> float:
    ar = np.asarray(a["raw_norm_xy"], dtype=float)[list(ANCHORS)]
    br = np.asarray(b["raw_norm_xy"], dtype=float)[list(ANCHORS)]
    return float(np.linalg.norm(ar - br, axis=1).mean())


def associate(cands_a: list[dict], cands_b: list[dict]) -> dict:
    na, nb = len(cands_a), len(cands_b)

    if na == 0 and nb == 0:
        return {
            "resolved": False,
            "mode": "no-target-both",
            "reason": "both runtimes returned zero candidates",
            "pairs": [],
        }

    if na == 1 and nb == 1:
        return {
            "resolved": True,
            "mode": "single-single",
            "reason": None,
            "pairs": [[0, 0]],
            "best_cost": anchor_pair_cost(cands_a[0], cands_b[0]),
            "second_cost": None,
            "gap": None,
        }

    if na == 2 and nb == 2:
        choices = []
        for perm in ((0, 1), (1, 0)):
            pair_costs = [anchor_pair_cost(cands_a[i], cands_b[perm[i]]) for i in (0, 1)]
            choices.append({
                "pairs": [[0, perm[0]], [1, perm[1]]],
                "pair_costs": pair_costs,
                "cost": float(np.mean(pair_costs)),
            })
        choices.sort(key=lambda x: (x["cost"], x["pairs"]))
        best, second = choices
        gap = float(second["cost"] - best["cost"])
        tied = abs(gap) <= TIE_TOL
        return {
            "resolved": not tied,
            "mode": "two-by-two-min-anchor",
            "reason": "exact/near-numeric tie" if tied else None,
            "pairs": [] if tied else best["pairs"],
            "best_cost": best["cost"],
            "second_cost": second["cost"],
            "gap": gap,
            "alternatives": choices,
            "tie_tolerance": TIE_TOL,
        }

    return {
        "resolved": False,
        "mode": "candidate-count-mismatch",
        "reason": f"cannot form complete one-to-one association for {na} vs {nb}",
        "pairs": [],
    }


def entry_metrics(pair_list: list[dict]) -> dict | None:
    if not pair_list:
        return None

    raw_all = np.concatenate([np.asarray(x["raw_21_delta"], dtype=float) for x in pair_list])
    anc_all = np.concatenate([np.asarray(x["anchor_delta"], dtype=float) for x in pair_list])
    can_all = np.concatenate([np.asarray(x["canonical_21_delta"], dtype=float) for x in pair_list])

    return {
        "matched_targets": len(pair_list),
        "raw_21_mean": float(raw_all.mean()),
        "raw_21_median": float(np.median(raw_all)),
        "raw_21_max": float(raw_all.max()),
        "anchor_mean": float(anc_all.mean()),
        "anchor_max": float(anc_all.max()),
        "axis_angle_deg": float(np.mean([x["axis_angle_deg"] for x in pair_list])),
        "width_rel": float(np.mean([x["width_rel"] for x in pair_list])),
        "height_rel": float(np.mean([x["height_rel"] for x in pair_list])),
        "canonical_mean": float(can_all.mean()),
        "canonical_max": float(can_all.max()),
        "handedness_agreement": bool(all(x["handedness_agreement"] for x in pair_list)),
    }


def aggregate_entries(entries: list[dict]) -> dict:
    transitions: dict[str, int] = {}
    count_equal = 0
    resolved = []
    handedness_total = 0
    handedness_equal = 0

    for e in entries:
        t = e["candidate_transition"]
        transitions[t] = transitions.get(t, 0) + 1
        count_equal += int(e["candidate_count_equal"])
        if e.get("metrics") is not None:
            resolved.append(e)
            handedness_total += 1
            handedness_equal += int(e["metrics"]["handedness_agreement"])

    metric_keys = (
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

    return {
        "entries": len(entries),
        "candidate_count_equal": count_equal,
        "candidate_count_agreement_rate": None if not entries else count_equal / len(entries),
        "candidate_transitions": transitions,
        "geometry_resolved_entries": len(resolved),
        "geometry_unresolved_entries": len(entries) - len(resolved),
        "metrics": {
            k: summary([float(e["metrics"][k]) for e in resolved])
            for k in metric_keys
        },
        "handedness": {
            "resolved_entries": handedness_total,
            "label_agreement_entries": handedness_equal,
            "label_agreement_rate": None if handedness_total == 0 else handedness_equal / handedness_total,
        },
    }


def parse_manifest(zf: zipfile.ZipFile) -> list[dict]:
    if "manifest.tsv" not in zf.namelist():
        raise RuntimeError("manifest.tsv missing")
    lines = zf.read("manifest.tsv").decode("utf-8").splitlines()
    if not lines:
        raise RuntimeError("empty manifest.tsv")
    header = lines[0].split("\t")
    required = ("sample_path", "dataset_person_id", "session", "image_index")
    idx = {k: header.index(k) for k in required}
    rows = []
    for ordinal, line in enumerate(lines[1:]):
        cols = line.split("\t")
        rows.append({
            "ordinal": ordinal,
            "file": cols[idx["sample_path"]],
            "person": int(cols[idx["dataset_person_id"]]),
            "session": int(cols[idx["session"]]),
            "image_index": int(cols[idx["image_index"]]),
        })
    return rows


def exif_orientation(data: bytes) -> int | None:
    try:
        with Image.open(io.BytesIO(data)) as image:
            value = image.getexif().get(274)
            return None if value is None else int(value)
    except Exception:
        return None


def convert_to_rgb(img: np.ndarray) -> np.ndarray:
    if img.ndim == 2:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    if img.ndim != 3:
        raise RuntimeError(f"unsupported decoded ndim={img.ndim}")
    if img.shape[2] == 3:
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    if img.shape[2] == 4:
        return cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
    raise RuntimeError(f"unsupported channel count={img.shape[2]}")


def prepare_sources(zip_path: Path, prepared_dir: Path) -> tuple[list[dict], dict]:
    prepared_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        rows = parse_manifest(zf)
        if len(rows) != EXPECTED_ROWS:
            raise RuntimeError(f"unexpected manifest row count: {len(rows)}")
        persons = sorted({r["person"] for r in rows})
        if len(persons) != 10:
            raise RuntimeError(f"unexpected person count: {len(persons)}")

        for r in rows:
            source = zf.read(r["file"])
            r["source_sha256"] = bytes_sha256(source)
            r["source_bytes"] = len(source)
            r["exif_orientation"] = exif_orientation(source)

            encoded = np.frombuffer(source, dtype=np.uint8)
            img = cv2.imdecode(encoded, cv2.IMREAD_UNCHANGED)
            if img is None:
                raise RuntimeError(f"decode failed: {r['file']}")
            raw_h, raw_w = img.shape[:2]

            max_dim = max(raw_h, raw_w)
            if max_dim > MAX_DIM:
                scale = MAX_DIM / max_dim
                work_w = round(raw_w * scale)
                work_h = round(raw_h * scale)
                work = cv2.resize(img, (work_w, work_h), interpolation=cv2.INTER_AREA)
            else:
                work = img
                work_h, work_w = raw_h, raw_w

            rgb = np.ascontiguousarray(convert_to_rgb(work), dtype=np.uint8)
            npy_name = f"{r['ordinal']:03d}.npy"
            npy_path = prepared_dir / npy_name
            np.save(npy_path, rgb, allow_pickle=False)

            r.update({
                "raw_shape_hw": [int(raw_h), int(raw_w)],
                "work_shape_hw": [int(rgb.shape[0]), int(rgb.shape[1])],
                "pixel_sha256": array_sha256(rgb),
                "pixel_dtype": str(rgb.dtype),
                "pixel_shape": list(map(int, rgb.shape)),
                "prepared_npy": npy_name,
                "decoder": "cv2.imdecode(IMREAD_UNCHANGED); full-frame max-dim resize; explicit RGB conversion",
                "exif_policy": "IMREAD_UNCHANGED raw stored pixel frame; EXIF orientation recorded but not applied",
            })

    by_hash: dict[str, list[dict]] = {}
    for r in rows:
        by_hash.setdefault(r["source_sha256"], []).append(r)

    if len(by_hash) != EXPECTED_UNIQUE_BYTES:
        raise RuntimeError(f"unexpected unique source-byte count: {len(by_hash)}")

    duplicate_groups = [g for g in by_hash.values() if len(g) > 1]
    observed_sets = {
        frozenset((r["person"], r["session"], r["image_index"]) for r in group)
        for group in duplicate_groups
    }
    if observed_sets != EXPECTED_DUPLICATE_GROUPS:
        raise RuntimeError(f"duplicate groups drift: {observed_sets}")

    for group in duplicate_groups:
        pixel_hashes = {r["pixel_sha256"] for r in group}
        if len(pixel_hashes) != 1:
            raise RuntimeError("byte-identical duplicate decoded to different prepared pixels")

    representative_ordinals = {min(r["ordinal"] for r in g) for g in by_hash.values()}
    for r in rows:
        r["primary_unique_representative"] = r["ordinal"] in representative_ordinals

    integrity = {
        "manifest_rows": len(rows),
        "persons": len({r["person"] for r in rows}),
        "unique_source_bytes": len(by_hash),
        "duplicate_groups": [
            {
                "source_sha256": group[0]["source_sha256"],
                "entries": [
                    {
                        "ordinal": r["ordinal"],
                        "person": r["person"],
                        "session": r["session"],
                        "image_index": r["image_index"],
                        "file": r["file"],
                    }
                    for r in group
                ],
                "prepared_pixel_sha256": group[0]["pixel_sha256"],
            }
            for group in duplicate_groups
        ],
    }
    return rows, integrity


def runtime_inventory(python: Path) -> dict:
    code = r'''
import json, platform, sys
import importlib.metadata as md
import numpy as np
import cv2
import mediapipe as mp
print(json.dumps({
    "python": platform.python_version(),
    "executable": sys.executable,
    "mediapipe": md.version("mediapipe"),
    "mediapipe_dunder": getattr(mp, "__version__", None),
    "numpy": np.__version__,
    "opencv": cv2.__version__,
    "platform": platform.platform(),
    "machine": platform.machine(),
}, sort_keys=True))
'''
    cp = subprocess.run([str(python), "-c", code], text=True, capture_output=True, check=True)
    return json.loads(cp.stdout.strip().splitlines()[-1])


def pip_freeze_without_mediapipe(python: Path) -> list[str]:
    cp = subprocess.run(
        [str(python), "-m", "pip", "list", "--format=freeze"],
        text=True,
        capture_output=True,
        check=True,
    )
    return sorted(line.strip() for line in cp.stdout.splitlines() if line.strip() and not line.lower().startswith("mediapipe=="))


def validate_phase0(path: Path, expected_sha: str, runtime: str) -> dict:
    got = file_sha256(path)
    if got != expected_sha:
        raise RuntimeError(f"Phase-0 artifact SHA mismatch for {runtime}: {got}")
    d = read_json(path)
    if d["runtime"]["python_version"] != EXPECTED_PYTHON:
        raise RuntimeError("Phase-0 Python identity drift")
    if d["package"]["distribution_version"] != runtime:
        raise RuntimeError("Phase-0 MediaPipe identity drift")
    if d["dependencies"]["numpy"] != EXPECTED_NUMPY or d["dependencies"]["opencv"] != EXPECTED_OPENCV:
        raise RuntimeError("Phase-0 dependency identity drift")
    if d["smoke"]["model_sha256"] != EXPECTED_MODEL_SHA256:
        raise RuntimeError("Phase-0 model identity drift")
    if d["smoke"]["api_smoke"] != "PASS":
        raise RuntimeError("Phase-0 API smoke was not PASS")
    if d["boundary"]["mohi_inference_executed"] is not False:
        raise RuntimeError("Phase-0 boundary says MOHI was executed")
    return {"sha256": got, "payload": d}


def category_name(category) -> str | None:
    return getattr(category, "category_name", None) or getattr(category, "display_name", None)


def worker_main(args: argparse.Namespace) -> None:
    import mediapipe as mp

    runtime = getattr(mp, "__version__", None)
    if runtime != args.expected_mediapipe:
        raise RuntimeError(f"worker runtime mismatch: expected {args.expected_mediapipe}, got {runtime}")

    model_path = Path(args.model)
    if file_sha256(model_path) != EXPECTED_MODEL_SHA256:
        raise RuntimeError("worker model SHA mismatch")

    manifest = read_json(Path(args.prepared_manifest))
    rows = manifest["rows"]
    prepared_dir = Path(args.prepared_dir)

    options = mp.tasks.vision.HandLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=str(model_path)),
        running_mode=mp.tasks.vision.RunningMode.IMAGE,
        num_hands=2,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    output = {
        "runtime": runtime,
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "opencv": cv2.__version__,
        "model_sha256": EXPECTED_MODEL_SHA256,
        "options": {
            "running_mode": "IMAGE",
            "num_hands": 2,
            "min_hand_detection_confidence": 0.5,
            "min_hand_presence_confidence": 0.5,
            "min_tracking_confidence": 0.5,
        },
        "entries": [],
    }

    with mp.tasks.vision.HandLandmarker.create_from_options(options) as landmarker:
        for n, r in enumerate(rows, 1):
            rgb = np.load(prepared_dir / r["prepared_npy"], allow_pickle=False)
            if str(rgb.dtype) != "uint8" or list(rgb.shape) != r["pixel_shape"]:
                raise RuntimeError(f"prepared array shape/dtype drift at ordinal {r['ordinal']}")
            pixel_sha = array_sha256(rgb)
            if pixel_sha != r["pixel_sha256"]:
                raise RuntimeError(f"prepared pixel SHA drift at ordinal {r['ordinal']}")

            image = mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(rgb))
            result = landmarker.detect(image)

            raw_h, raw_w = r["raw_shape_hw"]
            candidates = []
            for i, landmarks in enumerate(result.hand_landmarks):
                raw_norm_xy = []
                raw_xy = []
                xyz = []
                for p in landmarks:
                    x = float(p.x)
                    y = float(p.y)
                    z = float(p.z)
                    raw_norm_xy.append([x, y])
                    raw_xy.append([x * raw_w, y * raw_h])
                    xyz.append([x, y, z])

                handedness = None
                handedness_score = None
                if i < len(result.handedness) and result.handedness[i]:
                    c = result.handedness[i][0]
                    handedness = category_name(c)
                    handedness_score = float(c.score)

                candidates.append({
                    "worker_index": i,
                    "handedness": handedness,
                    "handedness_score": handedness_score,
                    "landmarks_xyz_work_normalized": xyz,
                    "raw_norm_xy": raw_norm_xy,
                    "raw_xy": raw_xy,
                })

            output["entries"].append({
                "ordinal": r["ordinal"],
                "file": r["file"],
                "source_sha256": r["source_sha256"],
                "input_pixel_sha256": pixel_sha,
                "candidate_count": len(candidates),
                "candidates": candidates,
            })
            print(f"[{n:03d}/{len(rows)}] runtime={runtime} candidates={len(candidates)} {r['file']}")

    write_json(Path(args.worker_output), output)
    print(Path(args.worker_output))


def run_worker(
    python: Path,
    script: Path,
    runtime: str,
    model: Path,
    prepared_manifest: Path,
    prepared_dir: Path,
    output: Path,
) -> None:
    cmd = [
        str(python), str(script),
        "--worker",
        "--expected-mediapipe", runtime,
        "--model", str(model),
        "--prepared-manifest", str(prepared_manifest),
        "--prepared-dir", str(prepared_dir),
        "--worker-output", str(output),
    ]
    subprocess.run(cmd, check=True)


def exact_duplicate_determinism(worker: dict, groups: list[dict]) -> list[dict]:
    by_ordinal = {e["ordinal"]: e for e in worker["entries"]}
    results = []
    for group in groups:
        ordinals = [e["ordinal"] for e in group["entries"]]
        first = by_ordinal[ordinals[0]]
        comparisons = []
        for ordinal in ordinals[1:]:
            other = by_ordinal[ordinal]
            comparisons.append({
                "a": ordinals[0],
                "b": ordinal,
                "candidate_count_equal": first["candidate_count"] == other["candidate_count"],
                "candidates_exact_equal": first["candidates"] == other["candidates"],
                "input_pixel_sha_equal": first["input_pixel_sha256"] == other["input_pixel_sha256"],
            })
        results.append({
            "source_sha256": group["source_sha256"],
            "ordinals": ordinals,
            "comparisons": comparisons,
            "all_exact": all(
                x["candidate_count_equal"] and x["candidates_exact_equal"] and x["input_pixel_sha_equal"]
                for x in comparisons
            ),
        })
    return results


def controller_main(args: argparse.Namespace) -> None:
    zip_path = Path(args.zip)
    model = Path(args.model)
    python101 = Path(args.python_baseline)
    python100 = Path(args.python_comparison)
    phase101_path = Path(args.phase0_baseline)
    phase100_path = Path(args.phase0_comparison)
    output_path = Path(args.output)
    script = Path(__file__).resolve()

    if file_sha256(zip_path) != EXPECTED_ZIP_SHA256:
        raise RuntimeError("MOHI ZIP SHA mismatch")
    if file_sha256(model) != EXPECTED_MODEL_SHA256:
        raise RuntimeError("Hand Landmarker model SHA mismatch")

    phase101 = validate_phase0(phase101_path, EXPECTED_PHASE0_101_SHA256, EXPECTED_RUNTIME_101)
    phase100 = validate_phase0(phase100_path, EXPECTED_PHASE0_100_SHA256, EXPECTED_RUNTIME_100)

    inv101 = runtime_inventory(python101)
    inv100 = runtime_inventory(python100)
    if inv101["python"] != EXPECTED_PYTHON or inv100["python"] != EXPECTED_PYTHON:
        raise RuntimeError("execution Python patch drift")
    if inv101["mediapipe"] != EXPECTED_RUNTIME_101 or inv100["mediapipe"] != EXPECTED_RUNTIME_100:
        raise RuntimeError("execution MediaPipe version drift")
    if inv101["mediapipe_dunder"] != EXPECTED_RUNTIME_101 or inv100["mediapipe_dunder"] != EXPECTED_RUNTIME_100:
        raise RuntimeError("execution mediapipe.__version__ drift")
    if inv101["numpy"] != inv100["numpy"] or inv101["numpy"] != EXPECTED_NUMPY:
        raise RuntimeError("NumPy drift")
    if inv101["opencv"] != inv100["opencv"] or inv101["opencv"] != EXPECTED_OPENCV:
        raise RuntimeError("OpenCV drift")

    freeze101 = pip_freeze_without_mediapipe(python101)
    freeze100 = pip_freeze_without_mediapipe(python100)
    if freeze101 != freeze100:
        raise RuntimeError("non-MediaPipe pip package drift")

    with tempfile.TemporaryDirectory(prefix="mp-runtime-mohi-") as td_raw:
        td = Path(td_raw)
        prepared_dir = td / "prepared"
        rows, integrity = prepare_sources(zip_path, prepared_dir)
        prepared_manifest_path = td / "prepared-manifest.json"
        write_json(prepared_manifest_path, {
            "zip_sha256": EXPECTED_ZIP_SHA256,
            "rows": rows,
            "integrity": integrity,
        })

        worker101_path = td / "worker-101.json"
        worker100_path = td / "worker-100.json"

        run_worker(python101, script, EXPECTED_RUNTIME_101, model, prepared_manifest_path, prepared_dir, worker101_path)
        run_worker(python100, script, EXPECTED_RUNTIME_100, model, prepared_manifest_path, prepared_dir, worker100_path)

        worker101 = read_json(worker101_path)
        worker100 = read_json(worker100_path)

        entries101 = {e["ordinal"]: e for e in worker101["entries"]}
        entries100 = {e["ordinal"]: e for e in worker100["entries"]}
        if set(entries101) != set(range(EXPECTED_ROWS)) or set(entries100) != set(range(EXPECTED_ROWS)):
            raise RuntimeError("worker output entry accounting drift")

        comparisons = []
        for r in rows:
            a = entries101[r["ordinal"]]
            b = entries100[r["ordinal"]]
            if a["source_sha256"] != r["source_sha256"] or b["source_sha256"] != r["source_sha256"]:
                raise RuntimeError("source SHA linkage drift")
            if a["input_pixel_sha256"] != r["pixel_sha256"] or b["input_pixel_sha256"] != r["pixel_sha256"]:
                raise RuntimeError("cross-runtime input pixel drift")

            association = associate(a["candidates"], b["candidates"])
            pair_list = []
            if association["resolved"]:
                for ia, ib in association["pairs"]:
                    pm = pair_metrics(a["candidates"][ia], b["candidates"][ib])
                    pm["baseline_candidate_index"] = ia
                    pm["comparison_candidate_index"] = ib
                    pair_list.append(pm)

            metrics = entry_metrics(pair_list)
            comparisons.append({
                "ordinal": r["ordinal"],
                "file": r["file"],
                "person": r["person"],
                "session": r["session"],
                "image_index": r["image_index"],
                "source_sha256": r["source_sha256"],
                "exif_orientation": r["exif_orientation"],
                "raw_shape_hw": r["raw_shape_hw"],
                "work_shape_hw": r["work_shape_hw"],
                "input_pixel_sha256": r["pixel_sha256"],
                "primary_unique_representative": r["primary_unique_representative"],
                "baseline_candidate_count": a["candidate_count"],
                "comparison_candidate_count": b["candidate_count"],
                "candidate_count_equal": a["candidate_count"] == b["candidate_count"],
                "candidate_transition": f"{a['candidate_count']}->{b['candidate_count']}",
                "association": association,
                "pair_metrics": pair_list,
                "metrics": metrics,
                "baseline_candidates": a["candidates"],
                "comparison_candidates": b["candidates"],
            })

        primary = [e for e in comparisons if e["primary_unique_representative"]]
        if len(primary) != EXPECTED_UNIQUE_BYTES:
            raise RuntimeError("primary unique representative accounting drift")

        per_person_session = {}
        for key, group_iter in itertools.groupby(
            sorted(primary, key=lambda e: (e["person"], e["session"], e["image_index"])),
            key=lambda e: (e["person"], e["session"]),
        ):
            group = list(group_iter)
            per_person_session[f"P{key[0]:03d}/S{key[1]}"] = aggregate_entries(group)

        duplicate_determinism = {
            EXPECTED_RUNTIME_101: exact_duplicate_determinism(worker101, integrity["duplicate_groups"]),
            EXPECTED_RUNTIME_100: exact_duplicate_determinism(worker100, integrity["duplicate_groups"]),
        }

        result = {
            "status": "REFERENCE-ONLY / CONTROLLED MEDIAPIPE RUNTIME-ONLY MOHI RAW EVIDENCE",
            "boundary": {
                "production_threshold": False,
                "compatibility_cutoff": False,
                "anatomical_ground_truth": False,
                "biometric_identity_claim": False,
                "palmistry_interpretation_validity": False,
            },
            "provenance": {
                "zip_sha256": EXPECTED_ZIP_SHA256,
                "model_sha256": EXPECTED_MODEL_SHA256,
                "phase0_baseline": {"path": str(phase101_path), "sha256": phase101["sha256"]},
                "phase0_comparison": {"path": str(phase100_path), "sha256": phase100["sha256"]},
                "baseline_runtime": inv101,
                "comparison_runtime": inv100,
                "non_mediapipe_pip_packages": freeze101,
                "controller_python": sys.version.split()[0],
                "controller_numpy": np.__version__,
                "controller_opencv": cv2.__version__,
                "decode_contract": "ZIP JPEG bytes -> cv2.imdecode(IMREAD_UNCHANGED) -> max-dim 1600 full-frame resize with INTER_AREA if needed -> explicit RGB uint8 -> one shared .npy pixel array consumed by both runtimes",
                "exif_contract": "EXIF orientation recorded diagnostically; decode uses raw stored pixel frame via IMREAD_UNCHANGED; no runtime-specific filename decode",
                "association_contract": "single-single direct; two-two minimum mean L0/L5/L17 raw-normalized anchor cost with best/second/gap accounting; candidate-count mismatch unresolved; no candidate-index identity authority",
                "canonical_contract": "L0/L5/L17; ey=normalize(midpoint(L5,L17)-L0); ex=orthogonalized L5-L17 toward index side; projected palm width",
            },
            "execution": {
                "image_entries": EXPECTED_ROWS,
                "primary_unique_source_representatives": EXPECTED_UNIQUE_BYTES,
                "duplicate_group_count": len(integrity["duplicate_groups"]),
                "baseline_inferences": len(worker101["entries"]),
                "comparison_inferences": len(worker100["entries"]),
                "stop": False,
            },
            "source_integrity": integrity,
            "summary_all_150_entries": aggregate_entries(comparisons),
            "summary_primary_148_unique_source_representatives": aggregate_entries(primary),
            "per_person_session_primary": per_person_session,
            "duplicate_determinism": duplicate_determinism,
            "entries": comparisons,
        }

        write_json(output_path, result)

    print("\nDONE")
    print(json.dumps(result["execution"], indent=2))
    print(output_path)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("--worker", action="store_true")

    p.add_argument("--expected-mediapipe")
    p.add_argument("--prepared-manifest")
    p.add_argument("--prepared-dir")
    p.add_argument("--worker-output")

    p.add_argument("--zip")
    p.add_argument("--model")
    p.add_argument("--python-baseline")
    p.add_argument("--python-comparison")
    p.add_argument("--phase0-baseline")
    p.add_argument("--phase0-comparison")
    p.add_argument("--output")
    return p


def main() -> None:
    args = build_parser().parse_args()
    if args.worker:
        required = ("expected_mediapipe", "prepared_manifest", "prepared_dir", "worker_output", "model")
        missing = [x for x in required if getattr(args, x) is None]
        if missing:
            raise SystemExit(f"worker missing args: {missing}")
        worker_main(args)
    else:
        required = (
            "zip", "model", "python_baseline", "python_comparison",
            "phase0_baseline", "phase0_comparison", "output",
        )
        missing = [x for x in required if getattr(args, x) is None]
        if missing:
            raise SystemExit(f"controller missing args: {missing}")
        controller_main(args)


if __name__ == "__main__":
    main()
