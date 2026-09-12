#!/usr/bin/env python3
"""REFERENCE-ONLY MediaPipe runtime identity probe.

This probe records package/runtime provenance and exercises a non-MOHI
HandLandmarker API smoke test with a disposable in-memory RGB fixture.
It does not produce runtime-compatibility results or production thresholds.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata as md
import json
import platform
import sys
from pathlib import Path
from typing import Any

import mediapipe as mp
import numpy as np

EXPECTED_MODEL_SHA256 = (
    "fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1"
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def dist_text_digest(dist: md.Distribution, name: str) -> dict[str, Any]:
    text = dist.read_text(name)
    if text is None:
        return {"present": False, "sha256": None, "length": None}
    data = text.encode("utf-8")
    return {
        "present": True,
        "sha256": sha256_bytes(data),
        "length": len(data),
    }


def package_identity() -> dict[str, Any]:
    dist = md.distribution("mediapipe")
    files = list(dist.files or [])
    record = next((x for x in files if str(x).endswith(".dist-info/RECORD")), None)
    record_path = Path(dist.locate_file(record)) if record is not None else None

    return {
        "mediapipe_dunder_version": getattr(mp, "__version__", None),
        "distribution_version": dist.version,
        "package_file": getattr(mp, "__file__", None),
        "distribution_root": str(dist.locate_file("")),
        "record_path": None if record_path is None else str(record_path),
        "record_sha256": (
            None
            if record_path is None or not record_path.is_file()
            else sha256_file(record_path)
        ),
        "metadata_digest": dist_text_digest(dist, "METADATA"),
        "wheel_metadata_digest": dist_text_digest(dist, "WHEEL"),
        "direct_url_digest": dist_text_digest(dist, "direct_url.json"),
        "installed_file_count": len(files),
    }


def optional_versions() -> dict[str, Any]:
    out: dict[str, Any] = {"numpy": np.__version__}
    try:
        import cv2
        out["opencv"] = cv2.__version__
        out["opencv_import"] = "PASS"
    except Exception as e:
        out["opencv"] = None
        out["opencv_import"] = f"UNAVAILABLE: {type(e).__name__}: {e}"
    return out


def synthetic_rgb() -> np.ndarray:
    y, x = np.mgrid[0:256, 0:256]
    img = np.zeros((256, 256, 3), dtype=np.uint8)
    img[..., 0] = np.clip(35 + x * 0.30, 0, 255).astype(np.uint8)
    img[..., 1] = np.clip(45 + y * 0.25, 0, 255).astype(np.uint8)
    img[..., 2] = 95
    # Disposable, intentionally non-biometric palm-like silhouette.
    yy = ((y - 145.0) / 78.0) ** 2
    xx = ((x - 128.0) / 60.0) ** 2
    m = (xx + yy) <= 1.0
    img[m] = np.array([178, 145, 126], dtype=np.uint8)
    return np.ascontiguousarray(img)


def smoke(model_path: Path) -> dict[str, Any]:
    model_sha = sha256_file(model_path)
    if model_sha != EXPECTED_MODEL_SHA256:
        raise RuntimeError(f"Hand Landmarker model SHA mismatch: {model_sha}")

    rgb = synthetic_rgb()
    pixel_sha = sha256_bytes(rgb.tobytes())
    image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

    options = mp.tasks.vision.HandLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=str(model_path)),
        running_mode=mp.tasks.vision.RunningMode.IMAGE,
        num_hands=2,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    with mp.tasks.vision.HandLandmarker.create_from_options(options) as detector:
        result = detector.detect(image)

    return {
        "model_path": str(model_path),
        "model_sha256": model_sha,
        "input_shape": list(rgb.shape),
        "input_dtype": str(rgb.dtype),
        "input_pixel_sha256": pixel_sha,
        "candidate_count": len(result.hand_landmarks),
        "api_smoke": "PASS",
        "note": (
            "candidate count is descriptive only; disposable fixture is not a "
            "domain-compatibility or accuracy test"
        ),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", type=Path, required=True)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()

    result = {
        "status": "REFERENCE-ONLY / MEDIAPIPE RUNTIME IDENTITY PROBE",
        "runtime": {
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "sys_executable": sys.executable,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "system": platform.system(),
            "release": platform.release(),
        },
        "package": package_identity(),
        "dependencies": optional_versions(),
        "tasks_api": {
            "BaseOptions": str(mp.tasks.BaseOptions),
            "HandLandmarkerOptions": str(mp.tasks.vision.HandLandmarkerOptions),
            "RunningMode_IMAGE": str(mp.tasks.vision.RunningMode.IMAGE),
        },
        "smoke": smoke(args.model),
        "boundary": {
            "mohi_inference_executed": False,
            "compatibility_result": False,
            "production_threshold": False,
            "production_upgrade_policy": False,
        },
    }

    text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
        print(args.output)
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
