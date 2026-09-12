# Palm Multi-capture Dataset Qualification Gate

Status: **REFERENCE-ONLY / DATASET QUALIFICATION COMPLETE / DEVICE PERMISSION AUDIT CLOSED-UNRESOLVED**

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

## Next research node: device-to-device repeatability

MOHI does not isolate device change, so device-to-device repeatability remains open.

The predeclared next-step owner is `DEVICE_REPEATABILITY_PLAN.md`.

A bounded public-authority permission audit was completed on 2026-09-12 for the two leading paired-device candidates. The audit intentionally distinguishes public release / reproducibility intent from dataset-level reuse authorization.

### MPD-v2 / Tongji Mobile Palmprint Dataset — primary structural candidate

The official Mobile Palmprint project page describes MPD 2.0 with an original `PalmSet` of 16,000 full palm images from 200 subjects / 400 hands.

The capture design explicitly uses two smartphone brands and two collection periods:

```text
Huawei
Xiaomi
2 periods
10 photos / hand / phone / period
```

That structure is unusually useful because device and session are explicit factors rather than confounded.

A paired analysis could therefore separate:

```text
same device / same session
same device / cross session
cross device / same session
cross device / cross session
```

This is a stronger fit for smartphone-to-smartphone repeatability than a corpus that merely contains many different phones across different participants.

Permission audit evidence:

- official project page: `https://cslinzhang.github.io/MobilePalmPrint/`;
- MPD paper: *Towards Palmprint Verification On Smartphones* (`arXiv:2003.13266`);
- project-linked MPD 2.0 download surface, to the extent retrievable in the current research environment.

The project page and paper establish public release, dataset provenance, reproducibility intent, and the device/session structure. They do **not** expose a dataset-level CC license, explicit research-use permission grant, EULA, data-use terms, redistribution rule, or equivalent reuse authorization on the inspected surfaces. The linked Baidu landing page could not be inspected in the current research environment, so no additional landing-page terms were observed.

Decision:

```text
PRIMARY DEVICE-REPEATABILITY STRUCTURAL CANDIDATE
FULL-HAND ORIGINALS AVAILABLE
DEVICE FACTOR EXPLICIT
SESSION FACTOR EXPLICIT
PUBLIC RELEASE / REPRODUCIBILITY INTENT ESTABLISHED
DATASET-LEVEL REUSE PERMISSION NOT ESTABLISHED
DATA-USE / LICENSE GATE UNRESOLVED AFTER PUBLIC-AUTHORITY AUDIT
→ execution blocked
```

### XJTU-UP — secondary paired-device candidate

Public literature and dataset references describe XJTU-UP as an unconstrained palmprint corpus captured using multiple smartphones and lighting conditions. Recent X-Palm benchmark documentation represents it with device-separated branches including iPhone and Huawei trees.

This makes XJTU-UP a useful independent device-effect confirmation candidate.

After MPD-v2 remained unresolved, the permission audit checked the XJTU-UP paper *Towards Efficient Unconstrained Palmprint Recognition via Deep Distillation Hashing* / *Deep Distillation Hashing for Unconstrained Palmprint Recognition* (`arXiv:2004.03303`) and Xi'an Jiaotong University faculty/project pages associated with the dataset resource route.

Those sources establish that the dataset was publicly released for research reproducibility and document its multi-smartphone acquisition. No inspected authoritative surface supplied a dataset-level CC license, explicit non-commercial/research-use grant, EULA, data-use terms, redistribution rule, or equivalent reuse statement.

Decision:

```text
MULTI-DEVICE STRUCTURE STRONG
CONTACTLESS DOMAIN STRONG
PUBLIC RELEASE / RESEARCH CONTEXT ESTABLISHED
DATASET-LEVEL REUSE PERMISSION NOT ESTABLISHED
DATA-USE / LICENSE GATE UNRESOLVED AFTER PUBLIC-AUTHORITY AUDIT
→ execution blocked
```

### Permission-closing boundary

For MPD-v2 and XJTU-UP, public release, citation by later papers, and availability of a download route are not treated as permission authority.

Before acquisition, the Playbook requires either:

- an authoritative dataset-owner page with explicit reuse terms; or
- direct written authorization that clearly covers the intended bounded non-commercial research use, local automated processing, and derived aggregate reporting.

Any closure evidence must record source, scope, restrictions, citation requirement, redistribution boundary, and local-retention conditions.

Until that evidence exists:

```text
MPD-v2: NO ACQUISITION / NO INFERENCE
XJTU-UP: NO ACQUISITION / NO INFERENCE
```

### X-Palm — cross-domain reference, not first phone-to-phone corpus

X-Palm (2026) provides paired scanner ↔ smartphone acquisition, with smartphone collection spanning 80+ device models from 10+ brands. Access is non-commercial academic use under an EULA workflow.

This is valuable for scanner-to-phone domain shift and broad smartphone diversity, but current evidence does not establish same-palm acquisition across multiple phone models. Therefore it is not the preferred first smartphone-to-smartphone repeatability corpus.

Decision:

```text
PAIRED SCANNER↔SMARTPHONE = YES
BROAD PHONE DIVERSITY = YES
SAME-PALM MULTI-PHONE PAIRING = NOT ESTABLISHED
ACCESS = EULA-CONTROLLED
```

