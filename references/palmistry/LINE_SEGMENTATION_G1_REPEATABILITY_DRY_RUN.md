# Palm Line Segmentation G1 Repeatability Dry Run

Status: **REFERENCE-ONLY / NON-MOHI DRY RUN PASS / READY FOR BOUNDED EXECUTION**

本文件記錄 `LINE_SEGMENTATION_G1_REPEATABILITY_PLAN.md` 與 `line_segmentation_g1_repeatability_runner.py` 在任何 G1 MOHI perturbation outcome inspection 前的 implementation dry run。

## Frozen condition

```text
adapter = C_G1_M0
geometry = G1_reconstructed_upstream_like
horizontal_mirror = false
```

Runtime/model lock沿用先前 validated environment；不引入 threshold、morphology cleanup、class remapping 或模型更換。

## Observed dry-run output

Baseline synthetic crop：

```text
crop_shape     = [530,403,3]
baseline_shape = [530,403]
baseline_values_subset = [0]
finite_logit_summary = true
```

五個 frozen perturbations 均完成：

```text
rotate_p5
rotate_m5
scale_090
scale_110
center_crop_3pct
```

Each variant observed：

```text
matrix_shape = [2,3]
variant_shape = [530,403,3]
mapped_shape = [530,403]
mapped_values_subset = [0]
```

Final result：

```text
mode = NON-MOHI G1 REPEATABILITY DRY RUN
adapter = C_G1_M0
schema = PASS
```

## Interpretation of synthetic all-background mask

`predicted_values_subset=[0]` on the synthetic fixture is not a model failure and is not substantive evidence about MOHI observability. The dry-run fixture is used only to validate：

- deterministic G1 rectangular crop path；
- model execution and finite logits；
- width/height-preserving perturbation transforms；
- exact 2×3 affine retention；
- inverse mapping back to the immutable rectangular baseline frame；
- output/schema compatibility。

No biological, anatomical or palmistry meaning is assigned to the synthetic output。

## Gate conclusion

The implementation gate is closed for the bounded G1 repeatability execution：

```text
10 frozen MOHI source images
× (1 baseline + 5 frozen perturbations)
= 60 ONNX inference executions
```

No G1 perturbation result has been inspected at this stage。

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
