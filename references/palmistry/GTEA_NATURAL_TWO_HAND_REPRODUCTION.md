# GTEA Natural Two-Hand Reproduction

Status: **REFERENCE-ONLY / NATURAL CAPTURE EXECUTED**

This Cold research note records the first natural-capture reproduction of the multi-hand candidate-count instability previously observed only in synthetic stress fixtures. It does not establish a production threshold, biometric identity rule, or Palmistry routing authority.

## Source and annotation semantics

Source asset: GTEA / GTEA Gaze+ Hand 2K dataset (`hand2K_dataset.zip`).

Uploaded archive SHA256:

```text
a64c0fcff572414fa964c5b524e989ffe2e0a6023316bf4554a0f3e24d66fb8b
```

The archive `Readme.txt` states that the dataset contains pixel-level hand annotations, raw LabelMe XML annotations, and processed PNG masks, with separate labels for left hand / right hand / intersecting hands. Direct inspection of XML confirms per-object labels such as `Left hand` and `Right hand` with polygon coordinates. Therefore this study does **not** use connected-component count as hand-count ground truth.

Archive inventory observed from the uploaded file:

```text
GTEA/Images        663 JPG
GTEA/Annotations   663 XML
GTEA/Masks         663 PNG
GTEA/oldImages     199 JPG
GTEA/oldMasks      199 PNG
GTEA_GAZE_PLUS/Images       1115 JPG
GTEA_GAZE_PLUS/Annotations  1115 XML
GTEA_GAZE_PLUS/Masks        1115 PNG
```

Across the 1,778 XML files, direct object-label inspection found 955 frames with exactly the `Left hand` + `Right hand` label combination, plus additional naming variants using underscores/case differences. This is annotation evidence, not detector output.

## Bounded natural sequence

Sequence selected: `GTEA s2_coffee`.

Selection rule:

```text
include an annotation sample iff its non-deleted XML objects contain
both normalized labels `left hand` and `right hand`
```

Result: **36** selected annotation samples. These are ordered annotation samples from one natural egocentric capture sequence; they are not every video frame.

The selected XML GT remains two annotated hands throughout the 36-sample study.

## Pinned detector baseline

Same research family as prior MediaPipe studies:

```text
Hand Landmarker model SHA256
fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1

MediaPipe full-run thresholds
num_hands = 4
min_hand_detection_confidence = 0.5
min_hand_presence_confidence = 0.5
min_tracking_confidence = 0.5
running_mode = IMAGE
```

The official MediaPipe graph config confirms that the hand detector uses 2,016 boxes, sigmoid scores, `min_detection_confidence`, weighted NMS with IoU threshold `0.3`, and clips the resulting hand-rect vector to `num_hands`. The landmark detector separately applies a hand-presence threshold. These implementation details are model-adapter evidence only.

## Detector-stage post-execution observation

The uploaded archive was also screened locally by reconstructing the pinned model's palm-detector preprocessing / anchor decoding / weighted-NMS stage. Before using it on GTEA, the reconstruction was checked against the prior Case A and Case B fixtures: both produced one NMS candidate, matching the previously recorded full Hand Landmarker baseline candidate count for those fixtures.

For the 36 direct-XML `Left hand + Right hand` samples in `s2_coffee`, palm-detector-stage candidate count was:

| Palm candidates | Frames |
|---:|---:|
| 0 | 1 |
| 1 | 18 |
| 2 | 17 |

Across adjacent selected annotation samples, candidate count changed **18 times**.

This is the first natural-capture evidence in this research line where the source annotation remains two hands while the detector stage alternates among retained-two-hand and hand-loss states.

Important boundary: these exact `0/1/2 = 1/18/17` values are **palm-detector-stage** observations, not final Hand Landmarker counts.

## Full Hand Landmarker confirmation

Ephemeral GitHub Actions research run:

```text
run 34623163259
head 30d20d0f9011da93ff12463f59205cf320a99976
```

The corrected workflow used direct XML object labels, selected exactly the same 36 `s2_coffee` GT-two-hand samples, and ran the pinned full MediaPipe Hand Landmarker. The run completed successfully.

The workflow had explicit assertions requiring all of the following to be true:

1. exactly 36 direct-XML GT-two-hand samples were selected;
2. at least one sample retained `>=2` final Hand Landmarker candidates;
3. at least one sample had `<2` final candidates;
4. at least one final candidate-count transition occurred across adjacent selected annotation samples.

Because the run passed, natural-capture candidate retention **and** candidate loss/transition are confirmed at the full Hand Landmarker output stage as well. The connector did not expose the job stdout, so this note does not invent an exact final-count distribution that was not independently retrieved.

## Evidence boundary

What is now supported:

```text
same natural sequence
+ source XML repeatedly annotates Left hand + Right hand
+ pinned detector sometimes retains two candidates
+ pinned detector sometimes retains fewer than two
+ full Hand Landmarker also exhibits retained >=2 and lost <2 states
→ candidate-count instability is not only a synthetic-composite artifact
```

What is **not** supported:

- a production numeric admission threshold;
- a claim that every annotation sample has equal visibility / palm orientation / image quality;
- a claim that annotation labels guarantee a palm is detector-observable;
- biometric identity continuity;
- a natural retained-two-candidate near-tie distribution;
- generalization to other devices, subjects, MediaPipe versions, or models.

## Fail-closed implication

The prior qualitative gate gains natural-capture support:

```text
expected / annotated multi-hand scene
+ candidate disappearance, reappearance, or count instability
→ target association is not automatically resolved
→ target-specific fine geometry should fail closed until target continuity is re-established
```

This remains a qualitative research implication. Palmistry remains `REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE`.

## Next bounded node

The highest-value remaining natural-image question is no longer whether candidate-count instability can occur naturally; this study confirms that it can. The next node is to characterize **why** retained/lost states differ using source-supported variables such as annotated occlusion, hand geometry/area, separation, and image quality, then test whether a natural retained-two-candidate near-tie / ranking swap can be reproduced without synthetic compositing.
