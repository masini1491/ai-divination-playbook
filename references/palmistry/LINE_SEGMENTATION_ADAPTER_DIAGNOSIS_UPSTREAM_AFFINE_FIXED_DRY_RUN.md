# Palm Line Segmentation Adapter Diagnosis — Upstream Affine Fixed Dry Run

Status: **REFERENCE-ONLY / NON-MOHI DRY RUN PASS / READY FOR BOUNDED RE-EXECUTION**

本文件記錄 `line_segmentation_adapter_diagnosis_runner.py` 在 G1 affine implementation fidelity correction 後的 non-MOHI dry run。此 dry run 發生於 corrected-G1 substantive MOHI outcome inspection 前。

## Repository state used

```text
main = d922af98dcd438efc0724a4e8153afe8b738e671
```

## Validation command

```text
python -m py_compile \
  references/palmistry/line_segmentation_adapter_diagnosis_runner.py

python references/palmistry/line_segmentation_adapter_diagnosis_runner.py \
  --model ~/palm-detector-study/palm-line-reader/models/student_fp32.onnx \
  --meta ~/palm-detector-study/palm-line-reader/models/model_meta.json \
  --dry-run
```

`py_compile` completed without error.

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

Final dry-run status：

```text
mode = NON-MOHI ADAPTER DIAGNOSIS DRY RUN
schema = PASS
```

## Interpretation

The corrected affine implementation preserves the expected dry-run execution contract：

- A/B unchanged；
- C/D execute successfully under the corrected upstream-style one-pass affine crop；
- all logits summaries are finite；
- mask dimensions match crop dimensions；
- mirror flags remain frozen；
- synthetic all-background output remains acceptable for an implementation/schema fixture。

The fact that C/D dry-run dimensions remain `530×403` does not imply equivalence with the superseded implementation; pixel sampling and affine translation semantics changed even when integer output dimensions coincide。

## Gate conclusion

The corrected adapter diagnosis runner is ready for bounded MOHI re-execution using a **new output filename** so the legacy artifact remains intact：

```text
MOHI_line_segmentation_adapter_diagnosis_upstream_affine_fixed.json
```

No corrected-G1 MOHI result has been inspected at this stage。

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
