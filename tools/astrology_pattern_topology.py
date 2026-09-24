#!/usr/bin/env python3
"""Deterministic E6 aspect-pattern topology projection for admitted natal aspect graphs."""
from __future__ import annotations

import argparse
import itertools
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from tools.astrology_runtime import gate_bundle

SCHEMA_NAME = "astrology_pattern_topology_projection"
SCHEMA_VERSION = "1.0.0"
PATTERN_POLICY_ID = "aspect-pattern-topology-major-v1"
CLUSTER_POLICY_ID = "conjunction-clusters-transitive-v1"

ADMITTED_PARTICIPANT_POLICY_ID = "aspect-participants-core-bodies-v1"
ADMITTED_ASPECT_POLICY_ID = "major-aspects-v1"
ADMITTED_ORB_POLICY_ID = "major-aspect-orbs-v1"

PROJECTION_POLICIES = {
    "pattern-projection-report-all-valid-v1",
    "pattern-projection-suppress-strict-subsets-v1",
}

# Ordered templates derived from the pinned E6 topology evidence.
# Every tuple is (left_vertex_index, right_vertex_index, required_aspect).
PATTERN_TEMPLATES: dict[str, tuple[int, tuple[tuple[int, int, str], ...]]] = {
    "T-Square": (
        3,
        (
            (0, 1, "square"),
            (0, 2, "opposition"),
            (1, 2, "square"),
        ),
    ),
    "Grand Trine": (
        3,
        (
            (0, 1, "trine"),
            (0, 2, "trine"),
            (1, 2, "trine"),
        ),
    ),
    "Grand Cross": (
        4,
        (
            (0, 1, "square"),
            (0, 2, "opposition"),
            (0, 3, "square"),
            (1, 2, "square"),
            (1, 3, "opposition"),
            (2, 3, "square"),
        ),
    ),
    "Kite": (
        4,
        (
            (0, 1, "trine"),
            (0, 2, "opposition"),
            (1, 2, "sextile"),
            (0, 3, "trine"),
            (1, 3, "trine"),
            (2, 3, "sextile"),
        ),
    ),
    "Mystic Rectangle": (
        4,
        (
            (0, 1, "sextile"),
            (0, 2, "opposition"),
            (1, 2, "trine"),
            (0, 3, "trine"),
            (1, 3, "opposition"),
            (2, 3, "sextile"),
        ),
    ),
    "Cradle": (
        4,
        (
            (0, 1, "sextile"),
            (0, 2, "trine"),
            (1, 2, "sextile"),
            (0, 3, "opposition"),
            (1, 3, "trine"),
            (2, 3, "sextile"),
        ),
    ),
    "Grand Sextile": (
        6,
        (
            (0, 1, "sextile"),
            (0, 2, "trine"),
            (1, 2, "sextile"),
            (0, 3, "opposition"),
            (1, 3, "trine"),
            (2, 3, "sextile"),
            (0, 4, "trine"),
            (1, 4, "opposition"),
            (2, 4, "trine"),
            (3, 4, "sextile"),
            (0, 5, "sextile"),
            (1, 5, "trine"),
            (2, 5, "opposition"),
            (3, 5, "trine"),
            (4, 5, "sextile"),
        ),
    ),
}


class PatternTopologyError(ValueError):
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


def _object_id_from_ref(ref: str) -> str:
    prefix = "fact:object:"
    if not isinstance(ref, str) or not ref.startswith(prefix):
        raise PatternTopologyError(f"aspect ref is not an object fact ref: {ref!r}")
    return ref[len(prefix):]


