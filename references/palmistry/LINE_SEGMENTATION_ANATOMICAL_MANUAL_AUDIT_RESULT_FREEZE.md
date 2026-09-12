# Palm Line Anatomical Manual Audit — Result Freeze

Status: **REFERENCE-ONLY / RESULT ARTIFACT FROZEN BEFORE SUBSTANTIVE INSPECTION**

## Purpose

Record the first model-comparison execution artifact and its provenance before any substantive metric interpretation or overlay inspection.

## Frozen annotation input

- annotation schema: `palm_line_manual_audit_v1`
- observer: `observer_1`
- selected sources: `10`
- annotation classes per source: `3`
- total class annotations: `30`
- tolerance: `8 px`
- annotation SHA256: `51c4886e20cb9aee2d660fe1ca39f25b927398261478c013090ab5d611858041`
- spatial-control provenance SHA256: `ba65456e3c7c3a645a4000c721961d0f600b46541ffc7e7566525b99a55f87e7`

The local validation immediately before comparison reported all 30 class annotations as schema-valid and all three classes observable in all ten selected images.

## First comparison execution

The runner completed all ten selected sources in order:

- `P001/S1/01.jpg`
- `P002/S1/01.jpg`
- `P003/S1/01.jpg`
- `P004/S1/01.jpg`
- `P005/S1/01.jpg`
- `P006/S1/01.jpg`
- `P007/S1/01.jpg`
- `P008/S1/01.jpg`
- `P009/S1/01.jpg`
- `P010/S1/01.jpg`

Runner execution summary printed:

```json
{
  "selected_sources": 10,
  "annotation_file_frozen": true,
  "stop": false
}
```

The output artifact was written to:

`/home/user/palm-detector-study/results/MOHI_line_manual_anatomical_audit.json`

and immediately hashed before substantive inspection.

## Frozen result artifact

- result JSON SHA256: `6f95828b70b388028a46ee1879835d432d9dd695bdbbdd1f2656b6ebf3572284`
- generated overlay count: `10`
- overlays were not inspected before this freeze record
- substantive JSON metrics were not inspected before this freeze record

## Evidence boundary

This record freezes only provenance and execution-state evidence. It does **not** itself establish anatomical correctness, class correctness, a production cutoff, or any palmistry interpretation claim. Metric interpretation and any overlay inspection occur only after this freeze record is committed.