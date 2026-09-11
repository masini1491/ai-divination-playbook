# GTEA Natural Two-Hand Feature Study

Status: **REFERENCE-ONLY / NATURAL CAPTURE EXECUTED**

This Cold study asks which observable source/image features differ between natural two-hand frames where the pinned MediaPipe Hand Landmarker retains two final candidates and frames where it returns fewer than two. It does not define a production admission threshold or Palmistry routing rule.

## Provenance and sample

Source: uploaded GTEA / GTEA Gaze+ Hand 2K archive.

```text
archive SHA256
a64c0fcff572414fa964c5b524e989ffe2e0a6023316bf4554a0f3e24d66fb8b
```

Ground-truth admission uses direct XML objects only: a frame is eligible when normalized non-deleted object labels contain both `Left hand` and `Right hand` and the paired JPG exists.

Observed GTEA candidate pool under that rule: **556 frames**.

Bounded deterministic sample: **240 frames**, evenly spaced over the sorted eligible XML/JPG pairs.

No source JPG/XML/PNG is copied into this repository.

## Pinned runtime

```text
MediaPipe               1.0.1
Python                  3.12.14
OpenCV                  5.0.0
Hand Landmarker SHA256  fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1
num_hands               4
detection/presence/tracking thresholds = 0.5 / 0.5 / 0.5
running_mode             IMAGE
```

Research run:

```text
34625071819
head 0c669d44307c0c79888fb475e5170df49e0ec88d
```

The first attempt (`34624942964`) failed only while JSON-serializing NumPy `float32` values; its metrics were not adopted. The corrected run completed successfully.

## Final candidate distribution

Across the 240 direct-XML two-hand frames:

| Final Hand Landmarker candidates | Frames |
|---:|---:|
| 0 | 42 |
| 1 | 129 |
| 2 | 69 |

Therefore:

```text
retained >=2 = 69
lost <2       = 171
```

The fact that source annotation says two hands does not imply both palms are detector-observable. These counts describe detector behavior, not annotation quality or identity continuity.

## Features measured

All measurements are post-execution observations derived from the paired source image/XML for this study:

- `min_area_frac`: smaller annotated hand polygon area / image area;
- `mean_area_frac`: mean of left/right polygon-area fractions;
- `area_ratio`: smaller polygon area / larger polygon area;
- `centroid_sep_diag`: annotated hand-centroid distance / image diagonal;
- `min_poly_gap_diag`: minimum polygon point-to-point distance / image diagonal;
- `bbox_iou`: left/right annotation bounding-box IoU;
- `min_border_frac`: minimum annotated polygon distance to image border / shorter image side;
- whole-frame brightness, contrast, Laplacian-variance blur;
- annotated-hand-region brightness and contrast.

The analysis compares `retained >=2` vs `lost <2` using two-sided Mann-Whitney U. Reported p-values are exploratory and **uncorrected for multiple comparisons**. The `AUC` column here is the Mann-Whitney probability form `U/(n_retained*n_lost)`, not a trained classifier score.

## Univariate results

| Feature | Median retained-2 | Median lost | AUC retained>lost | exploratory p |
|---|---:|---:|---:|---:|
| `area_ratio` | 0.7192 | 0.5120 | 0.6819 | 1.04e-5 |
| `min_area_frac` | 0.04690 | 0.03661 | 0.6572 | 1.39e-4 |
| `min_border_frac` | 0.0000 | 0.0000 | 0.6037 | 2.68e-4 |
| `min_poly_gap_diag` | 0.07432 | 0.09535 | 0.4055 | 0.0221 |
| `mean_area_frac` | 0.06367 | 0.05699 | 0.5562 | 0.173 |
| hand brightness | 73.16 | 71.44 | 0.5473 | 0.253 |
| hand contrast | 19.07 | 18.69 | 0.5345 | 0.403 |
| frame contrast | 32.83 | 32.61 | 0.5329 | 0.425 |
| `bbox_iou` | 0.0000 | 0.0000 | 0.4852 | 0.637 |
| `centroid_sep_diag` | 0.37408 | 0.37455 | 0.4851 | 0.719 |
| blur | 101.22 | 99.78 | 0.5085 | 0.837 |
| frame brightness | 111.30 | 111.98 | 0.4960 | 0.923 |

## Interpretation

The strongest observed one-variable signals are **hand-size balance** and **size of the smaller annotated hand**:

```text
more balanced left/right visible polygon area
+ larger smaller-hand area fraction
↔ more often two final candidates are retained
```

This reproduces the direction suggested by the earlier 36-frame `s2_coffee` screen, where retained-two frames also tended to have a larger smaller-hand area and more balanced hand areas.

By contrast, this sample provides little evidence that simple centroid separation, whole-frame brightness, or global blur explains retained-vs-lost state by itself. In particular, median centroid separation is effectively the same (`0.37408` vs `0.37455` image diagonals).

`min_poly_gap_diag` is directionally counterintuitive if interpreted as a simple "closer hands cause collapse" rule: retained-two frames have the *smaller* median polygon gap. Therefore hand proximity must not be promoted as a monotonic admission rule from this evidence.

`min_border_frac` has identical medians of zero because many annotations contact or slightly exceed the image edge; its rank difference may contain information, but the metric is unsuitable as a standalone gate in its current form and needs a better truncation descriptor.

## Quality-gate implication

Current evidence supports only a candidate feature family, not a cutoff:

```text
relative smaller-hand scale
+ left/right visible-area balance
+ explicit truncation/visibility state
→ candidate inputs for a future multi-hand observability gate
```

It does **not** support rules such as:

```text
area_ratio < X => reject
min_area_frac < Y => reject
hand separation < Z => ambiguous
```

No `X/Y/Z` is established here. A defensible gate would require predeclared evaluation criteria, held-out sequences/subjects, calibration against the final task (target-specific palm geometry), and preferably detector/runtime replication.

## Evidence boundary

Supported:

1. natural direct-XML two-hand frames frequently produce fewer than two final Hand Landmarker candidates;
2. in this 240-frame bounded sample, visible-area balance and smaller-hand area have the strongest univariate association with retaining two candidates;
3. centroid separation, brightness, and blur are weak univariate separators here;
4. simple hand proximity is not monotonic evidence for candidate loss.

Not supported:

- production thresholds;
- causality;
- independent-IID statistical claims across temporally related frames;
- generalization beyond this GTEA subset, model/runtime, or detector;
- a natural retained-two-candidate association near-tie/ranking-swap distribution;
- biometric identity continuity.

Palmistry remains `REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE`.

## Next bounded node

The next useful step is **sequence-held-out validation** rather than adding more correlated frames from the same pool: derive only a provisional observability score from size balance / smaller-hand scale / truncation, then test whether its ordering survives when entire GTEA sequences are held out. In parallel, retained-two natural frames can be screened for association near-ties without changing detector thresholds.
