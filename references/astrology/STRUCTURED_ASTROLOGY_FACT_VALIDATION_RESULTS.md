# Structured Astrology Fact Validation Results｜結構化占星事實驗證結果

Status: **REFERENCE-ONLY / RESEARCH RESULT / NOT PRODUCTION-ROUTABLE**

Branch baseline: `masini1491/ai-divination-playbook@bc0230f895eafd5c8c9e9aca3627e36d0431b52e`

This round converts the previous Structured Astrology Fact draft into a bounded deterministic research validator without promoting Astrology into production routing.

## 1. Validation placement

Current placement is **authorized session-side research execution**.

Reason:

- this is a single-maintainer research surface;
- the validator checks deterministic serialized-record invariants;
- there is no production merge/release/security gate attached to Astrology yet;
- always-on CI would add ceremony without currently adding meaningful independent enforcement.

This placement is not permanent. Production admission or broader mutation paths would require a fresh placement decision.

## 2. Runtime capability

Executed with:

```text
Python 3.13.5
standard library only
```

Commands:

```text
python3 -m py_compile validate_structured_astrology_fact.py
python3 -m unittest -v test_structured_astrology_fact_validator.py
python3 validate_structured_astrology_fact.py structured_astrology_fact_example.json --json
```

## 3. Canonical input identity

The executed local snapshot was reconciled against GitHub branch blobs.

```text
validate_structured_astrology_fact.py
Git blob: dc6e460ac9d79d9818828daf07c1aa16f871df2c

test_structured_astrology_fact_validator.py
Git blob: 17824975af589ab000eaac1f5f4f3ae302b6aa70

structured_astrology_fact_example.json
Git blob: 08f1e006cb1e351fc0f3fae1a1cd0fc39fb03a39
```

All three executed artifacts matched the corresponding branch blob identities before the final run.

## 4. Result

Final regression result:

```text
Ran 19 tests
OK
```

Reference example validator result:

```json
{
  "valid": true,
  "error_count": 0,
  "errors": []
}
```

This proves only the invariants actually covered by this research validator.

## 5. Deterministic invariants covered

The current validator checks:

```text
envelope / schema identity
required fact collections
record-kind/status enums
UTC Z timestamp syntax
search-window ordering
event time inside search window
exact / bounded / ambiguous / unavailable degree shape
exact / bounded / ambiguous / unavailable temporal shape
effective backend presence
sidereal → explicit ayanamsa
fact-id uniqueness
transit target reference resolution
multi-passage semantic identity uniqueness
unknown birth time → house unavailable
unknown birth time → angle/cusp unavailable
aspect signed-error / absolute-error consistency
DST ambiguous local time cannot silently choose one resolved UTC
DST nonexistent local time cannot resolve to UTC
L3/L4 policy/interpretation fields excluded from L1/L2 fact core
station event required shape
ingress event required shape
```

## 6. Positive boundary cases covered

The suite also confirms that these candidate states are representable without false rejection:

```text
synthetic reference triple-passage event collection
bounded natal target + bounded transit time
ambiguous local wall-time provenance with no falsely resolved chart facts
unknown birth time + unavailable house cusp
station event
sign ingress event
```

## 7. Failure-mode examples

Representative rejected states include:

```text
requested backend present but effective backend omitted
sidereal record with no ayanamsa
longitude = 360°
bounded longitude with no ranges
ambiguous event time with fewer than two candidates
exact event outside declared search window
transit target_ref pointing to no declared target fact
duplicate semantic passage_index
unknown-time Ascendant marked available
unknown-time house cusp marked available
fact-core score / interpretation-like policy field
ambiguous DST fold with resolved_utc already chosen
nonexistent DST wall time with resolved_utc
inconsistent aspect signed_error vs absolute_error
```

## 8. Boundary deliberately not automated

The validator does **not** decide:

- whether an astrology interpretation is good or true;
- whether a particular orb is correct;
- whether a dignity / rulership / house-topic tradition should be adopted;
- whether a numeric engine output is astronomically accurate;
- whether an upstream library is trustworthy beyond pinned evidence;
- whether a public fixture is sufficiently anonymized by semantic judgment;
- whether Astrology is ready for production routing;
- production tolerance for cross-engine timestamps / positions.

Those remain research / architecture / evidence decisions.

## 9. Validator role

The validator is intentionally a **research contract checker**, not a new fact owner.

```text
STRUCTURED_ASTROLOGY_FACT_SCHEMA_DRAFT.md
→ owns the current research contract prose

validate_structured_astrology_fact.py
→ mechanically checks selected objective invariants

test_structured_astrology_fact_validator.py
→ protects those validator semantics from regression

STRUCTURED_ASTROLOGY_FACT_VALIDATION_RESULTS.md
→ records this execution evidence
```

None of these artifacts establishes production Astrology capability.

## 10. Remaining gaps

This round closes the first executable schema-validation gap, but leaves:

```text
formal JSON Schema or equivalent interchange schema decision
complete required/optional matrix for every record subtype
stable semantic identifier registry
full fact-lineage reference validation
configuration cross-field validation beyond current minimum
engine-adapter mapping
cross-engine station / ingress / transit-to-natal benchmark
production tolerance selection
L3 tradition-projection contract
interpretation-source architecture
privacy fixture review procedure
production admission
```

A formal JSON Schema is not automatically required next: the current Python validator can express cross-field fail-closed rules that plain schema syntax may not capture cleanly. Whether to add JSON Schema should be decided by interoperability value, not by format completeness alone.

**Current state: REFERENCE-ONLY / RESEARCH RESULT / NOT PRODUCTION-ROUTABLE**
