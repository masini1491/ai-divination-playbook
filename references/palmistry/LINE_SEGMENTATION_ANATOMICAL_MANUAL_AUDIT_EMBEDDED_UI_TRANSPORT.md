# Palm Line Segmentation — Blind Anatomical Manual Audit Embedded UI Transport

Status: **REFERENCE-ONLY / UI TRANSPORT FIX / NO MODEL COMPARISON PERFORMED**

## Problem observed

The blind annotation UI loaded successfully, including its controls and canvas, but the separate `reference_blind/*.png` resource did not render inside the canvas in the user's browser environment.

This is a UI resource-transport problem, not evidence that the blind image itself is missing. The prepared packet already contains ten blind PNG files and records each PNG SHA256 in `annotation_template.json`.

## Correction

Add a transport-only helper:

```text
references/palmistry/line_segmentation_anatomical_manual_audit_embed_ui.py
```

The helper:

1. reads an already prepared blind packet;
2. verifies all ten `reference_blind/*.png` files against the pre-recorded `blind_png_sha256` values;
3. base64-embeds those exact PNG bytes into a new `annotate_embedded.html`;
4. replaces only the browser image-loading expression so the canvas reads the embedded `data:image/png;base64,...` URI instead of a relative PNG path.

## Evidence boundary

This fix does **not** change:

- source images or their bytes;
- corrected `C_G1_M0` adapter geometry;
- frozen source selection;
- annotation schema;
- class definitions;
- manual annotation content;
- model weights or inference;
- 8 px tolerance;
- comparison metrics;
- semantic-mismatch accounting.

It is therefore treated as a browser/UI transport correction before manual annotation freeze, not as outcome-driven tuning.

No model prediction, mask, overlay, or comparison result was inspected as part of this correction.

## Prior incomplete annotations

Any annotations created before the user could reliably see the blind palm image and understand the class controls are invalid for the formal audit and must not be frozen or compared.

The formal manual audit must restart from an empty annotation payload using the corrected visible UI.
