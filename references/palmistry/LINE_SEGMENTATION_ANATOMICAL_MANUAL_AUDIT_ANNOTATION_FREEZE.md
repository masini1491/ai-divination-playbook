# Palm Line Segmentation — Blind Anatomical Manual Audit Annotation Freeze

Status: **REFERENCE-ONLY / ANNOTATION FROZEN / MODEL COMPARISON NOT YET RUN**

## Frozen annotation artifact

The single-observer blind manual annotation artifact was completed with the simplified three-button UI defined by `ANATOMICAL_MANUAL_AUDIT_SIMPLE_UI_PROTOCOL_AMENDMENT.md` and then copied byte-identically from Windows Downloads into the WSL audit packet.

Frozen artifact path in the research workspace:

```text
/home/user/palm-detector-study/results/MOHI_line_segmentation_anatomical_manual_audit_blind_packet/annotations.json
```

Frozen SHA256:

```text
51c4886e20cb9aee2d660fe1ca39f25b927398261478c013090ab5d611858041
```

The Windows source file and WSL copy produced the same SHA256 before any model comparison.

## Schema / provenance checks

Observed before freeze:

```text
schema = palm_line_manual_audit_v1
observer_id = observer_1
images = 10
tolerance_px = 8
spatial_raw_sha256 = ba65456e3c7c3a645a4000c721961d0f600b46541ffc7e7566525b99a55f87e7
```

Validation summary:

```text
total_annotations = 30
invalid_annotations = 0
heart_line : observable=10  not_observable=0
head_line  : observable=10  not_observable=0
life_line  : observable=10  not_observable=0
ANNOTATION_SCHEMA_CHECK = PASS
ANNOTATION_FREEZE_CANDIDATE = PASS
```

## Frozen point counts

| Source | heart_line | head_line | life_line |
|---|---:|---:|---:|
| P001/S1/01.jpg | 3 | 5 | 6 |
| P002/S1/01.jpg | 4 | 3 | 6 |
| P003/S1/01.jpg | 6 | 5 | 9 |
| P004/S1/01.jpg | 4 | 3 | 8 |
| P005/S1/01.jpg | 4 | 4 | 8 |
| P006/S1/01.jpg | 5 | 3 | 9 |
| P007/S1/01.jpg | 5 | 2 | 4 |
| P008/S1/01.jpg | 3 | 3 | 8 |
| P009/S1/01.jpg | 5 | 5 | 4 |
| P010/S1/01.jpg | 4 | 4 | 4 |

All 30 image/class entries therefore satisfy the simplified UI export rule of `>=2` points → `observable`.

## Evidence boundary

At this freeze point:

- no model-comparison output had been generated or inspected for this annotation artifact;
- no model overlay had been used to create or edit the frozen annotations;
- the 8 px comparison tolerance remains unchanged;
- the ten frozen MOHI sources, corrected `C_G1_M0` geometry, model weights, shipped class IDs, and comparison metrics remain unchanged;
- earlier incomplete or invalid UI-generated JSON files are not audit evidence.

The next permitted step is the predeclared `--compare` phase using exactly the frozen SHA256 above. Any edit to `annotations.json` after this freeze invalidates the comparison unless a new explicit freeze is recorded first.
