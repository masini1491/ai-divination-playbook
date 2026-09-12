# Palm Multi-capture Dataset Qualification Gate

Status: **REFERENCE-ONLY / DATASET QUALIFICATION COMPLETE**

This Cold note qualifies candidate public palm-image corpora for the next Palmistry research gap: **independent multi-capture repeatability**.

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

## Candidate screen

### XINHUA Palmprint via `HewelXX/Dataset`

GitHub connector inspection confirms source JPEGs directly under `XINHUA/`, with repeated filename groups such as `100_1.jpg ... 100_20.jpg`.

The associated publication's Data Availability statement identifies both the GitHub dataset location and Zenodo DOI `10.5281/zenodo.15473268`, and describes 50 participants, 100 palm classes, 20 images per palm, split into two capture periods of 10 images each.

A connector capability probe successfully returned base64 JPEG content for `XINHUA/100_1.jpg` without raw-GitHub fallback.

However, the repository itself contains no confirmed dataset license, and the publication's Data Availability statement establishes location/provenance rather than explicit reuse permission. The associated Zenodo record has not yet supplied a sufficiently explicit dataset-level license statement in the evidence captured for this Playbook.

Decision:

```text
best current structural candidate for contactless multi-capture repeatability
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

This is one of the strongest domain-fit candidates for within-session versus cross-session observation repeatability, but the inspected project page does not state an explicit dataset reuse license comparable to THUPALMLAB's non-commercial-research statement.

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

This resolves the research-use permission gate more clearly than the current XINHUA / Tongji evidence.

THUPALMLAB is a **contact / scanner-acquired high-resolution palmprint corpus**, whereas the current Palmistry observation pipeline is primarily concerned with ordinary palm-facing photographs and MediaPipe full-hand landmark geometry.

The official archive location was resolved as:

```text
https://ivg.au.tsinghua.edu.cn/dataset/samples_THUPALMLAB/THUPALMLAB.rar
```

A user subsequently supplied a bounded extracted sample consisting of one dataset-provided palm class (`subject 1 / left palm`) with eight scanner impressions (`1_l_1.bmp ... 1_l_8.bmp`).

Observed bounded runtime probe:

```text
source ZIP SHA256:
8a97a27dab0bf362be9925f78873912f95fc19d79c49cfd789f6be55e63dfd93

MediaPipe 1.0.1
Hand Landmarker model SHA256:
fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1

IMAGE mode
num_hands = 2
min detection / presence / tracking = 0.5 / 0.5 / 0.5

2040 × 2040 source → 1600 × 1600 working image

candidate-count distribution:
0 = 8
1 = 0
2 = 0

