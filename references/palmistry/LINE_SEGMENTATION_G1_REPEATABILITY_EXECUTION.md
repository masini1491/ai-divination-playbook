# Palm Line Segmentation G1 Repeatability Execution

Status: **REFERENCE-ONLY / BOUNDED EXECUTION COMPLETE / RESULT INTERPRETATION PENDING**

本文件記錄 `LINE_SEGMENTATION_G1_REPEATABILITY_PLAN.md` 第一輪正式 MOHI G1 repeatability qualification execution accounting。此處只確認預先宣告的 `C_G1_M0` baseline 與五個 frozen perturbations 全部完成，不提前解讀 repeatability outcome。

## Frozen condition

```text
adapter = C_G1_M0
geometry = G1_reconstructed_upstream_like
horizontal_mirror = false
```

Perturbation family：

```text
baseline
rotate +5°
rotate -5°
scale 0.90×
scale 1.10×
center crop 3%
```

## Formal execution command

```text
mkdir -p ~/palm-detector-study/results

python references/palmistry/line_segmentation_g1_repeatability_runner.py \
  --model ~/palm-detector-study/palm-line-reader/models/student_fp32.onnx \
  --meta ~/palm-detector-study/palm-line-reader/models/model_meta.json \
  --zip /mnt/c/Users/user/Documents/X/MOHI_sample_10p_3s_5i.zip \
  --mediapipe-results /mnt/c/Users/user/Documents/X/MOHI_repeatability_results.json \
  --output ~/palm-detector-study/results/MOHI_line_segmentation_g1_repeatability.json
```

## Observed execution accounting

All ten frozen source images completed baseline + five perturbations：

```text
[01/10] P001/S1/01.jpg: baseline + 5 perturbations complete
[02/10] P002/S1/01.jpg: baseline + 5 perturbations complete
[03/10] P003/S1/01.jpg: baseline + 5 perturbations complete
[04/10] P004/S1/01.jpg: baseline + 5 perturbations complete
[05/10] P005/S1/01.jpg: baseline + 5 perturbations complete
[06/10] P006/S1/01.jpg: baseline + 5 perturbations complete
[07/10] P007/S1/01.jpg: baseline + 5 perturbations complete
[08/10] P008/S1/01.jpg: baseline + 5 perturbations complete
[09/10] P009/S1/01.jpg: baseline + 5 perturbations complete
[10/10] P010/S1/01.jpg: baseline + 5 perturbations complete
```

Final accounting：

```json
{
  "selected_sources": 10,
  "conditions_per_source": 6,
  "completed_inferences": 60,
  "stop": false
}
```

Output artifact：

```text
/home/user/palm-detector-study/results/MOHI_line_segmentation_g1_repeatability.json
```

## Current evidence boundary

At this stage established：

- all 10 frozen source images completed；
- all six frozen conditions per source completed；
- total ONNX inference count = 60；
- no execution stop rule triggered；
- the raw G1 repeatability JSON was written successfully；
- result inspection may now begin following the frozen directional questions and aggregation order。

Not yet interpreted in this record：

- baseline/variant class-presence retention；
- all-three-class retention；
- per-class Dice / IoU；
- foreground-union Dice / IoU；
- appearance/disappearance transitions；
- fragmentation / component changes；
- P001 / P009 perturbation stability；
- whether the 10/10 G1 baseline activation is robust or brittle。

No anatomical truth, Palmistry interpretation validity, production threshold or Chinese line-name equivalence is established。

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
