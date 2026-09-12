# Palm Detector Agreement Non-MOHI Dry Run

Status: **REFERENCE-ONLY / PRE-MOHI DRY RUN PASS**

本文件記錄 `detector_agreement_runner.py` 在任何 MOHI RTMPose inference 前的 synthetic / non-MOHI execution evidence。

## Purpose

這個 dry run 只驗證 runner 是否能在已鎖定 runtime 下：

- 載入 frozen RTMPose Hand5 config；
- 載入 pinned checkpoint；
- 以 CPU 執行 `inference_topdown()`；
- 產生 21 個 2D keypoints 與 21 個 keypoint scores；
- 通過 finite-value 與 schema checks。

它不使用 MOHI source image，也不產生 detector-agreement research result。

## Executed repository revision

```text
masini1491/ai-divination-playbook
main HEAD:
e920fc9be8ffe38d1b20c1fcfe2b2ca631024503
```

Local syntax validation:

```text
python -m py_compile references/palmistry/detector_agreement_runner.py
PASS / no output
```

## Command

```text
python references/palmistry/detector_agreement_runner.py \
  --checkpoint ~/palm-detector-study/models/rtmpose-m-hand5.pth \
  --dry-run
```

## Observed result

The pinned checkpoint loaded successfully through the local backend.

Runner output:

```json
{
  "mode": "NON-MOHI DRY RUN",
  "keypoints_shape": [21, 2],
  "scores_shape": [21],
  "finite_keypoints": true,
  "finite_scores": true,
  "score_mean": 0.09370951567377363,
  "schema": "PASS"
}
```

The `pkg_resources` deprecation warning remains an expected legacy-runtime warning under the already pinned `setuptools 80.9.0`; it did not prevent model loading or inference.

## Interpretation boundary

This dry run establishes only that the runner's RTMPose execution path and output schema are operational under the locked runtime.

It does **not** establish:

- MOHI domain compatibility for RTMPose;
- usable geometry on all 150 MOHI entries;
- detector-to-detector agreement magnitude;
- score acceptance thresholds;
- production Palmistry suitability.

No MOHI RTMPose result had been inspected when this record was created.

## Next allowed action

The runner may now execute the frozen 150-entry MOHI detector-agreement study, provided it first passes its built-in source ZIP / manifest / MediaPipe evidence / checkpoint / runtime integrity checks and preserves all predeclared stop rules.
