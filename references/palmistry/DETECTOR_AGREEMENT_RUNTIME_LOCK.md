# Palm Detector Agreement Runtime Lock

Status: **REFERENCE-ONLY / PRE-RUN RUNTIME + CHECKPOINT IDENTITY VALIDATED / MODEL-CONSTRUCTION SMOKE TEST PENDING**

本文件是 `DETECTOR_AGREEMENT_PLAN.md` 的 execution-side runtime identity record。

它不修改已凍結的 detector-agreement protocol，也不代表 MOHI inference 已執行。

## Purpose

在任何 MOHI RTMPose inference 前，把第二 detector 的 software / model identity 從 upstream version ranges 收斂成 exact runtime，並 durable-record 實際成功安裝與 checkpoint byte identity。

本文件區分：

```text
selected exact target
≠ installed successfully
≠ import/runtime validated
≠ checkpoint bytes validated
≠ model construction validated
≠ MOHI result produced
```

## Repository / release identities

### MMPose

```text
repository: open-mmlab/mmpose
release: v1.3.2
resolved commit:
5408bc76f5b848cf925a0d1857899011d8c5b497
```

MMPose v1.3.2 `setup.py` declares `python_requires >=3.7` and classifiers through Python 3.9.

### MMCV

```text
mmcv == 2.0.0
tag commit:
1db3967e860569c1501af4bff6c0964dec402289
```

### MMDetection

```text
mmdet == 3.2.0
tag commit:
fe3f809a0a514189baf889aa358c498d51ee36cd
```

Published compatibility constraint:

```text
mmcv >= 2.0.0rc4, < 2.2.0
mmengine >= 0.7.1, < 1.0.0
```

### MMEngine

```text
mmengine == 0.10.4
tag commit:
66fb81f7b392b2cd304fc1979d8af3cc71a011f5
```

MMPose v1.3.2 runtime guard accepts the selected MMCV / MMEngine pair.

## Actual validated execution runtime

Validated on the user-side Windows 11 WSL2 environment before any MOHI RTMPose inference:

```text
platform:
Linux-6.18.33.2-microsoft-standard-WSL2-x86_64-with-glibc2.35

Python: 3.9.18
NumPy: 1.26.4
OpenCV: 4.10.0
PyTorch: 1.13.1
TorchVision: 0.14.1
MMCV: 2.0.0
MMDetection: 3.2.0
MMEngine: 0.10.4
MMPose: 1.3.2
chumpy: 0.70
MKL: 2020.2
Intel OpenMP: 2023.0.0
execution device: CPU
CUDA available: False
backend: PyTorch eager inference via MMPose API
```

Validation observations:

```text
import torch = PASS
import torchvision = PASS
import mmcv = PASS
import mmengine = PASS
import mmdet = PASS
import mmpose = PASS
import mmcv.ops = PASS
NumPy -> torch.from_numpy bridge = PASS
python -m pip check = No broken requirements found
```

### Runtime-resolution record

The first install attempt exposed compatibility details that are now part of the reproducibility lock.

Initial Conda resolution installed:

```text
mkl = 2025.0.0
intel-openmp = 2025.0.0
```

Under PyTorch 1.13.1 this produced:

```text
libtorch_cpu.so: undefined symbol: iJIT_NotifyEvent
```

Before any MOHI result inspection, the runtime was corrected to:

```text
mkl = 2020.2
intel-openmp = 2023.0.0
```

and PyTorch import then passed.

A second compatibility issue appeared because pip had resolved:

```text
NumPy = 2.0.2
OpenCV = 5.0.0.93
```

The MMCV / PyTorch binary path warned that modules compiled against NumPy 1.x cannot safely run against NumPy 2.0.2. Before any MOHI result inspection, the environment was corrected and validated as:

```text
NumPy = 1.26.4
OpenCV = 4.10.0.84 package
cv2.__version__ = 4.10.0
```

`opencv-python` was installed with `--no-deps` after NumPy pinning so pip would not silently promote NumPy back to 2.x.

MMPose installation also required the legacy dependency:

```text
chumpy = 0.70
```