usable_exactly_one_rate = 0.0
```

This is a **bounded scanner-domain compatibility negative result** for the sampled subject-1 left-palm impressions. It does not establish dataset-wide detector failure and must not be generalized to all THUPALMLAB images or all scanner palmprints.

Decision:

```text
DATA-USE GATE SATISFIED for non-commercial research / education
sample acquisition achieved via user-provided extract
PINNED FULL-HAND RUNTIME COMPATIBILITY = NEGATIVE on 8/8 bounded impressions
→ stop this MediaPipe-based THUPALMLAB repeatability path
→ do not lower thresholds
→ do not expand to 10 classes merely to rescue the corpus
```

The detailed runtime record lives in `THUPALMLAB_DOMAIN_COMPATIBILITY.md`.

### MPW-180 / PalmWildNet

IAPR TC4 lists MPW-180 as a recent palmprint dataset, and the GitHub repository `bingolo/PalmWildNet` describes a mobile palmprint corpus with multiple smartphones, flash/non-flash conditions, realistic environments, 180 subjects, 720 videos, and thousands of ROI images.

The README claims:

```text
code: Apache-2.0
dataset: CC BY-NC 4.0
```

But connector inspection of the current repository root shows only `README.md`, `LICENSE`, `Figure12b.png`, and `Figures/`. The README's documented `DATASET_LICENSE` file is absent, the dataset DOI/link is still a placeholder, and the README states that the study is still under review.

Decision:

```text
capture-domain fit is excellent for future phone/device repeatability
CURRENT DATASET RELEASE SURFACE IS INCOMPLETE
README license claim alone is insufficient
→ hold until actual dataset + license artifact are published
```

### BJTU Palm V2 via `HewelXX/Dataset`

GitHub connector inspection confirms an actual archive object:

```text
path: BJTU_V2/bjtu_palm_v2.zip
Git blob: d51d1ee0776afc786f3e8a2a1ec5997bb34f9e1b
observed GitHub object size: 5,422,067 bytes
```

But the repository README is minimal and no license was found during qualification.

Decision: acquisition exists, license/provenance qualification insufficient → hold.

### NTU Palmprints / NTU Contactless Palmprints

Official/project documentation requires completing and returning a Data Release Agreement before a download link is supplied.

Decision: scientifically relevant but access-gated; not an anonymous reproducible baseline corpus.

### IITD Touchless Palmprint

Acquisition likewise requires a request/agreement workflow.

Decision: scientifically relevant but not suitable as an automated reproducible baseline corpus.

## Current ranking

| Candidate | Multi-capture structure | Data-use gate | Capture-domain fit | Current decision |
|---|---|---|---|---|
| Tongji Contactless | **2 sessions × 10 / palm** | unresolved | excellent | preferred if permission closes |
| XINHUA | **2 periods × 10 / palm** | unresolved | excellent | preferred if permission closes |
| MPW-180 | multi-device / video | release incomplete | **best future phone/device fit** | hold |
| THUPALMLAB | **8 / palm** | **explicit non-commercial research/education** | scanner/contact mismatch | bounded MediaPipe compatibility negative; stop current full-hand path |
| BJTU V2 | repeated dataset likely useful | unresolved | contactless | hold |
| NTU-CP / NTU-PI | repeated | agreement-controlled | contactless | hold |
| IITD | repeated | agreement-controlled | contactless | hold |

This ranking is about research operability and domain fit, not overall dataset scientific quality.

## Predeclared contactless multi-session experiment

If Tongji or XINHUA permission closes, do not tune the protocol after seeing repeatability results.

Use dataset-provided palm classes only as grouping labels.

```text
session/period A and B remain separate
run the same pinned MediaPipe Hand Landmarker baseline
require a unique usable target hand or fail closed
map landmarks to raw-image geometry
compute canonical L0/L5/L17 palm basis
compare within-class canonical geometry across captures
report within-session and cross-session distributions separately
```

At minimum report detector success/failure rate, candidate-count distribution, canonical anchor/frame drift, within-session versus cross-session drift, per-class heterogeneity, and failure modes.

## Common prohibitions

Do **not**:

- infer real identity from a dataset class label;
- train or evaluate biometric authentication for this Palmistry research node;
- lower detector thresholds to rescue failed frames;
- tune a production admission threshold from the same corpus;
- treat public download availability as equivalent to a reuse license;
- commit source images into this Playbook;
- silently generalize scanner results to contactless phone/camera capture;
- promote README-stated future dataset licensing to observed released-license evidence when the license artifact is absent.

## Evidence boundary

This node establishes dataset suitability, permission state, release state, acquisition constraints, and the bounded THUPALMLAB runtime-compatibility result only.

It does not establish:

- a multi-capture repeatability distribution;
- a device-to-device repeatability distribution;
- a production quality threshold;
- detector-to-detector agreement;
- line-segmentation repeatability;
- biometric identity continuity.

Current executable state:

```text
Tongji / XINHUA: strongest contactless multi-session candidates; permission unresolved
MPW-180: strongest future phone/device candidate; dataset release incomplete
THUPALMLAB: permission clear; bounded sample acquired; current pinned full-hand runtime failed 8/8 and is stopped
```

The next high-value executable node requires a permission-qualified **contactless full-hand multi-capture / multi-session corpus**. Until then, the correct outcome is evidence-bounded rather than invented repeatability evidence.

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
