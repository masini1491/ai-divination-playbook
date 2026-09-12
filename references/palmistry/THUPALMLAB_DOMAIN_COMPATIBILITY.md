# THUPALMLAB Domain Compatibility Probe

Status: **REFERENCE-ONLY / BOUNDED NEGATIVE RUNTIME RESULT**

This Cold note records a bounded compatibility probe between the existing pinned MediaPipe Hand Landmarker baseline and a user-supplied THUPALMLAB multi-impression sample.

It does **not** establish dataset-wide detector performance, scanner-domain repeatability, camera-domain repeatability, biometric identity continuity, or a production admission threshold.

## Source sample

User supplied a ZIP produced from the public THUPALMLAB multi-impression corpus.

Observed sample payload:

```text
source ZIP SHA256:
8a97a27dab0bf362be9925f78873912f95fc19d79c49cfd789f6be55e63dfd93

one dataset-provided palm class:
subject 1 / left palm

8 independent scanner impressions:
1_l_1.bmp ... 1_l_8.bmp

image geometry:
2040 × 2040
BMP / grayscale
```

The initial sampling helper had incorrectly treated a shared parent directory as the grouping key, so this first ZIP contains only one palm class rather than the originally intended 10 classes. That sampling defect does not invalidate the narrow runtime-compatibility question because eight independent impressions from one palm are still sufficient for the first fail-fast gate.

## Frozen runtime baseline

The probe used the same pinned observation runtime family already used by earlier Palmistry research:

```text
MediaPipe: 1.0.1
Hand Landmarker model SHA256:
fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1

running_mode = IMAGE
num_hands = 2
min_hand_detection_confidence = 0.5
min_hand_presence_confidence = 0.5
min_tracking_confidence = 0.5
```

Each `2040 × 2040` image was resized by the existing research max-dimension convention to `1600 × 1600` before inference (`scale = 0.7843137254901961`).

No detector threshold was lowered after observing failures.

## Observed result

All eight images decoded successfully.

Final Hand Landmarker candidate counts:

```text
0 candidates: 8
1 candidate:  0
2 candidates: 0

usable_exactly_one_rate = 0.0
```

Therefore this sample produces a clean bounded negative result:

```text
for subject-1 left-palm THUPALMLAB impressions 1..8,
under the pinned MediaPipe 1.0.1 / 0.5 / IMAGE baseline,
the current full-hand landmark runtime returned no hand candidate on every image.
```

## Interpretation

This is evidence of a **runtime / capture-domain compatibility failure for this bounded scanner sample**.

It is consistent with the prior concern that a high-resolution contact/scanner palmprint corpus is not necessarily compatible with a full-hand detector trained for ordinary hand imagery, even when the frame visually contains palm/finger structure.

It does **not** justify any of the following stronger claims:

- all THUPALMLAB images will fail;
- MediaPipe cannot process any scanner palmprint;
- the failure is caused by one specific visual factor;
- original `2040 × 2040` inference would necessarily behave identically;
- a lower detector threshold would be scientifically preferable;
- THUPALMLAB is unsuitable for palmprint algorithms in general.

The frozen protocol predeclared fail-closed behavior: if the pinned full-hand runtime could not produce usable landmarks, record the domain-compatibility result and stop rather than tuning the detector to rescue the corpus.

## Stop decision

For the current Palmistry canonical-coordinate research path:

```text
THUPALMLAB full-hand landmark compatibility probe = NEGATIVE
→ do not expand to 10 classes × 8 impressions with this runtime
→ do not lower detector thresholds
→ do not derive canonical repeatability statistics from nonexistent landmarks
```

THUPALMLAB remains potentially useful as an external scanner-domain palmprint reference, but it is no longer the preferred executable fallback for the current MediaPipe-based canonical observation pipeline.

The higher-value next dataset target remains a permission-qualified **contactless full-hand multi-capture / multi-session corpus**.

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
