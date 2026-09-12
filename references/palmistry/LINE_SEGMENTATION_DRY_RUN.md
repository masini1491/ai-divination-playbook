# Palm Line Segmentation Dry Run

Status: **REFERENCE-ONLY / PRE-MOHI DRY RUN PASS**

本文件記錄 `LINE_SEGMENTATION_REPEATABILITY_PLAN.md` 在任何 MOHI segmentation inference 前的最後一層 implementation dry-run evidence。

## Executed repository revision

```text
14c6e96775b0314261b6e775d584c989eab4dd8f
```

## Syntax validation

Command：

```text
python -m py_compile \
  references/palmistry/line_segmentation_repeatability_runner_cv2_fixed.py
```

Observed：無輸出，syntax compile PASS。

## Non-MOHI dry run

Command：

```text
python references/palmistry/line_segmentation_repeatability_runner_cv2_fixed.py \
  --model ~/palm-detector-study/palm-line-reader/models/student_fp32.onnx \
  --meta ~/palm-detector-study/palm-line-reader/models/model_meta.json \
  --dry-run
```

Observed output：

```json
{
  "mode": "NON-MOHI DRY RUN",
  "baseline_shape": [384, 384],
  "baseline_values_subset": [0],
  "finite_logit_summary": true,
  "variants": {
    "rotate_p5": {
      "matrix_shape": [2, 3],
      "mapped_shape": [384, 384],
      "mapped_values_subset": [0]
    },
    "rotate_m5": {
      "matrix_shape": [2, 3],
      "mapped_shape": [384, 384],
      "mapped_values_subset": [0]
    },
    "scale_090": {
      "matrix_shape": [2, 3],
      "mapped_shape": [384, 384],
      "mapped_values_subset": [0]
    },
    "scale_110": {
      "matrix_shape": [2, 3],
      "mapped_shape": [384, 384],
      "mapped_values_subset": [0]
    },
    "center_crop_3pct": {
      "matrix_shape": [2, 3],
      "mapped_shape": [384, 384],
      "mapped_values_subset": [0]
    }
  },
  "schema": "PASS"
}
```

## Interpretation boundary

`baseline_values_subset=[0]` 與各 transform 的 `mapped_values_subset=[0]` 不代表 model 在 MOHI 上只會輸出 background，也不構成 model failure。Synthetic fixture 的用途只有：

- 驗證 model session / preprocessing path 可執行；
- 驗證 transform matrix shape；
- 驗證 inverse-mapped mask 回到 baseline crop frame；
- 驗證 mask class-index schema 可序列化；
- 驗證 dry-run execution 不需要修改 frozen protocol。

Synthetic fixture 並非真實 palm-line accuracy test。

## First dry-run diagnostic

第一次 non-MOHI dry run 在 synthetic fixture generation 階段觸發：

```text
AttributeError: module 'cv2' has no attribute 'arc'
```

此錯誤發生在任何 MOHI inference 前，且不涉及 model/runtime failure。修正版 wrapper：

```text
references/palmistry/line_segmentation_repeatability_runner_cv2_fixed.py
```

只把 synthetic fixture 的不存在 `cv2.arc` primitive 改為 OpenCV Python 支援的 `cv2.ellipse(..., startAngle, endAngle, ...)` arc drawing；full MOHI execution path 仍沿用 frozen base runner，不改 study protocol、crop、transform、model preprocessing、class mapping 或 metrics。

## Gate conclusion

目前已閉合：

```text
runtime/model artifact gate = PASS
syntax gate                 = PASS
non-MOHI runner dry run     = PASS
implementation gate         = CLOSED
```

下一個允許動作是執行 frozen 10-image MOHI segmentation-repeatability study：

```text
10 baseline crops × (baseline + 5 perturbations) = 60 ONNX inference executions
```

結果 inspection 前不得修改 crop margin、transform set、model variant、normalization、class ordering、threshold 或 morphology。

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
