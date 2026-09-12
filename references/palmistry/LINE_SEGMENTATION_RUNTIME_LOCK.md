# Palm Line Segmentation Runtime Lock

Status: **REFERENCE-ONLY / PRE-INFERENCE RUNTIME VALIDATED / GATE CLOSED**

本文件在任何 MOHI line-segmentation inference 前，固定 `LINE_SEGMENTATION_REPEATABILITY_PLAN.md` 第一輪 execution 所使用的 runtime 與 upstream model artifact identity。

## Environment boundary

使用獨立 conda environment，避免污染既有 detector-agreement runtime：

```text
conda env: palm-lines
platform: Linux-6.18.33.2-microsoft-standard-WSL2-x86_64-with-glibc2.35
Python: 3.11.16
python path: /home/user/miniconda3/envs/palm-lines/bin/python
```

已實際安裝並驗證：

```text
onnxruntime    1.29.0
numpy          1.26.4
opencv-python  4.10.0.84
cv2 runtime    4.10.0
```

本次安裝同時解析：

```text
flatbuffers 25.12.19
protobuf    7.36.1
packaging   26.3
```

`python -m pip check` 實際結果：

```text
No broken requirements found.
```

## Execution provider validation

ONNX Runtime global available providers：

```text
['AzureExecutionProvider', 'CPUExecutionProvider']
```

本研究明確建立：

```text
InferenceSession(..., providers=['CPUExecutionProvider'])
```

實際 session providers：

```text
['CPUExecutionProvider']
```

因此第一輪 study 的 execution backend 固定為 CPU；Azure provider 雖存在於 runtime available-provider list，但未被 session 使用。

## Upstream repository identity

```text
repository: samuelwbarber/palm-line-reader
reviewed / execution revision:
bc48939f4deee6d8ff842bfde499396dab9c4830
```

Local checkout 已實際解析到同一 immutable commit。

## Frozen FP32 model artifact

第一輪 segmentation-repeatability study 只使用 upstream metadata 所描述的 highest-fidelity / verification baseline：

```text
models/student_fp32.onnx
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

## Model-load contract validation

Pinned `student_fp32.onnx` 已成功建立 CPU `InferenceSession`。

實際 observed contract：

```text
input : input  [1,3,512,512] tensor(float)
output: logits [1,4,512,512] tensor(float)
```

與 frozen metadata 完全一致。

## Synthetic / non-MOHI inference smoke test

在任何 MOHI line-segmentation inference 前，已使用 synthetic all-zero float32 tensor：

```text
input shape  = (1,3,512,512)
output shape = (1,4,512,512)
output dtype = float32
finite       = True
min logit    = -9.919937133789062
max logit    =  7.99305534362793
```

結果：

```text
MODEL SMOKE TEST: PASS
```

這只證明 runtime / model graph / tensor contract 可執行，不建立 MOHI segmentation evidence，也不建立 model accuracy。

## Runtime gate conclusion

下列 pre-inference gates 已全部實際閉合：

1. exact runtime package versions recorded；
2. `pip check` clean；
3. CPU provider available and CPU-only session used；
4. upstream repository revision pinned；
5. FP32 ONNX full SHA256 matched；
6. metadata full SHA256 matched；
7. input/output names、shapes、dtypes matched；
8. synthetic inference produced finite `[1,4,512,512]` logits。

因此 runtime/model artifact gate 現為：

```text
CLOSED / READY FOR NON-MOHI RUNNER DRY RUN
```

仍不得把 synthetic smoke test 視為 MOHI result。MOHI execution 必須等 study runner 本身通過 syntax/schema dry run 後才開始。

## Fail-closed conditions for later execution

後續 runner 每次 execution 仍需停止，如果：

- Python 不再是 3.11.16；
- exact package version drift；
- model / metadata SHA256 drift；
- CPU session 無法建立；
- input/output contract drift；
- MOHI raw frame 與 frozen MediaPipe evidence 不一致；
- 必須修改 ONNX graph 或 shipped preprocessing contract 才能執行。

不得為了讓結果看起來更穩定而在 outcome inspection 後更換 FP16/INT8、resize rule、normalization、class ordering、crop margin 或 output interpretation。

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
