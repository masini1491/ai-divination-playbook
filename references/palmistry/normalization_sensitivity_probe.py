#!/usr/bin/env python3
"""Research-only sensitivity sweep for draft palm normalization.

Cold reference surface: this file is NOT a production runtime owner.
Standard-library only. It imports normalization_probe.py from the same directory.
"""

from __future__ import annotations

from dataclasses import dataclass
import itertools
import math
import sys
from typing import Iterable, Mapping, Sequence

from normalization_probe import (
    INDEX_MCP,
    LITTLE_MCP,
    WRIST,
    PalmBasis,
    Point,
    build_palm_basis,
    dot,
    norm,
    normalize_point,
    synthetic_fixture,
)


DIRECTION_COUNT = 16
PERTURBATION_FRACTIONS = (0.0025, 0.005, 0.01, 0.02, 0.05)
GRID_AXIS = (-0.5, -0.25, 0.0, 0.25, 0.5)
GRID_Y = (0.0, 0.25, 0.5, 0.75, 1.0)


@dataclass(frozen=True)
class SensitivityMetrics:
    axis_angle_deg: float
    width_rel_error: float
    height_rel_error: float
    max_point_drift: float
    mean_point_drift: float


def direction_grid(count: int = DIRECTION_COUNT) -> tuple[Point, ...]:
    return tuple(
        Point(math.cos(2.0 * math.pi * i / count), math.sin(2.0 * math.pi * i / count))
        for i in range(count)
    )


def angle_deg(a: Point, b: Point) -> float:
    denominator = norm(a) * norm(b)
    if denominator == 0:
        raise ValueError("cannot compare zero-length axes")
    cosine = max(-1.0, min(1.0, dot(a, b) / denominator))
    return math.degrees(math.acos(cosine))


def denormalize_point(p: Point, basis: PalmBasis) -> Point:
    return (
        basis.origin
        + basis.ex.scale(p.x * basis.palm_width)
        + basis.ey.scale(p.y * basis.palm_height)
    )


def evaluation_grid(basis: PalmBasis) -> tuple[Point, ...]:
    return tuple(
        denormalize_point(Point(x, y), basis)
        for x in GRID_AXIS
        for y in GRID_Y
    )


def metrics(
    baseline_basis: PalmBasis,
    baseline_points: Sequence[Point],
    perturbed_landmarks: Mapping[int, Point],
) -> SensitivityMetrics:
    perturbed_basis = build_palm_basis(perturbed_landmarks)
    canonical_baseline = tuple(normalize_point(p, baseline_basis) for p in baseline_points)
    canonical_perturbed = tuple(normalize_point(p, perturbed_basis) for p in baseline_points)
    drift = tuple(
        math.hypot(after.x - before.x, after.y - before.y)
        for before, after in zip(canonical_baseline, canonical_perturbed)
    )
    return SensitivityMetrics(
        axis_angle_deg=angle_deg(baseline_basis.ey, perturbed_basis.ey),
        width_rel_error=abs(perturbed_basis.palm_width / baseline_basis.palm_width - 1.0),
        height_rel_error=abs(perturbed_basis.palm_height / baseline_basis.palm_height - 1.0),
        max_point_drift=max(drift),
        mean_point_drift=sum(drift) / len(drift),
    )


def componentwise_max(values: Iterable[SensitivityMetrics]) -> SensitivityMetrics:
    values = tuple(values)
    return SensitivityMetrics(
        axis_angle_deg=max(v.axis_angle_deg for v in values),
        width_rel_error=max(v.width_rel_error for v in values),
        height_rel_error=max(v.height_rel_error for v in values),
        max_point_drift=max(v.max_point_drift for v in values),
        mean_point_drift=max(v.mean_point_drift for v in values),
    )


def perturb_landmark(
    landmarks: Mapping[int, Point],
    landmark_id: int,
    direction: Point,
    magnitude: float,
) -> dict[int, Point]:
    out = dict(landmarks)
    out[landmark_id] = out[landmark_id] + direction.scale(magnitude)
    return out


def single_anchor_sweep(
    fraction: float,
    *,
    directions: Sequence[Point],
) -> dict[int, SensitivityMetrics]:
    landmarks, _ = synthetic_fixture()
    baseline_basis = build_palm_basis(landmarks)
    sample_points = evaluation_grid(baseline_basis)
    magnitude = baseline_basis.palm_width * fraction
    results: dict[int, SensitivityMetrics] = {}
    for landmark_id in (WRIST, INDEX_MCP, LITTLE_MCP):
        results[landmark_id] = componentwise_max(
            metrics(
                baseline_basis,
                sample_points,
                perturb_landmark(landmarks, landmark_id, direction, magnitude),
            )
            for direction in directions
        )
    return results


