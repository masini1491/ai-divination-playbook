#!/usr/bin/env python3
"""Deterministic validator for palm capture/mirroring/anatomical-side contract.

REFERENCE-ONLY research executable. Standard-library only.
It validates transform lineage and capability-state behavior; it does not
infer anatomical side from detector metadata and does not inspect real images.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any, Callable


TOL = 1e-12

POINTS = {
    "wrist": (0.46, 0.88),
    "index_mcp": (0.72, 0.48),
    "little_mcp": (0.24, 0.53),
    "index_tip": (0.82, 0.11),
    "little_tip": (0.13, 0.20),
    "thumb_tip": (0.91, 0.57),
    "mark_a": (0.64, 0.67),
}

EXIF_INVERSE = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 8, 7: 7, 8: 6}


def exif_transform(code: int, p: tuple[float, float]) -> tuple[float, float]:
    x, y = p
    if code == 1:
        return x, y
    if code == 2:
        return 1.0 - x, y
    if code == 3:
        return 1.0 - x, 1.0 - y
    if code == 4:
        return x, 1.0 - y
    if code == 5:
        return y, x
    if code == 6:
        return 1.0 - y, x
    if code == 7:
        return 1.0 - y, 1.0 - x
    if code == 8:
        return y, 1.0 - x
    raise ValueError(f"unsupported EXIF orientation code: {code}")


def horizontal_mirror(p: tuple[float, float]) -> tuple[float, float]:
    x, y = p
    return 1.0 - x, y


def map_points(fn: Callable[[tuple[float, float]], tuple[float, float]], points: dict[str, tuple[float, float]]) -> dict[str, tuple[float, float]]:
    return {k: fn(v) for k, v in points.items()}


def max_point_delta(a: dict[str, tuple[float, float]], b: dict[str, tuple[float, float]]) -> float:
    if set(a) != set(b):
        raise ValueError("point labels differ")
    return max(math.hypot(a[k][0] - b[k][0], a[k][1] - b[k][1]) for k in a)


def exif_round_trip(code: int) -> float:
    transformed = map_points(lambda p: exif_transform(code, p), POINTS)
    inverse = EXIF_INVERSE[code]
    recovered = map_points(lambda p: exif_transform(inverse, p), transformed)
    return max_point_delta(POINTS, recovered)


def model_mirror_round_trip() -> float:
    mirrored = map_points(horizontal_mirror, POINTS)
    recovered = map_points(horizontal_mirror, mirrored)
    return max_point_delta(POINTS, recovered)


def capability_state(
    *,
    mirrored_for_model: bool | None,
    inverse_model_mirror_applied: bool | None,
    inverse_mapping_verified: bool | None,
    explicit_side: str | None,
    detector_handedness: str | None,
    preview_mirrored: bool | None,
    stored_file_mirror_state: str,
    exif_state_ok: bool,
    detector_score: float | None = None,
) -> dict[str, Any]:
    del detector_score  # deliberately non-authoritative for hard-blocker rescue

    stored_geometry = "admitted"

    model_lineage_ok = (
        mirrored_for_model is False
        or (
            mirrored_for_model is True
            and inverse_model_mirror_applied is True
            and inverse_mapping_verified is True
        )
    )

    if mirrored_for_model is None:
        model_lineage_ok = False

    geometry_ok = bool(exif_state_ok and model_lineage_ok)

    raw_geometry = "admitted" if geometry_ok else "unresolved"
    canonical_geometry = "admitted" if geometry_ok else "unresolved"

    side_authority = explicit_side if explicit_side in {"left", "right"} else None
    anatomical_side = side_authority if side_authority is not None else "unresolved"

    metadata_conflict = bool(
        side_authority is not None
        and detector_handedness in {"Left", "Right"}
        and detector_handedness.lower() != side_authority
    )

    tradition_side_projection = "admitted" if side_authority is not None else "unresolved"

    return {
        "stored_frame_geometry": stored_geometry,
        "raw_image_geometry": raw_geometry,
        "canonical_hand_geometry": canonical_geometry,
        "anatomical_side": anatomical_side,
        "tradition_side_projection": tradition_side_projection,
        "detector_handedness": detector_handedness,
        "detector_metadata_conflict": metadata_conflict,
        "preview_mirrored": preview_mirrored,
        "stored_file_mirror_state": stored_file_mirror_state,
        "model_lineage_ok": model_lineage_ok,
        "exif_state_ok": exif_state_ok,
    }


def expect_equal(observed: Any, expected: Any, label: str, failures: list[str]) -> None:
    if observed != expected:
        failures.append(f"{label}: expected={expected!r} observed={observed!r}")


def expect_true(value: bool, label: str, failures: list[str]) -> None:
    if not value:
        failures.append(f"{label}: expected true")


def run_case(case_id: str) -> dict[str, Any]:
    failures: list[str] = []
    diagnostics: dict[str, Any] = {}
    violations: list[str] = []

    if case_id == "A":
        observed = capability_state(
            mirrored_for_model=False,
            inverse_model_mirror_applied=None,
            inverse_mapping_verified=True,
            explicit_side="right",
            detector_handedness="Right",
            preview_mirrored=False,
            stored_file_mirror_state="not_mirrored",
            exif_state_ok=True,
        )
        expect_equal(observed["raw_image_geometry"], "admitted", "raw geometry", failures)
        expect_equal(observed["canonical_hand_geometry"], "admitted", "canonical geometry", failures)
        expect_equal(observed["anatomical_side"], "right", "anatomical side", failures)
        expect_equal(observed["tradition_side_projection"], "admitted", "tradition projection", failures)

    elif case_id == "B":
        baseline = capability_state(
            mirrored_for_model=False,
            inverse_model_mirror_applied=None,
            inverse_mapping_verified=True,
            explicit_side="right",
            detector_handedness="Right",
            preview_mirrored=False,
            stored_file_mirror_state="not_mirrored",
            exif_state_ok=True,
        )
        observed = capability_state(
            mirrored_for_model=False,
            inverse_model_mirror_applied=None,
            inverse_mapping_verified=True,
            explicit_side="right",
            detector_handedness="Right",
            preview_mirrored=True,
            stored_file_mirror_state="not_mirrored",
            exif_state_ok=True,
        )
        for key in ("stored_frame_geometry", "raw_image_geometry", "canonical_hand_geometry", "anatomical_side"):
            expect_equal(observed[key], baseline[key], f"preview must not mutate {key}", failures)
        if any(observed[k] != baseline[k] for k in ("stored_frame_geometry", "raw_image_geometry", "canonical_hand_geometry", "anatomical_side")):
            violations.append("preview_to_stored_frame_leakage")

    elif case_id == "C":
        observed = capability_state(
            mirrored_for_model=False,
            inverse_model_mirror_applied=None,
            inverse_mapping_verified=True,
            explicit_side="right",
            detector_handedness="Left",
            preview_mirrored=True,
            stored_file_mirror_state="mirrored",
            exif_state_ok=True,
        )
        expect_equal(observed["stored_frame_geometry"], "admitted", "stored geometry", failures)
        expect_equal(observed["canonical_hand_geometry"], "admitted", "canonical geometry", failures)
        expect_equal(observed["anatomical_side"], "right", "explicit side survives stored mirror", failures)
        expect_true(observed["detector_metadata_conflict"], "metadata conflict retained", failures)

    elif case_id == "D":
        delta = model_mirror_round_trip()
        diagnostics["model_mirror_round_trip_max_delta"] = delta
        observed = capability_state(
            mirrored_for_model=True,
            inverse_model_mirror_applied=True,
            inverse_mapping_verified=True,
            explicit_side="right",
            detector_handedness="Left",
            preview_mirrored=False,
            stored_file_mirror_state="not_mirrored",
            exif_state_ok=True,
        )
        expect_true(delta <= TOL, "model mirror round trip", failures)
        expect_equal(observed["raw_image_geometry"], "admitted", "raw geometry", failures)
        expect_equal(observed["canonical_hand_geometry"], "admitted", "canonical geometry", failures)

    elif case_id == "E":
        observed = capability_state(
            mirrored_for_model=True,
            inverse_model_mirror_applied=False,
            inverse_mapping_verified=False,
            explicit_side="right",
            detector_handedness="Right",
            preview_mirrored=False,
            stored_file_mirror_state="not_mirrored",
            exif_state_ok=True,
            detector_score=0.999,
        )
        expect_equal(observed["raw_image_geometry"], "unresolved", "raw geometry fail closed", failures)
        expect_equal(observed["canonical_hand_geometry"], "unresolved", "canonical geometry fail closed", failures)
        if observed["raw_image_geometry"] != "unresolved" or observed["canonical_hand_geometry"] != "unresolved":
            violations.append("hard_blocker_rescue")

    elif case_id == "F":
        observed = capability_state(
            mirrored_for_model=None,
            inverse_model_mirror_applied=None,
            inverse_mapping_verified=None,
            explicit_side="right",
            detector_handedness="Right",
            preview_mirrored=None,
            stored_file_mirror_state="unknown",
            exif_state_ok=True,
            detector_score=0.999,
        )
        expect_equal(observed["raw_image_geometry"], "unresolved", "unknown mirror raw geometry", failures)
        expect_equal(observed["canonical_hand_geometry"], "unresolved", "unknown mirror canonical geometry", failures)
        if observed["raw_image_geometry"] != "unresolved" or observed["canonical_hand_geometry"] != "unresolved":
            violations.append("hard_blocker_rescue")

    elif case_id == "G":
        delta = exif_round_trip(6)
        diagnostics["exif_code"] = 6
        diagnostics["round_trip_max_delta"] = delta
        observed = capability_state(
            mirrored_for_model=False,
            inverse_model_mirror_applied=None,
            inverse_mapping_verified=True,
            explicit_side="right",
            detector_handedness="Right",
            preview_mirrored=False,
            stored_file_mirror_state="not_mirrored",
            exif_state_ok=delta <= TOL,
        )
        expect_true(delta <= TOL, "EXIF 6 round trip", failures)
        expect_equal(observed["canonical_hand_geometry"], "admitted", "canonical geometry", failures)

    elif case_id == "H":
        once = map_points(lambda p: exif_transform(6, p), POINTS)
        twice = map_points(lambda p: exif_transform(6, p), once)
        delta = max_point_delta(once, twice)
        diagnostics["once_vs_twice_max_delta"] = delta
        observed = capability_state(
            mirrored_for_model=False,
            inverse_model_mirror_applied=None,
            inverse_mapping_verified=True,
            explicit_side="right",
            detector_handedness="Right",
            preview_mirrored=False,
            stored_file_mirror_state="not_mirrored",
            exif_state_ok=False,
        )
        expect_true(delta > TOL, "double EXIF application must differ from exactly-once", failures)
        expect_equal(observed["raw_image_geometry"], "unresolved", "double EXIF raw geometry", failures)
        expect_equal(observed["canonical_hand_geometry"], "unresolved", "double EXIF canonical geometry", failures)

    elif case_id == "I":
        deltas = {code: exif_round_trip(code) for code in (2, 5, 7)}
        diagnostics["reflection_exif_round_trip_max_delta"] = deltas
        observed = capability_state(
            mirrored_for_model=False,
            inverse_model_mirror_applied=None,
            inverse_mapping_verified=True,
            explicit_side="left",
            detector_handedness="Right",
            preview_mirrored=False,
            stored_file_mirror_state="mirrored",
            exif_state_ok=all(v <= TOL for v in deltas.values()),
        )
        for code, delta in deltas.items():
            expect_true(delta <= TOL, f"EXIF {code} reflection round trip", failures)
        expect_equal(observed["canonical_hand_geometry"], "admitted", "reflection-aware geometry", failures)

    elif case_id == "J":
        observed = capability_state(
            mirrored_for_model=False,
            inverse_model_mirror_applied=None,
            inverse_mapping_verified=True,
            explicit_side="right",
            detector_handedness="Left",
            preview_mirrored=False,
            stored_file_mirror_state="not_mirrored",
            exif_state_ok=True,
        )
        expect_equal(observed["anatomical_side"], "right", "explicit side authority", failures)
        expect_true(observed["detector_metadata_conflict"], "conflict flag", failures)
        if observed["anatomical_side"] != "right":
            violations.append("detector_handedness_authority")

    elif case_id == "K":
        observed = capability_state(
            mirrored_for_model=False,
            inverse_model_mirror_applied=None,
            inverse_mapping_verified=True,
            explicit_side=None,
            detector_handedness="Right",
            preview_mirrored=False,
            stored_file_mirror_state="not_mirrored",
            exif_state_ok=True,
        )
        expect_equal(observed["anatomical_side"], "unresolved", "detector-only side must be unresolved", failures)
        expect_equal(observed["tradition_side_projection"], "unresolved", "side-dependent tradition projection", failures)
        if observed["anatomical_side"] != "unresolved":
            violations.append("detector_handedness_authority")

    elif case_id == "L":
        observed = capability_state(
            mirrored_for_model=False,
            inverse_model_mirror_applied=None,
            inverse_mapping_verified=True,
            explicit_side=None,
            detector_handedness=None,
            preview_mirrored=None,
            stored_file_mirror_state="unknown",
            exif_state_ok=True,
        )
        expect_equal(observed["raw_image_geometry"], "admitted", "raw geometry independent of side", failures)
        expect_equal(observed["canonical_hand_geometry"], "admitted", "canonical geometry independent of side", failures)
        expect_equal(observed["anatomical_side"], "unresolved", "side unresolved", failures)
        expect_equal(observed["tradition_side_projection"], "unresolved", "side-dependent projection unresolved", failures)
        if observed["raw_image_geometry"] != "admitted" or observed["canonical_hand_geometry"] != "admitted":
            violations.append("side_uncertainty_overblocking")

    else:
        raise ValueError(case_id)

    return {
        "case_id": case_id,
        "pass": not failures,
        "failures": failures,
        "violations": violations,
        "diagnostics": diagnostics,
        "observed": observed,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    cases = [run_case(x) for x in "ABCDEFGHIJKL"]

    violation_counts = {
        "transform_round_trip_failures": 0,
        "hard_blocker_rescue_failures": 0,
        "detector_handedness_authority_violations": 0,
        "preview_to_stored_frame_leakage_violations": 0,
        "side_uncertainty_overblocking_violations": 0,
    }

    for case in cases:
        if case["case_id"] in {"D", "G", "I"} and not case["pass"]:
            violation_counts["transform_round_trip_failures"] += 1
        for v in case["violations"]:
            if v == "hard_blocker_rescue":
                violation_counts["hard_blocker_rescue_failures"] += 1
            elif v == "detector_handedness_authority":
                violation_counts["detector_handedness_authority_violations"] += 1
            elif v == "preview_to_stored_frame_leakage":
                violation_counts["preview_to_stored_frame_leakage_violations"] += 1
            elif v == "side_uncertainty_overblocking":
                violation_counts["side_uncertainty_overblocking_violations"] += 1

    result = {
        "status": "REFERENCE-ONLY / CAPTURE-MIRRORING-ANATOMICAL-SIDE CONTRACT VALIDATION RAW EVIDENCE",
        "tolerance": TOL,
        "synthetic_fixture": {k: list(v) for k, v in POINTS.items()},
        "cases_total": len(cases),
        "cases_pass": sum(1 for c in cases if c["pass"]),
        "cases_fail": sum(1 for c in cases if not c["pass"]),
        **violation_counts,
        "cases": cases,
        "boundary": {
            "real_camera_pipeline_empirically_validated": False,
            "detector_handedness_anatomical_authority": False,
            "production_threshold": False,
            "production_routing": False,
            "biometric_identity_claim": False,
        },
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({k: result[k] for k in (
        "status",
        "cases_total",
        "cases_pass",
        "cases_fail",
        "transform_round_trip_failures",
        "hard_blocker_rescue_failures",
        "detector_handedness_authority_violations",
        "preview_to_stored_frame_leakage_violations",
        "side_uncertainty_overblocking_violations",
    )}, ensure_ascii=False, indent=2))
    print(out)

    if result["cases_fail"] != 0 or any(violation_counts.values()):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
