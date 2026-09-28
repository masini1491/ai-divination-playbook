from __future__ import annotations

import json
import sys
from pathlib import Path

ALLOWED_STATES = {
    "composition_adequate",
    "research_candidate",
    "exact_claim_admitted",
    "unsupported",
}
REQUIRED_TRIGGERS = {
    "materially_over_generic_after_valid_composition",
    "recurring_gap_not_safely_expressible_by_admitted_primitives",
    "source_backed_exact_semantics_materially_differ_from_composition",
    "typed_context_requires_unrepresented_semantic_distinction",
}

def validate(data: dict) -> list[str]:
    errors: list[str] = []
    if data.get("schema_name") != "astrology_sparse_exact_claim_admission_policy":
        errors.append("schema_name")
    if data.get("schema_version") != "1.0.0":
        errors.append("schema_version")
    if data.get("authority") != "REFERENCE_ONLY_RESEARCH_POLICY":
        errors.append("authority")
    if data.get("production_routable") is not False:
        errors.append("production_routable")
    if data.get("policy_id") != "astrology-sparse-exact-claim-admission-v1":
        errors.append("policy_id")

    states = data.get("states")
    if not isinstance(states, list) or set(states) != ALLOWED_STATES or len(states) != 4:
        errors.append("states")

    triggers = data.get("research_candidate_triggers")
    if not isinstance(triggers, list) or set(triggers) != REQUIRED_TRIGGERS:
        errors.append("research_candidate_triggers")

    anti = data.get("anti_cartesian_rules")
    if not isinstance(anti, dict) or not anti:
        errors.append("anti_cartesian_rules")
    else:
        for key, value in anti.items():
            if value is not False:
                errors.append(f"anti_cartesian_rules.{key}")

    promotion = data.get("promotion_boundary")
    expected_promotion = [
        "gap_evaluation",
        "bounded_research_candidate",
        "source_normalized_evidence",
        "research_registry_validation",
        "explicit_production_admission",
    ]
    if promotion != expected_promotion:
        errors.append("promotion_boundary")

    cases = data.get("representative_cases")
    if not isinstance(cases, list) or len(cases) < 4:
        errors.append("representative_cases")
    else:
        seen_ids: set[str] = set()
        seen_states: set[str] = set()
        for index, case in enumerate(cases):
            if not isinstance(case, dict):
                errors.append(f"representative_cases[{index}]")
                continue
            cid = case.get("case_id")
            state = case.get("expected_state")
            if not isinstance(cid, str) or not cid or cid in seen_ids:
                errors.append(f"representative_cases[{index}].case_id")
            else:
                seen_ids.add(cid)
            if state not in ALLOWED_STATES:
                errors.append(f"representative_cases[{index}].expected_state")
            else:
                seen_states.add(state)
            refs = case.get("evidence_refs")
            if not isinstance(refs, list) or not refs or any(not isinstance(x, str) or not x for x in refs):
                errors.append(f"representative_cases[{index}].evidence_refs")
            rationale = case.get("rationale")
            if not isinstance(rationale, str) or not rationale.strip():
                errors.append(f"representative_cases[{index}].rationale")
        if seen_states != ALLOWED_STATES:
            errors.append("representative_cases.state_coverage")
    return errors

def main(argv: list[str]) -> int:
    path = Path(argv[1]) if len(argv) > 1 else Path(__file__).with_name("EXACT_CLAIM_ADMISSION_POLICY_V1.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    errors = validate(data)
    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1
    print(f"{path}: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
