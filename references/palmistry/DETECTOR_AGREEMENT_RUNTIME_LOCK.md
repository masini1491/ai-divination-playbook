# Palm Detector Agreement Runtime Lock

Status: **REFERENCE-ONLY / PRE-RUN TARGET LOCK / CHECKPOINT SHA256 BLOCKED**

本文件是 `DETECTOR_AGREEMENT_PLAN.md` 的 execution-side runtime identity record。

它不修改已凍結的 detector-agreement protocol，也不代表 inference 已執行。

## Purpose

在任何 MOHI RTMPose inference 前，把第二 detector 的 software / model identity 從 upstream version ranges 收斂成 exact target runtime，並把尚未閉合的 artifact identity 明確留下。

本文件區分：

```text
selected exact target
≠ installed successfully
≠ execution validated
≠ result produced
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

Selected:

```text
mmcv == 2.0.0
tag commit:
1db3967e860569c1501af4bff6c0964dec402289
```

MMCV v2.0.0 release notes state support for PyTorch versions >=1.8 and Python >=3.7.

### MMDetection

Selected:

```text
mmdet == 3.2.0
tag commit:
fe3f809a0a514189baf889aa358c498d51ee36cd
```

Its `requirements/mminstall.txt` constrains:

```text
mmcv >= 2.0.0rc4, < 2.2.0
mmengine >= 0.7.1, < 1.0.0
```

### MMEngine

Selected:

```text
mmengine == 0.10.4
tag commit:
66fb81f7b392b2cd304fc1979d8af3cc71a011f5
```

MMPose v1.3.2 runtime guard accepts:

```text
mmengine >= 0.6.0, <= 1.0.0
mmcv >= 2.0.0rc4, <= 3.0.0
```

Therefore the selected MMEngine / MMCV pair sits inside both MMPose and MMDetection published compatibility ranges.

## Frozen target runtime

The first execution attempt, when a compatible environment is available, must use exactly:

```text
OS / arch: Linux x86_64
Python: 3.9.18
PyTorch: 1.13.1
TorchVision: 0.14.1
MMCV: 2.0.0
MMDetection: 3.2.0
MMEngine: 0.10.4
MMPose: 1.3.2
execution device: CPU
backend: PyTorch eager inference via MMPose API
```

Rationale for CPU-first:

- removes CUDA / cuDNN / GPU-driver variation from the first bounded comparison;
- the scientific question is geometry agreement, not throughput;
- MMPose official API supports CPU inference;
- a later GPU execution would be a separate runtime identity and must not silently replace this baseline.

No package may float to a newer compatible version during the first study.

## Current execution-environment reality

The current execution container reports:

```text
Python 3.13.5
```

No Python 3.9 interpreter, Conda, or Micromamba runtime was available in the inspected environment.

Therefore the frozen target runtime above is currently **selected but not installed / runtime-validated here**.

This is an environment capability gap, not evidence that the selected upstream versions are incompatible.

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

The COCO-WholeBody hand meta definition confirms:

```text
0  = wrist
5  = forefinger1
17 = pinky_finger1
```

## Official checkpoint identity

Frozen official checkpoint filename:

```text
rtmpose-m_simcc-hand5_pt-aic-coco_210e-256x256-74fb594_20230320.pth
```

Official MMPose v1.3.2 documentation and model metadata point to the OpenMMLab download artifact with that exact filename.

Important:

```text
74fb594
```

is part of the upstream filename and must **not** be treated as the full SHA256 value.

### Current hash state

```text
checkpoint full SHA256 = NOT YET ACQUIRED
```

A direct binary acquisition attempt from `download.openmmlab.com` in the current runtime failed at DNS / external-binary access level before any bytes were obtained.

This is classified as:

```text
ACQUISITION CAPABILITY GATE
≠ upstream source failure
≠ checkpoint missing
≠ checksum mismatch
```

The official GitHub-hosted MMPose documentation still identifies the checkpoint URL and filename, so source identity remains established while byte identity remains unresolved.

## Gate state

The detector-agreement execution gate is therefore:

```text
protocol predeclared = YES
MMPose release identity = LOCKED
MMCV target = LOCKED
MMDetection target = LOCKED
MMEngine target = LOCKED
Python target = LOCKED
PyTorch target = LOCKED
TorchVision target = LOCKED
CPU backend = LOCKED
checkpoint filename / official URL = LOCKED
checkpoint full SHA256 = BLOCKED
exact target runtime installed = NOT YET VALIDATED
```

Execution remains blocked.

## Required next action before inference

On a runtime that can reproduce the frozen target environment:

1. create Python 3.9.18 environment;
2. install the exact versions in this record;
3. record `python --version` and package versions from the actual environment;
4. obtain the official RTMPose Hand5 checkpoint from the upstream URL;
5. compute full SHA256 locally;
6. compare filename / source against this record;
7. durable-record the hash and successful model-load smoke test;
8. only then execute any MOHI image.

The smoke test may verify model construction and checkpoint loading, but must not use a MOHI source image before the hash is recorded.

## Stop rules

Stop before MOHI inference if any of the following occurs:

- exact target package versions cannot coexist;
- a package must be upgraded / downgraded outside this frozen set;
- official checkpoint source resolves to a different artifact identity;
- checkpoint bytes cannot be fully acquired;
- full SHA256 cannot be computed;
- checkpoint fails clean load under the frozen config;
- CPU execution requires changing model config or geometry adapter.

Any required runtime change must be recorded **before** viewing MOHI detector-agreement results and requires a new explicit runtime-lock revision rather than silent substitution.

## Evidence boundary

This record currently establishes only a reproducible **target runtime specification** and the exact remaining blockers.

It does not establish:

- successful installation;
- checkpoint byte identity;
- successful model loading;
- RTMPose compatibility with MOHI;
- detector-to-detector agreement results.

Until checkpoint SHA256 and actual environment validation are closed:

```text
NO MOHI RTMPOSE INFERENCE
NO DETECTOR-AGREEMENT RESULT INSPECTION
```
