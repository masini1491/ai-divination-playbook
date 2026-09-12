# Palm Multi-capture Dataset Qualification Gate

Status: **REFERENCE-ONLY / DATASET QUALIFICATION COMPLETE**

This Cold note qualifies candidate public palm-image corpora for Palmistry **independent multi-capture repeatability** research and records the first completed permission-qualified contactless study.

It intentionally separates:

```text
publicly described
≠ publicly downloadable
≠ reproducibly acquirable in the current runtime
≠ license-qualified for automated research reuse
≠ suitable for palm-facing geometry repeatability
```

No dataset in this note becomes production authority or biometric identity evidence.

## Research requirement

A useful corpus for this node should provide, at minimum:

1. multiple independently captured images of the same palm;
2. a grouping key that can be interpreted as dataset-provided palm class / capture group rather than inferred identity;
3. palm-facing images suitable for the existing landmark / canonical-coordinate research path;
4. acquisition that can be reproduced without bypassing repository access policy;
5. sufficiently clear license / data-use terms for the intended research use;
6. no need to commit third-party source images into this repository.

The target measurement is **within-dataset palm-class repeatability**, not biometric identity verification.

## Completed executable corpus: MOHI

Mutah University's official Hand Images Databases page states that the databases are freely available for **research and teaching purposes**; other uses require consultation.

MOHI provides mobile-phone-camera full-hand images with:

```text
200 persons
right hand only
3 sessions
5 images / person / session
15 images / person
3,000 images total
3264 × 2448
session interval ≈ 3 days
rotation / scale / lighting variation
```

The predeclared first study used the first 10 common complete dataset person IDs from S1/S2/S3 Group 1:

```text
10 persons × 3 sessions × 5 image entries = 150 entries
```

Frozen runtime:

```text
MediaPipe 1.0.1
Hand Landmarker model SHA256:
fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1
IMAGE mode
num_hands = 2
min detection / presence / tracking = 0.5 / 0.5 / 0.5
```

Observed bounded runtime compatibility:

```text
150 / 150 image entries decoded
150 / 150 exactly one candidate
usable rate = 1.0
```

Original pooled repeatability result:

```text
within-session pairs = 300
cross-session pairs = 750

anchor mean drift:
0.05056 within → 0.07216 cross

canonical mean drift:
0.05882 within → 0.07599 cross

axis angle delta:
7.14° within → 10.26° cross
```

Every reported cross-session pooled mean exceeded the corresponding within-session pooled mean.

A deterministic integrity audit then verified:

```text
manifest rows = 150
ZIP image entries = 150
manifest hash mismatches = 0

duplicate SHA groups = 2
duplicate image entries = 4
```

Duplicate groups:

```text
P005/S1/01.jpg == P005/S3/02.jpg
P001/S3/03.jpg == P001/S3/05.jpg
```

The two byte-identical detector-geometry groups correspond exactly to these duplicate source-image groups. Thus the exact-zero minima in the original pooled output are explained by duplicate source bytes, not unexplained detector invariance.

Only one within-session pair and one cross-session pair are duplicate-induced zero pairs. Removing those zero pairs changes pooled means by about `+0.334%` within-session and `+0.134%` cross-session respectively, so the observed cross > within ordering is not reversed.

Decision:

```text
DATA-USE GATE SATISFIED for research / teaching
CONTACTLESS FULL-HAND DOMAIN FIT SATISFIED
MULTI-SESSION STRUCTURE SATISFIED
PINNED RUNTIME COMPATIBILITY POSITIVE on 150/150 entries
BOUNDED REPEATABILITY STUDY COMPLETE
INTEGRITY AUDIT CLOSED with 2 duplicate-content groups characterized
```

Detailed records:

- `MOHI_MULTICAPTURE_PLAN.md`
- `MOHI_REPEATABILITY_RESULTS.md`
- `mohi_mediapipe_repeatability.py`
- `mohi_integrity_audit.py`

The sample must not be described as 150 unique independent source photographs because four entries belong to two byte-identical duplicate groups.

## Candidate screen

### XINHUA Palmprint via `HewelXX/Dataset`

GitHub connector inspection confirms source JPEGs directly under `XINHUA/`, with repeated filename groups such as `100_1.jpg ... 100_20.jpg`.

The associated publication's Data Availability statement identifies both the GitHub dataset location and Zenodo DOI `10.5281/zenodo.15473268`, and describes 50 participants, 100 palm classes, 20 images per palm, split into two capture periods of 10 images each.

However, the repository itself contains no confirmed dataset license, and the publication's Data Availability statement establishes location/provenance rather than explicit reuse permission. The associated Zenodo record has not yet supplied a sufficiently explicit dataset-level license statement in the evidence captured for this Playbook.

Decision:

```text
strong alternative contactless multi-session structure
LICENSE / DATA-USE GATE UNRESOLVED
```

### Tongji Contactless Palmprint Dataset

The official project page describes:

```text
300 volunteers
600 palms
2 sessions
10 images / palm / session
20 images / palm total
12,000 images total
mean inter-session interval ≈ 61 days
range 21–106 days
```

The official page exposes public links for original images and ROI images and documents the session/name correspondence.