### MPW-180 / PalmWildNet — broad device-diversity candidate, not paired-device authority

`bingolo/PalmWildNet` describes MPW-180 as a mobile palmprint corpus with:

```text
180 subjects
multiple smartphones
flash / non-flash
indoor / outdoor
720 videos
thousands of ROI images
```

The README claims dataset CC BY-NC 4.0, but current repository inspection still shows only README / figures / Apache code license; the documented `DATASET_LICENSE` artifact is absent and the dataset DOI/link remains a placeholder.

More importantly for this research question, current evidence establishes participant-owned device diversity, not clearly repeated same-palm acquisition across multiple smartphone models.

Decision:

```text
BROAD MOBILE DEVICE DIVERSITY = STRONG
PAIRED SAME-PALM MULTI-DEVICE STRUCTURE = NOT ESTABLISHED
DATASET RELEASE / LICENSE ARTIFACT = INCOMPLETE
→ hold
```

## Other candidate screen

### XINHUA Palmprint via `HewelXX/Dataset`

GitHub connector inspection confirms source JPEGs directly under `XINHUA/`, with repeated filename groups such as `100_1.jpg ... 100_20.jpg`.

The associated publication's Data Availability statement identifies both the GitHub dataset location and Zenodo DOI `10.5281/zenodo.15473268`, and describes 50 participants, 100 palm classes, 20 images per palm, split into two capture periods of 10 images each.

However, the repository itself contains no confirmed dataset license, and the publication's Data Availability statement establishes location/provenance rather than explicit reuse permission.

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

This remains a strong longer-interval contactless repeatability candidate, but reuse permission is unresolved in current evidence.

### THUPALMLAB multi-impression subset

The official Tsinghua University dataset page explicitly permits the public multi-impression subset for non-commercial research / education.

A bounded subject-1 left-palm 8-impression probe under the pinned MediaPipe baseline returned:

```text
0 candidates = 8
usable exactly-one rate = 0.0
```

Decision: bounded scanner-domain compatibility negative; current MediaPipe path stopped.

### BJTU Palm V2 via `HewelXX/Dataset`

Archive acquisition exists, but no sufficient dataset license/provenance statement was found.

### NTU Palmprints / NTU Contactless Palmprints

Access requires a Data Release Agreement.

### IITD Touchless Palmprint

Access requires a request/agreement workflow.

## Current ranking

| Candidate | Research role | Data-use gate | Device/session fit | Current decision |
|---|---|---|---|---|
| MOHI | completed multi-session baseline | **explicit research/teaching** | same capture setup, 3 sessions | **bounded study complete** |
| MPD-v2 | **primary phone-to-phone candidate** | unresolved after public-authority audit | **2 phones × 2 periods, paired** | **execution blocked** |
| XJTU-UP | secondary phone-to-phone candidate | unresolved after public-authority audit | multi-phone / multi-lighting | execution blocked |
| X-Palm | scanner↔phone cross-domain reference | EULA-controlled | broad phone diversity; pairing across phone models unproven | reference / gated |
| MPW-180 | broad phone-diversity reference | release/license artifact incomplete | many phones; same-palm multi-phone pairing unproven | hold |
| Tongji Contactless | longer-interval session candidate | unresolved | 2 sessions | hold |
| XINHUA | alternative session candidate | unresolved | 2 periods | hold |
| THUPALMLAB | scanner-domain control | explicit research/education | repeated impressions, scanner | bounded runtime negative |

This ranking is about research operability and factor isolation, not overall dataset scientific quality.

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
- treat broad device diversity as paired same-palm multi-device evidence;
- describe duplicated sample entries as unique independent captures.

## Evidence boundary

This node now establishes:

- one permission-qualified contactless full-hand multi-session bounded repeatability result under MOHI;
- positive pinned-runtime compatibility for all 150 MOHI image entries in the first study;
- descriptive within-session versus cross-session geometry distributions;
- a closed duplicate-content audit explaining all exact-zero detector-geometry groups;
- a bounded negative scanner-domain runtime result for THUPALMLAB;
- a predeclared device-repeatability design with MPD-v2 as the strongest current structural candidate;
- a completed public-authority permission audit for MPD-v2 and XJTU-UP that leaves both reuse gates unresolved.

It still does **not** establish:

- device-to-device repeatability;
- long-term longitudinal stability;
- production quality/admission thresholds;
- detector-to-detector agreement;
- principal-line segmentation repeatability;
- biometric identity continuity.

Current executable state:

```text
MOHI: bounded contactless multi-session study complete
MPD-v2: best paired smartphone-device design; public-authority permission audit unresolved
XJTU-UP: secondary paired-device candidate; public-authority permission audit unresolved
X-Palm: EULA-gated scanner↔smartphone cross-domain reference
MPW-180: broad device diversity but release/pairing evidence incomplete
THUPALMLAB: permission clear; bounded scanner sample incompatible with current pinned full-hand runtime
```

The next executable step is **not** dataset download. It is obtaining authoritative dataset-level reuse terms or direct written permission for MPD-v2 or XJTU-UP while preserving the already-frozen `DEVICE_REPEATABILITY_PLAN.md`.

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
