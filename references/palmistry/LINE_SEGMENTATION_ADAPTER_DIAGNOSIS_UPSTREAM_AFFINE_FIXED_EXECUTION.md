# Palm Line Segmentation Adapter Diagnosis — Upstream-Affine-Fixed Execution

Status: **REFERENCE-ONLY / CORRECTED BOUNDED EXECUTION COMPLETE / RESULT INTERPRETATION PENDING**

This record captures the formal MOHI rerun after the pre-existing G1 implementation-fidelity correction documented in `LINE_SEGMENTATION_G1_IMPLEMENTATION_FIDELITY_CORRECTION.md`.

The correction changed only the reconstructed G1 crop affine composition so that the float landmark bbox origin is absorbed directly into the affine translation before a single source-to-output `warpAffine`, matching the pinned upstream reconstruction more closely. It did not change the model, runtime, frozen source sample, MediaPipe landmarks, 100 px margin, rotation-sign selection, mirror definitions, thresholds, morphology, or class mapping.

## Formal execution

```text
python references/palmistry/line_segmentation_adapter_diagnosis_runner.py \
  --model ~/palm-detector-study/palm-line-reader/models/student_fp32.onnx \
  --meta ~/palm-detector-study/palm-line-reader/models/model_meta.json \
  --zip /mnt/c/Users/user/Documents/X/MOHI_sample_10p_3s_5i.zip \
  --mediapipe-results /mnt/c/Users/user/Documents/X/MOHI_repeatability_results.json \
  --output ~/palm-detector-study/results/MOHI_line_segmentation_adapter_diagnosis_upstream_affine_fixed.json
```

All ten frozen sources completed A/B/C/D.

Final accounting:

```json
{
  "selected_sources": 10,
  "adapters_per_source": 4,
  "completed_inferences": 40,
  "stop": false
}
```

Corrected raw artifact:

```text
/home/user/palm-detector-study/results/MOHI_line_segmentation_adapter_diagnosis_upstream_affine_fixed.json
```

Observed SHA256:

```text
c51651cdc267b0416c0883ffba13e1ed0b5992aa808944e1786e2bc20d0e38d3
```

## Evidence boundary

At this stage only execution completeness and raw-artifact identity are established. Corrected C/D observability, occupancy, components, factor effects, and legacy-vs-corrected agreement have not yet been interpreted in this record.

The legacy adapter diagnosis artifact remains preserved but is superseded for exact-upstream-affine G1 ranking. A/B remain unaffected by the G1 affine correction.

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
