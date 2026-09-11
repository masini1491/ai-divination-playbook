#!/usr/bin/env python3
"""Research-only deterministic probe for Palm ROI / coordinate normalization.

Cold reference surface: this file is NOT a production runtime owner.
Standard-library only.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
import sys
from typing import Dict, Mapping, Sequence


EPS = 1e-9
TOL = 1e-9

WRIST = 0
INDEX_MCP = 5
LITTLE_MCP = 17


class NormalizationError(ValueError):
    """Raised when the draft palm basis cannot be constructed safely."""


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
    palm_width: float
    palm_height: float


@dataclass(frozen=True)
class CropResizeTransform:
    crop_x: float
    crop_y: float
    crop_width: float
    crop_height: float
    output_width: float
    output_height: float

    def forward(self, p: Point) -> Point:
        if min(self.crop_width, self.crop_height, self.output_width, self.output_height) <= EPS:
            raise NormalizationError("degenerate crop/resize transform")
        return Point(
            (p.x - self.crop_x) * self.output_width / self.crop_width,
            (p.y - self.crop_y) * self.output_height / self.crop_height,
        )

    def inverse(self, p: Point) -> Point:
        if min(self.crop_width, self.crop_height, self.output_width, self.output_height) <= EPS:
            raise NormalizationError("degenerate crop/resize transform")
        return Point(
            p.x * self.crop_width / self.output_width + self.crop_x,
            p.y * self.crop_height / self.output_height + self.crop_y,
        )


def dot(a: Point, b: Point) -> float:
    return a.x * b.x + a.y * b.y


def norm(v: Point) -> float:
    return math.hypot(v.x, v.y)


def unit(v: Point, *, label: str) -> Point:
    n = norm(v)
    if n <= EPS:
        raise NormalizationError(f"degenerate {label}")
    return Point(v.x / n, v.y / n)


def build_palm_basis(landmarks: Mapping[int, Point]) -> PalmBasis:
    missing = [idx for idx in (WRIST, INDEX_MCP, LITTLE_MCP) if idx not in landmarks]
    if missing:
        raise NormalizationError(f"missing required landmarks: {missing}")

    l0 = landmarks[WRIST]
    l5 = landmarks[INDEX_MCP]
    l17 = landmarks[LITTLE_MCP]
    midpoint = Point((l5.x + l17.x) / 2.0, (l5.y + l17.y) / 2.0)

    ey = unit(midpoint - l0, label="palm height axis")
    raw_ex = l5 - l17
    orth = raw_ex - ey.scale(dot(raw_ex, ey))
    ex = unit(orth, label="palm width axis")

    palm_width = dot(l5 - l17, ex)
    palm_height = norm(midpoint - l0)
    if palm_width <= EPS:
        raise NormalizationError("degenerate palm width")
    if palm_height <= EPS:
        raise NormalizationError("degenerate palm height")

    # ex is constructed from little -> index, so index-side is positive.
    if dot(l5 - midpoint, ex) <= 0:
        ex = ex.scale(-1.0)
        palm_width = -palm_width

    return PalmBasis(l0, ex, ey, abs(palm_width), palm_height)


def normalize_point(p: Point, basis: PalmBasis) -> Point:
    rel = p - basis.origin
    return Point(
        dot(rel, basis.ex) / basis.palm_width,
        dot(rel, basis.ey) / basis.palm_height,
    )


def canonicalize(
    landmarks: Mapping[int, Point],
    points: Sequence[Point],
) -> list[Point]:
    basis = build_palm_basis(landmarks)
    return [normalize_point(p, basis) for p in points]


def translate(p: Point, delta: Point) -> Point:
    return p + delta


def rotate(p: Point, angle_radians: float, origin: Point = Point(0.0, 0.0)) -> Point:
    q = p - origin
    c = math.cos(angle_radians)
    s = math.sin(angle_radians)
    return Point(q.x * c - q.y * s, q.x * s + q.y * c) + origin


def mirror_x(p: Point, axis_x: float = 0.0) -> Point:
    return Point(2.0 * axis_x - p.x, p.y)


def detector_mirror_x(p: Point, width: float) -> Point:
    if width <= EPS:
        raise NormalizationError("degenerate detector width")
    return Point(width - p.x, p.y)


def perspective_mapping_allowed(
    foreshortening: str,
    *,
    reliable_rectifier: bool,
) -> bool:
    if foreshortening in {"material", "severe"} and not reliable_rectifier:
        return False
    return True


def select_target_hand(
    hands: Mapping[str, Mapping[int, Point]],
    target_hand_id: str | None,
) -> Mapping[int, Point]:
    if target_hand_id is None:
        raise NormalizationError("target hand is ambiguous or not selected")
    if target_hand_id not in hands:
        raise NormalizationError(f"unknown target hand: {target_hand_id}")
    return hands[target_hand_id]


def assert_close(a: Point, b: Point, tol: float = TOL) -> None:
    if abs(a.x - b.x) > tol or abs(a.y - b.y) > tol:
        raise AssertionError(f"{a!r} != {b!r} within {tol}")


def assert_point_lists_close(a: Sequence[Point], b: Sequence[Point], tol: float = TOL) -> None:
    if len(a) != len(b):
        raise AssertionError(f"length mismatch: {len(a)} != {len(b)}")
    for left, right in zip(a, b):
        assert_close(left, right, tol)


def expect_normalization_error(fn, contains: str | None = None) -> None:
    try:
        fn()
    except NormalizationError as exc:
        if contains is not None and contains not in str(exc):
            raise AssertionError(f"expected error containing {contains!r}, got {exc!r}")
        return
    raise AssertionError("expected NormalizationError")


def synthetic_fixture() -> tuple[Dict[int, Point], list[Point]]:
    landmarks = {
        WRIST: Point(0.0, 0.0),
        INDEX_MCP: Point(2.0, 4.0),
        LITTLE_MCP: Point(-2.0, 4.0),
    }
    points = [
        Point(0.0, 2.0),
        Point(1.25, 3.0),
        Point(-0.75, 1.25),
        Point(0.4, 3.6),
    ]
    return landmarks, points


def test_basis_anchor_expectations() -> None:
    landmarks, _ = synthetic_fixture()
    basis = build_palm_basis(landmarks)
    assert_close(normalize_point(landmarks[WRIST], basis), Point(0.0, 0.0))
    assert_close(normalize_point(Point(0.0, 4.0), basis), Point(0.0, 1.0))
    assert_close(normalize_point(landmarks[INDEX_MCP], basis), Point(0.5, 1.0))
    assert_close(normalize_point(landmarks[LITTLE_MCP], basis), Point(-0.5, 1.0))


def test_translation_invariance() -> None:
    landmarks, points = synthetic_fixture()
    baseline = canonicalize(landmarks, points)
    delta = Point(137.25, -42.5)
    moved_landmarks = {k: translate(v, delta) for k, v in landmarks.items()}
    moved_points = [translate(p, delta) for p in points]
    assert_point_lists_close(baseline, canonicalize(moved_landmarks, moved_points))


def test_rotation_invariance() -> None:
    landmarks, points = synthetic_fixture()
    baseline = canonicalize(landmarks, points)
    angle = math.radians(37.0)
    rotated_landmarks = {k: rotate(v, angle) for k, v in landmarks.items()}
    rotated_points = [rotate(p, angle) for p in points]
    assert_point_lists_close(baseline, canonicalize(rotated_landmarks, rotated_points))


def test_uniform_scale_invariance() -> None:
    landmarks, points = synthetic_fixture()
    baseline = canonicalize(landmarks, points)
    factor = 3.7
    scaled_landmarks = {k: v.scale(factor) for k, v in landmarks.items()}
    scaled_points = [p.scale(factor) for p in points]
    assert_point_lists_close(baseline, canonicalize(scaled_landmarks, scaled_points))


def test_mirror_chirality_invariance_when_labels_preserved() -> None:
    landmarks, points = synthetic_fixture()
    baseline = canonicalize(landmarks, points)
    mirrored_landmarks = {k: mirror_x(v) for k, v in landmarks.items()}
    mirrored_points = [mirror_x(p) for p in points]
    assert_point_lists_close(baseline, canonicalize(mirrored_landmarks, mirrored_points))


def test_detector_mirror_round_trip() -> None:
    _, points = synthetic_fixture()
    width = 512.0
    round_trip = [detector_mirror_x(detector_mirror_x(p, width), width) for p in points]
    assert_point_lists_close(points, round_trip)


def test_crop_resize_round_trip() -> None:
    _, points = synthetic_fixture()
    transform = CropResizeTransform(
        crop_x=-2.0,
        crop_y=-1.0,
        crop_width=6.0,
        crop_height=7.0,
        output_width=512.0,
        output_height=512.0,
    )
    round_trip = [transform.inverse(transform.forward(p)) for p in points]
    assert_point_lists_close(points, round_trip)


def test_missing_anchor_fails_closed() -> None:
    landmarks, _ = synthetic_fixture()
    bad = dict(landmarks)
    bad.pop(INDEX_MCP)
    expect_normalization_error(lambda: build_palm_basis(bad), "missing required landmarks")


def test_degenerate_axes_fail_closed() -> None:
    expect_normalization_error(
        lambda: build_palm_basis({
            WRIST: Point(0.0, 0.0),
            INDEX_MCP: Point(1.0, 0.0),
            LITTLE_MCP: Point(-1.0, 0.0),
        }),
        "palm height axis",
    )
    expect_normalization_error(
        lambda: build_palm_basis({
            WRIST: Point(0.0, 0.0),
            INDEX_MCP: Point(0.0, 4.0),
            LITTLE_MCP: Point(0.0, 4.0),
        }),
        "palm width axis",
    )


def test_multi_hand_target_selection() -> None:
    landmarks, _ = synthetic_fixture()
    other = {k: translate(v, Point(100.0, 50.0)) for k, v in landmarks.items()}
    hands = {"hand-001": landmarks, "hand-002": other}
    selected = select_target_hand(hands, "hand-002")
    if selected is not other:
        raise AssertionError("selected target hand was not returned")
    expect_normalization_error(lambda: select_target_hand(hands, None), "ambiguous")
    expect_normalization_error(lambda: select_target_hand(hands, "hand-999"), "unknown target hand")


def test_material_perspective_fails_closed_without_rectifier() -> None:
    if perspective_mapping_allowed("material", reliable_rectifier=False):
        raise AssertionError("material foreshortening must block fine mapping without rectifier")
    if perspective_mapping_allowed("severe", reliable_rectifier=False):
        raise AssertionError("severe foreshortening must block fine mapping without rectifier")
    if not perspective_mapping_allowed("mild", reliable_rectifier=False):
        raise AssertionError("mild foreshortening should not be categorically blocked")
    if not perspective_mapping_allowed("material", reliable_rectifier=True):
        raise AssertionError("reliable rectifier should allow material perspective mapping")


TESTS = [
    test_basis_anchor_expectations,
    test_translation_invariance,
    test_rotation_invariance,
    test_uniform_scale_invariance,
    test_mirror_chirality_invariance_when_labels_preserved,
    test_detector_mirror_round_trip,
    test_crop_resize_round_trip,
    test_missing_anchor_fails_closed,
    test_degenerate_axes_fail_closed,
    test_multi_hand_target_selection,
    test_material_perspective_fails_closed_without_rectifier,
]


def main() -> int:
    failures = 0
    for test in TESTS:
        try:
            test()
        except Exception as exc:  # probe runner intentionally reports all cases
            failures += 1
            print(f"FAIL {test.__name__}: {exc}")
        else:
            print(f"PASS {test.__name__}")

    print(f"\nsummary: {len(TESTS) - failures} passed, {failures} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
