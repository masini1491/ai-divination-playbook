# AST-P2-042 — Continuity-Constrained / Overlap Chebyshev Feasibility Result

Status: **REFERENCE-ONLY / RESEARCH COMPLETE / ARCHITECTURE FEASIBILITY PASS / NOT PRODUCTION-ADMITTED**

## Execution identity

```text
pre-execution frozen contract  6786fb20128c204f525971d06bdd1827620f318f
temporary non-merge PR          #238
probe head                      6d60eef7176a53cd7cab0955e460a591e8f4c7cc
Validate Playbook               run #835 / 36218219868
validate job                    108338359011
unit tests                      PASS
structural checker              PASS
Horizons signature              NASA/JPL Horizons API / 1.2
```

No candidate or threshold was changed after first execution.

## Result

| Variant | Binary | Query | Fixture lon max | Fixture speed max | 5-day-grid lon max | Boundary lon jump | Boundary speed jump | Result |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| C1 D5 / 45 d | 1,023,840 B | 48 B | 3.307″ | 0.000303°/d | 17.580″ | ~0″ | ~0°/d | PASS |
| C1 D7 / 60 d | 1,023,680 B | 64 B | 2.094″ | 0.000336°/d | 9.140″ | ~0″ | ~0°/d | PASS |
| Overlap D5 / 45 d / ±10 d | 1,023,840 B | 48 B | 15.134″ | 0.000990°/d | 29.375″ | 6.314″ | 0.001834°/d | FAIL |
| Overlap D7 / 60 d / ±15 d | 1,023,680 B | 64 B | 9.663″ | 0.000195°/d | 18.416″ | 12.519″ | 0.000467°/d | PASS |

Passing variants:

```text
c1-cheb-d5-w45
c1-cheb-d7-w60
overlap-cheb-d7-w60-p15
```

## What changed relative to AST-P2-041

AST-P2-041 showed that independent hard-switched segments could fit the sampled trajectory well but produced unacceptable speed jumps at segment boundaries.

AST-P2-042 confirms that the failure was architectural rather than a general Chebyshev-accuracy limitation.

The C1 candidates encode continuity directly in the stored coefficients:

```text
P_new(-1)     = P_previous(+1)
dP_new/dt(-1) = dP_previous/dt(+1)
```

They therefore retain the one-segment runtime lookup and satisfy the existing 48/64-byte query payload bound while driving measured boundary value/speed jumps to floating-point noise.

The overlap-trained D7/W60 candidate also passes without runtime blending, but its boundary continuity is only approximate.

## Research front-runner

`c1-cheb-d7-w60` is the strongest current research candidate because:

- every frozen gate passes;
- exact C1 boundary continuity is encoded into the coefficients;
- fixture longitude max is 2.094″;
- fixture speed max is 0.000336°/day;
- complete 5-day source-grid longitude max is 9.140″, the strongest worst-case grid margin among passing candidates;
- artifact size remains 1,023,680 bytes;
- one-query raw coefficient payload remains 64 bytes;
- ordinary runtime needs one segment and no network/blending.

This is a research preference, **not** a production provider selection.

## Queue consequence

AST-P2-042 satisfies the architecture-proof prerequisite that previously blocked AST-P2-040:

```text
at least one five-body local representation
+ prospectively declared accuracy/size/continuity gates
+ bounded ChatGPT materialization envelope
→ PASS
```

Therefore AST-P2-040 may proceed to a separate production-admission review.

That future review still needs to close, at minimum:

- deterministic artifact generator / source provenance;
- immutable artifact identity, integrity and materialization path;
- project-owned runtime evaluator;
- production numeric-validation policy beyond this feasibility experiment;
- coverage/failure behavior;
- provider/admission manifest integration;
- object participation / interpretation boundaries;
- regression evidence.

## Authority boundary

No production provider, calculation fact, object, aspect participant, interpretation claim or ordinary-runtime network dependency is admitted by this report.
