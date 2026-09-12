# Palm Line Segmentation Runtime Lock

Status: **REFERENCE-ONLY / PRE-INFERENCE RUNTIME SELECTION / VALIDATION PENDING**

本文件在任何 MOHI line-segmentation inference 前，固定 `LINE_SEGMENTATION_REPEATABILITY_PLAN.md` 第一輪 execution 所使用的 runtime 與 upstream model artifact identity。

## Environment boundary

使用獨立 conda environment，避免污染既有 detector-agreement runtime：

```text
conda env: palm-lines
platform: Linux / WSL2 / x86_64
Python: 3.11.16
python path: /home/user/miniconda3/envs/palm-lines/bin/python
```

目前上述 Python environment 已實際建立；下列 Python packages 為 pre-inference **selected lock**，尚未宣稱已驗證：

```text
onnxruntime == 1.29.0
numpy       == 1.26.4
opencv-python == 4.10.0.84
```

選擇原則：

- CPU ONNX Runtime；不引入 GPU/CUDA execution provider；
- ONNX Runtime 1.29.0 有 CPython 3.11 / Linux x86-64 wheel；
- 不追使用剛發布的 1.30.0，降低本一次性 qualification runtime 的新版本變數；
- NumPy 1.26.4 / OpenCV 4.10.0.84 已在同一 WSL2 host 的另一 isolated research env 實際運作過，但本 `palm-lines` env 仍需獨立驗證，不能沿用另一 env 的 PASS。

## Upstream repository identity

```text
repository: samuelwbarber/palm-line-reader
reviewed / execution revision:
bc48939f4deee6d8ff842bfde499396dab9c4830
```

Local checkout 已解析到同一 immutable commit。

## Frozen FP32 model artifact

第一輪 segmentation-repeatability study 只使用 upstream metadata 所描述的 highest-fidelity / verification baseline：

```text
models/student_fp32.onnx
size: ~22 MB
SHA256:
3c02b88b82e54889d0ab2bf2ba108aec554a1b50759f7c7aaa45f2f114ed24ff
```

不在第一輪混入 FP16 / INT8，以免把 model precision variant 與 transform-repeatability 混成同一 uncertainty source。

## Frozen model metadata artifact

```text
models/model_meta.json
SHA256:
880b17a1f0ae8f0ad9c4061b0674e86381f50fadb242a662b44fdbaf4b919a98
```

Metadata contract：

```text
input name: input
input shape: [1,3,512,512]
layout: NCHW
input dtype: float32
color order: RGB
pixel scale: /255 → [0,1]
normalize mean: [0.485,0.456,0.406]
normalize std:  [0.229,0.224,0.225]
resize: plain bilinear to 512×512, no letterbox

output name: logits
output shape: [1,4,512,512]
classes:
0 background
1 heart_line
2 head_line
3 life_line
postprocess: argmax over class axis for class-index mask
```

這些 class names 保持 **tool-local Western labels**；不得自動映射至中國手相的天／人／地紋。

## Runtime gate to close before MOHI execution

必須先完成：

1. 安裝上述 exact package versions；
2. `python -m pip check` clean；
3. 記錄 exact observed package versions；
4. `onnxruntime.get_available_providers()` 確認 CPU path 可用；
5. 以 pinned `student_fp32.onnx` 建立 `InferenceSession`；
6. 驗證 input/output names、shapes、dtypes符合 frozen metadata；
7. synthetic/non-MOHI tensor smoke inference 成功產生 `[1,4,512,512]` finite logits；
8. 重算 ONNX / metadata SHA256，必須與本文件一致。

在以上全部 PASS 前：

```text
DO NOT RUN MOHI LINE-SEGMENTATION INFERENCE
```

## Fail-closed conditions

停止並先處理 runtime drift，如果：

- Python 不再是 3.11.16；
- selected package exact version 無法安裝；
- ORT model load 失敗；
- model input/output contract與 metadata 不一致；
- artifact SHA256 不一致；
- CPU provider 不可用；
- smoke inference 產生 non-finite output；
- 必須修改 ONNX graph 或 preprocessing contract 才能執行。

不得為了讓模型跑起來而在看到 MOHI outcome 後更換 FP16/INT8、resize rule、normalization、class ordering或 output interpretation。

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
