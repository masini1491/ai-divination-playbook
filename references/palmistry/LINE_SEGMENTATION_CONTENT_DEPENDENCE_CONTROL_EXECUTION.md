# Palm Line Segmentation Content-Dependence / Specificity Control — Execution

Status: **REFERENCE-ONLY / BOUNDED EXECUTION COMPLETE / RESULT INTERPRETATION PENDING**

This record captures the formal MOHI content-dependence / specificity control defined in `LINE_SEGMENTATION_CONTENT_DEPENDENCE_CONTROL_PLAN.md`.

## Formal execution

```text
python references/palmistry/line_segmentation_content_dependence_control_runner.py \
  --model ~/palm-detector-study/palm-line-reader/models/student_fp32.onnx \
  --meta ~/palm-detector-study/palm-line-reader/models/model_meta.json \
  --zip /mnt/c/Users/user/Documents/X/MOHI_sample_10p_3s_5i.zip \
  --mediapipe-results /mnt/c/Users/user/Documents/X/MOHI_repeatability_results.json \
  --repeatability-results ~/palm-detector-study/results/MOHI_line_segmentation_g1_repeatability_upstream_affine_fixed.json \
  --output ~/palm-detector-study/results/MOHI_line_segmentation_content_dependence_control.json
```

All ten frozen sources completed baseline + three frozen content controls.

Final accounting:

```json
{
  "selected_sources": 10,
  "conditions_per_source": 4,
  "completed_inferences": 40,
  "baseline_reproduction_failures": 0,
  "stop": false
}
```

Raw local artifact:

```text
/home/user/palm-detector-study/results/MOHI_line_segmentation_content_dependence_control.json
```

Observed SHA256:

```text
317e85351e4141206b28aec5277433ba3caed9a53e3eb01866cd38900699022f
```

Pinned corrected repeatability authority used by the runner:

```text
a1f0293f3662846255f335fe79d060b054852367f60c74fa4d558e6fe825d238
```

Pinned corrected adapter-diagnosis authority:

```text
c51651cdc267b0416c0883ffba13e1ed0b5992aa808944e1786e2bc20d0e38d3
```

## Evidence boundary

At this stage only execution completeness, baseline-reproduction success, and raw-artifact identity are established. No substantive interpretation has yet been made about low-pass class retention, mask overlap, `global_mean_rgb`, cross-person consensus, canonical-prior behavior, P001/P002 behavior, or pathological occupancy/fragmentation.

No threshold, morphology, crop geometry, low-pass size, source inclusion, or control condition was changed after outcome inspection.

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
