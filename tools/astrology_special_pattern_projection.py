#!/usr/bin/env python3
"""Bounded deterministic projection for Yod, Stellium, and Grand Quintile."""
from __future__ import annotations

import argparse
import itertools
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

from tools.astrology_aspect_projection import CORE, PARTICIPANT_POLICIES as EXTENDED_PARTICIPANT_POLICIES
from tools.astrology_runtime import gate_bundle

SCHEMA_NAME = "astrology_special_pattern_projection"
SCHEMA_VERSION = "1.0.0"

CORE_PARTICIPANT_POLICY_ID = "aspect-participants-core-bodies-v1"
ASPECT_POLICY_ID = "pattern-aspects-yod-quintile-v1"
ORB_POLICY_ID = "pattern-aspect-orbs-yod-quintile-v1"
PATTERN_POLICY_ID = "special-pattern-topology-yod-stellium-grand-quintile-v1"
STELLIUM_POLICY_ID = "stellium-planets-same-sign-span10-min3-v1"
CLUSTER_POLICY_ID = "conjunction-clusters-transitive-v1"
PROJECTION_POLICY_ID = "pattern-projection-report-all-valid-v1"

PARTICIPANT_POLICIES: dict[str, dict[str, Any]] = {
    CORE_PARTICIPANT_POLICY_ID: {
        "object_ids": CORE,
        "exact_birth_time_required": False,
    },
    **EXTENDED_PARTICIPANT_POLICIES,
}

ASPECT_TARGETS_DEG = {
    "conjunction": 0.0,
    "sextile": 60.0,
    "quincunx": 150.0,
    "quintile": 72.0,
    "biquintile": 144.0,
}
MAX_ORB_DEGREES = {
    "conjunction": 8.0,
    "sextile": 5.0,
    "quincunx": 3.0,
    "quintile": 2.0,
    "biquintile": 2.0,
}

STELLIUM_ELIGIBLE_OBJECT_IDS = (
    "Sun", "Moon", "Mercury", "Venus", "Mars",
    "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto",
)
STELLIUM_MIN_COUNT = 3
STELLIUM_MAX_SPAN_DEG = 10.0
STELLIUM_SIGN_BOUNDARY_POLICY = "same_zodiac_sign_required"

YOD_TEMPLATE = (
    (0, 1, "quincunx"),
    (0, 2, "sextile"),
    (1, 2, "quincunx"),
)
GRAND_QUINTILE_TEMPLATE = (
    (0, 1, "quintile"),
    (1, 2, "quintile"),
    (2, 3, "quintile"),
    (3, 4, "quintile"),
    (4, 0, "quintile"),
    (0, 2, "biquintile"),
    (1, 3, "biquintile"),
    (2, 4, "biquintile"),
    (3, 0, "biquintile"),
    (4, 1, "biquintile"),
)


class SpecialPatternProjectionError(ValueError):
    pass


class _UnionFind:
    def __init__(self, values: list[str]) -> None:
        self.parent = {value: value for value in values}

    def find(self, value: str) -> str:
        parent = self.parent[value]
        if parent != value:
            self.parent[value] = self.find(parent)
        return self.parent[value]

    def union(self, left: str, right: str) -> None:
        a, b = self.find(left), self.find(right)
        if a == b:
            return
        lo, hi = sorted((a, b))
        self.parent[hi] = lo


def _signed_delta(left: float, right: float) -> float:
    return (right - left + 180.0) % 360.0 - 180.0


def _aspect(left: float, right: float) -> tuple[str, float] | None:
    separation = abs(_signed_delta(left, right))
    candidates = [
        (name, abs(separation - target))
        for name, target in ASPECT_TARGETS_DEG.items()
    ]
    name, orb = min(candidates, key=lambda row: (row[1], row[0]))
    return (name, orb) if orb <= MAX_ORB_DEGREES[name] else None


