# Palm Line Segmentation Adapter / Domain Diagnosis Execution

Status: **REFERENCE-ONLY / BOUNDED EXECUTION COMPLETE / RESULT INTERPRETATION PENDING**

本文件記錄 `LINE_SEGMENTATION_ADAPTER_DOMAIN_DIAGNOSIS_PLAN.md` 第一輪正式 MOHI adapter/domain diagnosis execution accounting。此處只確認預先宣告的四個 adapter 都完成，不提前解讀哪個 adapter 較好。

## Preconditions

正式 MOHI execution 前已完成：

- `palm-lines` runtime/model lock validated；
- FP32 ONNX / metadata SHA256 pinned；
- CPU-only ONNX Runtime session validated；
- adapter diagnosis plan predeclared；
- four adapter definitions frozen；
- non-MOHI adapter diagnosis dry run `schema = PASS`。

## Formal execution command

```text
python references/palmistry/line_segmentation_adapter_diagnosis_runner.py \
  --model ~/palm-detector-study/palm-line-reader/models/student_fp32.onnx \
  --meta ~/palm-detector-study/palm-line-reader/models/model_meta.json \
  --zip /mnt/c/Users/user/Documents/X/MOHI_sample_10p_3s_5i.zip \
  --mediapipe-results /mnt/c/Users/user/Documents/X/MOHI_repeatability_results.json \
  --output ~/palm-detector-study/results/MOHI_line_segmentation_adapter_diagnosis.json
```

## Observed execution accounting

All ten frozen source images completed all four adapters：

```text
[01/10] P001/S1/01.jpg: A/B/C/D complete
[02/10] P002/S1/01.jpg: A/B/C/D complete
[03/10] P003/S1/01.jpg: A/B/C/D complete
[04/10] P004/S1/01.jpg: A/B/C/D complete
[05/10] P005/S1/01.jpg: A/B/C/D complete
[06/10] P006/S1/01.jpg: A/B/C/D complete
[07/10] P007/S1/01.jpg: A/B/C/D complete
[08/10] P008/S1/01.jpg: A/B/C/D complete
[09/10] P009/S1/01.jpg: A/B/C/D complete
[10/10] P010/S1/01.jpg: A/B/C/D complete
```

Final accounting：

```json
{
  "selected_sources": 10,
  "adapters_per_source": 4,
  "completed_inferences": 40,
  "stop": false
}
```

Output artifact：

```text
/home/user/palm-detector-study/results/MOHI_line_segmentation_adapter_diagnosis.json
```

## Frozen adapter identities

```text
A_G0_M0 = first-study geometry / no mirror
B_G0_M1 = first-study geometry / horizontal mirror
C_G1_M0 = reconstructed-upstream-like geometry / no mirror
D_G1_M1 = reconstructed-upstream-like geometry / horizontal mirror
```

Therefore this completed execution corresponds to：

```text
10 source images × 4 adapters = 40 ONNX inference executions
```

## Current evidence boundary

At this stage established：

- all 10 source images completed all four predeclared adapters；
- no execution stop rule triggered；
- the raw diagnosis JSON was written successfully；
- result inspection may now begin following the frozen directional questions and aggregation order。

Not yet interpreted in this record：

- class presence count differences between adapters；
- foreground occupancy differences；
- fragmentation / connected-component differences；
- geometry effect G0 vs G1；
- mirror effect M0 vs M1；
- geometry × mirror interaction；
- P001 / P009 observability under alternative adapters。

Higher predicted presence must not be treated as higher segmentation accuracy because this study has no anatomical ground-truth line masks。

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
