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

GitHub connector inspection confirms that source JPEGs are present directly under `XINHUA/`, with repeated filename groups such as `100_1.jpg ... 100_20.jpg`.

The associated publication's Data Availability statement identifies both the GitHub dataset location and Zenodo DOI `10.5281/zenodo.15473268`. It describes the corpus as 50 participants, 100 palm classes, 20 images per palm, with two capture periods of 10 images each.

A connector capability probe successfully returned base64 JPEG content for `XINHUA/100_1.jpg`; no raw-GitHub fallback is required for bounded inspection.

However, the GitHub repository itself contains no confirmed dataset license, and the publication's Data Availability statement establishes location/provenance rather than explicit reuse permission. The associated Zenodo record has not yet supplied a sufficiently explicit dataset-level license statement in the evidence captured for this Playbook.

Decision:

```text
best current structural candidate for contactless multi-capture repeatability
LICENSE / DATA-USE GATE UNRESOLVED
```

### Tongji Contactless Palmprint Dataset

The official project page describes a particularly strong longitudinal contactless design:

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

The official page exposes public links for both original images and extracted ROI images and documents the session/name correspondence.

This is currently one of the strongest domain-fit candidates for the exact question of within-session versus cross-session observation repeatability.

However, the project page inspected in this research node does not state an explicit dataset reuse license comparable to THUPALMLAB's non-commercial-research statement.

Decision:

```text
excellent contactless / multi-session structure
public download surface exists
PROVENANCE STRONG
DATA-USE / LICENSE GATE UNRESOLVED
```

Do not treat public download availability alone as permission authority.

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

This resolves the basic research-use permission gate more clearly than the current XINHUA / Tongji evidence.

But THUPALMLAB is a **contact / scanner-acquired high-resolution palmprint corpus**, whereas the existing Palmistry observation pipeline is primarily concerned with ordinary palm-facing photographs and MediaPipe landmark geometry. It is therefore a control/fallback corpus rather than an equivalent contactless validation corpus.

A bounded acquisition probe resolved the official download link to:

```text
https://ivg.au.tsinghua.edu.cn/dataset/samples_THUPALMLAB/THUPALMLAB.rar
```

Observed execution boundary:

- the official HTML page remained reachable and advertised the archive;
- Web retrieval of the archive itself was blocked by crawler robots handling;
- the local execution container had no working external DNS/network path, so a direct archive download could not be verified there.

This is **not evidence that the official dataset download is dead**. It is only an environment-specific acquisition limitation.

Decision:

```text
DATA-USE GATE SATISFIED for non-commercial research / education
capture-domain mismatch with ordinary contactless Palmistry images
CURRENT RUNTIME ACQUISITION = UNVERIFIED / ENVIRONMENT-BLOCKED
```

Do not manufacture a MediaPipe compatibility result without actual source images.

### MPW-180 / PalmWildNet

IAPR TC4 lists MPW-180 as a recent palmprint dataset, and the GitHub repository `bingolo/PalmWildNet` describes a mobile palmprint corpus with multiple smartphones, flash/non-flash conditions, realistic environments, 180 subjects, 720 videos, and thousands of ROI images.

The README claims:

```text
code: Apache-2.0
dataset: CC BY-NC 4.0
```

But connector inspection of the current repository root shows only:

```text
README.md
LICENSE
Figure12b.png
Figures/
```

The README's documented `DATASET_LICENSE` file is not present, the dataset DOI/link is still a placeholder, and the README explicitly states that the study is still under review and more information will be added after review.

Decision:

```text
capture-domain fit is excellent for future phone/device repeatability
but CURRENT DATASET RELEASE SURFACE IS INCOMPLETE
README license claim alone is insufficient to treat the corpus as acquired/released
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

Decision:

```text
acquisition object exists
license / provenance qualification insufficient
→ hold
```

### NTU Palmprints / NTU Contactless Palmprints

Official/project documentation requires completing and returning a Data Release Agreement before a download link is supplied.

Decision:

```text
scientifically relevant
access-gated; not an anonymous reproducible baseline corpus
```

### IITD Touchless Palmprint

Acquisition likewise requires a request/agreement workflow.

Decision:

```text
scientifically relevant
but not suitable as an automated reproducible baseline corpus
```

## Current ranking

For the specific Palmistry repeatability research need:

| Candidate | Multi-capture structure | Data-use gate | Capture-domain fit | Current decision |
|---|---|---|---|---|
| Tongji Contactless | **2 sessions × 10 / palm** | unresolved | excellent | preferred if permission closes |
| XINHUA | **2 periods × 10 / palm** | unresolved | excellent | preferred if permission closes |
| MPW-180 | multi-device / video | release incomplete | **best future phone/device fit** | hold |
| THUPALMLAB | **8 / palm** | **explicit non-commercial research/education** | scanner/contact mismatch | qualified fallback/control; acquisition unverified in current runtime |
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

At minimum report:

- detector success/failure rate;
- candidate-count distribution;
- canonical anchor/frame drift;
- within-session versus cross-session drift;
- per-class heterogeneity;
- truncation/orientation/target ambiguity/landmark failure modes.

## Predeclared THUPALMLAB fallback experiment

If source images become reproducibly available in an execution environment, THUPALMLAB may be used only as a **scanner-domain control**.

Use each dataset-provided palm as one grouping class and its eight impressions as repeated captures.

First test runtime compatibility at pinned thresholds. If the Hand Landmarker cannot detect a full hand because the images contain palmprint regions without sufficient finger/hand context, record that as a **runtime/domain compatibility negative result** and stop. Do not lower thresholds or manufacture landmarks.

If full-hand detection is usable, apply the same canonical-coordinate repeatability measurements and report per-palm heterogeneity. Do not generalize scanner-domain repeatability to camera-domain repeatability.

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

This node establishes dataset suitability, permission state, release state, and acquisition constraints only.

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
THUPALMLAB: permission clear; scanner-domain control; acquisition not verified in this runtime
```

The next high-value executable node requires either:

1. a permission-qualified contactless multi-session corpus becoming available, or
2. THUPALMLAB source images being acquired in a runtime that can reach the official archive.

Until then, the correct outcome is **ACCESS / PERMISSION BOUNDED**, not invented repeatability evidence.

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