def _facts_by_object_id(
    bundle: dict[str, Any],
    required: tuple[str, ...],
) -> dict[str, dict[str, Any]]:
    rows = bundle.get("facts", {}).get("objects", [])
    by_id: dict[str, dict[str, Any]] = {}
    for row in rows if isinstance(rows, list) else []:
        if not isinstance(row, dict):
            continue
        object_id = row.get("object_id")
        longitude = row.get("longitude_deg")
        fact_id = row.get("fact_id")
        if (
            isinstance(object_id, str)
            and isinstance(fact_id, str)
            and not isinstance(longitude, bool)
            and isinstance(longitude, (int, float))
            and math.isfinite(float(longitude))
        ):
            if object_id in by_id:
                raise SpecialPatternProjectionError(
                    f"duplicate admitted participant object identity: {object_id}"
                )
            by_id[object_id] = {
                "fact_id": fact_id,
                "longitude_deg": float(longitude) % 360.0,
            }
    missing = [object_id for object_id in required if object_id not in by_id]
    if missing:
        raise SpecialPatternProjectionError(
            "admitted participant fact(s) unavailable: " + ", ".join(missing)
        )
    return by_id


def _qualified_aspects(
    required: tuple[str, ...],
    by_id: dict[str, dict[str, Any]],
    participant_policy_id: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for left, right in itertools.combinations(required, 2):
        hit = _aspect(by_id[left]["longitude_deg"], by_id[right]["longitude_deg"])
        if hit is None:
            continue
        name, orb = hit
        rows.append({
            "aspect_id": (
                f"special-aspect:{participant_policy_id}:"
                f"{left.lower()}:{name}:{right.lower()}"
            ),
            "left_object_id": left,
            "right_object_id": right,
            "aspect": name,
            "orb_deg": orb,
        })
    return rows


def _cluster_graph(
    required: tuple[str, ...],
    aspect_rows: list[dict[str, Any]],
) -> tuple[list[tuple[str, ...]], dict[tuple[int, int], dict[str, set[str]]]]:
    uf = _UnionFind(list(required))
    for row in aspect_rows:
        if row["aspect"] == "conjunction":
            uf.union(row["left_object_id"], row["right_object_id"])

    members: dict[str, set[str]] = defaultdict(set)
    for object_id in sorted(required):
        members[uf.find(object_id)].add(object_id)
    clusters = sorted(
        (tuple(sorted(group)) for group in members.values()),
        key=lambda group: group,
    )
    index = {
        object_id: i
        for i, group in enumerate(clusters)
        for object_id in group
    }

    edge_map: dict[tuple[int, int], dict[str, set[str]]] = defaultdict(
        lambda: defaultdict(set)
    )
    for row in aspect_rows:
        left = index[row["left_object_id"]]
        right = index[row["right_object_id"]]
        if left == right:
            continue
        edge_map[tuple(sorted((left, right)))][row["aspect"]].add(row["aspect_id"])
    return clusters, edge_map


def _support(
    ordered: tuple[int, ...],
    template: tuple[tuple[int, int, str], ...],
    edge_map: dict[tuple[int, int], dict[str, set[str]]],
) -> tuple[str, ...] | None:
    supporting: set[str] = set()
    for left_pos, right_pos, aspect in template:
        left = ordered[left_pos]
        right = ordered[right_pos]
        hits = edge_map.get(tuple(sorted((left, right))), {}).get(aspect, set())
        if not hits:
            return None
        supporting.update(hits)
    return tuple(sorted(supporting))


def _edge_defined_patterns(
    clusters: list[tuple[str, ...]],
    edge_map: dict[tuple[int, int], dict[str, set[str]]],
) -> list[dict[str, Any]]:
    specs = (
        ("Yod", 3, YOD_TEMPLATE),
        ("Grand Quintile", 5, GRAND_QUINTILE_TEMPLATE),
    )
    found: dict[tuple[str, tuple[int, ...]], dict[str, Any]] = {}
    for pattern_type, count, template in specs:
        for combo in itertools.combinations(range(len(clusters)), count):
            best: dict[str, Any] | None = None
            for ordered in itertools.permutations(combo):
                supporting = _support(ordered, template, edge_map)
                if supporting is None:
                    continue
                candidate = {
                    "pattern_type": pattern_type,
                    "cluster_indices": tuple(sorted(combo)),
                    "ordered_cluster_indices": tuple(ordered),
                    "supporting_aspect_ids": supporting,
                }
                if best is None or (
                    candidate["ordered_cluster_indices"],
                    candidate["supporting_aspect_ids"],
                ) < (
                    best["ordered_cluster_indices"],
                    best["supporting_aspect_ids"],
                ):
                    best = candidate
            if best is not None:
                found[(pattern_type, tuple(sorted(combo)))] = best
    return sorted(
        found.values(),
        key=lambda row: (row["pattern_type"], row["cluster_indices"]),
    )


def _stellium_groups(by_id: dict[str, dict[str, Any]]) -> list[tuple[str, ...]]:
    candidates: list[frozenset[str]] = []
    for sign_index in range(12):
        lower = sign_index * 30.0
        upper = lower + 30.0
        in_sign = [
            object_id
            for object_id in STELLIUM_ELIGIBLE_OBJECT_IDS
            if object_id in by_id
            and lower <= by_id[object_id]["longitude_deg"] < upper
        ]
        for count in range(STELLIUM_MIN_COUNT, len(in_sign) + 1):
            for combo in itertools.combinations(sorted(in_sign), count):
                longitudes = [
                    by_id[object_id]["longitude_deg"]
                    for object_id in combo
                ]
                if max(longitudes) - min(longitudes) <= STELLIUM_MAX_SPAN_DEG:
                    candidates.append(frozenset(combo))

    maximal = [
        group
        for group in candidates
        if not any(group < other for other in candidates)
    ]
    return sorted({tuple(sorted(group)) for group in maximal})


def build_special_pattern_projection(
    bundle: dict[str, Any],
    *,
    participant_policy_id: str,
    aspect_policy_id: str,
    orb_policy_id: str,
    pattern_policy_id: str,
    stellium_policy_id: str,
    pattern_projection_policy_id: str,
) -> dict[str, Any]:
    policy = PARTICIPANT_POLICIES.get(participant_policy_id)
    if policy is None:
        raise SpecialPatternProjectionError(
            "explicit admitted participant policy required"
        )
    if aspect_policy_id != ASPECT_POLICY_ID:
        raise SpecialPatternProjectionError(
            f"explicit admitted aspect policy required: {ASPECT_POLICY_ID}"
        )
    if orb_policy_id != ORB_POLICY_ID:
        raise SpecialPatternProjectionError(
            f"explicit admitted orb policy required: {ORB_POLICY_ID}"
        )
    if pattern_policy_id != PATTERN_POLICY_ID:
        raise SpecialPatternProjectionError(
            f"explicit admitted pattern policy required: {PATTERN_POLICY_ID}"
        )
    if stellium_policy_id != STELLIUM_POLICY_ID:
        raise SpecialPatternProjectionError(
            f"explicit admitted stellium policy required: {STELLIUM_POLICY_ID}"
        )
    if pattern_projection_policy_id != PROJECTION_POLICY_ID:
        raise SpecialPatternProjectionError(
            "explicit admitted pattern projection policy required: "
            + PROJECTION_POLICY_ID
        )

    gate = gate_bundle(bundle)
    if gate.get("status") != "admitted" or bundle.get("reading_mode") != "natal":
        raise SpecialPatternProjectionError(
            "special pattern projection requires an admitted natal Astrology fact bundle"
        )
    if (
        policy["exact_birth_time_required"]
        and bundle.get("birth_time_certainty") != "exact"
    ):
        raise SpecialPatternProjectionError(
            f"{participant_policy_id} requires exact birth time"
        )

    required = tuple(policy["object_ids"])
    by_id = _facts_by_object_id(bundle, required)
    aspects = _qualified_aspects(required, by_id, participant_policy_id)
    clusters, edge_map = _cluster_graph(required, aspects)

    patterns: list[dict[str, Any]] = []
    for row in _edge_defined_patterns(clusters, edge_map):
        ordered = row["ordered_cluster_indices"]
        patterns.append({
            "pattern_type": row["pattern_type"],
            "participant_object_ids": sorted({
                object_id
                for index in ordered
                for object_id in clusters[index]
            }),
            "vertex_clusters": [list(clusters[index]) for index in ordered],
            "supporting_aspect_ids": list(row["supporting_aspect_ids"]),
        })

    for group in _stellium_groups(by_id):
        patterns.append({
            "pattern_type": "Stellium",
            "participant_object_ids": list(group),
            "vertex_clusters": [[object_id] for object_id in group],
            "supporting_aspect_ids": [],
        })

    patterns.sort(
        key=lambda row: (
            row["pattern_type"],
            tuple(row["participant_object_ids"]),
            tuple(tuple(cluster) for cluster in row["vertex_clusters"]),
        )
    )
    for index, row in enumerate(patterns, start=1):
        row["pattern_id"] = f"special-pattern:{index}"
        row["participant_policy_id"] = participant_policy_id
        row["aspect_policy_id"] = ASPECT_POLICY_ID
        row["orb_policy_id"] = ORB_POLICY_ID
        row["pattern_policy_id"] = PATTERN_POLICY_ID
        row["stellium_policy_id"] = STELLIUM_POLICY_ID
        row["conjunction_cluster_policy_id"] = CLUSTER_POLICY_ID
        row["pattern_projection_policy_id"] = PROJECTION_POLICY_ID

    return {
        "schema_name": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "status": "projected",
        "authority": "deterministic_topology_projection_only",
        "method": "Astrology",
        "reading_mode": "natal",
        "subject_ref": bundle["subject_ref"],
        "birth_time_certainty": bundle.get("birth_time_certainty"),
        "participant_policy_id": participant_policy_id,
        "aspect_policy_id": ASPECT_POLICY_ID,
        "orb_policy_id": ORB_POLICY_ID,
        "pattern_policy_id": PATTERN_POLICY_ID,
        "stellium_policy_id": STELLIUM_POLICY_ID,
        "conjunction_cluster_policy_id": CLUSTER_POLICY_ID,
        "pattern_projection_policy_id": PROJECTION_POLICY_ID,
        "semantic_interpretation_authority": False,
        "exact_consumer_compatibility_claimed": False,
        "patterns": patterns,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument(
        "--participant-policy-id",
        required=True,
        choices=sorted(PARTICIPANT_POLICIES),
    )
    parser.add_argument("--aspect-policy-id", required=True, choices=[ASPECT_POLICY_ID])
    parser.add_argument("--orb-policy-id", required=True, choices=[ORB_POLICY_ID])
    parser.add_argument("--pattern-policy-id", required=True, choices=[PATTERN_POLICY_ID])
    parser.add_argument("--stellium-policy-id", required=True, choices=[STELLIUM_POLICY_ID])
    parser.add_argument(
        "--pattern-projection-policy-id",
        required=True,
        choices=[PROJECTION_POLICY_ID],
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    bundle = json.loads(args.input.read_text(encoding="utf-8"))
    result = build_special_pattern_projection(
        bundle,
        participant_policy_id=args.participant_policy_id,
        aspect_policy_id=args.aspect_policy_id,
        orb_policy_id=args.orb_policy_id,
        pattern_policy_id=args.pattern_policy_id,
        stellium_policy_id=args.stellium_policy_id,
        pattern_projection_policy_id=args.pattern_projection_policy_id,
    )
    encoded = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
