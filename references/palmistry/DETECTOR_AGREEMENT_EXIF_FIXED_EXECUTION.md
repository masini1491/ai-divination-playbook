# Detector Agreement EXIF-Fixed Execution

Status: **REFERENCE-ONLY / CORRECTED EXECUTION COMPLETE / RESULT INTERPRETATION PENDING**

本文件記錄第一次 EXIF-orientation frame mismatch 被確認後，使用修正版 runner 完成的 MOHI detector-agreement execution accounting。

## Why this rerun exists

第一次 detector-agreement execution 使用 `cv2.IMREAD_COLOR`，而 historical MediaPipe evidence 使用 `cv2.IMREAD_UNCHANGED`。MOHI JPEG 的 EXIF orientation 使兩條 execution path 對同一 source bytes 解出不同 pixel frame：

```text
MediaPipe / IMREAD_UNCHANGED: [2448, 3264]
RTMPose first run / IMREAD_COLOR: [3264, 2448]
```

因此第一次 run 的 cross-detector agreement metrics 不可解讀；其 execution completion 與 byte-identical duplicate determinism evidence 可保留，但 raw/canonical disagreement values 不作研究結論。

修正版 runner：

```text
references/palmistry/detector_agreement_runner_exif_fixed.py
```

使用：

```text
cv2.IMREAD_COLOR | cv2.IMREAD_IGNORE_ORIENTATION
```

並對每張 source image fail closed 驗證：

```text
decoded [h,w] == frozen MediaPipe evidence rec["raw"]
```

任何 frame mismatch 都會被標記 `raw_frame_mismatch` 並使 execution stop before interpretation。

## Corrected execution command

```text
python references/palmistry/detector_agreement_runner_exif_fixed.py \
  --checkpoint ~/palm-detector-study/models/rtmpose-m-hand5.pth \
  --zip /mnt/c/Users/user/Documents/X/MOHI_sample_10p_3s_5i.zip \
  --mediapipe-results /mnt/c/Users/user/Documents/X/MOHI_repeatability_results.json \
  --output ~/palm-detector-study/results/MOHI_detector_agreement_exif_fixed.json
```

## Observed execution accounting

All 150 entries completed with `usable` status under the corrected raw-image frame guard.

Final runner summary:

```json
{
  "total": 150,
  "usable": 150,
  "primary_unique": 148,
  "stop": false
}
```

Output artifact:

```text
/home/user/palm-detector-study/results/MOHI_detector_agreement_exif_fixed.json
```

Because the corrected runner only reaches `usable` after confirming the decoded frame equals each image's frozen MediaPipe `raw` frame, 150/150 usable also establishes that no raw-frame mismatch was encountered in this corrected execution.

## Current evidence boundary

Established at this point:

- corrected frame convention used for RTMPose execution;
- 150 / 150 source entries decoded and passed raw-frame equality + RTMPose geometry usability;
- deterministic primary analysis unit remained 148 unique source-byte representatives;
- no execution stop rule was triggered;
- corrected raw evidence artifact was successfully written.

Not yet established in this record:

- pooled detector-agreement magnitude;
- per-keypoint disagreement pattern;
- L0/L5/L17 relative agreement;
- canonical-vs-raw disagreement comparison;
- RTMPose score/disagreement relationship;
- person/session heterogeneity interpretation.

Those values must be inspected from the corrected artifact only. Values from the first EXIF-mismatched run remain invalid for detector-agreement interpretation.

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