This remains a strong candidate for a longer-interval contactless repeatability study, but the inspected project page does not state an explicit dataset reuse license comparable to MOHI's research/teaching statement.

Decision:

```text
excellent contactless / multi-session structure
public download surface exists
PROVENANCE STRONG
DATA-USE / LICENSE GATE UNRESOLVED
```

Public download availability alone is not permission authority.

### THUPALMLAB multi-impression subset

The official Tsinghua University dataset page explicitly states that the public multi-impression subset may be downloaded for **non-commercial research and educational purposes**.

The official page describes:

```text
80 subjects
2 palms per subject
8 impressions per palm
1,280 palmprint images
2040 × 2040 pixels
500 ppi
commercial Hisign palmprint scanner
```

A user supplied a bounded extracted sample consisting of one dataset-provided palm class (`subject 1 / left palm`) with eight scanner impressions.

Observed bounded runtime probe under the same pinned MediaPipe baseline:

```text
candidate-count distribution:
0 = 8
1 = 0
2 = 0
usable_exactly_one_rate = 0.0
```

Decision:

```text
DATA-USE GATE SATISFIED
scanner/contact domain mismatch
PINNED FULL-HAND RUNTIME COMPATIBILITY NEGATIVE on bounded 8/8 impressions
→ stop this MediaPipe-based THUPALMLAB path
```

This does not establish dataset-wide detector failure.

### MPW-180 / PalmWildNet

IAPR TC4 lists MPW-180 as a recent palmprint dataset, and the GitHub repository `bingolo/PalmWildNet` describes a mobile palmprint corpus with multiple smartphones, flash/non-flash conditions, realistic environments, 180 subjects, 720 videos, and thousands of ROI images.

The README claims code Apache-2.0 and dataset CC BY-NC 4.0, but the documented dataset-license artifact and final dataset DOI/link were not present during qualification.

Decision:

```text
best future phone/device-fit candidate
CURRENT DATASET RELEASE SURFACE INCOMPLETE
→ hold until actual dataset + license artifact are published
```

### BJTU Palm V2 via `HewelXX/Dataset`

An actual archive object exists, but no sufficient dataset license/provenance statement was found.

Decision: acquisition exists, license/provenance qualification insufficient → hold.

### NTU Palmprints / NTU Contactless Palmprints

Official/project documentation requires a Data Release Agreement before download.

Decision: scientifically relevant but access-gated; not an anonymous reproducible baseline corpus.

### IITD Touchless Palmprint

Acquisition requires a request/agreement workflow.

Decision: scientifically relevant but not suitable as an automated reproducible baseline corpus.

## Current ranking

| Candidate | Multi-capture structure | Data-use gate | Capture-domain fit | Current decision |
|---|---|---|---|---|
| MOHI | **3 sessions × 5 / person** | **explicit research/teaching** | **mobile/contactless full hand** | **bounded study complete; duplicate audit closed** |
| Tongji Contactless | **2 sessions × 10 / palm** | unresolved | excellent | preferred longer-interval follow-up if permission closes |
| XINHUA | **2 periods × 10 / palm** | unresolved | excellent | alternative if permission closes |
| MPW-180 | multi-device / video | release incomplete | **best future phone/device fit** | hold |
| THUPALMLAB | **8 / palm** | explicit non-commercial research/education | scanner/contact mismatch | bounded MediaPipe compatibility negative; stopped |
| BJTU V2 | repeated dataset likely useful | unresolved | contactless | hold |
| NTU-CP / NTU-PI | repeated | agreement-controlled | contactless | hold |
| IITD | repeated | agreement-controlled | contactless | hold |

This ranking is about research operability and domain fit, not overall dataset scientific quality.

## Common prohibitions

Do **not**:

- infer real identity from a dataset class label;
- train or evaluate biometric authentication for this Palmistry research node;
- lower detector thresholds to rescue failed frames;
- tune a production admission threshold from the same corpus;
- treat public download availability as equivalent to a reuse license;
- commit source images into this Playbook;
- silently generalize scanner results to contactless phone/camera capture;
- silently generalize MOHI results to device-to-device or long-term longitudinal stability;
- describe duplicated sample entries as unique independent captures.

## Evidence boundary

This node now establishes:

- one permission-qualified contactless full-hand multi-session bounded repeatability result under MOHI;
- positive pinned-runtime compatibility for all 150 MOHI image entries in the first study;
- descriptive within-session versus cross-session geometry distributions;
- a closed duplicate-content audit explaining all exact-zero detector-geometry groups;
- a bounded negative scanner-domain runtime result for THUPALMLAB.

It still does **not** establish:

- device-to-device repeatability;
- long-term longitudinal stability;
- production quality/admission thresholds;
- detector-to-detector agreement;
- principal-line segmentation repeatability;
- biometric identity continuity.

Current executable state:

```text
MOHI: bounded contactless multi-session study complete; integrity caveat characterized
Tongji / XINHUA: longer-interval / alternative contactless candidates; permission unresolved
MPW-180: strongest future multi-device candidate; release incomplete
THUPALMLAB: permission clear; bounded scanner sample incompatible with current pinned full-hand runtime
```

The next high-value research gaps are **device-to-device repeatability**, **longer-term longitudinal stability**, **detector-to-detector agreement**, and **principal-line segmentation repeatability**.

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
