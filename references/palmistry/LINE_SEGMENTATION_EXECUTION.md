# Palm Line Segmentation Execution

Status: **REFERENCE-ONLY / CORRECTED RUNNER EXECUTION COMPLETE / RESULT INTERPRETATION PENDING**

本文件記錄 `LINE_SEGMENTATION_REPEATABILITY_PLAN.md` 第一輪正式 MOHI execution accounting。此時只確認 execution 完成，不在本文件提前解讀 Dice / IoU outcome。

## Prerequisites

在正式 MOHI execution 前，已完成：

- isolated `palm-lines` runtime；
- exact package/runtime validation；
- FP32 ONNX / metadata SHA256 validation；
- CPU-only `InferenceSession` contract validation；
- synthetic tensor model smoke test；
- corrected non-MOHI dry-run `schema = PASS`；
- dry-run 的 `cv2.arc` typo 在任何 MOHI inference 前被發現並修正。

正式 full mode 使用：

```text
references/palmistry/line_segmentation_repeatability_runner_cv2_fixed.py
```

其 full MOHI path沿用 `line_segmentation_repeatability_runner.py`；corrected wrapper只替換 non-MOHI synthetic dry-run helper。

## Formal execution command

```text
python references/palmistry/line_segmentation_repeatability_runner_cv2_fixed.py \
  --model ~/palm-detector-study/palm-line-reader/models/student_fp32.onnx \
  --meta ~/palm-detector-study/palm-line-reader/models/model_meta.json \
  --zip /mnt/c/Users/user/Documents/X/MOHI_sample_10p_3s_5i.zip \
  --mediapipe-results /mnt/c/Users/user/Documents/X/MOHI_repeatability_results.json \
  --output ~/palm-detector-study/results/MOHI_line_segmentation_repeatability.json
```

## Observed execution accounting

All ten predeclared per-person sources completed：

```text
[01/10] P001/S1/01.jpg: complete
[02/10] P002/S1/01.jpg: complete
[03/10] P003/S1/01.jpg: complete
[04/10] P004/S1/01.jpg: complete
[05/10] P005/S1/01.jpg: complete
[06/10] P006/S1/01.jpg: complete
[07/10] P007/S1/01.jpg: complete
[08/10] P008/S1/01.jpg: complete
[09/10] P009/S1/01.jpg: complete
[10/10] P010/S1/01.jpg: complete
```

Final accounting：

```json
{
  "selected": 10,
  "completed": 10,
  "stop": false
}
```

Output artifact：

```text
/home/user/palm-detector-study/results/MOHI_line_segmentation_repeatability.json
```

每張 source 執行一個 baseline + 五個 frozen perturbations：

```text
baseline
rotate +5°
rotate -5°
scale 0.90×
scale 1.10×
center crop 3%
```

因此 completed execution 對應：

```text
10 source images × 6 conditions = 60 ONNX inference executions
```

## Current evidence boundary

At this point established：

- all 10 predeclared sources completed；
- no execution stop rule triggered；
- corrected runner produced the planned raw evidence JSON；
- the first result-inspection stage may now begin using the predeclared aggregation order。

Not yet interpreted in this record：

- per-class Dice / IoU；
- rotation vs scale/crop sensitivity；
- appearance/disappearance transitions；
- connected-component fragmentation；
- foreground-union vs class-specific repeatability；
- per-person instability heterogeneity。

Those values must be inspected from the generated artifact without changing the frozen crop, perturbation, threshold, class-order, or metric contracts。

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
