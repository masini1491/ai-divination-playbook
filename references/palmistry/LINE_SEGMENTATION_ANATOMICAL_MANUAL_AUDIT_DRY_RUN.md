# Palm Line Segmentation Anatomical Manual Audit — Dry Run

Status: **REFERENCE-ONLY / NON-MOHI DRY RUN PASS / READY FOR BLIND PACKET PREPARATION**

This record captures the bounded dry run of `line_segmentation_anatomical_manual_audit_runner.py` before any blind MOHI annotation packet is prepared.

## Command

```text
python references/palmistry/line_segmentation_anatomical_manual_audit_runner.py \
  --model ~/palm-detector-study/palm-line-reader/models/student_fp32.onnx \
  --meta ~/palm-detector-study/palm-line-reader/models/model_meta.json \
  --dry-run
```

## Observed output

```json
{
  "mode": "NON-MOHI ANATOMICAL MANUAL AUDIT DRY RUN",
  "model_mask_shape": [512, 512],
  "finite_logit_summary": true,
  "reference_pixels": 371,
  "synthetic_comparison": {
    "model_present": true,
    "model_on_reference_coverage": 1.0,
    "reference_on_model_coverage": 1.0,
    "harmonic_coverage": 1.0,
    "median_model_to_reference_px": 1.0,
    "median_reference_to_model_px": 0.0,
    "reference_px": 371,
    "model_px": 1839
  },
  "tolerance_px": 8.0,
  "schema": "PASS"
}
```

## Dry-run conclusion

The non-MOHI synthetic fixture verifies that:

- model inference returns a `512×512` mask;
- logit summary values are finite;
- manual-reference polyline rasterization is non-empty;
- the bidirectional tolerance-coverage path is operational;
- the frozen tolerance is `8.0 px`;
- the expected dry-run schema is satisfied.

The synthetic fixture is only an implementation test. Its perfect coverage is constructed and must not be interpreted as MOHI anatomical accuracy evidence.

## Next gate

Proceed only to `--prepare-blind`.

That phase may generate:

- ten corrected `baseline_512` blind images;
- `annotation_template.json`;
- `annotate.html`;
- a sealed marker stating that model overlays have intentionally not been generated.

Do **not** run `--compare` and do not inspect or generate model overlays until the completed `annotations.json` has been downloaded and its SHA256 has been frozen.

The prepared blind packet must reproduce each prior spatial-control baseline input SHA before an image is emitted.

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
