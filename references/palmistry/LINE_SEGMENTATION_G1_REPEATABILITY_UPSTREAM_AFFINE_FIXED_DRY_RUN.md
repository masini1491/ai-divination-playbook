# Palm Line Segmentation G1 Repeatability — Upstream-Affine-Fixed Dry Run

Status: **REFERENCE-ONLY / NON-MOHI DRY RUN PASS / READY FOR BOUNDED EXECUTION**

This record captures the synthetic-only dry run for the separately predeclared corrected-G1 repeatability qualification implemented by `line_segmentation_g1_repeatability_upstream_affine_fixed_runner.py`.

No MOHI substantive output was inspected in this dry run.

## Contract

```text
adapter = C_G1_M0
geometry = G1_reconstructed_upstream_like
horizontal_mirror = false
corrected adapter-diagnosis SHA256 = c51651cdc267b0416c0883ffba13e1ed0b5992aa808944e1786e2bc20d0e38d3
```

The crop implementation is supplied by the corrected adapter module using the direct source-to-crop upstream-affine reconstruction. The perturbation and inverse-mapping implementation is reused from the previously validated rectangular G1 repeatability runner.

## Observed dry-run output

```text
mode = NON-MOHI G1 REPEATABILITY DRY RUN
adapter = C_G1_M0
crop_shape = [530, 403, 3]
adapter_geometry = G1_reconstructed_upstream_like
horizontal_mirror = false
baseline_shape = [530, 403]
baseline_values_subset = [0]
finite_logit_summary = true
schema = PASS
```

All five frozen perturbations completed:

```text
rotate_p5
rotate_m5
scale_090
scale_110
center_crop_3pct
```

For each perturbation:

```text
matrix_shape = [2, 3]
variant_shape = [530, 403, 3]
mapped_shape = [530, 403]
mapped_values_subset = [0]
```

The all-background synthetic output is a property of the dry-run fixture only. It is not interpreted as a model-quality result and does not constitute MOHI evidence.

## Gate result

PASS for bounded formal execution because:

- the corrected C_G1_M0 adapter resolves successfully;
- finite logits are produced;
- the baseline frame is deterministic;
- every frozen perturbation uses a 2x3 affine matrix;
- every variant remains in the baseline rectangular frame dimensions;
- every inverse-mapped mask returns to the baseline mask dimensions;
- the output schema completes without drift.

No thresholds, morphology, margin tuning, source exclusions, mirror changes, or post-outcome rescue were introduced.

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