which was installed before MMPose using the current environment rather than an isolated legacy build path.

These are pre-result runtime corrections, not post-hoc detector tuning.

## Model config identity

Frozen config:

```text
configs/hand_2d_keypoint/rtmpose/hand5/
rtmpose-m_8xb256-210e_hand5-256x256.py
```

Key inspected properties:

```text
model = TopdownPoseEstimator
out_channels = 21
input_size = 256 × 256
flip_test = True
```

Training composition includes:

```text
COCO-WholeBody Hand
OneHand10K
FreiHand
RHD
Halpe Hand
```

The hand metainfo correspondence used by the frozen protocol is:

```text
0  = wrist
5  = forefinger1
17 = pinky_finger1
```

## Official checkpoint identity

Official checkpoint filename:

```text
rtmpose-m_simcc-hand5_pt-aic-coco_210e-256x256-74fb594_20230320.pth
```

User-side acquisition from the official OpenMMLab download endpoint completed successfully.

Observed file size:

```text
55,287,475 bytes
```

Full SHA256:

```text
b74fb5941684fe13c337b8d4fce644293e12903fed5407f8b27921f107dc6003
```

Important: the upstream filename fragment `74fb594` is not used as a substitute for the full digest above.

### Checkpoint deserialization smoke test

The pinned file was read locally with:

```text
torch.load(path, map_location="cpu")
```

Observed:

```text
checkpoint type: dict
top-level keys: ['meta', 'state_dict']
```

This establishes readable checkpoint serialization and byte identity under the pinned PyTorch runtime.

It does **not** yet establish that MMPose can construct the frozen RTMPose-Hand5 config and load the weights into the model without error.

## Current gate state

```text
protocol predeclared = YES
MMPose release identity = LOCKED
MMCV = VALIDATED
MMDetection = VALIDATED
MMEngine = VALIDATED
Python = VALIDATED
NumPy = VALIDATED
OpenCV = VALIDATED
PyTorch = VALIDATED
TorchVision = VALIDATED
MKL / Intel OpenMP = VALIDATED
CPU backend = VALIDATED
pip dependency consistency = VALIDATED
checkpoint official filename / source = LOCKED
checkpoint full SHA256 = VALIDATED
checkpoint torch deserialization = VALIDATED
frozen-config MMPose model construction + weight load = PENDING
MOHI RTMPose inference = NOT RUN
```

Execution remains fail-closed until the final model-construction smoke test passes.

## Final required action before MOHI inference

Using this same validated environment and exact checkpoint bytes:

1. resolve the installed MMPose copy of the frozen RTMPose-Hand5 config;
2. call MMPose model construction on CPU with that config and the pinned checkpoint;
3. confirm construction and weight loading complete without modifying config, model input size, crop rule, or checkpoint;
4. record the successful smoke test here;
5. only then permit runner execution against MOHI source images.

The final smoke test must not use a MOHI image.

## Stop rules

Stop before MOHI inference if any of the following occurs:

- frozen config cannot be resolved from the installed MMPose release;
- checkpoint fails MMPose model construction / weight loading;
- successful loading requires changing package versions outside this validated runtime;
- successful loading requires changing model config or geometry adapter;
- official checkpoint bytes differ from the full SHA256 above;
- CPU execution requires a different checkpoint or model definition.

Any required runtime change must be recorded **before** viewing MOHI detector-agreement results and requires an explicit runtime-lock revision rather than silent substitution.

## Evidence boundary

This record now establishes:

- successful exact runtime installation and import validation;
- binary-extension loading through `mmcv.ops`;
- a clean pip dependency check;
- official checkpoint acquisition;
- full checkpoint SHA256;
- checkpoint deserialization under the pinned PyTorch runtime.

It does not yet establish:

- frozen-config MMPose model-construction success;
- RTMPose compatibility with MOHI;
- detector-to-detector agreement results.

Until the final frozen-config model-construction smoke test is recorded:

```text
NO MOHI RTMPOSE INFERENCE
NO DETECTOR-AGREEMENT RESULT INSPECTION
```
