# Palm Line Segmentation Content-Dependence Control Dry Run

Status: **REFERENCE-ONLY / NON-MOHI DRY RUN PASS / READY FOR BOUNDED EXECUTION**

This record captures the pre-formal dry run for `LINE_SEGMENTATION_CONTENT_DEPENDENCE_CONTROL_PLAN.md` and `line_segmentation_content_dependence_control_runner.py`.

## Command

```text
python -m py_compile \
  references/palmistry/line_segmentation_content_dependence_control_runner.py

python references/palmistry/line_segmentation_content_dependence_control_runner.py \
  --model ~/palm-detector-study/palm-line-reader/models/student_fp32.onnx \
  --meta ~/palm-detector-study/palm-line-reader/models/model_meta.json \
  --dry-run
```

## Result

The runner reported:

```text
mode = NON-MOHI CONTENT-DEPENDENCE CONTROL DRY RUN
adapter = C_G1_M0
adapter_geometry = G1_reconstructed_upstream_like
horizontal_mirror = false
schema = PASS
```

All four frozen conditions were produced as RGB `512×512×3`, with mask outputs `512×512` and finite logit summaries:

```text
baseline_512
lowpass_32
lowpass_16
global_mean_rgb
```

The synthetic fixture produced background-only masks for all four conditions. This is dry-run fixture behavior only and is not substantive MOHI evidence.

## Manipulation-check note

On the synthetic ellipse fixture, the recorded 3×3 Sobel mean gradient energy for `lowpass_32` and `lowpass_16` was approximately 1% higher than baseline even though the transforms are explicitly:

```text
512 -> INTER_AREA downsample to 32 or 16 -> INTER_LINEAR upsample to 512
```

This does not invalidate the frozen low-pass controls. The Sobel statistic is a descriptive manipulation check rather than a monotonic pass/fail criterion. With a binary-like synthetic ellipse, downsample/upsample can broaden major object edges and slightly increase the mean local Sobel magnitude while still removing fine spatial detail.

No control sizes, interpolation rules, thresholds, morphology, or model settings were changed in response to this dry-run observation.

## Evidence boundary

This dry run establishes only executable/schema integrity before bounded MOHI execution. It does not establish content dependence, canonical-prior behavior, segmentation accuracy, anatomical validity, or production suitability.

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
