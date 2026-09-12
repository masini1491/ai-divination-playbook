# Palm Line Segmentation Spatial-Structure / Texture-Cue Control — Execution

Status: **REFERENCE-ONLY / BOUNDED EXECUTION COMPLETE / RESULT INTERPRETATION PENDING**

This record captures the formal MOHI execution of the predeclared spatial-structure / texture-cue control defined in `LINE_SEGMENTATION_SPATIAL_STRUCTURE_CONTROL_PLAN.md`.

## Formal execution

```text
python references/palmistry/line_segmentation_spatial_structure_control_runner.py \
  --model ~/palm-detector-study/palm-line-reader/models/student_fp32.onnx \
  --meta ~/palm-detector-study/palm-line-reader/models/model_meta.json \
  --zip /mnt/c/Users/user/Documents/X/MOHI_sample_10p_3s_5i.zip \
  --mediapipe-results /mnt/c/Users/user/Documents/X/MOHI_repeatability_results.json \
  --content-control-results ~/palm-detector-study/results/MOHI_line_segmentation_content_dependence_control.json \
  --output ~/palm-detector-study/results/MOHI_line_segmentation_spatial_structure_control.json
```

All ten frozen sources completed baseline + three spatial controls.

Final accounting:

```json
{
  "selected_sources": 10,
  "conditions_per_source": 4,
  "completed_inferences": 40,
  "anchor_reproduction_failures": 0,
  "stop": false
}
```

Raw artifact:

```text
/home/user/palm-detector-study/results/MOHI_line_segmentation_spatial_structure_control.json
```

Observed SHA256:

```text
ba65456e3c7c3a645a4000c721961d0f600b46541ffc7e7566525b99a55f87e7
```

## Upstream evidence authority

The spatial-structure plan pins the prior content-dependence raw artifact:

```text
317e85351e4141206b28aec5277433ba3caed9a53e3eb01866cd38900699022f
```

That prior artifact in turn pins the corrected adapter diagnosis and corrected G1 repeatability evidence nodes.

## Evidence boundary

At this stage only execution completeness, anchor reproduction success, and raw-artifact identity are established.

The following have **not** yet been interpreted in this record:

- class presence under `residual_shuffle_64`;
- class presence under `residual_shuffle_32`;
- class presence under `residual_sign_flip`;
- direct baseline Dice / IoU;
- inverse-unshuffle Dice / IoU;
- clipping behavior across the formal MOHI sample;
- fragmentation / flooding;
- cross-person consensus;
- P001 / P002 heterogeneity.

Do not use this execution record alone to infer coherent crease dependence, generic texture-cue dependence, anatomical correctness, segmentation accuracy, or production readiness.

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
