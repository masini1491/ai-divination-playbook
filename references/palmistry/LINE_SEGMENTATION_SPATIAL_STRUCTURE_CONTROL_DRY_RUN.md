# Palm Line Segmentation Spatial-Structure / Texture-Cue Control — Dry Run

Status: **REFERENCE-ONLY / NON-MOHI DRY RUN PASS / FORMAL RUN NOT YET INTERPRETED**

This record captures the non-MOHI dry run for `line_segmentation_spatial_structure_control_runner.py` under the predeclared `LINE_SEGMENTATION_SPATIAL_STRUCTURE_CONTROL_PLAN.md` contract.

## Repository state

Dry run executed after synchronizing `main` to:

```text
6f62f657dd0c9177aa3349783564b9507cc61c48
```

## Dry-run execution

```text
python -m py_compile \
  references/palmistry/line_segmentation_spatial_structure_control_runner.py

python references/palmistry/line_segmentation_spatial_structure_control_runner.py \
  --model ~/palm-detector-study/palm-line-reader/models/student_fp32.onnx \
  --meta ~/palm-detector-study/palm-line-reader/models/model_meta.json \
  --dry-run
```

Observed schema:

```text
mode = NON-MOHI SPATIAL-STRUCTURE CONTROL DRY RUN
adapter = C_G1_M0
adapter_geometry = G1_reconstructed_upstream_like
horizontal_mirror = false
schema = PASS
```

All four frozen conditions produced:

```text
input_shape = [512, 512, 3]
mask_shape = [512, 512]
finite_logit_summary = true
```

The frozen residual permutations satisfied their declared integrity checks:

```text
residual_shuffle_64:
  tile_px = 64
  tile_count = 64
  fixed_tile_positions = 0
  inverse_unshuffle_shape = [512, 512]

residual_shuffle_32:
  tile_px = 32
  tile_count = 256
  fixed_tile_positions = 0
  inverse_unshuffle_shape = [512, 512]
```

Synthetic dry-run residual mean absolute magnitude:

```text
3.12585186958313 / 255-scale RGB units
```

Observed clipping fractions:

```text
baseline_512         = 0.0000000000
residual_shuffle_64  = 0.0409113566
residual_shuffle_32  = 0.0546925863
residual_sign_flip   = 0.0009078979
```

## Clipping interpretation before formal MOHI execution

The non-zero clipping under shuffled residual reconstruction is not treated as a protocol failure because clipping is explicitly part of the predeclared S1/S2 reconstruction:

```text
clip(lowpass_32 + shuffled_residual, 0, 255)
```

The plan also freezes clipping behavior against post-outcome changes and declares clipping fraction as a primary manipulation metric.

Therefore the observed synthetic clipping fractions are retained as measured manipulation side effects; no tile size, permutation, residual scaling, clipping rule, or reconstruction formula is changed before the formal run.

This does not mean clipping is causally irrelevant. Formal interpretation must preserve it as a bounded confound/side effect when evaluating any S1/S2 output change.

## Dry-run conclusion

The executable contract, frozen conditions, permutation integrity, inverse-unshuffle path, model-input geometry, and finite inference path all passed the non-MOHI dry run.

Formal MOHI execution is permitted under the frozen protocol.

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