def _validate_explicit_policy_ids(
    bundle: dict[str, Any],
    *,
    participant_policy_id: str,
    aspect_policy_id: str,
    orb_policy_id: str,
    pattern_policy_id: str,
    projection_policy_id: str,
) -> None:
    if participant_policy_id != ADMITTED_PARTICIPANT_POLICY_ID:
        raise PatternTopologyError("explicit admitted participant_policy_id required")
    if aspect_policy_id != ADMITTED_ASPECT_POLICY_ID:
        raise PatternTopologyError("explicit admitted aspect_policy_id required")
    if orb_policy_id != ADMITTED_ORB_POLICY_ID:
        raise PatternTopologyError("explicit admitted orb_policy_id required")
    if pattern_policy_id != PATTERN_POLICY_ID:
        raise PatternTopologyError("explicit admitted pattern_policy_id required")
    if projection_policy_id not in PROJECTION_POLICIES:
        raise PatternTopologyError("explicit admitted pattern_projection_policy_id required")

    provider_policy = bundle.get("provider", {}).get("aspect_policies")
    if not isinstance(provider_policy, dict):
        raise PatternTopologyError("bundle lacks admitted E5 aspect policy provenance")
    expected = {
        "participant_policy_id": participant_policy_id,
        "aspect_policy_id": aspect_policy_id,
        "orb_policy_id": orb_policy_id,
    }
    for key, value in expected.items():
        if provider_policy.get(key) != value:
            raise PatternTopologyError(f"bundle {key} does not match explicit E6 selector")


