# Astrology Sparse Exact-Claim Admission Policy V1

Status: **REFERENCE-ONLY / RESEARCH POLICY / NOT PRODUCTION-ROUTABLE**

Purpose: decide whether an exact Planet×Sign or Planet-Pair×Aspect semantic claim is worth opening as a bounded research node. This policy does **not** itself admit claims into production.

## 1. State model

Every evaluated semantic gap must resolve to exactly one state:

```text
composition_adequate
research_candidate
exact_claim_admitted
unsupported
```

### composition_adequate

Use when already-admitted lower-level primitives can express the requested meaning without a material semantic loss.

Required properties:

- all required lower-level semantic primitives are production-admitted;
- typed applicability/profile/source gates pass;
- no exact claim is needed merely for prettier prose or matrix completeness;
- adding an exact claim would substantially duplicate the lower-level composition.

Action: use bounded composition; do not open exact-claim research.

### research_candidate

Use only when there is a bounded, demonstrable **material semantic delta** that lower-level composition cannot safely represent.

At least one trigger must be documented:

1. production interpretation remains materially over-generic after valid composition;
2. a recurring production gap cannot be expressed by admitted primitives without inventing meaning;
3. source-backed exact semantics materially differ from the lower-level composition;
4. typed applicability requires a context-specific semantic distinction not represented by current primitives.

The candidate must name:

- exact subject identity;
- current lower-level composition/boundary;
- missing semantic delta;
- proposed evidence search scope;
- applicable profile/context;
- anti-duplication note.

A candidate is **research only**. It creates no production support, routing authority, queue priority, neighboring matrix work, or default expansion.

### exact_claim_admitted

Use only when a separately admitted registry/claim/source-policy path already exists for the exact subject and applicable context.

The exact claim may add only its admitted emergent delta. It must not:

- rewrite deterministic facts;
- restate the entire lower-level composition;
- erase source/tradition/context boundaries;
- imply scientific, clinical, or psychometric validity.

### unsupported

Use when required primitives/evidence/profile/applicability are missing and there is not yet enough bounded evidence to justify either composition or exact-claim admission.

Unsupported may become a future research candidate only after a new bounded evidence trigger appears. Unsupported status alone does not create a backlog.

## 2. Anti-Cartesian rule

This policy explicitly rejects:

- mandatory 10×12 Planet×Sign completion;
- mandatory planet-pair × major-aspect completion;
- automatic neighboring-cell research after one exact claim is admitted;
- coverage percentages as a reason to author semantics;
- user “accuracy” or resonance feedback as semantic-admission evidence.

Research is event-triggered and sparse, not matrix-completion driven.

## 3. Production / research separation

```text
gap detected in production
→ evaluate with this research policy
→ maybe research_candidate
→ bounded evidence work
→ research registry / validator
→ explicit production admission decision
```

Skipping any step is forbidden. The research validator remains unable to self-promote a registry into production.

## 4. Representative current-state examples

The machine-readable fixture in `EXACT_CLAIM_ADMISSION_POLICY_V1.json` binds this policy to representative current repository states:

- ordinary Planet×Sign using admitted planet-function + sign-style primitives → `composition_adequate`;
- qualified-only high-value aspect pair meaning → `research_candidate`;
- admitted Moon–Saturn opposition exact meaning → `exact_claim_admitted`;
- generic natal aspect semantics without an admitted exact claim or admitted composition primitives → `unsupported`.

These examples are policy regressions, not a permanent ranked work queue.

## 5. Candidate closure rule

A research candidate closes by one of three outcomes:

```text
evidence shows no material delta
→ composition_adequate

evidence supports bounded exact claim + explicit production admission
→ exact_claim_admitted

evidence remains insufficient / inapplicable
→ unsupported
```

Do not preserve a permanent “candidate backlog” solely because research was once considered.
