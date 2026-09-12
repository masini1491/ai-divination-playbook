# Palm Line Segmentation Adapter/Domain Diagnosis Dry Run

Status: **REFERENCE-ONLY / NON-MOHI DRY RUN PASS / READY FOR BOUNDED EXECUTION**

本文件記錄 `LINE_SEGMENTATION_ADAPTER_DOMAIN_DIAGNOSIS_PLAN.md` 與 `line_segmentation_adapter_diagnosis_runner.py` 在任何新 adapter MOHI outcome inspection 前的 implementation dry run。

## Runtime/model boundary

沿用已 validated 的 `palm-lines` runtime/model lock：

```text
Python        3.11.16
NumPy         1.26.4
OpenCV        4.10.0
ONNX Runtime  1.29.0
student_fp32.onnx SHA256
3c02b88b82e54889d0ab2bf2ba108aec554a1b50759f7c7aaa45f2f114ed24ff
model_meta.json SHA256
880b17a1f0ae8f0ad9c4061b0674e86381f50fadb242a662b44fdbaf4b919a98
CPUExecutionProvider session
```

## Dry-run command

```text
python references/palmistry/line_segmentation_adapter_diagnosis_runner.py \
  --model ~/palm-detector-study/palm-line-reader/models/student_fp32.onnx \
  --meta ~/palm-detector-study/palm-line-reader/models/model_meta.json \
  --dry-run
```

## Observed adapter outputs

```text
A_G0_M0
crop_shape = [430,430,3]
mask_shape = [430,430]
finite_logit_summary = true
predicted_values_subset = [0]
horizontal_mirror = false

B_G0_M1
crop_shape = [430,430,3]
mask_shape = [430,430]
finite_logit_summary = true
predicted_values_subset = [0]
horizontal_mirror = true

C_G1_M0
crop_shape = [530,403,3]
mask_shape = [530,403]
finite_logit_summary = true
predicted_values_subset = [0]
horizontal_mirror = false

D_G1_M1
crop_shape = [530,403,3]
mask_shape = [530,403]
finite_logit_summary = true
predicted_values_subset = [0]
horizontal_mirror = true
```

Final result：

```text
mode   = NON-MOHI ADAPTER DIAGNOSIS DRY RUN
schema = PASS
```

`predicted_values_subset=[0]` is not an error because this synthetic fixture tests adapter geometry, tensor/model execution, output shape and schema only; it does not require line-class detection on artificial imagery.

## Shell-copy note

After the successful JSON output, literal example text such as：

```text
"mode": "NON-MOHI ADAPTER DIAGNOSIS DRY RUN"
...
"schema": "PASS"
```

was pasted into the shell and produced `Command not found` messages. Those shell messages occurred **after** the runner had already exited successfully and are unrelated to the model, runtime, adapter implementation or research evidence.

## Gate conclusion

All four frozen adapters completed the non-MOHI implementation path with finite model output and valid schema. Therefore the implementation gate is closed for the bounded adapter/domain diagnosis execution：

```text
10 frozen MOHI source images × 4 predeclared adapters = 40 ONNX inference executions
```

No adapter outcome ranking has been inspected at this stage.

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
