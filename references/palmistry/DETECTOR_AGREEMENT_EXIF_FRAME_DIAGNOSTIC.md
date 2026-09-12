# Detector Agreement EXIF Frame Diagnostic

Status: **REFERENCE-ONLY / FIRST EXECUTION METRICS INVALID FOR INTERPRETATION / ROOT CAUSE IDENTIFIED**

本 note 記錄第一次 MOHI MediaPipe-vs-RTMPose detector-agreement execution 後觸發的 coordinate-frame sanity check。

## What remained valid from the first execution

第一次 150-entry execution 本身成功完成，且：

```text
total = 150
RTMPose usable = 150
primary unique-source representatives = 148
stop = false
```

兩組已知 byte-identical source duplicates 在 RTMPose output 上也完全 deterministic：

```text
P005/S1/01.jpg == P005/S3/02.jpg
keypoints exact equal = true
scores exact equal = true
max delta = 0

P001/S3/03.jpg == P001/S3/05.jpg
keypoints exact equal = true
scores exact equal = true
max delta = 0
```

因此 runtime execution、serialization 與 duplicate-consistency evidence 可保留。

## Sanity-check trigger

第一次 primary-148 summary 出現高度系統性的異常：

```text
raw 21-point mean delta ≈ 0.391
anchor mean delta ≈ 0.540
axis-angle delta mean ≈ 87.98°
```

person/session 的 axis-angle delta 亦持續接近 90°，不像一般 detector noise。

第一個 primary sample 更直接顯示 coordinate-frame contradiction：

```text
RTMPose runner raw_size [h,w] = [3264, 2448]
MediaPipe wrist x ≈ 3019
```

若 width 真為 2448，MediaPipe x=3019 不可能位於同一 raw-image frame。

因此第一次 agreement distributions 不得解讀為 detector disagreement。

## Root cause

舊 MOHI MediaPipe runner 使用：

```python
cv2.imread(path, cv2.IMREAD_UNCHANGED)
```

而第一版 detector-agreement runner 使用：

```python
cv2.imdecode(..., cv2.IMREAD_COLOR)
```

對同一 `P001/S1/01.jpg` 實測：

```text
MediaPipe recorded raw [h,w] = [2448, 3264]
IMREAD_UNCHANGED [h,w] = [2448, 3264]
IMREAD_COLOR [h,w] = [3264, 2448]
IMREAD_COLOR | IMREAD_IGNORE_ORIENTATION [h,w] = [2448, 3264]
```

所以 OpenCV default color decode 套用了 JPEG EXIF display orientation；historical MediaPipe evidence 則保留原始 pixel orientation。

D4 diagnostic 也顯示 identity transform 明顯較差，而 90-degree transform 可大幅降低 raw disagreement，與上述 orientation-frame mismatch 一致。

## Interpretation decision

第一次 detector-agreement JSON：

```text
MOHI_detector_agreement_raw.json
```

保留作 execution / diagnostic artifact，但其中 cross-detector agreement metrics：

```text
raw delta
anchor delta
axis angle delta
width / height relative difference
canonical delta
score-vs-disagreement relationship
```

全部標記為 **INVALID FOR INTERPRETATION**，因為兩 detector outputs 不在同一 raw-image coordinate frame。

不得把約 88° axis disagreement 或約 0.39 raw mean delta 寫成 detector-model finding。

## Corrected execution contract

修正版 execution 保持所有 frozen protocol / model / checkpoint / metrics 不變，只修正 raw image decode frame：

```python
cv2.IMREAD_COLOR | cv2.IMREAD_IGNORE_ORIENTATION
```

並新增 hard fail-closed guard：

```text
decoded [h,w]
must exactly equal
frozen MediaPipe rec["raw"]
```

若任何 image 不相等，該 execution 必須停止 interpretation。

修正版另用新 output file，不能覆寫第一次 diagnostic artifact。

## Evidence boundary

這是 implementation-coordinate correction，不是 outcome-driven detector tuning：

- 不改 RTMPose config；
- 不改 checkpoint；
- 不改 21-keypoint semantic mapping；
- 不改 full-image bbox adapter；
- 不改 canonical basis；
- 不改 score threshold；
- 不排除任何 image/person/session。

第一次 execution 的異常分布只被用來觸發 coordinate-frame integrity check；修正依據是直接觀察到的 decode dimensions 與 frozen MediaPipe raw-size evidence。

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
