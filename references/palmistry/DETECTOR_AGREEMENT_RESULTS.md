# Palm Detector-to-Detector Agreement Results

Status: **REFERENCE-ONLY / BOUNDED EMPIRICAL RESULT / CORRECTED EXIF FRAME**

本文件記錄 MediaPipe 1.0.1 與 MMPose v1.3.2 / RTMPose-m Hand5 在既有 MOHI bounded sample 上的第一輪 detector-to-detector geometry agreement 結果。

本研究只量化 **observation implementation uncertainty**。兩個 detector 都不是 ground truth，本結果也不是 biometric identity evidence、production admission threshold 或一般 smartphone 場景的 universal estimate。

## Corrected execution provenance

第一次 detector-agreement execution 因 JPEG EXIF orientation decode 差異，使 MediaPipe 與 RTMPose 落在不同 raw-image pixel frame；該次 cross-detector agreement metrics 已標記為 **invalid for interpretation**。

修正版 execution 使用：

```text
cv2.IMREAD_COLOR | cv2.IMREAD_IGNORE_ORIENTATION
```

並逐張 fail closed 驗證：

```text
decoded [h,w] == frozen MediaPipe evidence rec["raw"]
```

Corrected execution accounting：

```text
total image entries = 150
RTMPose usable = 150
primary unique source-byte representatives = 148
stop = false
```

兩組已知 byte-identical source duplicates 在 corrected execution 中再次得到 exact-equal RTMPose keypoints 與 scores：

```text
P005/S1/01.jpg == P005/S3/02.jpg
keypoints exact equal = true
scores exact equal = true
max absolute deltas = 0

P001/S3/03.jpg == P001/S3/05.jpg
keypoints exact equal = true
scores exact equal = true
max absolute deltas = 0
```

因此 primary detector-agreement distributions 以下均使用預先固定的 **148 unique source-byte representatives**。

## Pooled corrected results

| Metric | Mean | Median | P95 | Max |
|---|---:|---:|---:|---:|
| raw 21-landmark mean delta | 0.016463 | 0.016555 | 0.020891 | 0.023920 |
| raw 21-landmark median delta | 0.012790 | 0.012819 | 0.016430 | 0.018822 |
| raw 21-landmark max delta | 0.045316 | 0.045119 | 0.060366 | 0.072451 |
| L0/L5/L17 raw anchor mean delta | 0.031355 | 0.031485 | 0.042734 | 0.049060 |
| L0/L5/L17 raw anchor max delta | 0.044986 | 0.044463 | 0.060366 | 0.072451 |
| canonical-axis angle delta | 1.536° | 1.152° | 4.811° | 7.865° |
| palm-width relative difference | 0.128252 | 0.130831 | 0.174905 | 0.213589 |
| palm-height relative difference | 0.140192 | 0.139170 | 0.213124 | 0.245021 |
| canonical 21-landmark mean delta | 0.137043 | 0.133087 | 0.205313 | 0.264706 |
| canonical 21-landmark max delta | 0.239075 | 0.231881 | 0.377947 | 0.466747 |
| RTMPose score mean | 0.861516 | 0.852688 | 0.937444 | 0.967618 |
| RTMPose score median | 0.880566 | 0.875976 | 0.954044 | 0.990367 |
| RTMPose score minimum | 0.627376 | 0.618663 | 0.741493 | 0.770635 |

Raw normalized deltas are Euclidean distances after dividing x by raw width and y by raw height. Canonical deltas use each detector's own L0/L5/L17 basis and therefore are **not numerically commensurate with the raw normalized metric**. Their magnitudes must not be directly compared as if they shared one scale.

## Per-keypoint pattern

Selected corrected raw mean deltas：

```text
L0 wrist       0.023828
L5 index root  0.025861
L17 pinky root 0.044376

thumb tip      0.015461
index tip      0.012145
middle tip     0.014662
ring tip       0.015121
little tip     0.018408
```

Several non-anchor / distal landmarks had lower raw normalized disagreement than the three canonical anchors. In particular L17 had the largest mean raw delta among the three anchors.

Canonical anchor deltas are small by construction because L0/L5/L17 define each detector's canonical frame:

```text
L0 canonical delta = 0
L5 canonical mean delta ≈ 0.022373
L17 canonical mean delta ≈ 0.022373
```

These small canonical-anchor values are therefore not independent evidence that anchors are intrinsically more detector-stable.

## Predeclared directional questions

### 1. Are L0/L5/L17 more cross-detector stable than fingertip / distal joints?

**Not in raw normalized image geometry.**

Pooled raw anchor mean delta was `0.031355`, nearly 1.9× the pooled 21-landmark raw mean `0.016463`. Many distal points, including several fingertips, had smaller mean raw deltas than L0/L5/L17.

Therefore the first-study result does **not** support the directional expectation that the three palm anchors necessarily have the smallest detector-to-detector disagreement.

The canonical-coordinate result cannot rescue that claim because those anchors define the canonical basis and thus receive structural advantage by construction.

