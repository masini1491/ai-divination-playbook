# Principal-line Line-detail Quality Gate — Dry-run Evidence

Status: **REFERENCE-ONLY / PRE-EXECUTION DRY RUN PASSED / NO MOHI QUALITY RESULT YET**

## Purpose

This record closes only the runtime dry-run gate for `LINE_DETAIL_QUALITY_GATE_PLAN.md` and `line_detail_quality_gate_runner.py`.

It does **not** contain the 9-source × 10-condition MOHI quality-study result and does not establish any production image-quality threshold.

## Repository / execution identity

User-side local repository was updated to and verified at:

```text
86e8b87ec243c35251652a71b3496d9be067de1e
```

The executed runner was:

```text
references/palmistry/line_detail_quality_gate_runner.py
```

The local environment used the existing `palm-lines` Conda environment and the already-pinned palm-line ONNX model / metadata paths.

## Syntax / execution checks

Observed:

```text
PY_COMPILE = PASS
DRY_RUN_EXECUTION = PASS
```

The dry-run mode reported:

```text
mode            = NON-MOHI LINE-DETAIL QUALITY GATE DRY RUN
schema          = PASS
condition_count = 10
```

## Frozen dry-run artifact

Local artifact:

```text
/home/user/palm-detector-study/results/LINE_DETAIL_QUALITY_GATE_DRY_RUN.json
```

SHA256:

```text
5d84370950c940b4961d36bee6598cb1f5d9f5452bbc8646c170a2c287e8bec5
```

This hash was computed immediately after the dry-run output was generated and parsed.

## Condition-level runtime checks

All 10 predeclared conditions preserved the required `512×512×3` `uint8` image contract and returned finite model-logit summaries.

Observed descriptor / synthetic-model foreground summaries:

| Condition | Laplacian variance | RMS contrast | Foreground fraction |
|---|---:|---:|---:|
| baseline | 1647.31 | 0.10209 | 0.000000 |
| blur sigma 1.5 | 52.05 | 0.09818 | 0.000000 |
| blur sigma 3.0 | 9.95 | 0.09514 | 0.000000 |
| blur sigma 6.0 | 5.02 | 0.09221 | 0.000000 |
| down/up 256 | 143.83 | 0.09941 | 0.000000 |
| down/up 128 | 47.38 | 0.09705 | 0.000000 |
| down/up 64 | 9.76 | 0.09406 | 0.000000 |
| contrast 0.75 | 917.46 | 0.07609 | 0.000000 |
| contrast 0.50 | 404.85 | 0.05016 | 0.000000 |
| contrast 0.25 | 104.34 | 0.02536 | 0.000000 |

The all-zero foreground behavior is a property of this **non-MOHI synthetic disposable fixture** and is not interpreted as evidence about principal-line model quality. The purpose of this dry run was to exercise preprocessing, degradation generation, descriptor calculation, ONNX inference, output schema, and comparison code paths without inspecting MOHI study results.

## Manipulation-path sanity

The observed descriptors move in the expected manipulation direction at a basic implementation level:

- Gaussian blur sharply reduces Laplacian variance as sigma increases.
- Resolution destruction reduces high-frequency detail as the downsample side decreases.
- Contrast compression reduces RMS contrast as the factor decreases.

These are manipulation checks only. They are not admission cutoffs and are not evidence that any one descriptor is sufficient to classify `line_detail` quality.

## Gate decision

The pre-execution dry-run gate is closed as:

```text
python syntax/import path exercised = YES
10 condition generators executed    = YES
512×512 geometry preserved          = YES
uint8 input contract preserved      = YES
finite ONNX logit summaries         = YES
JSON schema                         = PASS
dry-run artifact SHA frozen         = YES
```

Therefore the next allowed action is the predeclared full primary execution:

```text
P002/S1/01.jpg through P010/S1/01.jpg
9 sources
× 10 conditions
= 90 primary inference conditions
```

P001 remains excluded from primary quantitative aggregates because its frozen manual reference is reference-quality-confounded. Running P001 as an optional descriptive sentinel is not required for the primary node.

## Stop / interpretation boundary

The full run must still stop if frozen provenance fails to reproduce, including annotation SHA, anatomical-audit result SHA, spatial-control SHA, baseline input SHA, baseline mask SHA, source-set identity, runtime/model validation, or the 9-source execution contract.

No substantive full-study metric may be interpreted until the resulting JSON is written and SHA256-frozen.

This record establishes only that the dry-run implementation gate passed. It does not establish:

- MOHI quality-study results;
- a `line_detail` sufficient/partial/insufficient threshold;
- anatomical ground truth;
- production admission policy;
- Palmistry interpretation validity.

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