def simultaneous_anchor_sweep(
    fraction: float,
    *,
    directions: Sequence[Point],
) -> SensitivityMetrics:
    landmarks, _ = synthetic_fixture()
    baseline_basis = build_palm_basis(landmarks)
    sample_points = evaluation_grid(baseline_basis)
    magnitude = baseline_basis.palm_width * fraction

    def cases():
        for d0, d5, d17 in itertools.product(directions, repeat=3):
            yield metrics(
                baseline_basis,
                sample_points,
                {
                    WRIST: landmarks[WRIST] + d0.scale(magnitude),
                    INDEX_MCP: landmarks[INDEX_MCP] + d5.scale(magnitude),
                    LITTLE_MCP: landmarks[LITTLE_MCP] + d17.scale(magnitude),
                },
            )

    return componentwise_max(cases())


def missed_mirror_convention_drift() -> tuple[float, float]:
    """Model a missed detector-only mirror as x -> -x in canonical palm space."""
    canonical_grid = tuple(Point(x, y) for x in GRID_AXIS for y in GRID_Y)
    drift = tuple(abs((-p.x) - p.x) for p in canonical_grid)
    return max(drift), sum(drift) / len(drift)


def pct(value: float) -> str:
    return f"{value * 100.0:.3f}%"


def print_simultaneous_table(directions: Sequence[Point]) -> None:
    print("simultaneous bounded-anchor sweep")
    print(
        "fraction | axis_deg | width_error | height_error | max_coord_drift | mean_coord_drift"
    )
    previous = None
    for fraction in PERTURBATION_FRACTIONS:
        result = simultaneous_anchor_sweep(fraction, directions=directions)
        print(
            f"{fraction * 100:7.2f}% | "
            f"{result.axis_angle_deg:8.4f} | "
            f"{pct(result.width_rel_error):>11} | "
            f"{pct(result.height_rel_error):>12} | "
            f"{pct(result.max_point_drift):>15} | "
            f"{pct(result.mean_point_drift):>16}"
        )
        if previous is not None and result.max_point_drift + 1e-12 < previous:
            raise AssertionError("max coordinate drift should be monotonic over configured sweep")
        previous = result.max_point_drift


def print_single_anchor_one_percent(directions: Sequence[Point]) -> None:
    labels = {
        WRIST: "L0/wrist",
        INDEX_MCP: "L5/index-MCP",
        LITTLE_MCP: "L17/little-MCP",
    }
    results = single_anchor_sweep(0.01, directions=directions)
    print("\nsingle-anchor sweep at 1.00% palm-width perturbation")
    print("anchor | axis_deg | width_error | height_error | max_coord_drift")
    for landmark_id in (WRIST, INDEX_MCP, LITTLE_MCP):
        result = results[landmark_id]
        print(
            f"{labels[landmark_id]:14} | "
            f"{result.axis_angle_deg:8.4f} | "
            f"{pct(result.width_rel_error):>11} | "
            f"{pct(result.height_rel_error):>12} | "
            f"{pct(result.max_point_drift):>15}"
        )


def main() -> int:
    directions = direction_grid()
    print(
        f"direction-grid sweep: {len(directions)} directions per anchor; "
        f"{len(directions) ** 3} simultaneous combinations per perturbation level"
    )
    print(
        "NOTE: grid maximum is deterministic evidence for the configured directions, "
        "not a continuous mathematical worst-case bound.\n"
    )

    print_simultaneous_table(directions)
    print_single_anchor_one_percent(directions)

    max_mirror, mean_mirror = missed_mirror_convention_drift()
    print("\nmissed detector-mirror inverse (canonical x -> -x)")
    print(f"max_coord_drift={pct(max_mirror)} mean_coord_drift={pct(mean_mirror)}")

    # Sanity expectations: these are not production tolerances.
    one_percent = simultaneous_anchor_sweep(0.01, directions=directions)
    if not (1.0 < one_percent.axis_angle_deg < 1.3):
        raise AssertionError("unexpected 1% synthetic axis sensitivity")
    if not (0.02 < one_percent.max_point_drift < 0.023):
        raise AssertionError("unexpected 1% synthetic coordinate sensitivity")
    if max_mirror != 1.0:
        raise AssertionError("unexpected mirror-convention drift")

    print("\nsummary: sensitivity probe PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