### 2. Does constructing each detector's own canonical basis reduce disagreement relative to raw normalized coordinates?

**This question is not numerically answerable from the two pooled means as currently defined.**

Although both outputs are dimensionless, they use different normalization frames:

```text
raw metric       = image-width / image-height normalized coordinates
canonical metric = detector-specific palm-width / palm-height basis
```

Thus `raw_mean = 0.016463` and `canonical_mean = 0.137043` are not on one common numerical scale. A direct smaller/larger comparison would be methodologically invalid.

What can be stated is decomposition evidence: after raw-frame correction, the two detectors showed close palm-axis orientation (`1.536°` mean), while appreciable scale/shape differences remained in palm width (`12.8%` mean relative difference), palm height (`14.0%`), and canonical landmark geometry (`0.137` mean under the current canonical metric).

A future study would need a predeclared harmonized normalization or common physical/reference scale to answer a literal "reduction" question.

### 3. Are some persons / sessions more detector-sensitive?

**Person-level heterogeneity is visible; session-level means are comparatively stable.**

Per-session means were tightly grouped:

| Session | raw mean | anchor mean | axis delta | canonical mean |
|---|---:|---:|---:|---:|
| S1 | 0.016531 | 0.030977 | 1.861° | 0.140001 |
| S2 | 0.016511 | 0.031389 | 1.427° | 0.139305 |
| S3 | 0.016344 | 0.031713 | 1.311° | 0.131605 |

The raw-mean spread across sessions was only about 1.1% of the session-average raw mean.

By contrast, person-level canonical means ranged from about `0.1063` to `0.2043`. P009 was the clearest high-sensitivity person group:

```text
P009 raw mean       = 0.020275
P009 anchor mean    = 0.039093
P009 axis delta     = 4.332°
P009 canonical mean = 0.204309
```

This is corpus-person heterogeneity only. Dataset person IDs are grouping labels, not biometric identity claims, and no anatomical "palm class" taxonomy was inferred.

### 4. Is RTMPose score descriptively related to detector disagreement?

Yes, a **moderate negative descriptive association** was observed:

```text
Pearson(score mean, raw mean disagreement)       = -0.4684
Pearson(score mean, canonical mean disagreement) = -0.3372
```

Higher RTMPose mean score tended to accompany lower detector disagreement in this bounded sample, with a stronger association for raw normalized geometry.

This does not define or justify a score threshold. No post-hoc exclusion was performed.

### 5. How different are palm width, height, and axis orientation?

The detectors were relatively close on **axis orientation** but less close on **scale geometry**:

```text
axis angle delta:
mean   1.536°
median 1.152°
p95    4.811°
max    7.865°

palm width relative difference:
mean   12.8%
median 13.1%
p95    17.5%
max    21.4%

palm height relative difference:
mean   14.0%
median 13.9%
p95    21.3%
max    24.5%
```

Therefore one bounded interpretation is:

> MediaPipe and RTMPose generally agree on the gross palm-axis direction in these MOHI images, while detector choice still changes inferred palm scale and internal 21-landmark geometry enough that downstream canonical measurements should retain detector provenance.

## EXIF diagnostic significance

Before frame correction, the same study produced an apparent pooled axis delta near `88°`. That value was traced to different JPEG orientation handling rather than detector geometry and is invalid for detector-agreement interpretation.

The corrected mean axis delta of `1.536°` demonstrates why raw-image frame provenance and explicit EXIF policy are part of the measurement contract rather than mere I/O details.

The first mismatched run remains useful only as implementation-diagnostic evidence and duplicate-determinism evidence; its agreement distributions must not be cited as detector disagreement results.

## Bounded interpretation

Within this permission-qualified MOHI subset and the two pinned runtimes:

- both detector paths produced usable geometry for all 150 image entries after raw-frame alignment;
- byte-identical duplicates reproduced exact RTMPose keypoints and scores;
- cross-detector raw normalized landmark disagreement was small in image-normalized coordinates on average, but not uniform across keypoints;
- L0/L5/L17 were not the lowest-disagreement points in raw geometry;
- palm-axis direction agreed relatively closely;
- palm-width, palm-height and canonical shape retained material detector-dependent differences;
- person-group heterogeneity was more visible than session-level mean shifts;
- higher RTMPose score was descriptively associated with lower disagreement, but no score cutoff is justified.

These findings support preserving `detector_id / detector_version / model artifact / raw-frame policy` in Palm Observation provenance. They do not support silently treating outputs from different hand landmark detectors as interchangeable geometry.

## Evidence boundary

This result does **not** establish:

- which detector is anatomically more accurate;
- ground-truth hand geometry;
- biometric identity continuity;
- a production detector-selection rule;
- a production admission threshold;
- a score threshold;
- generalization to arbitrary phone cameras or uncontrolled backgrounds;
- device-to-device repeatability;
- long-term longitudinal stability;
- principal-line segmentation repeatability.

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
