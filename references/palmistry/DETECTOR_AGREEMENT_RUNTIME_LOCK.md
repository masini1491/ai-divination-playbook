# Palm Detector Agreement Runtime Lock

Status: **REFERENCE-ONLY / PRE-RUN RUNTIME ARTIFACT LOCK CLOSED / READY FOR FIRST MOHI EXECUTION**

本文件是 `DETECTOR_AGREEMENT_PLAN.md` 的 execution-side runtime identity record。

它不修改已凍結的 detector-agreement protocol，也不代表 MOHI inference 已執行。

## Purpose

在任何 MOHI RTMPose inference 前，把第二 detector 的 software / model identity 從 upstream version ranges 收斂成 exact runtime，並 durable-record 實際成功安裝、checkpoint byte identity 與 frozen-config model construction。

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
OpenCV package: 4.10.0.84
cv2.__version__: 4.10.0
PyTorch: 1.13.1
TorchVision: 0.14.1
MMCV: 2.0.0
MMDetection: 3.2.0
MMEngine: 0.10.4
MMPose: 1.3.2
chumpy: 0.70
setuptools: 80.9.0
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
import pkg_resources = PASS under setuptools 80.9.0
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

The first MMPose API smoke-test import then exposed a packaging compatibility issue:

```text
ModuleNotFoundError: No module named 'pkg_resources'
```

The environment had `setuptools 82.0.1`, while this MMPose/MMEngine path still imports `pkg_resources`. Before any MOHI inference or detector-agreement result inspection, setuptools was pinned to:

```text
setuptools = 80.9.0
```

After that pin:

```text
import pkg_resources = PASS
python -m pip check = No broken requirements found
```

The deprecation warning for `pkg_resources` is retained as runtime evidence; it does not invalidate this pinned one-time research environment.

These are pre-result runtime corrections, not post-hoc detector tuning.

## Model config identity

Frozen config:

```text
configs/hand_2d_keypoint/rtmpose/hand5/
rtmpose-m_8xb256-210e_hand5-256x256.py
```

Installed MMPose config resolved at runtime as:

```text
/home/user/miniconda3/envs/palm-detector/lib/python3.9/site-packages/
mmpose/.mim/configs/hand_2d_keypoint/rtmpose/hand5/
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

### Frozen-config model-construction smoke test

Before any MOHI image was supplied, the installed MMPose copy of the frozen config was resolved and loaded with:

```text
from mmpose.apis import init_model
init_model(config, checkpoint, device="cpu")
```

Observed:

```text
checkpoint exists: True
Loads checkpoint by local backend from pinned local path
model type: TopdownPoseEstimator
device: cpu
MODEL LOAD: PASS
```

This closes the previously outstanding model-construction + checkpoint weight-load gate without changing the config, checkpoint, input size, detector design, or geometry adapter.

No MOHI RTMPose inference had been executed when this gate was closed.

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
setuptools = VALIDATED / PINNED
chumpy = VALIDATED
MKL / Intel OpenMP = VALIDATED
CPU backend = VALIDATED
pip dependency consistency = VALIDATED
checkpoint official filename / source = LOCKED
checkpoint full SHA256 = VALIDATED
checkpoint torch deserialization = VALIDATED
frozen-config MMPose model construction + weight load = VALIDATED
runtime artifact lock = CLOSED
MOHI RTMPose inference = NOT RUN
```

The pre-run runtime artifact gate is now closed. The detector-agreement study may proceed to its first MOHI execution only under the already frozen protocol and this exact runtime identity.

## Next allowed action

The next execution step may construct the detector-agreement runner and execute the frozen MOHI protocol, subject to all existing plan invariants:

1. verify the existing MOHI source package / manifest identities before inference;
2. use the frozen full-image top-down bbox adapter only;
3. retain raw-image mapped 21-keypoint coordinates and scores;
4. perform 150-entry execution accounting;
5. preserve deterministic duplicate handling and the 148 unique-byte primary analysis unit;
6. do not introduce post-hoc score thresholds, crops, anchor changes, or hard-example exclusion.

Any runner dry-run that uses a non-MOHI synthetic or disposable image remains permissible, but no additional runtime qualification gate is required before the first MOHI inference as long as this exact lock is maintained.

## Stop rules

Stop before or during MOHI inference if any of the following occurs:

- actual runtime identity drifts from the versions recorded above;
- frozen config no longer resolves to the validated artifact;
- checkpoint bytes differ from the full SHA256 above;
- MMPose model construction / weight loading no longer reproduces the validated smoke test;
- successful execution requires changing model config or geometry adapter;
- CPU execution requires a different checkpoint or model definition;
- full-image raw-coordinate mapping cannot be preserved.

Any required runtime change must be recorded **before** viewing MOHI detector-agreement results and requires an explicit runtime-lock revision rather than silent substitution.

## Evidence boundary

This record now establishes:

- successful exact runtime installation and import validation;
- binary-extension loading through `mmcv.ops`;
- a clean pip dependency check;
- the required setuptools compatibility pin;
- official checkpoint acquisition;
- full checkpoint SHA256;
- checkpoint deserialization under the pinned PyTorch runtime;
- frozen-config MMPose model construction and checkpoint weight loading on CPU.

It does not establish:

- RTMPose compatibility with the MOHI image distribution;
- usable 21-keypoint geometry on MOHI;
- detector-to-detector agreement results;
- any production threshold or biometric claim.

The runtime artifact gate is closed, but the empirical detector-agreement study itself remains unexecuted at this record point.
