# Astrology Retrieval Behavior Validation Results

Status: **REFERENCE-ONLY / RESEARCH VALIDATION / NOT PRODUCTION-ROUTABLE**

Branch baseline:

`b3a1f83a96201a2d4d3e1befe67b23b3f0531d68`

Runtime used for the isolated deterministic replay:

- Python standard library only
- no network dependency
- no semantic-search package
- no astrology calculation package

## Scope

This round validates the deterministic boundary:

```text
resolved query specification
+
versioned interpretation claim registry
→
selected source-backed claims
+
conflicts
+
guardrails
+
source provenance
+
L2/L3/L4 synthesis references
```

The selector does not parse free-form user language and does not generate a reading.

## Files

Executable selector:

`retrieve_interpretation_claims.py`

Regression suite:

`test_retrieve_interpretation_claims.py`

Contract:

`RETRIEVAL_OUTPUT_PROVENANCE_CONTRACT_DRAFT.md`

## Deterministic invariants exercised

The regression set covers:

1. exact claim-type selection;
2. tradition filter;
3. applicability AND-filter;
4. missing L2 facts fail closed;
5. missing L3 policy fail closed;
6. unrepresented tradition returns `no_match`;
7. `REFERENCE_ONLY` source evidence excluded by default;
8. explicit qualified opt-in for `REFERENCE_ONLY` evidence;
9. unqualified `REFERENCE_ONLY` evidence remains excluded even with opt-in;
10. mixed claim-eligible + `REFERENCE_ONLY` provenance also requires explicit qualified opt-in;
11. conflict groups remain visible rather than being averaged;
12. external claims in a selected conflict group remain visible as `external_claim_refs`;
13. registered non-admitted claims can be carried as guardrails;
14. guardrails can be omitted when the resolved query does not request them;
15. selected claims retain source locator provenance;
16. missing source locator produces `provenance_incomplete` rather than `citation_ready`;
17. synthesis provenance preserves L2 fact refs;
18. synthesis provenance preserves L3 policy refs;
19. synthesis provenance preserves L4 claim refs and conflict refs;
20. research registry production/privacy guards fail closed.

## Important defect found during regression design

The first selector prototype treated a claim as admissible whenever at least one cited source was claim-eligible.

That was insufficient for a mixed-provenance claim such as:

```text
CLAIM_ELIGIBLE practitioner source
+
REFERENCE_ONLY reference implementation
```

because the claim-eligible source could effectively launder the reference-only source into the result.

The implemented rule is now:

```text
all sources claim-eligible
→ selected normally

any REFERENCE_ONLY source participates
→ explicit allow_reference_only_qualified=true required
→ claim must still be qualified / tradition-bounded / architecture-bounded / conflicted
```

This applies both to pure `REFERENCE_ONLY` and mixed provenance.

## Isolated execution result

A deterministic replay of the selector logic was executed against:

- 15 synthetic invariant cases;
- 5 query cases reconstructed from the current connector-reviewed domicile and Moon-Saturn registry fields relevant to those queries.

Observed result:

```text
20 cases executed
20 PASS
0 FAIL
```

The five real-family replay cases were:

1. classical domicile configuration;
2. southern-hemisphere domicile applicability conflict;
3. modern psychological natal Moon-Saturn opposition;
4. Moon-Saturn opposition reference-implementation opt-in behavior;
5. unrepresented Moon-Saturn tradition → `no_match`.

## Direct repo-file execution status

The committed unittest suite directly opens:

```text
domicile_claim_family_registry.json
saturn_moon_aspect_claim_family_registry.json
```

when executed in a repository checkout or CI workspace.

The current isolated Python runtime is not a repository checkout, so this round does **not** claim that the GitHub-hosted registry bytes themselves were directly opened by the runtime.

The evidence level for this round is therefore:

```text
selector logic executed
+
synthetic invariants executed
+
current registry fields connector-reviewed
+
real-family query behavior replayed from those reviewed fields
+
repo-local direct-file regression suite committed
```

not:

```text
remote GitHub files directly executed inside the isolated runtime
```

This distinction is intentional and preserves the repository's evidence rules.

## Selected behavioral outcomes

### Domicile configuration

Resolved query requires:

```text
claim_type = policy_configuration
tradition = ptolemaic/classical
applies_to = domicile configuration
L2 placement ref present
L3 policy ref present
```

Expected selected claim:

`claim:domicile-configuration`

The historical southern-hemisphere conflict remains a registered separate context rather than changing the requested configuration claim into a universal doctrine.

### Southern-hemisphere historical conflict

Resolved historical query selects:

`claim:southern-hemisphere-reversal-debate`

and preserves:

`conflict:southern-hemisphere-dignity-applicability`

with other claims in that conflict visible as external claim refs.

### Modern natal Moon-Saturn opposition

With:

```text
claim_type = aspect_meaning
tradition = modern / psychological_astrology
applies_to = natal + Moon-Saturn opposition
L2 aspect ref present
L3 aspect-policy ref present
```

expected selected claim is:

`claim:greene-moon-saturn-parent-image`

The more generic reference-implementation opposition claim is not selected merely because it shares the planet pair.

### Reference implementation opt-in

The reference-implementation claim:

`claim:reference-opposition-polarity`

contains mixed provenance:

```text
REFERENCE_ONLY implementation
+
CLAIM_ELIGIBLE practitioner source
```

Default:

```text
excluded
```

Explicit qualified opt-in:

```text
selected with source_admission_mode = mixed_claim_eligible_and_reference_only
```

The source admission boundary remains visible in the output bundle.

### Unknown tradition

A valid query for an unrepresented tradition returns:

```text
retrieval_status = no_match
selected_claim_ids = []
```

There is no automatic broadening and no model-memory fallback in the deterministic selector.

## Citation / output provenance result

A selected claim is considered `citation_ready` only when each cited source has a non-empty source locator.

The bundle retains:

```text
source_id
source role
source admission status
source locator
edition when present
immutable revision when present
publication date when present
license / copyright status when present
```

The bundle also retains:

```text
synthesis_provenance.l2_fact_refs
synthesis_provenance.l3_policy_refs
synthesis_provenance.claim_refs
synthesis_provenance.conflict_group_refs
```

This makes the later L5 synthesis auditable without pretending that the selector itself has formatted a final citation.

## Explicit non-goals

This validation does not establish:

- correct natural-language query parsing;
- semantic-search quality;
- a canonical tradition taxonomy;
- a canonical orb policy;
- completeness of claim coverage;
- correctness of astrological interpretation;
- clinical validity;
- predictive validity;
- another person's private state;
- production routing.

## Research conclusion

The interpretation research line now has an executable boundary from versioned claim registries into a provenance-preserving retrieval bundle.

The key invariant is:

```text
available deterministic fact
+
explicit policy context
+
exact claim applicability
+
source admission
+
conflict preservation
+
locator provenance
→ citation-ready research bundle
```

and not:

```text
planet pair keyword
→ retrieve every familiar meaning
→ blend traditions
→ fill gaps from model memory
```

## Next gap

The next useful research step is:

```text
query-resolution / routing contract
→ user-facing citation rendering contract
→ L5 synthesis regression
→ broader claim-family conflict coverage
→ explicit tradition taxonomy
→ production admission
```

**Current state: REFERENCE-ONLY / RESEARCH / NOT PRODUCTION-ROUTABLE.**