def _cluster_graph(bundle: dict[str, Any]) -> tuple[
    list[tuple[str, ...]],
    dict[tuple[int, int], dict[str, set[str]]],
]:
    aspects = bundle.get("facts", {}).get("aspects", [])
    if not isinstance(aspects, list):
        raise PatternTopologyError("pattern topology requires an admitted aspect list")

    object_ids: set[str] = set()
    aspect_rows: list[tuple[str, str, str, str]] = []
    for row in aspects:
        if not isinstance(row, dict):
            continue
        left = _object_id_from_ref(row.get("left_ref"))
        right = _object_id_from_ref(row.get("right_ref"))
        name = row.get("aspect")
        fact_id = row.get("fact_id")
        if not isinstance(name, str) or not isinstance(fact_id, str):
            raise PatternTopologyError("aspect row lacks deterministic identity")
        if row.get("participant_policy_id") != ADMITTED_PARTICIPANT_POLICY_ID:
            raise PatternTopologyError("aspect row participant policy mismatch")
        if row.get("aspect_policy_id") != ADMITTED_ASPECT_POLICY_ID:
            raise PatternTopologyError("aspect row aspect policy mismatch")
        if row.get("orb_policy_id") != ADMITTED_ORB_POLICY_ID:
            raise PatternTopologyError("aspect row orb policy mismatch")
        object_ids.update((left, right))
        aspect_rows.append((left, right, name, fact_id))

    if not object_ids:
        return [], {}

    uf = _UnionFind(sorted(object_ids))
    for left, right, name, _ in aspect_rows:
        if name == "conjunction":
            uf.union(left, right)

    members: dict[str, set[str]] = defaultdict(set)
    for object_id in sorted(object_ids):
        members[uf.find(object_id)].add(object_id)
    clusters = sorted((tuple(sorted(group)) for group in members.values()), key=lambda row: row)
    cluster_index = {object_id: idx for idx, group in enumerate(clusters) for object_id in group}

    edge_map: dict[tuple[int, int], dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for left, right, name, fact_id in aspect_rows:
        a, b = cluster_index[left], cluster_index[right]
        if a == b:
            continue
        edge_map[tuple(sorted((a, b)))][name].add(fact_id)
    return clusters, edge_map


def _match_template(
    vertex_indices: tuple[int, ...],
    template: tuple[tuple[int, int, str], ...],
    edge_map: dict[tuple[int, int], dict[str, set[str]]],
) -> tuple[str, ...] | None:
    supporting: set[str] = set()
    for left_pos, right_pos, aspect in template:
        left = vertex_indices[left_pos]
        right = vertex_indices[right_pos]
        fact_ids = edge_map.get(tuple(sorted((left, right))), {}).get(aspect, set())
        if not fact_ids:
            return None
        supporting.update(fact_ids)
    return tuple(sorted(supporting))


def _raw_matches(
    clusters: list[tuple[str, ...]],
    edge_map: dict[tuple[int, int], dict[str, set[str]]],
) -> list[dict[str, Any]]:
    matches: dict[tuple[str, tuple[int, ...]], dict[str, Any]] = {}
    for pattern_type, (vertex_count, template) in PATTERN_TEMPLATES.items():
        for combo in itertools.combinations(range(len(clusters)), vertex_count):
            best: dict[str, Any] | None = None
            for perm in itertools.permutations(combo):
                support = _match_template(perm, template, edge_map)
                if support is None:
                    continue
                candidate = {
                    "pattern_type": pattern_type,
                    "cluster_indices": tuple(sorted(combo)),
                    "ordered_cluster_indices": tuple(perm),
                    "supporting_aspect_ids": support,
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
                matches[(pattern_type, tuple(sorted(combo)))] = best
    return sorted(matches.values(), key=lambda row: (row["pattern_type"], row["cluster_indices"]))


def _apply_projection_policy(
    matches: list[dict[str, Any]],
    projection_policy_id: str,
) -> list[dict[str, Any]]:
    if projection_policy_id == "pattern-projection-report-all-valid-v1":
        return matches

    vertex_sets = [set(row["cluster_indices"]) for row in matches]
    return [
        row
        for row, vertices in zip(matches, vertex_sets)
        if not any(vertices < competing for competing in vertex_sets)
    ]


def build_pattern_topology_projection(
    bundle: dict[str, Any],
    *,
    participant_policy_id: str,
    aspect_policy_id: str,
    orb_policy_id: str,
    pattern_policy_id: str,
    pattern_projection_policy_id: str,
) -> dict[str, Any]:
    gate = gate_bundle(bundle)
    if gate.get("status") != "admitted":
        raise PatternTopologyError("pattern topology requires an admitted Astrology fact bundle")
    if bundle.get("reading_mode") != "natal":
        raise PatternTopologyError("pattern topology is admitted for natal bundles only")

    _validate_explicit_policy_ids(
        bundle,
        participant_policy_id=participant_policy_id,
        aspect_policy_id=aspect_policy_id,
        orb_policy_id=orb_policy_id,
        pattern_policy_id=pattern_policy_id,
        projection_policy_id=pattern_projection_policy_id,
    )
    clusters, edge_map = _cluster_graph(bundle)
    raw = _raw_matches(clusters, edge_map)
    selected = _apply_projection_policy(raw, pattern_projection_policy_id)

    patterns = []
    for index, row in enumerate(selected, start=1):
        ordered = row["ordered_cluster_indices"]
        patterns.append({
            "pattern_id": f"pattern:{index}",
            "pattern_type": row["pattern_type"],
            "pattern_policy_id": pattern_policy_id,
            "participant_policy_id": participant_policy_id,
            "aspect_policy_id": aspect_policy_id,
            "orb_policy_id": orb_policy_id,
            "conjunction_cluster_policy_id": CLUSTER_POLICY_ID,
            "pattern_projection_policy_id": pattern_projection_policy_id,
            "vertex_clusters": [list(clusters[i]) for i in ordered],
            "supporting_aspect_ids": list(row["supporting_aspect_ids"]),
        })

    return {
        "schema_name": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "status": "projected",
        "authority": "deterministic_topology_projection_only",
        "method": "Astrology",
        "reading_mode": "natal",
        "subject_ref": bundle["subject_ref"],
        "participant_policy_id": participant_policy_id,
        "aspect_policy_id": aspect_policy_id,
        "orb_policy_id": orb_policy_id,
        "pattern_policy_id": pattern_policy_id,
        "conjunction_cluster_policy_id": CLUSTER_POLICY_ID,
        "pattern_projection_policy_id": pattern_projection_policy_id,
        "semantic_interpretation_authority": False,
        "unsupported_pattern_types": ["Yod", "Stellium", "Grand Quintile"],
        "patterns": patterns,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--participant-policy-id", required=True)
    parser.add_argument("--aspect-policy-id", required=True)
    parser.add_argument("--orb-policy-id", required=True)
    parser.add_argument("--pattern-policy-id", required=True)
    parser.add_argument("--pattern-projection-policy-id", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    bundle = json.loads(args.input.read_text(encoding="utf-8"))
    result = build_pattern_topology_projection(
        bundle,
        participant_policy_id=args.participant_policy_id,
        aspect_policy_id=args.aspect_policy_id,
        orb_policy_id=args.orb_policy_id,
        pattern_policy_id=args.pattern_policy_id,
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
