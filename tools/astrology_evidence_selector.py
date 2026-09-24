#!/usr/bin/env python3
"""Deterministically select admitted Astrology evidence from explicit typed selectors.

A caller must provide typed selectors. This adapter does not infer them from free text.
It matches selectors against an admitted reading run, restricts claim search to
production-declared registries, binds claims to deterministic applicability derived from
the selected fact types, and asks the existing interpretation handoff to revalidate the
exact selection and source admission.

Authority: deterministic evidence selection only. No chart calculation, free-text NLU,
astrological meaning authorship, source-admission widening, or final prose authority.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from tools.astrology_interpretation_handoff import InterpretationHandoffError, build_handoff

REQUEST_SCHEMA_NAME = "astrology_typed_evidence_selection_request"
REQUEST_SCHEMA_VERSION = "1.0.0"
SELECTION_SCHEMA_NAME = "astrology_typed_evidence_selection"
SELECTION_SCHEMA_VERSION = "1.0.0"
SELECTOR_ID = "astrology-typed-evidence-selector-v1"
SELECTOR_VERSION = "1.0.0"
PRODUCTION_MANIFEST_PATH = "ASTROLOGY_PRODUCTION_ADMISSION_V1.json"
APPLICABILITY_SCOPES = {"selector_shape", "object_core", "sign_style", "object_sign_pair"}
HOUSE_NAMES = {
    1: "first house", 2: "second house", 3: "third house", 4: "fourth house",
    5: "fifth house", 6: "sixth house", 7: "seventh house", 8: "eighth house",
    9: "ninth house", 10: "tenth house", 11: "eleventh house", 12: "twelfth house",
}


class AstrologyEvidenceSelectionError(ValueError):
    """Typed selection could not be resolved uniquely and safely."""


def _root_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def _load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AstrologyEvidenceSelectionError(f"cannot load {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise AstrologyEvidenceSelectionError(f"{path} must contain a JSON object")
    return data


def _text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AstrologyEvidenceSelectionError(f"{path} must be a non-empty string")
    return value.strip()


def _string_list(value: Any, path: str, *, allow_empty: bool = True) -> list[str]:
    if not isinstance(value, list):
        raise AstrologyEvidenceSelectionError(f"{path} must be an array")
    output: list[str] = []
    for index, item in enumerate(value):
        text = _text(item, f"{path}[{index}]")
        if text in output:
            raise AstrologyEvidenceSelectionError(f"{path} must not contain duplicates: {text}")
        output.append(text)
    if not allow_empty and not output:
        raise AstrologyEvidenceSelectionError(f"{path} must not be empty")
    return output


def _exact_keys(data: dict[str, Any], *, allowed: set[str], required: set[str], path: str) -> None:
    missing = sorted(required - data.keys())
    if missing:
        raise AstrologyEvidenceSelectionError(f"{path} missing required field(s): {', '.join(missing)}")
    extra = sorted(data.keys() - allowed)
    if extra:
        raise AstrologyEvidenceSelectionError(f"{path} contains unsupported field(s): {', '.join(extra)}")


def _validate_request(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise AstrologyEvidenceSelectionError("$ must be an object")
    _exact_keys(
        data,
        allowed={"schema_name", "schema_version", "question_id", "question", "focus", "exclusions", "fact_selectors", "claim_selectors", "unsupported_factors"},
        required={"schema_name", "schema_version", "question_id", "question", "fact_selectors", "claim_selectors"},
        path="$",
    )
    if data["schema_name"] != REQUEST_SCHEMA_NAME:
        raise AstrologyEvidenceSelectionError(f"$.schema_name must equal {REQUEST_SCHEMA_NAME}")
    if data["schema_version"] != REQUEST_SCHEMA_VERSION:
        raise AstrologyEvidenceSelectionError(f"$.schema_version must equal {REQUEST_SCHEMA_VERSION}")
    if not isinstance(data["fact_selectors"], list) or not data["fact_selectors"]:
        raise AstrologyEvidenceSelectionError("$.fact_selectors must be a non-empty array")
    if not isinstance(data["claim_selectors"], list):
        raise AstrologyEvidenceSelectionError("$.claim_selectors must be an array")

    fact_selectors: list[dict[str, Any]] = []
    fact_selector_ids: set[str] = set()
    for index, raw in enumerate(data["fact_selectors"]):
        path = f"$.fact_selectors[{index}]"
        if not isinstance(raw, dict):
            raise AstrologyEvidenceSelectionError(f"{path} must be an object")
        kind = raw.get("selector_kind")
        common = {"selector_id", "selector_kind", "bundle", "cardinality"}
        if kind == "object":
            required, allowed = common | {"object_id"}, common | {"object_id", "object_type"}
        elif kind == "house":
            required, allowed = common | {"house_number"}, common | {"house_number"}
        elif kind == "aspect":
            required = common | {"left_object_id", "right_object_id", "aspect"}
            allowed = set(required)
        elif kind == "event":
            required = common | {"event_kind"}
            allowed = common | {"event_kind", "moving_body", "natal_target", "aspect", "passage_index", "transition", "ingress_type", "from_sign", "to_sign", "exact_time_utc"}
        else:
            raise AstrologyEvidenceSelectionError(f"{path}.selector_kind is unsupported")
        _exact_keys(raw, allowed=allowed, required=required, path=path)
        selector_id = _text(raw["selector_id"], f"{path}.selector_id")
        if selector_id in fact_selector_ids:
            raise AstrologyEvidenceSelectionError(f"duplicate fact selector_id: {selector_id}")
        fact_selector_ids.add(selector_id)
        if raw["bundle"] not in {"natal", "transit"}:
            raise AstrologyEvidenceSelectionError(f"{path}.bundle must be natal or transit")
        if kind in {"house", "aspect"} and raw["bundle"] != "natal":
            raise AstrologyEvidenceSelectionError(f"{path}.bundle must be natal for {kind} selectors")
        if kind == "event" and raw["bundle"] != "transit":
            raise AstrologyEvidenceSelectionError(f"{path}.bundle must be transit for event selectors")
        if raw["cardinality"] not in {"exactly_one", "one_or_more"}:
            raise AstrologyEvidenceSelectionError(f"{path}.cardinality is unsupported")
        if kind == "house" and (not isinstance(raw["house_number"], int) or not 1 <= raw["house_number"] <= 12):
            raise AstrologyEvidenceSelectionError(f"{path}.house_number must be 1..12")
        if "passage_index" in raw and (not isinstance(raw["passage_index"], int) or raw["passage_index"] < 1):
            raise AstrologyEvidenceSelectionError(f"{path}.passage_index must be >= 1")
        fact_selectors.append(dict(raw))

    claim_selectors: list[dict[str, Any]] = []
    claim_selector_ids: set[str] = set()
    for index, raw in enumerate(data["claim_selectors"]):
        path = f"$.claim_selectors[{index}]"
        if not isinstance(raw, dict):
            raise AstrologyEvidenceSelectionError(f"{path} must be an object")
        _exact_keys(
            raw,
            allowed={"selector_id", "registry_record_id", "claim_type", "applies_to_all", "tradition_context_refs_any", "fact_selector_ids", "applicability_scope", "semantic_profile"},
            required={"selector_id", "claim_type", "applies_to_all", "fact_selector_ids"},
            path=path,
        )
        selector_id = _text(raw["selector_id"], f"{path}.selector_id")
        if selector_id in claim_selector_ids:
            raise AstrologyEvidenceSelectionError(f"duplicate claim selector_id: {selector_id}")
        claim_selector_ids.add(selector_id)
        linked = _string_list(raw["fact_selector_ids"], f"{path}.fact_selector_ids", allow_empty=False)
        applicability_scope = raw.get("applicability_scope", "selector_shape")
        if applicability_scope not in APPLICABILITY_SCOPES:
            raise AstrologyEvidenceSelectionError(
                f"{path}.applicability_scope must be one of {sorted(APPLICABILITY_SCOPES)}"
            )
        unknown = sorted(set(linked) - fact_selector_ids)
        if unknown:
            raise AstrologyEvidenceSelectionError(f"{path}.fact_selector_ids contains unknown selector(s): {', '.join(unknown)}")
        claim_selectors.append({
            **raw,
            "selector_id": selector_id,
            "claim_type": _text(raw["claim_type"], f"{path}.claim_type"),
            "applicability_scope": applicability_scope,
            "semantic_profile": _text(raw["semantic_profile"], f"{path}.semantic_profile") if raw.get("semantic_profile") is not None else None,
            "applies_to_all": _string_list(raw["applies_to_all"], f"{path}.applies_to_all", allow_empty=False),
            "tradition_context_refs_any": _string_list(raw.get("tradition_context_refs_any", []), f"{path}.tradition_context_refs_any"),
            "fact_selector_ids": linked,
        })

    unsupported: list[dict[str, str]] = []
    raw_unsupported = data.get("unsupported_factors", [])
    if not isinstance(raw_unsupported, list):
        raise AstrologyEvidenceSelectionError("$.unsupported_factors must be an array")
    for index, raw in enumerate(raw_unsupported):
        path = f"$.unsupported_factors[{index}]"
        if not isinstance(raw, dict):
            raise AstrologyEvidenceSelectionError(f"{path} must be an object")
        _exact_keys(raw, allowed={"factor", "reason"}, required={"factor", "reason"}, path=path)
        unsupported.append({"factor": _text(raw["factor"], f"{path}.factor"), "reason": _text(raw["reason"], f"{path}.reason")})

    return {
        "schema_name": REQUEST_SCHEMA_NAME,
        "schema_version": REQUEST_SCHEMA_VERSION,
        "question_id": _text(data["question_id"], "$.question_id"),
        "question": _text(data["question"], "$.question"),
        "focus": _string_list(data.get("focus", []), "$.focus"),
        "exclusions": _string_list(data.get("exclusions", []), "$.exclusions"),
        "fact_selectors": fact_selectors,
        "claim_selectors": claim_selectors,
        "unsupported_factors": unsupported,
    }


def _validate_run(run: Any) -> dict[str, Any]:
    if not isinstance(run, dict):
        raise AstrologyEvidenceSelectionError("$run must be an object")
    if run.get("schema_name") != "astrology_reading_run" or run.get("schema_version") != "1.0.0":
        raise AstrologyEvidenceSelectionError("reading run must be astrology_reading_run@1.0.0")
    if run.get("status") != "admitted" or run.get("interpretation_allowed") is not True:
        raise AstrologyEvidenceSelectionError("reading run is not admitted for interpretation")
    if not isinstance(run.get("fact_bundles"), dict) or not isinstance(run.get("runtime_gates"), dict):
        raise AstrologyEvidenceSelectionError("reading run must contain fact_bundles and runtime_gates")
    for bundle_name in run["fact_bundles"]:
        gate = run["runtime_gates"].get(bundle_name)
        if not isinstance(gate, dict) or gate.get("interpretation_allowed") is not True:
            raise AstrologyEvidenceSelectionError(f"{bundle_name} bundle lacks an admitted runtime gate")
    return run


def _bundle_rows(run: dict[str, Any], bundle_name: str, collection: str) -> list[dict[str, Any]]:
    bundle = run["fact_bundles"].get(bundle_name)
    if not isinstance(bundle, dict):
        raise AstrologyEvidenceSelectionError(f"requested fact bundle is unavailable: {bundle_name}")
    rows = bundle.get("facts", {}).get(collection, [])
    return [row for row in rows if isinstance(row, dict) and isinstance(row.get("fact_id"), str)] if isinstance(rows, list) else []


def _object_id_index(run: dict[str, Any], bundle_name: str) -> dict[str, str]:
    return {row["fact_id"]: row["object_id"] for row in _bundle_rows(run, bundle_name, "objects") if isinstance(row.get("object_id"), str)}


def _fact_matches(run: dict[str, Any], selector: dict[str, Any]) -> list[dict[str, str]]:
    kind, bundle = selector["selector_kind"], selector["bundle"]
    if kind == "object":
        matched = [row for row in _bundle_rows(run, bundle, "objects") if row.get("object_id") == selector["object_id"] and ("object_type" not in selector or row.get("object_type") == selector["object_type"])]
    elif kind == "house":
        matched = [row for row in _bundle_rows(run, bundle, "houses") if row.get("house_number") == selector["house_number"]]
    elif kind == "aspect":
        objects = _object_id_index(run, bundle)
        requested_pair = {selector["left_object_id"], selector["right_object_id"]}
        matched = []
        for row in _bundle_rows(run, bundle, "aspects"):
            pair = {objects.get(row.get("left_ref")), objects.get(row.get("right_ref"))}
            if row.get("aspect") == selector["aspect"] and pair == requested_pair:
                matched.append(row)
    else:
        fields = {key: value for key, value in selector.items() if key not in {"selector_id", "selector_kind", "bundle", "cardinality"}}
        matched = [row for row in _bundle_rows(run, bundle, "events") if all(row.get(key) == value for key, value in fields.items())]

    refs = [{"bundle": bundle, "fact_id": row["fact_id"]} for row in matched]
    if selector["cardinality"] == "exactly_one" and len(refs) != 1:
        raise AstrologyEvidenceSelectionError(f"fact selector {selector['selector_id']} expected exactly one match, found {len(refs)}")
    if selector["cardinality"] == "one_or_more" and not refs:
        raise AstrologyEvidenceSelectionError(f"fact selector {selector['selector_id']} matched no facts")
    return refs


def _selector_applicability(selector: dict[str, Any]) -> set[str]:
    kind = selector["selector_kind"]
    tags = {selector["bundle"]}
    if kind == "house":
        tags.add(HOUSE_NAMES[selector["house_number"]])
    elif kind == "object":
        tags.add(selector["object_id"])
    elif kind == "aspect":
        tags.update({selector["left_object_id"], selector["right_object_id"], selector["aspect"]})
    else:
        event_kind = selector["event_kind"]
        tags.add({"transit_to_natal": "transit-to-natal", "station": "station", "ingress": "ingress"}[event_kind])
        if event_kind == "transit_to_natal":
            tags.add("exact passage")
    return tags


def _fact_bound_applicability(
    run: dict[str, Any],
    selector: dict[str, Any],
    refs: list[dict[str, str]],
    applicability_scope: str,
) -> set[str]:
    if applicability_scope == "selector_shape":
        return _selector_applicability(selector)
    if selector["selector_kind"] != "object":
        raise AstrologyEvidenceSelectionError(
            f"applicability_scope={applicability_scope} requires object fact selectors"
        )

    bundle = selector["bundle"]
    rows_by_id = {
        row["fact_id"]: row
        for row in _bundle_rows(run, bundle, "objects")
        if isinstance(row.get("fact_id"), str)
    }
    rows = [rows_by_id.get(ref["fact_id"]) for ref in refs]
    if not rows or any(not isinstance(row, dict) for row in rows):
        raise AstrologyEvidenceSelectionError(
            f"object applicability binding could not resolve matched facts for selector {selector['selector_id']}"
        )

    tags = {bundle}
    if applicability_scope in {"object_core", "object_sign_pair"}:
        object_ids = {row.get("object_id") for row in rows if isinstance(row.get("object_id"), str)}
        if len(object_ids) != 1:
            raise AstrologyEvidenceSelectionError(
                f"object applicability binding requires one stable object_id for selector {selector['selector_id']}"
            )
        tags.update(object_ids)

    if applicability_scope in {"sign_style", "object_sign_pair"}:
        if any(row.get("object_type") != "planet" for row in rows):
            raise AstrologyEvidenceSelectionError(
                f"applicability_scope={applicability_scope} requires planet object facts"
            )
        signs = {row.get("sign") for row in rows if isinstance(row.get("sign"), str) and row.get("sign")}
        if len(signs) != 1:
            raise AstrologyEvidenceSelectionError(
                f"sign applicability binding requires one admitted sign for selector {selector['selector_id']}"
            )
        tags.update(signs)

    return tags


def _derived_fact_interpretation_policy(
    manifest: dict[str, Any],
) -> tuple[set[str], dict[str, set[tuple[str, str]]]]:
    policy = manifest.get("natal_semantic_policy", {}).get("derived_fact_interpretation", {})
    raw_ids = policy.get("fact_only_object_ids", [])
    if not isinstance(raw_ids, list) or any(not isinstance(item, str) or not item for item in raw_ids):
        raise AstrologyEvidenceSelectionError("production manifest fact_only_object_ids must be a string array")
    raw_bindings = policy.get("admitted_claim_bindings", {})
    if not isinstance(raw_bindings, dict):
        raise AstrologyEvidenceSelectionError("production manifest admitted_claim_bindings must be an object")
    bindings: dict[str, set[tuple[str, str]]] = {}
    for object_id, rows in raw_bindings.items():
        if not isinstance(object_id, str) or not isinstance(rows, list):
            raise AstrologyEvidenceSelectionError("production manifest admitted_claim_bindings is invalid")
        allowed: set[tuple[str, str]] = set()
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get("registry_record_id"), str) or not isinstance(row.get("claim_id"), str):
                raise AstrologyEvidenceSelectionError("production manifest admitted_claim_bindings entry is invalid")
            allowed.add((row["registry_record_id"], row["claim_id"]))
        bindings[object_id] = allowed
    return set(raw_ids), bindings


def _guard_no_binding_fact_only_objects(
    run: dict[str, Any],
    selectors_by_id: dict[str, dict[str, Any]],
    refs_by_selector: dict[str, list[dict[str, str]]],
    linked_ids: list[str],
    fact_only_ids: set[str],
    admitted_bindings: dict[str, set[tuple[str, str]]],
) -> None:
    for selector_id in linked_ids:
        selector = selectors_by_id[selector_id]
        if selector["selector_kind"] != "object":
            continue
        rows_by_id = {
            row["fact_id"]: row
            for row in _bundle_rows(run, selector["bundle"], "objects")
            if isinstance(row.get("fact_id"), str)
        }
        for ref in refs_by_selector[selector_id]:
            row = rows_by_id.get(ref["fact_id"])
            object_id = row.get("object_id") if isinstance(row, dict) else None
            if object_id in fact_only_ids and not admitted_bindings.get(object_id):
                raise AstrologyEvidenceSelectionError(
                    f"claim binding is not admitted for derived fact-only object: {object_id}"
                )


def _guard_fact_only_claim_binding(
    run: dict[str, Any],
    selectors_by_id: dict[str, dict[str, Any]],
    refs_by_selector: dict[str, list[dict[str, str]]],
    linked_ids: list[str],
    fact_only_ids: set[str],
    admitted_bindings: dict[str, set[tuple[str, str]]],
    matches: list[dict[str, str]],
) -> None:
    for selector_id in linked_ids:
        selector = selectors_by_id[selector_id]
        if selector["selector_kind"] != "object":
            continue
        rows_by_id = {
            row["fact_id"]: row
            for row in _bundle_rows(run, selector["bundle"], "objects")
            if isinstance(row.get("fact_id"), str)
        }
        for ref in refs_by_selector[selector_id]:
            row = rows_by_id.get(ref["fact_id"])
            object_id = row.get("object_id") if isinstance(row, dict) else None
            if object_id in fact_only_ids:
                selected = {(row["registry_record_id"], row["claim_id"]) for row in matches}
                if not selected or not selected.issubset(admitted_bindings.get(object_id, set())):
                    raise AstrologyEvidenceSelectionError(
                        f"claim binding is not admitted for derived fact-only object: {object_id}"
                    )


def _registry_index(root: Path, manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    admitted = set(manifest.get("admitted_research_registries", []))
    index: dict[str, dict[str, Any]] = {}
    for path in sorted((root / "references" / "astrology").glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(data, dict) or data.get("schema_name") != "interpretation_claim_registry":
            continue
        record_id = data.get("record_id")
        if record_id not in admitted:
            continue
        if record_id in index:
            raise AstrologyEvidenceSelectionError(f"duplicate admitted registry record_id: {record_id}")
        index[str(record_id)] = data
    missing = sorted(admitted - index.keys())
    if missing:
        raise AstrologyEvidenceSelectionError(f"admitted registry file(s) not found: {', '.join(missing)}")
    return index


def _claim_matches(claim: dict[str, Any], selector: dict[str, Any], required_applicability: set[str]) -> bool:
    if claim.get("claim_type") != selector["claim_type"]:
        return False
    applies_to = {item for item in claim.get("applies_to", []) if isinstance(item, str)}
    if not (set(selector["applies_to_all"]) | required_applicability).issubset(applies_to):
        return False
    requested_traditions = set(selector.get("tradition_context_refs_any", []))
    if requested_traditions:
        claim_traditions = {item for item in claim.get("tradition_context_refs", []) if isinstance(item, str)}
        if not (requested_traditions & claim_traditions):
            return False
    return True


def _select_claims(registry_index: dict[str, dict[str, Any]], selector: dict[str, Any], required_applicability: set[str]) -> list[dict[str, str]]:
    requested_registry = selector.get("registry_record_id")
    if requested_registry is not None:
        if requested_registry not in registry_index:
            raise AstrologyEvidenceSelectionError(f"claim selector {selector['selector_id']} requests an unadmitted registry: {requested_registry}")
        candidates = [(requested_registry, registry_index[requested_registry])]
    else:
        candidates = sorted(registry_index.items())

    requested_profile = selector.get("semantic_profile")
    matches: list[dict[str, str]] = []
    for registry_id, registry in candidates:
        policy = registry.get("selection_policy", {})
        required_profile = policy.get("required_semantic_profile") if isinstance(policy, dict) else None
        if isinstance(required_profile, str) and required_profile:
            if requested_profile != required_profile:
                if requested_registry == registry_id:
                    raise AstrologyEvidenceSelectionError(
                        f"claim selector {selector['selector_id']} requires semantic_profile={required_profile} for registry {registry_id}"
                    )
                continue
        elif requested_profile is not None:
            continue
        for claim in registry.get("claims", []):
            if isinstance(claim, dict) and isinstance(claim.get("claim_id"), str) and _claim_matches(claim, selector, required_applicability):
                matches.append({"registry_record_id": registry_id, "claim_id": claim["claim_id"]})
    if not matches:
        raise AstrologyEvidenceSelectionError(f"claim selector {selector['selector_id']} matched no admitted claims after fact-applicability binding")
    if len(matches) > 1:
        rendered = ", ".join(f"{row['registry_record_id']}::{row['claim_id']}" for row in matches)
        raise AstrologyEvidenceSelectionError(f"claim selector {selector['selector_id']} is ambiguous; refine typed criteria: {rendered}")
    return matches


def _dedupe_fact_refs(refs: list[dict[str, str]]) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for ref in refs:
        key = (ref["bundle"], ref["fact_id"])
        if key not in seen:
            seen.add(key)
            output.append(ref)
    return output


def selection_to_interpretation_request(selection: dict[str, Any]) -> dict[str, Any]:
    if selection.get("schema_name") != SELECTION_SCHEMA_NAME or selection.get("status") != "selected":
        raise AstrologyEvidenceSelectionError("selection is not an admitted typed evidence selection")
    return {
        "schema_name": "astrology_interpretation_request",
        "schema_version": "1.0.0",
        "question_id": selection["question_id"],
        "question": selection["question"],
        "focus": selection.get("focus", []),
        "exclusions": selection.get("exclusions", []),
        "fact_refs": selection["fact_refs"],
        "claim_requests": selection["claim_requests"],
        "unsupported_factors": selection.get("unsupported_factors", []),
    }


def select_evidence(reading_run: Any, typed_request: Any, *, repo_root: Path | None = None) -> dict[str, Any]:
    run = _validate_run(reading_run)
    request = _validate_request(typed_request)
    root = repo_root or _root_dir()
    manifest = _load_json(root / PRODUCTION_MANIFEST_PATH)
    registries = _registry_index(root, manifest)
    fact_only_ids, admitted_bindings = _derived_fact_interpretation_policy(manifest)

    selectors_by_id = {selector["selector_id"]: selector for selector in request["fact_selectors"]}
    refs_by_selector: dict[str, list[dict[str, str]]] = {}
    fact_provenance: list[dict[str, Any]] = []
    all_fact_refs: list[dict[str, str]] = []
    for selector in request["fact_selectors"]:
        refs = _fact_matches(run, selector)
        refs_by_selector[selector["selector_id"]] = refs
        fact_provenance.append({"selector_id": selector["selector_id"], "matched_fact_refs": refs})
        all_fact_refs.extend(refs)
    all_fact_refs = _dedupe_fact_refs(all_fact_refs)

    claim_requests: list[dict[str, Any]] = []
    claim_provenance: list[dict[str, Any]] = []
    seen_claims: set[tuple[str, str]] = set()
    for selector in request["claim_selectors"]:
        linked_ids = selector["fact_selector_ids"]
        linked_refs = _dedupe_fact_refs([ref for selector_id in linked_ids for ref in refs_by_selector[selector_id]])
        _guard_no_binding_fact_only_objects(
            run,
            selectors_by_id,
            refs_by_selector,
            linked_ids,
            fact_only_ids,
            admitted_bindings,
        )
        required_applicability: set[str] = set()
        applicability_scope = selector["applicability_scope"]
        for selector_id in linked_ids:
            required_applicability.update(
                _fact_bound_applicability(
                    run,
                    selectors_by_id[selector_id],
                    refs_by_selector[selector_id],
                    applicability_scope,
                )
            )
        matches = _select_claims(registries, selector, required_applicability)
        _guard_fact_only_claim_binding(
            run,
            selectors_by_id,
            refs_by_selector,
            linked_ids,
            fact_only_ids,
            admitted_bindings,
            matches,
        )
        provenance_refs: list[dict[str, str]] = []
        for match in matches:
            identity = (match["registry_record_id"], match["claim_id"])
            if identity in seen_claims:
                raise AstrologyEvidenceSelectionError(f"claim selected more than once by typed criteria: {identity[0]} / {identity[1]}")
            seen_claims.add(identity)
            claim_requests.append({**match, "fact_refs": linked_refs})
            provenance_refs.append(match)
        claim_provenance.append({"selector_id": selector["selector_id"], "matched_claim_refs": provenance_refs})

    selection = {
        "schema_name": SELECTION_SCHEMA_NAME,
        "schema_version": SELECTION_SCHEMA_VERSION,
        "status": "selected",
        "selection_allowed": True,
        "selector": {
            "selector_id": SELECTOR_ID,
            "selector_version": SELECTOR_VERSION,
            "authority": "deterministic_evidence_selection_only",
            "natural_language_understanding_authority": False,
            "semantic_meaning_authority": False,
            "source_admission_authority": False,
            "final_prose_authority": False,
        },
        "question_id": request["question_id"],
        "question": request["question"],
        "focus": request["focus"],
        "exclusions": request["exclusions"],
        "fact_refs": all_fact_refs,
        "claim_requests": claim_requests,
        "unsupported_factors": request["unsupported_factors"],
        "selection_provenance": {"fact_selectors": fact_provenance, "claim_selectors": claim_provenance},
    }
    try:
        build_handoff(run, selection_to_interpretation_request(selection), repo_root=root)
    except InterpretationHandoffError as exc:
        raise AstrologyEvidenceSelectionError(f"selected evidence failed production handoff admission: {exc}") from exc
    return selection


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Select Astrology production evidence from explicit typed selectors.")
    parser.add_argument("reading_run", type=Path)
    parser.add_argument("typed_request", type=Path)
    args = parser.parse_args()
    try:
        result = select_evidence(_load(args.reading_run), _load(args.typed_request))
    except (OSError, json.JSONDecodeError, AstrologyEvidenceSelectionError) as exc:
        print(json.dumps({"schema_name": SELECTION_SCHEMA_NAME, "schema_version": SELECTION_SCHEMA_VERSION, "status": "rejected", "selection_allowed": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
