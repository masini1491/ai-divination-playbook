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

The associated dataset paper describes the corpus as:

```text
50 participants
100 palm classes
20 images per palm
2 capture periods × 10 images
```

This structure is especially useful for the research question because it provides repeated captures grouped by palm class and a session-like split.

The GitHub contents API also confirms individual JPEG objects are directly retrievable through the connector. A connector capability probe successfully returned base64 JPEG content for `XINHUA/100_1.jpg`; no raw-GitHub fallback is required for bounded inspection.

However, no repository license was found during qualification. A Zenodo DOI associated with the dataset publication was identified, but dataset-level license terms were not yet reliably resolved in this research node.

Decision:

```text
best current structural candidate for multi-capture repeatability
but LICENSE GATE NOT YET SATISFIED
```

Do not execute a broad corpus benchmark until the data-use / license boundary is resolved.

## Current ranking

For the specific Palmistry repeatability research need:

| Candidate | Repeated captures | Reproducible acquisition | License gate | Current decision |
|---|---|---|---|---|
| XINHUA | strong | strong through GitHub connector | unresolved | **preferred pending license** |
| BJTU V2 | likely useful | archive present | unresolved | hold |
| NTU-CP / NTU-PI | scientifically useful | application-gated | agreement-controlled | hold |
| IITD | scientifically useful | application-gated | agreement-controlled | hold |

This ranking is about research operability, not dataset scientific quality.

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

Do **not**:

- infer a person's real identity from the class label;
- train or evaluate biometric authentication;
- lower detector thresholds to rescue failed frames;
- tune a production admission threshold from the same corpus;
- interpret image-list order as identity beyond the dataset's own grouping contract;
- commit source JPEGs into this Playbook.

## Evidence boundary

This node establishes dataset suitability and access constraints only.

It does not establish:

- a multi-capture repeatability distribution;
- a device-to-device repeatability distribution;
- a production quality threshold;
- detector-to-detector agreement;
- line-segmentation repeatability;
- biometric identity continuity.

The next executable node is blocked only on obtaining sufficiently clear license / data-use authority for a reproducible repeated-capture corpus.

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
