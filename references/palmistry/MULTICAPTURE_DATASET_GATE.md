# Palm Multi-capture Dataset Qualification Gate

Status: **REFERENCE-ONLY / DATASET QUALIFICATION**

This Cold note qualifies candidate public palm-image corpora for the next Palmistry research gap: **independent multi-capture repeatability**.

It intentionally separates:

```text
publicly described
≠ publicly downloadable
≠ reproducibly acquirable
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

### IITD Touchless Palmprint

Public descriptions indicate repeated palm samples and make the dataset scientifically relevant.

However, acquisition requires a request / agreement process rather than anonymous reproducible retrieval.

Decision:

```text
scientifically relevant
but not suitable as an automated reproducible baseline corpus
```

### NTU Palmprints / NTU Contactless Palmprints

The NTU dataset repository and project documentation state that acquisition requires completing and returning a Data Release Agreement before a download link is supplied.

The related `Palmprint-Recognition-in-the-Wild` project likewise documents an application workflow for NTU palm data.

Decision:

```text
scientifically relevant
but access-gated; do not automate acquisition or treat GitHub project files as the dataset itself
```

### BJTU Palm V2 via `HewelXX/Dataset`

GitHub connector inspection confirms:

```text
repository: HewelXX/Dataset
branch: main
path: BJTU_V2/bjtu_palm_v2.zip
Git blob: d51d1ee0776afc786f3e8a2a1ec5997bb34f9e1b
observed GitHub object size: 5,422,067 bytes
```

This is materially better for reproducibility because a dataset archive is actually present in the repository rather than only an application form.

But the repository README contains only a minimal dataset statement and no license was found by repository code search during qualification.

Project policy also requires GitHub-hosted repository retrieval through the GitHub connector; an Actions workflow must not silently bypass that policy by downloading `raw.githubusercontent.com` directly.

Decision:

```text
acquisition object exists
license / provenance qualification insufficient for current automated benchmark use
```

### XINHUA Palmprint via `HewelXX/Dataset`

GitHub connector inspection confirms that source JPEGs are present directly under `XINHUA/`, with repeated filename groups such as:

```text
100_1.jpg
100_2.jpg
...
100_20.jpg
```

The associated publication's Data Availability statement identifies both the GitHub dataset location and Zenodo DOI `10.5281/zenodo.15473268`. It describes the corpus as 50 participants, 100 palm classes, 20 images per palm, with two capture periods of 10 images each.

This structure is especially useful for the research question because it provides repeated captures grouped by palm class and a session-like split.

The GitHub contents API also confirms individual JPEG objects are directly retrievable through the connector. A connector capability probe successfully returned base64 JPEG content for `XINHUA/100_1.jpg`; no raw-GitHub fallback is required for bounded inspection.

However, the GitHub repository itself contains no confirmed dataset license, and the publication's Data Availability statement establishes location/provenance rather than explicit data-use permission. The associated Zenodo record has not yet supplied a sufficiently explicit dataset-level license statement in the evidence captured for this Playbook.

Decision:

```text
best current structural candidate for contactless multi-capture repeatability
but LICENSE GATE REMAINS UNSATISFIED
```

Do not execute a broad corpus benchmark until the data-use / license boundary is resolved.

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

Independent catalog / literature descriptions agree on the 1,280-image, 80-subject, two-palms, eight-impressions-per-palm structure.

This resolves the basic research-use permission gate more clearly than the current XINHUA evidence.

But THUPALMLAB is a **contact / scanner-acquired high-resolution palmprint corpus**, whereas the existing Palmistry observation pipeline is primarily concerned with ordinary palm-facing photographs and MediaPipe landmark geometry. Therefore it is not an equivalent replacement for XINHUA's contactless capture domain.

Decision:

```text
LICENSE / DATA-USE GATE SATISFIED for non-commercial research
multi-impression structure suitable for true repeated-capture analysis
capture-domain mismatch with ordinary contactless Palmistry images
→ qualified fallback / control corpus, not a substitute for contactless validation
```

The public multi-impression subset may be used for a bounded repeatability/control study if acquisition is reproducible in the execution environment. Any such study must explicitly label the sensor/domain mismatch and must not generalize scanner repeatability to phone/camera palm photos.

## Current ranking

For the specific Palmistry repeatability research need:

| Candidate | Repeated captures | Reproducible acquisition | License/data-use gate | Capture-domain fit | Current decision |
|---|---|---|---|---|---|
| XINHUA | strong; 20/palm, two periods | strong through GitHub connector | unresolved | strong contactless fit | **preferred pending license** |
| THUPALMLAB | strong; 8/palm | official public download | **explicit non-commercial research/education** | scanner/contact mismatch | **qualified fallback/control** |
| BJTU V2 | likely useful | archive present | unresolved | contactless | hold |
| NTU-CP / NTU-PI | scientifically useful | application-gated | agreement-controlled | contactless | hold |
| IITD | scientifically useful | application-gated | agreement-controlled | contactless | hold |

This ranking is about research operability and domain fit, not overall dataset scientific quality.

## Predeclared XINHUA experiment if license gate clears

Do not tune the protocol after seeing repeatability results.

Use dataset-provided palm classes as scene-independent grouping labels only.

For a bounded first study:

```text
select deterministic palm classes before inference
use captures 1–10 as period/session A
use captures 11–20 as period/session B
run the same pinned MediaPipe Hand Landmarker baseline
require a unique usable target hand or fail closed
map landmarks back to raw-image geometry
compute canonical L0/L5/L17 palm basis
compare within-class canonical landmark / anchor geometry across captures
report within-session and cross-session distributions separately
```

At minimum report:

- detector success / failure rate;
- candidate-count distribution;
- canonical anchor / frame drift for usable captures;
- within-period vs cross-period drift;
- per-class heterogeneity rather than only pooled mean;
- failure modes such as truncation, orientation, target ambiguity, or landmark collapse.

## Predeclared THUPALMLAB fallback experiment

If XINHUA remains license-blocked, THUPALMLAB may be used as a **scanner-domain control** rather than silently substituting for contactless validation.

Use each dataset-provided palm as one grouping class and its eight impressions as repeated captures. Preserve the official train/test partition if exposed by the downloaded subset metadata; do not create an identity split from inferred personal information.

Measure only quantities that remain meaningful for the available image type. If the pinned MediaPipe Hand Landmarker cannot detect a full hand because the corpus contains palmprints without sufficient fingers/hand context, record that as a **runtime/domain compatibility result** and stop; do not lower thresholds or manufacture landmarks.

If full-hand detection is usable, apply the same canonical-coordinate repeatability measurements and report per-palm heterogeneity. Do not interpret scanner-domain repeatability as camera-domain repeatability.

## Common prohibitions

Do **not**:

- infer a person's real identity from a class label;
- train or evaluate biometric authentication;
- lower detector thresholds to rescue failed frames;
- tune a production admission threshold from the same corpus;
- interpret image-list order as identity beyond the dataset's own grouping contract;
- commit source images into this Playbook;
- silently generalize contact/scanner results to contactless phone/camera capture.

## Evidence boundary

This node establishes dataset suitability and access constraints only.

It does not establish:

- a multi-capture repeatability distribution;
- a device-to-device repeatability distribution;
- a production quality threshold;
- detector-to-detector agreement;
- line-segmentation repeatability;
- biometric identity continuity.

Current executable state:

```text
XINHUA: preferred contactless corpus, license gate unresolved
THUPALMLAB: research-use gate satisfied, qualified scanner-domain fallback/control
```

The next bounded executable node is to test whether the official THUPALMLAB public download is reproducibly acquirable and whether its images are compatible with the pinned observation runtime. A broad XINHUA benchmark remains blocked until explicit data-use authority is resolved.

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
