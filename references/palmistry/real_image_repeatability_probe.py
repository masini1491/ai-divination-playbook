#!/usr/bin/env python3
"""Research-only harness for palm-landmark transform repeatability.

Consumes detector-exported L0/L5/L17 landmarks for a baseline image and transformed
variants, maps every variant back into baseline-image coordinates, and reports
frame-level drift. Cold reference surface only; NOT a production runtime owner.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

EPS = 1e-9
WRIST = 0
INDEX_MCP = 5
LITTLE_MCP = 17
REQUIRED = (WRIST, INDEX_MCP, LITTLE_MCP)


class StudyError(ValueError):
    pass


@dataclass(frozen=True)
class Point:
    x: float
    y: float

    def __add__(self, other: "Point") -> "Point":
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Point") -> "Point":
        return Point(self.x - other.x, self.y - other.y)

    def scale(self, factor: float) -> "Point":
        return Point(self.x * factor, self.y * factor)


@dataclass(frozen=True)
class PalmBasis:
    origin: Point
    ex: Point
    ey: Point
    width: float
    height: float


@dataclass(frozen=True)
class VariantMetrics:
    name: str
    max_anchor_drift_fraction: float
    mean_anchor_drift_fraction: float
    axis_angle_deg: float
    width_rel_error: float
    height_rel_error: float
    max_canonical_grid_drift: float
    handedness_changed: bool | None


def dot(a: Point, b: Point) -> float:
    return a.x * b.x + a.y * b.y


def norm(v: Point) -> float:
    return math.hypot(v.x, v.y)


def unit(v: Point, label: str) -> Point:
    n = norm(v)
    if n <= EPS:
        raise StudyError(f"degenerate {label}")
    return Point(v.x / n, v.y / n)


def parse_landmarks(raw: Mapping[str, Sequence[float]]) -> dict[int, Point]:
    out: dict[int, Point] = {}
    for idx in REQUIRED:
        key = str(idx)
        if key not in raw:
            raise StudyError(f"missing landmark {idx}")
        value = raw[key]
        if len(value) != 2:
            raise StudyError(f"landmark {idx} must be [x, y]")
        out[idx] = Point(float(value[0]), float(value[1]))
    return out


def build_basis(landmarks: Mapping[int, Point]) -> PalmBasis:
    l0, l5, l17 = (landmarks[i] for i in REQUIRED)
    midpoint = Point((l5.x + l17.x) / 2.0, (l5.y + l17.y) / 2.0)
    ey = unit(midpoint - l0, "palm-height axis")
    raw_ex = l5 - l17
    orth = raw_ex - ey.scale(dot(raw_ex, ey))
    ex = unit(orth, "palm-width axis")
    width = dot(l5 - l17, ex)
    height = norm(midpoint - l0)
    if width <= EPS or height <= EPS:
        raise StudyError("degenerate palm basis")
    if dot(l5 - midpoint, ex) <= 0:
        ex = ex.scale(-1.0)
        width = -width
    return PalmBasis(l0, ex, ey, abs(width), height)


def normalize_point(p: Point, basis: PalmBasis) -> Point:
    rel = p - basis.origin
    return Point(dot(rel, basis.ex) / basis.width, dot(rel, basis.ey) / basis.height)


def denormalize_point(p: Point, basis: PalmBasis) -> Point:
    return basis.origin + basis.ex.scale(p.x * basis.width) + basis.ey.scale(p.y * basis.height)


def parse_matrix(raw: Sequence[Sequence[float]]) -> tuple[tuple[float, float, float], ...]:
    if len(raw) != 3 or any(len(row) != 3 for row in raw):
        raise StudyError("inverse_transform must be 3x3")
    return tuple(tuple(float(v) for v in row) for row in raw)


def apply_homography(p: Point, h: Sequence[Sequence[float]]) -> Point:
    x = h[0][0] * p.x + h[0][1] * p.y + h[0][2]
    y = h[1][0] * p.x + h[1][1] * p.y + h[1][2]
    w = h[2][0] * p.x + h[2][1] * p.y + h[2][2]
    if abs(w) <= EPS:
        raise StudyError("inverse transform maps point to infinity")
    return Point(x / w, y / w)


def angle_deg(a: Point, b: Point) -> float:
    c = dot(a, b) / (norm(a) * norm(b))
    c = max(-1.0, min(1.0, c))
    return math.degrees(math.acos(c))


def grid_points(basis: PalmBasis) -> tuple[Point, ...]:
    xs = (-0.5, -0.25, 0.0, 0.25, 0.5)
    ys = (0.0, 0.25, 0.5, 0.75, 1.0)
    return tuple(denormalize_point(Point(x, y), basis) for x in xs for y in ys)


def handedness_changed(base: str | None, variant: str | None) -> bool | None:
    if not base or not variant:
        return None
    return base.strip().lower() != variant.strip().lower()


def evaluate_variant(
    baseline_landmarks: Mapping[int, Point],
    baseline_handedness: str | None,
    variant: Mapping[str, object],
) -> VariantMetrics:
    name = str(variant.get("name", "unnamed"))
    landmarks = parse_landmarks(variant["landmarks"])  # type: ignore[index]
    inverse = parse_matrix(variant["inverse_transform"])  # type: ignore[index]
    mapped = {idx: apply_homography(p, inverse) for idx, p in landmarks.items()}

    baseline_basis = build_basis(baseline_landmarks)
    mapped_basis = build_basis(mapped)
    anchor_drift = tuple(
        norm(mapped[idx] - baseline_landmarks[idx]) / baseline_basis.width for idx in REQUIRED
    )

    grid = grid_points(baseline_basis)
    canonical_drift = []
    for raw_point in grid:
        before = normalize_point(raw_point, baseline_basis)
        after = normalize_point(raw_point, mapped_basis)
        canonical_drift.append(norm(after - before))

    return VariantMetrics(
        name=name,
        max_anchor_drift_fraction=max(anchor_drift),
        mean_anchor_drift_fraction=sum(anchor_drift) / len(anchor_drift),
        axis_angle_deg=angle_deg(baseline_basis.ey, mapped_basis.ey),
        width_rel_error=abs(mapped_basis.width / baseline_basis.width - 1.0),
        height_rel_error=abs(mapped_basis.height / baseline_basis.height - 1.0),
        max_canonical_grid_drift=max(canonical_drift),
        handedness_changed=handedness_changed(
            baseline_handedness,
            variant.get("handedness") if isinstance(variant.get("handedness"), str) else None,
        ),
    )


def evaluate_study(study: Mapping[str, object]) -> list[VariantMetrics]:
    baseline = study.get("baseline")
    if not isinstance(baseline, Mapping):
        raise StudyError("missing baseline object")
    landmarks_raw = baseline.get("landmarks")
    if not isinstance(landmarks_raw, Mapping):
        raise StudyError("baseline.landmarks missing")
    baseline_landmarks = parse_landmarks(landmarks_raw)  # type: ignore[arg-type]
    baseline_handedness = baseline.get("handedness") if isinstance(baseline.get("handedness"), str) else None

    variants = study.get("variants")
    if not isinstance(variants, list) or not variants:
        raise StudyError("variants must be a non-empty list")
    results = []
    for variant in variants:
        if not isinstance(variant, Mapping):
            raise StudyError("each variant must be an object")
        results.append(evaluate_variant(baseline_landmarks, baseline_handedness, variant))
    return results


def pct(value: float) -> str:
    return f"{value * 100.0:.4f}%"


def print_results(results: Sequence[VariantMetrics]) -> None:
    print("variant | max_anchor | mean_anchor | axis_deg | width_err | height_err | max_canonical | handedness_changed")
    for r in results:
        print(
            f"{r.name} | {pct(r.max_anchor_drift_fraction)} | {pct(r.mean_anchor_drift_fraction)} | "
            f"{r.axis_angle_deg:.6f} | {pct(r.width_rel_error)} | {pct(r.height_rel_error)} | "
            f"{pct(r.max_canonical_grid_drift)} | {r.handedness_changed}"
        )


def transform_point(p: Point, h: Sequence[Sequence[float]]) -> Point:
    return apply_homography(p, h)


def inverse_affine_rotation(theta_deg: float, tx: float, ty: float) -> tuple[tuple[float, float, float], ...]:
    """Inverse of q = R(theta) p + t."""
    t = math.radians(theta_deg)
    c, s = math.cos(t), math.sin(t)
    return (
        (c, s, -(c * tx + s * ty)),
        (-s, c, -(-s * tx + c * ty)),
        (0.0, 0.0, 1.0),
    )


def self_test() -> None:
    baseline = {
        "0": [0.0, 0.0],
        "5": [2.0, 4.0],
        "17": [-2.0, 4.0],
    }
    theta = 23.0
    tx, ty = 17.0, -8.0
    t = math.radians(theta)
    c, s = math.cos(t), math.sin(t)
    forward = (
        (c, -s, tx),
        (s, c, ty),
        (0.0, 0.0, 1.0),
    )
    transformed = {}
    for key, raw in baseline.items():
        q = transform_point(Point(*raw), forward)
        transformed[key] = [q.x, q.y]

    exact = {
        "name": "exact-rotate-translate",
        "landmarks": transformed,
        "inverse_transform": inverse_affine_rotation(theta, tx, ty),
        "handedness": "right",
    }
    noisy = json.loads(json.dumps(exact))
    noisy["name"] = "exact-plus-wrist-noise"
    noisy["landmarks"]["0"][0] += 0.04

    study = {
        "baseline": {"landmarks": baseline, "handedness": "right"},
        "variants": [exact, noisy],
    }
    results = evaluate_study(study)
    if results[0].max_anchor_drift_fraction > 1e-12:
        raise AssertionError("exact inverse-transform round trip is not stable")
    if results[0].max_canonical_grid_drift > 1e-12:
        raise AssertionError("exact transform changed canonical frame")
    if not (0.009 < results[1].max_anchor_drift_fraction < 0.011):
        raise AssertionError("synthetic 1% anchor displacement was not recovered")
    print_results(results)
    print("\nsummary: real-image repeatability harness self-test PASS")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("study", nargs="?", help="JSON study file exported by a detector runner")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return 0
    if not args.study:
        parser.error("provide a study JSON file or --self-test")
    study = json.loads(Path(args.study).read_text(encoding="utf-8"))
    results = evaluate_study(study)
    print_results(results)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except StudyError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(2)
