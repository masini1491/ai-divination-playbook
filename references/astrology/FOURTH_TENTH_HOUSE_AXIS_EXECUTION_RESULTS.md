# Fourth–Tenth House Axis Execution Results｜第四－第十宮軸執行驗證結果

Status: **REFERENCE-ONLY / RESEARCH / NOT PRODUCTION-ROUTABLE**

Baseline: `masini1491/ai-divination-playbook@b2e16a9375603fc9aed3c0032503aa178dc6046f`

## 1. Purpose

本紀錄保存 `fourth_tenth_house_axis_claim_family_registry.json` 與其 dedicated regression 的真實執行證據。

Temporary execution bridge 只負責把既有 `references/astrology/**` test modules 接進 repository 現有的 `python -m unittest discover -s tests -v`；bridge 不複製 claim、taxonomy、retrieval 或 validation logic，且在 final merge 前移除。

## 2. Canonical execution

GitHub Actions:

```text
workflow: Validate Playbook
run number: 205
run id: 34752246261
job id: 103710624476
feature head executed: 5aa43c423a52bdea93e1d239df76515892820691
PR merge-ref: cd4fd93fb81b0e278267efa25acdef0fbad08140
```

Runtime:

```text
Ubuntu 24.04.5 LTS
CPython 3.12.14
```

## 3. Dedicated Astrology regression result

New fourth/tenth-axis module:

```text
test_fourth_tenth_house_axis_registry.py
9 / 9 PASS
```

The new cases verify:

1. registry validates under `interpretation_claim_registry@0.2.0-research` + current taxonomy;
2. typed Hellenistic 4th-house route selects only the Valens claim;
3. typed Hellenistic 10th-house route selects only the Valens claim;
4. Lilly early-modern discovery keeps `tradition_context_refs=[]` instead of inventing a doctrinal lineage;
5. modern REFERENCE_ONLY calling/public-identity claim is excluded by default;
6. the same REFERENCE_ONLY claim can only enter through explicit qualified opt-in;
7. missing required IC/4th-house L2 refs fails closed before interpretation retrieval;
8. parent significations are preserved as a `coexist` conflict rather than promoted into a universal policy;
9. modern reference claims are not silently typed as `school:modern:psychological_astrology`.

Maintained related Astrology suites were run in the same job:

```text
test_first_seventh_house_axis_registry.py           8 PASS
test_interpretation_claim_registry_validator.py    27 PASS
test_retrieve_interpretation_claims.py             20 PASS
test_registry_typed_context_migration.py           11 PASS
test_typed_contract_v0_2.py                        12 PASS
```

Therefore:

```text
new fourth/tenth-axis regression    9 / 9 PASS
other related Astrology regressions 78 / 78 PASS
-----------------------------------------------
dedicated Astrology total           87 / 87 PASS
```

## 4. Repository-wide result

The same workflow reported:

```text
Ran 117 tests in 0.239s
OK
```

Then:

```text
python tools/playbook_check.py .
PASS playbook structure
```

## 5. Evidence boundaries

This execution establishes regression evidence for the research contract. It does **not** establish:

- scientific predictive validity of astrology;
- a production house system;
- universal equivalence between IC/MC and 4th/10th cusps under every house system;
- a universal father/mother house assignment;
- deterministic career or family outcomes;
- production routing authority.

The house/angle availability boundary is demonstrated only when the retrieval caller declares `requires_l2_facts=true`; registry metadata does not yet auto-inject that requirement into arbitrary callers.

## 6. Temporary bridge boundary

The execution head included:

`tests/test_astrology_fourth_tenth_axis_evidence_bridge.py`

solely to surface the dedicated modules to the existing root workflow.

The bridge is removed before final merge. Consequently, any final post-removal root CI run must be described as verifying the final merge state / normal repository suite, **not** as re-executing the 87 dedicated Astrology tests.

## 7. Research authority

Final authority remains:

`REFERENCE-ONLY / RESEARCH / NOT PRODUCTION-ROUTABLE`
