# Palm Line Segmentation G1 Repeatability — Upstream-Affine-Fixed Execution

Status: **REFERENCE-ONLY / CORRECTED BOUNDED EXECUTION COMPLETE / RESULT INTERPRETATION PENDING**

This record captures the formal MOHI repeatability rerun under the corrected upstream-affine-fixed `C_G1_M0` adapter contract defined in `LINE_SEGMENTATION_G1_REPEATABILITY_UPSTREAM_AFFINE_FIXED_PLAN.md`.

## Formal execution

```text
python references/palmistry/line_segmentation_g1_repeatability_upstream_affine_fixed_runner.py \
  --model ~/palm-detector-study/palm-line-reader/models/student_fp32.onnx \
  --meta ~/palm-detector-study/palm-line-reader/models/model_meta.json \
  --zip /mnt/c/Users/user/Documents/X/MOHI_sample_10p_3s_5i.zip \
  --mediapipe-results /mnt/c/Users/user/Documents/X/MOHI_repeatability_results.json \
  --output ~/palm-detector-study/results/MOHI_line_segmentation_g1_repeatability_upstream_affine_fixed.json
```

All ten frozen sources completed baseline + five frozen perturbations.

Final accounting:

```json
{
  "selected_sources": 10,
  "conditions_per_source": 6,
  "completed_inferences": 60,
  "stop": false
}
```

Corrected raw artifact:

```text
/home/user/palm-detector-study/results/MOHI_line_segmentation_g1_repeatability_upstream_affine_fixed.json
```

Observed SHA256:

```text
a1f0293f3662846255f335fe79d060b054852367f60c74fa4d558e6fe825d238
```

The runner pins the corrected adapter-diagnosis artifact SHA:

```text
c51651cdc267b0416c0883ffba13e1ed0b5992aa808944e1786e2bc20d0e38d3
```

## Evidence boundary

At this stage only execution completeness and raw-artifact identity are established. Corrected baseline presence, perturbation retention, Dice/IoU, transition accounting, fragmentation, per-image heterogeneity, and comparison with the legacy superseded repeatability artifact have not yet been interpreted in this record.

The legacy repeatability artifact remains historical evidence for the superseded pre-correction G1 crop implementation and must not be treated as the corrected result.

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
