# Zi Wei 14×12 Star × Palace Coverage Architecture V1

Status: **ARCHITECTURE CANDIDATE / ROUTING-COVERAGE ONLY**

## Goal

Expose all 14 major stars × 12 canonical palaces = **168 cells** as
machine-readable routing identities without forcing 168 dedicated L4 doctrines.

The earlier sparse architecture remains semantically valid: dedicated L4
overrides still require materially distinct admitted evidence. This refactor
changes the control plane, not that evidence rule.

## Canonical distinction

```text
168 dedicated L4 doctrine records       REJECTED
168 machine-visible coverage identities ADOPTED
```

Every cell has a review status and routing mode. Detailed evidence stays in its
canonical research/admission owner.

## Canonical identities

Stars:
`紫微 天機 太陽 武曲 天同 廉貞 天府 太陰 貪狼 巨門 天相 天梁 七殺 破軍`

Palaces:
`命宮 兄弟宮 夫妻宮 子女宮 財帛宮 疾厄宮 遷移宮 奴僕宮 官祿宮 田宅宮 福德宮 父母宮`

`奴僕宮` follows the existing canonical palace registry. `交友宮` may be an
alias elsewhere; it does not create a thirteenth matrix identity.

## Routing modes

- `DEDICATED_L4` — exact production-admitted contextual override.
- `BOUNDED_L5_COMPOSITION` — reviewed; existing star core + palace domain is sufficient.
- `CONDITIONAL_ONLY` — resolved only through explicit admitted conditions.
- `HIGH_RISK_BOUNDED` — reviewed high-stakes cell with stricter rendering policy.
- `DEFERRED_EVIDENCE` — reviewed but unresolved; does not count toward completion.
- `UNREVIEWED` — identity exists but research classification is incomplete.

## Completion

`reviewed_cells` counts completed classification passes, including deferred
cells. `resolved_cells` counts cells with a stable production routing mode.

**Project target = resolved_cells 168 / 168.**

Dedicated L4 count is tracked separately and is not the completion denominator.

## Authority and generation

```text
production star×palace registry ─┐
bounded research decision input ─┼→ project generator
                                 ↓
indexes/ziwei/star_palace_coverage_v1.json
                                 ↓
routing/control-plane only
```

The generated index never becomes source or doctrine authority.

## Hot / Cold loading

The 168-cell index is compact deterministic routing metadata. It intentionally
contains identity, mode and pointers only. Long-form source text, research
rationale and doctrine remain cold/on-demand.

Ordinary ChatGPT use should resolve the target cell first, then retrieve only
the required semantic owner. Full doctrine must not be copied into the Hot
index or ordinary load pack.

## Initial conservative backfill

- 7 current production pairs → `DEDICATED_L4 / resolved`
- 4 explicit redundant V1–V3 results → `BOUNDED_L5_COMPOSITION / resolved`
- 4 inconclusive/borderline V1–V3 results → `DEFERRED_EVIDENCE / reviewed`
- all other cells → `UNREVIEWED`

Initial metrics:

```text
total       168
reviewed     15
resolved     11
unreviewed  153
dedicated     7
bounded L5    4
deferred      4
```

V4 preliminary backlog candidates remain unreviewed until V4 research actually
executes.

## Safety

Coverage is not permission to invent deterministic claims. Existing
relationship, wealth/property, health/injury/mortality and concrete-event safety
boundaries remain in force.

## V4

`ZW-P2-026` resumes after this architecture is admitted and updates the matrix
in bounded research batches until `resolved_cells = 168`.
