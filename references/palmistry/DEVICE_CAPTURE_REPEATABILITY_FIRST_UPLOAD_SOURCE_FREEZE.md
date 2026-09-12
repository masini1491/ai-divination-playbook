# Device / Capture Repeatability — First Upload Source Freeze

Status: **REFERENCE-ONLY / PRE-INFERENCE SOURCE INTEGRITY FROZEN / PRIVATE IMAGES NOT COMMITTED**

## Purpose

本文件只固定第一批 two-device left-palm private upload 的 source integrity / accounting identity。它不包含原始影像、GPS values、完整 EXIF、MediaPipe outputs 或 substantive geometry results。

## Private source archive identity

Local/private upload：

```text
archive name = 左手.zip
SHA256 = b5854b545f3ff0193b51cc02278efdbca25e1e3d1147a8559c7bb042ff2b7ca0
```

Archive is not committed to the public repository。

## Source accounting

```text
source image entries = 30
Google Pixel 5       = 15
Google Pixel 10 Pro  = 15
unique source SHA256 = 30
byte-identical duplicate groups = 0
```

All 30 source files decoded successfully during integrity inspection。

## Image / orientation metadata

Observed task-relevant metadata：

```text
Google Pixel 5 image dimensions       = 3024 × 4032
Google Pixel 10 Pro image dimensions  = 3072 × 4080
EXIF Orientation                      = 1 for all 30 entries
```

This only records orientation / dimensions required for the capture-frame contract. It does not establish camera optical equivalence or geometry accuracy。

## Anatomical-side authority

User-provided authority：

```text
anatomical_side = left
side_authority = explicit_bodily_self_report
```

No detector handedness inference has been performed at source-freeze time。

## Capture semantics frozen before inference

User clarified that every still photo involved lowering and raising the hand again, with small angle / framing changes before capture。

Therefore the 30 entries are admitted as repeated-reposition still captures rather than frozen-pose burst frames。

However, the collection does not satisfy the original three-independent-session criterion. The source set is frozen as：

```text
one short collection block per device
15 repeated-reposition stills per device
```

Ordinal `01–05 / 06–10 / 11–15` may be used only as `B1/B2/B3` diagnostic strata, not renamed to `S1/S2/S3`。

## Privacy-minimized local manifest

Local integrity manifest identity：

```text
B2_left_source_integrity_manifest.json
SHA256 = a35dd54c275d95616e8b8c29fb3fc0e9e772a45c4ed9b5ac498d6cf5e282d01f
```

The local manifest is not committed because it contains per-file private source bookkeeping. Public research documents retain only bounded aggregate provenance and cryptographic identities needed to recognize the frozen input set。

## EXIF privacy note

Source files contain GPS-related EXIF tags. Their values are deliberately excluded from public research artifacts and must not be used for the Palmistry study。

No exact capture location, GPS coordinate, complete EXIF dump, serial, IMEI, MAC, or account identifier is admitted into the public evidence chain。

## Pre-inference state

At source freeze time：

```text
MediaPipe inference = not performed on this uploaded source set
landmark geometry summary = not inspected
candidate-count distribution = not inspected
cross-device geometry = not inspected
production cutoff = none
```

## Next allowed action

Implement / static-review a first-upload pilot runner that uses the existing pinned detector contract and preserves the pilot-only collection semantics. The raw inference artifact must be hashed before substantive geometry interpretation。

## Boundary

This source freeze does not establish formal B2 three-session closure, device portability, anatomical truth, biometric identity, production threshold, or production routing。

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**。