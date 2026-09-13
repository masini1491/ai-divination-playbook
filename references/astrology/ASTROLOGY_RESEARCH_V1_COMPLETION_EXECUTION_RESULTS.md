# Astrology Research v1 Completion — Execution Results

Status: **REFERENCE-ONLY / RESEARCH V1 COMPLETION EXECUTED / NOT PRODUCTION-ROUTABLE**

## 1. Purpose

This record captures direct GitHub Actions execution evidence for the integrated Astrology research-v1 completion tranche.

Baseline main before the tranche:

`795cff4f4d4425aa8ba674d4d189b7089038b074`

Feature branch:

`research/astrology-research-v1-completion-20260913`

PR:

`#28 research: complete Astrology research v1 coverage`

## 2. Executed scope

A temporary root unittest bridge loaded the following Astrology modules into the repository's existing `Validate Playbook` workflow:

### New research-v1 completion suites

```text
test_remaining_house_axes_registry.py
test_registry_retrieval_preconditions.py
test_essential_dignity_expansion_registry.py
test_high_value_planet_aspects_registry.py
test_transit_interpretation_registry.py
```

### Maintained existing Astrology suites

```text
test_fourth_tenth_house_axis_registry.py
test_first_seventh_house_axis_registry.py
test_interpretation_claim_registry_validator.py
test_retrieve_interpretation_claims.py
test_registry_typed_context_migration.py
test_typed_contract_v0_2.py
```

The bridge only imported existing unittest modules. It duplicated no claim, retrieval, validation, taxonomy or synthesis logic.

## 3. Canonical GitHub Actions execution

```text
workflow: Validate Playbook
run number: #209
run id: 34755269655
job id: 103718466405
feature head executed: b222e0feb1cd7d121b02f0fb883c99def5551519
PR merge-ref checkout: a4a8de51324f4771388eedc0ceff4f5139d01bef
base main: 795cff4f4d4425aa8ba674d4d189b7089038b074
status: completed
conclusion: success
```

Environment observed in the actual job log:

```text
GitHub runner: 2.337.0
runner image: ubuntu-24.04
Ubuntu: 24.04.5 LTS
runner image version: 20260907.300.1
CPython: 3.12.14
git: 2.55.0
```

Command actually executed:

```text
python -m unittest discover -s tests -v
```

## 4. Dedicated Astrology results

### New completion suites

```text
RemainingHouseAxesRegistryTests              8 / 8 PASS
RegistryRetrievalPreconditionTests           4 / 4 PASS
EssentialDignityExpansionRegistryTests       7 / 7 PASS
HighValuePlanetAspectsRegistryTests          7 / 7 PASS
TransitInterpretationRegistryTests           7 / 7 PASS
-------------------------------------------------------
new research-v1 completion tests            33 / 33 PASS
```

### Maintained existing suites

```text
FourthTenthHouseAxisRegistryTests             9 / 9 PASS
FirstSeventhHouseAxisRegistryTests            8 / 8 PASS
ClaimRegistryValidator + compatibility       27 / 27 PASS
Retrieval regressions / behavior              20 / 20 PASS
Registry typed-context migration              11 / 11 PASS
TypedContractV02Tests                         12 / 12 PASS
-------------------------------------------------------
maintained Astrology tests                    87 / 87 PASS
```

Dedicated Astrology total:

```text
33 + 87 = 120
120 / 120 PASS
```

No skipped, expected-failure, failure or error summary was reported.

## 5. Whole-repository result

The same job reported:

```text
Ran 150 tests in 0.205s
OK
```

Therefore:

```text
whole repository: 150 / 150 PASS
```

The workflow then executed:

```text
python tools/playbook_check.py .
```

Observed result:

```text
PASS playbook structure
```

Dedicated Astrology execution, whole-repository unit execution and structural validation are separate evidence categories and must remain described separately.

## 6. What this execution directly establishes

At this feature head, the tested research contracts include:

- all six house-axis research families collectively cover all twelve houses;
- the remaining-house registry validates under the v0.2 taxonomy contract;
- registry-declared L2 preconditions fail closed even when the query omits the old manual boolean flag;
- registry and query preconditions OR-compose deterministically;
- registries without `retrieval_preconditions` preserve prior behavior;
- dignity retrieval can require both supplied L2 dignity facts and an explicit L3 policy;
- Ptolemaic exaltation claims remain typed to the Ptolemaic context;
- competing terms/bounds systems are not flattened;
- Ptolemaic `proper face` terminology is not silently equated with later decan/face tables;
- pair-specific modern aspect interpretations remain qualified REFERENCE_ONLY unless explicitly opted in;
- primary aspect geometry is not treated as pair-specific psychological meaning;
- transit interpretation requires supplied L2 timing facts and L3 policy;
- project transit-policy evidence remains claim/policy eligible while modern timing meanings remain qualified references;
- unknown-time angle/house transit claims retain fail-closed boundaries;
- high-stakes event certainty remains explicitly excluded;
- existing v0.1 and v0.2 compatibility, typed taxonomy, retrieval, migration and L5 contracts remain green.

## 7. What this execution does not establish

This execution does **not** establish:

- scientific or predictive validity of Astrology;
- a production Astrology method;
- a production ephemeris/backend tolerance;
- a canonical house system;
- a canonical term/bound, triplicity or decan table;
- a canonical orb or station-window policy;
- exhaustive historical-source coverage for every planet/aspect pair;
- deterministic transit event prediction;
- production routing authority;
- production admission.

Passing code/regression tests establishes internal contract behavior, not external truth of astrological interpretation.

## 8. Temporary bridge boundary

The execution bridge exists only to obtain direct current-branch execution evidence from the root workflow. It must be deleted before merge.

After deletion, final root CI validates the persistent merge-state diff but must **not** be described as re-running these 120 dedicated Astrology tests.

## 9. Privacy and Palmistry boundary

No real birth data is included in the fixtures or registries in this tranche.

Palmistry is outside this work and is intentionally untouched.
