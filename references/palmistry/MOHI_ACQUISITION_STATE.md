# MOHI Acquisition State

Status: **REFERENCE-ONLY / ACQUISITION QUALIFIED**

This Cold note records the acquisition surface for the predeclared MOHI independent multi-capture / multi-session study.

## Official source state

The official Mutah University hand-image database page exposes direct Group-1 archives for the same nominal P1–P50 cohort across all three sessions:

```text
S1: https://www.mutah.edu.jo/biometrix/MOHI/S1/MOHI-S1-P1-50.rar
S2: https://www.mutah.edu.jo/biometrix/MOHI/S2/MOHI-S2-P1-50.rar
S3: https://www.mutah.edu.jo/biometrix/MOHI/S3/MOHI-S3-P1-50.rar
```

The page-level evidence also states that the hand-image databases are freely available for research and teaching purposes; other uses require consultation with the authors.

This makes MOHI the first currently qualified candidate in this research thread to close all of the following dataset-selection gates at once:

```text
research-use permission
+ contactless mobile-camera full-hand imagery
+ independent repeated captures
+ explicit three-session organization
+ direct official archive surface
```

## Current runtime acquisition observation

The ChatGPT execution container could resolve the official archive URLs from the source page but could not download them because the local container had no external DNS resolution for `www.mutah.edu.jo`.

Observed local error family:

```text
Could not resolve host: www.mutah.edu.jo
```

This is **environment-specific acquisition failure**, not evidence that the official archive is dead or inaccessible to an ordinary user browser/network.

Do not downgrade the dataset qualification because of this container-network limitation.

## Reproducible helper

`mohi_acquisition_sampler.py` is a Cold helper for a user/local Windows environment. It:

1. downloads only the official S1/S2/S3 Group-1 archives;
2. records archive SHA256 values;
3. extracts with 7-Zip / WinRAR / Windows tar where available;
4. recognizes dataset-provided session/person/image naming;
5. verifies complete common person IDs across all three sessions;
6. deterministically selects the first 10 complete common person IDs;
7. copies exactly five images per selected person per session;
8. writes a manifest containing only dataset person ID, session, image index, and image SHA256;
9. deliberately omits gender/age metadata from the research sample manifest;
10. packages the frozen target sample as `MOHI_sample_10p_3s_5i.zip`.

The helper must stop before inference if fewer than 10 complete common person IDs are present or if naming does not match the expected official structure.

## Frozen next step

Once `MOHI_sample_10p_3s_5i.zip` is available, run the already-predeclared `MOHI_MULTICAPTURE_PLAN.md` protocol without changing detector thresholds or replacing failed persons.

Target first study:

```text
10 persons × 3 sessions × 5 images = 150 images
```

The first runtime question remains detector usability. Repeatability statistics are calculated only for images yielding exactly one usable target under the pinned MediaPipe baseline.

## Evidence boundary

This note establishes acquisition structure and a reproducible local helper only.

It does not establish:

- that the three archives were successfully downloaded inside ChatGPT's current container;
- archive byte hashes until a successful local/user acquisition occurs;
- person-ID correspondence until archive contents are inspected;
- detector usability;
- within-session or cross-session repeatability results;
- biometric identity continuity;
- a production threshold.

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
