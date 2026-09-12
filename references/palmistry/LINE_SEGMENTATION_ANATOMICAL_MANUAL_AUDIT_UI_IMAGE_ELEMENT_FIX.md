# Palm Line Segmentation — Anatomical Manual Audit UI Image Element Fix

Status: **REFERENCE-ONLY / UI TRANSPORT IMPLEMENTATION FIX / NO MODEL COMPARISON RUN**

## Problem

After the annotation UI clarity change, the blind palm image canvas could remain blank even when the page controls rendered correctly. Subsequent attempts using relative PNG loading, local HTTP serving, and embedded data URIs did not make the palm image visible in the user's browser.

This indicates the remaining failure is in the presentation path that paints the palm image into the annotation canvas, not in the prepared blind-packet evidence itself.

## Frozen evidence boundary

This fix does not change:

- the ten frozen MOHI sources;
- corrected `C_G1_M0` baseline image bytes;
- the recorded blind PNG SHA256 values;
- annotation schema or class meanings;
- `observable / uncertain / not_observable` semantics;
- the 8 px comparison tolerance;
- model inference, masks, or comparison metrics;
- the procedural requirement that model output remain sealed until manual annotations are frozen.

No model comparison is run as part of this fix.

## UI-only change

For the self-contained embedded annotator:

1. each blind PNG is still SHA256-verified against `annotation_template.json` before use;
2. the palm photograph is displayed by a real HTML `<img>` element rather than being painted into the same canvas used for annotations;
3. the annotation `<canvas>` becomes a transparent overlay positioned directly over the image;
4. the first image data URI is written directly into the HTML `<img src=...>` so the first palm can remain visible even if later JavaScript logic fails;
5. navigation updates the `<img>` source from the already verified embedded data-URI map;
6. a visible image-load status is shown for diagnostics.

This is an implementation/display correction only and must not be interpreted as research evidence.
