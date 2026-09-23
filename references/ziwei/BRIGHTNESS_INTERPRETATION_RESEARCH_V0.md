# Zi Wei Brightness Interpretation Research v0

Authority：`REFERENCE-ONLY / RESEARCH DECISION / NOT PRODUCTION-ROUTABLE`

## Decision summary

```text
brightness identity                         PROFILE-BOUND CHART FACT
profile-free universal brightness           REJECTED
generic brightness-only L4 dictionary       NOT REQUIRED
brightness-conditioned L4 claims            ALLOWED WHEN SOURCED / ADMITTED
unknown / not_computed brightness            FAIL CLOSED
default project brightness table             NOT SELECTED
engine-table convergence                     NOT CLAIMED
production authority                         false
```

## Responsibility boundary

Brightness（廟／旺／得／利／平／不／陷等 label families）先是 calculation/profile 層的 chart fact，之後才可成為 interpretation claim 的 applicability modifier。

本研究線因此維持：

```text
calculation/profile evidence
→ profile-scoped brightness fact
→ sourced L4 claim applicability
→ bounded L5 synthesis
```

不得反向把 interpretation wording 當成 brightness table 的 calculation authority。

## Implementation evidence

Current reference implementations show that brightness is represented as configurable rule/profile data rather than inferred prose:

- `SylarLong/iztro@2c7ef9be669df7b19d1799f4dce335fed3794f78` stores per-star brightness arrays in `src/data/stars.ts`, with the file explicitly declaring branch ordering from 寅 and localized labels `廟／旺／得／利／平／不／陷`.
- `RedSC1/js-ephemeris-lite@559d4957bc063a6e03a3c810066be4eccf3ea2be` stores generated/configurable brightness rule tables and supports custom brightness labels/rules.

These implementations are `REFERENCE-ONLY`. Raw array differences are not treated as doctrinal disagreement until branch order, label scale and rule-profile identity are matched.

## Interpretation policy

Existing admitted claims already demonstrate the correct pattern:

- 太陽: 得地／失輝 is a material modifier;
- 太陰: 得垣／得輝／失輝 is a material modifier;
- other major-star claims may declare `dignity` / brightness-sensitive applicability without creating a universal “廟一定吉、陷一定凶” rule.

Therefore brightness normally modifies a sourced claim; it does not automatically generate a standalone doctrine sentence.

A dedicated L4 brightness claim requires explicit source support for the semantic effect being asserted. A brightness fact alone is insufficient to produce a guaranteed real-world outcome.

## Fact contract

A usable brightness fact must retain at least:

```text
star identity
branch / placement identity
brightness value / label
brightness_profile
rule source / engine revision
fact state
provenance
```

A bare value without profile/provenance is insufficient for research retrieval.

## Fail-closed behavior

```text
brightness unknown
→ skip brightness-dependent claim

brightness not_computed
→ do not infer from model memory

brightness profile unresolved
→ preserve ambiguity / omit dependent conclusion

implementation tables differ before normalization
→ do not majority-vote
```

## Default-profile decision

This stage does **not** select a project-wide `brightness_profile`. Current implementation evidence is sufficient to establish the responsibility boundary and modifier semantics, but not sufficient to claim that one table is the unique historical/default authority.

A future brightness-table selection requires a separately identified source/profile reconciliation or an explicit project design decision with its basis recorded.

## Research closure

```text
brightness interpretation responsibility = CLOSED — RESEARCH
brightness modifier semantics             = CLOSED — RESEARCH
project default brightness table          = OPEN / NOT SELECTED
production brightness provider            = NOT ADMITTED
```

This closure allows later interpretation research to proceed without silently selecting a brightness table.
